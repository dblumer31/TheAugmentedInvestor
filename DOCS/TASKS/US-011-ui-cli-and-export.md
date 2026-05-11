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

Implement the first operator interface as either FastAPI routes with simple pages or a CLI
if that produces a faster vertical slice. The interface must expose scope entry, thesis
approval, stage execution, review status, and export actions. Export replaces browser
clipboard actions with files.

---

## Acceptance Criteria

- [ ] In-memory JS variables from the prototype are represented by persisted artifacts.
- [ ] Thesis approval, apply fixes, export HTML, and export text/Markdown are exposed as FastAPI routes, UI form actions, or CLI commands.
- [ ] Review state is represented by persisted run status.
- [ ] Clipboard actions become export files.
- [ ] The system exports `issue.html`.
- [ ] The system exports `issue.md`.
- [ ] Review output includes current draft, source list, fact-check state, and export options.
- [ ] Export does not require browser clipboard access.

---

## Technical Notes

### Implementation Approach

- Use the route shape in `DOCS/DESIGN.md` Section 6.4 if FastAPI is selected.
- Keep UI thin; call orchestrator functions rather than duplicating workflow logic.
- Implement `markdown_exporter.py` and `html_exporter.py`.
- Manual testing is acceptable for UI behavior when documented per `DOCS/AI_GUIDE.md`.

### File Changes

| File | Change |
|------|--------|
| `src/augmented_investor/app.py` | Create FastAPI route handlers if web UI is selected. |
| `src/augmented_investor/cli.py` | Create CLI commands if CLI is selected. |
| `src/augmented_investor/exporters/markdown_exporter.py` | Create Markdown exporter. |
| `src/augmented_investor/exporters/html_exporter.py` | Create HTML exporter. |
| `tests/unit/test_exporters.py` | Add exporter tests. |
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

- The first implementation may use either FastAPI or CLI, but the interface must preserve the stage behavior in `DOCS/SPEC.md`.
- Markdown export is sufficient for text export in the first slice.

---

## Out of Scope

- User authentication.
- Multi-user issue history.
- Automated newsletter publishing.

---

## Definition of Done

- [ ] Code implemented following `DOCS/AI_GUIDE.md` standards.
- [ ] Acceptance criteria verified.
- [ ] Exporter tests pass.
- [ ] Manual UI/CLI verification is documented if applicable.
- [ ] No linter warnings introduced.
- [ ] Story file renamed with ` - DONE` suffix.
- [ ] `DOCS/BACKLOG.md` updated.
