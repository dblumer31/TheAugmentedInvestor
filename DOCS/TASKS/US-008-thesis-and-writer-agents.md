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

- [ ] Thesis output includes central thesis, thesis basis, bull case, base case, bear case, scenario math if any, mispricing view, contrarian test, confidence rationale, and newsletter angle.
- [ ] Thesis output references supporting and opposing evidence from the research brief.
- [ ] Scenario math is labeled as scenario analysis, not prediction.
- [ ] The generated thesis brief is visible to the operator before draft generation.
- [ ] The operator can approve, reject, or restart before draft generation.
- [ ] Draft output includes subject, title, subtitle, lede, body content, sources used, and word count.
- [ ] The draft cites evidence inline and avoids direct investment advice.
- [ ] The draft preserves reader type, horizon, depth, target length, and approved thesis.

---

## Technical Notes

### Implementation Approach

- Add `prompts/thesis.md` and `prompts/writer.md`.
- Use `ThesisBrief` and `DraftIssue` validation from US-005.
- Store approval state through the orchestrator and artifact store.
- Unit tests should prove `write_draft()` fails before approval.

### File Changes

| File | Change |
|------|--------|
| `src/augmented_investor/agents/thesis_agent.py` | Create Thesis Agent. |
| `src/augmented_investor/agents/writer_agent.py` | Create Writer Agent. |
| `src/augmented_investor/prompts/thesis.md` | Create thesis prompt template. |
| `src/augmented_investor/prompts/writer.md` | Create writer prompt template. |
| `src/augmented_investor/pipeline/orchestrator.py` | Wire thesis approval and draft stage. |
| `tests/unit/test_thesis_agent.py` | Add thesis agent tests. |
| `tests/unit/test_writer_agent.py` | Add writer agent tests. |

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

- [ ] Code implemented following `DOCS/AI_GUIDE.md` standards.
- [ ] Acceptance criteria verified.
- [ ] Unit tests cover thesis validation, approval gate, and draft generation with mocked LLM responses.
- [ ] No linter warnings introduced.
- [ ] Story file renamed with ` - DONE` suffix.
- [ ] `DOCS/BACKLOG.md` updated.
