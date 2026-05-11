"""Draft-stage contract for generated newsletter issues."""

from __future__ import annotations

from pydantic import AliasChoices, Field, field_validator

from augmented_investor.models.common import StrictBaseModel


class DraftIssue(StrictBaseModel):
    """Generated newsletter draft and review metadata."""

    IssueNumber: str | None = Field(
        default=None,
        validation_alias=AliasChoices("IssueNumber", "issueNumber", "issue_number"),
    )
    Date: str | None = Field(default=None, validation_alias=AliasChoices("Date", "date"))
    SubjectLine: str = Field(
        validation_alias=AliasChoices("SubjectLine", "subjectLine", "subject_line"),
    )
    Title: str = Field(validation_alias=AliasChoices("Title", "title"))
    Subtitle: str = Field(validation_alias=AliasChoices("Subtitle", "subtitle"))
    Lede: str = Field(validation_alias=AliasChoices("Lede", "lede"))
    Body: str = Field(validation_alias=AliasChoices("Body", "body", "bodyHtml"))
    SourcesUsed: list[str] = Field(
        default_factory=list,
        validation_alias=AliasChoices("SourcesUsed", "sourcesUsed", "sources_used"),
    )
    WordCount: int = Field(validation_alias=AliasChoices("WordCount", "wordCount", "word_count"))
    ContrarianScore: str | None = Field(
        default=None,
        validation_alias=AliasChoices("ContrarianScore", "contrarianScore"),
    )

    @field_validator("WordCount")
    @classmethod
    def _word_count_must_not_be_negative(cls, Value: int) -> int:
        """Reject negative word counts."""

        if Value < 0:
            raise ValueError("WordCount must be non-negative")
        return Value
