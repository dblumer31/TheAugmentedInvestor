"""Unit tests for the Fact Check Agent with fake message clients."""

from __future__ import annotations

from dataclasses import dataclass
import json

from augmented_investor.agents.fact_check_agent import FactCheckAgent
from augmented_investor.foundry_client import FoundryMessageRequest, FoundryMessageResponse
from augmented_investor.models.common import ClaimType, SourceQuality
from augmented_investor.models.draft import DraftIssue
from augmented_investor.models.fact_check import FactCheckCategory
from augmented_investor.models.research import ResearchBrief, ResearchClaim


def _draft() -> DraftIssue:
    """Return a draft fixture with a direct advice phrase."""

    return DraftIssue(
        subjectLine="AI infrastructure",
        title="The Durability Question",
        subtitle="A contrarian read",
        lede="AI demand may last.",
        body="Investors should buy the basket. Base case returns reach 20%.",
        sourcesUsed=["https://example.com/blog"],
        wordCount=120,
    )


def _research() -> ResearchBrief:
    """Return research with weak source quality for deterministic post-processing."""

    return ResearchBrief(
        topic="AI infrastructure",
        marketSnapshot=[
            ResearchClaim(
                claim="The basket returned 20%.",
                claimType=ClaimType.MarketReturn,
                source="Market blog",
                sourceQuality=SourceQuality.BlogOrSubstack,
                supportsExactClaim=True,
                confidence="low",
            )
        ],
    )


def _empty_report_payload() -> dict:
    """Return a valid empty fact-check report payload."""

    return {
        "flags": [],
        "sourceQualitySummary": {
            "weakSourceFlags": 0,
            "unverifiedQuantClaims": 0,
            "blogOnlyClaims": 0,
            "overallSourceQuality": "strong",
        },
        "overallScore": "clean",
        "summary": "No model-generated flags.",
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


def test_fact_check_agent_merges_llm_report_with_deterministic_flags():
    """Fact Check Agent should append deterministic source-quality and draft flags."""

    MessageClient = FakeMessageClient([json.dumps(_empty_report_payload())])

    Report = FactCheckAgent(MessageClient).run(_draft(), _research())

    Categories = {Flag.Category for Flag in Report.Flags}
    assert FactCheckCategory.InvestmentAdvice in Categories
    assert FactCheckCategory.ScenarioMathUnlabeled in Categories
    assert FactCheckCategory.OverreliesOnBlogOrSubstack in Categories
    assert Report.SourceQualitySummary.WeakSourceFlags >= 1
    assert Report.SourceQualitySummary.BlogOnlyClaims >= 1
    assert Report.OverallScore == "needs_work"


def test_fact_check_agent_retries_once_with_validation_context():
    """Invalid fact-check JSON should trigger one bounded validation retry."""

    MessageClient = FakeMessageClient(["not json", json.dumps(_empty_report_payload())])

    Report = FactCheckAgent(MessageClient).run(_draft(), _research())

    assert Report.Flags
    assert len(MessageClient.Requests) == 2
    RetryPrompt = MessageClient.Requests[1].messages[0]["content"]
    assert "validation_errors" in RetryPrompt
    assert "Return only valid JSON" in RetryPrompt
