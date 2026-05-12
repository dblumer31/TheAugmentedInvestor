"""Fact Check Agent for source-quality-aware draft audits."""

from __future__ import annotations

from pathlib import Path
import json
from typing import Protocol

from augmented_investor.foundry_client import FoundryMessageRequest, FoundryMessageResponse
from augmented_investor.models.draft import DraftIssue
from augmented_investor.models.fact_check import FactCheckReport
from augmented_investor.models.research import ResearchBrief
from augmented_investor.pipeline.json_parser import (
    JsonValidationError,
    build_retry_context,
    validate_model,
)
from augmented_investor.pipeline.fact_check_postprocess import (
    build_draft_language_flags,
    build_source_quality_flags,
    overall_score,
    summarize_flags,
)


FACT_CHECK_MAX_TOKENS = 8000
PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "fact_check.md"


class MessageClient(Protocol):
    """Provider interface needed by the Fact Check Agent."""

    def send_message(self, request: FoundryMessageRequest) -> FoundryMessageResponse:
        """Send one structured fact-check prompt."""


class FactCheckAgent:
    """Produce a FactCheckReport from a draft and its supporting research."""

    def __init__(self, message_client: MessageClient, prompt_template: str | None = None) -> None:
        self._message_client = message_client
        self._prompt_template = prompt_template or PROMPT_PATH.read_text(encoding="utf-8")

    def run(self, draft: DraftIssue, research: ResearchBrief) -> FactCheckReport:
        """Prompt for fact-check findings and apply deterministic source-quality rules."""

        Prompt = self._build_prompt(draft, research)
        Response = self._message_client.send_message(self._build_request(Prompt))
        try:
            Report = validate_model(Response.text, FactCheckReport)
        except JsonValidationError as Error:
            RetryPrompt = self._build_retry_prompt(Prompt, Error)
            RetryResponse = self._message_client.send_message(self._build_request(RetryPrompt))
            Report = validate_model(RetryResponse.text, FactCheckReport)
        return self._apply_deterministic_rules(Report, draft, research)

    def _build_prompt(self, draft: DraftIssue, research: ResearchBrief) -> str:
        """Build the fact-check prompt from draft and research artifacts."""

        Payload = {
            "draft": draft.model_dump(mode="json"),
            "research": research.model_dump(mode="json"),
        }
        return f"{self._prompt_template}\n\nFact-check context:\n{json.dumps(Payload, indent=2)}"

    def _build_request(self, prompt: str) -> FoundryMessageRequest:
        """Create a Foundry-compatible request for structured fact-check output."""

        return FoundryMessageRequest(
            model_role="sonnet",
            max_tokens=FACT_CHECK_MAX_TOKENS,
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

    def _apply_deterministic_rules(
        self,
        report: FactCheckReport,
        draft: DraftIssue,
        research: ResearchBrief,
    ) -> FactCheckReport:
        """Merge model flags with deterministic source-quality and language flags."""

        Flags = list(report.Flags)
        Flags.extend(build_draft_language_flags(draft))
        Flags.extend(build_source_quality_flags(research))
        return report.model_copy(
            update={
                "Flags": Flags,
                "SourceQualitySummary": summarize_flags(Flags),
                "OverallScore": overall_score(Flags),
                "Summary": _summary_for_flags(Flags),
            }
        )


def _summary_for_flags(flags) -> str:
    """Create a concise deterministic summary for merged fact-check output."""

    if not flags:
        return "No fact-check issues found."
    return f"Found {len(flags)} fact-check issue(s)."
