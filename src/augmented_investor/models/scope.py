"""Scope request contract for the first pipeline stage."""

from __future__ import annotations

from pydantic import AliasChoices, Field, field_validator

from augmented_investor.models.common import StrictBaseModel


class ScopeRequest(StrictBaseModel):
    """Validated editorial scope input for a newsletter run."""

    Market: str = Field(validation_alias=AliasChoices("Market", "market"))
    RecentWindow: str = Field(validation_alias=AliasChoices("RecentWindow", "recentWindow"))
    ContextWindow: str = Field(validation_alias=AliasChoices("ContextWindow", "contextWindow"))
    ReaderHorizon: str = Field(validation_alias=AliasChoices("ReaderHorizon", "readerHorizon"))
    ReaderType: str = Field(validation_alias=AliasChoices("ReaderType", "readerType"))
    ContrarianLean: str | None = Field(
        default=None,
        validation_alias=AliasChoices("ContrarianLean", "contrarianLean"),
    )
    Depth: str = Field(validation_alias=AliasChoices("Depth", "depth"))
    Length: str = Field(validation_alias=AliasChoices("Length", "length"))

    @field_validator(
        "Market",
        "RecentWindow",
        "ContextWindow",
        "ReaderHorizon",
        "ReaderType",
        "Depth",
        "Length",
    )
    @classmethod
    def _required_text_must_not_be_blank(cls, Value: str) -> str:
        """Reject blank required scope text."""

        CleanValue = Value.strip()
        if not CleanValue:
            raise ValueError("field must not be blank")
        return CleanValue

    @field_validator("ContrarianLean")
    @classmethod
    def _optional_text_is_trimmed(cls, Value: str | None) -> str | None:
        """Normalize optional scope text without making it required."""

        if Value is None:
            return None
        CleanValue = Value.strip()
        return CleanValue or None
