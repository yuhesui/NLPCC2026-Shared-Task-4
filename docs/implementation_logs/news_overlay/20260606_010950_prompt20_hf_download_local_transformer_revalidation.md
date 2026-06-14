# Implementation Log: prompt20 - hf_download_local_transformer_revalidation

**Created:** 2026-06-06 01:09:50

## Summary

Implemented explicit approved Hugging Face download-once mode, local-only model checks, BGE-backed cache/build/run/grid smoke evidence, and Prompt20 reports.

## Files Changed

src/nlpcc/news_overlay/hf_models.py,src/nlpcc/news_overlay/cli.py,src/nlpcc/news_overlay/base.py,src/nlpcc/news_overlay/config.py,src/nlpcc/news_overlay/model_availability.py,src/nlpcc/news_overlay/pipeline.py,src/nlpcc/news_overlay/registry.py,src/nlpcc/news_overlay/n_methods/architectures.py,src/nlpcc/news_overlay/i_methods/architectures.py,src/nlpcc/news_overlay/s_methods/architectures.py,configs/news_overlay/approved_hf_models.yaml,configs/news_overlay/local_models.example.yaml,configs/news_overlay/local_models.local.example.yaml,configs/news_overlay/grids/transformer_asset_smoke_grid.csv,tests/test_nlpcc/test_news_overlay/test_scaffold.py,docs/news_overlay/method_table.md,docs/news_overlay/transformer_architecture_table.md,docs/news_overlay/grid_search_table.md,outputs/reports/news_overlay/prompt01_11/progress/progress_20_hf_download_local_model_revalidation.md,outputs/reports/news_overlay/prompt01_11/presented/prompt20_hf_download_summary.md,outputs/reports/news_overlay/prompt01_11/presented/prompt20_local_transformer_revalidation.md

## Tests / Checks

download-models succeeded for BAAI/bge-small-zh-v1.5; check-models --offline --local-only passed with N6 blocked; build-cache local-only passed for N2,N3,N4,N5 and repeated N2 cache hit; run local-only passed for Track A N2/I2/S3 and Track B N2345/I256/S126; run-grid local-only passed 9 rows and blocked N6; pytest tests/test_nlpcc/test_news_overlay/test_scaffold.py -q --basetemp outputs/pytest_tmp_prompt20 passed 57 tests; AST syntax check passed.

## Caveats

N6 true cross-encoder remains blocked because reranker is disabled and cross-encoder scoring is not implemented; N3 uses real BGE encoder aspect similarity, not true FinBERT classifier logits; no full 2024/2025 evaluation or candidate promotion was run; Windows HF symlink warning was encountered before final local snapshot validation.

## Artifacts

- None

## Next Steps

Run no-proxy Prompt07-style 2024 construction rerun with the pinned local BGE snapshot before any 2025 validation or promotion.
