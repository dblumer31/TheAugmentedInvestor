"""Local JSON and text artifact persistence for pipeline runs."""

from __future__ import annotations

from datetime import UTC, datetime
import json
from pathlib import Path
from typing import Any
from uuid import uuid4

from pydantic import AliasChoices, BaseModel, Field, field_validator

from augmented_investor.models.common import StrictBaseModel, ensure_utc_datetime
from augmented_investor.models.run_artifact import RunArtifact


STATE_FILENAME = "run_state.json"


class RunState(StrictBaseModel):
    """Persisted state for one pipeline run."""

    RunId: str = Field(validation_alias=AliasChoices("RunId", "runId"))
    CreatedAt: datetime = Field(validation_alias=AliasChoices("CreatedAt", "createdAt"))
    UpdatedAt: datetime = Field(validation_alias=AliasChoices("UpdatedAt", "updatedAt"))
    CurrentStage: str | None = Field(
        default=None,
        validation_alias=AliasChoices("CurrentStage", "currentStage"),
    )
    ThesisApproved: bool = Field(
        default=False,
        validation_alias=AliasChoices("ThesisApproved", "thesisApproved"),
    )
    ThesisRejected: bool = Field(
        default=False,
        validation_alias=AliasChoices("ThesisRejected", "thesisRejected"),
    )
    ThesisRejectionReason: str | None = Field(
        default=None,
        validation_alias=AliasChoices("ThesisRejectionReason", "thesisRejectionReason"),
    )
    FailedStage: str | None = Field(
        default=None,
        validation_alias=AliasChoices("FailedStage", "failedStage"),
    )
    FailureMessage: str | None = Field(
        default=None,
        validation_alias=AliasChoices("FailureMessage", "failureMessage"),
    )
    Artifacts: dict[str, str] = Field(
        default_factory=dict,
        validation_alias=AliasChoices("Artifacts", "artifacts"),
    )

    @field_validator("CreatedAt", "UpdatedAt")
    @classmethod
    def _datetime_must_be_utc(cls, Value: datetime) -> datetime:
        """Require timezone-aware datetimes and normalize them to UTC."""

        return ensure_utc_datetime(Value)


class ArtifactStore:
    """Store and load run artifacts under a local runs directory."""

    def __init__(self, base_path: str | Path = "runs") -> None:
        self.base_path = Path(base_path)

    def create_run(self, run_id: str | None = None) -> RunState:
        """Create a new run directory and initial state."""

        RunId = run_id or self.create_run_id()
        CreatedAt = _utc_now()
        State = RunState(RunId=RunId, CreatedAt=CreatedAt, UpdatedAt=CreatedAt)
        self.run_path(RunId).mkdir(parents=True, exist_ok=False)
        self.save_state(State)
        return State

    def create_run_id(self) -> str:
        """Return a unique run identifier."""

        return uuid4().hex

    def run_path(self, run_id: str) -> Path:
        """Return the folder path for a run id."""

        return self.base_path / run_id

    def artifact_path(self, run_id: str, filename: str) -> Path:
        """Return a path inside a run directory."""

        _validate_artifact_filename(filename)
        return self.run_path(run_id) / filename

    def write_json_artifact(
        self,
        run_id: str,
        filename: str,
        payload: BaseModel | dict[str, Any],
        stage_name: str,
    ) -> RunArtifact:
        """Write a structured artifact and update run state."""

        ArtifactPath = self.artifact_path(run_id, filename)
        ArtifactPath.parent.mkdir(parents=True, exist_ok=True)
        Payload = _json_ready_payload(payload)
        _write_json_atomic(ArtifactPath, Payload)
        self._record_artifact(run_id, stage_name, filename)
        return RunArtifact(
            RunId=run_id,
            StageName=stage_name,
            Path=str(ArtifactPath),
            CreatedAt=_utc_now(),
            Status="complete",
        )

    def read_json_artifact(self, run_id: str, filename: str) -> dict[str, Any]:
        """Read a structured artifact from a run directory."""

        with self.artifact_path(run_id, filename).open("r", encoding="utf-8") as ArtifactFile:
            Payload = json.load(ArtifactFile)
        if not isinstance(Payload, dict):
            raise ValueError(f"Artifact {filename} must contain a JSON object")
        return Payload

    def write_text_artifact(self, run_id: str, filename: str, content: str, stage_name: str) -> Path:
        """Write a text artifact such as an HTML or Markdown export."""

        ArtifactPath = self.artifact_path(run_id, filename)
        ArtifactPath.parent.mkdir(parents=True, exist_ok=True)
        _write_text_atomic(ArtifactPath, content)
        self._record_artifact(run_id, stage_name, filename)
        return ArtifactPath

    def read_text_artifact(self, run_id: str, filename: str) -> str:
        """Read a text artifact from a run directory."""

        return self.artifact_path(run_id, filename).read_text(encoding="utf-8")

    def load_state(self, run_id: str) -> RunState:
        """Load persisted state for a run."""

        StatePayload = self.read_json_artifact(run_id, STATE_FILENAME)
        return RunState.model_validate(StatePayload)

    def save_state(self, state: RunState) -> RunState:
        """Persist run state using an atomic replace."""

        UpdatedState = state.model_copy(update={"UpdatedAt": _utc_now()})
        StatePath = self.artifact_path(UpdatedState.RunId, STATE_FILENAME)
        StatePath.parent.mkdir(parents=True, exist_ok=True)
        _write_json_atomic(StatePath, UpdatedState.model_dump(mode="json"))
        return UpdatedState

    def mark_thesis_approved(self, run_id: str, approved: bool = True) -> RunState:
        """Persist the human thesis approval decision."""

        State = self.load_state(run_id)
        UpdatedState = State.model_copy(
            update={
                "CurrentStage": "approve_thesis",
                "ThesisApproved": approved,
                "ThesisRejected": False,
                "ThesisRejectionReason": None,
                "FailedStage": None,
                "FailureMessage": None,
            }
        )
        return self.save_state(UpdatedState)

    def mark_thesis_rejected(self, run_id: str, reason: str | None = None) -> RunState:
        """Persist a human thesis rejection decision."""

        State = self.load_state(run_id)
        UpdatedState = State.model_copy(
            update={
                "CurrentStage": "reject_thesis",
                "ThesisApproved": False,
                "ThesisRejected": True,
                "ThesisRejectionReason": reason,
                "FailedStage": None,
                "FailureMessage": None,
            }
        )
        return self.save_state(UpdatedState)

    def record_failure(self, run_id: str, stage_name: str, error: Exception) -> RunState:
        """Persist failure metadata without deleting earlier artifacts."""

        State = self.load_state(run_id)
        UpdatedState = State.model_copy(
            update={
                "CurrentStage": stage_name,
                "FailedStage": stage_name,
                "FailureMessage": str(error),
            }
        )
        return self.save_state(UpdatedState)

    def _record_artifact(self, run_id: str, stage_name: str, filename: str) -> RunState:
        """Update state after a stage artifact is written."""

        State = self.load_state(run_id)
        Artifacts = dict(State.Artifacts)
        Artifacts[stage_name] = filename
        UpdatedState = State.model_copy(
            update={
                "CurrentStage": stage_name,
                "FailedStage": None,
                "FailureMessage": None,
                "Artifacts": Artifacts,
            }
        )
        return self.save_state(UpdatedState)


def _json_ready_payload(payload: BaseModel | dict[str, Any]) -> dict[str, Any]:
    """Convert supported payloads into JSON-serializable dictionaries."""

    if isinstance(payload, BaseModel):
        return payload.model_dump(mode="json")
    return payload


def _write_json_atomic(path: Path, payload: dict[str, Any]) -> None:
    """Write JSON via a temporary file and atomic replace."""

    TempPath = path.with_name(f".{path.name}.tmp")
    TempPath.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    TempPath.replace(path)


def _write_text_atomic(path: Path, content: str) -> None:
    """Write text via a temporary file and atomic replace."""

    TempPath = path.with_name(f".{path.name}.tmp")
    TempPath.write_text(content, encoding="utf-8")
    TempPath.replace(path)


def _validate_artifact_filename(filename: str) -> None:
    """Prevent artifact writes outside the run directory."""

    if Path(filename).name != filename:
        raise ValueError("artifact filename must not contain path separators")


def _utc_now() -> datetime:
    """Return the current timezone-aware UTC datetime."""

    return datetime.now(UTC)
