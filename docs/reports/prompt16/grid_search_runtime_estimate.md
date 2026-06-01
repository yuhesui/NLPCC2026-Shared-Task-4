# Prompt16 Grid Search Runtime Estimate

Benchmark basis: 20 macro dates, 11 assets. Reference replay: 0.0030 s for 1 candidate. NumPy batched replay: 0.0038 s for 8 candidates. Torch CUDA replay: 5.9686 s for 8 candidates at tiny scale, so CUDA is not recommended until larger batches prove useful.

| Scenario | Candidates | Dates | Folds | Backend | HF Mode | Estimated Runtime | Feasible Overnight? | Notes |
|---|---:|---:|---:|---|---|---:|---|---|
| quick target replay | 100 | 485 | 1 | NumPy batched | cached/no HF | < 1 min | yes | Replay-only estimate; strategy generation not included. |
| medium target replay | 1000 | 485 | 1 | NumPy batched | cached/no HF | ~1 min | yes | Uses measured batch unit cost plus overhead allowance. |
| five-fold target replay | 1000 | 485 | 5 | NumPy batched | cached/no HF | ~5 min | yes | Good first robustness run after target tensors exist. |
| reference-loop replay | 1000 | 485 | 5 | reference local | cached/no HF | ~6-10 min | yes | Correct but slower; useful for spot parity. |
| tiny-benchmark CUDA extrapolation | 1000 | 485 | 5 | Torch CUDA | cached/no HF | > 20 h | no | Tiny benchmark is overhead dominated; retest with larger tensors before use. |
| HF uncached grid | 100 | 485 | 1 | LocalSmoke/SystemRunner | uncached BGE/FinBERT | high/unknown | no | Prompt15 already showed local-model inference was runtime-expensive. |
| HF cached grid | 1000 | 485 | 5 | NumPy replay after cached features | cached HF features | ~6-15 min replay, plus cache build | yes | Cache build must be benchmarked separately. |

Recommended search tiers:

1. Quick search under 30 minutes: <= 100 candidates, 2024 only, rule-based Stage 1, NumPy batched replay.
2. Medium search under 3 hours: <= 1000 candidates, five-fold target replay, cached text features only.
3. Overnight search: <= 5000 candidates, five-fold replay plus selected reference spot checks.
4. Full research search: add local HF feature cache construction, then rerun only if cache build is bounded and reproducible.
