# US-002: Python Project Scaffold And Configuration

**Story Type:** Infrastructure  
**Priority:** Critical  
**Sprint:** 1  
**Story Points:** 3

---

## User Story

**As a** developer,  
**I want** a Python project scaffold with configuration and test structure,  
**So that** later pipeline stories can be implemented consistently and safely.

---

## Description

Create the Python package layout, dependency files, placeholder runtime folders, and
example environment template described in `DOCS/DESIGN.md`. This story establishes the
foundation for the Foundry smoke test, model contracts, pipeline orchestration, and tests.

---

## Acceptance Criteria

- [x] `src/augmented_investor/` package structure exists with planned subpackages.
- [x] `tests/unit/`, `tests/integration/`, and `tests/conftest.py` exist.
- [x] `requirements.txt` and `requirements-dev.txt` define the initial runtime and dev dependencies.
- [x] `example.env` documents only placeholder values for Foundry and optional search settings.
- [x] Runtime config reads from environment variables and does not read the real `.env` file.
- [x] Missing required live-provider config produces clear validation errors.

---

## Technical Notes

### Implementation Approach

- Follow `DOCS/DESIGN.md` Section 4 for directory structure.
- Use `pydantic-settings` for environment-based configuration.
- Keep functions small and focused per `DOCS/AI_GUIDE.md`.
- Add top-of-file purpose comments/docstrings for public modules.

### File Changes

| File | Change |
|------|--------|
| `src/augmented_investor/` | Create package and subpackage skeleton. |
| `src/augmented_investor/config.py` | Create settings model and validation helpers. |
| `tests/conftest.py` | Create fake-safe config fixtures. |
| `requirements.txt` | Add runtime dependencies. |
| `requirements-dev.txt` | Add test and quality dependencies. |
| `example.env` | Create placeholder environment template. |

---

## Dependencies

- None

---

## Spec References

- FR-2.8.1: Configure Azure AI Foundry From Environment

---

## Assumptions

- The existing `US-001-example-story.md` remains untouched as a template, so generated stories start at `US-002`.
- Python 3.11+ is acceptable as stated in `DOCS/DESIGN.md`.
- `runs/` will be runtime output and should not include committed run data.

---

## Out of Scope

- Live Foundry calls.
- Agent implementation.
- UI implementation.
- Database storage.

---

## Completion Notes

- Added the Python package scaffold, test structure, dependency files, runtime `runs/` placeholder, and `example.env`.
- Added environment-only configuration loading in `src/augmented_investor/config.py`.
- Added config unit tests using fake environment variables.
- Verified `python -m pytest`, `python -m radon cc -a -s`, and `python -m radon mi -s`.

---

## Definition of Done

- [x] Code implemented following `DOCS/AI_GUIDE.md` standards.
- [x] Acceptance criteria verified.
- [x] Unit tests added for config loading with fake environment variables.
- [x] No linter warnings introduced.
- [x] Story file renamed with ` - DONE` suffix.
- [x] `DOCS/BACKLOG.md` updated.
