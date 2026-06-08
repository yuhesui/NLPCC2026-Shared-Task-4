# Implementation Log: prompt21 - full_real_local_transformer_grid_audit

**Created:** 2026-06-08 15:05:18

## Summary

Ran full real-local News Overlay transformer grid, GPU tuning, frozen 2025 replay, ablations, audits, and promotion gate reports.

## Files Changed

src/nlpcc/news_overlay/prompt21_runner.py,src/nlpcc/news_overlay/grid_evaluator.py,src/nlpcc/news_overlay/n_methods/architectures.py,docs/news_overlay/grid_search_table.md,docs/news_overlay/method_table.md,docs/news_overlay/transformer_architecture_table.md,outputs/reports/news_overlay/prompt21

## Tests / Checks

pytest tests/test_nlpcc/test_news_overlay -q; check-models local-only; build-cache N2 twice cache-hit smoke; grid_evaluator checkpoint resume smoke; official runtime diff

## Caveats

No automatic promotion; official-server parity not run; several ablation toggles remain not_run_with_reason; G22B/G23B remain partial_blocked due deferred local assets.

## Artifacts

- None

## Next Steps

Human-review the Track A/B frozen candidate sets, then run official-server parity only for candidates that remain acceptable after ablation and turnover/drawdown review.
