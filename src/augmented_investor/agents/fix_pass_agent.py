"""Fix Pass Agent for surgical draft repair after fact-checking."""

from __future__ import annotations

from pathlib import Path
import json
from typing import Protocol

from augmented_investor.foundry_client import FoundryMessageRequest, FoundryMessageResponse
from augmented_investor.models.draft import DraftIssue
from augmented_investor.models.fact_check import FactCheckReport
from augmented_investor.pipeline.fix_pass_rules import (
    addressed_flag_categories,
    fix_pass_actions,
    partition_fixable_flags,
)
from augmented_investor.pipeline.json_parser import (
    JsonValidationError,
    build_retry_context,
    validate_model,
)


FIX_PASS_MAX_TOKENS = 5000
PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "fix_pass.md"


class MessageClient(Protocol):
    """Provider interface needed by the Fix Pass Agent."""

    def send_message(self, request: FoundryMessageRequest) -> FoundryMessageResponse:
        """Send one structured fix-pass prompt."""


class FixPassAgent:
    """Produce a fixed DraftIssue from an original draft and fact-check report."""

    def __init__(self, message_client: MessageClient, prompt_template: str | None = None) -> None:
        self._message_client = message_client
        self._prompt_template = prompt_template or PROMPT_PATH.read_text(encoding="utf-8")

    def run(self, draft: DraftIssue, report: FactCheckReport) -> DraftIssue:
        """Prompt for a fixed draft and perform one validation retry if needed."""

        Partition = partition_fixable_flags(report.Flags)
        Prompt = self._build_prompt(draft, report, Partition.RepairableFlags)
        Response = self._message_client.send_message(self._build_request(Prompt))
        try:
            FixedDraft = validate_model(Response.text, DraftIssue)
        except JsonValidationError as Error:
            RetryPrompt = self._build_retry_prompt(Prompt, Error)
            RetryResponse = self._message_client.send_message(self._build_request(RetryPrompt))
            FixedDraft = validate_model(RetryResponse.text, DraftIssue)
        return FixedDraft.model_copy(
            update={
                "AddressedFlagCategories": addressed_flag_categories(Partition.RepairableFlags),
                "FixPassActions": fix_pass_actions(Partition.RepairableFlags),
            }
        )

    def _build_prompt(
        self,
        draft: DraftIssue,
        report: FactCheckReport,
        repairable_flags,
    ) -> str:
        """Build the fix-pass prompt using only repairable flags."""

        Payload = {
            "draft": draft.model_dump(mode="json"),
            "repairableFlags": [Flag.model_dump(mode="json") for Flag in repairable_flags],
            "sourceQualitySummary": report.SourceQualitySummary.model_dump(mode="json"),
        }
        return f"{self._prompt_template}\n\nFix-pass context:\n{json.dumps(Payload, indent=2)}"

    def _build_request(self, prompt: str) -> FoundryMessageRequest:
        """Create a Foundry-compatible request for structured fixed draft output."""

        return FoundryMessageRequest(
            model_role="sonnet",
            max_tokens=FIX_PASS_MAX_TOKENS,
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
