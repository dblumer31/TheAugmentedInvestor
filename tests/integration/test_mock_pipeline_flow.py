"""Mocked end-to-end operator flow for run review and export."""

from __future__ import annotations

from augmented_investor.models.draft import DraftIssue
from augmented_investor.models.fact_check import FactCheckReport
from augmented_investor.models.research import ResearchBrief
from augmented_investor.models.scope import ScopeRequest
from augmented_investor.models.thesis import ThesisBrief
from augmented_investor.operator_interface import build_review_state, export_run
from augmented_investor.pipeline.artifact_store import ArtifactStore
from augmented_investor.pipeline.orchestrator import PipelineOrchestrator


def test_mock_pipeline_flow_can_review_and_export_issue(tmp_path):
    """The interface slice should run through persisted artifacts without live providers."""

    Store = ArtifactStore(tmp_path)
    Orchestrator = PipelineOrchestrator(
        Store,
        research_stage=lambda scope: ResearchBrief(topic=scope.Market),
        thesis_stage=lambda research: ThesisBrief(
            centralThesis="A durable cycle is possible.",
            thesisBasis="Demand remains broad enough to monitor.",
            bullCase="Capacity demand accelerates.",
            baseCase="Demand normalizes but remains healthy.",
            bearCase="Overbuild pressures margins.",
            whatMispricing="The market may underweight durability.",
            contrarianTest="Does evidence support persistence?",
            newsletterAngle="Durability versus overbuild.",
            confidence="medium",
            confidenceRationale="Mocked evidence is limited.",
        ),
        writer_stage=lambda thesis, research, scope: DraftIssue(
            subjectLine="Subject",
            title="Title",
            subtitle="Subtitle",
            lede="Lede",
            body="<p>Original draft.</p>",
            sourcesUsed=[],
            wordCount=100,
        ),
        fact_check_stage=lambda draft, research: FactCheckReport(
            sourceQualitySummary={
                "weakSourceFlags": 0,
                "unverifiedQuantClaims": 0,
                "blogOnlyClaims": 0,
                "overallSourceQuality": "strong",
            },
            overallScore="clean",
            summary=f"Checked {draft.Title}.",
        ),
        fix_pass_stage=lambda draft, report: draft.model_copy(update={"Body": "<p>Fixed draft.</p>"}),
        export_stage=lambda draft: ("", ""),
    )
    Scope = ScopeRequest(
        market="AI infrastructure",
        recentWindow="last quarter",
        contextWindow="five years",
        readerHorizon="three years",
        readerType="generalist investors",
        depth="standard",
        length="1200",
    )

    RunId = Orchestrator.refine_scope(Scope)
    Orchestrator.run_research(RunId)
    Orchestrator.run_thesis(RunId)
    Orchestrator.approve_thesis(RunId)
    Orchestrator.write_draft(RunId)
    Orchestrator.fact_check_draft(RunId)
    Orchestrator.apply_fix_pass(RunId)
    Orchestrator.recheck_draft(RunId)

    Review = build_review_state(Store, RunId)
    Paths = export_run(Store, RunId)

    assert Review["currentDraft"]["Body"] == "<p>Fixed draft.</p>"
    assert Paths["html"].exists()
    assert Paths["markdown"].exists()
    assert "Fixed draft" in Paths["html"].read_text(encoding="utf-8")
    assert "Fixed draft" in Paths["markdown"].read_text(encoding="utf-8")
