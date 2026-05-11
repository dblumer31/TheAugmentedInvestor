"""Application configuration loaded from environment variables and local .env files.

Runtime code may load a local .env file, but tests can disable env-file loading explicitly.
"""

from __future__ import annotations

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


PLACEHOLDER_VALUES = {"", "replace_me", "replace_me_if_used"}


class ProviderConfigError(ValueError):
    """Raised when live provider configuration is incomplete or still placeholder-only."""


class AppSettings(BaseSettings):
    """Environment-backed settings for model and optional search providers."""

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    AzureFoundryEndpoint: str | None = Field(
        default=None,
        validation_alias="AZURE_FOUNDRY_ENDPOINT",
    )
    AzureFoundryApiKey: SecretStr | None = Field(
        default=None,
        validation_alias="AZURE_FOUNDRY_API_KEY",
    )
    FoundryDefaultModel: str | None = Field(
        default=None,
        validation_alias="FOUNDRY_DEFAULT_MODEL",
    )
    FoundrySonnetModel: str | None = Field(
        default=None,
        validation_alias="FOUNDRY_SONNET_MODEL",
    )
    FoundryOpusModel: str | None = Field(
        default=None,
        validation_alias="FOUNDRY_OPUS_MODEL",
    )
    FoundryAnthropicVersion: str | None = Field(
        default=None,
        validation_alias="FOUNDRY_ANTHROPIC_VERSION",
    )
    FoundryTimeoutSeconds: int = Field(
        default=120,
        validation_alias="FOUNDRY_TIMEOUT_SECONDS",
        gt=0,
    )
    ExternalSearchProvider: str = Field(
        default="none",
        validation_alias="EXTERNAL_SEARCH_PROVIDER",
    )
    ExternalSearchEndpoint: str | None = Field(
        default=None,
        validation_alias="EXTERNAL_SEARCH_ENDPOINT",
    )
    ExternalSearchApiKey: SecretStr | None = Field(
        default=None,
        validation_alias="EXTERNAL_SEARCH_API_KEY",
    )

    def validate_live_provider_config(self) -> None:
        """Validate that all required Foundry settings are present for live requests."""

        MissingFields = [
            EnvName
            for EnvName, Value in self._live_provider_values().items()
            if _is_missing_or_placeholder(Value)
        ]
        if MissingFields:
            MissingList = ", ".join(MissingFields)
            raise ProviderConfigError(
                f"Live Foundry provider configuration is incomplete: {MissingList}"
            )

    def _live_provider_values(self) -> dict[str, str | SecretStr | None]:
        """Return settings required before making any live Foundry request."""

        return {
            "AZURE_FOUNDRY_ENDPOINT": self.AzureFoundryEndpoint,
            "AZURE_FOUNDRY_API_KEY": self.AzureFoundryApiKey,
            "FOUNDRY_DEFAULT_MODEL": self.FoundryDefaultModel,
            "FOUNDRY_ANTHROPIC_VERSION": self.FoundryAnthropicVersion,
        }


def load_settings() -> AppSettings:
    """Load application settings from environment variables and a local .env file."""

    return AppSettings()


def _is_missing_or_placeholder(Value: str | SecretStr | None) -> bool:
    """Return whether a config value is missing or still set to a documented placeholder."""

    if Value is None:
        return True
    if isinstance(Value, SecretStr):
        PlainValue = Value.get_secret_value()
    else:
        PlainValue = Value
    return PlainValue.strip().lower() in PLACEHOLDER_VALUES
