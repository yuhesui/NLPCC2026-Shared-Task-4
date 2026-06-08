# Implementation Log: prompt09 - news_overlay_verify_fix

**Created:** 2026-06-05 14:30:51

## Summary

Verified and fixed transformer News Overlay grid/cache/status issues: aligned bounded grid date tensors, corrected N3 component-proxy evidence reporting, reran targeted tests and offline/proxy checks.

## Files Changed

src/nlpcc/news_overlay/grid_evaluator.py,tests/test_nlpcc/test_news_overlay/test_scaffold.py,docs/news_overlay/grid_search_table.md,docs/news_overlay/method_table.md,outputs/reports/news_overlay/prompt01_11/reference/transformer_method_status.csv,outputs/reports/news_overlay/prompt01_11/reference/grid_search_status_table.csv,outputs/reports/news_overlay/prompt01_11/reference/prompt09_error_inventory.csv,outputs/reports/news_overlay/prompt01_11/reference/prompt09_fix_log.csv,outputs/reports/news_overlay/prompt01_11/reference/prompt09_rerun_status.csv,outputs/reports/news_overlay/prompt01_11/progress/progress_09_verify_fix_transformer_errors.md,outputs/reports/news_overlay/prompt01_11/presented/prompt09_verify_fix_transformer_errors.md

## Tests / Checks

python -B -m pytest tests\\test_nlpcc\\test_news_overlay\\test_scaffold.py::test_prompt09_grid_evaluator_aligns_selected_date_subset -q; python -B -m pytest tests\\test_nlpcc\\test_news_overlay\\test_scaffold.py -q; python -m nlpcc.news_overlay check-models --offline --device cpu --batch-size 2; python -m nlpcc.news_overlay.grid_evaluator --grid configs\\news_overlay\\grids\\mandatory_core_grid.csv --data-root data\\train_2024 --output-dir outputs\\reports\\news_overlay\\prompt01_11\\progress\\prompt09_smoke --cache-dir .var\\news_overlay_prompt01_11\\cache\\prompt09_smoke --trace-dir .var\\news_overlay_prompt01_11\\grid_runs\\prompt09_smoke --period 2024_prompt09_smoke --max-dates 2 --device cpu --batch-size 2 --proxy-mode --include-shuffled --run-id G10B; python -m nlpcc.news_overlay check-models --offline --device auto --batch-size 2 --proxy-mode; git diff -- configs\\preserved_candidates configs\\prompt18_final_candidates.json NLPCC_tasks\\agent_platform\\agents\\build_agent.py

## Caveats

No approved local transformer model assets are configured, so real local transformer inference remains blocked_missing_local_model. Proxy-mode evidence is research-only. Full ablation sweeps, frozen 2025 transformer evaluation, and official-server parity remain open. Existing Windows pytest cache permission warning persists but tests pass.

## Artifacts

- `outputs/reports/news_overlay/prompt01_11/reference/prompt09_error_inventory.csv`
- `outputs/reports/news_overlay/prompt01_11/reference/prompt09_fix_log.csv`
- `outputs/reports/news_overlay/prompt01_11/reference/prompt09_rerun_status.csv`
- `outputs/reports/news_overlay/prompt01_11/presented/prompt09_verify_fix_transformer_errors.md`

## Next Steps

prompt10_external_cross_check.md
