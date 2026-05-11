# The Augmented Investor

Proof-of-concept editorial pipeline for **The Augmented Investor**, a newsletter at the intersection of AI, finance, markets, and investing.

The current build is a single-file HTML prototype that tests the agent workflow before committing to a backend, database, or production app structure.

## Current Prototype

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

## Running The POC

Open the HTML file directly in a browser:

```text
augmented-investor-v3 (9).html
```

This is currently a browser-based proof of concept. It is intended for workflow testing, not production deployment.

## Current Limitations

- The prototype is still a single HTML file.
- It calls model APIs directly from browser code.
- It does not persist runs between sessions.
- It does not yet have a true backend orchestrator.
- It does not save research, thesis, draft, fact-check, and fix-pass artifacts to disk.
- Addendum flags are surfaced, but targeted research addendum search is not fully implemented.
- Source-quality scoring is prompt-driven and should still be treated as advisory until backed by deterministic source retrieval or stored source excerpts.
- Model-generated article HTML is rendered into the page, which should be sanitized in a production implementation.

## Next Steps

Recommended next POC improvements:

- Add a collapsible Research Brief panel.
- Add a visible Thesis Brief panel after approval.
- Add targeted Research Addendum support for unsupported claims.
- Add saved source excerpts so the Fact Check Agent can compare draft claims against exact retrieved text.
- Add primary market-data lookup for market-return and valuation claims.
- Save each run as JSON artifacts.
- Add export to Markdown for Obsidian.
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
