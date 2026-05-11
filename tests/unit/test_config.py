"""Unit tests for environment-backed application configuration."""

from __future__ import annotations

import pytest

from augmented_investor.config import AppSettings, ProviderConfigError, load_settings


def test_load_settings_reads_fake_environment(monkeypatch, fake_foundry_env):
    """Settings should prefer explicit environment variables."""

    for EnvName, EnvValue in fake_foundry_env.items():
        monkeypatch.setenv(EnvName, EnvValue)

    Settings = load_settings()

    assert Settings.AzureFoundryEndpoint == fake_foundry_env["AZURE_FOUNDRY_ENDPOINT"]
    assert Settings.AzureFoundryApiKey is not None
    assert Settings.AzureFoundryApiKey.get_secret_value() == "test-api-key"
    assert Settings.FoundryDefaultModel == fake_foundry_env["FOUNDRY_DEFAULT_MODEL"]
    assert Settings.FoundryTimeoutSeconds == 120
    assert Settings.ExternalSearchProvider == "none"


def test_load_settings_reads_local_env_file(monkeypatch, tmp_path):
    """Runtime settings should load from a local .env file when present."""

    EnvFile = tmp_path / ".env"
    EnvFile.write_text(
        "\n".join(
            [
                "AZURE_FOUNDRY_ENDPOINT=https://env-file.services.ai.azure.com",
                "AZURE_FOUNDRY_API_KEY=env-file-api-key",
                "FOUNDRY_DEFAULT_MODEL=env-file-model",
                "FOUNDRY_ANTHROPIC_VERSION=2023-06-01",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.chdir(tmp_path)

    Settings = load_settings()

    assert Settings.AzureFoundryEndpoint == "https://env-file.services.ai.azure.com"
    assert Settings.AzureFoundryApiKey is not None
    assert Settings.AzureFoundryApiKey.get_secret_value() == "env-file-api-key"
    assert Settings.FoundryDefaultModel == "env-file-model"


def test_live_provider_validation_accepts_complete_fake_config(fake_foundry_env):
    """Complete fake live-provider settings should pass validation."""

    Settings = AppSettings(**fake_foundry_env)

    Settings.validate_live_provider_config()


def test_live_provider_validation_reports_missing_required_fields():
    """Missing live-provider settings should produce a clear validation error."""

    Settings = AppSettings(_env_file=None)

    with pytest.raises(ProviderConfigError) as ErrorInfo:
        Settings.validate_live_provider_config()

    ErrorMessage = str(ErrorInfo.value)
    assert "AZURE_FOUNDRY_ENDPOINT" in ErrorMessage
    assert "AZURE_FOUNDRY_API_KEY" in ErrorMessage
    assert "FOUNDRY_DEFAULT_MODEL" in ErrorMessage
    assert "FOUNDRY_ANTHROPIC_VERSION" in ErrorMessage


def test_live_provider_validation_rejects_placeholder_secret():
    """Placeholder secrets from example config should not pass live validation."""

    Settings = AppSettings(
        AZURE_FOUNDRY_ENDPOINT="https://example.services.ai.azure.com",
        AZURE_FOUNDRY_API_KEY="replace_me",
        FOUNDRY_DEFAULT_MODEL="claude-opus-4-7",
        FOUNDRY_ANTHROPIC_VERSION="2023-06-01",
    )

    with pytest.raises(ProviderConfigError) as ErrorInfo:
        Settings.validate_live_provider_config()

    assert "AZURE_FOUNDRY_API_KEY" in str(ErrorInfo.value)
