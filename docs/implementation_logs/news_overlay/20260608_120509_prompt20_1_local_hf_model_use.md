# Implementation Log: prompt20_1 - local_hf_model_use

**Created:** 2026-06-08 12:05:09

## Summary

Implemented Prompt20.1 local-only Hugging Face model use: approved local model mapping, cache manifests, FinBERT N3 classifier execution, bge-reranker-v2-m3 N6 reranker execution, local-only CLI smokes, docs, and reports.

## Files Changed

configs/news_overlay/approved_hf_models.yaml,configs/news_overlay/local_models.example.yaml,configs/news_overlay/local_models.local.example.yaml,configs/news_overlay/grids/transformer_asset_smoke_grid.csv,src/nlpcc/news_overlay/hf_models.py,src/nlpcc/news_overlay/cli.py,src/nlpcc/news_overlay/n_methods/architectures.py,tests/test_nlpcc/test_news_overlay/test_scaffold.py,docs/news_overlay/method_table.md,docs/news_overlay/transformer_architecture_table.md,docs/news_overlay/grid_search_table.md,outputs/reports/news_overlay/prompt01_11/progress/progress_20_1_local_hf_model_use.md,outputs/reports/news_overlay/prompt01_11/presented/prompt20_1_local_model_use_summary.md,outputs/reports/news_overlay/prompt01_11/presented/prompt20_1_local_transformer_validation.md,outputs/reports/news_overlay/prompt01_11/reference/approved_hf_models.csv,outputs/reports/news_overlay/prompt01_11/reference/local_hf_model_manifest.csv,outputs/reports/news_overlay/prompt01_11/reference/model_availability_report.csv,outputs/reports/news_overlay/prompt01_11/reference/transformer_method_status.csv,outputs/reports/news_overlay/prompt01_11/reference/grid_search_status_table.csv,outputs/reports/news_overlay/prompt01_11/reference/cache_manifest.csv,outputs/reports/news_overlay/prompt01_11/reference/error_log.md

## Tests / Checks

check-models --local-only passed with network_attempted=false; build-cache --method N2/N3/N4/N5 --local-only passed; repeated N2 build-cache produced cache_hit=True; run Track A N2/I2/S3 --local-only passed; run Track B N2345/I256/S126 --local-only passed with BGE+FinBERT component evidence; run Track B N6/I23/S12 --local-only passed with true local bge-reranker-v2-m3 scoring; run-grid transformer_asset_smoke_grid.csv --local-only passed 11/11 rows; pytest tests/test_nlpcc/test_news_overlay/test_scaffold.py -q --basetemp outputs/pytest_tmp_prompt20_1 passed 63 tests, 1 skipped.

## Caveats

No downloads were run in Prompt20.1; N7,N8,I7,S7 remain blocked because no Prompt20.1 approved local assets are mapped; this is smoke validation only, not full 2024/2025 evaluation, promotion, or official runtime change; pytest reported non-fatal tokenizer deprecation and pytest cache warnings.

## Artifacts

- None

## Next Steps

Run real no-proxy Prompt07-style 2024 construction grid and ablations using the pinned local BGE, FinBERT, and reranker evidence before any 2025 validation or promotion.
