# AI GUIDE – How to Use Project Context

This guide explains how AI tools (like Cursor) should interpret this repository documentation to create code. We allow AI to be creative when defining the problem, and deterministic when solving it.

## Context Priority
1. `TASKS/` → Current work items. 
2. `SPEC.md` → Defines functional requirements.
3. `DESIGN.md` → Technical implementation details.
4. `DECISIONS.md` → Design rationale.
5. `BACKLOG.md` → Sprint status overview.

## Expected Coding Style
- Variable Names should be PascalCase.  example (FirstOrderBeginDate, CustomerId)
- Minimal dependencies: prefer standard library and existing project utilities over new libraries.
- Write clear variable and component names.names should describe intent, not implementation.

## Functions and Structure

- Keep functions small and focused: a function should do **one thing well**.
- Avoid deeply nested code (no more than 3 levels of nesting where possible).
- Prefer pure functions when practical (no hidden mutation or global state changes).
- Reuse existing helpers instead of copying logic (DRY – Don't Repeat Yourself).

# Formatting and Readability

- Keep lines reasonably short (e.g., ~100 characters max).
- Use consistent indentation (spaces, not tabs, unless project says otherwise).
- Group related code with blank lines to improve readability.
- Put related declarations close together (e.g., variables near where they're used).

## Comments and Documentation

- At the top of each file, briefly state its purpose in 1–2 sentences.
- For each public function/class, include a short doc comment describing:
  - What it does
  - Its main inputs and outputs
  - Any side effects or important constraints
- Use comments to explain *why* something is done, not *what* the code literally does.
- Avoid redundant comments that just restate the code.

## Error Handling and Logging

- Fail fast: validate inputs early and return clear errors.
- Do not swallow exceptions silently. If you catch an error, either:
  - Handle it fully, or
  - Log it and rethrow / return a meaningful error.
- Error messages should give enough context to debug (what operation failed, key IDs, etc.).
- Avoid excessive logging in tight loops or performance-critical paths.

## Data and Constants

- No magic numbers/strings: use named constants or enums for values with meaning.
- Use clear types for dates, times, and IDs (don't use raw strings where a stronger type exists).
- Prefer immutable data structures where reasonable to avoid accidental changes.

## AI-Generated Code Expectations

- Generated code must compile/run without syntax errors.
- Prefer clarity over cleverness: straightforward, readable solutions are better than tricky ones.
- If a non-obvious design choice is made, include a brief comment explaining the rationale.
- Do not leave placeholder code like `TODO: implement` unless explicitly requested.

## Cite Spec in every story

- When you write a story, require a small section like:
-- Spec references: FR-2.1.1, FR-2.4.1, etc.
-- Assumptions added by AI: (must list any)

## Testing Requirements

- **Unit tests are required** for all data layer functions (queries, persistence, repositories).
- **Unit tests are required** for business logic (validation, calculations, workflows).
- **Manual testing is acceptable** for UI/DOM manipulation; when used, document what was verified and why automated tests were not added (e.g., brittle selectors, one-off UI flows).
- Tests must be written **before or alongside** implementation (test-driven or test-alongside development); do not defer all testing to the end.
