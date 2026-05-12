"""Unit tests for command-line smoke-test behavior."""

from __future__ import annotations

import json

from augmented_investor import cli


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
