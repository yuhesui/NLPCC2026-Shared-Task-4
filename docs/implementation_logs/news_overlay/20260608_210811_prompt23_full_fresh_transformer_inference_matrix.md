# Implementation Log: prompt23 - full_fresh_transformer_inference_matrix

**Created:** 2026-06-08 21:08:11

## Summary

Implemented Prompt23 fresh per-row transformer inference runner and cache policy audit; completed a partial 5-row fresh smoke but did not complete the full 212-row matrix due measured multi-hour runtime.

## Files Changed

src/nlpcc/news_overlay/prompt23_runner.py,outputs/reports/news_overlay/prompt23

## Tests / Checks

rtk python -m pytest tests/test_nlpcc/test_news_overlay -q; Prompt23 row-limit 5 fresh smoke; strict local-only check-models; partial artifact invariants; official runtime diff check

## Caveats

Prompt23 is partial: only 5 of 212 required rows completed. Full fresh per-row inference is estimated to require several hours; no promotion or full fresh candidate freeze should be claimed from this partial run.

## Artifacts

- `outputs/reports/news_overlay/prompt23/reference/full_fresh_2024_matrix.csv`
- `outputs/reports/news_overlay/prompt23/reference/cache_policy_audit.csv`
- `outputs/reports/news_overlay/prompt23/reference/prompt22_vs_prompt23_equivalence.csv`
- `outputs/reports/news_overlay/prompt23/presented/full_fresh_2024_summary.md`

## Next Steps

Run Prompt23 full matrix as a long-running job or add a safe low-level embedding cache that does not bypass N/I/S row execution, then rerun selection and frozen 2025 from the complete fresh matrix.
