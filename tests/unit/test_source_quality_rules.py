"""Unit tests for deterministic source-quality and triage helpers."""

from __future__ import annotations

import pytest

from augmented_investor.models.common import ClaimType, SourceQuality
from augmented_investor.models.fact_check import (
    FactCheckCategory,
    Severity,
    TriageBucket,
    VerificationStatus,
)
from augmented_investor.pipeline.source_quality_rules import (
    ClaimEvidence,
    classify_source_quality,
    has_source_citation,
    is_reasonable_numeric_restatement,
)


@pytest.mark.parametrize(
    ("claim_type", "source_quality"),
    [
        (ClaimType.MarketReturn, SourceQuality.PrimaryMarketData),
        (ClaimType.MarketReturn, SourceQuality.CompanyFilingOrIr),
        (ClaimType.MarketReturn, SourceQuality.ReputableFinancialMedia),
        (ClaimType.Valuation, SourceQuality.PrimaryMarketData),
        (ClaimType.Valuation, SourceQuality.CompanyFilingOrIr),
        (ClaimType.CompanyFinancial, SourceQuality.CompanyFilingOrIr),
        (ClaimType.CompanyFinancial, SourceQuality.ReputableFinancialMedia),
        (ClaimType.EditorialInterpretation, SourceQuality.BlogOrSubstack),
    ],
)
def test_source_quality_matrix_accepts_adequate_sources(claim_type, source_quality):
    """Adequate source quality should produce an ok finding."""

    Flag = classify_source_quality(
        ClaimEvidence(
            ClaimText="Supported claim",
            ClaimType=claim_type,
            SourceQuality=source_quality,
            SupportsExactClaim=True,
            QuotedEvidence="Relevant evidence",
            SourceUrl="https://example.com/source",
        )
    )

    assert Flag.Category == FactCheckCategory.Ok
    assert Flag.Severity == Severity.Ok
    assert Flag.VerificationStatus == VerificationStatus.Verified


def test_market_return_syndicated_only_is_weak_quant_source():
    """Syndicated-only market-return support is weak for quantitative claims."""

    Flag = classify_source_quality(
        ClaimEvidence(
            ClaimText="The basket returned 42%.",
            ClaimType=ClaimType.MarketReturn,
            SourceQuality=SourceQuality.SyndicatedMarketArticle,
            SupportsExactClaim=True,
            SourceUrl="https://example.com/wire",
            IsLoadBearing=True,
        )
    )

    assert Flag.Category == FactCheckCategory.WeakSourceForQuantClaim
    assert Flag.Severity == Severity.Error
    assert Flag.Triage == TriageBucket.NeedsResearchAddendum


def test_blog_only_quant_claim_is_overreliance_and_needs_addendum():
    """Blog/Substack-only quantitative support must not be treated as proven."""

    Flag = classify_source_quality(
        ClaimEvidence(
            ClaimText="The valuation is 18x EBITDA.",
            ClaimType=ClaimType.Valuation,
            SourceQuality=SourceQuality.BlogOrSubstack,
            SupportsExactClaim=True,
            SourceUrl="https://example.com/blog",
            IsLoadBearing=True,
        )
    )

    assert Flag.Category == FactCheckCategory.OverreliesOnBlogOrSubstack
    assert Flag.VerificationStatus == VerificationStatus.NeedsPrimarySource
    assert Flag.Triage == TriageBucket.NeedsResearchAddendum


def test_citation_present_is_not_proof_when_source_does_not_support_claim():
    """A URL alone should not prove a claim when exact support is false."""

    Flag = classify_source_quality(
        ClaimEvidence(
            ClaimText="The company doubled capex.",
            ClaimType=ClaimType.CompanyFinancial,
            SourceQuality=SourceQuality.CompanyFilingOrIr,
            SupportsExactClaim=False,
            SourceUrl="https://example.com/filing",
            IsLoadBearing=False,
        )
    )

    assert Flag.Category == FactCheckCategory.CitationPresentButClaimUnproven
    assert Flag.Severity == Severity.Warning
    assert Flag.Triage == TriageBucket.GeneralizeOrRemoveUnsupportedSpecificity


def test_plain_text_footnote_url_counts_as_citation():
    """A URL anywhere in nearby text should satisfy the missing URL check."""

    assert has_source_citation("Revenue rose according to https://example.com/filing") is True
    assert has_source_citation("Revenue rose according to Company filing") is True
    assert has_source_citation("Revenue rose with no citation") is False


def test_reasonable_unit_conversion_is_ok():
    """Reasonable restatements and unit conversions should not become unsupported numbers."""

    assert is_reasonable_numeric_restatement(1_200_000_000, 1.2, scale=1_000_000_000)
    assert is_reasonable_numeric_restatement(100, 101, tolerance=0.02)
    assert not is_reasonable_numeric_restatement(100, 120, tolerance=0.02)


def test_institutional_report_missing_metadata_flags_exact_quote_missing():
    """Institutional reports need exact report metadata."""

    Flag = classify_source_quality(
        ClaimEvidence(
            ClaimText="The report expects demand growth.",
            ClaimType=ClaimType.InstitutionalReport,
            SourceQuality=SourceQuality.OfficialInstitutionalReport,
            SupportsExactClaim=True,
            SourceUrl="https://example.com/report",
            QuotedEvidence=None,
            Publisher=None,
            PublishedDate=None,
        )
    )

    assert Flag.Category == FactCheckCategory.ExactQuoteMissing
    assert Flag.Triage == TriageBucket.FixableWithExistingResearch


def test_unlabeled_scenario_math_flags_scenario_math_unlabeled():
    """Scenario math and forecasts must be labeled."""

    Flag = classify_source_quality(
        ClaimEvidence(
            ClaimText="The stock will double if margins rise.",
            ClaimType=ClaimType.ScenarioMath,
            SourceQuality=SourceQuality.ReputableFinancialMedia,
            SupportsExactClaim=True,
            SourceUrl="https://example.com/source",
            HasScenarioLabel=False,
        )
    )

    assert Flag.Category == FactCheckCategory.ScenarioMathUnlabeled
    assert Flag.Severity == Severity.Warning
