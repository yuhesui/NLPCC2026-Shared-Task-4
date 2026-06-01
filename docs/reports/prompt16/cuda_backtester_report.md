# Prompt16 CUDA / Parallel Backtester Report

| Check | Result | Evidence | Notes |
|---|---|---|---|
| Reference official-semantics replay exists | pass | `src/tools/backtesting/reference_official_semantics.py` | Extracted from Prompt14 parity semantics. |
| Batched replay preserves official execution order | pass | Prompt16 tests | Buy orders consume decision cash before sells add cash. |
| CPU fallback exists | pass | NumPy backend test | `backend="numpy"` always runs on CPU. |
| Torch CUDA path is real | pass | benchmark device=`cuda` | CUDA was available in this environment. |
| Reference vs batched parity | pass | max value diff <= `4.4e-11` in smoke | S0-like and S1-like tests passed. |
| Batch results match single-run loop | pass | Prompt16 test | Two candidates matched reference runs. |
| Leakage-safe target generation | partial | backend only replays targets | Strategy target generation must still use safe inputs. |

| Backend | Device | Candidates | Dates | Runtime Seconds | Speedup vs Reference | Max Metric Diff | Status |
|---|---|---:|---:|---:|---:|---:|---|
| Reference loop | CPU | 1 | 20 | 0.0030 | 1.00 | 0 | correctness source |
| NumPy batched | CPU | 8 | 20 | 0.0038 | 7.05 | `4.4e-11` value diff | useful for bounded grids |
| Torch batched | CUDA | 8 | 20 | 5.9686 | 0.004 | `2.9e-11` value diff | real CUDA, too much overhead at tiny scale |

Interpretation: CUDA acceleration is real but not yet useful at the small Prompt16 benchmark size. The NumPy batched path is the preferred default for quick and medium searches; CUDA should be retested only with much larger candidate batches before promoting it.
