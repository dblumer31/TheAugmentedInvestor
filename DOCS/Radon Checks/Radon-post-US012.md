# Radon Complexity Analysis - Post US-012

**Date:** 2026-05-11  
**Trigger:** US-012 final quality gate

---

## Cyclomatic Complexity by Function

| File | Function | Grade | Score |
|------|----------|-------|-------|
| `src/augmented_investor/foundry_client.py` | `_extract_text` | B | 7 |
| `src/augmented_investor/pipeline/fact_check_postprocess.py` | `_overall_source_quality` | B | 7 |
| `src/augmented_investor/pipeline/fix_pass_rules.py` | `action_label_for_flag` | B | 7 |
| `src/augmented_investor/foundry_client.py` | `FoundryClient.smoke_test` | B | 6 |
| `src/augmented_investor/pipeline/source_quality_rules.py` | `classify_source_quality` | B | 6 |
| `src/augmented_investor/cli.py` | `_run_foundry_smoke_test` | A | 5 |
| `src/augmented_investor/foundry_client.py` | `normalize_messages_endpoint` | A | 5 |
| `src/augmented_investor/foundry_client.py` | `_tool_support_from_response` | A | 5 |
| `src/augmented_investor/pipeline/fact_check_postprocess.py` | `overall_score` | A | 5 |
| `src/augmented_investor/pipeline/source_quality_rules.py` | `_scenario_label_flag` | A | 5 |
| `src/augmented_investor/pipeline/source_quality_rules.py` | `_institutional_metadata_flag` | A | 5 |
| `src/augmented_investor/exporters/html_exporter.py` | `_source_items` | A | 5 |
| `src/augmented_investor` | Others | A | 1-4 |

**Average Complexity: A (1.96)**

---

## Maintainability Index by File

| File | Grade | Score |
|------|-------|-------|
| `src/augmented_investor/app.py` | A | 100.00 |
| `src/augmented_investor/cli.py` | A | 36.97 |
| `src/augmented_investor/config.py` | A | 58.85 |
| `src/augmented_investor/external_search_client.py` | A | 57.46 |
| `src/augmented_investor/foundry_client.py` | A | 28.99 |
| `src/augmented_investor/operator_interface.py` | A | 46.81 |
| `src/augmented_investor/agents/fact_check_agent.py` | A | 49.11 |
| `src/augmented_investor/agents/fix_pass_agent.py` | A | 52.16 |
| `src/augmented_investor/agents/research_agent.py` | A | 41.39 |
| `src/augmented_investor/agents/thesis_agent.py` | A | 53.13 |
| `src/augmented_investor/agents/writer_agent.py` | A | 52.70 |
| `src/augmented_investor/exporters/html_exporter.py` | A | 53.95 |
| `src/augmented_investor/exporters/markdown_exporter.py` | A | 49.80 |
| `src/augmented_investor/models/common.py` | A | 60.65 |
| `src/augmented_investor/models/draft.py` | A | 54.94 |
| `src/augmented_investor/models/fact_check.py` | A | 46.43 |
| `src/augmented_investor/models/research.py` | A | 35.66 |
| `src/augmented_investor/models/scope.py` | A | 53.79 |
| `src/augmented_investor/models/thesis.py` | A | 60.92 |
| `src/augmented_investor/pipeline/artifact_store.py` | A | 35.39 |
| `src/augmented_investor/pipeline/fact_check_postprocess.py` | A | 36.54 |
| `src/augmented_investor/pipeline/fix_pass_rules.py` | A | 47.26 |
| `src/augmented_investor/pipeline/json_parser.py` | A | 46.90 |
| `src/augmented_investor/pipeline/orchestrator.py` | A | 44.90 |
| `src/augmented_investor/pipeline/source_quality_rules.py` | A | 28.96 |

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

- **Total Blocks Analyzed:** 260
- **Average Complexity:** A (1.96)
- **Maintainability:** All analyzed files are grade A.
- **Action Items:** None. No functions grade C or worse and no files have MI below A.

---

## Raw Radon Output

### Cyclomatic Complexity (`python -m radon cc -a -s src/`)

```text
src\augmented_investor\cli.py
    F 128:0 _run_foundry_smoke_test - A (5)
    F 198:0 _run_export_run - A (3)
    F 46:0 main - A (2)
    F 60:0 _handler_for_command - A (2)
    F 94:0 _add_operator_commands - A (2)
    F 153:0 _run_create_run - A (2)
    F 165:0 _run_review_run - A (2)
    F 176:0 _run_approve_thesis - A (2)
    F 187:0 _run_reject_thesis - A (2)
    F 209:0 _run_live_stage - A (2)
    F 265:0 _json_ready - A (2)
    F 76:0 _build_parser - A (1)
    F 122:0 _add_runs_dir_argument - A (1)
    F 223:0 _build_live_orchestrator - A (1)
    F 245:0 _dispatch_stage - A (1)
    F 259:0 _store - A (1)
    F 273:0 _print_json - A (1)
    F 279:0 _print_error - A (1)
    F 286:0 _print_request_summary - A (1)
src\augmented_investor\foundry_client.py
    F 377:0 _extract_text - B (7)
    M 127:4 FoundryClient.smoke_test - B (6)
    F 288:0 normalize_messages_endpoint - A (5)
    F 323:0 _tool_support_from_response - A (5)
    C 25:0 FoundrySmokeTestError - A (4)
    C 43:0 FoundryProviderError - A (4)
    M 167:4 FoundryClient.send_message - A (4)
    M 253:4 FoundryClient.model_for_role - A (4)
src\augmented_investor\pipeline\fact_check_postprocess.py
    F 218:0 _overall_source_quality - B (7)
    F 91:0 overall_score - A (5)
    F 48:0 build_draft_language_flags - A (4)
    F 75:0 summarize_flags - A (4)
    F 192:0 _looks_like_unlabeled_scenario - A (4)
src\augmented_investor\pipeline\fix_pass_rules.py
    F 43:0 action_label_for_flag - B (7)
    F 30:0 partition_fixable_flags - A (3)
src\augmented_investor\pipeline\source_quality_rules.py
    F 38:0 classify_source_quality - B (6)
    F 182:0 _scenario_label_flag - A (5)
    F 214:0 _institutional_metadata_flag - A (5)
    F 85:0 has_source_citation - A (4)
    F 110:0 required_source_quality - A (4)
    F 155:0 _inadequate_source_flag - A (4)

260 blocks (classes, functions, methods) analyzed.
Average complexity: A (1.9615384615384615)
```

### Maintainability Index (`python -m radon mi -s src/`)

```text
src\augmented_investor\app.py - A (100.00)
src\augmented_investor\cli.py - A (36.97)
src\augmented_investor\config.py - A (58.85)
src\augmented_investor\external_search_client.py - A (57.46)
src\augmented_investor\foundry_client.py - A (28.99)
src\augmented_investor\operator_interface.py - A (46.81)
src\augmented_investor\__init__.py - A (100.00)
src\augmented_investor\agents\fact_check_agent.py - A (49.11)
src\augmented_investor\agents\fix_pass_agent.py - A (52.16)
src\augmented_investor\agents\research_agent.py - A (41.39)
src\augmented_investor\agents\thesis_agent.py - A (53.13)
src\augmented_investor\agents\writer_agent.py - A (52.70)
src\augmented_investor\agents\__init__.py - A (100.00)
src\augmented_investor\exporters\html_exporter.py - A (53.95)
src\augmented_investor\exporters\markdown_exporter.py - A (49.80)
src\augmented_investor\exporters\__init__.py - A (100.00)
src\augmented_investor\models\common.py - A (60.65)
src\augmented_investor\models\draft.py - A (54.94)
src\augmented_investor\models\fact_check.py - A (46.43)
src\augmented_investor\models\research.py - A (35.66)
src\augmented_investor\models\run_artifact.py - A (100.00)
src\augmented_investor\models\scope.py - A (53.79)
src\augmented_investor\models\thesis.py - A (60.92)
src\augmented_investor\models\__init__.py - A (100.00)
src\augmented_investor\pipeline\artifact_store.py - A (35.39)
src\augmented_investor\pipeline\fact_check_postprocess.py - A (36.54)
src\augmented_investor\pipeline\fix_pass_rules.py - A (47.26)
src\augmented_investor\pipeline\json_parser.py - A (46.90)
src\augmented_investor\pipeline\orchestrator.py - A (44.90)
src\augmented_investor\pipeline\source_quality_rules.py - A (28.96)
src\augmented_investor\pipeline\__init__.py - A (100.00)
```
