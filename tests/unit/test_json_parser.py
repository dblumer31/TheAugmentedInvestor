"""Unit tests for deterministic JSON parsing helpers."""

from __future__ import annotations

import json

import pytest

from augmented_investor.models.common import ClaimType, SourceQuality
from augmented_investor.models.research import ResearchClaim
from augmented_investor.models.scope import ScopeRequest
from augmented_investor.pipeline.json_parser import (
    JsonValidationError,
    build_retry_context,
    preview_raw_output,
    validate_items,
    validate_model,
)


def _valid_scope_json() -> str:
    """Return valid lower-camel scope JSON."""

    return json.dumps(
        {
            "market": "AI infrastructure",
            "recentWindow": "last 30 days",
            "contextWindow": "three years",
            "readerHorizon": "long term",
            "readerType": "operator-investor",
            "depth": "deep",
            "length": "1500 words",
        }
    )


def test_validate_model_parses_valid_json_into_model():
    """Valid JSON should produce the target Pydantic model."""

    Scope = validate_model(_valid_scope_json(), ScopeRequest)

    assert Scope.Market == "AI infrastructure"
    assert Scope.Length == "1500 words"


def test_validate_model_raises_typed_error_for_invalid_json():
    """Invalid JSON should expose a bounded preview and structured errors."""

    with pytest.raises(JsonValidationError) as ErrorInfo:
        validate_model("{not json", ScopeRequest)

    Error = ErrorInfo.value
    assert Error.message == "Agent output was not valid JSON"
    assert Error.raw_preview == "{not json"
    assert Error.validation_errors[0]["type"] == "json_decode_error"


def test_validate_model_raises_typed_error_for_schema_failure():
    """Schema failures should include validation details for retry prompts."""

    with pytest.raises(JsonValidationError) as ErrorInfo:
        validate_model(json.dumps({"market": "AI infrastructure"}), ScopeRequest)

    Error = ErrorInfo.value
    assert "ScopeRequest" in Error.message
    assert Error.raw_preview
    assert any("recentwindow" in str(Item["loc"]).lower() for Item in Error.validation_errors)


def test_build_retry_context_is_bounded_and_redacted():
    """Retry context should never include unbounded raw output or secrets."""

    SecretRawOutput = (
        '{"market":"AI","x-api-key":"super-secret-key","authorization":"Bearer token-value"}'
        + "x" * 2000
    )
    Error = JsonValidationError(
        "failed",
        raw_preview=preview_raw_output(SecretRawOutput, limit=120),
        validation_errors=[{"loc": ("market",), "msg": "bad", "type": "value_error"}],
    )

    Context = build_retry_context(Error)

    assert len(Context["raw_preview"]) <= 120
    assert "super-secret-key" not in Context["raw_preview"]
    assert "token-value" not in Context["raw_preview"]
    assert "[REDACTED]" in Context["raw_preview"]
    assert Context["validation_errors"] == Error.validation_errors


def test_validate_items_salvages_valid_items_and_reports_bad_items():
    """One invalid list item should not discard the valid batch items."""

    Items = [
        {
            "claim": "AI capex is rising",
            "claimType": ClaimType.CompanyFinancial,
            "source": "10-K",
            "sourceQuality": SourceQuality.CompanyFilingOrIr,
            "supportsExactClaim": True,
            "confidence": "high",
        },
        {
            "claim": "Missing required metadata",
        },
    ]

    Result = validate_items(Items, ResearchClaim)

    assert len(Result.ValidItems) == 1
    assert Result.ValidItems[0].Claim == "AI capex is rising"
    assert len(Result.Warnings) == 1
    assert Result.Warnings[0].Index == 1
    assert Result.Warnings[0].ValidationErrors
