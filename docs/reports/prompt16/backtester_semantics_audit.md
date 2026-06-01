# Prompt16 Backtester Semantics Audit

| Backtester / Runner | Path | Used By | CUDA? | Vectorised? | Official Semantics Match? | Known Differences | Status | Required Fix |
|---|---|---|---|---|---|---|---|---|
| LocalSmokeBacktester | `src/tools/backtesting/local_backtester.py` | `run_experiment.py`, Prompt13 local runs, Prompt15 grid | no | no | partial | Share-based holdings; executes at close; differs from official value holdings. | legacy_research | Keep for old evidence, do not call official-equivalent. |
| Matrix vectorized backtester | `src/tools/backtesting/vectorized_backtester.py` | Prompt04 batch helper | no | yes, NumPy matrix | no | Direct target-weight rebalance; not buy-by-cash/sell-percentage. | research_only | Keep as simple matrix model with caveat. |
| CUDA backend status helper | `src/tools/backtesting/cuda_backend.py` | capability reporting | status only | no | n/a | Only detects torch/CUDA. | capability_helper | No longer treated as backtester. |
| Prompt14 script local parity replay | `scripts/run_prompt14_audit.py` | Prompt14 parity | no | no | yes for S0/S1 window | Logic was script-local, not reusable. | evidence_only | Extracted reusable equivalent in Prompt16. |
| Reference official semantics | `src/tools/backtesting/reference_official_semantics.py` | Prompt16 tests/benchmark | no | no | yes, local reference | Value holdings, buy-first/sell-second, no same-day sell funding, commission, finish update. | new_reference | Use as correctness source. |
| Batched official semantics | `src/tools/backtesting/cuda_vectorized_backtester.py` | Prompt16 batch/grid replay | optional torch CUDA | yes, batched candidates | yes vs reference | Does not call agents; replays precomputed target weights. | new_accelerated | Use for grid scoring after leakage-safe target generation. |
| Constant-weight batched grid helper | `src/tools/backtesting/batched_grid_backtester.py` | Prompt16 grid smoke helpers | optional | yes | yes via batched backend | Constant target-weight candidates only. | helper | Extend if strategy-specific target tensors are needed. |
| OfficialServerRunner | `src/tools/backtesting/official_server_runner.py` | server probe/start helper | no | n/a | official source | Server not reachable during Prompt16. | blocked | Start server before official parity rerun. |

Current grid-search path: `scripts/run_prompt15_grid_search.py` still uses `run_local_backtest`, so its evidence is not official-equivalent. Prompt16 adds the official-equivalent replay layer for target-weight grids, but does not rewrite Prompt15 grid execution.
