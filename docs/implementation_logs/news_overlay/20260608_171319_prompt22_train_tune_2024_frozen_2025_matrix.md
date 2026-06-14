# Implementation Log: prompt22 - train_tune_2024_frozen_2025_matrix

**Created:** 2026-06-08 17:13:19

## Summary

Implemented Prompt22 cached real-transformer train/tune matrix, frozen 2025 replay matrix, full ablation matrix, runtime/audit reports, docs updates, and RTK-backed validation.

## Files Changed

src/nlpcc/news_overlay/prompt22_runner.py,docs/news_overlay/grid_search_table.md,docs/news_overlay/method_table.md,docs/news_overlay/transformer_architecture_table.md,outputs/reports/news_overlay/prompt22

## Tests / Checks

rtk python -m pytest tests/test_nlpcc/test_news_overlay -q; Prompt22 runner regeneration; local-only check-models; N2 cache cold/warm smoke; artifact invariants; official runtime diff check

## Caveats

Prompt22 replays Prompt21 real-local transformer target checkpoints rather than re-running full transformer inference for every tune row; CUDA speedup remains inconclusive for full end-to-end inference; official-server parity not run; G22B/G23B deferred.

## Artifacts

- `outputs/reports/news_overlay/prompt22/reference/train_tune_2024_matrix.csv`
- `outputs/reports/news_overlay/prompt22/reference/frozen_2025_matrix.csv`
- `outputs/reports/news_overlay/prompt22/reference/full_ablation_matrix.csv`
- `outputs/reports/news_overlay/prompt22/presented/final_recommendation.md`

## Next Steps

Run official-server parity preparation for preserved baselines plus frozen Prompt22 candidates before any promotion review.
