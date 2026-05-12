# US-012: End-To-End Tests And Quality Gates

**Story Type:** Testing  
**Priority:** High  
**Sprint:** 4  
**Story Points:** 5

---

## User Story

**As a** maintainer,  
**I want** end-to-end tests and quality reports for the Python rewrite,  
**So that** the pipeline can be changed safely and kept within project quality standards.

---

## Description

Add the test and quality coverage required by `DOCS/SPEC.md`, `DOCS/TDD_GUIDE.md`, and
`DOCS/CODE-QUALITY.md`. This story consolidates the final verification pass across the
mocked pipeline, opt-in live Foundry test, external search mocks, and Radon reporting.

---

## Acceptance Criteria

- [x] Unit tests cover config loading with fake environment variables.
- [x] Unit tests cover prompt rendering.
- [x] Unit tests cover JSON parsing and validation.
- [x] Unit tests cover fact-check triage rules.
- [x] Unit tests cover fix-pass filtering behavior.
- [x] Unit tests cover fact-check URL footnote handling and unit conversion/restatement handling.
- [x] Unit tests cover source-quality requirements by claim type.
- [x] Unit tests cover severity calibration and Re-Check persistence rules.
- [x] Azure Foundry integration tests are opt-in because they require real credentials.
- [x] External search integration tests use mocked API calls first.
- [x] End-to-end pipeline test runs with mocked LLM and search clients.
- [x] Radon complexity and maintainability checks are run after implementation.
- [x] Radon report is stored in `DOCS/Radon Checks/` using the documented naming convention.
- [x] Test report is stored in `DOCS/Test Reports/` for the final full-suite run.
- [x] README documents the Python CLI run path, test commands, opt-in Foundry test, and Radon check.

---

## Technical Notes

### Implementation Approach

- Follow `DOCS/TDD_GUIDE.md` test layout and fixture guidance.
- Use mocked providers for default test runs.
- Mark live integration tests explicitly so they do not run accidentally.
- Follow `DOCS/CODE-QUALITY.md` for Radon commands and report format.

### File Changes

| File | Change |
|------|--------|
| `tests/conftest.py` | Expand shared fixtures for sample pipeline data. |
| `tests/unit/` | Fill unit coverage gaps from previous stories. |
| `tests/integration/` | Add mocked end-to-end pipeline tests and opt-in live tests. |
| `DOCS/Test Reports/` | Add full-suite test report after implementation. |
| `DOCS/Radon Checks/` | Add Radon report after implementation. |
| `README.md` | Update run/test instructions if needed. |

---

## Dependencies

- US-002 through US-011

---

## Spec References

- FR-2.1.1: Preserve Editorial Stage Order
- FR-2.1.2: Persist Every Stage Output
- FR-2.3.3: Abstract Search Provider
- FR-2.6.2: Enforce Source Quality By Claim Type
- FR-2.6.3: Apply Triage Buckets
- FR-2.7.2: Re-Check Fixed Draft
- FR-2.8.2: Smoke-Test Foundry Before Full Pipeline Use
- FR-2.9.2: Export Final Issue

---

## Assumptions

- This story is completed after the feature stories so it can verify the integrated behavior.
- Per-story tests should still be written alongside implementation; this story is the final quality gate, not a reason to defer all tests.

---

## Out of Scope

- New product features.
- Refactoring unrelated code.
- Live external search calls unless the user approves a provider.

---

## Definition of Done

- [x] All tests pass.
- [x] Opt-in live tests are documented and skipped by default.
- [x] Radon report created per `DOCS/CODE-QUALITY.md`.
- [x] Test report created per `run-tests` skill reporting format.
- [x] Any complexity findings are documented with follow-up recommendations.
- [x] `README.md` reflects the Python app run/test path if implementation is complete.
- [x] Story file renamed with ` - DONE` suffix.
- [x] `DOCS/BACKLOG.md` updated.

---

## Implementation Summary

- Expanded shared pytest fixtures for canonical scope, research, thesis, draft, fact-check, and artifact store data.
- Added a mocked agent-level end-to-end integration test using fake LLM and search clients.
- Verified existing unit coverage for config loading, prompt rendering, JSON validation, fact-check/source-quality rules, fix-pass behavior, URL/citation handling, unit restatement, severity, re-check persistence, and mocked search behavior.
- Updated `README.md` with the Python CLI workflow, test commands, opt-in live Foundry smoke-test path, and Radon commands.
- Added `DOCS/Test Reports/TestReport-all-2026-05-11.md` and `DOCS/Radon Checks/Radon-post-US012.md`.
- Verification: `python -m pytest` passed with 83 passed and 1 skipped; linter diagnostics reported no errors; Radon CC average was A (1.96) and all MI grades were A.
