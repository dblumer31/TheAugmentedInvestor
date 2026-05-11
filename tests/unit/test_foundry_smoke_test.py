"""Unit tests for Azure AI Foundry smoke-test behavior."""

from __future__ import annotations

import httpx

from augmented_investor.config import AppSettings
from augmented_investor.foundry_client import (
    ANTHROPIC_MESSAGES_PATH,
    FoundryClient,
    FoundrySmokeTestError,
    classify_endpoint_shape,
    normalize_messages_endpoint,
)


def test_normalize_messages_endpoint_accepts_base_endpoint():
    """A base Foundry endpoint should normalize to the Anthropic messages path."""

    Endpoint = normalize_messages_endpoint("https://example.services.ai.azure.com")

    assert Endpoint == f"https://example.services.ai.azure.com{ANTHROPIC_MESSAGES_PATH}"


def test_normalize_messages_endpoint_accepts_full_messages_endpoint():
    """A full messages endpoint should not get the path appended twice."""

    RawEndpoint = f"https://example.services.ai.azure.com{ANTHROPIC_MESSAGES_PATH}"

    assert normalize_messages_endpoint(RawEndpoint) == RawEndpoint
    assert classify_endpoint_shape(RawEndpoint) == "full_messages_endpoint"


def test_smoke_test_sends_tiny_prompt_and_returns_safe_metadata(fake_foundry_env):
    """The smoke test should send a tiny request and return structured diagnostics."""

    CapturedRequest = {}

    def Handler(Request: httpx.Request) -> httpx.Response:
        CapturedRequest["url"] = str(Request.url)
        CapturedRequest["body"] = Request.read().decode()
        return httpx.Response(
            status_code=200,
            json={"content": [{"type": "text", "text": "ok"}]},
        )

    Settings = AppSettings(**fake_foundry_env)
    HttpClient = httpx.Client(transport=httpx.MockTransport(Handler))

    Result = FoundryClient(Settings, http_client=HttpClient).smoke_test()

    assert CapturedRequest["url"].endswith(ANTHROPIC_MESSAGES_PATH)
    assert "Reply with the single word ok." in CapturedRequest["body"]
    assert "web_search_20250305" in CapturedRequest["body"]
    assert Result.status_code == 200
    assert Result.endpoint_shape == "base_endpoint"
    assert Result.model_alias == "claude-opus-4-7"
    assert Result.tool_support == "accepted"
    assert Result.request_summary["headers"]["x-api-key"] == "[REDACTED]"
    assert "test-api-key" not in str(Result.request_summary)


def test_smoke_test_reports_tool_rejection_safely(fake_foundry_env):
    """Tool rejection should be reported without exposing secret request values."""

    def Handler(Request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=400,
            text="unsupported tool web_search_20250305",
        )

    Settings = AppSettings(**fake_foundry_env)
    HttpClient = httpx.Client(transport=httpx.MockTransport(Handler))

    try:
        FoundryClient(Settings, http_client=HttpClient).smoke_test()
    except FoundrySmokeTestError as Error:
        assert Error.status_code == 400
        assert Error.request_summary["headers"]["x-api-key"] == "[REDACTED]"
        assert "test-api-key" not in str(Error)
        assert "test-api-key" not in str(Error.request_summary)
    else:
        raise AssertionError("Expected FoundrySmokeTestError")


def test_smoke_test_reports_request_failure_cause_safely(fake_foundry_env):
    """Transport failures should include a safe cause and redacted request summary."""

    def Handler(Request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("DNS lookup failed for example host", request=Request)

    Settings = AppSettings(**fake_foundry_env)
    HttpClient = httpx.Client(transport=httpx.MockTransport(Handler))

    try:
        FoundryClient(Settings, http_client=HttpClient).smoke_test()
    except FoundrySmokeTestError as Error:
        assert Error.cause is not None
        assert "ConnectError" in Error.cause
        assert "DNS lookup failed" in Error.cause
        assert Error.request_summary["headers"]["x-api-key"] == "[REDACTED]"
        assert "test-api-key" not in str(Error)
        assert "test-api-key" not in str(Error.request_summary)
    else:
        raise AssertionError("Expected FoundrySmokeTestError")
