"""Unit tests for log-safe secret redaction boundaries."""

from __future__ import annotations

from augmented_investor.foundry_client import REDACTED, _redact_headers


def test_redact_headers_hides_known_secret_headers():
    """Credential-bearing headers should be redacted before diagnostics are built."""

    Headers = {
        "x-api-key": "raw-secret",
        "Authorization": "Bearer raw-secret",
        "content-type": "application/json",
    }

    RedactedHeaders = _redact_headers(Headers)

    assert RedactedHeaders["x-api-key"] == REDACTED
    assert RedactedHeaders["Authorization"] == REDACTED
    assert RedactedHeaders["content-type"] == "application/json"
    assert "raw-secret" not in str(RedactedHeaders)
