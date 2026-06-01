# Implementation Log: prompt17 - overnight_grid_search

## Created

2026-06-01 01:25:21

## Summary

Prompt17 added cached Stage 1 text features, leakage-safe SystemRunner target tensors, official-semantics batched replay/search, locked 2025 and five-fold reports, and a clean package audit.

## Files Changed

- `src/nlpcc/stage1_news/schema.py`
- `src/nlpcc/stage1_news/pipeline.py`
- `src/nlpcc/stage1_news/text_feature_store.py`
- `src/nlpcc/stage1_news/feature_cache.py`
- `src/tools/experiments/leakage_safe_input_builder.py`
- `src/tools/experiments/candidate_factory.py`
- `src/tools/experiments/strategy_config_expander.py`
- `src/tools/experiments/target_tensor_cache.py`
- `src/tools/experiments/target_tensor_generator.py`
- `src/tools/verification/submission_package.py`
- `scripts/build_text_feature_cache.py`
- `scripts/generate_target_tensors.py`
- `scripts/run_prompt17_overnight_search.py`
- `tests/test_tools/test_experiments/test_prompt17_target_tensors.py`
- `tests/test_nlpcc/test_stage1_news/test_prompt17_text_feature_cache.py`
- `docs/reports/prompt17/*`

## Target Tensor Generation

Implemented target tensor generation through `SystemRunner`, not the legacy local smoke backtester. The generator builds daily inputs with current-day `open` available and current-day `close`, `high`, `low`, `change`, and `pct_change` masked before strategy execution. It advances each candidate's portfolio with local official value-holding semantics between decision dates so turnover-aware agents see realistic current holdings.

Artifacts:

- `.var/prompt17/target_tensors/`
- `.var/prompt17/generated_configs/`

## Text Feature Cache

Added a Stage 1 filesystem cache keyed by decision date, raw news content, and text config. The cache supports `no_news`, `rule_based`, `bge_small_zh`, `finbert_tone_chinese`, and `hybrid_rule_bge_finbert`. The bounded run cache-smoked all five modes; target-tensor ranking used `no_news` and `rule_based` to stay under the per-run time cap.

Artifact:

- `.var/prompt17/text_feature_cache/`

## Backtester Parity

The bounded search used `run_batched_official_semantics` with NumPy backend and compared the first candidate per track against `run_reference_official_semantics`. Both track parity checks were within tolerance in `docs/reports/prompt17/stage0_smoke_report.md`.

## Overnight Search

Executed bounded search command:

```powershell
python scripts\run_prompt17_overnight_search.py --stage0-dates 3 --stage1-dates 20 --stage2-dates 10 --max-candidates-per-track 12 --candidate-text-modes no_news,rule_based --backend numpy
```

Result: 24 candidates evaluated across both tracks in 85.56 seconds. Full overnight grid was intentionally not run inside this prompt.

## 2025 Locked Evaluation

Top 2024 candidates were replayed on public A 2025 with locked parameters and no 2025 tuning. The locked top Track A candidate was `bsa_rp_macro_tilt25`; the locked top Track B candidate was `sector_rotation_graph15`.

## Five-Fold Robustness

Generated five contiguous replay folds from the bounded 2024 tensor horizon and wrote fold summaries to:

- `.var/prompt17/five_fold_scores.csv`
- `docs/reports/prompt17/five_fold_evaluation_report.md`

## Official Server Spot Check

Executed:

```powershell
python scripts\run_official_server_smoke.py --output .var\prompt17\official_server_smoke.json
```

Status: blocked. `http://localhost:6207` refused the connection (`WinError 10061`), so no official server parity claim is made.

## Final Candidate Freeze

Bounded-run freeze:

- Track A: `bsa_rp_macro_tilt25`
- Track B: `sector_rotation_graph15`

This is a bounded candidate freeze, not a claim that the full overnight grid has been exhausted.

## Package

Built final package:

- `.var/prompt17/packages/nlpcc_task4_candidate_prompt17_final_20260601_0128.zip`

Package audit found 283 archive entries and no raw-data issues. The package includes `src/tools/` so Prompt17 reproducibility scripts have their local helper imports.

## Tests / Checks

- `python -m pytest tests/test_nlpcc/test_stage1_news/test_prompt17_text_feature_cache.py -q --basetemp=outputs/pytest_tmp/prompt17_stage1 -o cache_dir=outputs/pytest_cache`
- `python -m pytest tests/test_tools/test_experiments/test_prompt17_target_tensors.py -q --basetemp=outputs/pytest_tmp/prompt17_tensors -o cache_dir=outputs/pytest_cache`
- `python scripts/run_prompt17_overnight_search.py --stage0-dates 3 --stage1-dates 20 --stage2-dates 10 --max-candidates-per-track 12 --candidate-text-modes no_news,rule_based --backend numpy`
- `python scripts/run_official_server_smoke.py --output .var/prompt17/official_server_smoke.json`

## Caveats

- Bounded under-10-minute evidence run only; full overnight grid should rerun with larger candidate/date limits.
- Official server spotcheck was blocked because no local official server was available.
- Candidate search excluded local-model modes from target tensor ranking, but cache-smoked all required text modes.
- CUDA was not claimed; bounded evidence used NumPy backend.

## Artifacts

- `.var/prompt17/prompt17_results.json`
- `.var/prompt17/candidate_scores_2024.csv`
- `.var/prompt17/candidate_scores_2025.csv`
- `.var/prompt17/five_fold_scores.csv`
- `.var/prompt17/official_server_smoke.json`
- `.var/prompt17/packages/`
- `docs/reports/prompt17/`

## Next Steps

Run the same workflow with larger candidate/date limits and `--backend auto --prefer-cuda` on a CUDA host, then rerun the official server spotcheck once the local official server is started.
