"""Unit tests for the Thesis Agent with fake message clients."""

from __future__ import annotations

from dataclasses import dataclass
import json

from augmented_investor.agents.thesis_agent import ThesisAgent
from augmented_investor.foundry_client import FoundryMessageRequest, FoundryMessageResponse
from augmented_investor.models.common import ClaimType, SourceQuality
from augmented_investor.models.research import ResearchBrief, ResearchClaim, ResearchPoint


def _research() -> ResearchBrief:
    """Return a research fixture with supporting and opposing evidence."""

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
        evidenceFor=[
            ResearchPoint(
                point="Cloud capex plans remain elevated.",
                claimType=ClaimType.CompanyFinancial,
                source="Company filings",
                sourceQuality=SourceQuality.CompanyFilingOrIr,
                supportsExactClaim=True,
                confidence="medium",
            )
        ],
        evidenceAgainst=[
            ResearchPoint(
                point="Capacity could overshoot demand.",
                claimType=ClaimType.Forecast,
                source="Reputable media",
                sourceQuality=SourceQuality.ReputableFinancialMedia,
                supportsExactClaim=True,
                confidence="medium",
            )
        ],
        recommendedAngle="Durability versus cyclicality.",
    )


def _thesis_payload() -> dict:
    """Return a valid thesis payload fixture."""

    return {
        "centralThesis": "AI infrastructure demand is more durable than cyclicals imply.",
        "thesisBasis": "Supporting evidence outweighs near-term capacity concerns.",
        "bullCase": "Demand accelerates as inference workloads grow.",
        "baseCase": "Demand remains steady while supply catches up.",
        "bearCase": "Capacity overshoots and compresses returns.",
        "scenarioMath": {
            "included": True,
            "projections": ["Scenario analysis: utilization remains above 70%."],
        },
        "whatMispricing": "The market may underprice demand duration.",
        "contrarianTest": "What if capex is simply cyclical?",
        "contrarianAnswer": "Filings suggest demand is still broadening.",
        "newsletterAngle": "Durability versus cyclicality.",
        "confidence": "medium",
        "confidenceRationale": "Evidence is credible but still early.",
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


def test_thesis_agent_produces_valid_thesis_from_research():
    """Thesis output should validate and reference research context in the prompt."""

    MessageClient = FakeMessageClient([json.dumps(_thesis_payload())])

    Thesis = ThesisAgent(MessageClient).run(_research())

    Prompt = MessageClient.Requests[0].messages[0]["content"]
    assert "AI capex is rising" in Prompt
    assert Thesis.CentralThesis.startswith("AI infrastructure demand")
    assert Thesis.ScenarioMath.Included is True
    assert "Scenario analysis" in Thesis.ScenarioMath.Projections[0]


def test_thesis_agent_retries_once_with_validation_context():
    """Invalid thesis JSON should trigger one bounded validation retry."""

    MessageClient = FakeMessageClient(["not json", json.dumps(_thesis_payload())])

    Thesis = ThesisAgent(MessageClient).run(_research())

    assert Thesis.NewsletterAngle == "Durability versus cyclicality."
    assert len(MessageClient.Requests) == 2
    RetryPrompt = MessageClient.Requests[1].messages[0]["content"]
    assert "validation_errors" in RetryPrompt
    assert "Return only valid JSON" in RetryPrompt
