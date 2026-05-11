# Process Executive Summary: AI-Assisted Software Development Lifecycle

**Version:** 1.2  
**Last Updated:** January 31, 2026

---

## Table of Contents

1. [Overview](#overview)
2. [Process Framework](#process-framework)
3. [Documentation Structure](#documentation-structure)
4. [User Story Format](#user-story-format)
5. [Skills Library](#skills-library)
6. [Coding Standards](#coding-standards)
7. [Quality Assurance](#quality-assurance)
8. [Definition of Done](#definition-of-done)
9. [Status Tracking](#status-tracking)
10. [Design Decisions](#design-decisions)
11. [Philosophy](#philosophy)
12. [New Project Setup](#new-project-setup)

---

## Overview

This framework combines structured documentation with reusable AI agent skills to create a repeatable, quality-focused SDLC. It enables efficient collaboration between human developers and AI agents (Cursor) to deliver consistent, maintainable software.

---

## Process Framework

```
Plan Mode → create-story-from-plan → review-story → implement-story
                                                          ↓
                    create-pr ← update-backlog ← code-review
```

| Step | Action |
|------|--------|
| 1. Plan | Use Cursor's plan mode to discuss and align |
| 2. Create Stories | `/create-story-from-plan` |
| 3. Review | `/review-story @DOCS/TASKS/US-XXX.md` |
| 4. Implement | `/implement-story @DOCS/TASKS/US-XXX.md` |
| 5. Code Review | `/code-review @DOCS/TASKS/US-XXX.md` |
| 6. Update Status | `/update-backlog` |
| 7. Create PR | `/create-pr @DOCS/TASKS/US-XXX.md` |

---

## Documentation Structure

```
DOCS/
├── SPEC.md              # Functional requirements
├── DESIGN.md            # Technical architecture
├── AI_GUIDE.md          # Coding standards
├── DECISIONS.md         # Architectural decisions with rationale
├── BACKLOG.md           # Sprint status and tracking
└── TASKS/
    └── US-XXX-*.md      # Individual user stories
```

**Minimum needed:** `DOCS/TASKS/` folder with at least one story file.

**AI Context Priority:** TASKS → SPEC → DESIGN → DECISIONS → BACKLOG

---

## User Story Format

```markdown
# US-XXX: Story Title

**Story Type:** Database Schema | Infrastructure | Feature | Testing | Documentation
**Priority:** Critical | High | Medium | Low
**Sprint:** [number]  |  **Story Points:** [1-13]

## User Story
**As a** [role], **I want** [feature], **So that** [value].

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2

## Technical Notes
- Implementation guidance

## Dependencies
- US-XXX (if any)
```

**Sizing:** Small (1-3 pts) | Medium (5 pts) | Large (8-13 pts) — Target 1-3 days per story.

**Naming:** `US-XXX-descriptive-name.md` → `US-XXX-descriptive-name - DONE.md`

---

## Skills Library

### Core SDLC Skills (`~\.cursor\skills\`)

| Skill | Purpose |
|-------|---------|
| **create-story-from-plan** | Converts plans into sized user stories |
| **review-story** | Validates stories before implementation |
| **implement-story** | Executes implementation per acceptance criteria |
| **code-review** | Reviews code against standards |
| **update-backlog** | Maintains sprint progress |
| **create-pr** | Generates PR descriptions |
| **radon-analysis** | *(Python)* Code complexity analysis |

### IDE & System Skills

| Location | Skills |
|----------|--------|
| `~\.cursor\skills-cursor\` | create-rule, create-skill, update-cursor-settings |
| `~\.codex\skills\.system\` | skill-creator, skill-installer |

---

## Coding Standards

Defined in each project's `AI_GUIDE.md`:

- **Naming:** PascalCase variables; intent-describing names
- **Structure:** Small focused functions; max 3 nesting levels; DRY
- **Docs:** File-level purpose comments; docstrings for public functions
- **Errors:** Fail fast; never swallow exceptions; context in messages
- **Data:** Named constants; strong types; prefer immutability
- **AI Code:** Must compile; clarity over cleverness; no placeholders

---

## Quality Assurance

### TDD Workflow

**RED** → Write failing test | **GREEN** → Minimal code to pass | **REFACTOR** → Improve

```
tests/
├── unit/           # Fast, isolated, mocked
└── integration/    # Real dependencies, requires setup
```

### Code Complexity

Use static analysis tools for your language:

| Language | Tools |
|----------|-------|
| Python | Radon (grades A-F for complexity, A-C for maintainability) |
| JavaScript/TypeScript | ESLint, SonarQube |
| Java/C# | SonarQube, PMD |
| Go | golangci-lint |

---

## Definition of Done

A story is **Done** when all applicable criteria are met:

#### Code Quality
- [ ] Follows AI_GUIDE.md standards
- [ ] Compiles without errors
- [ ] Error handling implemented
- [ ] No linter errors introduced

#### Testing
- [ ] Tests exist if required
- [ ] Unit tests pass
- [ ] Integration tests pass (if applicable)
- [ ] Tests cover acceptance criteria

#### Code Complexity
- [ ] No high-complexity functions (grade D+ / score 21+)
- [ ] No low-maintainability files (grade C / score 0-9)
- [ ] Static analysis run for significant changes

#### Acceptance & Tracking
- [ ] All acceptance criteria met
- [ ] No unrelated changes (scope discipline)
- [ ] Story file renamed with "- DONE" suffix
- [ ] BACKLOG.md updated

---

## Status Tracking

| Symbol | Status |
|--------|--------|
| ✅ | Done |
| 🚧 | In Progress |
| 📋 | Pending |
| 🔴 | Blocked |

---

## Design Decisions

Each project maintains `DECISIONS.md` with:

- **Context** → Problem or choice
- **Decision** → What was decided
- **Rationale** → Why
- **Consequences** → Trade-offs

---

## Philosophy

> **"Allow AI to be creative when defining the problem, and deterministic when solving it."**

- Implementation follows acceptance criteria exactly
- Ambiguous requirements require clarification
- No new behavior beyond what's specified
- AI assumptions must be documented

---

## New Project Setup

### 1. Create Folder Structure

```bash
mkdir DOCS
mkdir DOCS/TASKS
```

### 2. Create Required Documentation

| File | Purpose | Create When |
|------|---------|-------------|
| `DOCS/SPEC.md` | Functional requirements | At project start |
| `DOCS/DESIGN.md` | Technical architecture | At project start |
| `DOCS/AI_GUIDE.md` | Coding standards for this project | At project start |
| `DOCS/BACKLOG.md` | Sprint status and tracking | At project start |
| `DOCS/TASKS/README.md` | Sprint organization | At project start |

### 3. Create Optional Documentation

| File | Purpose | Create When |
|------|---------|-------------|
| `DOCS/DECISIONS.md` | Architectural decisions log | When first major decision is made |
| `DOCS/STORY_GUIDE.md` | Story format reference | If team needs detailed guidance |
| `DOCS/TDD_GUIDE.md` | Test-Driven Development workflow | If using TDD practices |

### 4. Begin Development

1. **Plan** — Use Cursor's plan mode to discuss features
2. **Create Stories** — `/create-story-from-plan` to break plan into stories
3. **Review** — `/review-story` to validate before implementing
4. **Implement** — `/implement-story` to build the feature
5. **Code Review** — `/code-review` to check quality
6. **Update Backlog** — `/update-backlog` to track progress
7. **Create PR** — `/create-pr` to prepare for merge

### Tips for Success

- Start with a minimal `SPEC.md` and iterate as requirements clarify
- Keep stories small (1-3 days) — split larger work
- Use `DECISIONS.md` to document "why" for future reference
- Review stories before implementing to catch issues early

---
