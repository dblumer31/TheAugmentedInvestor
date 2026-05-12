"""Mocked agent-level end-to-end tests for the editorial pipeline."""

from __future__ import annotations

from datetime import UTC, datetime

from augmented_investor.agents.fact_check_agent import FactCheckAgent
from augmented_investor.agents.fix_pass_agent import FixPassAgent
from augmented_investor.agents.research_agent import ResearchAgent
from augmented_investor.agents.thesis_agent import ThesisAgent
from augmented_investor.agents.writer_agent import WriterAgent
from augmented_investor.foundry_client import FoundryMessageRequest, FoundryMessageResponse
from augmented_investor.models.research import SearchResult, SourceEvidence
from augmented_investor.operator_interface import export_run
from augmented_investor.pipeline.orchestrator import PipelineOrchestrator


class QueueMessageClient:
    """Fake Foundry-compatible client that returns queued model responses."""

    def __init__(self, responses: list[str]) -> None:
        self.Responses = responses
        self.Requests: list[FoundryMessageRequest] = []

    def send_message(self, request: FoundryMessageRequest) -> FoundryMessageResponse:
        """Return the next queued response and record the request."""

        self.Requests.append(request)
        return FoundryMessageResponse(
            text=self.Responses.pop(0),
            raw_response={},
            metadata={"model": "fake"},
        )


class FakeSearchClient:
    """Search client that avoids network calls while exercising retrieval flow."""

    def search(self, query: str, limit: int = 5) -> list[SearchResult]:
        """Return one deterministic search result."""

        return [
            SearchResult(
                source="mock",
                title="Company filing",
                url="https://example.com/filing",
                snippet=query,
                provider="fake",
                rank=1,
                retrievedAt=datetime.now(UTC),
            )
        ][:limit]

    def retrieve(self, url: str) -> SourceEvidence | None:
        """Return deterministic source evidence for the search result."""

        return SourceEvidence(
            source="mock",
            sourceUrl=url,
            retrievedAt=datetime.now(UTC),
            title="Company filing",
            retrievedText="Capex remains elevated.",
            excerpt="Capex remains elevated.",
        )


def test_mocked_agent_pipeline_runs_with_fake_llm_and_search_clients(
    artifact_store,
    sample_scope,
    sample_research_brief,
    sample_thesis_brief,
    sample_draft_issue,
    sample_fact_check_report,
):
    """The full agent path should run with mocked LLM and search clients."""

    FixedDraft = sample_draft_issue.model_copy(update={"Body": "<p>Fixed draft.</p>"})
    MessageClient = QueueMessageClient(
        [
            sample_research_brief.model_dump_json(),
            sample_thesis_brief.model_dump_json(),
            sample_draft_issue.model_dump_json(),
            sample_fact_check_report.model_dump_json(),
            FixedDraft.model_dump_json(),
            sample_fact_check_report.model_dump_json(),
        ]
    )
    Orchestrator = PipelineOrchestrator(
        artifact_store,
        research_stage=ResearchAgent(MessageClient, FakeSearchClient()).run,
        thesis_stage=ThesisAgent(MessageClient).run,
        writer_stage=WriterAgent(MessageClient).run,
        fact_check_stage=FactCheckAgent(MessageClient).run,
        fix_pass_stage=FixPassAgent(MessageClient).run,
        export_stage=lambda Draft: ("", ""),
    )

    RunId = Orchestrator.refine_scope(sample_scope)
    Orchestrator.run_research(RunId)
    Orchestrator.run_thesis(RunId)
    Orchestrator.approve_thesis(RunId)
    Orchestrator.write_draft(RunId)
    Orchestrator.fact_check_draft(RunId)
    Orchestrator.apply_fix_pass(RunId)
    Orchestrator.recheck_draft(RunId)
    Paths = export_run(artifact_store, RunId)

    assert len(MessageClient.Requests) == 6
    assert Paths["html"].exists()
    assert "Fixed draft" in Paths["markdown"].read_text(encoding="utf-8")
