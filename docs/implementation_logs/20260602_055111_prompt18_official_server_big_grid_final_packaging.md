# Implementation Log: prompt18 - official_server_big_grid_final_packaging

## Created

2026-06-02 05:51:11

## Summary

Repaired official server startup, aligned local replay with candidate-specific planner configs and official 2025 lookback/news semantics, reran the full 320-candidate 2024 grid, froze final Track A/B candidates, ran locked 2025, parity, package split, and reports.

## Files Changed

NLPCC_tasks/logs.py, NLPCC_tasks/agent_platform/agents/build_agent.py, src/tools/backtesting/cuda_vectorized_backtester.py, src/tools/experiments/leakage_safe_input_builder.py, src/tools/experiments/target_tensor_generator.py, scripts/run_prompt18_big_grid.py, configs/prompt18_final_candidates.json, configs/systems/prompt18_track_a_primary.yaml, configs/systems/prompt18_track_a_fallback.yaml, configs/systems/prompt18_track_b_primary.yaml, configs/systems/prompt18_track_b_fallback.yaml, tests/test_tools/test_backtesting/test_prompt16_cuda_backtester.py, tests/test_tools/test_experiments/test_prompt17_target_tensors.py

## Context Review

Reviewed Prompt17b reports, repository rules, official starter READMEs, current compatibility docs, and Prompt18 requirements. Treated prior readiness claims as provisional until official server parity, repaired replay semantics, large-grid evidence, locked 2025 evaluation, and package audits were regenerated.

## Official Server Startup / Repair

Installed starter requirements after the first startup failed on missing uvicorn. Repaired Windows startup blockers by launching with UTF-8 output and changing Loguru enqueue behavior in NLPCC_tasks/logs.py to default off unless NLPCC_LOGURU_ENQUEUE is enabled. Official server smoke passed on localhost:6207.

## Pre-Grid Integrity Gate

Reran the hard gate after replay repairs. Leakage masking, target tensor cache key fields, representative reference-vs-batched parity, catalog generation, and runtime raw-data exclusion passed.

## Big Grid Search

Reran Prompt18 Option 1 under repaired semantics: 320 candidates, 160 macro, 160 sector, all over 242 2024 construction dates, no_news/rule_based modes, NumPy official-semantics batched replay. Final top Track A candidate was p18_rp_macro_w10_s5; final top Track B candidate was p18_leeqa_sector_k5_temp35.

## Candidate Freeze

Froze candidates strictly from 2024 grid evidence: Track A primary p18_rp_macro_w10_s5, Track A fallback p18_rp_macro_w40_s5, Track B primary p18_leeqa_sector_k5_temp35, Track B fallback p18_s1_sector_t35_v30_w20. Wrote prompt18 alias configs and configs/prompt18_final_candidates.json.

## Locked 2025 Evaluation

Reran locked public-A 2025 evaluation after freeze with official dataset-root lookback into 2024. Included frozen candidates, top 2024 comparators, baselines, and exact Prompt17b frozen names. Frozen candidates generalized strongly; no candidate parameters were changed after freeze.

## Final Local Parity

Final local reference-vs-batched parity passed for all selected baselines/frozen candidates with numerical diffs around floating-point tolerance.

## Official Server Parity

Final official-server parity passed for S0 macro, S1 macro, S1 sector, Track A primary, and Track B primary over the 2025-01-02 to 2025-01-08 official server window. The key fixes were candidate-specific planner configs, official dataset-root 2024 lookback for 2025 sessions, and official news-source/window behavior.

## Package Split

Built separate packages under .var/prompt18/packages: prompt18_official_runtime_20260601_215404.zip and prompt18_reproducibility_20260601_215404.zip. Runtime audit passed with no raw data, pycache, or model-binary issues.

## Tests / Checks

Prompt18 phases run: integrity, plan, benchmark, forced full 320-candidate grid, freeze, locked-2025, local-parity, official-parity, packages, reports. Targeted pytest suite passed: 11 passed, with one pytest cache permission warning.

## Caveats

One earlier grouped macro run and one earlier 20-candidate sector chunk exceeded the 10-minute run budget before chunk sizing was corrected; final repaired grid chunks stayed below 10 minutes. Pytest cache writes still warn with WinError 5. NLPCC_tasks/server_platform/users.json had temporary server users removed; only a newline-format diff remains.

## Artifacts

- outputs/reports/prompt18/presented/final_submission_readiness_report.md
- outputs/reports/prompt18/reference/big_grid_2024_ranking.csv
- outputs/reports/prompt18/reference/locked_2025_evaluation.csv
- outputs/reports/prompt18/reference/official_server_parity.csv
- .var/prompt18/packages/prompt18_official_runtime_20260601_215404.zip
- .var/prompt18/packages/prompt18_reproducibility_20260601_215404.zip

## Next Steps

Prompt19 should produce final submission prose/handoff checklist and optionally rerun official server parity on a wider date window before external submission.
