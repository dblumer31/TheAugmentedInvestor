"""Writer Agent implementation for structured newsletter draft generation."""

from __future__ import annotations

from pathlib import Path
import json
from typing import Protocol

from augmented_investor.foundry_client import FoundryMessageRequest, FoundryMessageResponse
from augmented_investor.models.draft import DraftIssue
from augmented_investor.models.research import ResearchBrief
from augmented_investor.models.scope import ScopeRequest
from augmented_investor.models.thesis import ThesisBrief
from augmented_investor.pipeline.json_parser import (
    JsonValidationError,
    build_retry_context,
    validate_model,
)


WRITER_MAX_TOKENS = 5000
PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "writer.md"


class MessageClient(Protocol):
    """Provider interface needed by the Writer Agent."""

    def send_message(self, request: FoundryMessageRequest) -> FoundryMessageResponse:
        """Send one structured writer prompt."""


class WriterAgent:
    """Produce a validated DraftIssue from approved thesis, research, and scope."""

    def __init__(self, message_client: MessageClient, prompt_template: str | None = None) -> None:
        self._message_client = message_client
        self._prompt_template = prompt_template or PROMPT_PATH.read_text(encoding="utf-8")

    def run(
        self,
        thesis: ThesisBrief,
        research: ResearchBrief,
        scope: ScopeRequest,
    ) -> DraftIssue:
        """Prompt for a draft and perform one validation retry if needed."""

        Prompt = self._build_prompt(thesis, research, scope)
        Response = self._message_client.send_message(self._build_request(Prompt))
        try:
            return validate_model(Response.text, DraftIssue)
        except JsonValidationError as Error:
            RetryPrompt = self._build_retry_prompt(Prompt, Error)
            RetryResponse = self._message_client.send_message(self._build_request(RetryPrompt))
            return validate_model(RetryResponse.text, DraftIssue)

    def _build_prompt(
        self,
        thesis: ThesisBrief,
        research: ResearchBrief,
        scope: ScopeRequest,
    ) -> str:
        """Build the writer prompt from approved thesis, research, and scope."""

        Payload = {
            "scope": scope.model_dump(mode="json"),
            "approvedThesis": thesis.model_dump(mode="json"),
            "research": research.model_dump(mode="json"),
        }
        return f"{self._prompt_template}\n\nDraft context:\n{json.dumps(Payload, indent=2)}"

    def _build_request(self, prompt: str) -> FoundryMessageRequest:
        """Create a Foundry-compatible request for structured draft output."""

        return FoundryMessageRequest(
            model_role="sonnet",
            max_tokens=WRITER_MAX_TOKENS,
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
