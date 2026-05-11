"""Deterministic JSON parsing and Pydantic validation helpers for agent outputs."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from augmented_investor.models.common import compact_validation_errors


MAX_RAW_PREVIEW_CHARS = 1000
SECRET_PATTERNS = [
    re.compile(r"(?i)(x-api-key|api[_-]?key|authorization)(\"?\s*[:=]\s*\"?)([^\",}]+)"),
    re.compile(r"(?i)(bearer\s+)([A-Za-z0-9._\-]+)"),
]

ModelT = TypeVar("ModelT", bound=BaseModel)


class JsonValidationError(ValueError):
    """Raised when raw agent output cannot be parsed or validated."""

    def __init__(
        self,
        message: str,
        raw_preview: str,
        validation_errors: list[dict[str, Any]] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.raw_preview = raw_preview
        self.validation_errors = validation_errors or []


@dataclass(frozen=True)
class ItemValidationWarning:
    """Warning produced when one item in a list fails validation."""

    Index: int
    RawItemPreview: str
    ValidationErrors: list[dict[str, Any]] = field(default_factory=list)


@dataclass(frozen=True)
class ItemValidationResult:
    """Result for item-level validation where invalid items can be dropped."""

    ValidItems: list[BaseModel]
    Warnings: list[ItemValidationWarning]


def parse_json_object(raw_output: str) -> dict[str, Any]:
    """Parse raw model output as a JSON object or raise a typed validation error."""

    try:
        Parsed = json.loads(raw_output)
    except json.JSONDecodeError as Error:
        raise JsonValidationError(
            "Agent output was not valid JSON",
            raw_preview=preview_raw_output(raw_output),
            validation_errors=[
                {
                    "loc": (Error.lineno, Error.colno),
                    "msg": Error.msg,
                    "type": "json_decode_error",
                }
            ],
        ) from Error
    if not isinstance(Parsed, dict):
        raise JsonValidationError(
            "Agent output JSON must be an object",
            raw_preview=preview_raw_output(raw_output),
            validation_errors=[
                {
                    "loc": (),
                    "msg": "JSON root must be an object",
                    "type": "json_root_type",
                }
            ],
        )
    return Parsed


def validate_model(raw_output: str, model_type: type[ModelT]) -> ModelT:
    """Parse and validate one structured agent output against a Pydantic model."""

    Parsed = parse_json_object(raw_output)
    try:
        return model_type.model_validate(Parsed)
    except ValidationError as Error:
        raise JsonValidationError(
            f"Agent output failed validation for {model_type.__name__}",
            raw_preview=preview_raw_output(raw_output),
            validation_errors=compact_validation_errors(Error.errors()),
        ) from Error


def validate_items(items: list[Any], model_type: type[ModelT]) -> ItemValidationResult:
    """Validate list items independently so one bad item does not drop the batch."""

    ValidItems: list[BaseModel] = []
    Warnings: list[ItemValidationWarning] = []
    for Index, Item in enumerate(items):
        try:
            ValidItems.append(model_type.model_validate(Item))
        except ValidationError as Error:
            Warnings.append(
                ItemValidationWarning(
                    Index=Index,
                    RawItemPreview=preview_raw_output(json.dumps(Item, default=str)),
                    ValidationErrors=compact_validation_errors(Error.errors()),
                )
            )
    return ItemValidationResult(ValidItems=ValidItems, Warnings=Warnings)


def build_retry_context(error: JsonValidationError) -> dict[str, Any]:
    """Build provider-agnostic retry context from a parsing or validation error."""

    return {
        "message": error.message,
        "raw_preview": error.raw_preview,
        "validation_errors": error.validation_errors,
        "instruction": "Return only valid JSON matching the requested schema.",
    }


def preview_raw_output(raw_output: str, limit: int = MAX_RAW_PREVIEW_CHARS) -> str:
    """Return bounded, redacted raw model output for debugging and retry prompts."""

    RedactedOutput = redact_sensitive_text(raw_output)
    CompactOutput = " ".join(RedactedOutput.split())
    return CompactOutput[:limit]


def redact_sensitive_text(value: str) -> str:
    """Redact common secret patterns before text enters diagnostics."""

    RedactedValue = value
    for Pattern in SECRET_PATTERNS:
        RedactedValue = Pattern.sub(_redact_match, RedactedValue)
    return RedactedValue


def _redact_match(match: re.Match[str]) -> str:
    """Replace the secret part of a regex match while preserving context."""

    if len(match.groups()) == 3:
        return f"{match.group(1)}{match.group(2)}[REDACTED]"
    return f"{match.group(1)}[REDACTED]"
