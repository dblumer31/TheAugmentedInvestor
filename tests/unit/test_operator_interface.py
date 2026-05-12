"""Unit tests for artifact-backed operator interface helpers."""

from __future__ import annotations

from augmented_investor.models.common import SourceQuality
from augmented_investor.models.draft import DraftIssue
from augmented_investor.models.fact_check import FactCheckReport
from augmented_investor.models.research import ResearchBrief, ResearchSource
from augmented_investor.models.scope import ScopeRequest
from augmented_investor.operator_interface import (
    build_review_state,
    create_run_from_scope,
    export_run,
)
from augmented_investor.pipeline.artifact_store import ArtifactStore
from augmented_investor.pipeline.orchestrator import (
    DRAFT_ARTIFACT,
    FACT_CHECK_ARTIFACT,
    FIXED_DRAFT_ARTIFACT,
    RESEARCH_ARTIFACT,
)


def _scope() -> ScopeRequest:
    """Return a valid scope fixture."""

    return ScopeRequest(
        market="AI infrastructure",
        recentWindow="last quarter",
        contextWindow="five years",
        readerHorizon="three years",
        readerType="generalist investors",
        depth="standard",
        length="1200",
    )


def _draft(body: str = "<p>Original draft.</p>") -> DraftIssue:
    """Return a draft fixture."""

    return DraftIssue(
        subjectLine="Subject",
        title="Title",
        subtitle="Subtitle",
        lede="Lede",
        body=body,
        sourcesUsed=["Source A"],
        wordCount=100,
    )


def _fact_check(summary: str = "Review.") -> FactCheckReport:
    """Return a valid fact-check fixture."""

    return FactCheckReport(
        sourceQualitySummary={
            "weakSourceFlags": 0,
            "unverifiedQuantClaims": 0,
            "blogOnlyClaims": 0,
            "overallSourceQuality": "strong",
        },
        overallScore="clean",
        summary=summary,
    )


def test_create_run_from_scope_persists_scope_and_status(tmp_path):
    """Scope entry should create a persisted run."""

    Store = ArtifactStore(tmp_path)

    RunId = create_run_from_scope(Store, _scope())
    Review = build_review_state(Store, RunId)

    assert Review["runId"] == RunId
    assert Review["state"]["RunId"] == RunId
    assert Review["currentDraft"] is None


def test_review_state_includes_current_draft_sources_fact_check_and_exports(tmp_path):
    """Review output should expose the editor's status bundle."""

    Store = ArtifactStore(tmp_path)
    RunId = create_run_from_scope(Store, _scope())
    Store.write_json_artifact(
        RunId,
        RESEARCH_ARTIFACT,
        ResearchBrief(
            topic="AI infrastructure",
            sourceList=[
                ResearchSource(
                    publication="Source A",
                    url="https://example.com/a",
                    sourceQuality=SourceQuality.ReputableFinancialMedia,
                    supports="Claim A",
                )
            ],
        ),
        "research",
    )
    Store.write_json_artifact(RunId, DRAFT_ARTIFACT, _draft(), "draft")
    Store.write_json_artifact(RunId, FACT_CHECK_ARTIFACT, _fact_check(), "fact_check")

    Review = build_review_state(Store, RunId)

    assert Review["currentDraft"]["Title"] == "Title"
    assert Review["sourceList"][0]["Publication"] == "Source A"
    assert Review["factCheckState"]["Summary"] == "Review."
    assert Review["exportOptions"] == {"html": "issue.html", "markdown": "issue.md"}


def test_export_run_uses_fixed_draft_when_available(tmp_path):
    """Export should use the current fixed draft rather than stale original draft."""

    Store = ArtifactStore(tmp_path)
    RunId = create_run_from_scope(Store, _scope())
    Store.write_json_artifact(RunId, DRAFT_ARTIFACT, _draft("<p>Original draft.</p>"), "draft")
    Store.write_json_artifact(RunId, FIXED_DRAFT_ARTIFACT, _draft("<p>Fixed draft.</p>"), "fixed_draft")

    Paths = export_run(Store, RunId)

    assert Paths["html"].name == "issue.html"
    assert Paths["markdown"].name == "issue.md"
    assert "Fixed draft" in Store.read_text_artifact(RunId, "issue.html")
    assert "Fixed draft" in Store.read_text_artifact(RunId, "issue.md")
