"""Shared model utilities and enums for pipeline data contracts."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, field_validator


class StrictBaseModel(BaseModel):
    """Base model that rejects unknown fields so contracts stay explicit."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class SourceQuality(StrEnum):
    """Supported source-quality categories from the functional specification."""

    PrimaryMarketData = "primary_market_data"
    CompanyFilingOrIr = "company_filing_or_ir"
    OfficialInstitutionalReport = "official_institutional_report"
    ReputableFinancialMedia = "reputable_financial_media"
    SyndicatedMarketArticle = "syndicated_market_article"
    BlogOrSubstack = "blog_or_substack"
    Unknown = "unknown"


class ClaimType(StrEnum):
    """Claim types used by research and fact-check contracts."""

    MarketReturn = "market_return"
    Valuation = "valuation"
    CompanyFinancial = "company_financial"
    InstitutionalReport = "institutional_report"
    MacroData = "macro_data"
    Forecast = "forecast"
    ScenarioMath = "scenario_math"
    EditorialInterpretation = "editorial_interpretation"


def ensure_utc_datetime(Value: datetime) -> datetime:
    """Require timezone-aware datetimes and normalize them to UTC."""

    if Value.tzinfo is None:
        raise ValueError("datetime must be timezone-aware")
    return Value.astimezone(UTC)


def compact_validation_errors(errors: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Return validation errors with only stable, prompt-safe fields."""

    return [
        {
            "loc": Error.get("loc", ()),
            "msg": Error.get("msg", ""),
            "type": Error.get("type", ""),
        }
        for Error in errors
    ]
