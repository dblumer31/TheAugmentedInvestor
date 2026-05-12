"""Unit tests for command-line smoke-test behavior."""

from __future__ import annotations

import json

from augmented_investor import cli
from augmented_investor.external_search_client import SearchProviderError
from augmented_investor.pipeline.json_parser import JsonValidationError


def test_foundry_smoke_test_cli_is_gated_by_environment(monkeypatch, capsys):
    """The CLI should not run live Foundry calls unless explicitly enabled."""

    monkeypatch.delenv(cli.LIVE_FOUNDRY_TEST_FLAG, raising=False)

    ExitCode = cli.main(["foundry-smoke-test"])

    Captured = capsys.readouterr()
    assert ExitCode == 2
    assert cli.LIVE_FOUNDRY_TEST_FLAG in Captured.err


def test_cli_can_create_review_and_export_artifact_run(tmp_path, capsys):
    """Artifact-only commands should provide the minimal operator interface."""

    ScopeFile = tmp_path / "scope.json"
    ScopeFile.write_text(
        json.dumps(
            {
                "market": "AI infrastructure",
                "recentWindow": "last quarter",
                "contextWindow": "five years",
                "readerHorizon": "three years",
                "readerType": "generalist investors",
                "depth": "standard",
                "length": "1200",
            }
        ),
        encoding="utf-8",
    )

    CreateExit = cli.main(
        [
            "create-run",
            "--scope-file",
            str(ScopeFile),
            "--runs-dir",
            str(tmp_path / "runs"),
        ]
    )
    Created = json.loads(capsys.readouterr().out)
    RunId = Created["runId"]

    ReviewExit = cli.main(["review-run", RunId, "--runs-dir", str(tmp_path / "runs")])
    Review = json.loads(capsys.readouterr().out)

    assert CreateExit == 0
    assert ReviewExit == 0
    assert Review["runId"] == RunId
    assert Review["exportOptions"]["html"] == "issue.html"


def test_cli_error_prints_redacted_request_summary(capsys):
    """Live-stage failures should include safe provider diagnostics."""

    Error = SearchProviderError(
        "Foundry message request failed",
        request_summary={
            "method": "POST",
            "endpoint": "https://example.com/anthropic/v1/messages",
            "headers": {"x-api-key": "[REDACTED]"},
        },
        cause="ReadTimeout: timed out",
    )

    ExitCode = cli._print_error("run-research failed", Error)

    Captured = capsys.readouterr()
    assert ExitCode == 1
    assert "ReadTimeout" in Captured.err
    assert "Redacted request summary" in Captured.err
    assert "[REDACTED]" in Captured.err


def test_cli_error_prints_validation_context(capsys):
    """Agent validation failures should show bounded schema diagnostics."""

    Error = JsonValidationError(
        "Agent output failed validation for ResearchBrief",
        raw_preview='{"topic":"AI"}',
        validation_errors=[{"loc": ("marketSnapshot",), "msg": "bad", "type": "missing"}],
    )

    ExitCode = cli._print_error("run-research failed", Error)

    Captured = capsys.readouterr()
    assert ExitCode == 1
    assert "Validation errors" in Captured.err
    assert "marketSnapshot" in Captured.err
    assert "Raw output preview" in Captured.err
