# US-010: Fix Pass And Re-Check

**Story Type:** Feature  
**Priority:** High  
**Sprint:** 3  
**Story Points:** 5

---

## User Story

**As an** editor,  
**I want** the system to repair flagged draft issues and re-check the result,  
**So that** the final issue improves without losing the approved thesis or rewriting clean sections.

---

## Description

Implement the Fix Pass Agent and Re-Check stage. The Fix Pass must apply surgical changes
only to flagged issues where existing evidence supports a fix. Issues requiring research
addendum must not be silently fabricated or repaired without evidence.

---

## Acceptance Criteria

- [x] Fix Pass preserves the approved thesis, article structure, editorial voice, and unflagged sections.
- [x] Fix Pass can add date qualifiers, add citations, rephrase investment advice language, label scenario estimates, add existing counterarguments, correct instrument names, soften weakly sourced claims, generalize unsupported named examples, and remove unsupported specificity.
- [x] Fix Pass records which fact-check flags were addressed.
- [x] Claims marked as requiring research addendum are not silently fabricated or repaired without evidence.
- [x] Unsupported named analysts, companies, institutions, exact spreads, counts, valuation figures, and named source attributions are removed or generalized only when the broader claim is supported by existing research.
- [x] Weak-source quantitative claims remove exact percentages, return spreads, counts, basis points, and valuation figures unless adequate source quality exists.
- [x] Load-bearing quantitative claims are removed or sent to research addendum; adding "unverified" or "primary data pending" is not considered a fix.
- [x] Blog/intermediary citations are attributed precisely and are not upgraded to "research suggests" or "institutional research" without direct support.
- [x] Source-quality `needsResearchAddendum` flags are passed to Fix Pass for softening/removal only; non-source-quality `needsResearchAddendum` flags are skipped.
- [x] Fix Pass logs actions as removed unsupported specificity, generalized claim, softened weak-source quant, marked source-limited, or removed claim.
- [x] Fixed draft artifacts record addressed flag categories and fix-pass action labels for auditability.
- [x] Invalid fixed-draft JSON performs one controlled retry using bounded validation context from the JSON parser.
- [x] Re-Check produces a new `FactCheckReport`.
- [x] Review output can show before/after issue counts.
- [x] Remaining high-severity issues are visible before export.
- [x] Re-Check applies the same URL, unit-conversion, source-quality, severity, and triage rules as the first pass.
- [x] Re-Check flags unresolved unsupported specificity and weak-source load-bearing claims again at the same severity.

---

## Technical Notes

### Implementation Approach

- Add `prompts/fix_pass.md`.
- Wire `apply_fix_pass()` and `recheck_draft()` in the orchestrator.
- Reuse `FactCheckAgent` for re-check rather than creating separate logic.
- Tests should verify the fixed draft is the input to re-check.
- Add tests for load-bearing quantitative claims, source-quality addendum handling, and Re-Check persistence rules.
- Add deterministic fix-pass rule helpers to decide which flags are repairable and which research-addendum flags must be skipped.
- Store fix-pass audit metadata on the fixed `DraftIssue` model so `05_fixed_draft.json` is self-describing.
- Do not introduce direct provider calls in unit tests; use fake message clients.

### File Changes

| File | Change |
|------|--------|
| `src/augmented_investor/agents/fix_pass_agent.py` | Create Fix Pass Agent. |
| `src/augmented_investor/prompts/fix_pass.md` | Create fix-pass prompt template. |
| `src/augmented_investor/pipeline/fix_pass_rules.py` | Add deterministic repairability and action-label helpers. |
| `src/augmented_investor/models/draft.py` | Add fix-pass audit metadata fields. |
| `src/augmented_investor/pipeline/orchestrator.py` | Wire fix pass and re-check stages. |
| `tests/unit/test_fix_pass_agent.py` | Add fix-pass tests. |
| `tests/unit/test_recheck_flow.py` | Add re-check orchestration tests. |

### Implementation Summary

- Added `FixPassAgent` with structured fixed-draft validation and one controlled retry.
- Added `prompts/fix_pass.md` for the fix-pass contract.
- Added `fix_pass_rules.py` for repairable/skipped flag partitioning and action labels.
- Added fix-pass audit fields to `DraftIssue` so `05_fixed_draft.json` records addressed categories and actions.
- Added unit tests for research-addendum safeguards, action labels, fixed-draft retry, and re-check persistence.
- Verified `python -m pytest`, Radon CC, Radon MI, and linter diagnostics.

---

## Dependencies

- US-009 (Fact check and source quality rules)

---

## Spec References

- FR-2.7.1: Apply Surgical Fixes
- FR-2.7.2: Re-Check Fixed Draft

---

## Assumptions

- Fix Pass may return a full revised draft, but tests should ensure unrelated sections are preserved.
- Research addendum support remains a later enhancement unless explicitly included in a future story.

---

## Out of Scope

- Targeted research addendum execution.
- Manual rich-text editing UI.
- Newsletter publishing.

---

## Definition of Done

- [x] Code implemented following `DOCS/AI_GUIDE.md` standards.
- [x] Acceptance criteria verified.
- [x] Unit tests cover fixed-draft re-check and research-addendum safeguards.
- [x] No linter warnings introduced.
- [x] Radon CC check: all production functions grade A (CC <= 10), or any exception is documented.
- [x] Radon MI check: all production files grade A (MI >= 20).
- [x] Story file renamed with ` - DONE` suffix.
- [x] `DOCS/BACKLOG.md` updated.
