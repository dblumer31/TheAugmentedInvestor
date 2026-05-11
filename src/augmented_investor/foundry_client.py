"""Azure AI Foundry client helpers for provider smoke testing.

This module centralizes endpoint construction, request shape, and safe diagnostics before
the full agent pipeline depends on Foundry behavior.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import time
from typing import Any, Literal
from urllib.parse import urlparse

import httpx

from augmented_investor.config import AppSettings


ANTHROPIC_MESSAGES_PATH = "/anthropic/v1/messages"
WEB_SEARCH_TOOL_NAME = "web_search_20250305"
REDACTED = "[REDACTED]"
SENSITIVE_HEADER_NAMES = {"authorization", "x-api-key", "api-key", "ocp-apim-subscription-key"}


class FoundrySmokeTestError(RuntimeError):
    """Raised when the Foundry smoke test cannot complete."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        request_summary: dict[str, Any] | None = None,
        cause: str | None = None,
    ) -> None:
        DisplayMessage = f"{message}: {cause}" if cause else message
        super().__init__(DisplayMessage)
        self.message = message
        self.status_code = status_code
        self.request_summary = request_summary or {}
        self.cause = cause


class FoundryProviderError(RuntimeError):
    """Raised when a non-smoke Foundry provider call fails."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        request_summary: dict[str, Any] | None = None,
        cause: str | None = None,
    ) -> None:
        DisplayMessage = f"{message}: {cause}" if cause else message
        super().__init__(DisplayMessage)
        self.message = message
        self.status_code = status_code
        self.request_summary = request_summary or {}
        self.cause = cause


@dataclass(frozen=True)
class FoundrySmokeTestResult:
    """Safe smoke-test diagnostics that can be printed or persisted."""

    endpoint_shape: str
    messages_endpoint: str
    status_code: int
    model_alias: str
    tool_support: str
    elapsed_ms: int
    response_text_preview: str
    request_summary: dict[str, Any]


ModelRole = Literal["default", "sonnet", "opus"]


@dataclass(frozen=True)
class FoundryMessageRequest:
    """Provider-neutral request shape for Foundry Anthropic Messages calls."""

    messages: list[dict[str, Any]]
    max_tokens: int
    model_role: ModelRole = "default"
    tools: list[dict[str, Any]] = field(default_factory=list)
    system: str | None = None


@dataclass(frozen=True)
class FoundryMessageResponse:
    """Safe response data and metadata from a Foundry Messages call."""

    text: str
    raw_response: dict[str, Any]
    metadata: dict[str, Any]


class FoundryClient:
    """Small Azure AI Foundry client for Anthropic Messages calls."""

    def __init__(
        self,
        settings: AppSettings,
        http_client: httpx.Client | None = None,
    ) -> None:
        settings.validate_live_provider_config()
        self._settings = settings
        self._http_client = http_client or httpx.Client(timeout=settings.FoundryTimeoutSeconds)
        self._owns_http_client = http_client is None

    def close(self) -> None:
        """Close the owned HTTP client, if this instance created it."""

        if self._owns_http_client:
            self._http_client.close()

    def __enter__(self) -> "FoundryClient":
        """Return this client for context manager use."""

        return self

    def __exit__(self, exc_type: object, exc_value: object, traceback: object) -> None:
        """Close the owned HTTP client when leaving a context manager."""

        self.close()

    def smoke_test(self, include_tool_probe: bool = True) -> FoundrySmokeTestResult:
        """Send a tiny prompt and return redacted Foundry capability diagnostics."""

        Start = time.perf_counter()
        Endpoint = normalize_messages_endpoint(self._settings.AzureFoundryEndpoint or "")
        Headers = self._build_headers()
        Body = self._build_smoke_body(include_tool_probe)
        RequestSummary = self._build_request_summary(Endpoint, Headers, Body)

        try:
            Response = self._http_client.post(Endpoint, headers=Headers, json=Body)
        except httpx.HTTPError as Error:
            raise FoundrySmokeTestError(
                "Foundry smoke test request failed",
                request_summary=RequestSummary,
                cause=_safe_error_cause(Error),
            ) from Error

        ElapsedMs = int((time.perf_counter() - Start) * 1000)
        ToolSupport = _tool_support_from_response(Response, include_tool_probe)
        Preview = _preview_response_text(Response.text)

        if Response.status_code >= 400:
            raise FoundrySmokeTestError(
                "Foundry smoke test returned an error status",
                status_code=Response.status_code,
                request_summary=RequestSummary,
            )

        return FoundrySmokeTestResult(
            endpoint_shape=classify_endpoint_shape(self._settings.AzureFoundryEndpoint or ""),
            messages_endpoint=Endpoint,
            status_code=Response.status_code,
            model_alias=self._settings.FoundryDefaultModel or "",
            tool_support=ToolSupport,
            elapsed_ms=ElapsedMs,
            response_text_preview=Preview,
            request_summary=RequestSummary,
        )

    def send_message(self, request: FoundryMessageRequest) -> FoundryMessageResponse:
        """Send an Anthropic Messages request and return text plus safe metadata."""

        Endpoint = normalize_messages_endpoint(self._settings.AzureFoundryEndpoint or "")
        Headers = self._build_headers()
        Body = self._build_message_body(request)
        RequestSummary = self._build_request_summary(Endpoint, Headers, Body)
        Start = time.perf_counter()

        try:
            Response = self._http_client.post(Endpoint, headers=Headers, json=Body)
        except httpx.HTTPError as Error:
            raise FoundryProviderError(
                "Foundry message request failed",
                request_summary=RequestSummary,
                cause=_safe_error_cause(Error),
            ) from Error

        ElapsedMs = int((time.perf_counter() - Start) * 1000)
        ResponseText = _preview_response_text(Response.text, limit=1000)

        if Response.status_code >= 400:
            raise FoundryProviderError(
                "Foundry message request returned an error status",
                status_code=Response.status_code,
                request_summary=RequestSummary,
                cause=ResponseText,
            )

        ResponseJson = _parse_response_json(Response, RequestSummary)
        Metadata = {
            "model": Body.get("model"),
            "model_role": request.model_role,
            "status_code": Response.status_code,
            "elapsed_ms": ElapsedMs,
            "usage": ResponseJson.get("usage"),
            "request_summary": RequestSummary,
        }
        return FoundryMessageResponse(
            text=_extract_text(ResponseJson),
            raw_response=ResponseJson,
            metadata=Metadata,
        )

    def _build_headers(self) -> dict[str, str]:
        """Build Foundry request headers for Anthropic Messages calls."""

        ApiKey = self._settings.AzureFoundryApiKey
        Version = self._settings.FoundryAnthropicVersion or ""
        return {
            "content-type": "application/json",
            "x-api-key": ApiKey.get_secret_value() if ApiKey else "",
            "anthropic-version": Version,
        }

    def _build_smoke_body(self, include_tool_probe: bool) -> dict[str, Any]:
        """Build the minimal smoke-test request body."""

        Body: dict[str, Any] = {
            "model": self._settings.FoundryDefaultModel,
            "max_tokens": 16,
            "messages": [
                {
                    "role": "user",
                    "content": "Reply with the single word ok.",
                }
            ],
        }
        if include_tool_probe:
            Body["tools"] = [{"type": WEB_SEARCH_TOOL_NAME, "name": "web_search"}]
        return Body

    def _build_message_body(self, request: FoundryMessageRequest) -> dict[str, Any]:
        """Build the Anthropic Messages body for a provider request."""

        Body: dict[str, Any] = {
            "model": self.model_for_role(request.model_role),
            "max_tokens": request.max_tokens,
            "messages": request.messages,
        }
        if request.system:
            Body["system"] = request.system
        if request.tools:
            Body["tools"] = request.tools
        return Body

    def model_for_role(self, model_role: ModelRole) -> str:
        """Return the configured Foundry model/deployment alias for an agent role."""

        RoleModels = {
            "default": self._settings.FoundryDefaultModel,
            "sonnet": self._settings.FoundrySonnetModel or self._settings.FoundryDefaultModel,
            "opus": self._settings.FoundryOpusModel or self._settings.FoundryDefaultModel,
        }
        Model = RoleModels[model_role]
        if not Model:
            raise FoundryProviderError(f"No Foundry model configured for role: {model_role}")
        return Model

    def _build_request_summary(
        self,
        endpoint: str,
        headers: dict[str, str],
        body: dict[str, Any],
    ) -> dict[str, Any]:
        """Build a log-safe request summary for diagnostics."""

        return {
            "method": "POST",
            "endpoint": endpoint,
            "headers": _redact_headers(headers),
            "body": {
                "model": body.get("model"),
                "max_tokens": body.get("max_tokens"),
                "message_count": len(body.get("messages", [])),
                "tool_names": [Tool.get("type") for Tool in body.get("tools", [])],
                "has_system": bool(body.get("system")),
            },
        }


def normalize_messages_endpoint(endpoint: str) -> str:
    """Normalize a base Foundry endpoint or full messages URL to the messages endpoint."""

    CleanEndpoint = endpoint.strip().rstrip("/")
    if not CleanEndpoint:
        raise ValueError("AZURE_FOUNDRY_ENDPOINT is required")
    if CleanEndpoint.endswith(ANTHROPIC_MESSAGES_PATH):
        return CleanEndpoint
    Parsed = urlparse(CleanEndpoint)
    if not Parsed.scheme or not Parsed.netloc:
        raise ValueError("AZURE_FOUNDRY_ENDPOINT must be an absolute HTTPS URL")
    return f"{CleanEndpoint}{ANTHROPIC_MESSAGES_PATH}"


def classify_endpoint_shape(endpoint: str) -> str:
    """Return whether the configured endpoint is a base URL or full messages URL."""

    CleanEndpoint = endpoint.strip().rstrip("/")
    if CleanEndpoint.endswith(ANTHROPIC_MESSAGES_PATH):
        return "full_messages_endpoint"
    return "base_endpoint"


def _redact_headers(headers: dict[str, str]) -> dict[str, str]:
    """Return headers with credential-bearing values replaced by a redaction marker."""

    RedactedHeaders = {}
    for HeaderName, HeaderValue in headers.items():
        if HeaderName.lower() in SENSITIVE_HEADER_NAMES:
            RedactedHeaders[HeaderName] = REDACTED
        else:
            RedactedHeaders[HeaderName] = HeaderValue
    return RedactedHeaders


def _tool_support_from_response(response: httpx.Response, include_tool_probe: bool) -> str:
    """Classify web-search tool support from the smoke-test response status and text."""

    if not include_tool_probe:
        return "not_checked"
    if response.status_code < 400:
        return "accepted"
    ResponseText = response.text.lower()
    if "tool" in ResponseText or WEB_SEARCH_TOOL_NAME in ResponseText:
        return "rejected"
    return "unknown"


def _preview_response_text(response_text: str, limit: int = 240) -> str:
    """Return a bounded response preview for diagnostics."""

    CompactText = " ".join(response_text.split())
    return CompactText[:limit]


def _safe_error_cause(error: httpx.HTTPError) -> str:
    """Return a bounded HTTP error cause without request headers or body."""

    ErrorText = str(error).replace("\n", " ")
    CompactText = " ".join(ErrorText.split())
    if CompactText:
        return f"{error.__class__.__name__}: {CompactText[:240]}"
    return error.__class__.__name__


def _parse_response_json(
    response: httpx.Response,
    request_summary: dict[str, Any],
) -> dict[str, Any]:
    """Parse a Foundry JSON response or raise a typed provider error."""

    try:
        Parsed = response.json()
    except ValueError as Error:
        raise FoundryProviderError(
            "Foundry message response was not valid JSON",
            status_code=response.status_code,
            request_summary=request_summary,
            cause=_preview_response_text(response.text),
        ) from Error
    if not isinstance(Parsed, dict):
        raise FoundryProviderError(
            "Foundry message response JSON was not an object",
            status_code=response.status_code,
            request_summary=request_summary,
        )
    return Parsed


def _extract_text(response_json: dict[str, Any]) -> str:
    """Extract text blocks from an Anthropic Messages response."""

    Content = response_json.get("content", [])
    if not isinstance(Content, list):
        return ""
    TextParts = [
        Block.get("text", "")
        for Block in Content
        if isinstance(Block, dict) and Block.get("type") == "text"
    ]
    return "\n".join(Part for Part in TextParts if Part)
