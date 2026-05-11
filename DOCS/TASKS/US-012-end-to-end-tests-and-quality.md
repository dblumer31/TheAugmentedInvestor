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

- [ ] Unit tests cover config loading with fake environment variables.
- [ ] Unit tests cover prompt rendering.
- [ ] Unit tests cover JSON parsing and validation.
- [ ] Unit tests cover fact-check triage rules.
- [ ] Unit tests cover fix-pass filtering behavior.
- [ ] Unit tests cover fact-check URL footnote handling and unit conversion/restatement handling.
- [ ] Unit tests cover source-quality requirements by claim type.
- [ ] Unit tests cover severity calibration and Re-Check persistence rules.
- [ ] Azure Foundry integration tests are opt-in because they require real credentials.
- [ ] External search integration tests use mocked API calls first.
- [ ] End-to-end pipeline test runs with mocked LLM and search clients.
- [ ] Radon complexity and maintainability checks are run after implementation.
- [ ] Radon report is stored in `DOCS/Radon Checks/` using the documented naming convention.

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

- [ ] All tests pass.
- [ ] Opt-in live tests are documented and skipped by default.
- [ ] Radon report created per `DOCS/CODE-QUALITY.md`.
- [ ] Any complexity findings are documented with follow-up recommendations.
- [ ] `README.md` reflects the Python app run/test path if implementation is complete.
- [ ] Story file renamed with ` - DONE` suffix.
- [ ] `DOCS/BACKLOG.md` updated.
