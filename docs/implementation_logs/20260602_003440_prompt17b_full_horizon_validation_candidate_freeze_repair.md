# Implementation Log: prompt17b - full_horizon_validation_candidate_freeze_repair

## Created

2026-06-02 00:34:40 Asia/Shanghai

## Summary

Prompt17b repaired the Prompt17 validation gap by adding target-tensor trace/data-version auditing, a broad reference-vs-batched parity gate, full-horizon 2024 replay for the Prompt17 24 no-news/rule-based candidate slice, a corrected 2024-only candidate freeze, locked 2025 evaluation, 485-date research five-fold robustness, text-cache/runtime evidence, official-server spotcheck, package audit, and the required report tree under `outputs/reports/prompt17b/`.

## Files Changed

- `src/tools/experiments/target_tensor_generator.py`
- `scripts/run_prompt17b_validation.py`
- `src/tools/verification/submission_package.py`
- `tests/test_tools/test_experiments/test_prompt17_target_tensors.py`
- `outputs/reports/prompt17b/`
- `.var/prompt17b/`
- `docs/implementation_logs/20260602_003440_prompt17b_full_horizon_validation_candidate_freeze_repair.md`

## Prompt17 Gap Review

Created `outputs/reports/prompt17b/reference/prompt17_gap_matrix.md` and `outputs/reports/prompt17b/progress/progress_00_inventory_and_gap_review.md`. Prompt17 claims were treated as provisional because it used bounded 20-date evidence, had limited parity coverage, froze Track B from mixed 2024/2025 evidence, and left the official server blocked.

## Target Tensor Audit

Added data-root fingerprinting to the target-tensor cache key and decision-trace JSONL samples for each generated tensor bundle. Audit covered S0, S1, risk parity, DRO-BL-RP, BSA-RP, HGF-MPC, ARMOR, CEVA, LEEQA, KG-MoE, and OCO fallback. All audited candidates generated without failed days; trace samples and cache data-version fields are present.

## Leakage Safety Audit

`outputs/reports/prompt17b/reference/leakage_safety_audit.csv` records that current-day close/high/low/change/pct_change are masked and current-day open is available. Same-day news remains gated by the 15:00 cutoff recorded by the leakage-safe input builder.

## Parity Gate

Broad parity covered 12 candidates over 20 trading dates: S0 macro/sector, S1 macro/sector, S1 sector trend60, BSA-RP, DRO-BL-RP, risk parity, sector_rotation_graph15, CEVA sector, LEEQA top4, and KG-MoE lite. All reference-vs-NumPy-batched comparisons passed tolerance with final/max value diffs at numerical-noise scale.

## Full 2024 Search

Full 2024 replay used all available 242 trading dates for 12 macro and 12 sector no-news/rule-based Prompt17 candidates. Top macro candidate was `bsa_rp_macro_tilt25` with conservative score 0.863571, cumulative return 0.096623, and Sharpe 0.981740. Top sector candidate was `armor_omd_sector_default` with conservative score 0.778180, cumulative return 0.097944, and Sharpe 0.524427.

## Candidate Freeze Repair

Freeze discipline was corrected to 2024-only before locked 2025 evaluation. Track A primary/fallback are `bsa_rp_macro_tilt25` and `bsa_rp_macro_rule`. Track B primary/fallback are `armor_omd_sector_default` and `s0_sector_cash02`. `sector_rotation_graph15` was not frozen from 2025-only evidence; on full 2024 it scored 0.133205 while `s1_sector_default` scored 0.744663.

## Locked 2025 Evaluation

Locked evaluation used 243 public-A 2025 dates for the pre-frozen and baseline candidate sets only. The locked 2025 result is evidence, not a parameter-selection source. `sector_rotation_graph15` led the locked sector slice on 2025, but the freeze remains 2024-only.

## Full Five-Fold Robustness

Generated 485-date research five-fold scores from combined 2024 and public-A 2025 frozen-candidate tensors. Each selected candidate has five validation folds. Caveat: source target generation resets portfolio state at the 2024/2025 dataset boundary, so this is robustness evidence, not a continuous official replay claim.

## Text Feature Cache

Built Stage 1 cache evidence for all configured text modes over a bounded three-date sample per track. Local text-model weights loaded for the configured offline models; ranking and freeze used no-news/rule-based candidates only.

## Runtime / CUDA Benchmark

Runtime benchmark reports NumPy vectorized replay for 20-date parity tensors and tiled 100/300-candidate batches. CUDA was not claimed in this run because the executed benchmark backend was NumPy/CPU. The vectorized replay reached roughly 5.5k-8.3k candidates/sec on the benchmark slices.

## Official Server Spotcheck

Official server smoke was rerun through `scripts/run_official_server_smoke.py --base-url http://localhost:6207`. Status remains blocked with `[WinError 10061] No connection could be made because the target machine actively refused it`, indicating no official server was listening on the configured localhost port.

## Package Audit

Built package `.var/prompt17b/packages/nlpcc_task4_candidate_prompt17b_20260601_163312.zip`. Archive audit status is ok with 284 entries and no raw data paths. `src/tools/` is included deliberately for reproducibility/reporting tools; competition runtime code remains under `src/nlpcc/`.

## Tests / Checks

- `python -m pytest tests/test_tools/test_experiments/test_prompt17_target_tensors.py tests/test_tools/test_backtesting/test_prompt16_cuda_backtester.py tests/test_tools/test_verification/test_prompt12_submission_package.py -q` -> 7 passed.
- Prompt17b phases run: `init`, `audit`, `parity`, `full-2024 --track macro`, `full-2024 --track sector`, `freeze`, `locked-2025 --track macro`, `locked-2025 --track sector`, `fivefold`, `text-runtime`, `official-package`, `reports`.
- Required Prompt17b report filename check -> all required files present.

## Caveats

- Official server remains blocked, so readiness is `provisionally_ready_except_official_server`, not final official-ready.
- Full 2024 search used the Prompt17 24-candidate no-news/rule-based slice, not a 100-300 candidate expansion, to keep individual runs bounded.
- Five-fold robustness uses concatenated train_2024/public_a_2025 target tensors with a dataset-boundary reset caveat.
- Pytest emitted an existing `.pytest_cache` permission warning, but the targeted tests passed.

## Artifacts

- `outputs/reports/prompt17b/`
- `.var/prompt17b/prompt17b_state.json`
- `.var/prompt17b/target_tensors/`
- `.var/prompt17b/generated_configs/`
- `.var/prompt17b/search_runs/`
- `.var/prompt17b/checkpoints/`
- `.var/prompt17b/benchmarks/`
- `.var/prompt17b/official_server/official_server_smoke.json`
- `.var/prompt17b/packages/`

## Next Steps

Start the official server on `http://localhost:6207`, rerun `python scripts/run_prompt17b_validation.py --phase official-package --backend numpy`, and only then proceed to final submission packaging polish if the official spotcheck passes.
