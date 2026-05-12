# US-008: Thesis And Writer Agents

**Story Type:** Feature  
**Priority:** High  
**Sprint:** 2  
**Story Points:** 8

---

## User Story

**As an** editor,  
**I want** the system to generate an approvable thesis and then draft from that thesis,  
**So that** the article follows a deliberate editorial argument rather than a loose summary.

---

## Description

Implement the Thesis Agent, human thesis approval wiring, and Writer Agent. The Writer
Agent must not run until the thesis is approved. The generated draft must preserve the
approved thesis, cite research evidence, avoid direct investment advice, label scenario
estimates, and end with an investable question.

---

## Acceptance Criteria

- [x] Thesis output includes central thesis, thesis basis, bull case, base case, bear case, scenario math if any, mispricing view, contrarian test, confidence rationale, and newsletter angle.
- [x] Thesis output references supporting and opposing evidence from the research brief.
- [x] Scenario math is labeled as scenario analysis, not prediction.
- [x] The generated thesis brief is visible to the operator before draft generation.
- [x] The operator can approve, reject, or restart before draft generation, with approval/rejection persisted in run state.
- [x] Draft output includes subject, title, subtitle, lede, body content, sources used, and word count.
- [x] The draft cites evidence inline and avoids direct investment advice.
- [x] The draft preserves reader type, horizon, depth, target length, and approved thesis.
- [x] Invalid thesis or draft JSON performs one controlled retry using bounded validation context from the JSON parser.

---

## Technical Notes

### Implementation Approach

- Add `prompts/thesis.md` and `prompts/writer.md`.
- Use `ThesisBrief` and `DraftIssue` validation from US-005.
- Store approval state through the orchestrator and artifact store.
- Unit tests should prove `write_draft()` fails before approval.
- Do not introduce direct provider calls in unit tests; use fake message clients.
- `restart` should be represented as a new run created from a supplied `ScopeRequest`, while the original run remains unapproved/rejected for auditability.
- The orchestrator should pass the persisted `ScopeRequest` into the writer stage so the draft can preserve reader type, horizon, depth, and target length.

### File Changes

| File | Change |
|------|--------|
| `src/augmented_investor/agents/thesis_agent.py` | Create Thesis Agent. |
| `src/augmented_investor/agents/writer_agent.py` | Create Writer Agent. |
| `src/augmented_investor/prompts/thesis.md` | Create thesis prompt template. |
| `src/augmented_investor/prompts/writer.md` | Create writer prompt template. |
| `src/augmented_investor/pipeline/orchestrator.py` | Add rejection/restart helpers while reusing existing approval and draft gate. |
| `src/augmented_investor/pipeline/artifact_store.py` | Persist thesis rejection metadata in run state. |
| `tests/unit/test_thesis_agent.py` | Add thesis agent tests. |
| `tests/unit/test_writer_agent.py` | Add writer agent tests. |

### Implementation Summary

- Added `ThesisAgent` and `WriterAgent` with structured JSON prompts and one controlled validation retry.
- Added `prompts/thesis.md` and `prompts/writer.md`.
- Updated the orchestrator so the writer receives the persisted `ScopeRequest`.
- Added thesis rejection and restart support while preserving original run audit state.
- Added unit tests for thesis validation, writer prompt context, approval gate, rejection, restart, and mocked LLM responses.
- Verified `python -m pytest`, Radon CC, Radon MI, and linter diagnostics.

---

## Dependencies

- US-006 (Artifact store and pipeline orchestrator)
- US-007 (Research and retrieval agent)

---

## Spec References

- FR-2.1.3: Support Human Thesis Approval
- FR-2.4.1: Produce Thesis Briefs From Research
- FR-2.5.1: Generate Newsletter Drafts
- FR-2.5.2: Preserve Editorial Voice And Structure

---

## Assumptions

- The first UI for thesis approval may be CLI-based if that enables a faster vertical slice.
- Newsletter voice is encoded in the writer prompt until a richer style system is needed.

---

## Out of Scope

- Fact-check and fix-pass behavior.
- Final export UI.
- Automated publishing.

---

## Definition of Done

- [x] Code implemented following `DOCS/AI_GUIDE.md` standards.
- [x] Acceptance criteria verified.
- [x] Unit tests cover thesis validation, approval gate, and draft generation with mocked LLM responses.
- [x] No linter warnings introduced.
- [x] Radon CC check: all production functions grade A (CC <= 10), or any exception is documented.
- [x] Radon MI check: all production files grade A (MI >= 20).
- [x] Story file renamed with ` - DONE` suffix.
- [x] `DOCS/BACKLOG.md` updated.
