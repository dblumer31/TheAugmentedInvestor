# US-013: FastAPI Operator GUI

**Story Type:** Feature  
**Priority:** High  
**Sprint:** 5  
**Story Points:** 8

---

## User Story

**As an** editor,  
**I want** a local web interface for running and reviewing the pipeline,  
**So that** I can use the Python rewrite with buttons and review panels instead of CLI commands.

---

## Description

Add a thin FastAPI operator GUI over the existing artifact-backed pipeline. The GUI should
reuse the same `ArtifactStore`, `PipelineOrchestrator`, `operator_interface`, and exporter
helpers that the CLI uses. It must not duplicate stage logic or introduce a second state
model.

---

## Acceptance Criteria

- [ ] A local FastAPI app starts from the project root with documented command-line instructions.
- [ ] The home page provides a scope-entry form and creates a persisted run.
- [ ] The run page displays run status, completed artifacts, current draft, source list, thesis state, fact-check state, and export links.
- [ ] The run page exposes actions for research, thesis generation, thesis approval/rejection, draft generation, fact-check, fix pass, re-check, and export.
- [ ] Stage actions call existing orchestrator/operator-interface helpers and persist the same artifacts as the CLI.
- [ ] Provider failures are shown with redacted diagnostics only.
- [ ] Export links provide access to `issue.html` and `issue.md` without browser clipboard access.
- [ ] Existing CLI behavior remains intact.

---

## Technical Notes

### Implementation Approach

- Use FastAPI with simple server-rendered HTML or minimal JSON endpoints plus static HTML.
- Keep the GUI local/development-only; authentication is out of scope.
- Use redirects back to the run page after each stage action.
- Keep templates small and readable. Avoid adding a front-end framework in this story.
- Reuse the existing styled HTML export for final issue display where practical.

### File Changes

| File | Change |
|------|--------|
| `src/augmented_investor/app.py` | Implement FastAPI app, routes, and form handlers. |
| `src/augmented_investor/operator_interface.py` | Add any missing GUI-friendly helper functions if needed. |
| `tests/unit/` | Add tests for route/helper behavior that can run without live providers. |
| `tests/integration/` | Add mocked GUI flow tests if practical. |
| `README.md` | Document how to start and use the local GUI. |

---

## Dependencies

- US-006 (Artifact store and pipeline orchestrator)
- US-011 (CLI and export interface)
- US-012 (Final test and quality gate)

---

## Spec References

- FR-2.1.1: Preserve Editorial Stage Order
- FR-2.1.2: Persist Every Stage Output
- FR-2.9.1: Replace Browser-Only Interactions
- FR-2.9.2: Add FastAPI Operator GUI
- FR-2.9.3: Export Final Issue

---

## Assumptions

- The GUI is a local operator interface, not a production multi-user web app.
- The GUI uses the current live provider configuration path and does not manage secrets.
- CLI remains supported for debugging and scripted runs.

---

## Out of Scope

- User authentication and authorization.
- Database-backed run history.
- Deployment hosting.
- Rich front-end framework or custom design system.
- Automated newsletter publishing.

---

## Definition of Done

- [ ] GUI routes/pages implemented following `DOCS/AI_GUIDE.md` standards.
- [ ] Acceptance criteria verified.
- [ ] Tests pass without live provider credentials.
- [ ] Manual GUI verification is documented.
- [ ] No linter warnings introduced.
- [ ] Radon CC/MI checked for changed production files.
- [ ] README updated with GUI start/use instructions.
- [ ] Story file renamed with ` - DONE` suffix.
- [ ] `DOCS/BACKLOG.md` and `DOCS/TASKS/README.md` updated.
