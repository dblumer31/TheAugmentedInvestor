"""Opt-in live integration test for Azure AI Foundry smoke testing."""

from __future__ import annotations

import os

import pytest

from augmented_investor.config import load_settings
from augmented_investor.foundry_client import FoundryClient


@pytest.mark.skipif(
    os.getenv("RUN_LIVE_FOUNDRY_TESTS") != "1",
    reason="Live Foundry tests disabled. Set RUN_LIVE_FOUNDRY_TESTS=1.",
)
def test_live_foundry_smoke_test():
    """Run the live Foundry smoke test only when explicitly enabled."""

    Settings = load_settings()

    with FoundryClient(Settings) as Client:
        Result = Client.smoke_test()

    assert Result.status_code < 400
    assert Result.model_alias
    assert Result.request_summary["headers"]["x-api-key"] == "[REDACTED]"
