"""Command-line entry point for local pipeline operations."""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path
from typing import Any

from augmented_investor.agents.fact_check_agent import FactCheckAgent
from augmented_investor.agents.fix_pass_agent import FixPassAgent
from augmented_investor.agents.research_agent import ResearchAgent
from augmented_investor.agents.thesis_agent import ThesisAgent
from augmented_investor.agents.writer_agent import WriterAgent
from augmented_investor.config import ProviderConfigError, load_settings
from augmented_investor.exporters.html_exporter import export_html
from augmented_investor.exporters.markdown_exporter import export_markdown
from augmented_investor.external_search_client import FoundryToolSearchClient
from augmented_investor.foundry_client import FoundryClient, FoundrySmokeTestError
from augmented_investor.models.scope import ScopeRequest
from augmented_investor.operator_interface import (
    approve_thesis,
    build_review_state,
    create_run_from_scope,
    export_run,
    reject_thesis,
)
from augmented_investor.pipeline.artifact_store import ArtifactStore
from augmented_investor.pipeline.orchestrator import PipelineOrchestrator


LIVE_FOUNDRY_TEST_FLAG = "RUN_LIVE_FOUNDRY_TESTS"
LIVE_STAGE_COMMANDS = {
    "run-research",
    "run-thesis",
    "write-draft",
    "fact-check",
    "apply-fix-pass",
    "recheck",
}


def main(argv: list[str] | None = None) -> int:
    """Run the command-line interface and return a process exit code."""

    Parser = _build_parser()
    Args = Parser.parse_args(argv)

    Handler = _handler_for_command(Args.command)
    if Handler:
        return Handler(Args)

    Parser.print_help()
    return 1


def _handler_for_command(command: str | None):
    """Return the handler for a parsed command."""

    Handlers = {
        "foundry-smoke-test": _run_foundry_smoke_test,
        "create-run": _run_create_run,
        "review-run": _run_review_run,
        "approve-thesis": _run_approve_thesis,
        "reject-thesis": _run_reject_thesis,
        "export-run": _run_export_run,
    }
    if command in LIVE_STAGE_COMMANDS:
        return _run_live_stage
    return Handlers.get(command)


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
    _add_operator_commands(Subparsers)
    return Parser


def _add_operator_commands(subparsers: argparse._SubParsersAction) -> None:
    """Register artifact-backed operator commands."""

    CreateParser = subparsers.add_parser("create-run", help="Create a run from a scope JSON file.")
    CreateParser.add_argument("--scope-file", required=True, help="Path to a scope JSON file.")
    _add_runs_dir_argument(CreateParser)

    for CommandName, HelpText in [
        ("run-research", "Run the live research stage."),
        ("run-thesis", "Run the live thesis stage."),
        ("write-draft", "Run the live writer stage."),
        ("fact-check", "Run the live fact-check stage."),
        ("apply-fix-pass", "Run the live fix-pass stage."),
        ("recheck", "Run the live re-check stage."),
        ("review-run", "Print the current review state for a run."),
        ("approve-thesis", "Approve the persisted thesis for a run."),
        ("export-run", "Write issue.html and issue.md for a run."),
    ]:
        CommandParser = subparsers.add_parser(CommandName, help=HelpText)
        CommandParser.add_argument("run_id", help="Run identifier.")
        _add_runs_dir_argument(CommandParser)

    RejectParser = subparsers.add_parser("reject-thesis", help="Reject the persisted thesis.")
    RejectParser.add_argument("run_id", help="Run identifier.")
    RejectParser.add_argument("--reason", default=None, help="Optional rejection reason.")
    _add_runs_dir_argument(RejectParser)


def _add_runs_dir_argument(parser: argparse.ArgumentParser) -> None:
    """Add the common runs directory argument."""

    parser.add_argument("--runs-dir", default="runs", help="Directory containing run artifacts.")


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


def _run_create_run(args: argparse.Namespace) -> int:
    """Create a new run from a scope file."""

    try:
        Payload = json.loads(Path(args.scope_file).read_text(encoding="utf-8"))
        RunId = create_run_from_scope(_store(args), ScopeRequest.model_validate(Payload))
    except Exception as Error:
        return _print_error("Create run failed", Error)
    _print_json({"runId": RunId})
    return 0


def _run_review_run(args: argparse.Namespace) -> int:
    """Print review state for a run."""

    try:
        ReviewState = build_review_state(_store(args), args.run_id)
    except Exception as Error:
        return _print_error("Review failed", Error)
    _print_json(ReviewState)
    return 0


def _run_approve_thesis(args: argparse.Namespace) -> int:
    """Approve a thesis for a run."""

    try:
        State = approve_thesis(_store(args), args.run_id)
    except Exception as Error:
        return _print_error("Approve thesis failed", Error)
    _print_json(State)
    return 0


def _run_reject_thesis(args: argparse.Namespace) -> int:
    """Reject a thesis for a run."""

    try:
        State = reject_thesis(_store(args), args.run_id, args.reason)
    except Exception as Error:
        return _print_error("Reject thesis failed", Error)
    _print_json(State)
    return 0


def _run_export_run(args: argparse.Namespace) -> int:
    """Export current draft artifacts for a run."""

    try:
        Paths = export_run(_store(args), args.run_id)
    except Exception as Error:
        return _print_error("Export failed", Error)
    _print_json({Key: str(Value) for Key, Value in Paths.items()})
    return 0


def _run_live_stage(args: argparse.Namespace) -> int:
    """Run one live provider-backed pipeline stage."""

    try:
        Settings = load_settings()
        with FoundryClient(Settings) as Client:
            Orchestrator = _build_live_orchestrator(_store(args), Client)
            Result = _dispatch_stage(Orchestrator, args.command, args.run_id)
    except Exception as Error:
        return _print_error(f"{args.command} failed", Error)
    _print_json(_json_ready(Result))
    return 0


def _build_live_orchestrator(store: ArtifactStore, client: FoundryClient) -> PipelineOrchestrator:
    """Build the live orchestrator used by stage execution commands."""

    ResearchAgentInstance = ResearchAgent(client, FoundryToolSearchClient(client))
    ThesisAgentInstance = ThesisAgent(client)
    WriterAgentInstance = WriterAgent(client)
    FactCheckAgentInstance = FactCheckAgent(client)
    FixPassAgentInstance = FixPassAgent(client)
    return PipelineOrchestrator(
        store,
        research_stage=ResearchAgentInstance.run,
        thesis_stage=ThesisAgentInstance.run,
        writer_stage=WriterAgentInstance.run,
        fact_check_stage=FactCheckAgentInstance.run,
        fix_pass_stage=FixPassAgentInstance.run,
        export_stage=lambda Draft: (
            export_html(Draft),
            export_markdown(Draft),
        ),
    )


def _dispatch_stage(orchestrator: PipelineOrchestrator, command: str, run_id: str):
    """Dispatch a CLI command to an orchestrator stage."""

    StageFunctions = {
        "run-research": orchestrator.run_research,
        "run-thesis": orchestrator.run_thesis,
        "write-draft": orchestrator.write_draft,
        "fact-check": orchestrator.fact_check_draft,
        "apply-fix-pass": orchestrator.apply_fix_pass,
        "recheck": orchestrator.recheck_draft,
    }
    return StageFunctions[command](run_id)


def _store(args: argparse.Namespace) -> ArtifactStore:
    """Build an artifact store from CLI arguments."""

    return ArtifactStore(Path(args.runs_dir))


def _json_ready(value: Any) -> Any:
    """Convert common return values into JSON-serializable data."""

    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    return value


def _print_json(payload: Any) -> None:
    """Print JSON output for CLI automation."""

    print(json.dumps(payload, indent=2, sort_keys=True))


def _print_error(prefix: str, error: Exception) -> int:
    """Print a concise CLI error and return a failure exit code."""

    print(f"{prefix}: {error}", file=sys.stderr)
    return 1


def _print_request_summary(request_summary: dict[str, Any]) -> None:
    """Print a redacted request summary for troubleshooting smoke-test failures."""

    print("Redacted request summary:", file=sys.stderr)
    print(json.dumps(request_summary, indent=2, sort_keys=True), file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
