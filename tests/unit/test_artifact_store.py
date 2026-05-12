"""Unit tests for run artifact persistence."""

from __future__ import annotations

from datetime import UTC

from augmented_investor.models.scope import ScopeRequest
from augmented_investor.pipeline.artifact_store import ArtifactStore


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


def test_create_run_generates_unique_run_ids(tmp_path):
    """Each run should receive a unique id and persisted state."""

    Store = ArtifactStore(tmp_path)

    FirstRun = Store.create_run()
    SecondRun = Store.create_run()

    assert FirstRun.RunId != SecondRun.RunId
    assert Store.run_path(FirstRun.RunId).exists()
    assert Store.run_path(SecondRun.RunId).exists()
    assert Store.load_state(FirstRun.RunId).RunId == FirstRun.RunId


def test_write_json_artifact_persists_structured_payload_and_updates_state(tmp_path):
    """Completed stage artifacts should be saved under the run folder."""

    Store = ArtifactStore(tmp_path)
    State = Store.create_run()

    Artifact = Store.write_json_artifact(State.RunId, "00_scope.json", _scope(), "scope")
    Payload = Store.read_json_artifact(State.RunId, "00_scope.json")
    UpdatedState = Store.load_state(State.RunId)

    assert Payload["Market"] == "AI infrastructure"
    assert Artifact.Path.endswith("00_scope.json")
    assert Artifact.CreatedAt.tzinfo == UTC
    assert UpdatedState.CurrentStage == "scope"
    assert UpdatedState.Artifacts["scope"] == "00_scope.json"


def test_text_exports_are_written_under_run_folder(tmp_path):
    """Export artifacts may be plain text rather than JSON."""

    Store = ArtifactStore(tmp_path)
    State = Store.create_run()

    HtmlPath = Store.write_text_artifact(State.RunId, "issue.html", "<h1>Issue</h1>", "export_html")
    MarkdownPath = Store.write_text_artifact(State.RunId, "issue.md", "# Issue", "export_markdown")

    assert HtmlPath.name == "issue.html"
    assert MarkdownPath.name == "issue.md"
    assert Store.read_text_artifact(State.RunId, "issue.html") == "<h1>Issue</h1>"
    assert Store.load_state(State.RunId).Artifacts["export_markdown"] == "issue.md"


def test_record_failure_preserves_existing_artifacts(tmp_path):
    """Failure state should not remove completed artifacts."""

    Store = ArtifactStore(tmp_path)
    State = Store.create_run()
    Store.write_json_artifact(State.RunId, "00_scope.json", _scope(), "scope")

    Store.record_failure(State.RunId, "research", RuntimeError("provider failed"))

    assert Store.artifact_path(State.RunId, "00_scope.json").exists()
    assert not Store.artifact_path(State.RunId, "01_research.json").exists()
    FailedState = Store.load_state(State.RunId)
    assert FailedState.FailedStage == "research"
    assert FailedState.FailureMessage == "provider failed"
