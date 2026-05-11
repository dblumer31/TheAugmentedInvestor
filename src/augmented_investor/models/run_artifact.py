"""Run artifact metadata model for persisted pipeline outputs."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import AliasChoices, Field, field_validator

from augmented_investor.models.common import StrictBaseModel, ensure_utc_datetime


class RunArtifact(StrictBaseModel):
    """Metadata for one persisted pipeline stage artifact."""

    RunId: str = Field(validation_alias=AliasChoices("RunId", "runId"))
    StageName: str = Field(validation_alias=AliasChoices("StageName", "stageName"))
    Path: str = Field(validation_alias=AliasChoices("Path", "path"))
    CreatedAt: datetime = Field(validation_alias=AliasChoices("CreatedAt", "createdAt"))
    Status: str = Field(validation_alias=AliasChoices("Status", "status"))
    ModelMetadata: dict[str, Any] = Field(
        default_factory=dict,
        validation_alias=AliasChoices("ModelMetadata", "modelMetadata"),
    )

    @field_validator("CreatedAt")
    @classmethod
    def _created_at_must_be_utc(cls, Value: datetime) -> datetime:
        """Require timezone-aware datetimes and normalize them to UTC."""

        return ensure_utc_datetime(Value)
