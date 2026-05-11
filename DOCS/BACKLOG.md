# The Augmented Investor - Backlog & Sprint Status

**Last Updated:** 2026-05-11

---

## Status Legend

| Symbol | Meaning |
|--------|---------|
| ✅ | Done |
| 🚧 | In Progress |
| 📋 | Pending |
| 🔴 | Blocked |

---

## Current Sprint: Sprint 1

**Sprint Goal:** Establish the Python foundation and validate Azure AI Foundry before building the full pipeline.  
**Sprint Duration:** TBD

### Sprint 1 Stories

| Story | Title | Points | Status | Notes |
|-------|-------|--------|--------|-------|
| US-002 | Python Project Scaffold And Configuration | 3 | ✅ | Foundation for all later stories |
| US-003 | Azure Foundry Smoke Test | 5 | ✅ | Must happen early to validate endpoint/tool support |
| US-004 | Provider And Search Client Abstractions | 5 | ✅ | Foundry web search abstraction implemented |
| US-005 | Core Models And JSON Validation | 5 | ✅ | Core contracts and JSON validation implemented |

**Sprint Velocity:** 18 / 18 points completed

---

## Sprint 2 (Planned)

**Sprint Goal:** Build the persisted pipeline foundation and generate research, thesis, and draft outputs.

### Sprint 2 Stories

| Story | Title | Points | Status | Notes |
|-------|-------|--------|--------|-------|
| US-006 | Artifact Store And Pipeline Orchestrator | 8 | 📋 | Enforces stage order and run artifacts |
| US-007 | Research And Retrieval Agent | 8 | 📋 | Produces structured evidence and stored source excerpts |
| US-008 | Thesis And Writer Agents | 8 | 📋 | Adds thesis gate and draft generation |

**Planned Points:** 24

---

## Sprint 3 (Planned)

**Sprint Goal:** Add review, repair, re-check, and export behavior.

### Sprint 3 Stories

| Story | Title | Points | Status | Notes |
|-------|-------|--------|--------|-------|
| US-009 | Fact Check And Source Quality Rules | 8 | 📋 | Preserves `citation exists != claim is proven` |
| US-010 | Fix Pass And Re-Check | 5 | 📋 | Repairs flagged issues and re-checks fixed draft |
| US-011 | Minimal UI Or CLI And Issue Export | 8 | 📋 | Replaces browser buttons and clipboard actions |

**Planned Points:** 21

---

## Sprint 4 (Planned)

**Sprint Goal:** Verify the integrated workflow and complete quality reporting.

### Sprint 4 Stories

| Story | Title | Points | Status | Notes |
|-------|-------|--------|--------|-------|
| US-012 | End-To-End Tests And Quality Gates | 5 | 📋 | Adds mocked E2E tests and Radon report |

**Planned Points:** 5

---

## Backlog (Unprioritized)

| Story | Title | Points | Priority | Notes |
|-------|-------|--------|----------|-------|
| TBD | Targeted Research Addendum | TBD | Medium | Future enhancement after base flow is stable |
| TBD | Database-Backed Issue History | TBD | Low | Out of scope for first implementation |
| TBD | Automated Newsletter Publishing | TBD | Low | Out of scope for first implementation |

---

## Completed Sprints

### Sprint 0 - Project Setup

| Story | Title | Points | Status |
|-------|-------|--------|--------|
| - | Project documentation created | - | ✅ |
| - | Development environment setup | - | ✅ |

### Completed Stories

| Story | Title | Points | Completed |
|-------|-------|--------|-----------|
| US-002 | Python Project Scaffold And Configuration | 3 | 2026-05-11 |
| US-003 | Azure Foundry Smoke Test | 5 | 2026-05-11 |
| US-004 | Provider And Search Client Abstractions | 5 | 2026-05-11 |
| US-005 | Core Models And JSON Validation | 5 | 2026-05-11 |

---

## Blockers & Risks

| ID | Description | Impact | Mitigation | Status |
|----|-------------|--------|------------|--------|
| RISK-001 | Azure AI Foundry Claude may not support Anthropic web search tools. | Research implementation may require external search provider. | US-003 confirmed tool support and US-004 added `FoundryToolSearchClient`. | Mitigated |
| RISK-002 | Foundry endpoint path/header/deployment shape may differ from public Anthropic API. | Provider calls may fail if assumptions are wrong. | Endpoint construction centralized and live verification is available through US-003 smoke test. | Mitigated |
| RISK-003 | Source verification is weak without retrieved evidence. | Fact-check may over-trust model summaries. | Store source excerpts in US-007 and triage claims in US-009. | Open |

---

## Sprint Metrics

| Sprint | Planned Points | Completed | Velocity |
|--------|----------------|-----------|----------|
| Sprint 0 | N/A | N/A | N/A |
| Sprint 1 | 18 | 18 | 100% |
| Sprint 2 | 24 | 0 | 0% |
| Sprint 3 | 21 | 0 | 0% |
| Sprint 4 | 5 | 0 | 0% |

---

## Notes

- Generated implementation stories start at US-002 because `DOCS/TASKS/US-001-example-story.md` already exists as the template story.
- The Foundry smoke test is intentionally early to reduce provider-integration risk before full pipeline implementation.
