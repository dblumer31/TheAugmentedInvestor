# US-009: Fact Check And Source Quality Rules

**Story Type:** Feature  
**Priority:** High  
**Sprint:** 3  
**Story Points:** 8

---

## User Story

**As an** editor,  
**I want** drafts audited against research evidence and source quality,  
**So that** citations are not mistaken for proof and unsupported claims are surfaced before export.

---

## Description

Implement the Fact Check Agent and deterministic source-quality triage rules. The stage
must compare draft claims against the research brief and stored source evidence when
available, then produce a structured `FactCheckReport`.

---

## Acceptance Criteria

- [x] Fact Check identifies unsupported numbers, missing URLs, instrument imprecision, overconfident projections, missing counterarguments, investment advice language, and unlabeled scenario math.
- [x] Fact Check identifies weak source, source mismatch, source-quality mismatch, unverified market return, overreliance on blog/Substack, missing exact quote, and claim unproven.
- [x] Fact Check includes a source-quality summary and overall score.
- [x] Fact Check classifies claim types such as primary data, interpretation, scenario math, and editorial extrapolation.
- [x] Plain-text footnote URLs count as valid source citations when a URL appears anywhere for the claim.
- [x] Valid mathematical restatements, unit conversions, and reasonable roundings of cited figures are classified as `ok`.
- [x] Source-quality rules are enforced by claim type for `market_return`, `valuation`, `company_financial`, `institutional_report`, `forecast`, `scenario_math`, and `editorial_interpretation`.
- [x] Severity calibration follows the prototype rules for `error`, `warning`, `info`, and `ok`.
- [x] Fact-check flags include `claimType`, `requiredSourceQuality`, `actualSourceQuality`, `verificationStatus`, `triage`, and optional `addendumQuery`.
- [x] Each flag is classified as fixable with existing research, generalize/remove unsupported specificity, or needs research addendum.
- [x] Load-bearing weak-source claims are removed or sent to research addendum, not merely softened.
- [x] The rule `citation exists != claim is proven` is preserved in code and tests.
- [x] Invalid fact-check JSON performs one controlled retry using bounded validation context from the JSON parser.
- [x] Deterministic source-quality helpers are exposed for reuse by Fix Pass and Re-Check.

---

## Technical Notes

### Implementation Approach

- Add `prompts/fact_check.md`.
- Keep deterministic triage helpers separate from prompt rendering.
- Prefer pure functions for source-quality classification and triage where practical.
- Use fixture drafts and research briefs to test each flag category.
- Add fixtures for the URL rule, unit conversion rule, source-quality claim-type matrix, and severity calibration.
- Implement reusable helpers in `src/augmented_investor/pipeline/source_quality_rules.py`.
- Do not introduce direct provider calls in unit tests; use fake message clients.

### File Changes

| File | Change |
|------|--------|
| `src/augmented_investor/agents/fact_check_agent.py` | Create Fact Check Agent. |
| `src/augmented_investor/prompts/fact_check.md` | Create fact-check prompt template. |
| `src/augmented_investor/pipeline/source_quality_rules.py` | Add deterministic source-quality and triage helpers. |
| `src/augmented_investor/pipeline/fact_check_postprocess.py` | Add deterministic report post-processing helpers. |
| `src/augmented_investor/pipeline/orchestrator.py` | Reuse existing injectable `fact_check_draft()` boundary from US-006. |
| `tests/unit/test_fact_check_agent.py` | Add mocked agent tests. |
| `tests/unit/test_source_quality_rules.py` | Add deterministic triage rule tests. |

### Implementation Summary

- Added `FactCheckAgent` with structured JSON parsing and one controlled validation retry.
- Added `prompts/fact_check.md` for the fact-check contract.
- Added deterministic source-quality rules for claim-type requirements, citation recognition, source-quality mismatch, triage buckets, and severity calibration.
- Added fact-check post-processing for investment advice, unlabeled scenario language, source-quality summaries, and overall scoring.
- Added tests for source-quality categories, triage buckets, URL handling, numeric restatements, and fake-client fact-check behavior.
- Verified `python -m pytest`, Radon CC, Radon MI, and linter diagnostics.

---

## Dependencies

- US-007 (Research and retrieval agent)
- US-008 (Thesis and writer agents)

---

## Spec References

- FR-2.6.1: Run Structured Fact Check
- FR-2.6.2: Enforce Source Quality By Claim Type
- FR-2.6.3: Apply Triage Buckets

---

## Assumptions

- The first implementation can combine LLM-generated fact-check reports with deterministic post-processing for source-quality triage.
- Source verification becomes stronger as retrieved evidence quality improves.

---

## Out of Scope

- Fixing flagged draft text.
- Running targeted research addendum.
- External market-data vendor lookup.

---

## Definition of Done

- [x] Code implemented following `DOCS/AI_GUIDE.md` standards.
- [x] Acceptance criteria verified.
- [x] Unit tests cover all source-quality categories and triage buckets.
- [x] No linter warnings introduced.
- [x] Radon CC check: all production functions grade A (CC <= 10), or any exception is documented.
- [x] Radon MI check: all production files grade A (MI >= 20).
- [x] Story file renamed with ` - DONE` suffix.
- [x] `DOCS/BACKLOG.md` updated.
