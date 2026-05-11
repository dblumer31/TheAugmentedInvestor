"""Unit tests for the reusable Azure AI Foundry message client."""

from __future__ import annotations

import httpx

from augmented_investor.config import AppSettings
from augmented_investor.foundry_client import (
    FoundryClient,
    FoundryMessageRequest,
    FoundryProviderError,
)


def test_send_message_builds_messages_request_and_metadata(fake_foundry_env):
    """Message calls should use configured model aliases and return safe metadata."""

    CapturedRequest = {}

    def Handler(Request: httpx.Request) -> httpx.Response:
        CapturedRequest["body"] = Request.read().decode()
        CapturedRequest["headers"] = dict(Request.headers)
        return httpx.Response(
            status_code=200,
            json={
                "content": [{"type": "text", "text": "hello"}],
                "usage": {"input_tokens": 3, "output_tokens": 1},
            },
        )

    Settings = AppSettings(**fake_foundry_env)
    HttpClient = httpx.Client(transport=httpx.MockTransport(Handler))
    Request = FoundryMessageRequest(
        model_role="sonnet",
        max_tokens=25,
        messages=[{"role": "user", "content": "Say hello"}],
    )

    Response = FoundryClient(Settings, http_client=HttpClient).send_message(Request)

    assert '"model":"claude-sonnet-4-6"' in CapturedRequest["body"].replace(" ", "")
    assert Response.text == "hello"
    assert Response.metadata["model"] == "claude-sonnet-4-6"
    assert Response.metadata["model_role"] == "sonnet"
    assert Response.metadata["status_code"] == 200
    assert Response.metadata["usage"] == {"input_tokens": 3, "output_tokens": 1}
    assert Response.metadata["request_summary"]["headers"]["x-api-key"] == "[REDACTED]"
    assert "test-api-key" not in str(Response.metadata)


def test_model_for_role_uses_default_sonnet_and_opus_aliases(fake_foundry_env):
    """Foundry model selection should support default, Sonnet, and Opus roles."""

    Client = FoundryClient(
        AppSettings(**fake_foundry_env),
        http_client=httpx.Client(transport=httpx.MockTransport(lambda request: None)),
    )

    assert Client.model_for_role("default") == "claude-opus-4-7"
    assert Client.model_for_role("sonnet") == "claude-sonnet-4-6"
    assert Client.model_for_role("opus") == "claude-opus-4-7"


def test_send_message_error_includes_redacted_request_summary(fake_foundry_env):
    """Provider errors should include typed attributes and redacted diagnostics."""

    def Handler(Request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=500, text="server unavailable")

    Settings = AppSettings(**fake_foundry_env)
    HttpClient = httpx.Client(transport=httpx.MockTransport(Handler))
    Request = FoundryMessageRequest(
        max_tokens=10,
        messages=[{"role": "user", "content": "test"}],
    )

    try:
        FoundryClient(Settings, http_client=HttpClient).send_message(Request)
    except FoundryProviderError as Error:
        assert Error.status_code == 500
        assert Error.message == "Foundry message request returned an error status"
        assert Error.request_summary["headers"]["x-api-key"] == "[REDACTED]"
        assert "test-api-key" not in str(Error)
        assert "test-api-key" not in str(Error.request_summary)
    else:
        raise AssertionError("Expected FoundryProviderError")
