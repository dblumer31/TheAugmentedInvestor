"""Thesis Agent implementation for structured editorial argument generation."""

from __future__ import annotations

from pathlib import Path
import json
from typing import Protocol

from augmented_investor.foundry_client import FoundryMessageRequest, FoundryMessageResponse
from augmented_investor.models.research import ResearchBrief
from augmented_investor.models.thesis import ThesisBrief
from augmented_investor.pipeline.json_parser import (
    JsonValidationError,
    build_retry_context,
    validate_model,
)


THESIS_MAX_TOKENS = 2500
PROMPT_PATH = Path(__file__).resolve().parents[1] / "prompts" / "thesis.md"


class MessageClient(Protocol):
    """Provider interface needed by the Thesis Agent."""

    def send_message(self, request: FoundryMessageRequest) -> FoundryMessageResponse:
        """Send one structured thesis prompt."""


class ThesisAgent:
    """Produce a validated ThesisBrief from a ResearchBrief."""

    def __init__(self, message_client: MessageClient, prompt_template: str | None = None) -> None:
        self._message_client = message_client
        self._prompt_template = prompt_template or PROMPT_PATH.read_text(encoding="utf-8")

    def run(self, research: ResearchBrief) -> ThesisBrief:
        """Prompt for a thesis and perform one validation retry if needed."""

        Prompt = self._build_prompt(research)
        Response = self._message_client.send_message(self._build_request(Prompt))
        try:
            return validate_model(Response.text, ThesisBrief)
        except JsonValidationError as Error:
            RetryPrompt = self._build_retry_prompt(Prompt, Error)
            RetryResponse = self._message_client.send_message(self._build_request(RetryPrompt))
            return validate_model(RetryResponse.text, ThesisBrief)

    def _build_prompt(self, research: ResearchBrief) -> str:
        """Build the thesis prompt from the research brief."""

        Payload = {"research": research.model_dump(mode="json")}
        return f"{self._prompt_template}\n\nResearch context:\n{json.dumps(Payload, indent=2)}"

    def _build_request(self, prompt: str) -> FoundryMessageRequest:
        """Create a Foundry-compatible request for structured thesis output."""

        return FoundryMessageRequest(
            model_role="sonnet",
            max_tokens=THESIS_MAX_TOKENS,
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
