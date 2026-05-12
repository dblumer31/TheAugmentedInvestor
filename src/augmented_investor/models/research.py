"""Research-stage contracts, including canonical source evidence models."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import AliasChoices, Field, field_validator

from augmented_investor.models.common import ClaimType as ClaimTypeValue
from augmented_investor.models.common import SourceQuality as SourceQualityValue
from augmented_investor.models.common import StrictBaseModel
from augmented_investor.models.common import ensure_utc_datetime


class SearchResult(StrictBaseModel):
    """One search result or provider summary returned by a search client."""

    Source: str = Field(validation_alias=AliasChoices("Source", "source"))
    Title: str = Field(validation_alias=AliasChoices("Title", "title"))
    Url: str | None = Field(default=None, validation_alias=AliasChoices("Url", "url"))
    Snippet: str | None = Field(default=None, validation_alias=AliasChoices("Snippet", "snippet"))
    Provider: str = Field(validation_alias=AliasChoices("Provider", "provider"))
    Rank: int = Field(validation_alias=AliasChoices("Rank", "rank"))
    RetrievedAt: datetime = Field(validation_alias=AliasChoices("RetrievedAt", "retrievedAt"))
    Metadata: dict[str, Any] = Field(
        default_factory=dict,
        validation_alias=AliasChoices("Metadata", "metadata"),
    )

    @field_validator("RetrievedAt")
    @classmethod
    def _retrieved_at_must_be_utc(cls, Value: datetime) -> datetime:
        """Require timezone-aware datetimes and normalize them to UTC."""

        return ensure_utc_datetime(Value)


class SourceEvidence(StrictBaseModel):
    """Retrieved source text or excerpt used for deterministic verification."""

    Source: str = Field(validation_alias=AliasChoices("Source", "source"))
    SourceUrl: str = Field(validation_alias=AliasChoices("SourceUrl", "sourceUrl"))
    RetrievedAt: datetime = Field(validation_alias=AliasChoices("RetrievedAt", "retrievedAt"))
    Title: str | None = Field(default=None, validation_alias=AliasChoices("Title", "title"))
    Publisher: str | None = Field(
        default=None,
        validation_alias=AliasChoices("Publisher", "publisher"),
    )
    PublishedAt: datetime | None = Field(
        default=None,
        validation_alias=AliasChoices("PublishedAt", "publishedAt"),
    )
    RetrievedText: str | None = Field(
        default=None,
        validation_alias=AliasChoices("RetrievedText", "retrievedText"),
    )
    Excerpt: str | None = Field(default=None, validation_alias=AliasChoices("Excerpt", "excerpt"))
    QuotedEvidence: str | None = Field(
        default=None,
        validation_alias=AliasChoices("QuotedEvidence", "quotedEvidence"),
    )
    SourceQuality: SourceQualityValue = Field(
        default=SourceQualityValue.Unknown,
        validation_alias=AliasChoices("SourceQuality", "sourceQuality"),
    )
    SupportsExactClaim: bool = Field(
        default=False,
        validation_alias=AliasChoices("SupportsExactClaim", "supportsExactClaim"),
    )
    Metadata: dict[str, Any] = Field(
        default_factory=dict,
        validation_alias=AliasChoices("Metadata", "metadata"),
    )

    @field_validator("RetrievedAt", "PublishedAt")
    @classmethod
    def _datetime_must_be_utc(cls, Value: datetime | None) -> datetime | None:
        """Require timezone-aware datetimes and normalize them to UTC."""

        if Value is None:
            return None
        return ensure_utc_datetime(Value)


class ResearchClaim(StrictBaseModel):
    """A structured research claim with source quality metadata."""

    Claim: str = Field(validation_alias=AliasChoices("Claim", "claim"))
    Instrument: str | None = Field(
        default=None,
        validation_alias=AliasChoices("Instrument", "instrument"),
    )
    InstrumentPrecision: str | None = Field(
        default=None,
        validation_alias=AliasChoices("InstrumentPrecision", "instrumentPrecision"),
    )
    ClaimType: ClaimTypeValue = Field(validation_alias=AliasChoices("ClaimType", "claimType"))
    Source: str = Field(validation_alias=AliasChoices("Source", "source"))
    SourceQuality: SourceQualityValue = Field(
        validation_alias=AliasChoices("SourceQuality", "sourceQuality"),
    )
    SupportsExactClaim: bool = Field(
        validation_alias=AliasChoices("SupportsExactClaim", "supportsExactClaim"),
    )
    QuotedEvidence: str | None = Field(
        default=None,
        validation_alias=AliasChoices("QuotedEvidence", "quotedEvidence"),
    )
    Date: str | None = Field(default=None, validation_alias=AliasChoices("Date", "date"))
    Confidence: str = Field(validation_alias=AliasChoices("Confidence", "confidence"))


class ResearchPoint(StrictBaseModel):
    """A pro/con evidence point with source quality metadata."""

    Point: str = Field(validation_alias=AliasChoices("Point", "point"))
    Instrument: str | None = Field(
        default=None,
        validation_alias=AliasChoices("Instrument", "instrument"),
    )
    InstrumentPrecision: str | None = Field(
        default=None,
        validation_alias=AliasChoices("InstrumentPrecision", "instrumentPrecision"),
    )
    ClaimType: ClaimTypeValue = Field(validation_alias=AliasChoices("ClaimType", "claimType"))
    Source: str = Field(validation_alias=AliasChoices("Source", "source"))
    SourceQuality: SourceQualityValue = Field(
        validation_alias=AliasChoices("SourceQuality", "sourceQuality"),
    )
    SupportsExactClaim: bool = Field(
        validation_alias=AliasChoices("SupportsExactClaim", "supportsExactClaim"),
    )
    QuotedEvidence: str | None = Field(
        default=None,
        validation_alias=AliasChoices("QuotedEvidence", "quotedEvidence"),
    )
    Date: str | None = Field(default=None, validation_alias=AliasChoices("Date", "date"))
    Confidence: str = Field(validation_alias=AliasChoices("Confidence", "confidence"))


class ResearchSource(StrictBaseModel):
    """Source-list entry attached to a research brief."""

    Publication: str = Field(validation_alias=AliasChoices("Publication", "publication"))
    Url: str | None = Field(default=None, validation_alias=AliasChoices("Url", "url"))
    SourceQuality: SourceQualityValue = Field(
        validation_alias=AliasChoices("SourceQuality", "sourceQuality"),
    )
    Date: str | None = Field(default=None, validation_alias=AliasChoices("Date", "date"))
    Supports: str | None = Field(
        default=None,
        validation_alias=AliasChoices("Supports", "supports"),
    )
    SupportsExactClaim: bool = Field(
        default=False,
        validation_alias=AliasChoices("SupportsExactClaim", "supportsExactClaim"),
    )
    QuotedEvidence: str | None = Field(
        default=None,
        validation_alias=AliasChoices("QuotedEvidence", "quotedEvidence"),
    )


class ResearchBrief(StrictBaseModel):
    """Structured research output used by thesis, writer, and fact-check stages."""

    Topic: str = Field(validation_alias=AliasChoices("Topic", "topic"))
    OneSentenceSummary: str | None = Field(
        default=None,
        validation_alias=AliasChoices("OneSentenceSummary", "oneSentenceSummary"),
    )
    MarketSnapshot: list[ResearchClaim] = Field(
        default_factory=list,
        validation_alias=AliasChoices("MarketSnapshot", "marketSnapshot"),
    )
    PriorTrend: list[ResearchClaim] = Field(
        default_factory=list,
        validation_alias=AliasChoices("PriorTrend", "priorTrend"),
    )
    WhatChanged: list[ResearchClaim] = Field(
        default_factory=list,
        validation_alias=AliasChoices("WhatChanged", "whatChanged"),
    )
    EvidenceFor: list[ResearchPoint] = Field(
        default_factory=list,
        validation_alias=AliasChoices("EvidenceFor", "evidenceFor"),
    )
    EvidenceAgainst: list[ResearchPoint] = Field(
        default_factory=list,
        validation_alias=AliasChoices("EvidenceAgainst", "evidenceAgainst"),
    )
    PossibleMispricing: str | None = Field(
        default=None,
        validation_alias=AliasChoices("PossibleMispricing", "possibleMispricing"),
    )
    SourceList: list[ResearchSource] = Field(
        default_factory=list,
        validation_alias=AliasChoices("SourceList", "sourceList"),
    )
    RetrievedEvidence: list[SourceEvidence] = Field(
        default_factory=list,
        validation_alias=AliasChoices(
            "RetrievedEvidence",
            "retrievedEvidence",
            "retrievedContent",
        ),
    )
    RecommendedAngle: str | None = Field(
        default=None,
        validation_alias=AliasChoices("RecommendedAngle", "recommendedAngle"),
    )
    Provider: str | None = Field(default=None, validation_alias=AliasChoices("Provider", "provider"))
