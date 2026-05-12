# US-011: Minimal UI Or CLI And Issue Export

**Story Type:** Feature  
**Priority:** High  
**Sprint:** 3  
**Story Points:** 8

---

## User Story

**As an** editor,  
**I want** a minimal interface to run, review, approve, repair, and export an issue,  
**So that** the Python rewrite replaces the browser prototype's buttons and clipboard behavior.

---

## Description

Implement the first operator interface as a CLI vertical slice. The interface must expose
scope entry, thesis approval, stage execution, review status, and export actions. Export
replaces browser clipboard actions with files.

---

## Acceptance Criteria

- [x] In-memory JS variables from the prototype are represented by persisted artifacts.
- [x] Thesis approval, apply fixes, export HTML, and export text/Markdown are exposed as FastAPI routes, UI form actions, or CLI commands.
- [x] Review state is represented by persisted run status.
- [x] Clipboard actions become export files.
- [x] The system exports `issue.html`.
- [x] The system exports `issue.md`.
- [x] Review output includes current draft, source list, fact-check state, and export options.
- [x] Export does not require browser clipboard access.
- [x] CLI commands include scope creation, thesis approval/rejection, stage execution, review, fix pass, re-check, and export.
- [x] Export command writes from the current fixed draft when available and otherwise from the current draft.

---

## Technical Notes

### Implementation Approach

- Use CLI for the first implementation; FastAPI remains out of scope for this story.
- Keep CLI thin; call orchestrator/operator-interface functions rather than duplicating workflow logic.
- Implement `markdown_exporter.py` and `html_exporter.py`.
- Manual CLI verification is acceptable when documented per `DOCS/AI_GUIDE.md`.
- Live stage execution commands may require Foundry configuration; unit/integration tests should use mocked or pre-populated artifacts.

### File Changes

| File | Change |
|------|--------|
| `src/augmented_investor/cli.py` | Create CLI commands. |
| `src/augmented_investor/operator_interface.py` | Add thin operator helpers for review/export. |
| `src/augmented_investor/exporters/markdown_exporter.py` | Create Markdown exporter. |
| `src/augmented_investor/exporters/html_exporter.py` | Create HTML exporter. |
| `tests/unit/test_exporters.py` | Add exporter tests. |
| `tests/unit/test_operator_interface.py` | Add review/export helper tests. |
| `tests/integration/test_mock_pipeline_flow.py` | Add mocked end-to-end interface flow. |

---

## Dependencies

- US-006 (Artifact store and pipeline orchestrator)
- US-010 (Fix pass and re-check)

---

## Spec References

- FR-2.1.1: Preserve Editorial Stage Order
- FR-2.1.3: Support Human Thesis Approval
- FR-2.9.1: Replace Browser-Only Interactions
- FR-2.9.2: Export Final Issue

---

## Assumptions

- The first implementation uses CLI, but the interface must preserve the stage behavior in `DOCS/SPEC.md`.
- Markdown export is sufficient for text export in the first slice.

---

## Out of Scope

- User authentication.
- Multi-user issue history.
- Automated newsletter publishing.

---

## Definition of Done

- [x] Code implemented following `DOCS/AI_GUIDE.md` standards.
- [x] Acceptance criteria verified.
- [x] Exporter tests pass.
- [x] Manual UI/CLI verification is documented if applicable.
- [x] No linter warnings introduced.
- [x] Radon CC check: all production functions grade A (CC <= 10), or any exception is documented.
- [x] Radon MI check: all production files grade A (MI >= 20).
- [x] Story file renamed with ` - DONE` suffix.
- [x] `DOCS/BACKLOG.md` updated.

---

## Implementation Summary

- Added CLI commands for scope creation, live stage execution, thesis approval/rejection, review output, fix pass, re-check, and export.
- Added artifact-backed review/export helpers that report current draft, source list, fact-check state, persisted run status, and export options.
- Added Markdown and HTML exporters that write `issue.md` and `issue.html` without browser clipboard access.
- Added unit tests for exporters, operator-interface helpers, and CLI artifact commands plus a mocked integration flow.
- Verification: `python -m pytest` passed with 82 passed and 1 skipped; linter diagnostics reported no errors; Radon CC and MI checks passed with A grades for new production files.
