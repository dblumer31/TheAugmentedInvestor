"""Unit tests for command-line smoke-test behavior."""

from __future__ import annotations

from augmented_investor import cli


def test_foundry_smoke_test_cli_is_gated_by_environment(monkeypatch, capsys):
    """The CLI should not run live Foundry calls unless explicitly enabled."""

    monkeypatch.delenv(cli.LIVE_FOUNDRY_TEST_FLAG, raising=False)

    ExitCode = cli.main(["foundry-smoke-test"])

    Captured = capsys.readouterr()
    assert ExitCode == 2
    assert cli.LIVE_FOUNDRY_TEST_FLAG in Captured.err
