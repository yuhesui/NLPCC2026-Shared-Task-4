# Prompt 03 — Four-Stage Modular Strategy Reorganisation

**Task:** NLPCC 2026 Shared Task 4 — *LLM-based Investment Advisor Agents for Asset Allocation in the Chinese Market*  
**Objective:** Reorganise previously proposed full-strategy designs into a modular, implementation-ready four-stage architecture.

**Decision stance:** Build the system as a deterministic, replaceable pipeline where the LLM or language model is a controlled extractor/verifier, not the final allocator. The final trading decision must be made by a quantitative engine with explicit risk, turnover, fallback, and leakage controls.

---

## A. Four-Stage Architecture Definition

The previous strategy names are useful for discussion but too coarse for implementation. The correct engineering architecture should decompose every design into four separately testable stages:

1. **Stage 1 — News Processing:** raw Top-20 hot news into structured textual signals.
2. **Stage 2 — Quantified Text Data Storage Medium:** structured signals into persistent, queryable quantitative state.
3. **Stage 3 — Trade Data Processing:** official historical prices and portfolio state into market/risk state.
4. **Stage 4 — Final Trading Agent:** text state plus market state into target weights and executable official trades.

| Stage | Purpose | Input | Output | Main Risk | Fallback |
|---|---|---|---|---|---|
| Stage 1 — News Processing | Convert raw daily Top-20 news into typed, validated financial signals. | Timestamp-safe news titles/bodies/rank/source before official cutoff. | Event tuples, sector tags, macro tags, view scores, confidence, horizon, uncertainty flags. | Prompt instability, schema drift, hallucinated event-to-ETF mapping, same-day timestamp misuse. | Rule-based keyword tags + sentiment-only + no-news neutral signal. |
| Stage 2 — Quantified Text Data Storage Medium | Store structured news signals as numerical objects that can be queried, decayed, aggregated, or passed to optimisers. | Stage 1 outputs from current and prior days. | Flat event panel, view matrix, belief vector, event memory, retrieval index, KG, causal graph, confidence matrix. | Over-complex storage that cannot be reproduced or ablated; memory overfits 2024/2025. | Daily flat feature table and neutral view/confidence store. |
| Stage 3 — Trade Data Processing | Convert official historical price, cash, holdings, and prior weights into market state. | Leakage-safe historical price endpoint, current-day open only, previous holdings/cash, previous weights. | Returns, vol, covariance, momentum, drawdown, breadth, risk budgets, turnover capacity, cash feasibility. | Future-price leakage, using current-day close/high/low/return, buy-before-sell execution mismatch. | S0/S1 quant core with inverse-vol, momentum, drawdown, turnover caps. |
| Stage 4 — Final Trading Agent | Combine quantified text state and market state into target weights, then translate target weights into official trades. | Stage 2 text state + Stage 3 market state + previous portfolio. | Target weights, cash/sell/buy instructions, logs, explanations, fallback decisions. | Overfit optimiser, excessive turnover, direct LLM allocation, dependency failure under B-list. | Conservative ensemble or S1 fallback with low-turnover rebalancing. |

### Stage 1 — News Processing

**Purpose.** Reduce unstructured news into typed financial observations. The best Stage 1 module should produce structured JSON records, not prose. Each record should be validated and bounded.

**Allowed data.** Official Top-20 news available under timestamp cutoff; historical prior-day news if supplied through the official loader; pre-2026 frozen dictionaries/models.

**Forbidden data.** Same-day returns/close/high/low; any post-2025 model, external knowledge base, or online API memory; manually added 2026-specific knowledge.

**Success metric.** Schema validity, financial specificity, cross-run stability, ablation contribution versus sentiment-only and no-news baselines.

**Fallback behaviour.** If extraction fails or confidence is low, emit neutral views, low-confidence flags, and allow Stage 4 to collapse to S1.

### Stage 2 — Quantified Text Data Storage Medium

**Purpose.** Make news information persistent and usable by mathematical engines. Stage 2 is not a database convenience layer; it defines the mathematical representation of news.

**Allowed data.** Stage 1 records; historical Stage 1 records; pre-built ETF-sector-policy taxonomy frozen before B-list; pre-2026 local embeddings if submitted.

**Forbidden data.** Any post-2025 retrieval corpus, online vector search, or hidden-period tuning.

**Success metric.** Information retention, queryability, interpretability, clean ablation, and compatibility with Stage 4.

**Fallback behaviour.** Drop to daily flat feature table with neutral confidence.

### Stage 3 — Trade Data Processing

**Purpose.** Build the price/risk backbone before adding news. This stage should be finished before any fancy LLM module.

**Allowed data.** Prior trading days’ OHLCV/returns; current-day open only if officially exposed; previous weights, holdings, cash, and generated trade logs.

**Forbidden data.** Current-day close/high/low/return before decision time; unsafe convenience endpoints that leak current close; future benchmark statistics.

**Success metric.** Correct leakage whitelist, stable baselines, correct turnover/cost accounting, reproducible daily state.

**Fallback behaviour.** Use equal weight, inverse-volatility, momentum, defensive sleeve, and low-turnover constraints.

### Stage 4 — Final Trading Agent

**Purpose.** Allocate capital using deterministic quantitative optimisation. This is where performance is made or lost.

**Allowed data.** Stage 2 text state, Stage 3 market state, previous portfolio state, fixed configs, deterministic random seeds.

**Forbidden data.** Direct unbounded LLM-generated target weights; post-hoc 2025 over-tuning; internet APIs at B-list runtime.

**Success metric.** Turnover-adjusted Sharpe, cumulative return, drawdown, turnover category, B-list crash resistance, clean daily logs.

**Fallback behaviour.** If text confidence, optimiser feasibility, dependency check, or risk check fails, run S1 quant core and log the fallback reason.

---

## B. Stage-Level Candidate Map

### Stage 1 — News Processing Candidates

| Candidate | Originating Full Strategy | Mathematical Object | Output Schema | Track 1 Fit | Track 2 Fit | Keep / Merge / Reject | Reason |
|---|---|---|---|---:|---:|---|---|
| Simple news summarisation | Generic RAG summariser / CPA baseline | Text compression only | `{summary, key_topics}` | 4 | 4 | Baseline only | Useful for human report, weak as quant input; too lossy and not directly optimisable. |
| Sentiment classification | Sentiment-MV, news sentiment baseline | Scalar polarity | `{asset_or_sector, sentiment, confidence}` | 5 | 5 | Baseline only | Necessary control but insufficient for policy, horizon, and cross-asset transmission. |
| Event tuple extraction | TEMA, LEEQA, CEVA-KF | Typed event record | `{event_type, entity, asset_tag, direction, magnitude, horizon, confidence}` | 8 | 8 | Core build | Best general Stage 1 primitive; reusable by BL, memory, graph, causal, and ranker systems. |
| Macro regime classification | BSA-RP, Regime-HMM-RP, HGF-MPC | Observation over latent regime | `{growth, inflation, liquidity, risk_appetite, policy_stance, confidence}` | 9 | 5 | Keep | Strong Track 1 module; should be merged with event extraction, not standalone. |
| Sector impact extraction | KG-MoE, LEEQA, TEMA | Sector impact vector | `{sector, direction, magnitude, horizon, source_weight, confidence}` | 5 | 9 | Core build for Track 2 | Essential for sector rotation; less useful for broad macro baskets. |
| View extraction for Black-Litterman | DRO-BL / simple BL | View vector and confidence | `{P_row, q, omega, view_type, confidence, rationale_id}` | 9 | 7 | Core build | Direct bridge from news to a robust optimiser; must be schema-validated. |
| Causal shock extraction | CEVA-KF / CIRM / CIGA | Directed shock relation | `{cause, channel, affected_sector, sign, lag, invariance_group, confidence}` | 7 | 8 | Report-centrepiece / secondary | High report value but too fragile as first production signal. |
| Entity / sector / ETF mapping | KG-MoE, LEEQA, graph systems | Bipartite mapping | `{entity, sector, ETF, relation_type, confidence}` | 6 | 9 | Core support module | Required by Track 2 and graph systems; should be dictionary-assisted. |
| News denoising and relevance filtering | All structured systems | Relevance mask | `{news_id, relevance_score, duplicate_cluster, noise_flag}` | 8 | 8 | Core support module | Prevents Top-20 public-attention noise from overtrading. |
| LLM self-consistency / verifier extraction | All LLM-dependent systems | Agreement / validity score | `{schema_valid, sign_agreement, confidence_adjustment, reject_reason}` | 8 | 8 | Keep selectively | Improves reliability but increases cost; use offline/cache/frozen local model if possible. |

### Stage 2 — Quantified Text Storage Candidates

| Candidate | Originating Full Strategy | Mathematical Object | Output Schema | Track 1 Fit | Track 2 Fit | Keep / Merge / Reject | Reason |
|---|---|---|---|---:|---:|---|---|
| Daily flat feature table | LEEQA, baseline, all MVPs | Matrix `X_t` | `date × feature columns` | 8 | 8 | Core MVP | First storage to build; easiest to test and ablate. |
| Decayed event memory | BSA-RP, TEMA-RP | Exponential state `m_t = λm_{t-1}+e_t` | `date, event_type, sector, decayed_score` | 8 | 8 | Secondary build | Good balance of memory and simplicity; better than KV memory as first memory layer. |
| Transformer-style key-value event memory | TEMA / RAMA-T | Key-value memory `{K,V}` with attention | `event_key, value_vector, timestamp, decay` | 7 | 8 | Defer / report-centrepiece | Attractive but higher overfit and implementation burden. |
| Retrieval analogue index | ARMOR-SPO / OMD-RAG | Embedding index with historical outcome labels | `embedding, date, analogue_quality, subsequent_return_label` | 6 | 7 | Secondary build | Useful if distance-gated and fallback-safe; not first build. |
| Regime posterior / belief state | BSA-RP, HGF-MPC, Regime-HMM-RP | Probability vector `π_t = P(z_t | history)` | `date, regime_probs, entropy, confidence` | 9 | 6 | Core for Track 1 | Strong mathematical state for macro allocation and risk control. |
| Black-Litterman view store | DRO-BL / simple BL | View matrix `P_t`, view returns `q_t`, uncertainty `Ω_t` | `P, q, Ω, confidence, horizon` | 9 | 7 | Core build | Best direct storage for performance-first robust BL. |
| ETF-sector-policy knowledge graph | KG-MoE, CIGA, graph systems | Dynamic heterogeneous graph | `nodes, edges, edge_type, weight, timestamp` | 6 | 9 | Track-specific build | Strongest Track 2 report asset; build after flat table/mapping stable. |
| Causal event-impact graph | CEVA-KF / CIRM / CIGA | Directed causal graph / SCM | `cause, effect, lag, sign, stability_score` | 7 | 8 | Report-centrepiece | Very strong narrative; should start as diagnostics/verification before allocator core. |
| Text-managed factor panel | LEEQA, factor extraction | Factor exposure matrix | `date × ETF × factor_score` | 8 | 8 | Keep | Good bridge between text and ranker/BL; implement as extension of flat table. |
| Uncertainty / confidence matrix | DRO-BL, verifier systems | Diagonal/block uncertainty matrix | `Ω_t`, `confidence_t`, `source_dispersion` | 9 | 8 | Core support module | Crucial for robust optimisers and fallback gating. |

### Stage 3 — Trade Data Processing Candidates

| Candidate | Originating Full Strategy | Mathematical Object | Output Schema | Track 1 Fit | Track 2 Fit | Keep / Merge / Reject | Reason |
|---|---|---|---|---:|---:|---|---|
| Equal weight state | Baseline ladder | Static vector | `w_equal` | 6 | 6 | Baseline only | Required sanity check and fallback floor. |
| Inverse-volatility state | S1 / risk parity | Volatility vector | `σ_i, inv_vol_weight` | 8 | 7 | Core baseline | Essential risk anchor; low overfit and strong in hidden tests. |
| Multi-horizon momentum | S1, sector trend | Momentum panel | `mom_20, mom_60, mom_120, rank` | 8 | 9 | Core build | Strong baseline and feature source for all final agents. |
| Sector trend state | S1 Track 2 | Sector rank vector | `sector_score, top_k_mask` | 5 | 9 | Core Track 2 | Main hurdle for graph/news systems. |
| Covariance / shrinkage covariance | DRO-BL, MV, risk parity | `Σ_t` | `cov_matrix, corr_matrix, shrinkage_alpha` | 9 | 8 | Core build | Needed for BL, risk parity, drawdown control, and diagnostics. |
| Drawdown state | All robust systems | Drawdown and peak state | `portfolio_dd, asset_dd, risk_off_flag` | 9 | 8 | Core build | Directly aligned with evaluation and B-list survival. |
| Breadth state | S1 Track 1 | Market breadth vector | `breadth, positive_mom_share, defensive_score` | 9 | 6 | Core Track 1 | Simple and robust macro risk-on/risk-off signal. |
| HMM regime state from prices | Regime-HMM-RP, HGF-MPC | Latent price regime posterior | `π_price_t, regime_vol, regime_return` | 8 | 6 | Secondary | Useful but may overfit with short data; keep simple. |
| Graph correlation state | KG-MoE, graph systems | Price correlation graph | `edge_weight_ij, cluster_id` | 6 | 8 | Track-specific | Useful for Track 2 sector clusters and graph MoE; not first baseline. |
| Turnover and cash feasibility state | All final agents | Execution feasibility vector | `prev_w, cash, sell_needed, buy_budget, turnover_limit` | 10 | 10 | Core build | Non-negotiable because official trades are not direct target weights. |
| Baseline allocator performance state | ARMOR-SPO, OCO-Ensemble | Online sleeve performance weights | `sleeve_return, regret, confidence, rolling_sharpe` | 8 | 8 | Secondary | Enables OCO/meta-allocation and fallback selection. |

### Stage 4 — Final Trading Agent Candidates

| Candidate | Originating Full Strategy | Mathematical Object | Output Schema | Track 1 Fit | Track 2 Fit | Keep / Merge / Reject | Reason |
|---|---|---|---|---:|---:|---|---|
| S1 quant core | Baseline / fallback | Hand-crafted quant allocator | `target_weights, reason_codes` | 9 | 9 | Core fallback | First final agent to implement; performance floor and fallback for all systems. |
| Risk parity | BSA-RP / robust RP | Risk-budget solution | `target_weights, risk_contrib` | 8 | 7 | Core component | Robust, interpretable, good with weak text signals. |
| Robust Black-Litterman | DRO-BL / DRO-BL-RP | BL posterior + uncertainty shrinkage | `target_weights, posterior_mu, Ω` | 9 | 7 | Core build | Best Track 1 performance-first engine. |
| Distributionally robust optimiser | DRO-BL, robust MV, RP | Worst-case objective | `target_weights, ambiguity_radius, risk_penalty` | 9 | 7 | Merge with robust BL | Best as a layer inside BL/RP rather than separate first build. |
| Belief-state risk parity | BSA-RP | Regime-weighted risk budgets | `π_t, regime_budget, target_weights` | 9 | 6 | Core/secondary | Best one-student robust research system after S1. |
| Kalman/HMM MPC | HGF-MPC | Filtered latent drift + control | `filtered_mu, control_weight, target_weights` | 9 | 6 | Secondary build | Strong mathematical Track 1 system but more complex than BSA-RP. |
| Graph MoE | KG-MoE | Dynamic graph + expert router | `expert_weights, sector_scores, target_weights` | 6 | 9 | Track-specific build | Best Track 2 research/performance candidate, but only after mapping is stable. |
| Retrieval meta-allocator | ARMOR-SPO / OMD-RAG | Analogue-weighted sleeve ensemble | `analogue_weights, sleeve_mix, target_weights` | 7 | 8 | Secondary | Good fallback-safe system if retrieval quality gating is strict. |
| Online mirror descent / OCO | OCO-Bandit / OCO-Ensemble | No-regret sleeve update | `sleeve_weights, regret, target_weights` | 8 | 8 | Core support / fallback | Useful as ensemble layer rather than standalone alpha generator. |
| Learning-to-rank allocator | LEEQA | Cross-sectional ranker | `asset_rank, score, top_k_weights` | 6 | 8 | Secondary / ablation | Good for Track 2, but must be risk-wrapped. |
| Causal invariant allocator | CEVA-KF / CIRM / CIGA | Invariant event-impact model | `causal_score, invariant_mask, target_weights` | 7 | 8 | Report-centrepiece | Best report idea; not first submission engine unless simple. |
| Conservative ensemble | Final production stack | Rule-gated blend | `system_weights, fallback_flag, target_weights` | 9 | 9 | Core production | Final B-list submission should likely be an ensemble with hard fallback. |
| Direct LLM allocator | Pure LLM allocator / CPA control | Unbounded text-to-trade policy | `freeform trades/weights` | 2 | 2 | Reject | Prompt-sensitive, weak risk control, poor reproducibility; keep only as rejected baseline. |

---

## C. Stage-Level Quantitative Comparison

Scores are **ex ante architecture scores**, not realised backtest results. They should be treated as build-priority scores before empirical validation.

### Stage 1 — News Processing Scoring

| Candidate | Extraction Accuracy | Prompt Stability | Schema Validity | Financial Specificity | Noise Filtering | Track 1 Fit | Track 2 Fit | Cost | Reproducibility | Overall Stage 1 Score |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Simple news summarisation | 5 | 6 | 6 | 4 | 4 | 4 | 4 | 2 | 7 | 4.8 |
| Sentiment classification | 6 | 7 | 8 | 5 | 5 | 5 | 5 | 3 | 8 | 5.9 |
| Event tuple extraction | 8 | 7 | 8 | 8 | 7 | 8 | 8 | 5 | 7 | 7.4 |
| Macro regime classification | 7 | 7 | 8 | 8 | 6 | 9 | 5 | 4 | 8 | 7.1 |
| Sector impact extraction | 7 | 6 | 8 | 8 | 7 | 5 | 9 | 5 | 7 | 7.0 |
| View extraction for Black-Litterman | 7 | 6 | 8 | 9 | 6 | 9 | 7 | 5 | 7 | 7.2 |
| Causal shock extraction | 6 | 5 | 7 | 9 | 7 | 7 | 8 | 6 | 6 | 6.7 |
| Entity / sector / ETF mapping | 8 | 8 | 9 | 8 | 7 | 6 | 9 | 4 | 8 | 7.7 |
| News denoising and relevance filtering | 8 | 8 | 9 | 7 | 9 | 8 | 8 | 3 | 9 | 8.1 |
| LLM self-consistency / verifier extraction | 7 | 7 | 9 | 8 | 8 | 8 | 8 | 7 | 7 | 7.4 |

**Stage 1 decision.** The best practical Stage 1 stack is **news denoising + event tuple extraction + entity/ETF mapping + BL-view extraction where needed**. Sentiment and summarisation should remain baselines only.

### Stage 2 — Quantified Text Storage Scoring

| Candidate | Information Retention | Temporal Memory | Mathematical Cleanliness | Queryability | Robustness | Interpretability | Reproducibility | Track 1 Fit | Track 2 Fit | Overall Stage 2 Score |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Daily flat feature table | 6 | 3 | 9 | 9 | 8 | 9 | 10 | 8 | 8 | 7.8 |
| Decayed event memory | 8 | 8 | 8 | 8 | 8 | 8 | 9 | 8 | 8 | 8.1 |
| Transformer-style key-value event memory | 9 | 9 | 6 | 8 | 6 | 6 | 6 | 7 | 8 | 7.2 |
| Retrieval analogue index | 8 | 7 | 7 | 9 | 7 | 7 | 7 | 6 | 7 | 7.3 |
| Regime posterior / belief state | 7 | 8 | 9 | 7 | 8 | 9 | 8 | 9 | 6 | 8.0 |
| Black-Litterman view store | 8 | 5 | 9 | 8 | 8 | 9 | 8 | 9 | 7 | 8.1 |
| ETF-sector-policy knowledge graph | 9 | 8 | 7 | 8 | 7 | 8 | 6 | 6 | 9 | 7.6 |
| Causal event-impact graph | 9 | 8 | 8 | 7 | 7 | 9 | 6 | 7 | 8 | 7.6 |
| Text-managed factor panel | 8 | 6 | 8 | 9 | 8 | 8 | 9 | 8 | 8 | 8.0 |
| Uncertainty / confidence matrix | 7 | 5 | 9 | 8 | 9 | 9 | 9 | 9 | 8 | 8.2 |

**Stage 2 decision.** Build in this order: **daily flat feature table → uncertainty matrix / BL view store → decayed event memory → regime posterior → knowledge graph / retrieval index**. Do not start with KV memory.

### Stage 3 — Trade Data Processing Scoring

| Candidate | Predictive Usefulness | Leakage Safety | Risk Relevance | Turnover Usefulness | Robustness | Simplicity | Track 1 Fit | Track 2 Fit | Overall Stage 3 Score |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Equal weight state | 4 | 10 | 5 | 7 | 8 | 10 | 6 | 6 | 7.0 |
| Inverse-volatility state | 7 | 10 | 9 | 8 | 9 | 9 | 8 | 7 | 8.5 |
| Multi-horizon momentum | 8 | 9 | 7 | 7 | 7 | 8 | 8 | 9 | 7.9 |
| Sector trend state | 8 | 9 | 6 | 7 | 7 | 8 | 5 | 9 | 7.4 |
| Covariance / shrinkage covariance | 7 | 9 | 10 | 7 | 8 | 7 | 9 | 8 | 8.1 |
| Drawdown state | 7 | 10 | 10 | 8 | 9 | 8 | 9 | 8 | 8.6 |
| Breadth state | 7 | 9 | 8 | 7 | 8 | 8 | 9 | 6 | 7.8 |
| HMM regime state from prices | 7 | 8 | 8 | 6 | 6 | 5 | 8 | 6 | 6.8 |
| Graph correlation state | 6 | 9 | 8 | 6 | 7 | 6 | 6 | 8 | 7.0 |
| Turnover and cash feasibility state | 8 | 10 | 10 | 10 | 10 | 8 | 10 | 10 | 9.5 |
| Baseline allocator performance state | 7 | 9 | 7 | 9 | 8 | 7 | 8 | 8 | 7.9 |

**Stage 3 decision.** Build Stage 3 before any advanced text work. The non-negotiable modules are **turnover/cash feasibility**, **drawdown state**, **inverse-vol**, **multi-horizon momentum**, and **shrinkage covariance**.

### Stage 4 — Final Trading Agent Scoring

| Candidate | Sharpe Potential | Drawdown Control | Turnover Efficiency | B-list Robustness | Mathematical Depth | Interpretability | Feasibility | Report Signal | Overfit Risk | Overall Stage 4 Score |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| S1 quant core | 7 | 8 | 8 | 9 | 5 | 8 | 10 | 5 | 3 | 7.9 |
| Risk parity | 6 | 9 | 8 | 9 | 6 | 9 | 9 | 6 | 3 | 8.0 |
| Robust Black-Litterman | 8 | 8 | 7 | 8 | 9 | 9 | 7 | 8 | 5 | 8.0 |
| Distributionally robust optimiser | 8 | 9 | 7 | 8 | 9 | 8 | 6 | 8 | 5 | 7.9 |
| Belief-state risk parity | 7 | 9 | 8 | 8 | 8 | 9 | 7 | 8 | 5 | 8.0 |
| Kalman/HMM MPC | 8 | 8 | 7 | 7 | 9 | 8 | 6 | 8 | 6 | 7.5 |
| Graph MoE | 8 | 7 | 6 | 6 | 8 | 7 | 5 | 9 | 7 | 6.9 |
| Retrieval meta-allocator | 7 | 7 | 8 | 8 | 7 | 8 | 7 | 8 | 5 | 7.6 |
| Online mirror descent / OCO | 7 | 7 | 8 | 8 | 8 | 8 | 8 | 8 | 5 | 7.8 |
| Learning-to-rank allocator | 7 | 6 | 6 | 6 | 7 | 7 | 6 | 8 | 7 | 6.4 |
| Causal invariant allocator | 7 | 7 | 6 | 7 | 9 | 9 | 5 | 10 | 7 | 7.1 |
| Conservative ensemble | 8 | 9 | 9 | 9 | 7 | 9 | 8 | 8 | 4 | 8.5 |
| Direct LLM allocator | 3 | 2 | 2 | 2 | 2 | 3 | 5 | 4 | 9 | 2.2 |

**Stage 4 decision.** The production endpoint should be **S1 + robust BL/BSA-RP + conservative ensemble/fallback**. Graph MoE and causal invariant systems are report-rich but should not be first submission engines.

---

## D. Cross-Stage Compatibility Matrix

Scores measure architectural compatibility between Stage 2 storage media and Stage 4 final agents.

| Stage 2 Storage Medium \ Stage 4 Agent | S1 quant core | Risk parity | Robust BL | Belief-state RP | HMM / Kalman MPC | Graph MoE | Retrieval meta | OCO / mirror descent | Learning-to-rank | Causal invariant |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Daily flat feature table | 8 | 7 | 7 | 6 | 6 | 6 | 6 | 8 | 9 | 6 |
| Decayed event memory | 7 | 8 | 8 | 9 | 8 | 7 | 7 | 8 | 7 | 7 |
| Key-value event memory | 5 | 5 | 6 | 7 | 7 | 7 | 8 | 6 | 7 | 6 |
| Retrieval analogue index | 5 | 5 | 5 | 6 | 6 | 6 | 10 | 9 | 8 | 6 |
| Regime posterior / belief state | 7 | 9 | 8 | 10 | 10 | 6 | 6 | 7 | 5 | 7 |
| Black-Litterman view matrix | 4 | 6 | 10 | 7 | 7 | 5 | 5 | 6 | 5 | 6 |
| Knowledge graph | 4 | 5 | 6 | 5 | 5 | 10 | 7 | 6 | 8 | 8 |
| Causal event-impact graph | 4 | 6 | 7 | 7 | 8 | 8 | 6 | 6 | 7 | 10 |

### Compatibility conclusions

1. **Best high-performance pairings.**
   - BL view matrix → robust BL.
   - Regime posterior → belief-state RP or HMM/Kalman MPC.
   - Daily flat feature table → S1/OCO/ranker.
   - Decayed event memory → BSA-RP or robust BL with time-decayed views.

2. **Best research-report pairings.**
   - Knowledge graph → graph MoE.
   - Causal event-impact graph → causal invariant allocator.
   - KV event memory → retrieval/meta-allocator or TEMA-style allocator.
   - Regime posterior → HGF-MPC with belief plots.

3. **Best one-student pairings.**
   - Daily flat feature table → S1 quant core / OCO ensemble.
   - BL view matrix → robust BL.
   - Decayed event memory → risk parity.
   - Regime posterior → BSA-RP if HMM implementation is kept simple.

4. **Incompatible pairings to avoid.**
   - Knowledge graph → robust BL as first design: graph state does not naturally produce `P, q, Ω` without an extra translation layer.
   - BL view matrix → graph MoE: view matrices are too aggregated for edge-level routing.
   - Key-value memory → direct BL: attention memory needs compression into views before BL can use it.
   - Causal graph → simple ranker: loses causal structure and produces a weak report narrative.

5. **Pairings that sound good but are redundant.**
   - Regime posterior + HMM/Kalman MPC can duplicate Stage 3 price-HMM if both are independently fitted.
   - Decayed event memory + retrieval index can be redundant if retrieval only returns recent similar events without adding analogue outcome information.
   - Knowledge graph + causal graph can become two inconsistent graph stores unless causal edges are explicitly a typed subset of the KG.

---

## E. Final Modular System Designs

Each system is expressed as a four-stage pipeline:

```text
News Processing
→ Quantified Text Storage Medium
→ Trade Data Processing
→ Final Trading Agent
```

| System | Stage 1 News Processing | Stage 2 Text Storage | Stage 3 Trade Processing | Stage 4 Final Agent | Track Fit | Main Edge | Main Risk | Build Priority |
|---|---|---|---|---|---|---|---|---|
| M1 — Performance-first Track 1 Robust BL | Denoising + macro/event extraction + BL view extraction | BL view matrix + confidence/uncertainty matrix | Shrinkage covariance + inverse-vol + drawdown + turnover/cash feasibility | Robust BL + RP anchor + S1 fallback | T1 very strong, T2 medium | Best risk-controlled way to turn news into macro views | Bad view extraction can harm posterior means | 1 |
| M2 — Performance-first Track 2 Graph-Rank | Denoising + entity/sector/ETF mapping + sector impact extraction | Flat sector factor panel → lightweight ETF-sector-policy KG | Sector trend + covariance + graph correlation + turnover state | Sector trend S1 + graph/ranker tilt + conservative ensemble | T1 medium, T2 very strong | Track 2 policy-to-sector transmission | KG/MoE can overfit and underperform simple trend | 4 |
| M3 — Best One-Student Robust BSA-RP | Denoising + event extraction + macro regime classification | Decayed event memory + regime posterior | Inverse-vol + drawdown + breadth + turnover state | Belief-state risk parity + S1 fallback | T1 strong, T2 moderate | Robust, interpretable, visually reportable | Regime posterior may be weak with short sample | 2 |
| M4 — Best Research/Award Causal Graph | Causal shock extraction + entity/sector mapping + verifier | Causal event-impact graph + factor panel | Covariance + drawdown + sector trend + baseline states | Causal invariant allocator or causal verifier gating S1/BL | T1 medium, T2 strong | Strongest system-report thesis | Implementation burden and causal overclaiming | 5 |
| M5 — Fallback-safe OCO Ensemble | Denoising + basic event tuple/sentiment | Daily flat feature table + uncertainty flags | Baseline allocator performance state + turnover/cash feasibility | OCO/mirror descent over S1, RP, momentum, defensive, BL sleeves | Both strong fallback | Learns which sleeve works while limiting crash risk | Slow adaptation; may not beat best single sleeve | 3 |
| M6 — Highest-upside TEMA/Retrieval Memory | Event extraction + embedding/event tagging + verifier | Decayed memory + retrieval analogue index or KV memory | Momentum + covariance + analogue outcome stats + turnover | Retrieval meta-allocator / TEMA-RP with distance-gated fallback | T1 medium, T2 strong | Novel transformer-memory/analogue narrative | High overfit and dependency risk | 6 |
| M7 — Ablation/Control System | Summarisation + sentiment classification | Daily flat sentiment table | Inverse-vol + momentum + no advanced state | Sentiment score-to-weight with risk caps | Both weak/moderate | Clean control for paper | Not likely to beat S1 | Control only |

### M1 — Performance-first Track 1 Robust BL

**Pipeline.**

```text
News denoising + macro/event extraction + BL view extraction
→ BL view matrix (P_t, q_t, Ω_t)
→ shrinkage covariance, inverse-vol, drawdown, turnover/cash feasibility
→ robust Black-Litterman with RP anchor and S1 fallback
```

**Coherence.** Stage 1 directly emits the mathematical objects Stage 4 needs: view matrix `P_t`, view returns `q_t`, and uncertainty `Ω_t`. Stage 3 supplies the risk model. Stage 4 shrinks noisy text views into a robust posterior.

**Swappable parts.** View extractor can be replaced with event-to-view rules; BL can be replaced by RP-only if views are low confidence; DRO radius can be disabled for ablation.

**Fallback.** If `max confidence < threshold`, `Ω_t` ill-conditioned, or BL target violates risk constraints, use S1 quant core.

**Evaluation.** Must beat S1 on 2024 walk-forward turnover-adjusted Sharpe and remain stable in at least three subwindows.

### M2 — Performance-first Track 2 Graph-Rank

**Pipeline.**

```text
Entity/sector/ETF mapping + sector impact extraction
→ sector factor panel + lightweight ETF-sector-policy graph
→ sector trend, graph correlation, covariance, turnover state
→ conservative graph/ranker tilt over S1 sector trend
```

**Coherence.** Track 2 is sector-sensitive. Stage 1 maps policy/entity events to sectors; Stage 2 stores this as either a factor panel or graph; Stage 3 supplies sector trend; Stage 4 only tilts the strong sector trend baseline instead of replacing it.

**Swappable parts.** Full KG-MoE can be downgraded to factor-panel ranker; graph correlation can be removed; sector trend can dominate under low confidence.

**Fallback.** If graph signal contradicts trend without high confidence, use sector trend S1 top-k.

**Evaluation.** Must show incremental value over sector trend-following, especially in policy-sensitive ETFs.

### M3 — Best One-Student Robust BSA-RP

**Pipeline.**

```text
Event extraction + macro regime classification
→ decayed event memory + regime posterior
→ inverse-vol, breadth, drawdown, turnover/cash feasibility
→ belief-state risk parity with defensive S1 fallback
```

**Coherence.** This is the cleanest student-buildable system: text contributes a low-dimensional regime belief, not high-dimensional direct alpha. Stage 4 changes risk budgets rather than making aggressive return forecasts.

**Swappable parts.** Regime posterior can be rule-based first, then HMM-filtered later. Risk parity can be replaced by inverse-vol in MVP.

**Fallback.** If regime entropy is high or classifier confidence is low, use neutral risk budgets from inverse-vol/S1.

**Evaluation.** Must reduce drawdown or improve turnover-adjusted Sharpe versus S1, even if raw return gain is modest.

### M4 — Best Research/Award Causal Graph

**Pipeline.**

```text
Causal shock extraction + entity/sector mapping + verifier
→ causal event-impact graph
→ covariance, drawdown, sector trend, baseline performance
→ causal invariant allocator or causal gate over S1/BL
```

**Coherence.** The system-report thesis is strong: not all news correlations are stable; use typed causal channels and invariance checks to decide when text should affect allocation.

**Swappable parts.** Keep causal graph as diagnostic/verifier first; only promote to allocator if ablations show value.

**Fallback.** If causal stability score is low, block text-driven active tilts and use S1.

**Evaluation.** Report selection can be justified if causal filters prevent bad trades under distribution shift, even without top Sharpe.

### M5 — Fallback-safe OCO Ensemble

**Pipeline.**

```text
Basic event extraction / sentiment + uncertainty flags
→ flat feature table
→ rolling performance of S1, RP, momentum, defensive, BL sleeves
→ OCO / mirror descent ensemble with turnover penalty
```

**Coherence.** This system does not need the text signal to be perfect. It treats every allocator as a sleeve and learns conservative sleeve weights online.

**Swappable parts.** Any new allocator can become a sleeve; OCO can be replaced by fixed ensemble weights.

**Fallback.** If OCO weights become unstable, clamp to S1/RP blend.

**Evaluation.** Must beat the average sleeve and ideally approach the best sleeve without higher drawdown.

### M6 — Highest-upside TEMA/Retrieval Memory

**Pipeline.**

```text
Event extraction + event embedding + verifier
→ decayed memory + retrieval analogue index / KV memory
→ analogue outcome statistics + covariance + turnover
→ TEMA/Retrieval meta-allocator with distance-gated fallback
```

**Coherence.** This is the most “LLM-architecture-inspired” system: attention/retrieval is used as a market-memory mechanism, not as free-form generation.

**Swappable parts.** Use decayed event memory as MVP; only add vector retrieval if embeddings are stable.

**Fallback.** If analogue distance is high or neighbour outcomes disagree, ignore retrieval and run S1/BL.

**Evaluation.** Must show memory/retrieval beats same-day flat features and that high-distance fallback prevents large losses.

### M7 — Ablation/Control System

**Pipeline.**

```text
Summary + sentiment classification
→ daily flat sentiment table
→ inverse-vol + momentum
→ sentiment score-to-weight with hard caps
```

**Coherence.** This is not a submission target. It is the control that proves event extraction, view confidence, memory, graph, or causal structure adds value beyond naïve text polarity.

**Fallback.** Always fallback-cap to inverse-vol.

**Evaluation.** Should probably be beaten by M1/M3/M5. If it beats them, the advanced modules are over-engineered.

---

## F. Stage-Specific Ablation Plan

| System | Critical Stage | Required Ablation | Expected Effect | Red Flag if... |
|---|---|---|---|---|
| M1 — Robust BL | Stage 1 + Stage 2 + Stage 4 | Replace BL view extraction with sentiment-only; set `Ω_t` constant; remove robust/DRO penalty; S1 fallback only. | Sentiment-only should be noisier; no robustness should increase drawdown/turnover; fallback should reduce active return but improve stability. | No-LLM or sentiment-only performs the same, meaning BL views add no value. |
| M2 — Graph-Rank | Stage 1 + Stage 2 | Remove entity/sector mapping; use flat sector table; no graph edges; no sector trend input. | Removing graph should hurt policy-sensitive sector allocation but not break the system. | Full KG-MoE cannot beat sector trend top-k. |
| M3 — BSA-RP | Stage 2 + Stage 4 | No regime posterior; no decayed memory; static risk parity; no volatility scaling. | Regime posterior should improve drawdown timing; no vol scaling should worsen drawdown. | Regime classifier changes allocation often but does not improve risk-adjusted returns. |
| M4 — Causal Graph | Stage 1 + Stage 2 | Replace causal shock extraction with event tuples; remove invariance filter; causal graph used for explanation only. | Causal filter should reduce bad text tilts; explanation-only version should remain competitive. | Causal labels are unstable, unverifiable, or purely rhetorical. |
| M5 — OCO Ensemble | Stage 3 + Stage 4 | Fixed equal sleeve mix; no OCO update; no turnover penalty; no text features. | OCO should beat fixed mix or adaptively avoid bad sleeves; no turnover penalty should overtrade. | OCO underperforms best single sleeve and raises turnover. |
| M6 — TEMA/Retrieval | Stage 2 | Same-day only; flat feature table instead of memory; random retrieval neighbours; no distance gate. | Memory should beat same-day; distance gate should prevent novel-event mistakes. | Random retrieval performs similarly to semantic retrieval. |
| M7 — Sentiment Control | Stage 1 | No news; event extraction instead of sentiment; inverse-vol only. | Event extraction should dominate sentiment; no-news should reveal price-only floor. | Sentiment control beats all structured systems, implying over-engineering. |

### Minimum ablation package

1. **Competition submission minimum.**
   - Equal weight, inverse-vol, momentum, sector trend, low-turnover persistence, S1 quant core.
   - Final system with and without text signal.
   - Final system with and without turnover control.
   - S1 fallback-only replay.

2. **System report minimum.**
   - No-news, no-LLM, sentiment-only, flat-feature-only, no-risk-control, no-turnover-control, no-final-optimiser.
   - For selected architecture: no BL/no DRO for M1, no regime/no memory for M3, no graph/no router for M2, no causal/no invariance for M4, no retrieval/no OCO for M5/M6.

3. **Debugging minimum.**
   - Stage 1 schema error rate.
   - Stage 2 daily state diff and null-rate report.
   - Stage 3 leakage whitelist test.
   - Stage 4 target-weight-to-official-trade reconciliation.

4. **B-list hardening minimum.**
   - Offline-only dependency check.
   - Deterministic seed and cache replay.
   - Crash fallback test.
   - Low-confidence fallback test.
   - Maximum turnover and maximum position-limit guard.

---

## G. Implementation Repository Mapping

Recommended repo structure:

```text
src/nlpcc4/
  data_contract/
  news_processing/
  text_store/
  trade_processing/
  agents/
  portfolio/
  execution/
  reports/
  evaluation/
  utils/

configs/
  data_contract/
  news_processing/
  text_store/
  trade_processing/
  agents/
  systems/
  evaluation/

tests/
  test_data_contract/
  test_news_processing/
  test_text_store/
  test_trade_processing/
  test_agents/
  test_portfolio/
  test_execution/
  test_systems/

artifacts/
  daily_states/
  ablations/
  backtests/
  reports/
  figures/
```

### Directory responsibilities

| Directory | Responsibility | Inputs | Outputs | Should Not Contain | Test Files | Report Artifacts |
|---|---|---|---|---|---|---|
| `src/nlpcc4/data_contract/` | Safe wrappers around official data; leakage whitelist; date split policy. | Official loader/server outputs. | Safe daily observation object. | Models, prompts, optimiser logic. | `test_safe_fields.py`, `test_date_splits.py` | leakage audit table. |
| `src/nlpcc4/news_processing/` | Stage 1 extraction, denoising, schema validation, mapping. | Safe news records. | Structured event/view/sector JSON. | Portfolio weights or price-derived labels. | `test_schema_validity.py`, `test_mapping_rules.py` | extraction quality report, invalid-record log. |
| `src/nlpcc4/text_store/` | Stage 2 stores: flat table, BL views, event memory, KG, retrieval. | Stage 1 structured outputs. | Queryable text state per date. | Raw official price processing. | `test_view_store.py`, `test_event_memory.py`, `test_kg_edges.py` | state plots, view-confidence maps. |
| `src/nlpcc4/trade_processing/` | Stage 3 market/risk state: returns, vol, covariance, momentum, drawdown, turnover. | Safe prices, holdings, cash, prior trades. | Market state object. | LLM prompts, event extraction. | `test_no_future_prices.py`, `test_covariance.py`, `test_turnover_state.py` | baseline statistics, risk diagnostics. |
| `src/nlpcc4/agents/` | Stage 4 allocators: S1, RP, BL, BSA-RP, OCO, graph/ranker, causal gate. | Text state + market state. | Target weights and reason codes. | Raw data-loading or execution semantics. | `test_s1_agent.py`, `test_bl_agent.py`, `test_oco_agent.py` | agent comparison tables. |
| `src/nlpcc4/portfolio/` | Weight normalisation, caps, volatility scaling, turnover penalty, fallback gates. | Target weights, risk state, config. | Feasible target portfolio. | News text processing. | `test_caps.py`, `test_turnover_penalty.py`, `test_fallback.py` | risk contribution charts. |
| `src/nlpcc4/execution/` | Convert target weights into official buy/sell trade instructions. | Feasible target portfolio + current holdings/cash. | Official trade list. | Alpha logic. | `test_trade_adapter.py`, `test_buy_before_sell.py` | trade reconciliation logs. |
| `src/nlpcc4/evaluation/` | Backtest metrics, walk-forward, ablation runner, scoring. | Daily logs and portfolio values. | Sharpe, return, drawdown, turnover tables. | Online model calls. | `test_metrics.py`, `test_walkforward.py` | A-list package tables. |
| `src/nlpcc4/reports/` | Generate markdown/figures/system report artifacts. | Evaluation outputs and daily traces. | `.md`, `.csv`, `.png` artifacts. | Strategy code. | `test_report_generation.py` | final report pack. |

### Config mapping

```text
configs/
  data_contract/
    official_safe_fields.yaml
    date_splits.yaml
  news_processing/
    event_schema.yaml
    extractor_rules.yaml
    llm_extractor_local.yaml
    sector_mapping.yaml
  text_store/
    flat_table.yaml
    bl_view_store.yaml
    event_memory.yaml
    kg_store.yaml
    retrieval_index.yaml
  trade_processing/
    risk_features.yaml
    covariance.yaml
    momentum.yaml
    turnover.yaml
  agents/
    s1_core.yaml
    robust_bl.yaml
    bsa_rp.yaml
    graph_rank.yaml
    oco_ensemble.yaml
    causal_gate.yaml
  systems/
    m1_track1_robust_bl.yaml
    m2_track2_graph_rank.yaml
    m3_bsa_rp.yaml
    m5_oco_fallback.yaml
  evaluation/
    walkforward.yaml
    ablations.yaml
    report_pack.yaml
```

| Stage | Source Directory | Config Directory | Tests | Reports |
|---|---|---|---|---|
| Stage 0 / Data Contract | `src/nlpcc4/data_contract/` | `configs/data_contract/` | `tests/test_data_contract/` | `artifacts/reports/leakage_audit.md` |
| Stage 1 — News Processing | `src/nlpcc4/news_processing/` | `configs/news_processing/` | `tests/test_news_processing/` | `artifacts/reports/news_extraction_quality.md` |
| Stage 2 — Text Storage | `src/nlpcc4/text_store/` | `configs/text_store/` | `tests/test_text_store/` | `artifacts/daily_states/text_state/`, `artifacts/figures/view_confidence/` |
| Stage 3 — Trade Processing | `src/nlpcc4/trade_processing/` | `configs/trade_processing/` | `tests/test_trade_processing/` | `artifacts/reports/baseline_risk_report.md` |
| Stage 4 — Final Agents | `src/nlpcc4/agents/`, `src/nlpcc4/portfolio/`, `src/nlpcc4/execution/` | `configs/agents/`, `configs/systems/` | `tests/test_agents/`, `tests/test_portfolio/`, `tests/test_execution/` | `artifacts/backtests/`, `artifacts/ablations/` |
| Evaluation / Reports | `src/nlpcc4/evaluation/`, `src/nlpcc4/reports/` | `configs/evaluation/` | `tests/test_systems/` | `artifacts/reports/final_system_report.md` |

---

## H. Recommended Build Order

The build order must not begin with sophisticated text models. Build the market-state and official execution pipeline first, because a flawed Stage 3/4 execution layer invalidates all news experiments.

| Phase | Focus Stage | Deliverable | Time Estimate | Success Criterion | Stop Criterion |
|---|---|---|---:|---|---|
| Phase 0R — Reset and Data Contract | Data contract before Stage 1–4 | Frozen official repo commit, safe-field whitelist, date split policy, no-leakage loader wrapper, official timestamp tests. | 1–2 student-days | Every daily observation excludes current-day close/high/low/return and includes only timestamp-safe news. | Any ambiguity in safe fields or official trade semantics remains unresolved. |
| Phase 1R — Official Starter Reproduction | Official environment + execution | Reproduce official starter backtest for both tracks; save daily logs; verify buy/sell schema and cost accounting. | 2–3 student-days | Local replay produces stable logs and correct metric computation. | Backtester/session/trade adapter cannot be reproduced. |
| Phase 2R — Stage 3 Trade Data Processing + S0/S1 Baselines | Stage 3 + simple Stage 4 | Implement equal weight, inverse-vol, momentum, sector trend, low-turnover persistence, S1 quant core, drawdown, turnover, covariance. | 4–6 student-days | Baseline report with 2024 walk-forward Sharpe/return/drawdown/turnover by track. | S1 cannot beat or at least sensibly dominate naïve baselines. |
| Phase 3R — Stage 1 News Processing MVP | Stage 1 | Build denoising, event tuple extraction, entity/sector/ETF mapping, BL-view extraction schema, validator. | 3–5 student-days | >95% schema-valid extraction; deterministic replay; low invalid mapping rate. | Extraction is unstable, unbounded, or requires online API at runtime. |
| Phase 4R — Stage 2 Text Storage MVP | Stage 2 | Build daily flat table, BL view store, uncertainty matrix, and decayed event memory. | 3–5 student-days | Text state can be replayed date-by-date and joined to Stage 3 without leakage. | Store cannot reproduce exactly or cannot support ablations. |
| Phase 5R — Stage 4 Final Agent Prototype | Stage 4 | Build M1 robust BL first, with RP anchor, turnover penalty, and S1 fallback. | 4–7 student-days | M1 beats or nearly matches S1 on 2024 walk-forward after costs and has lower/equal drawdown in weak periods. | Robust BL underperforms S1 badly and ablations show no useful view signal. |
| Phase 6R — Integrated Modular Systems and Ablations | All stages | Add M3 BSA-RP and M5 OCO ensemble; run modular ablations; optionally begin Track 2 M2 graph-rank. | 5–8 student-days | At least one text-aware system clears promotion gate; ablation tables are report-ready. | No text module adds value; lock to S1/OCO fallback and report negative result. |
| Phase 7R — A-list Package and B-list Hardening | Production | Docker, dependency lock, local cache/frozen models, deterministic seeds, crash fallback, final report pack. | 4–6 student-days | One final system passes offline replay, no-internet test, fallback test, and 2025 sparse evaluation. | Any system requires external API, unstable runtime, or post-2025 resources. |

### First prototype choice

The first full four-stage prototype should be **M1 — Performance-first Track 1 Robust BL**, because it has the cleanest module boundary:

```text
validated news views → (P, q, Ω) store → covariance/risk state → robust BL/RP optimiser
```

It also creates reusable infrastructure for later systems: event extraction, confidence matrices, covariance, turnover feasibility, and fallback gates.

### Second prototype choice

The second prototype should be **M3 — Best One-Student Robust BSA-RP**, not KG-MoE yet. It reuses the Stage 1 extractor and Stage 3 risk core while testing a different storage object: regime posterior / decayed memory. It is more implementable than full graph MoE and more B-list robust than TEMA.

### Track 2 extension

After M1 and M3, build **M2 — Track 2 Graph-Rank** in a restrained form: start with sector factor panel + mapping + sector trend tilt. Only add a full dynamic KG/MoE if the flat factor panel improves over sector trend.

---

## I. Final Decision

```text
## Final Modular Recommendation

- Best Stage 1 news processing method:
  News denoising and relevance filtering + event tuple extraction + entity/sector/ETF mapping + BL-view extraction. Use schema-validated deterministic JSON, not prose summaries.

- Best Stage 2 quantified text storage medium:
  First: daily flat feature table + BL view matrix + uncertainty/confidence matrix.
  Second: decayed event memory / regime posterior.
  Later: ETF-sector-policy knowledge graph only after mapping and sector factor panel are stable.

- Best Stage 3 trade data processing method:
  Turnover/cash feasibility state + inverse-volatility + multi-horizon momentum + shrinkage covariance + drawdown/breadth state. This must be built before advanced news systems.

- Best Stage 4 final trading agent:
  Conservative ensemble anchored by S1, with robust Black-Litterman/RP as the first text-aware allocator and hard fallback to S1 when text confidence, optimiser feasibility, or risk checks fail.

- First complete four-stage system to build:
  M1 — Performance-first Track 1 Robust BL.
  Pipeline: denoised event/view extraction → BL view/confidence store → covariance/drawdown/turnover state → robust BL + RP anchor + S1 fallback.

- Second system to build:
  M3 — Best One-Student Robust BSA-RP.
  Pipeline: event/regime extraction → decayed event memory + regime posterior → inverse-vol/breadth/drawdown/turnover state → belief-state risk parity + S1 fallback.

- Best Track 1 system:
  M1 Robust BL for performance; M3 BSA-RP for robustness and interpretability.

- Best Track 2 system:
  M2 Graph-Rank, but only in staged form: sector impact extraction → sector factor panel/light KG → sector trend + graph correlation → conservative sector tilt over S1 top-k trend.

- Best research / award system:
  M4 Causal Graph if built as a verifier and interpretability layer; M6 TEMA/Retrieval Memory if the team wants the most architecture-novel narrative. Neither should be the first production submission engine.

- Best fallback if text signal is weak:
  M5 OCO Ensemble over S1, inverse-vol, risk parity, momentum, defensive, and robust-BL sleeves; or pure S1 if OCO fails promotion gates.

- Modules to reject:
  Direct LLM allocator, generic RAG summariser as allocator, simple sentiment-to-weight allocator, multi-agent debate, heavy fine-tuning, deep RL/graph RL as first build, and any runtime external-API-dependent component.

- Modules to keep only as ablations:
  Simple summarisation, sentiment classification, simple BL without robustness, LLM-only CPA-style control, flat feature table without memory, no-turnover-control optimiser, no-risk-control optimiser, and causal graph as explanation-only if allocation value is not proven.

- System report thesis:
  A robust modular investment-agent architecture where daily Chinese financial news is converted into validated quantitative state objects, combined with leakage-safe market/risk states, and passed into deterministic risk-aware allocators with explicit uncertainty, turnover, and fallback controls. The central contribution is not “LLM predicts trades,” but “LLM-derived information is made auditable, storable, ablatable, and safely usable by classical quantitative portfolio engines.”
```
