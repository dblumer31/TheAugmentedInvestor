"""Pipeline orchestration with persisted stage boundaries and approval gates."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from augmented_investor.models.draft import DraftIssue
from augmented_investor.models.fact_check import FactCheckReport
from augmented_investor.models.research import ResearchBrief
from augmented_investor.models.scope import ScopeRequest
from augmented_investor.models.thesis import ThesisBrief
from augmented_investor.pipeline.artifact_store import ArtifactStore


SCOPE_ARTIFACT = "00_scope.json"
RESEARCH_ARTIFACT = "01_research.json"
THESIS_ARTIFACT = "02_thesis.json"
DRAFT_ARTIFACT = "03_draft.json"
FACT_CHECK_ARTIFACT = "04_fact_check.json"
FIXED_DRAFT_ARTIFACT = "05_fixed_draft.json"
RECHECK_ARTIFACT = "06_recheck.json"
HTML_EXPORT = "issue.html"
MARKDOWN_EXPORT = "issue.md"


class PipelineStateError(RuntimeError):
    """Raised when a pipeline stage is requested out of order."""


class PipelineOrchestrator:
    """Run pipeline stages in order while persisting every completed artifact."""

    def __init__(
        self,
        artifact_store: ArtifactStore,
        research_stage: Callable[[ScopeRequest], ResearchBrief],
        thesis_stage: Callable[[ResearchBrief], ThesisBrief],
        writer_stage: Callable[[ThesisBrief, ResearchBrief, ScopeRequest], DraftIssue],
        fact_check_stage: Callable[[DraftIssue, ResearchBrief], FactCheckReport],
        fix_pass_stage: Callable[[DraftIssue, FactCheckReport], DraftIssue],
        export_stage: Callable[[DraftIssue], tuple[str, str]],
    ) -> None:
        self.artifact_store = artifact_store
        self._research_stage = research_stage
        self._thesis_stage = thesis_stage
        self._writer_stage = writer_stage
        self._fact_check_stage = fact_check_stage
        self._fix_pass_stage = fix_pass_stage
        self._export_stage = export_stage

    def refine_scope(self, scope: ScopeRequest) -> str:
        """Create a run and persist the validated scope artifact."""

        State = self.artifact_store.create_run()
        self.artifact_store.write_json_artifact(State.RunId, SCOPE_ARTIFACT, scope, "scope")
        return State.RunId

    def run_research(self, run_id: str) -> ResearchBrief:
        """Run research after scope has been persisted."""

        self._require_artifact(run_id, SCOPE_ARTIFACT, "scope")
        Scope = ScopeRequest.model_validate(
            self.artifact_store.read_json_artifact(run_id, SCOPE_ARTIFACT)
        )
        return self._run_stage(
            run_id,
            "research",
            lambda: self._research_stage(Scope),
            RESEARCH_ARTIFACT,
        )

    def run_thesis(self, run_id: str) -> ThesisBrief:
        """Run thesis generation after research has completed."""

        Research = self._load_research(run_id)
        return self._run_stage(
            run_id,
            "thesis",
            lambda: self._thesis_stage(Research),
            THESIS_ARTIFACT,
        )

    def approve_thesis(self, run_id: str) -> None:
        """Persist human thesis approval for a run."""

        self._require_artifact(run_id, THESIS_ARTIFACT, "thesis")
        self.artifact_store.mark_thesis_approved(run_id, approved=True)

    def reject_thesis(self, run_id: str, reason: str | None = None) -> None:
        """Persist human thesis rejection for a run."""

        self._require_artifact(run_id, THESIS_ARTIFACT, "thesis")
        self.artifact_store.mark_thesis_rejected(run_id, reason)

    def restart_from_scope(
        self,
        run_id: str,
        scope: ScopeRequest,
        reason: str | None = None,
    ) -> str:
        """Reject the current thesis and start a new run from supplied scope."""

        self.reject_thesis(run_id, reason)
        return self.refine_scope(scope)

    def write_draft(self, run_id: str) -> DraftIssue:
        """Generate a draft only after thesis approval is persisted."""

        State = self.artifact_store.load_state(run_id)
        if not State.ThesisApproved:
            raise PipelineStateError("Thesis must be approved before writer stage can run")
        Thesis = self._load_thesis(run_id)
        Research = self._load_research(run_id)
        Scope = self._load_scope(run_id)
        return self._run_stage(
            run_id,
            "draft",
            lambda: self._writer_stage(Thesis, Research, Scope),
            DRAFT_ARTIFACT,
        )

    def fact_check_draft(self, run_id: str) -> FactCheckReport:
        """Fact-check the original draft against research evidence."""

        Draft = self._load_draft(run_id, DRAFT_ARTIFACT)
        Research = self._load_research(run_id)
        return self._run_stage(
            run_id,
            "fact_check",
            lambda: self._fact_check_stage(Draft, Research),
            FACT_CHECK_ARTIFACT,
        )

    def apply_fix_pass(self, run_id: str) -> DraftIssue:
        """Apply the fix pass to the original draft and fact-check report."""

        Draft = self._load_draft(run_id, DRAFT_ARTIFACT)
        Report = self._load_fact_check(run_id, FACT_CHECK_ARTIFACT)
        return self._run_stage(
            run_id,
            "fixed_draft",
            lambda: self._fix_pass_stage(Draft, Report),
            FIXED_DRAFT_ARTIFACT,
        )

    def recheck_draft(self, run_id: str) -> FactCheckReport:
        """Run re-check against the fixed draft artifact."""

        FixedDraft = self._load_draft(run_id, FIXED_DRAFT_ARTIFACT)
        Research = self._load_research(run_id)
        return self._run_stage(
            run_id,
            "recheck",
            lambda: self._fact_check_stage(FixedDraft, Research),
            RECHECK_ARTIFACT,
        )

    def export_issue(self, run_id: str) -> dict[str, Path]:
        """Export the final fixed draft to HTML and Markdown artifacts."""

        FixedDraft = self._load_draft(run_id, FIXED_DRAFT_ARTIFACT)
        try:
            HtmlContent, MarkdownContent = self._export_stage(FixedDraft)
        except Exception as Error:
            self.artifact_store.record_failure(run_id, "export", Error)
            raise
        HtmlPath = self.artifact_store.write_text_artifact(
            run_id,
            HTML_EXPORT,
            HtmlContent,
            "export_html",
        )
        MarkdownPath = self.artifact_store.write_text_artifact(
            run_id,
            MARKDOWN_EXPORT,
            MarkdownContent,
            "export_markdown",
        )
        return {"html": HtmlPath, "markdown": MarkdownPath}

    def _run_stage(
        self,
        run_id: str,
        stage_name: str,
        stage_function: Callable[[], object],
        artifact_filename: str,
    ):
        """Execute one stage, write its artifact on success, and persist failures."""

        try:
            Result = stage_function()
        except Exception as Error:
            self.artifact_store.record_failure(run_id, stage_name, Error)
            raise
        self.artifact_store.write_json_artifact(run_id, artifact_filename, Result, stage_name)
        return Result

    def _load_scope(self, run_id: str) -> ScopeRequest:
        """Load the persisted scope artifact."""

        self._require_artifact(run_id, SCOPE_ARTIFACT, "scope")
        return ScopeRequest.model_validate(
            self.artifact_store.read_json_artifact(run_id, SCOPE_ARTIFACT)
        )

    def _load_research(self, run_id: str) -> ResearchBrief:
        """Load the persisted research artifact."""

        self._require_artifact(run_id, RESEARCH_ARTIFACT, "research")
        return ResearchBrief.model_validate(
            self.artifact_store.read_json_artifact(run_id, RESEARCH_ARTIFACT)
        )

    def _load_thesis(self, run_id: str) -> ThesisBrief:
        """Load the persisted thesis artifact."""

        self._require_artifact(run_id, THESIS_ARTIFACT, "thesis")
        return ThesisBrief.model_validate(
            self.artifact_store.read_json_artifact(run_id, THESIS_ARTIFACT)
        )

    def _load_draft(self, run_id: str, artifact_filename: str) -> DraftIssue:
        """Load a draft artifact by filename."""

        self._require_artifact(run_id, artifact_filename, artifact_filename)
        return DraftIssue.model_validate(
            self.artifact_store.read_json_artifact(run_id, artifact_filename)
        )

    def _load_fact_check(self, run_id: str, artifact_filename: str) -> FactCheckReport:
        """Load a fact-check report artifact by filename."""

        self._require_artifact(run_id, artifact_filename, artifact_filename)
        return FactCheckReport.model_validate(
            self.artifact_store.read_json_artifact(run_id, artifact_filename)
        )

    def _require_artifact(self, run_id: str, filename: str, stage_name: str) -> None:
        """Require a prior stage artifact before continuing."""

        if not self.artifact_store.artifact_path(run_id, filename).exists():
            raise PipelineStateError(f"Required {stage_name} artifact is missing")
