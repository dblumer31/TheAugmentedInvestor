"""Post-processing helpers that merge deterministic fact-check findings."""

from __future__ import annotations

from augmented_investor.models.common import ClaimType
from augmented_investor.models.draft import DraftIssue
from augmented_investor.models.fact_check import (
    ActualSourceQuality,
    FactCheckCategory,
    FactCheckFlag,
    OverallScore,
    OverallSourceQuality,
    RequiredSourceQuality,
    Severity,
    SourceQualitySummary,
    TriageBucket,
    VerificationStatus,
)
from augmented_investor.models.research import ResearchBrief, ResearchClaim, ResearchPoint
from augmented_investor.pipeline.source_quality_rules import (
    ClaimEvidence,
    classify_source_quality,
)


DIRECT_ADVICE_PATTERNS = (
    "should buy",
    "should sell",
    "must buy",
    "must sell",
    "recommend buying",
    "recommend selling",
)
SCENARIO_TERMS = ("base case", "bull case", "bear case", "upside", "downside", "returns")


def build_source_quality_flags(research: ResearchBrief) -> list[FactCheckFlag]:
    """Build deterministic source-quality flags from all research claims."""

    Flags: list[FactCheckFlag] = []
    for Evidence in _research_evidence_items(research):
        Flag = classify_source_quality(Evidence)
        if Flag.Category != FactCheckCategory.Ok:
            Flags.append(Flag)
    return Flags


def build_draft_language_flags(draft: DraftIssue) -> list[FactCheckFlag]:
    """Identify deterministic draft-language issues before export."""

    Flags: list[FactCheckFlag] = []
    Body = draft.Body.lower()
    if any(Pattern in Body for Pattern in DIRECT_ADVICE_PATTERNS):
        Flags.append(
            _draft_flag(
                FactCheckCategory.InvestmentAdvice,
                Severity.Error,
                "Draft contains direct investment advice language.",
                "Rephrase as an investable question or risk framing.",
            )
        )
    if _looks_like_unlabeled_scenario(Body):
        Flags.append(
            _draft_flag(
                FactCheckCategory.ScenarioMathUnlabeled,
                Severity.Warning,
                "Draft includes scenario-style return language without clear scenario framing.",
                "Label the statement as scenario analysis.",
                ClaimType.ScenarioMath,
            )
        )
    return Flags


def summarize_flags(flags: list[FactCheckFlag]) -> SourceQualitySummary:
    """Create the source-quality summary required by FactCheckReport."""

    WeakSourceFlags = sum(_is_weak_source_flag(Flag) for Flag in flags)
    UnverifiedQuantClaims = sum(_is_unverified_quant_claim(Flag) for Flag in flags)
    BlogOnlyClaims = sum(
        Flag.ActualSourceQuality == ActualSourceQuality.BlogOrSubstack for Flag in flags
    )
    return SourceQualitySummary(
        WeakSourceFlags=WeakSourceFlags,
        UnverifiedQuantClaims=UnverifiedQuantClaims,
        BlogOnlyClaims=BlogOnlyClaims,
        OverallSourceQuality=_overall_source_quality(flags),
    )


def overall_score(flags: list[FactCheckFlag]) -> OverallScore:
    """Return the overall score from calibrated flag severities."""

    if any(Flag.Severity == Severity.Error for Flag in flags):
        return OverallScore.NeedsWork
    if any(Flag.Severity == Severity.Warning for Flag in flags):
        return OverallScore.MinorIssues
    return OverallScore.Clean


def _research_evidence_items(research: ResearchBrief) -> list[ClaimEvidence]:
    """Flatten research claims and evidence points into rule inputs."""

    EvidenceItems: list[ClaimEvidence] = []
    for Claim in research.MarketSnapshot + research.PriorTrend + research.WhatChanged:
        EvidenceItems.append(_claim_to_evidence(Claim))
    for Point in research.EvidenceFor + research.EvidenceAgainst:
        EvidenceItems.append(_point_to_evidence(Point))
    return EvidenceItems


def _claim_to_evidence(claim: ResearchClaim) -> ClaimEvidence:
    """Convert a research claim to deterministic rule input."""

    return ClaimEvidence(
        ClaimText=claim.Claim,
        ClaimType=claim.ClaimType,
        SourceQuality=claim.SourceQuality,
        SupportsExactClaim=claim.SupportsExactClaim,
        SourceName=claim.Source,
        QuotedEvidence=claim.QuotedEvidence,
        PublishedDate=claim.Date,
        HasScenarioLabel=_text_has_scenario_label(claim.Claim),
        IsLoadBearing=_claim_type_is_quantitative(claim.ClaimType),
    )


def _point_to_evidence(point: ResearchPoint) -> ClaimEvidence:
    """Convert a research evidence point to deterministic rule input."""

    return ClaimEvidence(
        ClaimText=point.Point,
        ClaimType=point.ClaimType,
        SourceQuality=point.SourceQuality,
        SupportsExactClaim=point.SupportsExactClaim,
        SourceName=point.Source,
        QuotedEvidence=point.QuotedEvidence,
        PublishedDate=point.Date,
        HasScenarioLabel=_text_has_scenario_label(point.Point),
        IsLoadBearing=_claim_type_is_quantitative(point.ClaimType),
    )


def _draft_flag(
    category: FactCheckCategory,
    severity: Severity,
    issue: str,
    suggestion: str,
    claim_type: ClaimType = ClaimType.EditorialInterpretation,
) -> FactCheckFlag:
    """Build a deterministic draft-language flag."""

    return FactCheckFlag(
        Category=category,
        Severity=severity,
        Excerpt=None,
        Issue=issue,
        Suggestion=suggestion,
        ClaimType=claim_type,
        RequiredSourceQuality=RequiredSourceQuality.Any,
        ActualSourceQuality=ActualSourceQuality.NoneValue,
        VerificationStatus=VerificationStatus.Unsupported,
        Triage=TriageBucket.FixableWithExistingResearch,
        AddendumQuery=None,
    )


def _is_weak_source_flag(flag: FactCheckFlag) -> bool:
    """Return true when a flag indicates weak source quality."""

    return flag.Category in {
        FactCheckCategory.WeakSourceForQuantClaim,
        FactCheckCategory.SourceQualityMismatch,
        FactCheckCategory.OverreliesOnBlogOrSubstack,
    }


def _is_unverified_quant_claim(flag: FactCheckFlag) -> bool:
    """Return true when an unresolved quantitative claim remains."""

    return flag.VerificationStatus in {
        VerificationStatus.Unsupported,
        VerificationStatus.NeedsPrimarySource,
    } and flag.ClaimType in {
        ClaimType.MarketReturn,
        ClaimType.Valuation,
        ClaimType.CompanyFinancial,
        ClaimType.ScenarioMath,
    }


def _looks_like_unlabeled_scenario(body: str) -> bool:
    """Return true when draft contains return/case language without scenario framing."""

    if "scenario analysis" in body or "scenario estimate" in body:
        return False
    return any(Term in body for Term in SCENARIO_TERMS)


def _text_has_scenario_label(text: str) -> bool:
    """Return true when text explicitly frames scenario or forecast language."""

    LowerText = text.lower()
    return any(Term in LowerText for Term in ("scenario", "estimate", "case"))


def _claim_type_is_quantitative(claim_type: ClaimType) -> bool:
    """Return true when claim type is usually load-bearing and quantitative."""

    return claim_type in {
        ClaimType.MarketReturn,
        ClaimType.Valuation,
        ClaimType.CompanyFinancial,
        ClaimType.ScenarioMath,
    }


def _overall_source_quality(flags: list[FactCheckFlag]) -> OverallSourceQuality:
    """Return aggregate source-quality rating from flags."""

    if any(Flag.Severity == Severity.Error for Flag in flags):
        return OverallSourceQuality.Unreliable
    if any(Flag.Category == FactCheckCategory.OverreliesOnBlogOrSubstack for Flag in flags):
        return OverallSourceQuality.Weak
    if any(Flag.Severity == Severity.Warning for Flag in flags):
        return OverallSourceQuality.Acceptable
    return OverallSourceQuality.Strong
