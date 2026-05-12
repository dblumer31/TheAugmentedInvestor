"""Research Agent implementation for structured evidence generation."""

from __future__ import annotations

from pathlib import Path
import json
from typing import Protocol

from augmented_investor.external_search_client import SearchClient
from augmented_investor.foundry_client import FoundryMessageRequest, FoundryMessageResponse
from augmented_investor.models.research import ResearchBrief, SearchResult, SourceEvidence
from augmented_investor.models.scope import ScopeRequest
from augmented_investor.pipeline.json_parser import (
    JsonValidationError,
    build_retry_context,
    validate_model,
)


DEFAULT_SEARCH_LIMIT = 5
DEFAULT_EVIDENCE_CHAR_LIMIT = 1000
RESEARCH_MAX_TOKENS = 4000
PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "research.md"


class MessageClient(Protocol):
    """Provider interface needed by the Research Agent."""

    def send_message(self, request: FoundryMessageRequest) -> FoundryMessageResponse:
        """Send one structured research prompt."""


class ResearchAgent:
    """Produce a validated ResearchBrief from scope and optional retrieved evidence."""

    def __init__(
        self,
        message_client: MessageClient,
        search_client: SearchClient,
        evidence_char_limit: int = DEFAULT_EVIDENCE_CHAR_LIMIT,
        search_limit: int = DEFAULT_SEARCH_LIMIT,
        prompt_template: str | None = None,
    ) -> None:
        self._message_client = message_client
        self._search_client = search_client
        self._evidence_char_limit = evidence_char_limit
        self._search_limit = search_limit
        self._prompt_template = prompt_template or PROMPT_PATH.read_text(encoding="utf-8")

    def run(self, scope: ScopeRequest) -> ResearchBrief:
        """Run search/retrieval, prompt the model, and return a validated brief."""

        SearchResults = self._search(scope)
        RetrievedEvidence = self._retrieve_evidence(SearchResults)
        Prompt = self._build_prompt(scope, SearchResults, RetrievedEvidence)
        Response = self._message_client.send_message(self._build_request(Prompt))
        try:
            Brief = validate_model(Response.text, ResearchBrief)
        except JsonValidationError as Error:
            RetryPrompt = self._build_retry_prompt(Prompt, Error)
            RetryResponse = self._message_client.send_message(self._build_request(RetryPrompt))
            Brief = validate_model(RetryResponse.text, ResearchBrief)
        return self._merge_provider_metadata(Brief, RetrievedEvidence)

    def _search(self, scope: ScopeRequest) -> list[SearchResult]:
        """Search for scope-relevant evidence through the configured abstraction."""

        return self._search_client.search(_scope_query(scope), limit=self._search_limit)

    def _retrieve_evidence(self, search_results: list[SearchResult]) -> list[SourceEvidence]:
        """Retrieve bounded evidence text from search result URLs."""

        RetrievedEvidence: list[SourceEvidence] = []
        for Result in search_results:
            if not Result.Url:
                continue
            Evidence = self._search_client.retrieve(Result.Url)
            if Evidence is not None:
                RetrievedEvidence.append(self._bounded_evidence(Evidence))
        return RetrievedEvidence

    def _bounded_evidence(self, evidence: SourceEvidence) -> SourceEvidence:
        """Limit retrieved text before it is inserted into prompts or artifacts."""

        return evidence.model_copy(
            update={
                "RetrievedText": _bounded_text(evidence.RetrievedText, self._evidence_char_limit),
                "Excerpt": _bounded_text(evidence.Excerpt, self._evidence_char_limit),
            }
        )

    def _build_prompt(
        self,
        scope: ScopeRequest,
        search_results: list[SearchResult],
        retrieved_evidence: list[SourceEvidence],
    ) -> str:
        """Build the research prompt from scope, search summaries, and source text."""

        Payload = {
            "scope": scope.model_dump(mode="json"),
            "searchResults": [Result.model_dump(mode="json") for Result in search_results],
            "retrievedEvidence": [
                Evidence.model_dump(mode="json") for Evidence in retrieved_evidence
            ],
        }
        return (
            f"{self._prompt_template}\n\n"
            f"Scope and retrieval context:\n{json.dumps(Payload, indent=2)}\n\n"
            "Retrieved evidence is bounded and should be treated as the source of truth "
            "when it supports an exact claim."
        )

    def _build_request(self, prompt: str) -> FoundryMessageRequest:
        """Create a Foundry-compatible request for structured research."""

        return FoundryMessageRequest(
            model_role="sonnet",
            max_tokens=RESEARCH_MAX_TOKENS,
            messages=[{"role": "user", "content": prompt}],
        )

    def _build_retry_prompt(self, original_prompt: str, error: JsonValidationError) -> str:
        """Create a one-shot retry prompt with bounded validation context."""

        RetryContext = build_retry_context(error)
        return (
            f"{original_prompt}\n\n"
            "The prior response failed JSON validation. Fix only the JSON contract.\n"
            f"Validation context:\n{json.dumps(RetryContext, indent=2)}"
        )

    def _merge_provider_metadata(
        self,
        brief: ResearchBrief,
        retrieved_evidence: list[SourceEvidence],
    ) -> ResearchBrief:
        """Record provider and retrieved evidence in the validated research brief."""

        Provider = getattr(self._search_client, "Provider", self._search_client.__class__.__name__)
        ExistingEvidence = list(brief.RetrievedEvidence)
        if not ExistingEvidence:
            ExistingEvidence = retrieved_evidence
        return brief.model_copy(update={"Provider": Provider, "RetrievedEvidence": ExistingEvidence})


def _scope_query(scope: ScopeRequest) -> str:
    """Create a concise search query from a scope request."""

    QueryParts = [
        scope.Market,
        scope.RecentWindow,
        scope.ContextWindow,
        scope.ReaderHorizon,
        scope.ReaderType,
        scope.ContrarianLean,
    ]
    return " ".join(Part for Part in QueryParts if Part)


def _bounded_text(value: str | None, limit: int) -> str | None:
    """Return text truncated to the configured evidence limit."""

    if value is None:
        return None
    return value[:limit]
