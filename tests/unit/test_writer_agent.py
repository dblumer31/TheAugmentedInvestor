"""Unit tests for the Writer Agent with fake message clients."""

from __future__ import annotations

from dataclasses import dataclass
import json

from augmented_investor.agents.writer_agent import WriterAgent
from augmented_investor.foundry_client import FoundryMessageRequest, FoundryMessageResponse
from augmented_investor.models.common import ClaimType, SourceQuality
from augmented_investor.models.research import ResearchBrief, ResearchClaim
from augmented_investor.models.scope import ScopeRequest
from augmented_investor.models.thesis import ThesisBrief


def _scope() -> ScopeRequest:
    """Return a scope fixture."""

    return ScopeRequest(
        market="AI infrastructure",
        recentWindow="last 30 days",
        contextWindow="three years",
        readerHorizon="long term",
        readerType="operator-investor",
        depth="deep",
        length="1500 words",
    )


def _research() -> ResearchBrief:
    """Return a research fixture."""

    return ResearchBrief(
        topic="AI infrastructure",
        marketSnapshot=[
            ResearchClaim(
                claim="AI capex is rising.",
                instrument="AI infrastructure equities",
                instrumentPrecision="sector basket",
                claimType=ClaimType.CompanyFinancial,
                source="Company filings",
                sourceQuality=SourceQuality.CompanyFilingOrIr,
                supportsExactClaim=True,
                quotedEvidence="Capital expenditure increased.",
                confidence="high",
            )
        ],
        recommendedAngle="Durability versus cyclicality.",
    )


def _thesis() -> ThesisBrief:
    """Return a thesis fixture."""

    return ThesisBrief(
        centralThesis="AI infrastructure demand is durable.",
        thesisBasis="Capex and utilization support the thesis.",
        bullCase="Demand accelerates.",
        baseCase="Demand remains steady.",
        bearCase="Capacity overshoots demand.",
        whatMispricing="The market may underprice durability.",
        contrarianTest="What if capex is cyclical?",
        newsletterAngle="Durability versus cyclicality.",
        confidence="medium",
        confidenceRationale="Evidence is early but consistent.",
    )


def _draft_payload() -> dict:
    """Return a valid draft payload fixture."""

    return {
        "subjectLine": "AI infrastructure durability",
        "title": "The Durability Question",
        "subtitle": "A contrarian read on AI capex",
        "lede": "AI infrastructure demand may last longer than expected.",
        "body": (
            "AI infrastructure demand is durable, based on company filings. "
            "Scenario analysis suggests utilization could remain elevated. "
            "What would prove this durability wrong?"
        ),
        "sourcesUsed": ["Company filings"],
        "wordCount": 150,
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


def test_writer_agent_generates_valid_draft_from_scope_thesis_and_research():
    """Writer prompt should include scope, thesis, and evidence contracts."""

    MessageClient = FakeMessageClient([json.dumps(_draft_payload())])

    Draft = WriterAgent(MessageClient).run(_thesis(), _research(), _scope())

    Prompt = MessageClient.Requests[0].messages[0]["content"]
    assert "operator-investor" in Prompt
    assert "1500 words" in Prompt
    assert "AI infrastructure demand is durable" in Prompt
    assert Draft.Title == "The Durability Question"
    assert Draft.SourcesUsed == ["Company filings"]
    assert Draft.Body.endswith("?")


def test_writer_agent_retries_once_with_validation_context():
    """Invalid draft JSON should trigger one bounded validation retry."""

    MessageClient = FakeMessageClient(["not json", json.dumps(_draft_payload())])

    Draft = WriterAgent(MessageClient).run(_thesis(), _research(), _scope())

    assert Draft.SubjectLine == "AI infrastructure durability"
    assert len(MessageClient.Requests) == 2
    RetryPrompt = MessageClient.Requests[1].messages[0]["content"]
    assert "validation_errors" in RetryPrompt
    assert "Return only valid JSON" in RetryPrompt
