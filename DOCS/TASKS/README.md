# The Augmented Investor - User Stories

This folder contains user stories for the Python rewrite of The Augmented Investor.

---

## Story Status Legend

| Status | Meaning |
|--------|---------|
| Pending | Story file exists, not started |
| In Progress | Currently being implemented |
| Done | File renamed with " - DONE" suffix |

---

## Sprint 1: Foundation And Provider Validation

| Story | Title | Type | Points | Status | Dependencies |
|-------|-------|------|--------|--------|--------------|
| [US-002](./US-002-python-project-scaffold%20-%20DONE.md) | Python Project Scaffold And Configuration | Infrastructure | 3 | Done | None |
| [US-003](./US-003-foundry-smoke-test%20-%20DONE.md) | Azure Foundry Smoke Test | Infrastructure | 5 | Done | US-002 |
| [US-004](./US-004-provider-and-search-clients%20-%20DONE.md) | Provider And Search Client Abstractions | Infrastructure | 5 | Done | US-002, US-003 |
| [US-005](./US-005-core-models-and-json-validation%20-%20DONE.md) | Core Models And JSON Validation | Infrastructure | 5 | Done | US-002, US-004 |

---

## Sprint 2: Core Pipeline And Draft Generation

| Story | Title | Type | Points | Status | Dependencies |
|-------|-------|------|--------|--------|--------------|
| [US-006](./US-006-artifact-store-and-orchestrator.md) | Artifact Store And Pipeline Orchestrator | Feature | 8 | Pending | US-005 |
| [US-007](./US-007-research-and-retrieval-agent.md) | Research And Retrieval Agent | Feature | 8 | Pending | US-004, US-005, US-006 |
| [US-008](./US-008-thesis-and-writer-agents.md) | Thesis And Writer Agents | Feature | 8 | Pending | US-006, US-007 |

---

## Sprint 3: Review, Repair, And Export

| Story | Title | Type | Points | Status | Dependencies |
|-------|-------|------|--------|--------|--------------|
| [US-009](./US-009-fact-check-source-quality.md) | Fact Check And Source Quality Rules | Feature | 8 | Pending | US-007, US-008 |
| [US-010](./US-010-fix-pass-and-recheck.md) | Fix Pass And Re-Check | Feature | 5 | Pending | US-009 |
| [US-011](./US-011-ui-cli-and-export.md) | Minimal UI Or CLI And Issue Export | Feature | 8 | Pending | US-006, US-010 |

---

## Sprint 4: Verification And Quality

| Story | Title | Type | Points | Status | Dependencies |
|-------|-------|------|--------|--------|--------------|
| [US-012](./US-012-end-to-end-tests-and-quality.md) | End-To-End Tests And Quality Gates | Testing | 5 | Pending | US-002 through US-011 |

---

## Dependency Graph

```text
Sprint 1:
  US-002 Scaffold
    ├── US-003 Foundry Smoke Test
    │     └── US-004 Provider And Search Clients
    └── US-005 Core Models And JSON Validation

Sprint 2:
  US-005 ───────────────▶ US-006 Artifact Store And Orchestrator
  US-004 + US-005 + US-006 ─▶ US-007 Research And Retrieval
  US-006 + US-007 ───────▶ US-008 Thesis And Writer

Sprint 3:
  US-007 + US-008 ───────▶ US-009 Fact Check
  US-009 ────────────────▶ US-010 Fix Pass And Re-Check
  US-006 + US-010 ───────▶ US-011 UI Or CLI And Export

Sprint 4:
  US-002 through US-011 ─▶ US-012 End-To-End Tests And Quality
```

---

## Story Types

| Type | Description |
|------|-------------|
| Database Schema | Creating tables, indexes, constraints |
| Infrastructure | Configuration, utilities, setup |
| Feature | Business functionality |
| Testing | Test implementation |
| Documentation | Docs, guides, runbooks |

---

## Creating New Stories

1. Copy `US-001-example-story.md` as a template
2. Rename to `US-XXX-descriptive-name.md`
3. Fill in all sections
4. Add to the appropriate sprint table above
5. Update dependencies if needed

---

## Completing Stories

1. Verify all acceptance criteria are met
2. Ensure tests pass
3. Rename file to `US-XXX-name - DONE.md`
4. Update status in this README
5. Update `BACKLOG.md`
