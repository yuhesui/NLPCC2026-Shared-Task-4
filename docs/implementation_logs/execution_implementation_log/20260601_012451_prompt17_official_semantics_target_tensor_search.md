# Implementation Log: prompt17 - official_semantics_target_tensor_search

**Created:** 2026-06-01 01:24:51

## Summary

Added SystemRunner target-tensor generation, Stage 1 text feature caching, bounded official-semantics search workflow, five-fold replay reporting, and package audit for Prompt17.

## Files Changed

src/nlpcc/stage1_news/schema.py,src/nlpcc/stage1_news/pipeline.py,src/nlpcc/stage1_news/text_feature_store.py,src/nlpcc/stage1_news/feature_cache.py,src/tools/experiments/leakage_safe_input_builder.py,src/tools/experiments/candidate_factory.py,src/tools/experiments/strategy_config_expander.py,src/tools/experiments/target_tensor_cache.py,src/tools/experiments/target_tensor_generator.py,scripts/build_text_feature_cache.py,scripts/generate_target_tensors.py,scripts/run_prompt17_overnight_search.py,tests/test_tools/test_experiments/test_prompt17_target_tensors.py,tests/test_nlpcc/test_stage1_news/test_prompt17_text_feature_cache.py,docs/reports/prompt17

## Tests / Checks

python -m pytest tests/test_nlpcc/test_stage1_news/test_prompt17_text_feature_cache.py -q --basetemp=outputs/pytest_tmp/prompt17_stage1 -o cache_dir=outputs/pytest_cache; python -m pytest tests/test_tools/test_experiments/test_prompt17_target_tensors.py -q --basetemp=outputs/pytest_tmp/prompt17_tensors -o cache_dir=outputs/pytest_cache; python scripts/run_prompt17_overnight_search.py --stage0-dates 3 --stage1-dates 20 --stage2-dates 10 --max-candidates-per-track 12 --candidate-text-modes no_news,rule_based --backend numpy; python scripts/run_official_server_smoke.py --output .var/prompt17/official_server_smoke.json

## Caveats

Bounded under-10-minute evidence run only; full overnight grid should rerun with larger date/candidate limits. Official server spotcheck blocked because localhost:6207 was unavailable. Candidate search excluded local-model modes from target tensor ranking but cache-smoked all requested text modes.

## Artifacts

- `.var/prompt17/prompt17_results.json`
- `.var/prompt17/candidate_scores_2024.csv`
- `.var/prompt17/candidate_scores_2025.csv`
- `.var/prompt17/five_fold_scores.csv`
- `.var/prompt17/packages`
- `docs/reports/prompt17`

## Next Steps

Run full overnight Prompt17 search with CUDA/torch if available, then re-run official server spotcheck once the local server is started.
