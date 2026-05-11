"""Fact-check contracts and enums used by audit and fix-pass stages."""

from __future__ import annotations

from enum import StrEnum

from pydantic import AliasChoices, Field

from augmented_investor.models.common import ClaimType as ClaimTypeValue
from augmented_investor.models.common import StrictBaseModel


class FactCheckCategory(StrEnum):
    """Prototype-compatible fact-check categories."""

    UnsupportedNumber = "unsupported_number"
    MissingUrl = "missing_url"
    InstrumentImprecision = "instrument_imprecision"
    OverconfidentProjection = "overconfident_projection"
    MissingCounterargument = "missing_counterargument"
    InvestmentAdvice = "investment_advice"
    ScenarioMathUnlabeled = "scenario_math_unlabeled"
    WeakSourceForQuantClaim = "weak_source_for_quant_claim"
    SourceDoesNotSupportClaim = "source_does_not_support_claim"
    SourceQualityMismatch = "source_quality_mismatch"
    UnverifiedMarketReturn = "unverified_market_return"
    OverreliesOnBlogOrSubstack = "overrelies_on_blog_or_substack"
    ExactQuoteMissing = "exact_quote_missing"
    CitationPresentButClaimUnproven = "citation_present_but_claim_unproven"
    Ok = "ok"


class FactCheckSeverity(StrEnum):
    """Fact-check severity levels."""

    Error = "error"
    Warning = "warning"
    Info = "info"
    Ok = "ok"


class FactVerificationStatus(StrEnum):
    """Verification status for a flagged claim."""

    Verified = "verified"
    PartiallySupported = "partially_supported"
    Unsupported = "unsupported"
    NeedsPrimarySource = "needs_primary_source"


class TriageBucket(StrEnum):
    """Repair path for a fact-check flag."""

    FixableWithExistingResearch = "fixableWithExistingResearch"
    GeneralizeOrRemoveUnsupportedSpecificity = "generalizeOrRemoveUnsupportedSpecificity"
    NeedsResearchAddendum = "needsResearchAddendum"


class RequiredSourceQualityValue(StrEnum):
    """Required source quality allows `any` in addition to source-quality values."""

    PrimaryMarketData = "primary_market_data"
    CompanyFilingOrIr = "company_filing_or_ir"
    OfficialInstitutionalReport = "official_institutional_report"
    ReputableFinancialMedia = "reputable_financial_media"
    SyndicatedMarketArticle = "syndicated_market_article"
    Any = "any"


class ActualSourceQualityValue(StrEnum):
    """Actual source quality allows `none` in addition to source-quality values."""

    PrimaryMarketData = "primary_market_data"
    CompanyFilingOrIr = "company_filing_or_ir"
    OfficialInstitutionalReport = "official_institutional_report"
    ReputableFinancialMedia = "reputable_financial_media"
    SyndicatedMarketArticle = "syndicated_market_article"
    BlogOrSubstack = "blog_or_substack"
    Unknown = "unknown"
    NoneValue = "none"


class OverallSourceQualityRating(StrEnum):
    """Overall source-quality summary classification."""

    Strong = "strong"
    Acceptable = "acceptable"
    Weak = "weak"
    Unreliable = "unreliable"


class OverallScoreValue(StrEnum):
    """Fact-check report score."""

    Clean = "clean"
    MinorIssues = "minor_issues"
    NeedsWork = "needs_work"


class FactCheckFlag(StrictBaseModel):
    """One fact-check issue or explicit clear finding."""

    Category: FactCheckCategory = Field(validation_alias=AliasChoices("Category", "category"))
    Severity: FactCheckSeverity = Field(validation_alias=AliasChoices("Severity", "severity"))
    Excerpt: str | None = Field(default=None, validation_alias=AliasChoices("Excerpt", "excerpt"))
    Issue: str = Field(validation_alias=AliasChoices("Issue", "issue"))
    Suggestion: str | None = Field(
        default=None,
        validation_alias=AliasChoices("Suggestion", "suggestion"),
    )
    ClaimType: ClaimTypeValue = Field(validation_alias=AliasChoices("ClaimType", "claimType"))
    RequiredSourceQuality: RequiredSourceQualityValue = Field(
        validation_alias=AliasChoices("RequiredSourceQuality", "requiredSourceQuality"),
    )
    ActualSourceQuality: ActualSourceQualityValue = Field(
        validation_alias=AliasChoices("ActualSourceQuality", "actualSourceQuality"),
    )
    VerificationStatus: FactVerificationStatus = Field(
        validation_alias=AliasChoices("VerificationStatus", "verificationStatus"),
    )
    Triage: TriageBucket = Field(validation_alias=AliasChoices("Triage", "triage"))
    AddendumQuery: str | None = Field(
        default=None,
        validation_alias=AliasChoices("AddendumQuery", "addendumQuery"),
    )


class SourceQualitySummaryDetails(StrictBaseModel):
    """Aggregate source-quality counts and score."""

    WeakSourceFlags: int = Field(
        default=0,
        validation_alias=AliasChoices("WeakSourceFlags", "weakSourceFlags"),
    )
    UnverifiedQuantClaims: int = Field(
        default=0,
        validation_alias=AliasChoices("UnverifiedQuantClaims", "unverifiedQuantClaims"),
    )
    BlogOnlyClaims: int = Field(
        default=0,
        validation_alias=AliasChoices("BlogOnlyClaims", "blogOnlyClaims"),
    )
    OverallSourceQuality: OverallSourceQualityRating = Field(
        validation_alias=AliasChoices("OverallSourceQuality", "overallSourceQuality"),
    )


class FactCheckReport(StrictBaseModel):
    """Structured fact-check output used by review and fix-pass stages."""

    Flags: list[FactCheckFlag] = Field(
        default_factory=list,
        validation_alias=AliasChoices("Flags", "flags"),
    )
    SourceQualitySummary: SourceQualitySummaryDetails = Field(
        validation_alias=AliasChoices("SourceQualitySummary", "sourceQualitySummary"),
    )
    OverallScore: OverallScoreValue = Field(
        validation_alias=AliasChoices("OverallScore", "overallScore"),
    )
    Summary: str = Field(validation_alias=AliasChoices("Summary", "summary"))


Severity = FactCheckSeverity
VerificationStatus = FactVerificationStatus
RequiredSourceQuality = RequiredSourceQualityValue
ActualSourceQuality = ActualSourceQualityValue
SourceQualitySummary = SourceQualitySummaryDetails
OverallSourceQuality = OverallSourceQualityRating
OverallScore = OverallScoreValue
