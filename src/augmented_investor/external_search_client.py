"""Search and retrieval provider abstractions for the research pipeline.

Agents consume these interfaces instead of calling Foundry or future external providers
directly.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any, Protocol

from augmented_investor.foundry_client import (
    FoundryClient,
    FoundryMessageRequest,
    FoundryProviderError,
    WEB_SEARCH_TOOL_NAME,
)
from augmented_investor.models.research import SearchResult, SourceEvidence


FOUNDRY_SEARCH_PROVIDER = "foundry_web_search"
NOOP_SEARCH_PROVIDER = "noop"


class SearchProviderError(RuntimeError):
    """Raised when a search provider fails rather than returning an empty result."""

    def __init__(
        self,
        message: str,
        status_code: int | None = None,
        request_summary: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.request_summary = request_summary or {}


class SearchClient(Protocol):
    """Protocol implemented by all search and retrieval providers."""

    def search(self, query: str, limit: int = 5) -> list[SearchResult]:
        """Search for a query and return zero or more results."""

    def retrieve(self, url: str) -> SourceEvidence | None:
        """Retrieve a specific source URL when supported."""


class NoopSearchClient:
    """Offline search client for tests and local development."""

    Provider = NOOP_SEARCH_PROVIDER

    def search(self, query: str, limit: int = 5) -> list[SearchResult]:
        """Return no results without treating that as an error."""

        return []

    def retrieve(self, url: str) -> SourceEvidence | None:
        """Return no evidence without treating that as an error."""

        return None


class FoundryToolSearchClient:
    """Search client backed by Foundry's Anthropic web-search tool."""

    Provider = FOUNDRY_SEARCH_PROVIDER

    def __init__(self, foundry_client: FoundryClient) -> None:
        self._foundry_client = foundry_client

    def search(self, query: str, limit: int = 5) -> list[SearchResult]:
        """Run a web-search-backed Foundry request and return provider summaries."""

        if not query.strip() or limit <= 0:
            return []
        Response = self._send_search_message(query)
        if not Response.text.strip():
            return []
        return [
            SearchResult(
                Source=self.Provider,
                Title="Foundry web search summary",
                Snippet=Response.text,
                Provider=self.Provider,
                Rank=1,
                RetrievedAt=_utc_now(),
                Metadata={
                    "model": Response.metadata.get("model"),
                    "status_code": Response.metadata.get("status_code"),
                    "evidence_source": self.Provider,
                },
            )
        ][:limit]

    def retrieve(self, url: str) -> SourceEvidence | None:
        """Retrieve a URL through Foundry web search when a URL is supplied."""

        CleanUrl = url.strip()
        if not CleanUrl:
            return None
        Response = self._send_search_message(f"Retrieve and summarize this source: {CleanUrl}")
        if not Response.text.strip():
            return None
        return SourceEvidence(
            Source=self.Provider,
            SourceUrl=CleanUrl,
            RetrievedAt=_utc_now(),
            RetrievedText=Response.text,
            Excerpt=Response.text[:1000],
            Metadata={
                "model": Response.metadata.get("model"),
                "status_code": Response.metadata.get("status_code"),
                "evidence_source": self.Provider,
            },
        )

    def _send_search_message(self, prompt: str):
        """Send a web-search-enabled Foundry request and map provider failures."""

        Request = FoundryMessageRequest(
            model_role="default",
            max_tokens=1000,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            tools=[{"type": WEB_SEARCH_TOOL_NAME, "name": "web_search"}],
        )
        try:
            return self._foundry_client.send_message(Request)
        except FoundryProviderError as Error:
            raise SearchProviderError(
                Error.message,
                status_code=Error.status_code,
                request_summary=Error.request_summary,
            ) from Error


def _utc_now() -> datetime:
    """Return the current timezone-aware UTC datetime."""

    return datetime.now(UTC)
