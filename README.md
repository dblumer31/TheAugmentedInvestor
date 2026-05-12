# The Augmented Investor

Proof-of-concept editorial pipeline for **The Augmented Investor**, a newsletter at the intersection of AI, finance, markets, and investing.

The current implementation is a Python rewrite of the original single-file HTML prototype.
The HTML file remains useful as workflow reference material, while the Python package now
provides persisted run artifacts, agent modules, CLI operations, and file exports.

## Current Python App

Primary package:

```text
src/augmented_investor/
```

The Python app runs the same editorial workflow with explicit stage artifacts:

```text
Scope -> Research -> Thesis Gate -> Write -> Fact Check -> Fix Pass -> Re-Check -> Export
```

Run artifacts are written under `runs/{run_id}/` and include JSON for each stage plus
`issue.html` and `issue.md` after export.

### Setup

Install runtime and development dependencies:

```powershell
python -m pip install -r requirements.txt
python -m pip install -r requirements-dev.txt
```

Set `PYTHONPATH` when running from the project root:

```powershell
$env:PYTHONPATH = "src"
```

The app reads provider settings from environment variables and can also use a local `.env`
file that remains outside source control.

### CLI Workflow

Create a scope JSON file, then create a run:

```powershell
python -m augmented_investor.cli create-run --scope-file .\scope.json
```

Run the live provider-backed stages:

```powershell
python -m augmented_investor.cli run-research <run_id>
python -m augmented_investor.cli run-thesis <run_id>
python -m augmented_investor.cli approve-thesis <run_id>
python -m augmented_investor.cli write-draft <run_id>
python -m augmented_investor.cli fact-check <run_id>
python -m augmented_investor.cli apply-fix-pass <run_id>
python -m augmented_investor.cli recheck <run_id>
```

Review and export:

```powershell
python -m augmented_investor.cli review-run <run_id>
python -m augmented_investor.cli export-run <run_id>
```

The export command writes `issue.html` and `issue.md` to the run folder.

### Tests And Quality

Run the default test suite:

```powershell
python -m pytest
```

Run the live Foundry smoke test only when credentials are intentionally configured:

```powershell
$env:RUN_LIVE_FOUNDRY_TESTS = "1"
python -m pytest tests/integration/test_foundry_smoke_test.py
python -m augmented_investor.cli foundry-smoke-test
```

Run Radon quality checks:

```powershell
python -m radon cc -a -s src/
python -m radon mi -s src/
```

Full test reports are stored in `DOCS/Test Reports/`. Radon reports are stored in
`DOCS/Radon Checks/`.

## Legacy HTML Prototype

Primary file:

```text
augmented-investor-v3 (9).html
```

The prototype runs an AI-assisted editorial workflow:

```text
Scope -> Research -> Thesis Gate -> Write -> Fact Check -> Fix Pass -> Re-Check -> Review
```

The goal is not just to generate a newsletter draft. The goal is to create an inspectable editorial desk where agents research, form a thesis, write, audit, and repair the issue before human approval.

## Agent Flow

### 1. Scope

The user enters a rough market question and chooses:

- Market or asset class
- Recent window
- Historical context window
- Reader horizon
- Reader type
- Contrarian lean
- Depth and length

The scoping step keeps vague prompts from turning into vague market summaries.

### 2. Research Agent

The Research Agent returns structured evidence rather than article prose.

It asks for:

- Market snapshot
- Prior trend
- What changed
- Evidence for the thesis
- Evidence against the thesis
- Possible mispricing
- Source list
- Recommended angle

The research schema emphasizes source, date, confidence, and instrument precision.

It also classifies source quality for each claim:

- `primary_market_data`
- `company_filing_or_ir`
- `official_institutional_report`
- `reputable_financial_media`
- `syndicated_market_article`
- `blog_or_substack`
- `unknown`

Each claim should identify whether the source directly supports the exact claim, whether quoted evidence is available, and whether confidence is high, medium, or low.

### 3. Thesis Agent

The Thesis Agent turns the research briefing into an editorial argument.

It produces:

- Central thesis
- Thesis basis
- Bull case
- Base case
- Bear case
- Scenario math, if any
- What investors may be mispricing
- Contrarian test
- Confidence rationale
- Newsletter angle

The human editor must approve the thesis before the Writer Agent runs.

### 4. Writer Agent

The Writer Agent drafts the newsletter from the approved thesis and selected research facts.

It is instructed to:

- Write in the newsletter voice
- Cite evidence inline
- Avoid direct investment advice
- Label projections as scenario estimates
- End with an investable question, not a recommendation

### 5. Fact Check Agent

The Fact Check Agent compares the draft against the research JSON and now also performs source-quality verification.

It checks:

- Whether the cited source exists.
- Whether the source directly supports the exact claim.
- Whether the source quality is appropriate for the claim type.
- Whether the claim is primary data, interpretation, scenario math, or editorial extrapolation.
- Whether the draft overstates a medium- or low-confidence source.

It flags:

- Unsupported numbers
- Missing URLs
- Instrument imprecision
- Overconfident projections
- Missing counterarguments
- Investment advice language
- Unlabeled scenario math
- Weak source for quantitative claims
- Source does not support claim
- Source quality mismatch
- Unverified market return
- Overreliance on blog or Substack
- Missing exact quote
- Citation present but claim unproven

It separates issues into three triage buckets:

- Fixable with existing research
- Generalize or remove unsupported specificity
- Needs research addendum

Source-quality metadata includes:

- `claimType`
- `requiredSourceQuality`
- `actualSourceQuality`
- `verificationStatus`

The key principle is:

```text
citation exists != claim is proven
```

### 6. Fix Pass Agent

The Fix Pass Agent applies surgical fixes to flagged issues without restarting the pipeline.

It should preserve:

- Approved thesis
- Article structure
- Editorial voice
- Unflagged sections

It handles fixes such as:

- Adding date qualifiers
- Adding citations
- Rephrasing investment advice language
- Labeling scenario estimates
- Adding missing counterarguments already present in the research JSON
- Correcting instrument names
- Softening market-return or valuation claims backed only by weak sources
- Generalizing unsupported named examples when the broader claim is supported
- Removing unsupported specificity that cannot be repaired without new research

After the Fix Pass, the Fact Check Agent runs again and the review badge shows before/after issue counts.

### 7. Review

The human editor reviews the final draft, fact-check status, and source list.

Available actions:

- Approve
- Start over
- Copy HTML
- Copy text

## Running The Legacy POC

Open the HTML file directly in a browser:

```text
augmented-investor-v3 (9).html
```

The browser-based proof of concept is retained for workflow comparison, not production deployment.

## Current Limitations

- The Python CLI is the current runnable implementation; the HTML prototype is legacy reference material.
- The first interface is CLI-based; a FastAPI or web UI can be added later.
- Addendum flags are surfaced, but targeted research addendum search is not fully implemented.
- Model-generated article HTML is rendered into the page, which should be sanitized in a production implementation.

## Next Steps

Recommended next improvements:

- Add targeted Research Addendum support for unsupported claims.
- Add primary market-data lookup for market-return and valuation claims.
- Add a FastAPI or web UI on top of the existing artifact-backed pipeline.
- Add issue history.

Recommended production direction:

```text
Frontend -> Backend Orchestrator -> Agent Modules -> Stored Run Artifacts -> Export/Publish
```

Likely backend options:

- Python for fast agent experimentation.
- C# / ASP.NET Core for a more durable .NET application.

## Product Principle

The article is the final artifact, but the real value is the reasoning trail behind it.

The strongest version of this product is:

> An AI-assisted investor brief that shows its reasoning, surfaces the market narrative, challenges it, and turns it into a clear investable question.
