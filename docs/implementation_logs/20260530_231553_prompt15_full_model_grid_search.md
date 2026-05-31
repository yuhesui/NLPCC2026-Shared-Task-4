# Implementation Log: prompt15 - full_model_grid_search

## Created

2026-05-30 23:15:53

## Summary

Implemented Prompt15 functional MVP paths for the seven required method families, added optional offline Stage 1 BGE/FinBERT integration, wired new agents into registries/SystemRunner/experiment tooling, ran a compatibility-filtered construction-sample grid, evaluated the top 5 on locked 2025 sample dates, generated evidence reports, updated docs, and rebuilt the candidate package.

## Files Changed

- `src/nlpcc/stage1_news/`
- `src/nlpcc/stage2_text_store/`
- `src/nlpcc/stage3_trade/`
- `src/nlpcc/stage4_agent/`
- `src/nlpcc/runtime/system_runner.py`
- `src/tools/experiments/runner.py`
- `configs/`
- `scripts/run_prompt15_grid_search.py`
- `tests/test_nlpcc/test_stage1_news/test_prompt15_local_text_models.py`
- `tests/test_nlpcc/test_stage2_text_store/test_prompt15_top_method_stores.py`
- `tests/test_nlpcc/test_stage3_trade/test_prompt15_top_method_states.py`
- `tests/test_nlpcc/test_stage4_agent/test_prompt15_top_methods.py`
- `README.md`
- `METHODOLOGY.md`
- `docs/strategy/B_LIST_HARDENING.md`
- `docs/architecture/OFFICIAL_COMPATIBILITY.md`
- `docs/strategy/METHODOLOGY.md`
- `outputs/reports/prompt15/`
- `outputs/submissions/nlpcc_task4_candidate_prompt15_mvp_grid_20260530_232000.zip`

## Models Implemented

- DRO-BL-RP: functional robust BL / risk-parity anchor MVP.
- BSA-RP: belief-state conditioned risk-parity MVP.
- ARMOR-OMD: exponentiated-weight base-allocator ensemble MVP with optional state persistence.
- LEEQA-Rank: deterministic Track B rank-scoring MVP.
- KG-MoE-Lite: functional graph/router prototype retained and wired into Prompt15 grid.
- HGF-MPC: one-step Kalman/HMM constrained controller MVP.
- CEVA-KF/CIGA: stable event-impact graph plus Kalman overlay MVP.

## Stage 1 Local Model Integration

Added offline local-model discovery and extractors for:

- `BAAI/bge-small-zh-v1.5`
- `yiyanghkust/finbert-tone-chinese`

Runtime defaults remain `text_model.enabled: false` with rule-based fallback. No silent downloads are performed.

## Grid Search

Ran:

```text
python scripts/run_prompt15_grid_search.py --max-dates 10 --top5-2025-max-dates 10
```

The grid covered 17 compatibility-filtered pipelines. Because local text-model inference was expensive, this is a 10-trading-date construction sample, not full-year final evidence.

## Top 5 Pipelines

1. `armor_omd_macro`
2. `hgf_mpc_track1`
3. `s0_macro_no_news`
4. `s1_macro_no_news`
5. `dro_bl_rp_rule_track1`

## 2025 Evaluation

The top 5 were evaluated on the first 10 locked 2025 public-A dates with no parameter changes. Results are in `outputs/reports/prompt15/top5_2025_evaluation.md`.

## Wrapper / Parity Status

S0/S1 parity remains inherited from Prompt14. Prompt15 advanced candidates ran through the local wrapper path, but official-server parity was not rerun for the new MVP systems.

## Package Status

Package rebuilt successfully:

- `outputs/submissions/nlpcc_task4_candidate_prompt15_mvp_grid_20260530_232000.zip`

The archive includes wrapper/source/configs/docs and excludes raw official data, dataset paths, outputs, caches, pycache files, and downloaded Hugging Face models.

## Tests / Checks

```text
python -m pytest tests/test_nlpcc/test_stage1_news/test_prompt15_local_text_models.py tests/test_nlpcc/test_stage2_text_store/test_prompt15_top_method_stores.py tests/test_nlpcc/test_stage3_trade/test_prompt15_top_method_states.py tests/test_nlpcc/test_stage4_agent/test_prompt15_top_methods.py -q
```

Result: 11 passed. Pytest emitted cache-write warnings due `.pytest_cache` permissions.

```text
python scripts/run_prompt15_grid_search.py --max-dates 10 --top5-2025-max-dates 10
```

Result: completed, 17 pipelines scored.

```text
python scripts/package_submission.py --package-name nlpcc_task4_candidate_prompt15_mvp_grid_20260530_232000
```

Result: package/audit status ok; no archive issues.

## Caveats

- Prompt15 grid and 2025 evaluation are runtime-bounded samples, not full-year results.
- Official-server parity for advanced Prompt15 systems remains required.
- Offline HF models are integrated and resolved locally but excluded from the package and disabled by default.
- MVP labels must not be overstated as full GNN/MoE, full causal discovery, full MPC, or full OCO.

## Artifacts

- `outputs/reports/prompt15/stage1_local_model_integration_report.md`
- `outputs/reports/prompt15/grid_search_summary.md`
- `outputs/reports/prompt15/grid_search_results.csv`
- `outputs/reports/prompt15/top5_candidate_pipelines.md`
- `outputs/reports/prompt15/top5_2025_evaluation.md`
- `outputs/reports/prompt15/wrapper_parity_validation.md`
- `outputs/reports/prompt15/final_system_evidence_pack.md`
- `outputs/reports/prompt15/model_implementation_status.md`
- `outputs/reports/prompt15/final_package_report.md`
- `outputs/reports/prompt15/documentation_update_report.md`
- `outputs/reports/prompt15/final_recommendation.md`
- `outputs/submissions/nlpcc_task4_candidate_prompt15_mvp_grid_20260530_232000.zip`

## Next Steps

Prompt16 full-year rerun, official-server parity closure, and final candidate freeze.
