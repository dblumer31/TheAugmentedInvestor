# Design Decisions Log

This document records significant architectural and design decisions for The Augmented Investor.

---

## Decision Template

```markdown
## DEC-XXX: [Decision Title]

**Date:** [YYYY-MM-DD]  
**Status:** Proposed | Accepted | Deprecated | Superseded by DEC-YYY

### Context

[What is the issue that we're seeing that is motivating this decision or change?]

### Decision

[What is the change that we're proposing and/or doing?]

### Rationale

[Why is this the best choice? What alternatives were considered?]

### Consequences

[What becomes easier or more difficult to do because of this change?]
```

---

## Decisions

### DEC-001: Python as Primary Implementation Language

**Date:** 2026-05-11  
**Status:** Accepted

#### Context

The HTML prototype proved the editorial workflow but kept provider calls, state, and UI behavior in a single browser file. The rewrite needs explicit state, testable agent modules, stronger JSON validation, and local run artifacts.

#### Decision

Use Python as the primary implementation language for the rewrite.

#### Rationale

- Python supports fast agent experimentation and straightforward CLI tooling.
- Pydantic gives explicit contracts for the workflow's JSON artifacts.
- `pytest`, `httpx`, and Radon provide the testing, provider, and quality tooling needed for this phase.
- The implementation can still expose a FastAPI UI later without rewriting the core pipeline.

**Alternatives Considered:**
- Continue with single-file HTML: rejected because browser state, direct provider calls, and clipboard-driven review do not support durable runs or test coverage.
- C# / ASP.NET Core: viable for a later durable app, but slower for the initial agent workflow migration.

#### Consequences

**Positive:**
- Agent stages are testable with fake providers.
- Run state can be persisted as local artifacts.
- Provider integration and JSON parsing can be isolated from UI concerns.

**Negative:**
- A future production web app may need additional packaging, hosting, authentication, and HTML sanitization work.

---

### DEC-002: Azure AI Foundry as Primary Model Provider

**Date:** 2026-05-11  
**Status:** Accepted

#### Context

The rewrite needs to call Claude deployments through Azure AI Foundry and validate the exact endpoint/header/tool behavior before depending on live model calls.

#### Decision

Use Azure AI Foundry as the primary model provider, with a centralized `FoundryClient` that handles Anthropic Messages endpoint construction, headers, model roles, timeouts, smoke tests, and safe diagnostics.

#### Rationale

- The user's working credentials and endpoint are for Azure AI Foundry.
- A smoke-test command verified the Anthropic Messages API shape and web-search tool acceptance.
- Centralizing provider behavior prevents each agent from duplicating request and redaction logic.

#### Consequences

- Live provider tests remain opt-in because they require credentials and network access.
- Certificate trust and corporate proxy setup are local runtime concerns.
- If Foundry behavior changes, the integration point is isolated in one client.

---

### DEC-003: Local JSON Run Artifacts Before Database Storage

**Date:** 2026-05-11  
**Status:** Accepted

#### Context

The prototype stored workflow state in browser variables. The rewrite needs replayable state, auditability, and a simple persistence mechanism before deciding whether a database is needed.

#### Decision

Persist every run under `runs/{run_id}/` as JSON and text artifacts, including scope, research, thesis, draft, fact-check, fixed draft, re-check, `issue.html`, and `issue.md`.

#### Rationale

- Local files are transparent and easy to inspect during the rewrite.
- JSON artifacts match the agent contract boundaries.
- The approach avoids premature database design while preserving a clear migration path.

#### Consequences

- Multi-user history, authorization, and queryable run search remain future work.
- Run folders should not contain secrets and should generally stay out of source control.
- The artifact contract becomes the shared boundary for CLI, future FastAPI routes, exporters, and tests.

---

### DEC-004: CLI First, FastAPI GUI Next

**Date:** 2026-05-11  
**Status:** Accepted

#### Context

The original browser prototype had buttons and clipboard actions. The Python rewrite needed a first operator interface quickly, while the core pipeline and provider issues were still being stabilized.

#### Decision

Implement the first operator interface as CLI commands over the artifact-backed pipeline. Defer the interactive FastAPI GUI to a follow-up story that reuses the same orchestrator and operator-interface helpers.

#### Rationale

- CLI commands were the fastest path to a working vertical slice.
- The CLI exposed the required workflow actions without blocking on web templates or front-end polish.
- Keeping UI thin preserves the pipeline as the source of truth and makes the future GUI additive.

#### Consequences

- Operators can run the full workflow now, but must use commands rather than page buttons.
- The next interface story should add FastAPI pages/routes for scope entry, stage buttons, thesis approval, review, and export links.
- The GUI must not duplicate workflow logic; it should call the same artifact store, orchestrator, and exporter helpers.

---

## Decision Index

| ID | Title | Status | Date |
|----|-------|--------|------|
| DEC-001 | Python as Primary Implementation Language | Accepted | 2026-05-11 |
| DEC-002 | Azure AI Foundry as Primary Model Provider | Accepted | 2026-05-11 |
| DEC-003 | Local JSON Run Artifacts Before Database Storage | Accepted | 2026-05-11 |
| DEC-004 | CLI First, FastAPI GUI Next | Accepted | 2026-05-11 |
