# NLPCC (AlphaAllocator) → ICAIF audit

Source: `yuhesui/NLPCC2026-Shared-Task-4` at branch head `be69433` (898 files; `src/nlpcc` ≈ 22.2k LOC,
`src/tools` ≈ 5.0k, `scripts/` ≈ 12.5k, `tests/` ≈ 1.8k). The old repository was **not modified**.
Nothing was copied wholesale: every reused idea was re-implemented in `src/icaif/` with fresh tests.

Classification: **R** reuse nearly as-is · **A** adapt · **I** reimplement for ICAIF · **RO** research-only · **X** archive / do not port.

## Repo-level facts that shaped the migration

* Data and model files in the old repo are Git LFS pointers; nothing data-driven runs without an LFS pull. No data was migrated.
* `.gitignore` ignored `/tests/`, `/scripts/`, `/data/`, `/outputs/` while they were force-tracked. Not copied.
* The submission wrappers import modules missing from the repo (`phase12_final_agent`, `prompt09_real_transformer_agent`).
* `NLPCC_tasks/nlpcc/` is a vendored copy of 26 modules from `src/nlpcc`.
* **Fee 10× lower** in NLPCC (0.0001 in `evaluation/reference_official_semantics.py:24` and the backtest tools) vs ICAIF 0.001.
* All logic assumed daily decisions with `YYYYMMDD` ints, a 15:00 China cutoff and "current-day open only" visibility.

## Component table

| old path | old purpose | class | ICAIF replacement path | required changes | risk / caveat |
|---|---|---|---|---|---|
| `src/nlpcc/core/leakage_guard.py` | reject future bars, current-day close/high/low, same-day news ≥15:00 | A→I | `core/leakage_guard.py`, `data/point_in_time.py`, `data/market/panel.py` | single invariant `available_at ≤ decision_time`; per-round timestamps; model-cutoff and label-purge guards | none known; covered by `tests/leakage` |
| `src/nlpcc/core/data_contracts.py` | frozen dataclasses (RawNewsItem, PriceBar, PricePanel…) | A | `core/schemas.py` | add event/published/available/retrieved times + provenance; drop `TrackName`, `date_int`, order payloads | — |
| `src/nlpcc/core/fund_universe.py` | 11 macro + 16 sector Chinese funds per track | I | `core/universe.py` | 30-ticker official universe, parity-tested | — |
| `src/nlpcc/portfolio/target_weights.py` | normalise/blend; proportional water-filling projection | A | `portfolio/constraints.py` (`scale_to_capped_simplex`, new exact `project_capped_simplex`) | all-zero scores no longer silently become equal weight (`on_zero` explicit) | — |
| `src/nlpcc/portfolio/risk_parity.py` | multiplicative ERC fixed point from inverse-vol | A→I | `portfolio/risk_parity.py` | default rewritten as cyclical coordinate descent (convex); legacy kept as `method="multiplicative"`; explicit gross | legacy update fails to converge with mixed-sign correlations (`tests/portfolio`) |
| `src/nlpcc/portfolio/turnover_control.py` | one-way turnover (0.5·L1) cap by blending | A | `portfolio/turnover.py` | two-sided L1 (ICAIF metric), band, sparse, min-change HOLD, per-day budget | mixing one-/two-sided definitions would mis-scale caps 2× |
| `src/nlpcc/portfolio/constraints.py` | max 0.35, 3% cash reserve, turnover 0.25 | A | `portfolio/constraints.py` | 0.30 cap enforced, gross free in [0,1], no reserve default | — |
| `src/nlpcc/portfolio/robust_optimizer.py` | projected-gradient MV with anchor penalty | A→I | `portfolio/optimizer.py` | exact L1 turnover penalty via FISTA + exact prox; cost-aware γ | alpha scale must be calibrated (Grinold) |
| `src/nlpcc/portfolio/black_litterman.py` | BL posterior from text views (Chinese asset groups) | RO | — (planned research) | asset groups removed | not ported yet |
| `src/nlpcc/stage3_trade/models/shrinkage_covariance.py` | fixed-α shrink to avg-variance diagonal | A | `features/covariance.py` | kept as `fixed`; added Ledoit-Wolf, constant-correlation, EWMA, PSD repair | NLPCC Track A used α=0.05 (tuned on daily ETFs) |
| `stage3_trade/models/{covariance,inverse_volatility,momentum,breadth,drawdown}.py` | sample cov, IV, windowed momentum, breadth, drawdown | A | `features/{covariance,volatility,momentum,regime}.py`, `portfolio/inverse_vol.py` | horizons in trading hours (1h…20d), NaN-aware | — |
| `stage3_trade/models/{kalman_drift,price_hmm_state,stable_effect_estimator,base_allocator_performance,correlation_graph,sector_trend}.py` | drift filter, threshold regime, effect stability, expert perf, corr graph, sector trend | RO | (future `models/regime`, `models/alpha`) | — | not ported |
| `stage3_trade/models/cash_feasibility.py`, `portfolio/position_sizing.py`, `execution/*` | NLPCC buy-cash/sell-% order planning | X | ICAIF uses target weights only | — | — |
| `stage3_trade/models/rank_training_labels.py` | forward-return rank labels | A | `features/returns.forward_returns`, `models/text/linear.py` | label windows purged at split boundaries | — |
| `src/nlpcc/stage4_agent/models/s1_quant_core.py`, `s0_equal_weight_agent.py`, `risk_parity_agent.py` | no-news baselines; frozen Track A primary (RP w10, shrink 0.05, cap 0.325, cash 0.021) | A | `configs/systems/q0..q3*.yaml` | config-driven pipelines; NLPCC hyper-parameters not inherited | — |
| `stage4_agent/models/leeqa_rank_agent.py` | momentum/IV/sentiment score → top-k softmax (k=5, T=0.35; frozen Track B primary) | A | `models/alpha/selection.topk_softmax` (+hysteresis) | 30-stock cross-section; k/T are research parameters | NLPCC values are a start point only |
| `stage4_agent/models/armor_omd_agent.py`, `oco_ensemble_agent.py` | exponentiated-gradient / OCO expert ensembles | A | `models/ensemble/expert_weights.py` | causal updates from realised period returns; lr not inherited | not yet wired into a system config |
| other `stage4_agent/models/*` (robust_bl, dro_bl_rp, bsa_rp, kg_moe, hgf_mpc, ceva_kf, sector_rotation, …) | MVP research allocators | RO / X | — | — | broad `except → S1` patterns |
| `stage4_agent/models/rejected_direct_llm_allocator.py`, `NLPCC_tasks/agent_platform/agents/advanced_agents.py` | direct LLM trading agents | RO | `llm/tasks.direct_allocation` (refused unless enabled) | experimental baseline only | — |
| `src/nlpcc/runtime/decision_trace.py` | immutable trace + fallback events | R→A | `runtime/decision_trace.py` | per-round sections answering the 11 trace questions; secret redaction | — |
| `src/nlpcc/runtime/fallback_manager.py` | primary → validate → fallback with trace | A | `runtime/agent.py`, `runtime/fallback.py`, `runtime/safety.py` | ordered chain; only anticipated errors fall back; strict mode re-raises; terminal HOLD | old version caught every `Exception` |
| `src/nlpcc/runtime/dependency_guard.py` | `find_spec` dependency checks | R | `nlp/embeddings` (`ModelUnavailable`) | explicit at model construction | — |
| `src/nlpcc/runtime/system_runner.py` | track alias table, hand-written YAML parser, agent zoo | I | `core/config.py` (PyYAML + `extends`), `runtime/agent.build_agent` | — | — |
| `src/nlpcc/news_overlay/base.py`, `model_availability.py`, `transformer_features.py`, `config.py`, `registry.py` | N/I/S method specs, availability statuses, offline provider | A | `nlp/embeddings.py` (`EncoderSpec`, `check_policy`), `configs/embeddings/registry.yaml` | `requires_rule_confirmation`; no Track codes; no `.var/...` defaults | — |
| `src/nlpcc/news_overlay/tensor_overlay.py` | news tensor (BGE/FinBERT or hash proxy) + bounded overlay (gates, deadband, caps, turnover guard) | A | `nlp/feature_store.py`, `portfolio/fusion.py` | exact zero-sum Δw, L1 budget, event/confidence/vol/regime budgets, 6 transforms, gross preserved | old: hard-coded `~/.cache/huggingface/...zh` paths, Chinese cues, `except Exception: return 0.65` recency, renormalise-to-1, hash "encoder proxy" used silently |
| `src/nlpcc/news_overlay/production_tensor.py` | fail-closed real-transformer provider, overlay normalised to 0.97 | A | same + `nlp/embeddings.LocalSentenceEncoder` | fail-closed kept; fixed 0.97 removed | Windows paths `C:\Users\jeanna\...` (lines 28-34) not carried |
| `src/nlpcc/news_overlay/hf_models.py` | approved-model YAML, revision pins, download-once | A (schema) | `configs/embeddings/registry.yaml` | no download code at all in this repo | hard-coded Windows HF cache (line 14) |
| `news_overlay/n_methods/architectures.py` | lexical/bi-encoder/aspect tone/label-attention/cross-encoder/temporal attention | A (interfaces) | `nlp/relevance.py`, `nlp/event_extraction.LabelAttentionEventMatcher`, `nlp/sentiment.py` | English, asset profiles, model-agnostic `Encoder` | temporal attention not yet ported |
| `news_overlay/s_methods/architectures.py`, `i_methods/architectures.py` | sensitivity matrices, rank-IC gate, event priors (China sectors) | RO | `nlp/event_impact.py` + `configs/news/event_priors.yaml` | US event taxonomy; priors marked uncalibrated | — |
| `news_overlay/optimisation/{scoring,typec_splitter}.py` | robust score; purged blocked folds | R→A | `backtest/walk_forward.py`, registry | purge + embargo; locked final test | robust score not ported (use official metrics) |
| `news_overlay/grid_evaluator.py` | grid runner with checkpoint and shuffled-news ablation | A | `experiments/{runner,matrix,ablations}.py` | deterministic IDs; 9 ablations + component variants | — |
| `news_overlay/{cli,prompt21..23_runner,track_a_*,track_b_*}.py` | prompt-numbered runners | X | — | — | heavy Track coupling |
| `src/nlpcc/stage1_news/*` | Chinese normalisation, keyword extractors, sector maps, BL views | A (interfaces) / I (lexicons) | `nlp/{preprocessing,entity_linking,sentiment,event_extraction}.py` | English, ticker linking with ambiguity rules, HTML/zero-width cleaning, near-dup clustering | — |
| `stage1_news/text_feature_store.py`, `cache.py` | content-addressed feature cache | A | `nlp/feature_store.ArticleFeatureCache` | key includes model ids + config hash; model cutoff check | old silent `except ValueError: continue` |
| `stage1_news/local_model_loader.py`, `text_model_config.py` | offline HF path resolution | A | `nlp/embeddings.LocalSentenceEncoder` | explicit `local_path`, `HF_HUB_OFFLINE=1`, `local_files_only` | — |
| `stage1_news/models/{bge_small_zh,finbert_tone_chinese}_extractor.py` | Chinese encoders | X | registry entries marked `unsuitable` | — | language mismatch |
| `src/nlpcc/stage2_text_store/models/decayed_event_memory.py` | half-life memory (5 days) | A | `nlp/recency.py` | event-specific τ, wall/trading clock, raises on future items | — |
| `stage2_text_store/models/{event_table,confidence_matrix,flat_feature_table}.py` | event merge, clamps, flat features | A | `nlp/feature_store.TextState` | per-asset arrays with evidence | — |
| `stage2_text_store/models/{knowledge_graph,retrieval_index,belief_state,causal_event_graph,…}` | research stores | RO / X | — | — | — |
| `src/nlpcc/evaluation/reference_official_semantics.py` | NLPCC replay + metrics (252 periods, 0.98 invested) | I | `backtest/engine.py`, `competition/evaluation.py` | ICAIF period accounting, √1764 Sharpe, drawdown on endpoints + closes | — |
| `src/tools/backtesting/metrics.py` | Sharpe/MDD/turnover | A | `competition/evaluation.py`, `backtest/metrics.py` | official definitions; extra diagnostics separate | — |
| `src/tools/backtesting/{vectorized,cuda_vectorized,batched_grid}_backtester.py` | batched candidate replay | RO | — (future fast path) | must be re-validated against `backtest/engine.py` | — |
| `src/tools/experiments/{experiment_config,result_store,target_tensor_cache}.py` | config hashing, JSON store | R→A | `experiments/registry.py`, `core/config.config_hash` | deterministic IDs, evidence grades, duplicate-result refusal | — |
| `src/tools/experiments/leakage_safe_input_builder.py` | per-day masked inputs | A | `MarketPanel.as_of`, `PITStore` | per-round | — |
| `src/tools/optimiser/*` (grid/random/successive halving/walk-forward/promotion) | HPO primitives | R (later) | — | not needed for the first baselines | promotion must use downstream PIT evidence |
| `src/tools/data_tools/manifest_builder.py` | sha256 + LFS detection | A | `data/provenance.py` | manifest hash in every experiment record | — |
| `src/tools/verification/*`, `reporting/*` | audits, reports | A (ideas) | `experiments/reporting.py`, `docs/FINAL_REPO_AUDIT.md` | — | — |
| `NLPCC_tasks/agent_platform/agents/build_agent.py`, track wrappers | official-facing NLPCC wrappers | X | `runtime/scheduler.py` + official ICAIF client | — | wrappers import missing modules |
| `NLPCC_tasks/server_platform/**`, `dataset/**`, `package/**` | NLPCC server, LFS data/models | X | — | — | — |
| `configs/systems/*`, `configs/tracks/*`, `configs/preserved_candidates/**` | frozen Track A/B selections | X (record) | — | winners noted above as history only | NLPCC-tuned |
| `configs/stage3_trade/*.yaml`, `configs/stage4_agent/*.yaml` | parameter defaults | A (values reconsidered) | `configs/{risk,portfolio,systems}/` | ICAIF defaults | — |
| `configs/news_overlay/approved_hf_models.yaml`, `local_models*.yaml` | approved Chinese models with Windows paths | A (schema only) | `configs/embeddings/registry.yaml` | every entry replaced | — |
| `tests/test_nlpcc/**` | core/portfolio/runtime/stage tests | A (ideas) | `tests/{leakage,portfolio,runtime,nlp}` | fresh tests (159) | old tests write to `outputs/` |
| `scripts/run_prompt*.py`, `prompt23_launch.py`, … | prompt-numbered runners, PowerShell `Stop-Process` | X | `scripts/{experiments,backtest,live}/` | — | — |
| `docs/prompts/**` (108), `docs/implementation_logs/**` (55), `outputs/**`, `docs/archived/**` | prompt packs, logs, generated results | X | — | not migrated | — |
| `docs/research/**`, `docs/architecture/**`, `METHODOLOGY.md` | design notes, frozen decisions | RO | `docs/research/*` (rewritten) | bounded-news philosophy preserved | — |

## Hazards found in `src/nlpcc` and how they are avoided

| Hazard (examples) | Avoided by |
|---|---|
| Hard-coded Windows paths: `news_overlay/hf_models.py:14`, `production_tensor.py:28-34`, `prompt21_runner.py:28`, `prompt22_runner.py:38` | no default model paths; `local_path` must be configured; `ModelUnavailable` otherwise |
| Hard-coded HF cache snapshots: `tensor_overlay.py:35-52` | same |
| Silent fallbacks: `tensor_overlay.py:555` / `production_tensor.py:503` (`except Exception: return 0.65`), `gpu.py:28`, hash "encoder proxy" | `recency.age_hours` raises; HashingEncoder labelled `is_transformer=False`; fallback classes explicit |
| Broad `except Exception → S1` in ~11 agents | `runtime/fallback.classify_exception`; strict mode for research/tests |
| Track A/B coupling (`core/fund_universe.py`, `normalize_track`, `TRACK_A_*` sets) | single universe; no track concept |
| Fixed 2-day half-life (`tensor_overlay.py:141,162`, `production_tensor.py:496`) | event-specific τ (`configs/news/event_priors.yaml`) |
| Fixed ~0.97/0.98 gross (`production_tensor.py:553`, `grid_evaluator.py:676`, cash reserve 0.03) | explicit `exposure` config; experiment family `exposure_policies` includes `fixed_97_nlpcc` as a comparator |
| Chinese models/lexicons (bge-small-zh, finbert-tone-chinese, Erlangshen, CJK cue lists) | English pipeline; Chinese models marked `unsuitable` |
| NLPCC dataset layouts (`price_data/{fund}.csv`, uppercase `TITLE/CONTENT/PUBLISH_TIME`) | `data/market/loaders.py` CSV contract with `available_at`; `data/news/sources.py` JSONL contract |
