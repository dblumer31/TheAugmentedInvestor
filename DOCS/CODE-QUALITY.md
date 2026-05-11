# Code Quality Guide - Complexity Analysis

This guide explains how to measure and manage code complexity using static analysis tools, with a focus on Radon for Python.

For the project policies that govern when complexity checks are required and what thresholds apply, see:

- `DOCS/STORY_GUIDE.md` -- Post-Story Quality Gate and Definition of Done
- `DOCS/process-executive-summary.md` -- Code Complexity checklist under Definition of Done
- `DOCS/CodeQualityChecks/TEMPLATE.md` -- Per-story assessment format and threshold policy

---

## What is Radon?

Radon is a Python tool that computes source code metrics. It provides:

- **Cyclomatic Complexity (CC)** -- Measures the number of independent paths through a function. Higher complexity means more branches, more test cases needed, and higher risk of bugs.
- **Maintainability Index (MI)** -- A composite score (0-100) combining lines of code, complexity, and Halstead volume. Higher is better.

Radon also offers Halstead metrics (`radon hal`) and raw line counts (`radon raw`), but CC and MI are the two used in this project's quality process.

---

## Installation

### Install Radon

```bash
pip install radon
```

### Add to Dev Dependencies

If your project uses a requirements file for development tools, add radon there:

```
# requirements-dev.txt
radon
```

Then install with:

```bash
pip install -r requirements-dev.txt
```

### Verify Installation

```bash
radon --version
```

---

## Running Radon

### Cyclomatic Complexity

The `radon cc` command analyzes functions, methods, and classes for branching complexity.

**Basic usage -- all Python files in a directory:**

```bash
radon cc -a -s src/
```

| Flag | Purpose |
|------|---------|
| `-a` | Show the average complexity at the end |
| `-s` | Show the complexity score next to each grade |
| `-n C` | Only show results at grade C or worse (filter out low-complexity code) |
| `-j` | Output as JSON (useful for automation) |

**Examples:**

```bash
# Analyze everything in src/ with averages and scores
radon cc -a -s src/

# Show only functions graded C or worse
radon cc -a -s -n C src/

# Analyze a single file
radon cc -a -s src/data_parser.py

# Analyze all .py files in the current directory (non-recursive)
radon cc -a -s *.py
```

**Sample output:**

```
src/data_parser.py
    F 12:0 parse_file - B (8)
    F 45:0 validate_row - A (3)
    F 78:0 transform_record - C (14)

3 blocks (classes, functions, methods) analyzed.
Average complexity: B (8.3)
```

Each line shows: file, type (F=function, M=method, C=class), line number, name, grade, and score.

---

### Maintainability Index

The `radon mi` command scores each file on a 0-100 scale for overall maintainability.

**Basic usage:**

```bash
radon mi -s src/
```

| Flag | Purpose |
|------|---------|
| `-s` | Show the numeric score next to each grade |
| `-j` | Output as JSON |
| `-n C` | Only show files at grade C or worse |

**Examples:**

```bash
# All files in src/ with scores
radon mi -s src/

# Only show files that need attention (grade B or C)
radon mi -s -n B src/

# Single file
radon mi -s src/data_parser.py
```

**Sample output:**

```
src/data_parser.py - A (65.42)
src/db_operations.py - A (72.10)
src/main.py - B (18.55)
```

---

### Other Radon Commands

These are less commonly used in this project but available for deeper analysis:

| Command | What It Measures |
|---------|-----------------|
| `radon hal src/` | Halstead metrics (volume, difficulty, effort) |
| `radon raw src/` | Raw line counts (LOC, LLOC, SLOC, comments, blanks) |

---

## Interpreting Results

### Cyclomatic Complexity Grades

| Grade | Score Range | Meaning |
|-------|-------------|---------|
| A | 1-5 | Simple, low risk |
| B | 6-10 | Moderate complexity |
| C | 11-20 | Complex, moderate risk |
| D | 21-30 | Very complex, high risk |
| E | 31-40 | Very high complexity |
| F | 41+ | Untestable, extreme risk |

### Maintainability Index Grades

| Grade | Score Range | Meaning |
|-------|-------------|---------|
| A | 20-100 | Very maintainable |
| B | 10-19 | Moderately maintainable |
| C | 0-9 | Difficult to maintain |

For the project thresholds that determine what grades require action, see the policy in `DOCS/CodeQualityChecks/TEMPLATE.md` and the Definition of Done checklist in `DOCS/process-executive-summary.md`.

---

## Where to Store Results

Radon reports are stored in the `DOCS/Radon Checks/` directory. Create this directory if it does not exist.

```
DOCS/
└── Radon Checks/
    ├── Radon-baseline-2026-02-20.md
    ├── Radon-post-US011.md
    ├── Radon-pre-refactor.md
    └── ...
```

### File Naming Convention

Format: `Radon-{trigger-label}.md`

| Trigger | Example Filename |
|---------|-----------------|
| After implementing a story | `Radon-post-US011.md` |
| Baseline snapshot | `Radon-baseline-2026-02-20.md` |
| Before a refactor | `Radon-pre-refactor.md` |
| After a refactor | `Radon-post-refactor.md` |
| Periodic audit | `Radon-audit-2026-Q1.md` |

---

## Generating a Report

Follow these steps to produce a complete Radon report.

### Step 1: Run Both Commands

```bash
radon cc -a -s src/
radon mi -s src/
```

Replace `src/` with the directory or files relevant to your analysis.

### Step 2: Create the Report File

Create a new file in `DOCS/Radon Checks/` using the naming convention above.

### Step 3: Fill In the Report

Use this structure:

```markdown
# Radon Complexity Analysis - {Trigger Label}

**Date:** YYYY-MM-DD
**Trigger:** {Description of what prompted this analysis}

---

## Cyclomatic Complexity by Function

| File | Function | Grade | Score |
|------|----------|-------|-------|
| `file.py` | `function_name` | **X** | NN |

**Average Complexity: X (N.N)**

---

## Maintainability Index by File

| File | Grade | Score |
|------|-------|-------|
| `file.py` | X | NN.NN |

---

## Grading Scale Reference

### Cyclomatic Complexity

| Grade | Score Range | Meaning |
|-------|-------------|---------|
| A | 1-5 | Simple, low risk |
| B | 6-10 | Moderate complexity |
| C | 11-20 | Complex, moderate risk |
| D | 21-30 | Very complex, high risk |
| E | 31-40 | Very high complexity |
| F | 41+ | Untestable, extreme risk |

### Maintainability Index

| Grade | Score Range | Meaning |
|-------|-------------|---------|
| A | 20-100 | Very maintainable |
| B | 10-19 | Moderately maintainable |
| C | 0-9 | Difficult to maintain |

---

## Summary

- **Total Functions Analyzed:** N
- **Average Complexity:** X (N.N)
- **Action Items:** List any functions with grade C or worse

---

## Raw Radon Output

### Cyclomatic Complexity (`radon cc -a -s`)

{paste raw output here}

### Maintainability Index (`radon mi -s`)

{paste raw output here}
```

### Report Tips

- Sort the Cyclomatic Complexity table by score, highest first.
- Bold any grades of C, D, E, or F to make them stand out.
- For large codebases, group low-complexity functions (grade A, score 1-3) as "Others (N functions)" to keep the table readable.
- Always include the raw output at the bottom for reference.

For per-story quality assessments (not full Radon reports), use the template in `DOCS/CodeQualityChecks/TEMPLATE.md`.

---

## Where Complexity Checks Fit in the SDLC

Complexity analysis connects to several points in the development workflow. The enforcement details live in the linked documents.

| Workflow Step | What Happens | Reference |
|---------------|-------------|-----------|
| Post-story quality gate | Assess complexity of changed code before marking a story done | `DOCS/STORY_GUIDE.md` -- Post-Story Quality Gate |
| Pre-PR checklist | Verify no high-complexity functions introduced | `DOCS/process-executive-summary.md` -- Code Complexity under Definition of Done |
| Periodic audit | Run a full Radon analysis across the codebase | Team decision / sprint cadence |
| Pre/post refactoring | Capture baseline before refactoring, then measure improvement after | Compare two report files in `DOCS/Radon Checks/` |

---

## Other Languages

Radon is Python-specific. For other languages, use equivalent static analysis tools:

| Language | Tools | Notes |
|----------|-------|-------|
| Python | Radon | This guide |
| JavaScript / TypeScript | ESLint, SonarQube | ESLint for linting + complexity rules; SonarQube for broader analysis |
| Java / C# | SonarQube, PMD | SonarQube provides complexity metrics; PMD focuses on code patterns |
| Go | golangci-lint | Includes cyclomatic complexity via the `gocyclo` linter |

The grading thresholds and storage conventions in this guide apply regardless of tool. Adapt the commands but follow the same report structure and store results in `DOCS/Radon Checks/` (or an equivalent `DOCS/CodeQualityChecks/` directory for non-Python projects).

---

## Quick Reference

| Command | Description |
|---------|-------------|
| `pip install radon` | Install Radon |
| `radon --version` | Verify installation |
| `radon cc -a -s src/` | Cyclomatic complexity with averages and scores |
| `radon cc -a -s -n C src/` | Show only grade C or worse |
| `radon mi -s src/` | Maintainability index with scores |
| `radon mi -s -n B src/` | Show only grade B or worse |
| `radon cc -a -s -j src/` | CC output as JSON |
| `radon hal src/` | Halstead metrics |
| `radon raw src/` | Raw line counts |

---

## Instructions for AI Assistants

This section explains how Cursor and other AI assistants should use this guide together with the `radon-analysis` skill.

### How This Guide and the Skill Work Together

- **This guide** (`DOCS/CODE-QUALITY.md`) is the reference for grading scales, command syntax, report structure, and storage conventions. Treat it as the source of truth for "what goes in a report" and "what the grades mean."
- **The radon-analysis skill** (`radon-analysis` in Cursor skills) is the automation procedure. It tells you the step-by-step execution: run commands, parse output, generate the report file. Follow the skill's steps when performing an analysis.
- If there is a conflict between this guide and the skill, follow this guide for grading scales and report structure, and follow the skill for execution steps.

### When to Run a Radon Analysis

Run the `radon-analysis` skill when:

- The user asks for a complexity analysis, code quality check, or Radon report
- A story implementation is complete and the post-story quality gate requires a complexity assessment (see `DOCS/STORY_GUIDE.md` -- Post-Story Quality Gate)
- The user is preparing a pull request and the Definition of Done requires a static analysis check (see `DOCS/process-executive-summary.md` -- Code Complexity checklist)
- The user asks for a baseline or before/after comparison around a refactor

### Step-by-Step: Running an Analysis with the Skill

1. **Get the trigger label** from the user (e.g., "Post US-011", "Pre-refactor baseline"). If not provided, ask for one.
2. **Get the target scope** from the user (specific files, a directory, or default to `*.py` in the project root).
3. **Verify Radon is installed.** If `radon --version` fails, install it with `pip install radon`.
4. **Follow the skill's analysis steps:** run `radon cc -a -s` and `radon mi -s` against the target scope.
5. **Generate the report** in `DOCS/Radon Checks/` using the naming convention `Radon-{trigger-label}.md`.
6. **Use the report template** from the "Generating a Report" section of this guide. The report must include all sections: CC table, MI table, Grading Scale Reference, Summary, and Raw Output.
7. **Apply the formatting rules:**
   - Sort CC table by score, highest first
   - Bold grades C, D, E, and F
   - Group low-complexity functions (grade A, score 1-3) as "Others (N functions)" for readability
   - Always include the raw command output at the bottom
8. **Flag action items** for any functions or files that exceed thresholds:
   - CC grade D (21-30): should be refactored
   - CC grade E (31-40): must be refactored
   - CC grade F (41+): must be refactored, untestable
   - MI grade C (0-9): file needs cleanup

### What Not to Do

- Do not modify source code as part of a Radon analysis. The analysis is read-only.
- Do not delete or overwrite previous report files. Each analysis is a point-in-time snapshot.
- Do not skip the raw output section in the report.
- Do not invent or estimate scores. Run the actual commands and use the real output.

### Per-Story Quality Assessments

For lightweight, per-story complexity checks (not full Radon reports), use the template in `DOCS/CodeQualityChecks/TEMPLATE.md` instead. That template is for quick assessments embedded in the story workflow. Full Radon reports in `DOCS/Radon Checks/` are for deeper or broader analyses.

### Related Documents

| Document | Role |
|----------|------|
| `DOCS/CODE-QUALITY.md` | This guide -- grading scales, commands, report format, storage |
| `radon-analysis` skill | Automation procedure for running analysis and generating reports |
| `DOCS/STORY_GUIDE.md` | Post-Story Quality Gate -- when complexity checks are required |
| `DOCS/process-executive-summary.md` | Definition of Done -- code complexity checklist |
| `DOCS/CodeQualityChecks/TEMPLATE.md` | Per-story quality assessment template |
| `DOCS/SKILLS_SUMMARY.md` | Full list of available Cursor skills |
