"""Shared pytest fixtures that avoid real environment files and secrets."""

from __future__ import annotations

from pathlib import Path
import sys

import pytest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))


@pytest.fixture
def fake_foundry_env() -> dict[str, str]:
    """Return fake Foundry environment variables safe for unit tests."""

    return {
        "AZURE_FOUNDRY_ENDPOINT": "https://example.services.ai.azure.com",
        "AZURE_FOUNDRY_API_KEY": "test-api-key",
        "FOUNDRY_DEFAULT_MODEL": "claude-opus-4-7",
        "FOUNDRY_SONNET_MODEL": "claude-sonnet-4-6",
        "FOUNDRY_OPUS_MODEL": "claude-opus-4-7",
        "FOUNDRY_ANTHROPIC_VERSION": "2023-06-01",
        "FOUNDRY_TIMEOUT_SECONDS": "120",
        "EXTERNAL_SEARCH_PROVIDER": "none",
    }
