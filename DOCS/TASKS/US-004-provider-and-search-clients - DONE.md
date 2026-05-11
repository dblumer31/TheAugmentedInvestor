# US-004: Provider And Search Client Abstractions

**Story Type:** Infrastructure  
**Priority:** Critical  
**Sprint:** 1  
**Story Points:** 5

---

## User Story

**As a** developer,  
**I want** isolated Foundry and search client abstractions,  
**So that** agent code can use models and retrieval without depending on provider-specific details.

---

## Description

Implement the provider layer described in `DOCS/DESIGN.md`: a Foundry client for Anthropic
Messages calls and a search/retrieval interface that can later use Foundry tools or an
external search provider. This keeps research independent from the question of whether
Foundry supports model-side web search.

The US-003 smoke test confirmed that the configured Foundry deployment accepts
`web_search_20250305`, so this story should include a Foundry tool-backed search adapter
as the first real retrieval provider while still keeping the abstraction open for later
external search providers.

---

## Acceptance Criteria

- [x] `FoundryClient` can build Anthropic Messages requests against Azure Foundry.
- [x] `FoundryClient` supports default, Sonnet, and Opus model aliases from configuration.
- [x] Provider metadata records selected model/deployment, elapsed time, response status, and token usage when available.
- [x] API keys and authorization headers are never logged or persisted.
- [x] Search behavior is isolated behind a `search()` and `retrieve()` interface.
- [x] A `NoopSearchClient` exists for tests and offline development.
- [x] A `FoundryToolSearchClient` exists and uses the Foundry `web_search_20250305` tool through the provider abstraction.
- [x] The chosen provider and evidence source can be recorded in research artifacts.
- [x] Empty search results are treated as a normal condition, distinct from provider failures.
- [x] Provider failures raise typed errors with redacted request summaries.

---

## Technical Notes

### Implementation Approach

- Build on the endpoint behavior verified in US-003.
- Keep request construction, headers, timeouts, and response parsing inside `FoundryClient`.
- Define search result and source evidence contracts in the model layer or search client module.
- Use `httpx` for HTTP calls.

<!-- QA-ADDED -->
- US-003 verified `web_search_20250305` is accepted by Foundry, so implement `FoundryToolSearchClient` now rather than treating Foundry tool support as only hypothetical.
- All `datetime` fields on search/source evidence models must be timezone-aware UTC. Enforce via an explicit validator that rejects naive datetimes and normalizes non-UTC offsets to UTC.
- All `list`, `dict`, and `set` fields on Pydantic models must use `Field(default_factory=list)` or equivalent. Never use `= []` or `= {}` defaults.
- Reuse the existing secret redaction boundary from `foundry_client.py`; tests must assert raw API keys do not appear in logs, exceptions, metadata, or request summaries.
- Provider exception classes must expose typed attributes, at minimum `message`, optional `status_code`, and redacted `request_summary`.
- Explicitly distinguish between an empty result and provider failure:
  - Empty result: provider responded successfully but returned no usable results. Return an empty list and do not log an error.
  - Provider failure: provider returned an error, timed out, or raised an exception. Raise a typed provider error with redacted diagnostics.
<!-- END QA-ADDED -->

### File Changes

| File | Change |
|------|--------|
| `src/augmented_investor/foundry_client.py` | Implement provider message calls and safe metadata. |
| `src/augmented_investor/external_search_client.py` | Define search/retrieval interface, `NoopSearchClient`, and `FoundryToolSearchClient`. |
| `tests/unit/test_foundry_client.py` | Add mocked provider tests. |
| `tests/unit/test_external_search_client.py` | Add search abstraction tests. |

---

## Dependencies

- US-002 (Python project scaffold and configuration)
- US-003 (Azure Foundry smoke test)

---

## Spec References

- FR-2.3.3: Abstract Search Provider
- FR-2.8.1: Configure Azure AI Foundry From Environment
- FR-2.8.3: Support Role-Based Model Selection

---

## Assumptions

- Foundry `web_search_20250305` is available based on the completed US-003 smoke test.
- External provider-specific adapters beyond Foundry and `NoopSearchClient` can be added later.
- The Research Agent should consume search results as input rather than call provider-specific APIs directly.

---

## Out of Scope

- Full research agent implementation.
- Paid external search provider integration.
- Browser UI.

---

## Completion Notes

- Added reusable `FoundryClient.send_message()` and role-based model selection.
- Added safe response metadata, request summaries, and typed provider errors.
- Added `SearchClient` protocol, `NoopSearchClient`, `FoundryToolSearchClient`, `SearchResult`, and `SourceEvidence`.
- Added timezone-aware UTC validation for search/source evidence timestamps.
- Added mocked provider/search tests for empty results, provider failures, redaction, metadata, and retrieval.
- Verified `python -m pytest`, Radon CC, Radon MI, and linter diagnostics.

---

## Definition of Done

- [x] Code implemented following `DOCS/AI_GUIDE.md` standards.
- [x] Acceptance criteria verified.
- [x] Unit tests use mocked HTTP and fake config.
- [x] No linter warnings introduced.
- [x] Radon CC check: all production functions grade A (CC <= 10), or any exception is documented.
- [x] Radon MI check: all production files grade A (MI >= 20).
- [x] Story file renamed with ` - DONE` suffix.
- [x] `DOCS/BACKLOG.md` updated.
