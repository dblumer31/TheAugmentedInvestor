"""Deterministic source-quality, citation, severity, and triage helpers."""

from __future__ import annotations

from dataclasses import dataclass
import re

from augmented_investor.models.common import ClaimType, SourceQuality
from augmented_investor.models.fact_check import (
    ActualSourceQuality,
    FactCheckCategory,
    FactCheckFlag,
    RequiredSourceQuality,
    Severity,
    TriageBucket,
    VerificationStatus,
)


URL_PATTERN = re.compile(r"https?://\S+")
@dataclass(frozen=True)
class ClaimEvidence:
    """Normalized claim evidence used by deterministic source-quality rules."""

    ClaimText: str
    ClaimType: ClaimType
    SourceQuality: SourceQuality | None
    SupportsExactClaim: bool
    SourceUrl: str | None = None
    SourceName: str | None = None
    QuotedEvidence: str | None = None
    Publisher: str | None = None
    PublishedDate: str | None = None
    HasScenarioLabel: bool = True
    IsLoadBearing: bool = False


def classify_source_quality(evidence: ClaimEvidence) -> FactCheckFlag:
    """Classify one claim against source-quality rules and triage expectations."""

    RequiredQuality = required_source_quality(evidence.ClaimType)
    ActualQuality = actual_source_quality(evidence.SourceQuality)
    if not _has_claim_citation(evidence):
        return _flag(
            FactCheckCategory.MissingUrl,
            Severity.Warning,
            evidence,
            RequiredQuality,
            ActualQuality,
            VerificationStatus.Unsupported,
            TriageBucket.FixableWithExistingResearch,
            "Claim has no URL or recognizable source citation.",
        )
    if not evidence.SupportsExactClaim:
        return _flag(
            FactCheckCategory.CitationPresentButClaimUnproven,
            _unsupported_severity(evidence),
            evidence,
            RequiredQuality,
            ActualQuality,
            VerificationStatus.Unsupported,
            _unsupported_triage(evidence),
            "Citation exists but does not prove the exact claim.",
        )
    ScenarioFlag = _scenario_label_flag(evidence, RequiredQuality, ActualQuality)
    if ScenarioFlag is not None:
        return ScenarioFlag
    InstitutionalFlag = _institutional_metadata_flag(evidence, RequiredQuality, ActualQuality)
    if InstitutionalFlag is not None:
        return InstitutionalFlag
    if _source_quality_is_allowed(evidence.ClaimType, ActualQuality):
        return _flag(
            FactCheckCategory.Ok,
            Severity.Ok,
            evidence,
            RequiredQuality,
            ActualQuality,
            VerificationStatus.Verified,
            TriageBucket.FixableWithExistingResearch,
            "Claim is supported at appropriate source quality.",
        )
    return _inadequate_source_flag(evidence, RequiredQuality, ActualQuality)


def has_source_citation(text: str | None) -> bool:
    """Return true when text contains a URL or recognizable source reference."""

    if not text:
        return False
    CleanText = text.strip().lower()
    if URL_PATTERN.search(CleanText):
        return True
    return any(Token in CleanText for Token in ("filing", "report", "source", "10-k", "ir"))


def is_reasonable_numeric_restatement(
    source_value: float,
    claim_value: float,
    scale: float = 1.0,
    tolerance: float = 0.05,
) -> bool:
    """Return true when a claim value is a reasonable scaled restatement."""

    ExpectedValue = source_value / scale
    if ExpectedValue == 0:
        return claim_value == 0
    return abs(ExpectedValue - claim_value) / abs(ExpectedValue) <= tolerance


def required_source_quality(claim_type: ClaimType) -> RequiredSourceQuality:
    """Return the minimum source-quality category expected for a claim type."""

    if claim_type in {ClaimType.MarketReturn, ClaimType.Valuation}:
        return RequiredSourceQuality.PrimaryMarketData
    if claim_type == ClaimType.CompanyFinancial:
        return RequiredSourceQuality.CompanyFilingOrIr
    if claim_type == ClaimType.InstitutionalReport:
        return RequiredSourceQuality.OfficialInstitutionalReport
    return RequiredSourceQuality.Any


def actual_source_quality(source_quality: SourceQuality | None) -> ActualSourceQuality:
    """Map research source quality to fact-check actual source quality."""

    if source_quality is None:
        return ActualSourceQuality.NoneValue
    return ActualSourceQuality(source_quality.value)


def _source_quality_is_allowed(claim_type: ClaimType, actual_quality: ActualSourceQuality) -> bool:
    """Return true when source quality satisfies the claim type."""

    Allowed = {
        ClaimType.MarketReturn: {
            ActualSourceQuality.PrimaryMarketData,
            ActualSourceQuality.CompanyFilingOrIr,
            ActualSourceQuality.ReputableFinancialMedia,
        },
        ClaimType.Valuation: {
            ActualSourceQuality.PrimaryMarketData,
            ActualSourceQuality.CompanyFilingOrIr,
        },
        ClaimType.CompanyFinancial: {
            ActualSourceQuality.CompanyFilingOrIr,
            ActualSourceQuality.ReputableFinancialMedia,
        },
        ClaimType.InstitutionalReport: {
            ActualSourceQuality.OfficialInstitutionalReport,
            ActualSourceQuality.ReputableFinancialMedia,
        },
    }
    return actual_quality in Allowed.get(claim_type, set(ActualSourceQuality))


def _inadequate_source_flag(
    evidence: ClaimEvidence,
    required_quality: RequiredSourceQuality,
    actual_quality: ActualSourceQuality,
) -> FactCheckFlag:
    """Create the appropriate flag for insufficient source quality."""

    Category = FactCheckCategory.SourceQualityMismatch
    if evidence.ClaimType == ClaimType.MarketReturn:
        Category = FactCheckCategory.UnverifiedMarketReturn
        if actual_quality == ActualSourceQuality.SyndicatedMarketArticle:
            Category = FactCheckCategory.WeakSourceForQuantClaim
    if actual_quality == ActualSourceQuality.BlogOrSubstack:
        Category = FactCheckCategory.OverreliesOnBlogOrSubstack
    return _flag(
        Category,
        _weak_source_severity(evidence),
        evidence,
        required_quality,
        actual_quality,
        VerificationStatus.NeedsPrimarySource,
        _weak_source_triage(evidence),
        "Claim requires stronger source quality.",
        addendum_query=f"Primary support for: {evidence.ClaimText}",
    )


def _scenario_label_flag(
    evidence: ClaimEvidence,
    required_quality: RequiredSourceQuality,
    actual_quality: ActualSourceQuality,
) -> FactCheckFlag | None:
    """Return a scenario/forecast label flag when needed."""

    if evidence.ClaimType == ClaimType.ScenarioMath and not evidence.HasScenarioLabel:
        return _flag(
            FactCheckCategory.ScenarioMathUnlabeled,
            Severity.Warning,
            evidence,
            required_quality,
            actual_quality,
            VerificationStatus.PartiallySupported,
            TriageBucket.FixableWithExistingResearch,
            "Scenario math is not labeled as scenario analysis.",
        )
    if evidence.ClaimType == ClaimType.Forecast and not evidence.HasScenarioLabel:
        return _flag(
            FactCheckCategory.OverconfidentProjection,
            Severity.Warning,
            evidence,
            required_quality,
            actual_quality,
            VerificationStatus.PartiallySupported,
            TriageBucket.FixableWithExistingResearch,
            "Forecast is framed with too much certainty.",
        )
    return None


def _institutional_metadata_flag(
    evidence: ClaimEvidence,
    required_quality: RequiredSourceQuality,
    actual_quality: ActualSourceQuality,
) -> FactCheckFlag | None:
    """Return an institutional report metadata flag when details are missing."""

    if evidence.ClaimType != ClaimType.InstitutionalReport:
        return None
    if evidence.QuotedEvidence and evidence.Publisher and evidence.PublishedDate:
        return None
    return _flag(
        FactCheckCategory.ExactQuoteMissing,
        Severity.Warning,
        evidence,
        required_quality,
        actual_quality,
        VerificationStatus.PartiallySupported,
        TriageBucket.FixableWithExistingResearch,
        "Institutional report support lacks exact quote, publisher, or date.",
    )


def _flag(
    category: FactCheckCategory,
    severity: Severity,
    evidence: ClaimEvidence,
    required_quality: RequiredSourceQuality,
    actual_quality: ActualSourceQuality,
    verification_status: VerificationStatus,
    triage: TriageBucket,
    issue: str,
    addendum_query: str | None = None,
) -> FactCheckFlag:
    """Build a FactCheckFlag from deterministic rule output."""

    return FactCheckFlag(
        Category=category,
        Severity=severity,
        Excerpt=evidence.ClaimText,
        Issue=issue,
        Suggestion=_suggestion_for_triage(triage),
        ClaimType=evidence.ClaimType,
        RequiredSourceQuality=required_quality,
        ActualSourceQuality=actual_quality,
        VerificationStatus=verification_status,
        Triage=triage,
        AddendumQuery=addendum_query,
    )


def _has_claim_citation(evidence: ClaimEvidence) -> bool:
    """Return true when source URL/name provides a citation."""

    return has_source_citation(evidence.SourceUrl) or bool(evidence.SourceName)


def _unsupported_severity(evidence: ClaimEvidence) -> Severity:
    """Return calibrated severity for unsupported exact claims."""

    if evidence.IsLoadBearing:
        return Severity.Error
    return Severity.Warning


def _weak_source_severity(evidence: ClaimEvidence) -> Severity:
    """Return calibrated severity for weak source quality."""

    if evidence.IsLoadBearing or evidence.ClaimType in {ClaimType.MarketReturn, ClaimType.Valuation}:
        return Severity.Error
    return Severity.Warning


def _unsupported_triage(evidence: ClaimEvidence) -> TriageBucket:
    """Return triage for unsupported exact support."""

    if evidence.IsLoadBearing:
        return TriageBucket.NeedsResearchAddendum
    return TriageBucket.GeneralizeOrRemoveUnsupportedSpecificity


def _weak_source_triage(evidence: ClaimEvidence) -> TriageBucket:
    """Return triage for weak source quality."""

    if evidence.IsLoadBearing:
        return TriageBucket.NeedsResearchAddendum
    return TriageBucket.GeneralizeOrRemoveUnsupportedSpecificity


def _suggestion_for_triage(triage: TriageBucket) -> str:
    """Return a fix-pass-friendly suggestion for a triage bucket."""

    if triage == TriageBucket.NeedsResearchAddendum:
        return "Find stronger evidence or remove the load-bearing claim."
    if triage == TriageBucket.GeneralizeOrRemoveUnsupportedSpecificity:
        return "Generalize or remove unsupported specificity."
    return "Use existing research to repair the issue."


