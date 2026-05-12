"""Unit tests for the Fix Pass Agent with fake message clients."""

from __future__ import annotations

from dataclasses import dataclass
import json

from augmented_investor.agents.fix_pass_agent import FixPassAgent
from augmented_investor.foundry_client import FoundryMessageRequest, FoundryMessageResponse
from augmented_investor.models.common import ClaimType
from augmented_investor.models.draft import DraftIssue
from augmented_investor.models.fact_check import (
    ActualSourceQuality,
    FactCheckCategory,
    FactCheckFlag,
    FactCheckReport,
    RequiredSourceQuality,
    Severity,
    TriageBucket,
    VerificationStatus,
)


def _draft() -> DraftIssue:
    """Return a draft fixture with clean and flagged sections."""

    return DraftIssue(
        subjectLine="AI infrastructure",
        title="The Durability Question",
        subtitle="A contrarian read",
        lede="Keep this lede.",
        body="Keep this clean section.\nInvestors should buy after the 42% move.",
        sourcesUsed=["Company filings"],
        wordCount=120,
    )


def _flag(category: FactCheckCategory, triage: TriageBucket, claim_type: ClaimType) -> FactCheckFlag:
    """Return a fact-check flag fixture."""

    return FactCheckFlag(
        category=category,
        severity=Severity.Error,
        excerpt="Investors should buy after the 42% move.",
        issue="Issue",
        suggestion="Suggestion",
        claimType=claim_type,
        requiredSourceQuality=RequiredSourceQuality.PrimaryMarketData,
        actualSourceQuality=ActualSourceQuality.BlogOrSubstack,
        verificationStatus=VerificationStatus.NeedsPrimarySource,
        triage=triage,
        addendumQuery="primary source",
    )


def _report() -> FactCheckReport:
    """Return a fact-check report with repairable and skipped flags."""

    return FactCheckReport(
        flags=[
            _flag(
                FactCheckCategory.InvestmentAdvice,
                TriageBucket.FixableWithExistingResearch,
                ClaimType.EditorialInterpretation,
            ),
            _flag(
                FactCheckCategory.OverreliesOnBlogOrSubstack,
                TriageBucket.NeedsResearchAddendum,
                ClaimType.Valuation,
            ),
            _flag(
                FactCheckCategory.MissingCounterargument,
                TriageBucket.NeedsResearchAddendum,
                ClaimType.EditorialInterpretation,
            ),
        ],
        sourceQualitySummary={
            "weakSourceFlags": 1,
            "unverifiedQuantClaims": 1,
            "blogOnlyClaims": 1,
            "overallSourceQuality": "unreliable",
        },
        overallScore="needs_work",
        summary="Needs work",
    )


def _fixed_payload() -> dict:
    """Return a valid fixed draft payload."""

    return {
        "subjectLine": "AI infrastructure",
        "title": "The Durability Question",
        "subtitle": "A contrarian read",
        "lede": "Keep this lede.",
        "body": "Keep this clean section.\nWhat would make the 42% move sustainable?",
        "sourcesUsed": ["Company filings"],
        "wordCount": 115,
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


def test_fix_pass_agent_filters_skipped_flags_and_records_actions():
    """Fix Pass should repair only eligible flags and persist audit metadata."""

    MessageClient = FakeMessageClient([json.dumps(_fixed_payload())])

    FixedDraft = FixPassAgent(MessageClient).run(_draft(), _report())

    Prompt = MessageClient.Requests[0].messages[0]["content"]
    assert "MissingCounterargument" not in Prompt
    assert "Keep this clean section" in FixedDraft.Body
    assert "investment_advice" in FixedDraft.AddressedFlagCategories
    assert "overrelies_on_blog_or_substack" in FixedDraft.AddressedFlagCategories
    assert "removed claim" in FixedDraft.FixPassActions
    assert "softened weak-source quant" in FixedDraft.FixPassActions


def test_fix_pass_agent_retries_once_with_validation_context():
    """Invalid fixed-draft JSON should trigger one bounded validation retry."""

    MessageClient = FakeMessageClient(["not json", json.dumps(_fixed_payload())])

    FixedDraft = FixPassAgent(MessageClient).run(_draft(), _report())

    assert FixedDraft.Title == "The Durability Question"
    assert len(MessageClient.Requests) == 2
    RetryPrompt = MessageClient.Requests[1].messages[0]["content"]
    assert "validation_errors" in RetryPrompt
    assert "Return only valid JSON" in RetryPrompt
