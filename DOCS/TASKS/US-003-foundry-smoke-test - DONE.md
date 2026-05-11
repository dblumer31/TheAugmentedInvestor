# US-003: Azure Foundry Smoke Test

**Story Type:** Infrastructure  
**Priority:** Critical  
**Sprint:** 1  
**Story Points:** 5

---

## User Story

**As a** developer,  
**I want** a minimal Azure AI Foundry smoke test,  
**So that** endpoint shape, headers, deployment IDs, and tool support are verified before building the full pipeline.

---

## Description

Build an opt-in CLI smoke test command and supporting function that sends a tiny prompt to the configured
Foundry endpoint and records safe diagnostics. This story must happen early because the
Python rewrite depends on knowing whether the user's Foundry Anthropic deployment supports
the expected Messages API shape and web-search/tool behavior.

---

## Acceptance Criteria

- [x] Smoke test sends a tiny prompt to the configured Foundry endpoint.
- [x] Smoke test verifies endpoint path construction, headers, deployment/model identifier usage, Anthropic Messages request body shape, and response parsing.
- [x] Smoke test confirms whether Foundry supports Anthropic-style tools such as `web_search_20250305`.
- [x] Smoke test writes safe request/response metadata without secrets.
- [x] Endpoint path construction is centralized and easy to adjust.
- [x] Live smoke test is opt-in and skipped by default in normal unit test runs.
- [x] CLI exposes a smoke-test command that can be run intentionally by the operator.
- [x] Live integration test and CLI live execution are gated by `RUN_LIVE_FOUNDRY_TESTS=1`.
- [x] Secret redaction is verified for `x-api-key`, `Authorization`, and any API-key-like values in logs, exceptions, and metadata.
- [x] Smoke test result includes endpoint shape, HTTP status, model/deployment alias, tool-support result, elapsed time, and redacted request summary.

---

## Technical Notes

### Implementation Approach

- Implement `FoundryClient.smoke_test(includeToolProbe: bool = True)`.
- Expose a CLI command, such as `python -m augmented_investor.cli foundry-smoke-test`, that calls the smoke test only when live testing is explicitly enabled.
- Accept either a base endpoint or full `/anthropic/v1/messages` endpoint and normalize internally.
- Redact API keys, authorization headers, and any secret-like values from diagnostics.
- Implement a `_redact_headers(headers: dict) -> dict` helper or equivalent redaction boundary and test it directly.
- Use mocked HTTP responses for unit tests and an explicit integration marker for live tests.
- Skip live integration tests by default with `RUN_LIVE_FOUNDRY_TESTS=1` as the opt-in flag.
- Return safe diagnostics as a structured result object. Do not write files unless a path is explicitly configured by the caller.
- If `httpx.AsyncClient` is used, reuse a client rather than creating one per request, and expose shutdown/close behavior.

### File Changes

| File | Change |
|------|--------|
| `src/augmented_investor/foundry_client.py` | Create smoke test client behavior. |
| `src/augmented_investor/cli.py` | Add operator-facing Foundry smoke test command. |
| `src/augmented_investor/config.py` | Add endpoint normalization support if not already present. |
| `tests/unit/test_foundry_smoke_test.py` | Add mocked smoke test coverage. |
| `tests/unit/test_secret_redaction.py` | Add redaction tests for headers, errors, and metadata. |
| `tests/integration/test_foundry_smoke_test.py` | Add opt-in live smoke test. |
| `example.env` | Document `RUN_LIVE_FOUNDRY_TESTS=0` as the default live-test gate. |

---

## Dependencies

- US-002 (Python project scaffold and configuration)

---

## Spec References

- FR-2.8.2: Smoke-Test Foundry Before Full Pipeline Use
- FR-2.8.3: Support Role-Based Model Selection

---

## Assumptions

- The smoke test may discover that Foundry does not support `web_search_20250305`; that result should guide later search-provider implementation.
- The first live request should be intentionally tiny to limit cost and blast radius.
- The CLI command is for explicit operator use, not for automatic execution during normal test runs.

---

## Out of Scope

- Full agent prompting.
- End-to-end pipeline execution.
- Choosing a permanent external search provider.

---

## Completion Notes

- Added `FoundryClient.smoke_test()` with centralized endpoint normalization and safe structured diagnostics.
- Added CLI command gating via `RUN_LIVE_FOUNDRY_TESTS=1`.
- Added secret redaction for credential-bearing headers and tests proving raw secrets do not appear in metadata or exceptions.
- Added opt-in live integration test, skipped by default.
- Verified the gated CLI command exits before any live call unless the flag is set.
- Verified `python -m pytest`, Radon CC, Radon MI, and linter diagnostics.

---

## Definition of Done

- [x] Code implemented following `DOCS/AI_GUIDE.md` standards.
- [x] Acceptance criteria verified.
- [x] Unit tests pass with mocked HTTP responses.
- [x] Live integration test is opt-in and documented.
- [x] No secrets appear in logs, test output, or artifacts.
- [x] Radon CC check: all production functions grade A (CC <= 10), or any exception is documented.
- [x] Radon MI check: all production files grade A (MI >= 20).
- [x] Story file renamed with ` - DONE` suffix.
- [x] `DOCS/BACKLOG.md` updated.
