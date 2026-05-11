# US-005: Core Models And JSON Validation

**Story Type:** Infrastructure  
**Priority:** Critical  
**Sprint:** 1  
**Story Points:** 5

---

## User Story

**As a** developer,  
**I want** Pydantic models and deterministic JSON validation for every pipeline stage,  
**So that** model responses become reliable contracts instead of unstructured text.

---

## Description

Create the core data contracts for scope, research, thesis, draft, fact-check, source
evidence, and run artifacts. Add JSON parsing and validation helpers that perform one
controlled retry when model output fails parsing or schema validation.

US-004 introduced provider/search contracts, including source evidence for retrieved
content. This story must consolidate that contract with the core model layer rather than
creating a second incompatible `SourceEvidence` shape.

---

## Acceptance Criteria

- [x] `ScopeRequest` validates market, windows, reader horizon, reader type, contrarian lean, depth, and length.
- [x] `ResearchBrief` supports claims, evidence, sources, source quality, confidence, exact quote support, and retrieved evidence.
- [x] `ThesisBrief`, `DraftIssue`, `FactCheckReport`, and `RunArtifact` models exist.
- [x] Source evidence/search evidence contracts from US-004 are reused, moved into the model layer, or re-exported from one canonical location so downstream code has one compatible source evidence type.
- [x] Source-quality categories match `DOCS/SPEC.md`.
- [x] `FactCheckFlag` supports the complete prototype category enum, severity enum, claim-type enum, required/actual source quality fields, verification status, triage, and optional addendum query.
- [x] `FactCheckReport.sourceQualitySummary` supports weak-source flag count, unverified quantitative claim count, blog-only claim count, and overall source-quality rating.
- [x] Agent outputs must parse as valid JSON for structured stages.
- [x] Parsed JSON must validate against the stage Pydantic model.
- [x] JSON parsing performs one controlled retry with validation errors included in retry context.
- [x] Raw model output can be preserved for debugging without secrets.
- [x] JSON parsing validates list items independently where a model output contains lists, so one invalid item does not discard an otherwise valid batch.
- [x] Retry context contains validation errors and a bounded raw-output preview, not full unbounded model output.

---

## Technical Notes

### Implementation Approach

- Implement model files under `src/augmented_investor/models/`.
- Implement JSON parsing helpers under `src/augmented_investor/pipeline/json_parser.py`.
- Keep validation errors clear enough for both operator display and retry prompts.
- Unit tests should use fixture payloads from `tests/conftest.py`.
- Reconcile the `SourceEvidence` model already used by `external_search_client.py`; avoid duplicate model definitions with incompatible fields.

<!-- QA-ADDED -->
- All `datetime` fields must be timezone-aware UTC. Enforce via explicit validators that reject naive datetimes and normalize non-UTC offsets to UTC via `.astimezone(timezone.utc)`. Tests must cover naive datetime rejected, non-UTC datetime normalized, and valid UTC accepted.
- All `list`, `dict`, and `set` fields on Pydantic models must use `Field(default_factory=list)` or equivalent. Never use `= []` or `= {}` defaults.
- When parsing LLM JSON output containing a list, iterate over the list and validate each element individually where item-level salvage is appropriate. One invalid item must drop only that item, not the entire batch. Log or return a warning for each dropped item with enough context to debug.
- Raw model output persistence/debug fields must be bounded and redacted. Do not store API keys, authorization headers, or unbounded raw responses in validation errors or retry prompts.
- If this story introduces custom parsing exceptions, they must expose typed attributes such as `message`, `raw_preview`, and validation error details instead of requiring callers to parse strings.
- The retry helper prepares retry context only; it must not call Foundry or any other provider directly.
<!-- END QA-ADDED -->

### File Changes

| File | Change |
|------|--------|
| `src/augmented_investor/models/scope.py` | Created `ScopeRequest`. |
| `src/augmented_investor/models/research.py` | Created `ResearchBrief`, claims, sources, canonical `SearchResult`, and canonical `SourceEvidence`. |
| `src/augmented_investor/models/thesis.py` | Created `ThesisBrief`. |
| `src/augmented_investor/models/draft.py` | Created `DraftIssue`. |
| `src/augmented_investor/models/fact_check.py` | Created `FactCheckReport` and flag models. |
| `src/augmented_investor/models/run_artifact.py` | Created `RunArtifact`. |
| `src/augmented_investor/pipeline/json_parser.py` | Created parse/validate/retry support. |
| `tests/unit/test_models.py` | Added model validation tests. |
| `tests/unit/test_json_parser.py` | Added parsing and retry tests. |

### Implementation Summary

- Added core Pydantic contracts for scope, research, thesis, draft, fact-check, source evidence, search results, and run artifacts.
- Moved `SearchResult` and `SourceEvidence` into the model layer and updated `external_search_client.py` to import the canonical types.
- Added UTC-aware datetime validation, lower-camel prototype JSON aliases, strict extra-field rejection, and `Field(default_factory=...)` mutable defaults.
- Added typed JSON validation errors, bounded/redacted raw previews, provider-agnostic retry context, and item-level list validation salvage.
- Verified `python -m pytest`, Radon CC, Radon MI, and linter diagnostics.

---

## Dependencies

- US-002 (Python project scaffold and configuration)
- US-004 (Provider and search client abstractions)

---

## Spec References

- FR-2.2.1: Capture Editorial Scope Inputs
- FR-2.2.2: Validate Scope Before Research
- FR-2.3.1: Produce Structured Research Briefs
- FR-2.3.2: Store Retrieved Evidence
- FR-2.3.3: Abstract Search Provider
- FR-2.4.1: Produce Thesis Briefs From Research
- FR-2.5.1: Generate Newsletter Drafts
- FR-2.6.1: Run Structured Fact Check
- FR-2.6.2: Enforce Source Quality By Claim Type
- FR-2.6.3: Apply Triage Buckets

---

## Assumptions

- Field names should preserve the intent of `DOCS/SPEC.md`; exact Python naming can be finalized during implementation.
- The retry helper prepares retry context but does not itself call the LLM provider.
- If moving source evidence models from `external_search_client.py` into `models/research.py`, update imports in `external_search_client.py` in the same story to keep tests green.

---

## Out of Scope

- Agent prompts.
- Provider HTTP calls.
- UI rendering.

---

## Definition of Done

- [x] Code implemented following `DOCS/AI_GUIDE.md` standards.
- [x] Acceptance criteria verified.
- [x] Unit tests pass for valid and invalid payloads.
- [x] No linter warnings introduced.
- [x] Radon CC check: all production functions grade A (CC <= 10), or any exception is documented.
- [x] Radon MI check: all production files grade A (MI >= 20).
- [x] Story file renamed with ` - DONE` suffix.
- [x] `DOCS/BACKLOG.md` updated.
