# US-007: Research And Retrieval Agent

**Story Type:** Feature  
**Priority:** High  
**Sprint:** 2  
**Story Points:** 8

---

## User Story

**As an** editor,  
**I want** the Research Agent to produce structured evidence with source metadata,  
**So that** later thesis and fact-check stages are grounded in inspectable research.

---

## Description

Implement the Research Agent and prompt template. The agent should accept a validated
`ScopeRequest`, consume retrieved source evidence when available, and produce a
`ResearchBrief` rather than prose. Search/retrieval must remain provider-agnostic.

---

## Acceptance Criteria

- [x] Research output includes market snapshot, prior trend, what changed, evidence for, evidence against, possible mispricing, source list, and recommended angle.
- [x] Claims include source, date, confidence, instrument precision, and source-quality metadata.
- [x] Claims indicate whether cited evidence directly supports the exact claim.
- [x] Claims indicate whether exact quoted evidence is available.
- [x] `01_research.json` stores retrieved evidence when a retrieval provider returns it.
- [x] The Research Agent can operate with Foundry tool support if available.
- [x] The Research Agent can operate with a separate provider abstraction.
- [x] The chosen provider and evidence source are recorded in the research artifact.
- [x] Retrieved evidence included in prompts and artifacts is bounded to avoid unbounded source text.
- [x] Invalid research JSON or schema failures perform one controlled retry using bounded validation context from the JSON parser.

---

## Technical Notes

### Implementation Approach

- Add `prompts/research.md` for the research contract.
- Inject `FoundryClient` and search client interfaces into `ResearchAgent`.
- Call `search()` and `retrieve()` before prompting when a provider is configured.
- Use the JSON parser and `ResearchBrief` validation from US-005.
- Do not introduce direct provider calls in unit tests; use fake message/search clients.
- US-006 already made `run_research()` injectable, so this story should not require new orchestrator behavior unless integration tests expose a mismatch.

### File Changes

| File | Change |
|------|--------|
| `src/augmented_investor/agents/research_agent.py` | Create Research Agent. |
| `src/augmented_investor/prompts/research.md` | Create research prompt template. |
| `src/augmented_investor/pipeline/orchestrator.py` | Reuse existing injectable `run_research()` boundary from US-006. |
| `tests/unit/test_research_agent.py` | Add mocked LLM/search tests. |

### Implementation Summary

- Added `ResearchAgent` with injected message and search/retrieval clients.
- Added `prompts/research.md` with the structured research JSON contract.
- Added bounded retrieved evidence handling before prompt construction and artifact merge.
- Added one controlled retry using the US-005 JSON parser validation context.
- Added `instrumentPrecision` support to research claim and evidence-point models.
- Verified with fake message/search clients, full pytest, Radon CC, Radon MI, and linter diagnostics.

---

## Dependencies

- US-004 (Provider and search client abstractions)
- US-005 (Core models and JSON validation)
- US-006 (Artifact store and pipeline orchestrator)

---

## Spec References

- FR-2.3.1: Produce Structured Research Briefs
- FR-2.3.2: Store Retrieved Evidence
- FR-2.3.3: Abstract Search Provider

---

## Assumptions

- The first implementation can use mocked or no-op retrieval if no external provider has been approved.
- Source excerpts may be truncated to a safe, useful length for artifacts and prompts.

---

## Out of Scope

- Paid external search provider selection.
- Market data vendor integration.
- Thesis or draft generation.

---

## Definition of Done

- [x] Code implemented following `DOCS/AI_GUIDE.md` standards.
- [x] Acceptance criteria verified.
- [x] Unit tests cover research with and without retrieved evidence.
- [x] No linter warnings introduced.
- [x] Radon CC check: all production functions grade A (CC <= 10), or any exception is documented.
- [x] Radon MI check: all production files grade A (MI >= 20).
- [x] Story file renamed with ` - DONE` suffix.
- [x] `DOCS/BACKLOG.md` updated.
