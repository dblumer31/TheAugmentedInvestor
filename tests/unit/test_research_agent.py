"""Unit tests for the Research Agent with fake message and search clients."""

from __future__ import annotations

from dataclasses import dataclass
import json

from augmented_investor.agents.research_agent import ResearchAgent
from augmented_investor.foundry_client import FoundryMessageRequest, FoundryMessageResponse
from augmented_investor.models.common import ClaimType, SourceQuality
from augmented_investor.models.research import SearchResult, SourceEvidence
from augmented_investor.models.scope import ScopeRequest


def _scope() -> ScopeRequest:
    """Return a valid scope fixture."""

    return ScopeRequest(
        market="AI infrastructure",
        recentWindow="last 30 days",
        contextWindow="three years",
        readerHorizon="long term",
        readerType="operator-investor",
        contrarianLean="skeptical",
        depth="deep",
        length="1500 words",
    )


def _research_payload() -> dict:
    """Return a valid research payload fixture."""

    return {
        "topic": "AI infrastructure",
        "oneSentenceSummary": "AI infrastructure demand remains durable.",
        "marketSnapshot": [
            {
                "claim": "AI capex is rising.",
                "instrument": "AI infrastructure equities",
                "instrumentPrecision": "sector basket",
                "claimType": ClaimType.CompanyFinancial,
                "source": "Company filings",
                "sourceQuality": SourceQuality.CompanyFilingOrIr,
                "supportsExactClaim": True,
                "quotedEvidence": "Capital expenditure increased.",
                "date": "2026-05-11",
                "confidence": "high",
            }
        ],
        "priorTrend": [],
        "whatChanged": [],
        "evidenceFor": [
            {
                "point": "Cloud capex plans remain elevated.",
                "instrument": "hyperscalers",
                "instrumentPrecision": "company group",
                "claimType": ClaimType.CompanyFinancial,
                "source": "Company filings",
                "sourceQuality": SourceQuality.CompanyFilingOrIr,
                "supportsExactClaim": True,
                "quotedEvidence": "Management guided higher capex.",
                "date": "2026-05-11",
                "confidence": "medium",
            }
        ],
        "evidenceAgainst": [],
        "possibleMispricing": "The market may underprice duration.",
        "sourceList": [
            {
                "publication": "Company filings",
                "url": "https://example.com/filing",
                "sourceQuality": SourceQuality.CompanyFilingOrIr,
                "date": "2026-05-11",
                "supports": "Capex claim",
                "supportsExactClaim": True,
                "quotedEvidence": "Capital expenditure increased.",
            }
        ],
        "recommendedAngle": "Durability versus cyclicality.",
    }


@dataclass
class FakeMessageClient:
    """Fake Foundry-compatible message client."""

    Responses: list[str]

    def __post_init__(self) -> None:
        self.Requests: list[FoundryMessageRequest] = []

    def send_message(self, request: FoundryMessageRequest) -> FoundryMessageResponse:
        """Record requests and return queued responses."""

        self.Requests.append(request)
        Text = self.Responses.pop(0)
        return FoundryMessageResponse(text=Text, raw_response={}, metadata={"model": "fake"})


class FakeSearchClient:
    """Fake search client that can return search results and retrieved evidence."""

    Provider = "fake_search"

    def __init__(self, evidence_text: str | None = "Retrieved source text") -> None:
        self.EvidenceText = evidence_text
        self.SearchCalls: list[tuple[str, int]] = []
        self.RetrieveCalls: list[str] = []

    def search(self, query: str, limit: int = 5) -> list[SearchResult]:
        """Return a single search result with a retrievable URL."""

        self.SearchCalls.append((query, limit))
        return [
            SearchResult(
                source=self.Provider,
                title="Company filing",
                url="https://example.com/filing",
                snippet="Capex disclosure",
                provider=self.Provider,
                rank=1,
                retrievedAt="2026-05-11T12:00:00Z",
                metadata={"evidence_source": self.Provider},
            )
        ]

    def retrieve(self, url: str) -> SourceEvidence | None:
        """Return source evidence when configured."""

        self.RetrieveCalls.append(url)
        if self.EvidenceText is None:
            return None
        return SourceEvidence(
            source=self.Provider,
            sourceUrl=url,
            retrievedAt="2026-05-11T12:00:00Z",
            retrievedText=self.EvidenceText,
            excerpt=self.EvidenceText,
            sourceQuality=SourceQuality.CompanyFilingOrIr,
            supportsExactClaim=True,
            metadata={"evidence_source": self.Provider},
        )


def test_research_agent_produces_valid_brief_with_retrieved_evidence():
    """Retrieved evidence should be included in prompt context and final brief."""

    LongEvidence = "A" * 2000
    MessageClient = FakeMessageClient([json.dumps(_research_payload())])
    SearchClient = FakeSearchClient(evidence_text=LongEvidence)
    Agent = ResearchAgent(MessageClient, SearchClient, evidence_char_limit=200)

    Brief = Agent.run(_scope())

    FirstRequest = MessageClient.Requests[0]
    Prompt = FirstRequest.messages[0]["content"]
    assert "Retrieved evidence" in Prompt
    assert len(Prompt) < 5000
    assert SearchClient.RetrieveCalls == ["https://example.com/filing"]
    assert Brief.Topic == "AI infrastructure"
    assert Brief.Provider == "fake_search"
    assert len(Brief.RetrievedEvidence) == 1
    assert Brief.RetrievedEvidence[0].RetrievedText == "A" * 200
    assert Brief.MarketSnapshot[0].InstrumentPrecision == "sector basket"


def test_research_agent_operates_without_retrieved_evidence():
    """No-op or empty retrieval should still produce a validated research brief."""

    MessageClient = FakeMessageClient([json.dumps(_research_payload())])
    SearchClient = FakeSearchClient(evidence_text=None)

    Brief = ResearchAgent(MessageClient, SearchClient).run(_scope())

    assert Brief.Provider == "fake_search"
    assert Brief.RetrievedEvidence == []
    assert SearchClient.SearchCalls


def test_research_agent_retries_once_with_validation_context():
    """Invalid model JSON should trigger one retry with bounded validation context."""

    MessageClient = FakeMessageClient(["not json", json.dumps(_research_payload())])
    SearchClient = FakeSearchClient()

    Brief = ResearchAgent(MessageClient, SearchClient).run(_scope())

    assert Brief.Topic == "AI infrastructure"
    assert len(MessageClient.Requests) == 2
    RetryPrompt = MessageClient.Requests[1].messages[0]["content"]
    assert "validation_errors" in RetryPrompt
    assert "Return only valid JSON" in RetryPrompt
