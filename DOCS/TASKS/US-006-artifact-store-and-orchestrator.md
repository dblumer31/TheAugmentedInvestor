# US-006: Artifact Store And Pipeline Orchestrator

**Story Type:** Feature  
**Priority:** Critical  
**Sprint:** 2  
**Story Points:** 8

---

## User Story

**As an** editor,  
**I want** each pipeline stage to run in order and save its output,  
**So that** every issue has an inspectable reasoning trail.

---

## Description

Implement the local artifact store and pipeline orchestrator that preserve the prototype
workflow while replacing browser-only state with persisted run files. The orchestrator
should enforce stage order, thesis approval, and artifact writes between stages.

---

## Acceptance Criteria

- [ ] Each run gets a unique `run_id`.
- [ ] Each completed stage writes a structured artifact under `runs/{run_id}/`.
- [ ] Minimum artifacts include `00_scope.json`, `01_research.json`, `02_thesis.json`, `03_draft.json`, `04_fact_check.json`, `05_fixed_draft.json`, and `06_recheck.json`.
- [ ] The orchestrator exposes `refine_scope()`, `run_research()`, `run_thesis()`, `approve_thesis()`, `write_draft()`, `fact_check_draft()`, `apply_fix_pass()`, `recheck_draft()`, and `export_issue()` boundaries.
- [ ] Writer cannot run until the thesis is approved.
- [ ] Re-Check runs against the fixed draft, not the original draft.
- [ ] A failed stage does not delete earlier artifacts.

---

## Technical Notes

### Implementation Approach

- Implement `ArtifactStore` with atomic-ish JSON writes where practical.
- Use `tmp_path` for file-system unit tests.
- Keep orchestrator provider dependencies injectable so tests can use mocked agents.
- Persist approval status as run state rather than in memory.

### File Changes

| File | Change |
|------|--------|
| `src/augmented_investor/pipeline/artifact_store.py` | Create run artifact persistence. |
| `src/augmented_investor/pipeline/orchestrator.py` | Create stage orchestration and state transitions. |
| `tests/unit/test_artifact_store.py` | Add artifact persistence tests. |
| `tests/unit/test_orchestrator.py` | Add stage order and approval gate tests. |

---

## Dependencies

- US-005 (Core models and JSON validation)

---

## Spec References

- FR-2.1.1: Preserve Editorial Stage Order
- FR-2.1.2: Persist Every Stage Output
- FR-2.1.3: Support Human Thesis Approval

---

## Assumptions

- JSON files are the system of record until a database is explicitly introduced.
- A simple UUID or timestamp-based run id is sufficient for the first implementation.

---

## Out of Scope

- Real agent prompting.
- UI route handlers.
- Database-backed issue history.

---

## Definition of Done

- [ ] Code implemented following `DOCS/AI_GUIDE.md` standards.
- [ ] Acceptance criteria verified.
- [ ] Unit tests cover stage ordering, failed stages, and persisted artifacts.
- [ ] No linter warnings introduced.
- [ ] Story file renamed with ` - DONE` suffix.
- [ ] `DOCS/BACKLOG.md` updated.
