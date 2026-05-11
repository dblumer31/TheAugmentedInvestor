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

- [ ] Research output includes market snapshot, prior trend, what changed, evidence for, evidence against, possible mispricing, source list, and recommended angle.
- [ ] Claims include source, date, confidence, instrument precision, and source-quality metadata.
- [ ] Claims indicate whether cited evidence directly supports the exact claim.
- [ ] Claims indicate whether exact quoted evidence is available.
- [ ] `01_research.json` stores retrieved evidence when a retrieval provider returns it.
- [ ] The Research Agent can operate with Foundry tool support if available.
- [ ] The Research Agent can operate with a separate provider abstraction.
- [ ] The chosen provider and evidence source are recorded in the research artifact.

---

## Technical Notes

### Implementation Approach

- Add `prompts/research.md` for the research contract.
- Inject `FoundryClient` and search client interfaces into `ResearchAgent`.
- Call `search()` and `retrieve()` before prompting when a provider is configured.
- Use the JSON parser and `ResearchBrief` validation from US-005.

### File Changes

| File | Change |
|------|--------|
| `src/augmented_investor/agents/research_agent.py` | Create Research Agent. |
| `src/augmented_investor/prompts/research.md` | Create research prompt template. |
| `src/augmented_investor/pipeline/orchestrator.py` | Wire `run_research()`. |
| `tests/unit/test_research_agent.py` | Add mocked LLM/search tests. |

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

- [ ] Code implemented following `DOCS/AI_GUIDE.md` standards.
- [ ] Acceptance criteria verified.
- [ ] Unit tests cover research with and without retrieved evidence.
- [ ] No linter warnings introduced.
- [ ] Story file renamed with ` - DONE` suffix.
- [ ] `DOCS/BACKLOG.md` updated.
