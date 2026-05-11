"""Unit tests for search and retrieval provider abstractions."""

from __future__ import annotations

from datetime import UTC, datetime, timezone, timedelta

import httpx
import pytest

from augmented_investor.config import AppSettings
from augmented_investor.external_search_client import (
    FOUNDRY_SEARCH_PROVIDER,
    FoundryToolSearchClient,
    NoopSearchClient,
    SearchProviderError,
    SearchResult,
    SourceEvidence,
)
from augmented_investor.foundry_client import FoundryClient


def test_noop_search_client_returns_empty_results_without_error():
    """Empty results from the no-op client are normal and not provider failures."""

    Client = NoopSearchClient()

    assert Client.search("AI infrastructure", limit=5) == []
    assert Client.retrieve("https://example.com") is None


def test_search_result_rejects_naive_datetime():
    """Search result timestamps must be timezone-aware."""

    with pytest.raises(ValueError, match="timezone-aware"):
        SearchResult(
            Source="test",
            Title="Test",
            Provider="test",
            Rank=1,
            RetrievedAt=datetime(2026, 5, 11),
        )


def test_source_evidence_normalizes_datetime_to_utc():
    """Source evidence timestamps should normalize non-UTC offsets to UTC."""

    EasternTime = timezone(timedelta(hours=-4))
    Evidence = SourceEvidence(
        Source="test",
        SourceUrl="https://example.com",
        RetrievedAt=datetime(2026, 5, 11, 12, 0, tzinfo=EasternTime),
    )

    assert Evidence.RetrievedAt.tzinfo == UTC
    assert Evidence.RetrievedAt.hour == 16


def test_foundry_tool_search_client_returns_result_with_provider_metadata(fake_foundry_env):
    """Foundry search should return a provider-tagged result from response text."""

    CapturedRequest = {}

    def Handler(Request: httpx.Request) -> httpx.Response:
        CapturedRequest["body"] = Request.read().decode()
        return httpx.Response(
            status_code=200,
            json={
                "content": [{"type": "text", "text": "AI infrastructure search summary"}],
                "usage": {"input_tokens": 20, "output_tokens": 5},
            },
        )

    Foundry = FoundryClient(
        AppSettings(**fake_foundry_env),
        http_client=httpx.Client(transport=httpx.MockTransport(Handler)),
    )

    Results = FoundryToolSearchClient(Foundry).search("AI infrastructure", limit=3)

    assert len(Results) == 1
    assert "web_search_20250305" in CapturedRequest["body"]
    assert Results[0].Source == FOUNDRY_SEARCH_PROVIDER
    assert Results[0].Provider == FOUNDRY_SEARCH_PROVIDER
    assert Results[0].Snippet == "AI infrastructure search summary"
    assert Results[0].Metadata["evidence_source"] == FOUNDRY_SEARCH_PROVIDER


def test_foundry_tool_search_client_empty_text_is_empty_result(fake_foundry_env):
    """A successful provider response with no text should return an empty result list."""

    def Handler(Request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=200, json={"content": []})

    Foundry = FoundryClient(
        AppSettings(**fake_foundry_env),
        http_client=httpx.Client(transport=httpx.MockTransport(Handler)),
    )

    assert FoundryToolSearchClient(Foundry).search("quiet topic") == []


def test_foundry_tool_search_client_provider_failure_is_typed(fake_foundry_env):
    """Provider failures should raise typed search errors with redacted diagnostics."""

    def Handler(Request: httpx.Request) -> httpx.Response:
        return httpx.Response(status_code=503, text="provider unavailable")

    Foundry = FoundryClient(
        AppSettings(**fake_foundry_env),
        http_client=httpx.Client(transport=httpx.MockTransport(Handler)),
    )

    with pytest.raises(SearchProviderError) as ErrorInfo:
        FoundryToolSearchClient(Foundry).search("AI infrastructure")

    Error = ErrorInfo.value
    assert Error.status_code == 503
    assert Error.request_summary["headers"]["x-api-key"] == "[REDACTED]"
    assert "test-api-key" not in str(Error)
    assert "test-api-key" not in str(Error.request_summary)


def test_foundry_tool_search_client_retrieves_source_evidence(fake_foundry_env):
    """Foundry retrieval should return source evidence with a provider tag."""

    def Handler(Request: httpx.Request) -> httpx.Response:
        return httpx.Response(
            status_code=200,
            json={"content": [{"type": "text", "text": "Retrieved source content"}]},
        )

    Foundry = FoundryClient(
        AppSettings(**fake_foundry_env),
        http_client=httpx.Client(transport=httpx.MockTransport(Handler)),
    )

    Evidence = FoundryToolSearchClient(Foundry).retrieve("https://example.com/report")

    assert Evidence is not None
    assert Evidence.Source == FOUNDRY_SEARCH_PROVIDER
    assert Evidence.SourceUrl == "https://example.com/report"
    assert Evidence.RetrievedText == "Retrieved source content"
    assert Evidence.Metadata["evidence_source"] == FOUNDRY_SEARCH_PROVIDER
