"""Command-line entry point for local pipeline operations."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict
from typing import Any

from augmented_investor.config import ProviderConfigError, load_settings
from augmented_investor.foundry_client import FoundryClient, FoundrySmokeTestError


LIVE_FOUNDRY_TEST_FLAG = "RUN_LIVE_FOUNDRY_TESTS"


def main(argv: list[str] | None = None) -> int:
    """Run the command-line interface and return a process exit code."""

    Parser = _build_parser()
    Args = Parser.parse_args(argv)

    if Args.command == "foundry-smoke-test":
        return _run_foundry_smoke_test(Args)

    Parser.print_help()
    return 1


def _build_parser() -> argparse.ArgumentParser:
    """Create the command parser."""

    Parser = argparse.ArgumentParser(prog="augmented-investor")
    Subparsers = Parser.add_subparsers(dest="command")
    SmokeParser = Subparsers.add_parser(
        "foundry-smoke-test",
        help="Run an opt-in Azure AI Foundry smoke test.",
    )
    SmokeParser.add_argument(
        "--skip-tool-probe",
        action="store_true",
        help="Send the tiny prompt without probing web-search tool support.",
    )
    return Parser


def _run_foundry_smoke_test(args: argparse.Namespace) -> int:
    """Run the gated live Foundry smoke test."""

    if os.getenv(LIVE_FOUNDRY_TEST_FLAG) != "1":
        print(
            f"Live Foundry smoke test is disabled. Set {LIVE_FOUNDRY_TEST_FLAG}=1 "
            "to run it intentionally.",
            file=sys.stderr,
        )
        return 2

    try:
        Settings = load_settings()
        with FoundryClient(Settings) as Client:
            Result = Client.smoke_test(include_tool_probe=not args.skip_tool_probe)
    except (ProviderConfigError, FoundrySmokeTestError, ValueError) as Error:
        print(f"Foundry smoke test failed: {Error}", file=sys.stderr)
        if isinstance(Error, FoundrySmokeTestError) and Error.request_summary:
            _print_request_summary(Error.request_summary)
        return 1

    print(json.dumps(asdict(Result), indent=2, sort_keys=True))
    return 0


def _print_request_summary(request_summary: dict[str, Any]) -> None:
    """Print a redacted request summary for troubleshooting smoke-test failures."""

    print("Redacted request summary:", file=sys.stderr)
    print(json.dumps(request_summary, indent=2, sort_keys=True), file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
