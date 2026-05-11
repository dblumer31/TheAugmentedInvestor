"""Unit tests for core Pydantic pipeline contracts."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta, timezone

import pytest
from pydantic import ValidationError

from augmented_investor.external_search_client import SourceEvidence as SearchSourceEvidence
from augmented_investor.models import SourceEvidence
from augmented_investor.models.common import ClaimType, SourceQuality
from augmented_investor.models.fact_check import (
    ActualSourceQuality,
    FactCheckCategory,
    FactCheckReport,
    RequiredSourceQuality,
    Severity,
    TriageBucket,
    VerificationStatus,
)
from augmented_investor.models.research import ResearchBrief, ResearchClaim
from augmented_investor.models.run_artifact import RunArtifact
from augmented_investor.models.scope import ScopeRequest


def test_scope_request_validates_required_text():
    """Scope requests should reject blank required fields."""

    with pytest.raises(ValidationError, match="field must not be blank"):
        ScopeRequest(
            market=" ",
            recentWindow="last week",
            contextWindow="one year",
            readerHorizon="long term",
            readerType="investor",
            depth="standard",
            length="1200 words",
        )


def test_scope_request_accepts_prototype_field_names():
    """The model should accept lower-camel JSON from agent prompts."""

    Scope = ScopeRequest(
        market="AI infrastructure",
        recentWindow="last 30 days",
        contextWindow="three years",
        readerHorizon="long term",
        readerType="operator-investor",
        contrarianLean="skeptical",
        depth="deep",
        length="1500 words",
    )

    assert Scope.Market == "AI infrastructure"
    assert Scope.ContrarianLean == "skeptical"


def test_research_brief_uses_mutable_default_factories():
    """Separate model instances should not share list defaults."""

    First = ResearchBrief(topic="AI infrastructure")
    Second = ResearchBrief(topic="Energy")

    First.MarketSnapshot.append(
        ResearchClaim(
            claim="AI capex is rising",
            claimType=ClaimType.CompanyFinancial,
            source="10-K",
            sourceQuality=SourceQuality.CompanyFilingOrIr,
            supportsExactClaim=True,
            confidence="high",
        )
    )

    assert len(First.MarketSnapshot) == 1
    assert Second.MarketSnapshot == []


def test_source_evidence_is_canonical_for_search_client():
    """Search clients and model consumers should use the same SourceEvidence class."""

    assert SearchSourceEvidence is SourceEvidence


def test_source_evidence_rejects_naive_datetime_and_normalizes_offset():
    """Source evidence timestamps must be timezone-aware UTC."""

    with pytest.raises(ValidationError, match="timezone-aware"):
        SourceEvidence(
            source="test",
            sourceUrl="https://example.com",
            retrievedAt=datetime(2026, 5, 11),
        )

    EasternTime = timezone(timedelta(hours=-4))
    Evidence = SourceEvidence(
        source="test",
        sourceUrl="https://example.com",
        retrievedAt=datetime(2026, 5, 11, 12, 0, tzinfo=EasternTime),
        publishedAt=datetime(2026, 5, 10, 12, 0, tzinfo=EasternTime),
    )

    assert Evidence.RetrievedAt.tzinfo == UTC
    assert Evidence.RetrievedAt.hour == 16
    assert Evidence.PublishedAt is not None
    assert Evidence.PublishedAt.tzinfo == UTC


def test_fact_check_report_supports_complete_source_quality_summary():
    """Fact-check reports should preserve source-quality triage metadata."""

    Report = FactCheckReport(
        flags=[
            {
                "category": FactCheckCategory.WeakSourceForQuantClaim,
                "severity": Severity.Error,
                "excerpt": "The stock returned 42%.",
                "issue": "Quant claim is supported only by a blog.",
                "suggestion": "Use market data or remove the number.",
                "claimType": ClaimType.MarketReturn,
                "requiredSourceQuality": RequiredSourceQuality.PrimaryMarketData,
                "actualSourceQuality": ActualSourceQuality.BlogOrSubstack,
                "verificationStatus": VerificationStatus.NeedsPrimarySource,
                "triage": TriageBucket.NeedsResearchAddendum,
                "addendumQuery": "market return primary data",
            }
        ],
        sourceQualitySummary={
            "weakSourceFlags": 1,
            "unverifiedQuantClaims": 1,
            "blogOnlyClaims": 1,
            "overallSourceQuality": "weak",
        },
        overallScore="needs_work",
        summary="Needs stronger support.",
    )

    assert Report.Flags[0].Category == FactCheckCategory.WeakSourceForQuantClaim
    assert Report.SourceQualitySummary.WeakSourceFlags == 1
    assert Report.SourceQualitySummary.BlogOnlyClaims == 1


def test_run_artifact_requires_utc_created_at():
    """Run artifact timestamps should reject naive values."""

    with pytest.raises(ValidationError, match="timezone-aware"):
        RunArtifact(
            runId="run-1",
            stageName="research",
            path="runs/run-1/01_research.json",
            createdAt=datetime(2026, 5, 11),
            status="complete",
        )
