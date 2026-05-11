# The Augmented Investor - Functional Requirements Specification

**Version:** 1.0  
**Last Updated:** 2026-05-11

---

## 1. Overview

### 1.1 Purpose

The Augmented Investor is an AI-assisted editorial pipeline for producing investor-focused newsletter issues at the intersection of AI, finance, markets, and investing. The Python rewrite must preserve the successful single-file HTML proof-of-concept workflow while adding a backend orchestrator, explicit run state, validated data contracts, safer provider integration, and replayable artifacts.

The product goal is not only to draft an article. The system must create an inspectable editorial desk where agents research, form a thesis, write, audit, repair, and export an issue before human approval.

### 1.2 Scope

This specification covers the functional requirements for rewriting the current browser-based prototype as a Python application. The initial implementation should provide a narrow vertical slice with a modular backend, Azure AI Foundry integration, persisted JSON artifacts, deterministic validation, and a minimal UI or CLI for operating the workflow.

In scope:

- Python backend pipeline for Scope, Research, Thesis, Writer, Fact Check, Fix Pass, Re-Check, and Export stages.
- Azure AI Foundry Anthropic Messages API integration.
- Foundry smoke test for endpoint shape, deployment identifiers, headers, request body, and tool/search support.
- Optional external search provider abstraction if Foundry does not support model-side web search.
- Pydantic data models for all stage contracts.
- Local run artifact storage.
- Source-quality checks and fact-check triage.
- Markdown and HTML export.
- Tests with mocked LLM/search clients by default.

Out of scope for the first implementation:

- Production authentication and multi-user accounts.
- Database-backed issue history.
- Automated publishing to newsletter platforms.
- Financial data vendor integration beyond an abstraction point.
- Investment recommendations or personalized financial advice.

### 1.3 Definitions

| Term | Definition |
|------|------------|
| Agent | A pipeline module that prompts an LLM or applies deterministic business logic for one editorial stage. |
| Foundry | Azure AI Foundry endpoint used to access Anthropic Claude model deployments. |
| Run | One end-to-end attempt to produce an issue from a scope request through export. |
| Run Artifact | A JSON or export file saved under a run-specific folder for replay, review, and debugging. |
| Research Brief | Structured evidence returned by the Research Agent, including claims, sources, source quality, and retrieved excerpts when available. |
| Thesis Brief | Structured editorial argument approved by the human editor before draft generation. |
| Draft Issue | The article draft produced by the Writer Agent. |
| Fact Check Report | Structured list of flags, triage buckets, source-quality findings, and overall score. |
| Fix Pass | A surgical revision pass that repairs flagged issues without restarting the full workflow. |
| Source Quality | Classification of source reliability for a given claim, such as primary market data, filing/IR, institutional report, reputable media, syndicated article, blog/Substack, or unknown. |

---

## 2. Functional Requirements

### 2.1 Pipeline Workflow

#### FR-2.1.1 Preserve Editorial Stage Order

**Description:** The system must preserve the prototype workflow: Scope -> Research -> Thesis Gate -> Write -> Fact Check -> Fix Pass -> Re-Check -> Review/Export.

**Acceptance Criteria:**

- [ ] The orchestrator exposes stage functions for `refine_scope()`, `run_research()`, `run_thesis()`, `approve_thesis()`, `write_draft()`, `fact_check_draft()`, `apply_fix_pass()`, `recheck_draft()`, and `export_issue()`.
- [ ] The Writer stage cannot run until a thesis has been approved.
- [ ] The Re-Check stage runs against the fixed draft, not the original draft.
- [ ] The final review shows the current draft, source list, fact-check state, and export options.

**Priority:** High

#### FR-2.1.2 Persist Every Stage Output

**Description:** The system must save each stage output as a run artifact so a run can be inspected, replayed, and debugged after the process exits.

**Acceptance Criteria:**

- [ ] Each run gets a unique `run_id`.
- [ ] Each stage writes a structured artifact under `runs/{run_id}/`.
- [ ] The minimum artifacts are `00_scope.json`, `01_research.json`, `02_thesis.json`, `03_draft.json`, `04_fact_check.json`, `05_fixed_draft.json`, `06_recheck.json`, `issue.html`, and `issue.md`.
- [ ] Research artifacts include retrieved source evidence when available, not only model-generated citations.
- [ ] Raw model responses are saved in a way that supports debugging without exposing secrets.

**Priority:** High

#### FR-2.1.3 Support Human Thesis Approval

**Description:** The system must include a human approval gate between thesis generation and article drafting.

**Acceptance Criteria:**

- [ ] The generated thesis brief is visible to the operator before draft generation.
- [ ] The operator can approve the thesis.
- [ ] The operator can reject or restart before draft generation.
- [ ] Approval status is persisted in the run state.

**Priority:** High

### 2.2 Scope Capture

#### FR-2.2.1 Capture Editorial Scope Inputs

**Description:** The system must capture the same scope controls as the current prototype so vague prompts become structured market questions.

**Acceptance Criteria:**

- [ ] Scope includes market or asset class.
- [ ] Scope includes recent window and historical context window.
- [ ] Scope includes reader horizon and reader type.
- [ ] Scope includes contrarian lean.
- [ ] Scope includes depth and target length.
- [ ] Scope can be serialized as a validated `ScopeRequest`.

**Priority:** High

#### FR-2.2.2 Validate Scope Before Research

**Description:** The system must validate scope inputs before invoking research.

**Acceptance Criteria:**

- [ ] Missing required fields produce validation errors.
- [ ] Invalid enum-like values are rejected or normalized.
- [ ] Validation errors are shown to the operator without starting a run stage.

**Priority:** High

### 2.3 Research And Retrieval

#### FR-2.3.1 Produce Structured Research Briefs

**Description:** The Research Agent must return structured evidence rather than article prose.

**Acceptance Criteria:**

- [ ] Research output includes market snapshot, prior trend, what changed, evidence for, evidence against, possible mispricing, source list, and recommended angle.
- [ ] Claims include source, date, confidence, instrument precision, and source-quality metadata.
- [ ] Claims indicate whether cited evidence directly supports the exact claim.
- [ ] Claims indicate whether exact quoted evidence is available.

**Priority:** High

#### FR-2.3.2 Store Retrieved Evidence

**Description:** Research must store source excerpts or retrieved source text when available so fact-checking can compare draft claims against evidence.

**Acceptance Criteria:**

- [ ] `ResearchBrief` supports `source_url`, retrieved text or excerpt, quoted evidence, and retrieval timestamp.
- [ ] `01_research.json` stores retrieved evidence when a retrieval provider returns it.
- [ ] Fact Check can consume stored evidence instead of relying only on prompt-generated source summaries.
- [ ] Market-return and valuation claims prefer primary data or reputable data providers when available.

**Priority:** High

#### FR-2.3.3 Abstract Search Provider

**Description:** The system must not assume Azure AI Foundry Claude supports Anthropic web search tools.

**Acceptance Criteria:**

- [ ] Search behavior is isolated behind an external search/retrieval abstraction.
- [ ] The Research Agent can operate with Foundry tool support if available.
- [ ] The Research Agent can operate with a separate provider such as Bing Search API, Tavily, SerpAPI, Exa, or another approved endpoint.
- [ ] The chosen provider and evidence source are recorded in the research artifact.

**Priority:** High

### 2.4 Thesis Generation

#### FR-2.4.1 Produce Thesis Briefs From Research

**Description:** The Thesis Agent must convert the research brief into a structured editorial argument.

**Acceptance Criteria:**

- [ ] Thesis output includes central thesis, thesis basis, bull case, base case, bear case, scenario math if any, mispricing view, contrarian test, confidence rationale, and newsletter angle.
- [ ] Thesis output references supporting and opposing evidence from the research brief.
- [ ] Scenario math is labeled as scenario analysis, not prediction.
- [ ] The thesis can be serialized as a validated `ThesisBrief`.

**Priority:** High

### 2.5 Draft Generation

#### FR-2.5.1 Generate Newsletter Drafts

**Description:** The Writer Agent must draft the issue from the approved thesis and selected research facts.

**Acceptance Criteria:**

- [ ] Draft output includes subject, title, subtitle, lede, body HTML or structured body content, sources used, and word count.
- [ ] The draft cites evidence inline.
- [ ] The draft avoids direct investment advice.
- [ ] Projections are labeled as scenario estimates.
- [ ] The draft ends with an investable question, not a recommendation.

**Priority:** High

#### FR-2.5.2 Preserve Editorial Voice And Structure

**Description:** The Writer Agent must write in the newsletter voice while following the approved thesis.

**Acceptance Criteria:**

- [ ] The draft does not introduce a contradictory central thesis.
- [ ] The draft does not invent unsupported quantitative specificity.
- [ ] The draft preserves the scope's reader type, horizon, depth, and target length.

**Priority:** High

### 2.6 Fact Checking And Source Quality

#### FR-2.6.1 Run Structured Fact Check

**Description:** The Fact Check Agent must compare the draft against the research brief and source-quality metadata.

**Acceptance Criteria:**

- [ ] Fact Check identifies unsupported numbers, missing URLs, instrument imprecision, overconfident projections, missing counterarguments, investment advice language, and unlabeled scenario math.
- [ ] Fact Check identifies weak source, source mismatch, source-quality mismatch, unverified market return, overreliance on blog/Substack, missing exact quote, and claim unproven.
- [ ] Fact Check includes a source-quality summary and overall score.
- [ ] Fact Check classifies claim types such as primary data, interpretation, scenario math, and editorial extrapolation.
- [ ] Plain-text footnote URLs count as valid citations; `missing_url` is only valid when no URL or source name exists anywhere for the claim.
- [ ] Valid mathematical restatements, unit conversions, and reasonable roundings of cited figures are classified as `ok`, not `unsupported_number`.
- [ ] Severity calibration follows the prototype rules: `error` means materially misleading, `warning` weakens credibility, `info` is non-actionable context, and `ok` is fully supported at appropriate source quality.
- [ ] Fact-check flags include `claimType`, `requiredSourceQuality`, `actualSourceQuality`, `verificationStatus`, `triage`, and optional `addendumQuery`.

**Priority:** High

#### FR-2.6.2 Enforce Source Quality By Claim Type

**Description:** Fact Check must apply source-quality requirements by claim type, not only detect whether a citation exists.

**Acceptance Criteria:**

- [ ] `market_return` claims require primary market data, filing/IR, or reputable financial media; syndicated-only support is `weak_source_for_quant_claim`.
- [ ] `valuation` claims require primary market data or filing/IR; syndicated, blog/Substack, unknown, or no source is insufficient.
- [ ] `company_financial` claims require company filing/IR or reputable financial media.
- [ ] `institutional_report` claims require exact title, publisher, and date; missing any of these is `exact_quote_missing`.
- [ ] `forecast` and `scenario_math` claims must be labeled in the draft; unlabeled claims are `scenario_math_unlabeled`.
- [ ] `editorial_interpretation` claims may use any source quality but must be framed as opinion.
- [ ] Blog/Substack-only support for quantitative claims is flagged as `overrelies_on_blog_or_substack`.

#### FR-2.6.3 Apply Triage Buckets

**Description:** Fact Check must classify each issue into a repair path.

**Acceptance Criteria:**

- [ ] Each flag is classified as fixable with existing research, generalize/remove unsupported specificity, or needs research addendum.
- [ ] Load-bearing weak-source claims are removed or sent to research addendum, not merely softened.
- [ ] The system preserves the rule: `citation exists != claim is proven`.
- [ ] Source-quality `needsResearchAddendum` flags may be passed to Fix Pass for softening or removal only; non-source-quality `needsResearchAddendum` flags are not auto-fixed because they need new evidence.

**Priority:** High

### 2.7 Fix Pass And Re-Check

#### FR-2.7.1 Apply Surgical Fixes

**Description:** The Fix Pass Agent must repair flagged issues without restarting the pipeline or rewriting unflagged sections unnecessarily.

**Acceptance Criteria:**

- [ ] Fix Pass preserves the approved thesis, article structure, editorial voice, and unflagged sections.
- [ ] Fix Pass can add date qualifiers, add citations, rephrase investment advice language, label scenario estimates, add existing counterarguments, correct instrument names, soften weakly sourced claims, generalize unsupported named examples, and remove unsupported specificity.
- [ ] Fix Pass records which fact-check flags were addressed.
- [ ] Claims marked as requiring research addendum are not silently fabricated or repaired without evidence.
- [ ] Unsupported named analysts, companies, institutions, exact spreads, counts, valuation figures, and named source attributions are removed or generalized only when the broader claim is supported by existing research.
- [ ] Weak-source quantitative claims remove exact percentages, return spreads, counts, basis points, and valuation figures unless adequate source quality exists.
- [ ] Load-bearing quantitative claims are removed or sent to research addendum; adding "unverified" or "primary data pending" is not considered a fix.
- [ ] Blog/intermediary citations must be attributed precisely and cannot be upgraded to "research suggests" or "institutional research" without direct support.
- [ ] Fix Pass logs each action as removed unsupported specificity, generalized claim, softened weak-source quant, marked source-limited, or removed claim.

**Priority:** High

#### FR-2.7.2 Re-Check Fixed Draft

**Description:** The system must run fact-checking again after the Fix Pass.

**Acceptance Criteria:**

- [ ] Re-Check produces a new `FactCheckReport`.
- [ ] The review view shows before/after issue counts.
- [ ] Remaining high-severity issues are visible before export.
- [ ] Re-Check applies the same source-quality, severity, triage, URL, and unit-conversion rules as the first fact-check pass.
- [ ] Re-Check flags unresolved issues again at the same severity when unsupported named specificity, weak-source load-bearing quantitative claims, or unsupported qualitative replacements remain.

**Priority:** High

### 2.8 Provider Integration

#### FR-2.8.1 Configure Azure AI Foundry From Environment

**Description:** The system must read model provider settings from environment variables and never require reading the real `.env` file during implementation.

**Acceptance Criteria:**

- [ ] The app supports `AZURE_FOUNDRY_ENDPOINT`, `AZURE_FOUNDRY_API_KEY`, `FOUNDRY_DEFAULT_MODEL`, `FOUNDRY_SONNET_MODEL`, `FOUNDRY_OPUS_MODEL`, `FOUNDRY_ANTHROPIC_VERSION`, and `FOUNDRY_TIMEOUT_SECONDS`.
- [ ] `example.env` documents expected variables with placeholders only.
- [ ] API keys are never printed, logged, stored in artifacts, or committed.
- [ ] Missing required provider config produces clear startup or command errors.

**Priority:** High

#### FR-2.8.2 Smoke-Test Foundry Before Full Pipeline Use

**Description:** The system must include a minimal provider smoke test before relying on Foundry for the full pipeline.

**Acceptance Criteria:**

- [ ] Smoke test sends a tiny prompt to the configured endpoint.
- [ ] Smoke test verifies endpoint path construction, headers, deployment/model identifier usage, Anthropic Messages request body shape, and response parsing.
- [ ] Smoke test confirms whether Foundry supports Anthropic-style tools such as `web_search_20250305`.
- [ ] Smoke test writes safe metadata without secrets.
- [ ] Endpoint path construction is centralized and easy to adjust.

**Priority:** High

#### FR-2.8.3 Support Role-Based Model Selection

**Description:** The Foundry client must support model selection by pipeline role.

**Acceptance Criteria:**

- [ ] Agents can use default, Sonnet, or Opus model aliases from config.
- [ ] The selected model/deployment is recorded in safe run metadata.
- [ ] Stage-specific timeout and token settings are supported.

**Priority:** Medium

### 2.9 UI, CLI, And Export

#### FR-2.9.1 Replace Browser-Only Interactions

**Description:** The Python app must replace the prototype's browser state, buttons, and clipboard actions with explicit UI or CLI behavior.

**Acceptance Criteria:**

- [ ] In-memory JS variables such as saved research, thesis, draft, and fact-check state are represented by persisted artifacts.
- [ ] Thesis approval, apply fixes, copy/export HTML, and copy/export text are exposed as FastAPI routes, UI form actions, or CLI commands.
- [ ] Review state is represented by persisted run status.
- [ ] Clipboard actions become export files.

**Priority:** High

#### FR-2.9.2 Export Final Issue

**Description:** The system must export approved or review-ready issues in portable formats.

**Acceptance Criteria:**

- [ ] The system exports `issue.html`.
- [ ] The system exports `issue.md`.
- [ ] The system can include source list and fact-check status in review output.
- [ ] Export does not require browser clipboard access.

**Priority:** High

---

## 3. Data Requirements

### 3.1 Input Data

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| market | string | Yes | Market, asset class, company, sector, or instrument being analyzed. |
| recentWindow | string | Yes | Recent period to analyze. |
| contextWindow | string | Yes | Historical comparison window. |
| readerHorizon | string | Yes | Investor time horizon for the issue. |
| readerType | string | Yes | Intended audience sophistication and perspective. |
| contrarianLean | string | No | Optional preferred contrarian posture. |
| depth | string | Yes | Research and article depth. |
| length | string/integer | Yes | Target article length or range. |
| approvedThesis | object | Yes for draft | Human-approved thesis brief. |
| draft | object | Yes for fact-check | Draft issue to inspect. |
| factCheckReport | object | Yes for fix pass | Structured issues to repair. |

### 3.2 Output Data

| Field | Type | Description |
|-------|------|-------------|
| ScopeRequest | object | Validated editorial scope. |
| ResearchBrief | object | Structured research, claims, source metadata, and retrieved evidence. |
| ThesisBrief | object | Structured editorial thesis and scenarios. |
| DraftIssue | object | Generated newsletter draft and metadata. |
| FactCheckReport | object | Flags, triage buckets, source-quality findings, and score. |
| RunArtifact | object | Metadata about one persisted stage artifact. |
| issue.html | file | HTML export for review or publishing. |
| issue.md | file | Markdown export for review, editing, or Obsidian use. |

### 3.3 Run Folder Contract

Each run should use this minimum artifact structure:

```text
runs/{run_id}/
  00_scope.json
  01_research.json
  02_thesis.json
  03_draft.json
  04_fact_check.json
  05_fixed_draft.json
  06_recheck.json
  issue.html
  issue.md
```

---

## 4. Validation Rules

| Rule ID | Description | Error Message |
|---------|-------------|---------------|
| VAL-001 | Required scope fields must be present before research starts. | Scope is incomplete. Complete required fields before running research. |
| VAL-002 | Agent outputs must parse as valid JSON for structured stages. | Agent output did not produce valid JSON for this stage. |
| VAL-003 | Parsed JSON must validate against the stage Pydantic model. | Agent output failed schema validation. |
| VAL-004 | Writer cannot run before thesis approval. | Thesis must be approved before drafting. |
| VAL-005 | Fix Pass cannot run without a fact-check report. | Fact-check report is required before applying fixes. |
| VAL-006 | Re-Check cannot run without a fixed draft. | Fixed draft is required before re-check. |
| VAL-007 | Claims with exact quantitative specificity must have adequate evidence. | Quantitative claim lacks adequate source support. |
| VAL-008 | Direct investment advice language must be flagged. | Draft contains investment advice language that must be revised. |
| VAL-009 | API keys and secrets must not be serialized to logs or artifacts. | Secret value detected in output path. |

### 4.1 JSON Retry Rule

When a model response fails JSON parsing or schema validation, the system should perform one controlled retry with validation errors included in the retry prompt. If the retry fails, the stage must fail visibly and preserve raw output for debugging.

---

## 5. Error Handling

| Category | Description | Response |
|----------|-------------|----------|
| Input Error | Missing or invalid operator input. | Show validation details and do not run the next stage. |
| Provider Configuration Error | Missing endpoint, model, API key, or invalid provider setting. | Fail startup or command with clear config error; do not expose secret values. |
| Provider Request Error | Foundry or search API request fails, times out, or returns an unexpected shape. | Save safe metadata, mark the stage failed, and allow retry. |
| Provider Capability Error | Foundry does not support expected tools such as web search. | Fall back to external search abstraction if configured, or fail with setup guidance. |
| Parsing Error | Model response is not valid JSON or does not match schema. | Retry once, then save raw output and fail the stage visibly. |
| Source Verification Error | Claim cannot be verified against stored evidence. | Flag the claim for removal, generalization, or research addendum. |
| Export Error | HTML or Markdown export cannot be written. | Report file path and error, leaving prior artifacts intact. |

---

## 6. Non-Functional Requirements

### 6.1 Security

- The system must not read, print, modify, or commit the real `.env` file.
- Secrets must come from environment variables at runtime.
- Logs and artifacts must redact API keys and full secret values.
- Browser-rendered draft HTML should be treated as untrusted until sanitized in a production implementation.

### 6.2 Reliability

- The pipeline must persist each completed stage before starting the next stage.
- A failed stage must not delete earlier artifacts.
- Provider calls should use explicit timeouts.
- The app should support mocked provider clients for local tests.

### 6.3 Maintainability

- Business contracts must use Pydantic models.
- Prompt templates must live outside core orchestration logic.
- Provider code must be isolated from agent business logic.
- Search/retrieval must be isolated so provider choice can change without rewriting the Research Agent.
- Code quality should be tracked with Radon after implementation.

### 6.4 Testability

- Unit tests must cover config loading with fake environment variables.
- Unit tests must cover prompt rendering.
- Unit tests must cover JSON parsing and validation.
- Unit tests must cover fact-check triage rules.
- Unit tests must cover fix-pass filtering behavior.
- Azure Foundry integration tests must be opt-in because they require real credentials.
- External search integration tests must use mocked API calls first.

---

## 7. Assumptions and Constraints

### 7.1 Assumptions

- The initial backend will be Python.
- The initial API/UI approach will use FastAPI or a minimal CLI if that provides a faster vertical slice.
- Azure AI Foundry will be the primary model provider.
- Foundry may wrap Anthropic endpoints differently than the public Anthropic API.
- Foundry may not support Anthropic web search tools.
- JSON artifacts are sufficient before introducing a database.

### 7.2 Constraints

- The system must avoid direct investment advice.
- The real `.env` file must not be read, modified, printed, or committed.
- Claims should not be treated as verified merely because a citation exists.
- Load-bearing weak-source claims must be removed or sent to research addendum, not merely softened.
- Any live Foundry test must be explicitly opt-in and safe with respect to secrets.

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-05-11 | Cursor Agent | Replaced template with Python rewrite functional requirements based on the approved plan. |
