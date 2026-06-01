# Prompt17 Final Status Report

## 1. Readiness Verdict

Ready for final packaging/submission polish

## 2. Target Tensor Wiring Status

Implemented. Target tensors are generated through `SystemRunner` with leakage-safe price/news inputs and per-candidate official-style portfolio advancement.

## 3. Text Feature Cache Status

Implemented. Cache-smoked `no_news`, `rule_based`, `bge_small_zh`, `finbert_tone_chinese`, and `hybrid_rule_bge_finbert` under `.var/prompt17/text_feature_cache/`.

## 4. Backtester / Replay Status

Implemented. Final selection evidence used `reference_official_semantics` and `batched_official_semantics` with NumPy backend. No final evidence used `LocalSmokeBacktester`.

## 5. Overnight Search Summary

Bounded search completed: 24 candidates, 20 construction dates, 10 locked 2025 dates, 85.56 seconds.

## 6. 2024 Construction Top Candidates

Top bounded construction candidates are recorded in `.var/prompt17/candidate_scores_2024.csv` and `docs/reports/prompt17/top_candidates_2024_construction.md`.

## 7. 2025 Locked Evaluation Summary

Locked 2025 top-k replay completed without parameter changes. Top Track A candidate was `bsa_rp_macro_tilt25`; top Track B candidate was `sector_rotation_graph15`.

## 8. Five-Fold Robustness Summary

Five contiguous validation folds were replayed from the bounded 2024 target tensors. Detailed metrics are in `.var/prompt17/five_fold_scores.csv`.

## 9. Official Server Spot Check

Blocked. `http://localhost:6207` refused the connection (`WinError 10061`). No official server parity claim is made.

## 10. Final Track A Candidate

`bsa_rp_macro_tilt25`

## 11. Final Track B Candidate

`sector_rotation_graph15`

## 12. Package Status

Pass. Final package: `.var/prompt17/packages/nlpcc_task4_candidate_prompt17_final_20260601_0128.zip`; archive audit found no raw-data issues.

## 13. Remaining Blockers

Full overnight CUDA-scale search was not run in this prompt. Official server spotcheck needs a running local official server.

## 14. Recommended Next Step

Run the same workflow with larger date/candidate limits and `--backend auto --prefer-cuda`, then rerun the official server spotcheck once the server is available.
