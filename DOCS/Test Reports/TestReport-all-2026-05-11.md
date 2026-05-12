# Test Report

**Date:** 2026-05-11  
**Framework:** pytest  
**Scope:** all  
**Trigger:** US-012 final verification  
**Command:** `python -m pytest`

## Summary

| Metric | Count |
|--------|-------|
| Total | 84 |
| Passed | 83 |
| Failed | 0 |
| Skipped | 1 |
| Errors | 0 |
| Duration | 1.15s |
| **Result** | **PASS** |

## Failed Tests

None - all tests passed.

## Skipped Tests

| Test | Reason |
|------|--------|
| `tests/integration/test_foundry_smoke_test.py` | Live Foundry tests disabled. Set `RUN_LIVE_FOUNDRY_TESTS=1`. |

## Raw Output

<details>
<summary>Full test output</summary>

```text
============================= test session starts =============================
platform win32 -- Python 3.13.2, pytest-8.4.2, pluggy-1.6.0
rootdir: C:\personal\TheAugmentedInvestor
plugins: anyio-4.9.0, langsmith-0.3.44, asyncio-0.26.0, cov-7.0.0, httpx-0.35.0, mock-3.15.1
asyncio: mode=Mode.STRICT, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collected 84 items

tests\integration\test_foundry_smoke_test.py s                           [  1%]
tests\integration\test_mock_agent_pipeline_flow.py .                     [  2%]
tests\integration\test_mock_pipeline_flow.py .                           [  3%]
tests\unit\test_artifact_store.py ....                                   [  8%]
tests\unit\test_cli.py ..                                                [ 10%]
tests\unit\test_config.py .....                                          [ 16%]
tests\unit\test_exporters.py ..                                          [ 19%]
tests\unit\test_external_search_client.py .......                        [ 27%]
tests\unit\test_fact_check_agent.py ..                                   [ 29%]
tests\unit\test_fix_pass_agent.py ..                                     [ 32%]
tests\unit\test_fix_pass_rules.py ..                                     [ 34%]
tests\unit\test_foundry_client.py ...                                    [ 38%]
tests\unit\test_foundry_smoke_test.py .....                              [ 44%]
tests\unit\test_json_parser.py .....                                     [ 50%]
tests\unit\test_models.py .......                                        [ 58%]
tests\unit\test_operator_interface.py ...                                [ 61%]
tests\unit\test_orchestrator.py .......                                  [ 70%]
tests\unit\test_recheck_flow.py ..                                       [ 72%]
tests\unit\test_research_agent.py ...                                    [ 76%]
tests\unit\test_secret_redaction.py .                                    [ 77%]
tests\unit\test_source_quality_rules.py ...............                  [ 95%]
tests\unit\test_thesis_agent.py ..                                       [ 97%]
tests\unit\test_writer_agent.py ..                                       [100%]

======================== 83 passed, 1 skipped in 1.15s ========================
```

</details>
