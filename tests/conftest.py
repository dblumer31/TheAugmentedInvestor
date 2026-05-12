"""Shared pytest fixtures that avoid real environment files and secrets."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from augmented_investor.models.common import ClaimType, SourceQuality
from augmented_investor.models.draft import DraftIssue
from augmented_investor.models.fact_check import FactCheckReport
from augmented_investor.models.research import (
    ResearchBrief,
    ResearchClaim,
    ResearchSource,
)
from augmented_investor.models.scope import ScopeRequest
from augmented_investor.models.thesis import ThesisBrief
from augmented_investor.pipeline.artifact_store import ArtifactStore


@pytest.fixture
def fake_foundry_env() -> dict[str, str]:
    """Return fake Foundry environment variables safe for unit tests."""

    return {
        "AZURE_FOUNDRY_ENDPOINT": "https://example.services.ai.azure.com",
        "AZURE_FOUNDRY_API_KEY": "test-api-key",
        "FOUNDRY_DEFAULT_MODEL": "claude-opus-4-7",
        "FOUNDRY_SONNET_MODEL": "claude-sonnet-4-6",
        "FOUNDRY_OPUS_MODEL": "claude-opus-4-7",
        "FOUNDRY_ANTHROPIC_VERSION": "2023-06-01",
        "FOUNDRY_TIMEOUT_SECONDS": "120",
        "EXTERNAL_SEARCH_PROVIDER": "none",
    }


@pytest.fixture
def sample_scope() -> ScopeRequest:
    """Return a reusable valid scope for pipeline tests."""

    return ScopeRequest(
        market="AI infrastructure",
        recentWindow="last quarter",
        contextWindow="five years",
        readerHorizon="three years",
        readerType="generalist investors",
        depth="standard",
        length="1200",
    )


@pytest.fixture
def sample_research_brief() -> ResearchBrief:
    """Return reusable research with one source-backed claim."""

    return ResearchBrief(
        topic="AI infrastructure",
        marketSnapshot=[
            ResearchClaim(
                claim="AI capex remains elevated.",
                claimType=ClaimType.CompanyFinancial,
                source="Company filings",
                sourceQuality=SourceQuality.CompanyFilingOrIr,
                supportsExactClaim=True,
                quotedEvidence="Capex remains elevated.",
                confidence="medium",
            )
        ],
        sourceList=[
            ResearchSource(
                publication="Company filings",
                url="https://example.com/filing",
                sourceQuality=SourceQuality.CompanyFilingOrIr,
                supports="AI capex remains elevated.",
                supportsExactClaim=True,
                quotedEvidence="Capex remains elevated.",
            )
        ],
        recommendedAngle="Durability versus overbuild.",
    )


@pytest.fixture
def sample_thesis_brief() -> ThesisBrief:
    """Return a reusable thesis fixture."""

    return ThesisBrief(
        centralThesis="AI infrastructure demand may be more durable than expected.",
        thesisBasis="Company evidence suggests demand remains broad.",
        bullCase="Capacity demand accelerates.",
        baseCase="Demand normalizes but remains healthy.",
        bearCase="Overbuild pressures margins.",
        whatMispricing="The market may underweight durability.",
        contrarianTest="Does evidence support persistence?",
        newsletterAngle="Durability versus overbuild.",
        confidence="medium",
        confidenceRationale="The evidence is useful but incomplete.",
    )


@pytest.fixture
def sample_draft_issue() -> DraftIssue:
    """Return a reusable draft fixture."""

    return DraftIssue(
        subjectLine="AI infrastructure durability",
        title="The Durability Question",
        subtitle="A contrarian read",
        lede="AI demand may last longer than expected.",
        body="<p>AI infrastructure demand may be durable.</p>",
        sourcesUsed=["Company filings"],
        wordCount=120,
    )


@pytest.fixture
def sample_fact_check_report() -> FactCheckReport:
    """Return a reusable clean fact-check report."""

    return FactCheckReport(
        sourceQualitySummary={
            "weakSourceFlags": 0,
            "unverifiedQuantClaims": 0,
            "blogOnlyClaims": 0,
            "overallSourceQuality": "strong",
        },
        overallScore="clean",
        summary="No material issues found.",
    )


@pytest.fixture
def artifact_store(tmp_path) -> ArtifactStore:
    """Return an artifact store rooted in a temporary directory."""

    return ArtifactStore(tmp_path)
