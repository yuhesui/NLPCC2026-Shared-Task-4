# Initial experiment matrix

Machine-readable source: `configs/experiments/initial_matrix.yaml` (expanded by
`experiments/matrix.py`; run with `scripts/experiments/run_matrix.py`). Every concrete experiment
gets a deterministic id `<family>.<name>.<digest>` and a record under `outputs/experiments/`.

| Family | Variants | Purpose | Status |
|---|---|---|---|
| quant_baselines | Q0 cash, Q0 EW, Q1 buy&hold, Q2 IV, Q3 shrinkage ERC, Q4 momentum 5d, Q5 vol-scaled momentum, Q6 multi-horizon trend + ERC, Q7 turnover-aware optimizer, Q8 dynamic exposure | quant core reference set | runnable (synthetic) |
| momentum_horizons | 1h, 2h, 4h, 1d, 5d, 20d | horizon vs cost trade-off | runnable (synthetic) |
| covariance_estimators | sample, fixed α, Ledoit-Wolf, constant correlation, EWMA | risk model choice | runnable (synthetic) |
| exposure_policies | fixed 100 / 97 (NLPCC) / 80, vol target 15% / 10%, regime, drawdown guard | is fixed ~97% optimal? | runnable (synthetic) |
| turnover_controls | unaware, light, standard, strict sparse, rebalance R1+R4 only | fee/turnover-metric trade-off | runnable (synthetic) |
| nlp_relevance | lexical entity, dense hash, hybrid hash; *blocked*: bge-small-en, Qwen3-Embedding, fine-tuned bi-encoder, cross-encoder, LLM judge | relevance method | partly runnable; rest blocked_local_model / blocked_rule / blocked_real_data |
| nlp_components | no text, relevance only, sentiment only, market sentiment, event only, relevance+sentiment, relevance+event, full structured | which text component matters | runnable (synthetic) |
| overlay_caps | η = 0, 0.005, 0.01, 0.02, 0.04 | overlay magnitude | runnable (synthetic) |
| overlay_transforms | linear, rank, softmax, sigmoid, z-score, top-k | score → tilt mapping | runnable (synthetic) |
| overlay_recency | event priors (wall / trading clock), fixed 6h, fixed 48h, no decay | decay design | runnable (synthetic) |
| overlay_budget_modes | none, confidence, confidence+event, event | adaptive budget | runnable (synthetic) |
| overlay_turnover_awareness | unaware vs aware | does text churn the book? | runnable (synthetic) |
| text_ablations | no_news, zeroed, shuffled, wrong_asset, random, stale 24h, stale 120h, sign flip, full | incremental-value tests | runnable (synthetic) |
| source_removal | all sources vs drop one source | source dependence | runnable (synthetic) |
| planted_signal_recovery | planted impact 0.15/0.40/0.80%/bar × no_news, full, sign_flip, shuffled | detection power of the NLP plumbing | runnable (synthetic) |
| embedding_models | registry candidates (EMBEDDING_MODEL_PLAN E1–E5) | encoder comparison | blocked_local_model |
| llm_extraction | allowed hosted/open models as event extractors / relevance judges; direct allocation baseline | LLM value | blocked_rule (no client, credits, disclosure plan) |

Portfolio dimension is covered across families: fixed vs vol-target vs regime exposure
(exposure_policies), risk parity (Q3/Q8), penalised optimizer (Q7).

## Evidence status

**No configuration has real-market evidence.** The default data source is the seeded synthetic world,
and every such result is graded `synthetic_plumbing` in the registry. To produce evidence: supply
point-in-time bars/news (DATA_PROVENANCE.md), set `defaults.data` to the CSV data config, run
walk-forward windows, and compare against the quant controls.
