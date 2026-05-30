# Implementation Log: prompt14 - pipeline_repair

## Created

2026-05-30 11:22:25

## Summary

Repaired the official-facing wrapper path, portfolio-state conversion, target-weight order planner, trade validator, and SystemRunner. Generated Prompt14 track/stage/model/package/parity/Hugging Face reports and rebuilt a candidate package including the official wrapper.

## Files Changed

- `NLPCC_tasks/agent_platform/agents/build_agent.py`
- `src/nlpcc/execution/official_adapter.py`
- `src/nlpcc/execution/order_planner.py`
- `src/nlpcc/execution/trade_validator.py`
- `src/nlpcc/runtime/system_runner.py`
- `src/nlpcc/stage3_trade/models/cash_feasibility.py`
- `src/nlpcc/portfolio/position_sizing.py`
- `configs/stage1_news/rule_based.yaml`
- `README.md`
- `METHODOLOGY.md`
- `docs/architecture/OFFICIAL_COMPATIBILITY.md`
- `docs/strategy/B_LIST_HARDENING.md`
- `docs/strategy/METHODOLOGY.md`
- `scripts/run_prompt14_audit.py`
- `tests/test_integration/test_prompt14_build_agent.py`
- `tests/test_nlpcc/test_execution/test_prompt14_official_adapter.py`
- `tests/test_nlpcc/test_runtime/test_prompt14_system_runner.py`
- `outputs/reports/prompt14/`

## Tests / Checks

- `python scripts/run_official_server_smoke.py --track macro --start-date 2024-01-02 --end-date 2024-01-03 --output outputs/reports/prompt14/official_server_probe.json` -> `status=ok`.
- `python scripts/run_prompt14_audit.py --base-url http://localhost:6207` -> generated Prompt14 reports and rebuilt package; parity rows were regenerated after fixing the local official-semantics simulator.
- `python -B -m pytest -p no:cacheprovider tests/test_nlpcc/test_execution/test_prompt14_official_adapter.py tests/test_nlpcc/test_runtime/test_prompt14_system_runner.py tests/test_integration/test_prompt14_build_agent.py` -> `10 passed`.
- `python -B -m pytest -p no:cacheprovider` with workspace-local temp -> `92 passed`.

## Track A Status

Track A default is `robust_bl_track1` with `s1_macro` fallback. Wrapper-based parity now passes for `s0_equal_weight_macro` and `s1_macro`; `robust_bl_track1` still has a small official/local value mismatch and should remain a local candidate until text/news-window parity is closed.

## Track B Status

Track B default is `s1_sector`; `sector_rotation_track2` remains experimental. Wrapper-based parity passes for `s1_sector`; `sector_rotation_track2` still fails trade/value parity and should not be promoted.

## Stage Status

Stage 1 remains deterministic/rule-based by default. Stage 2 BL/sector text structures remain usable but retrieval/KG/causal components are not production claims. Stage 3 is comparatively mature and now supports explicit official value-holding semantics. Stage 4 has production candidates and prototypes. Execution/runtime was the main repair area and is now a working prototype with wrapper tests.

## Model Status

Promote S1, S0 sanity baseline, rule-based Stage 1, and Track A robust BL as a local candidate only. Keep OCO-style ensemble, sector rotation, KG-MoE-Lite, and robust BL ablations as report/ablation systems. Defer or reject full KG, causal/invariant, retrieval memory, transformer memory, HMM/Kalman/MPC, learning-to-rank, pure LLM allocator, deep RL, and graph RL.

## Hugging Face / Local Model Audit

No Hugging Face model was downloaded. Optional local text models remain disabled by default with `text_model.enabled=false` and `fallback=rule_based`. Model-card sources were checked for the candidates listed in `outputs/reports/prompt14/huggingface_model_audit.md`.

## Key Findings

- `build_agent.py` now exists and imports `src/nlpcc` through a thin official-facing wrapper.
- Official holdings with `value` are now treated as monetary holding value, not shares.
- The order planner emits official buy-amount and sell-percentage payloads and rejects invalid trades before submission.
- Same-day sell proceeds are not used for same-day buys.
- S0 macro, S1 macro, and S1 sector pass wrapper-based official/local parity over 2024-01-02 to 2024-01-31.
- The rebuilt package includes the official wrapper, `src/nlpcc`, configs, and requirements, and excludes raw data/cache/pycache/model files.

## Caveats

- `robust_bl_track1` still fails exact parity by a small value difference, while trade count matches.
- `sector_rotation_track2` still fails trade and value parity and remains experimental.
- Full-year 2024 and locked 2025 were not rerun through the new wrapper path in this prompt.
- No Docker or equivalent environment lock was added.

## Artifacts

- `outputs/reports/prompt14/pipeline_repair_report.md`
- `outputs/reports/prompt14/track_status_matrix.md`
- `outputs/reports/prompt14/stage_status_matrix.md`
- `outputs/reports/prompt14/model_status_matrix.md`
- `outputs/reports/prompt14/official_wrapper_repair_report.md`
- `outputs/reports/prompt14/official_local_parity_rerun_report.md`
- `outputs/reports/prompt14/huggingface_model_audit.md`
- `outputs/reports/prompt14/package_rebuild_report.md`
- `outputs/reports/prompt14/final_recommendation.md`
- `outputs/submissions/nlpcc_task4_candidate_prompt14_repaired_20260529_115936.zip`

## Next Steps

Prompt15 - Wrapper-Based Full-Year Validation and Package Dry-Run: run full-year 2024 and locked 2025 through the official wrapper, verify the rebuilt package from a clean extraction, and close robust BL text/news parity before final submission.
