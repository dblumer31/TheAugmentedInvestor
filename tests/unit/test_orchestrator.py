"""Unit tests for pipeline stage ordering and approval gates."""

from __future__ import annotations

import pytest

from augmented_investor.models.common import ClaimType, SourceQuality
from augmented_investor.models.draft import DraftIssue
from augmented_investor.models.fact_check import FactCheckReport
from augmented_investor.models.research import ResearchBrief, ResearchClaim
from augmented_investor.models.scope import ScopeRequest
from augmented_investor.models.thesis import ThesisBrief
from augmented_investor.pipeline.artifact_store import ArtifactStore
from augmented_investor.pipeline.orchestrator import PipelineOrchestrator, PipelineStateError


def _scope() -> ScopeRequest:
    """Return a valid scope fixture."""

    return ScopeRequest(
        market="AI infrastructure",
        recentWindow="last 30 days",
        contextWindow="three years",
        readerHorizon="long term",
        readerType="operator-investor",
        depth="deep",
        length="1500 words",
    )


def _research() -> ResearchBrief:
    """Return a minimal valid research brief."""

    return ResearchBrief(
        topic="AI infrastructure",
        marketSnapshot=[
            ResearchClaim(
                claim="AI capex is rising",
                claimType=ClaimType.CompanyFinancial,
                source="10-K",
                sourceQuality=SourceQuality.CompanyFilingOrIr,
                supportsExactClaim=True,
                confidence="high",
            )
        ],
    )


def _thesis() -> ThesisBrief:
    """Return a minimal valid thesis brief."""

    return ThesisBrief(
        centralThesis="AI infrastructure demand is durable.",
        thesisBasis="Capex and utilization support the thesis.",
        bullCase="Demand accelerates.",
        baseCase="Demand remains steady.",
        bearCase="Capacity overshoots demand.",
        whatMispricing="The market may underprice durability.",
        contrarianTest="What if capex is cyclical?",
        newsletterAngle="Durability versus cyclicality.",
        confidence="medium",
        confidenceRationale="Evidence is early but consistent.",
    )


def _draft(body: str = "Draft body") -> DraftIssue:
    """Return a minimal valid draft."""

    return DraftIssue(
        subjectLine="AI infrastructure durability",
        title="The Durability Question",
        subtitle="A contrarian read",
        lede="Demand may last longer than expected.",
        body=body,
        sourcesUsed=["10-K"],
        wordCount=100,
    )


def _fact_check(summary: str = "Clean") -> FactCheckReport:
    """Return a minimal fact-check report."""

    return FactCheckReport(
        flags=[],
        sourceQualitySummary={
            "weakSourceFlags": 0,
            "unverifiedQuantClaims": 0,
            "blogOnlyClaims": 0,
            "overallSourceQuality": "strong",
        },
        overallScore="clean",
        summary=summary,
    )


def _orchestrator(tmp_path, **overrides) -> PipelineOrchestrator:
    """Build an orchestrator with deterministic fake stage functions."""

    Defaults = {
        "research_stage": lambda scope: _research(),
        "thesis_stage": lambda research: _thesis(),
        "writer_stage": lambda thesis, research, scope: _draft("Original draft"),
        "fact_check_stage": lambda draft, research: _fact_check(f"Checked {draft.Body}"),
        "fix_pass_stage": lambda draft, report: _draft("Fixed draft"),
        "export_stage": lambda draft: ("<h1>Issue</h1>", "# Issue"),
    }
    Defaults.update(overrides)
    return PipelineOrchestrator(ArtifactStore(tmp_path), **Defaults)


def test_orchestrator_runs_stages_and_persists_expected_artifacts(tmp_path):
    """The orchestrator should enforce the documented stage file contract."""

    Orchestrator = _orchestrator(tmp_path)

    RunId = Orchestrator.refine_scope(_scope())
    Orchestrator.run_research(RunId)
    Orchestrator.run_thesis(RunId)
    Orchestrator.approve_thesis(RunId)
    Orchestrator.write_draft(RunId)
    Orchestrator.fact_check_draft(RunId)
    Orchestrator.apply_fix_pass(RunId)
    Orchestrator.recheck_draft(RunId)
    ExportPaths = Orchestrator.export_issue(RunId)

    RunPath = Orchestrator.artifact_store.run_path(RunId)
    ExpectedFiles = [
        "00_scope.json",
        "01_research.json",
        "02_thesis.json",
        "03_draft.json",
        "04_fact_check.json",
        "05_fixed_draft.json",
        "06_recheck.json",
        "issue.html",
        "issue.md",
    ]
    assert all((RunPath / FileName).exists() for FileName in ExpectedFiles)
    assert ExportPaths["html"].name == "issue.html"
    assert Orchestrator.artifact_store.load_state(RunId).ThesisApproved is True


def test_writer_cannot_run_until_thesis_is_approved(tmp_path):
    """Draft generation must be blocked before approval is persisted."""

    Orchestrator = _orchestrator(tmp_path)
    RunId = Orchestrator.refine_scope(_scope())
    Orchestrator.run_research(RunId)
    Orchestrator.run_thesis(RunId)

    with pytest.raises(PipelineStateError, match="approved"):
        Orchestrator.write_draft(RunId)

    assert not Orchestrator.artifact_store.artifact_path(RunId, "03_draft.json").exists()


def test_writer_receives_original_scope_after_approval(tmp_path):
    """Writer stage should receive scope so draft generation can preserve audience inputs."""

    CapturedScope = {}

    def WriterStage(
        Thesis: ThesisBrief,
        Research: ResearchBrief,
        Scope: ScopeRequest,
    ) -> DraftIssue:
        CapturedScope["reader_type"] = Scope.ReaderType
        CapturedScope["length"] = Scope.Length
        return _draft("Original draft")

    Orchestrator = _orchestrator(tmp_path, writer_stage=WriterStage)
    RunId = Orchestrator.refine_scope(_scope())
    Orchestrator.run_research(RunId)
    Orchestrator.run_thesis(RunId)
    Orchestrator.approve_thesis(RunId)
    Orchestrator.write_draft(RunId)

    assert CapturedScope == {"reader_type": "operator-investor", "length": "1500 words"}


def test_reject_thesis_blocks_writer_and_persists_reason(tmp_path):
    """Rejected thesis state should be persisted and block draft generation."""

    Orchestrator = _orchestrator(tmp_path)
    RunId = Orchestrator.refine_scope(_scope())
    Orchestrator.run_research(RunId)
    Orchestrator.run_thesis(RunId)

    Orchestrator.reject_thesis(RunId, "Needs sharper angle")

    State = Orchestrator.artifact_store.load_state(RunId)
    assert State.ThesisApproved is False
    assert State.ThesisRejected is True
    assert State.ThesisRejectionReason == "Needs sharper angle"
    with pytest.raises(PipelineStateError, match="approved"):
        Orchestrator.write_draft(RunId)


def test_restart_from_scope_keeps_original_run_rejected_and_creates_new_run(tmp_path):
    """Restart should preserve old run audit state and create a fresh scope run."""

    Orchestrator = _orchestrator(tmp_path)
    OriginalRunId = Orchestrator.refine_scope(_scope())
    Orchestrator.run_research(OriginalRunId)
    Orchestrator.run_thesis(OriginalRunId)

    NewRunId = Orchestrator.restart_from_scope(OriginalRunId, _scope(), "Restart thesis")

    OriginalState = Orchestrator.artifact_store.load_state(OriginalRunId)
    assert OriginalState.ThesisRejected is True
    assert OriginalState.ThesisRejectionReason == "Restart thesis"
    assert NewRunId != OriginalRunId
    assert Orchestrator.artifact_store.artifact_path(NewRunId, "00_scope.json").exists()


def test_recheck_uses_fixed_draft_not_original_draft(tmp_path):
    """Re-check must consume the fixed draft artifact."""

    CheckedBodies = []

    def FactCheckStage(Draft: DraftIssue, Research: ResearchBrief) -> FactCheckReport:
        CheckedBodies.append(Draft.Body)
        return _fact_check(f"Checked {Draft.Body}")

    Orchestrator = _orchestrator(tmp_path, fact_check_stage=FactCheckStage)
    RunId = Orchestrator.refine_scope(_scope())
    Orchestrator.run_research(RunId)
    Orchestrator.run_thesis(RunId)
    Orchestrator.approve_thesis(RunId)
    Orchestrator.write_draft(RunId)
    Orchestrator.fact_check_draft(RunId)
    Orchestrator.apply_fix_pass(RunId)
    Orchestrator.recheck_draft(RunId)

    assert CheckedBodies == ["Original draft", "Fixed draft"]


def test_failed_stage_preserves_earlier_artifacts_and_records_state(tmp_path):
    """A failed stage should leave prior artifacts intact and persist failure metadata."""

    def BrokenResearch(Scope: ScopeRequest) -> ResearchBrief:
        raise RuntimeError("research failed")

    Orchestrator = _orchestrator(tmp_path, research_stage=BrokenResearch)
    RunId = Orchestrator.refine_scope(_scope())

    with pytest.raises(RuntimeError, match="research failed"):
        Orchestrator.run_research(RunId)

    Store = Orchestrator.artifact_store
    assert Store.artifact_path(RunId, "00_scope.json").exists()
    assert not Store.artifact_path(RunId, "01_research.json").exists()
    State = Store.load_state(RunId)
    assert State.FailedStage == "research"
    assert State.FailureMessage == "research failed"
