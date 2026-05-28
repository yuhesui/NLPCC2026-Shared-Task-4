# Implementation Log: prompt03-real-data - real_data_baseline_rerun

**Created:** 2026-05-28 15:35:09

## Summary

Reran S0 and S1 baseline local backtests on copied official 2024 training and 2025 public A data instead of the synthetic smoke subset; added a no-news backtester switch for faster baseline runs.

## Files Changed

src/tools/backtesting/local_backtester.py,outputs/backtests/real_train_2024_s0_macro.json,outputs/backtests/real_train_2024_s1_macro.json,outputs/backtests/real_train_2024_s0_sector.json,outputs/backtests/real_train_2024_s1_sector.json,outputs/backtests/real_public_a_2025_s0_macro.json,outputs/backtests/real_public_a_2025_s1_macro.json,outputs/backtests/real_public_a_2025_s0_sector.json,outputs/backtests/real_public_a_2025_s1_sector.json

## Tests / Checks

PYTHONPATH=src python -B real-data S0/S1 baseline runs over data/train_2024 and data/public_a_2025 with lookback_days=60 and load_news=False; PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -B -m pytest tests/test_nlpcc/test_stage3_trade tests/test_nlpcc/test_stage4_agent tests/test_integration/test_prompt01_smoke.py -p no:cacheprovider (11 passed)

## Caveats

2025 public A results are evaluation-only and were not used for tuning. Local backtester remains a simplified official-compatible approximation, not the official HTTP server.

## Artifacts

- None

## Next Steps

Use these real-data S0/S1 outputs as the baseline floor for prompt04 research tooling and later official-server parity checks.
