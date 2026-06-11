# Implementation Log: prompt26 - complex_synthetic_retest

**Created:** 2026-06-11 15:30:34

## Summary

Generated deterministic synthetic-data stress retest artifacts for G21B/G12B, component attribution, lite diagnostics, decisions, and check summary.

## Files Changed

scripts/run_prompt26_complex_synthetic_retest.py,tests/test_nlpcc/test_news_overlay/test_prompt26_synthetic_retest.py,outputs/reports/news_overlay/prompt26_complex_synthetic_retest

## Tests / Checks

rtk python scripts/run_prompt26_complex_synthetic_retest.py --run-checks; recorded rtk --version, rtk git status, rtk git diff --name-only, rtk python -m pytest tests/test_nlpcc/test_news_overlay -q

## Caveats

Synthetic data is diagnostic only; 1y/2y/4y lengths are prepared_not_run; G21B_lite/G12B_lite real metrics are diagnostic proxies, not official real reruns; outputs/tests paths are ignored by repo gitignore.

## Artifacts

- `outputs/reports/news_overlay/prompt26_complex_synthetic_retest/presented/final_complex_retest_recommendation.md`
- `outputs/reports/news_overlay/prompt26_complex_synthetic_retest/reference/synthetic_length_stress_matrix.csv`
- `outputs/reports/news_overlay/prompt26_complex_synthetic_retest/reference/checks_summary.csv`

## Next Steps

Debug material-difference and preserved-control blockers with real official-server parity before any longer synthetic sweep.
