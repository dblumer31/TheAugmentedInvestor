"""Unit tests for fix-pass and re-check orchestration behavior."""

from __future__ import annotations

from tests.unit.test_orchestrator import _draft, _fact_check, _orchestrator, _scope


def test_recheck_persists_new_report_with_fixed_draft_counts(tmp_path):
    """Re-check should persist a new report using the fixed draft as input."""

    CheckedBodies = []

    def FactCheckStage(Draft, Research):
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
    Recheck = Orchestrator.recheck_draft(RunId)

    assert CheckedBodies == ["Original draft", "Fixed draft"]
    assert Recheck.Summary == "Checked Fixed draft"
    assert Orchestrator.artifact_store.artifact_path(RunId, "06_recheck.json").exists()


def test_recheck_flags_unresolved_high_severity_issue_again(tmp_path):
    """Unresolved fixed draft issues should be visible in the re-check artifact."""

    def FixPassStage(Draft, Report):
        return _draft("Original draft")

    Orchestrator = _orchestrator(tmp_path, fix_pass_stage=FixPassStage)
    RunId = Orchestrator.refine_scope(_scope())
    Orchestrator.run_research(RunId)
    Orchestrator.run_thesis(RunId)
    Orchestrator.approve_thesis(RunId)
    Orchestrator.write_draft(RunId)
    FirstReport = Orchestrator.fact_check_draft(RunId)
    Orchestrator.apply_fix_pass(RunId)
    Recheck = Orchestrator.recheck_draft(RunId)

    assert len(Recheck.Flags) == len(FirstReport.Flags)
    assert Recheck.OverallScore == FirstReport.OverallScore
