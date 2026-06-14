# Implementation Log: news_overlay_prompt04 - transformer_impact_architectures

**Created:** 2026-06-04 17:48:28

## Summary

Implemented Prompt04 Substage I cache-backed impact methods, N-to-I pipeline handoff, leakage guards, tests, and report updates.

## Files Changed

src/nlpcc/news_overlay/i_methods/architectures.py,src/nlpcc/news_overlay/registry.py,src/nlpcc/news_overlay/pipeline.py,src/nlpcc/news_overlay/base.py,src/nlpcc/news_overlay/config.py,src/nlpcc/news_overlay/cli.py,tests/test_nlpcc/test_news_overlay/test_scaffold.py,docs/news_overlay/method_table.md,docs/news_overlay/grid_search_table.md,docs/news_overlay/transformer_architecture_table.md,outputs/reports/news_overlay/prompt01_11

## Tests / Checks

python -B -m pytest tests\\test_nlpcc\\test_news_overlay\\test_scaffold.py -q -p no:cacheprovider passed 32/32; CLI-equivalent list-methods/check-models/build-cache/run/run-grid smokes passed

## Caveats

No local impact transformer model assets are configured, so I5/I6/I7 local-model inference was not exercised; Substage S remains scaffold pending Prompt05; no backtest or official-server validation run.

## Artifacts

- `outputs/reports/news_overlay/prompt01_11/presented/substage_i_summary.md`
- `outputs/reports/news_overlay/prompt01_11/reference/method_implementation_table.csv`
- `outputs/reports/news_overlay/prompt01_11/reference/transformer_method_status.csv`
- `outputs/reports/news_overlay/prompt01_11/reference/grid_search_status_table.csv`

## Next Steps

prompt05_sensitivity_overlay_transformer_integration.md
