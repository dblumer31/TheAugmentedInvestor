"""Thin operator-interface helpers backed by persisted run artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from augmented_investor.exporters.html_exporter import export_html
from augmented_investor.exporters.markdown_exporter import export_markdown
from augmented_investor.models.draft import DraftIssue
from augmented_investor.models.fact_check import FactCheckReport
from augmented_investor.models.research import ResearchBrief
from augmented_investor.models.scope import ScopeRequest
from augmented_investor.pipeline.artifact_store import ArtifactStore
from augmented_investor.pipeline.orchestrator import (
    DRAFT_ARTIFACT,
    FACT_CHECK_ARTIFACT,
    FIXED_DRAFT_ARTIFACT,
    HTML_EXPORT,
    MARKDOWN_EXPORT,
    RECHECK_ARTIFACT,
    RESEARCH_ARTIFACT,
)


def create_run_from_scope(artifact_store: ArtifactStore, scope: ScopeRequest) -> str:
    """Create a run from validated scope input."""

    State = artifact_store.create_run()
    artifact_store.write_json_artifact(State.RunId, "00_scope.json", scope, "scope")
    return State.RunId


def approve_thesis(artifact_store: ArtifactStore, run_id: str) -> dict[str, Any]:
    """Persist thesis approval and return updated run state."""

    artifact_store.mark_thesis_approved(run_id, approved=True)
    return artifact_store.load_state(run_id).model_dump(mode="json")


def reject_thesis(artifact_store: ArtifactStore, run_id: str, reason: str | None) -> dict[str, Any]:
    """Persist thesis rejection and return updated run state."""

    artifact_store.mark_thesis_rejected(run_id, reason)
    return artifact_store.load_state(run_id).model_dump(mode="json")


def build_review_state(artifact_store: ArtifactStore, run_id: str) -> dict[str, Any]:
    """Return the editor review bundle for the current run."""

    Draft = _load_current_draft(artifact_store, run_id)
    Research = _load_optional_model(artifact_store, run_id, RESEARCH_ARTIFACT, ResearchBrief)
    Report = _load_optional_model(artifact_store, run_id, RECHECK_ARTIFACT, FactCheckReport)
    if Report is None:
        Report = _load_optional_model(artifact_store, run_id, FACT_CHECK_ARTIFACT, FactCheckReport)
    return {
        "runId": run_id,
        "state": artifact_store.load_state(run_id).model_dump(mode="json"),
        "currentDraft": Draft.model_dump(mode="json") if Draft else None,
        "sourceList": _source_list(Research),
        "factCheckState": Report.model_dump(mode="json") if Report else None,
        "exportOptions": {"html": HTML_EXPORT, "markdown": MARKDOWN_EXPORT},
    }


def export_run(artifact_store: ArtifactStore, run_id: str) -> dict[str, Path]:
    """Write HTML and Markdown exports from the current draft artifact."""

    Draft = _load_current_draft(artifact_store, run_id)
    if Draft is None:
        raise ValueError("A draft or fixed draft artifact is required before export")
    Research = _load_optional_model(artifact_store, run_id, RESEARCH_ARTIFACT, ResearchBrief)
    Report = _load_optional_model(artifact_store, run_id, RECHECK_ARTIFACT, FactCheckReport)
    if Report is None:
        Report = _load_optional_model(artifact_store, run_id, FACT_CHECK_ARTIFACT, FactCheckReport)
    HtmlPath = artifact_store.write_text_artifact(
        run_id,
        HTML_EXPORT,
        export_html(Draft, Research, Report),
        "export_html",
    )
    MarkdownPath = artifact_store.write_text_artifact(
        run_id,
        MARKDOWN_EXPORT,
        export_markdown(Draft, Research, Report),
        "export_markdown",
    )
    return {"html": HtmlPath, "markdown": MarkdownPath}


def _load_current_draft(artifact_store: ArtifactStore, run_id: str) -> DraftIssue | None:
    """Load the fixed draft when available, otherwise the original draft."""

    FixedDraft = _load_optional_model(artifact_store, run_id, FIXED_DRAFT_ARTIFACT, DraftIssue)
    if FixedDraft is not None:
        return FixedDraft
    return _load_optional_model(artifact_store, run_id, DRAFT_ARTIFACT, DraftIssue)


def _load_optional_model(artifact_store: ArtifactStore, run_id: str, filename: str, model_type):
    """Load and validate an optional artifact model."""

    if not artifact_store.artifact_path(run_id, filename).exists():
        return None
    return model_type.model_validate(artifact_store.read_json_artifact(run_id, filename))


def _source_list(research: ResearchBrief | None) -> list[dict[str, Any]]:
    """Return source metadata for review output."""

    if research is None:
        return []
    return [Source.model_dump(mode="json") for Source in research.SourceList]
