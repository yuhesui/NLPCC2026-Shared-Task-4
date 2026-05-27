<img src="https://r2cdn.perplexity.ai/pplx-full-logo-primary-dark%402x.png" style="height:64px;margin-right:32px"/>

# \# Role and Objective

You are a quantitative finance researcher, LLM-systems architect, and competition strategy analyst.

Your task is to conduct an in-depth research analysis for NLPCC 2026 Shared Task 4: “LLM-based Investment Advisor Agents for Asset Allocation in the Chinese Market.”

Official repository:
[https://github.com/splash-li/NLPCC2026-Shared-Task-4/](https://github.com/splash-li/NLPCC2026-Shared-Task-4/)

You must design at least 5 highly distinct, mathematically serious, award-worthy system architectures for this task.

Do not produce generic LLM-agent brainstorming.
Do not blindly recommend using the strongest LLM API.
Do not propose direct “LLM says buy/sell” systems unless only as a rejected baseline.
Focus on novel, mathematically principled, reproducible designs that could plausibly produce both:

1. competitive Sharpe / drawdown / turnover performance, and
2. a strong system-report / shared-task-paper narrative.

The output should be useful for deciding what to implement.

---

# Context

The task is a daily asset-allocation competition using Chinese financial hot news and ETF/index price data.

Known task facts to verify from official sources:

- The task has two tracks:
    - Track 1: Macro-Asset Allocation.
    - Track 2: Sector-Rotation Allocation.
- Agents receive daily Top-20 financial hot news and historical price data.
- Agents produce daily rebalancing / trading decisions for predefined ETF pools.
- The official backtesting engine has 0.01% transaction friction.
- Public 2024 data is used for training / agent construction.
- Public 2025 data is the A-list / Phase A evaluation data.
- 2026-01-01 to 2026-06-01 is private B-list blind evaluation.
- Current-day close/high/low/return must not be used before decision time.
- Same-day news is available only under official timestamp rules, before the cutoff.
- Models, external datasets, and knowledge bases must be available before 2026.
- B-list evaluation is run centrally by the organisers using submitted code.
- System reports / shared-task paper inclusion may reward not only top performance but also creative, informative architectures.

Verify these facts from official sources before analysis.

---

# Required Source Use

You MUST browse and inspect primary sources.

Minimum official sources to inspect:

1. Repository root README.
2. `NLPCC_tasks/README.md`.
3. `NLPCC_tasks/dataset/README.md`.
4. `NLPCC_tasks/server_platform/app/core/data_loader.py`.
5. `NLPCC_tasks/server_platform/app/core/backtest.py`.
6. `NLPCC_tasks/dataset/dataloader_eval.py`.
7. Any official FAQ / Q\&A / demonstration notes available in the repo or linked material.
8. Any official shared-task schedule or registration material if available.

Then search recent and foundational research papers.

Required research-paper areas:

1. LLM agents for financial decision-making.
2. News-driven asset allocation.
3. Text-conditioned portfolio optimisation.
4. Event-based trading and event memory.
5. Retrieval-augmented generation for finance.
6. Representation learning for financial text.
7. Temporal transformers / state-space models for time series.
8. Graph neural networks / knowledge graphs for sector and asset relations.
9. Black-Litterman, risk parity, robust portfolio optimisation, distributionally robust optimisation.
10. Online convex optimisation, universal portfolios, bandits, reinforcement learning for portfolio allocation.
11. Mixture-of-experts, routing, attention mechanisms, memory mechanisms, transformer internals, recurrent/state-space memory, toolformer-style modular control.
12. Causal representation learning, invariant risk minimisation, counterfactual reasoning, and causal graphs in finance.
13. Bayesian filtering, hidden Markov models, particle filters, Kalman filters, and belief-state modelling.

Use papers from arXiv, SSRN, ACL/EMNLP, NeurIPS, ICML, ICLR, KDD, WWW, AAAI, IJCAI, Quantitative Finance, Journal of Portfolio Management, and similar sources when possible.

Do not rely only on blog posts.

---

# Central Design Philosophy

You should search for architectural ideas, not just tools.

For each possible system, ask:

- What mathematical object represents market belief?
- What is the state variable?
- What is the update rule?
- What is the portfolio construction rule?
- What is the risk-control rule?
- What part, if any, uses an LLM?
- Which part borrows from LLM architecture internals?
- Can the method run reproducibly on official B-list data?
- Can it be ablated cleanly?
- Can it survive hidden 2026 distribution shift?
- Would it produce a strong system-report narrative?

Do not blindly use LLM APIs as an oracle.
Instead, consider whether components of LLM architectures can be repurposed:

- attention as event-to-asset relevance weighting,
- key-value memory as market event memory,
- retrieval as historical analogue search,
- MoE routing as regime-dependent allocator routing,
- chain-of-thought-like decomposition as hidden modular reasoning but with structured outputs,
- transformer positional decay as news half-life modelling,
- contrastive representation learning as event embedding,
- self-consistency as uncertainty estimation,
- tool-use as deterministic portfolio optimisation,
- verifier models as leakage / consistency / hallucination guards.

---

# Required Design Families

You must propose at least 5 final designs, but you should initially consider at least 10 candidates.

Your final designs must include, at minimum, one strong candidate from each group:

1. Belief-state / memory-based agent.
2. Graph / knowledge-based sector or ETF relation agent.
3. Robust portfolio-optimisation / risk-theory-driven agent.
4. LLM-structured event extraction + quantitative allocator.
5. Learning-to-rank or meta-allocation model.
6. Regime-switching or hidden-state model.
7. Retrieval / analogue-market agent.
8. Online-learning or bandit-style allocator.
9. Causal or counterfactual event-impact model.
10. Transformer-inspired architecture that does not merely call a large API.

You may merge or reject designs later, but you must explicitly consider them.

---

# Design Output Requirements

For each proposed design, include:

## 1. Name

Give the design a concise technical name.

Examples:

- BSA-RP: Belief-State Agent with Risk-Parity Control.
- KG-MoE: Knowledge-Graph Mixture-of-Experts Allocator.
- DRO-BL: Distributionally Robust Black-Litterman Agent.
- TEMA: Transformer Event Memory Allocator.


## 2. One-Sentence Thesis

State the core idea.

## 3. Novelty Claim

Explain what makes it more novel than:

- a pure LLM allocator,
- a normal momentum strategy,
- a simple sentiment strategy,
- a standard RAG system.


## 4. Mathematical State Representation

Specify the state variable.

Examples:

- decayed event-memory vector,
- latent regime posterior,
- graph node embeddings,
- robust expected-return ambiguity set,
- belief vector over macro states,
- event-to-ETF impact matrix,
- posterior distribution over sector tilts.

Use formulas where useful.

## 5. Update Rule

Specify how the state evolves daily.

Examples:

- Bayesian update,
- exponential decay,
- attention-weighted event aggregation,
- Kalman filter,
- hidden Markov model filtering,
- online mirror descent,
- contrastive embedding update,
- graph message passing,
- robust posterior shrinkage.


## 6. LLM Role

Classify the LLM role precisely:

- event extraction,
- news denoising,
- entity/sector mapping,
- regime classification,
- uncertainty estimation,
- explanation generation only,
- verifier,
- not used.

The LLM should not be the uncontrolled allocator unless as a rejected baseline.

## 7. Non-LLM Engine

Specify the real engine:

- risk parity,
- Black-Litterman,
- robust mean-variance,
- HMM,
- graph neural net,
- online convex optimisation,
- rank model,
- Bayesian filter,
- transformer-like memory,
- causal graph,
- mixture-of-experts.


## 8. Portfolio Construction

Give exact formulas or algorithmic steps.

Must include:

- score-to-weight conversion,
- volatility scaling,
- concentration limits,
- turnover control,
- drawdown control,
- fallback baseline.


## 9. Data Use and Leakage Safety

Specify:

- which fields from price data are used,
- how news is used,
- how the 15:00 cutoff is respected,
- how 2024 and 2025 are separated,
- how 2026 resources are excluded,
- what cannot be used.


## 10. Track Fit

Score separately:

- Track 1 fit, 0–10.
- Track 2 fit, 0–10.

Explain why.

## 11. Implementation Plan

Break into:

- MVP version,
- strong version,
- report-ready version.

Estimate effort in student-days.

## 12. Failure Modes

Include at least:

- overfitting 2025,
- future leakage,
- hallucinated causal reasoning,
- excessive turnover,
- unstable event-to-asset mapping,
- hidden 2026 regime shift,
- prompt sensitivity,
- non-reproducibility,
- weak incremental value over S1 baseline.


## 13. Ablation Plan

For each design, define ablations:

- no LLM,
- no news,
- no memory,
- no risk control,
- no turnover control,
- no graph/retrieval/regime module,
- baseline fallback only,
- quant-only,
- LLM-only,
- 2024-tuned vs 2025-tuned.


## 14. Paper / Award Narrative

Explain why this design could be interesting even if not first on Sharpe.

---

# Quantitative Benchmarking Requirement

You must build a quantitative comparison framework.

Use at least these criteria:


| Criterion | Description |
| :-- | :-- |
| Track 1 Fit | Macro-asset allocation suitability |
| Track 2 Fit | Sector-rotation suitability |
| Sharpe Potential | Expected ability to improve risk-adjusted returns |
| Drawdown Control | Expected max-drawdown robustness |
| Turnover Efficiency | Expected cost-aware trading discipline |
| B-list Robustness | Expected hidden-2026 generalisation |
| Novelty | Architectural/research novelty |
| Mathematical Depth | Depth of modelling / optimisation |
| Interpretability | Explainable daily decisions |
| Reproducibility | Ease of Docker/code evaluation |
| Implementation Feasibility | One-student feasibility |
| Baseline Beating Probability | Probability of beating strong S1/S0 baselines |
| Report / Paper Signal | Likelihood of being selected as creative/informative |
| Overfit Risk | Higher means worse |
| Tool Dependency Risk | Higher means worse |
| Data Compliance Risk | Higher means worse |

Use 0–10 scores.

Use this provisional formula:

Overall Research-Competition ROI =
0.12 * max(Track1Fit, Track2Fit)

+ 0.12 * SharpePotential
+ 0.08 * DrawdownControl
+ 0.07 * TurnoverEfficiency
+ 0.12 * BListRobustness
+ 0.11 * Novelty
+ 0.10 * MathematicalDepth
+ 0.08 * Interpretability
+ 0.07 * Reproducibility
+ 0.08 * Feasibility
+ 0.08 * BaselineBeatingProbability
+ 0.10 * ReportPaperSignal
- 0.08 * OverfitRisk
- 0.04 * ToolDependencyRisk
- 0.03 * DataComplianceRisk

Use the full score range where justified.
Be conservative.
Do not give high scores to fragile ideas just because they sound novel.

Also compute two sub-scores:

1. Competition Score:
    - prioritise Sharpe, drawdown, turnover, B-list robustness, baseline beating.
2. Research/Award Score:
    - prioritise novelty, mathematical depth, interpretability, report value, reproducibility.

---

# Baseline Challenge

Every design must be compared against:

1. Equal weight.
2. Inverse-volatility allocation.
3. Momentum-only.
4. Sector trend-following.
5. Persistence / low-turnover baseline.
6. Rule-based macro rotation.
7. News sentiment only.
8. S1 quant core:
    - Track 1 inverse-vol/momentum/breadth/defensive allocator.
    - Track 2 sector trend-following top-k allocator.

State exactly what each design must prove to justify implementation.

Minimum promotion threshold:

- Must beat S1 on 2024 walk-forward or provide clear research novelty.
- Must not materially worsen turnover-adjusted Sharpe.
- Must remain stable across multiple 2024 subwindows.
- Must not require 2026-or-later data, models, or knowledge.
- Must produce reproducible logs and ablation evidence.
- Must have a credible path to running under B-list central evaluation.

---

# Required Final Output Structure

Use exactly the following sections:

A. Official Task Constraints and Research Opportunity
B. Research Source Ledger
C. Candidate Design Universe
D. Five to Eight Final Design Blueprints
E. Mathematical Formulation of Each Design
F. Quantitative Comparison Table
G. Competition Score vs Research/Award Score
H. Baseline-Beating and Ablation Plan
I. Hidden B-List Robustness Audit
J. Implementation Roadmap
K. Final Recommendation

---

# A. Official Task Constraints and Research Opportunity

Summarise the task constraints using citations.

Clearly distinguish:

- official facts,
- inferred implications,
- still-uncertain points.

---

# B. Research Source Ledger

Create a table:

| Source | Type | What it contributes | Reliability | How it affects design |

Include official sources and research papers.

---

# C. Candidate Design Universe

List at least 10 candidate designs before consolidation.

For each:

- name,
- core idea,
- main mathematical engine,
- LLM role,
- likely track fit,
- keep / merge / reject / defer,
- reason.

---

# D. Five to Eight Final Design Blueprints

Present 5–8 final designs.

Each must be genuinely distinct.

---

# E. Mathematical Formulation of Each Design

Give formulas, not just prose.

At minimum include:

- state variable,
- update rule,
- score-to-weight rule,
- risk control,
- turnover control.

---

# F. Quantitative Comparison Table

Use the required score columns and ROI formula.

---

# G. Competition Score vs Research/Award Score

Create a 2-axis interpretation:

- high competition + high research,
- high competition + low research,
- low competition + high research,
- low competition + low research.

State which designs are likely award-winning even if not top Sharpe.

---

# H. Baseline-Beating and Ablation Plan

Define exact benchmarks and ablations.

---

# I. Hidden B-List Robustness Audit

Assess 2026 hidden-period risks:

- regime shift,
- prompt instability,
- dependency risk,
- macro event novelty,
- sector label drift,
- data compliance,
- overfitting 2025.

---

# J. Implementation Roadmap

Give phased build plan:

- Phase 0R: source/data reset.
- Phase 1R: official starter reproduction.
- Phase 2R: baselines.
- Phase 3R: first innovative prototype.
- Phase 4R: full comparison.
- Phase 5R: A-list package.
- Phase 6R: B-list hardening.

---

# K. Final Recommendation

Give:

1. best performance-first design,
2. best research/award design,
3. best one-student design,
4. best Track 1 design,
5. best Track 2 design,
6. designs to reject,
7. exact first implementation target,
8. exact fallback if novelty underperforms.

Be decisive.

A. Official Task Constraints and Research Opportunity
-----------------------------------------------

**Verified official facts**

From the task README and starter kit:

- **Two tracks.**
    - Track 1: Macro-Asset Allocation over ~11 broad ETFs/indices (CSI 300, CSI 500, ChiNext, STAR 50, consumer, new energy, media, nonferrous, energy, treasury bond index, gold ETF).
    - Track 2: Sector-Rotation Allocation over ~14 sector/industry ETFs (securities, banking, insurance, semiconductors, AI, communication equipment, software, pharma, healthcare, innovative drugs, F\&B, liquor, nonferrous, coal, chemicals, real estate).
- **Inputs and timing.**
    - Daily *Top-20 Financial Hot News* sourced from Sina Finance, Tiantian Fund, Tencent Finance/Stock, Caixin.
    - Daily OHLCV-style ETF/index data with `open, close, high, low, volume, pctchange` plus adjusted-price fields where available.
    - Official `DataLoader.get_historical_prices` returns full history for past $lookback\_days-1$ trading days, plus **only the current-day open; close/high/low/%change are set to None** for current day, preventing future-price leakage.
    - `DataLoader.get_news` returns news from previous trading days and **same-day news only up to 15:00**, truncated by `PUBLISH_TIME` and ranked by `RANKING` (top-N hot items).
- **Data splits and evaluation.**
    - Public training: 2024-01-01–2024-12-31 (agent development).
    - Public A-list test: 2025-01-01–2025-12-31 (teams evaluate locally; no public online leaderboard; results shared informally in WeChat group).
    - Private B-list test: 2026-01-01–2026-06-01, held back; organizers run submitted agents and produce final ranking.
    - Initial capital: 100,000 CNY; daily-frequency trades; execution at **close price** with 0.01% transaction friction.
    - Backtest engine updates portfolio values using daily `pct_change`, then executes end-of-day trades at close, charging 0.01% commission on trade value.
    - Evaluation metrics: primary Sharpe ratio, plus cumulative return and max drawdown, with separate evaluation categories for different turnover levels.
- **Submission and reproducibility.**
    - B-list is run centrally; teams must submit **executable agent code + environment** (e.g., Docker), along with A-list logs and predictions.
    - Any training/fine-tuning/knowledge construction must use data and external resources available **before 2026** and must be submitted with full data, scripts, and model weights or reproducible pipelines.
    - No future-data leakage: agents must not use any information only available after the decision timestamp; organizers strongly recommend reusing the provided `DataLoader` to avoid subtle errors.

**Inferred implications**

- **State is daily, not intraday.** You cannot exploit intraday paths; only daily OHLC and hot-news snapshots, so designs should focus on daily regimes, event narratives, and medium-horizon rotation, not high-frequency microstructure.
- **Top-20 hot news implies event crowding.** The news feed is about market attention, not exhaustive firm news; architectures should explicitly model attention, narrative saturation, and “buzz-to-portfolio” mapping (CN‑Buzz2Portfolio is effectively this task’s research companion).[^1][^2][^3]
- **Two structurally different pools.** Track 1 is macro/beta and defensive assets; Track 2 is sector/thematic, more pro-cyclical and policy-sensitive. Allocators the same in code, but state and risk logic should be track-specific.
- **Transaction cost is small but not negligible.** 0.01% favors reasonably active daily agents, yet uncontrolled churn can still degrade Sharpe and push the submission into high-turnover buckets.

**Still-uncertain or underspecified points**

- Precise **turnover thresholds** for evaluation categories (low/medium/high) are not specified in the repo; must be inferred by exploratory backtests on baselines.
- Treatment of **corporate actions** (splits, ETF changes) is mostly abstracted by the `price_normalizer`, but details of adjusted factors and survivorship are not deeply documented.
- The organizers mention LLM-based agents in docs but do not constrain LLM model families beyond the “pre‑2026 resources” rule; whether very large proprietary models are logistically acceptable for B-list Docker is a practical concern, not a formal one.

B. Research Source Ledger
-------------------------

| Source | Type | What it contributes | Reliability | How it affects design |
| :-- | :-- | :-- | :-- | :-- |
| NLPCC2026 Task 4 root README | Official task README | Tracks, data splits (2024/2025/2026), evaluation metrics, submission rules, pre‑2026 resource constraint, A/B list protocol | High | Hard constraints on data usage, evaluation regime, and reproducibility; motivates robust, non-overfitted architectures. |
| NLPCC_tasks/README.md | Starter-kit README | ETF pools per track, backtest rules, API endpoints, recommended reading order, leakage constraints, turnover-aware eval | High | Defines two-track asset universes and the official anti-leakage interface; informs state representation and backtest compatibility. |
| dataset/README.md | Dataset description | Price and news directory structure, adjusted-price conventions, news ranking and THEDATE/PUBLISH_TIME logic, anti-leakage rationale | High | Anchors allowed features (no same-day close/high/low/returns; news only up to 15:00) and motivates using official DataLoader as the input abstraction. |
| server_platform/app/core/data_loader.py | Core DataLoader | Concrete implementation of `get_historical_prices` and `get_news`; exact masking of current-day prices and 15:00 cutoff | High | Determines exactly what the agent can see each day; drives state definition and prevents backtest vs. evaluation mismatch. |
| server_platform/app/core/backtest.py | Backtesting engine | Portfolio value update (pct_change-based), capital/holdings representation, buy-by-amount/sell-by-% logic, result saving | High | Defines the mapping from target allocations or trade lists to realized paths, including friction; shapes turnover and risk-control design. |
| dataset/dataloader_eval.py | Local eval DataLoader | Mirror of server DataLoader for local experiments, fallback trading dates, news handling for CSV evaluation | High | Ensures that local backtests faithfully mirror server behavior; supports offline experiments and ablations. |
| CN-Buzz2Portfolio | LLM-based Chinese macro/sector allocation benchmark from trending news | Dataset and CPA (Compression–Perception–Allocation) workflow for mapping daily trending Chinese financial news to macro/sector ETF allocations; 2024–mid-2025 rolling horizon | High (peer-reviewed/archival)[^1][^2][^3] | Very close to this task’s setting; inspires tri-stage architectures, attention over trending events, and allocation from compressed textual states. |
| Unveiling the Potential of Sentiment: Can LLMs Predict Chinese Stock Price Movements? | LLM-based sentiment factor extraction | Studies Chinese news summarization and sentiment factors via several LLMs and backtested strategies in Chinese equities.[^4] | Medium–High | Shows LLMs are useful for **factor extraction** rather than direct allocators; motivates LLM-as-feature-generator design. |
| CFGPT / SNFinLLM / ICE-PIXIU | Chinese financial LLMs | Domain-adapted Chinese financial LLMs; instruction tuning, retrieval-augmented Q\&A, and numerical reasoning over Chinese finance text.[^5][^6][^7][^8] | High (arXiv/ACL venues) | Suggests using moderately sized, Chinese-financial LLMs for event extraction, sentiment, and classification, not as direct allocators. |
| LLM-based multi-agent systems (e.g. TradingAgents, AlphaAgents, REITs multi-agent system) | LLM trading agent architectures | Multi-agent LLM frameworks with specialized agents (event, momentum, macro, risk) and aggregation.[^9][^10][^11][^12] | Medium–High | Motivates modular decomposition of analysis–prediction–decision; we repurpose architecture ideas but keep final allocation quant-driven. |
| Robustifying Conditional Portfolio Decisions via Optimal Transport | DRO with side-information | Distributionally robust portfolio with side-information using optimal-transport ambiguity sets; conditional DRO formulation.[^13] | High | Backbone for robust text-conditioned allocations (news as side information), informing DRO-BL design. |
| Distributionally Robust Mean-Variance with Wasserstein | DRO Markowitz | Wasserstein-robust mean-variance portfolio selection beating Black–Litterman and FF factors empirically.[^14][^15] | High | Supports robust risk-theory-based allocator with regularized covariance and ambiguity radius tuned on 2024. |
| Black–Litterman literature \& expositions | Bayesian portfolio model | Bayesian blending of equilibrium (market-cap) weights with views; extensions with VaR/CVaR and mixture distributions.[^16][^17][^18] | High | Basis for BL-style “views from news”, extended with robust ambiguity sets (DRO-BL agent). |
| Online portfolio selection / universal portfolios | Online convex optimization | Universal portfolios, log-regret online convex optimization, dynamic regret bounds for portfolios.[^19][^20][^21][^22] | High | Supports online mirror descent / bandit-style allocator (OMD‑Band agent) with turnover-aware regularization. |
| Temporal Fusion Transformer (TFT) | Temporal transformer with interpretable attention | Temporal transformer mixture of recurrent layers and attention for multi-horizon forecasting; interpretable attention over inputs.[^23][^24][^25] | High | Basis for transformer-inspired event-memory allocator (TEMA/RAMA‑T) without depending on giant closed LLM APIs. |
| HMM, Kalman, Bayesian filters in finance | Regime switching \& latent state | Hidden Markov models for market regimes, Kalman/particle filters for latent drivers and time-varying betas.[^26][^27][^28][^29] | Medium–High | Backbone for regime-switching allocator (Regime‑HMM‑RP) and belief-state update logic. |
| GNN-ETF / graph resource allocation | Graph neural networks | GNN-ETF models inter-sector ETF relations and co-movement; other GNN resource-allocation and spatio-temporal GNN work.[^30][^31][^32][^33] | Medium–High | Supports using sector/ETF relation graphs plus graph attention for sector rotation and macro spillover modelling. |
| Causal \& counterfactual finance | Causal inference in asset pricing and multimodal causal models | Guides causal driver selection, counterfactual reasoning, and invariant risk minimization for financial returns.[^34][^35][^36] | Medium–High | Underpins causal-impact agent (CIGA), using news-derived drivers and causal graphs for robust tilt decisions under regime shifts. |
| RAG in finance | Retrieval-augmented generation/time-series forecasting | RAG frameworks for financial analysis and time-series forecasting, reducing hallucinations and grounding in retrieved context.[^37][^38][^39] | Medium–High | Inspires retrieval/analogue-market agent (RAMA‑T) where retrieval is over historical market states rather than web text. |
| Sector rotation / event-based trading literature | Sector-rotation, event-driven methods | Two-stage sector rotation with ML and RNNs; event-driven trading strategies; sector-momentum tools.[^40][^41][^42][^43][^44] | Medium–High | Calibrates expectations for trend-following and news/event-based sector allocators vs. baselines. |

C. Candidate Design Universe
----------------------------

Below are at least 12 candidate designs, before consolidation.

For brevity, I’ll only flag keep/merge/reject/defer and why.

1. **BSA-RP: Belief-State Agent with Risk-Parity Control**
    - Core idea: Maintain a **low-dimensional belief state** over macro/sector states driven by decayed news and returns, then allocate via risk-parity-weighted tilts.
    - Engine: Bayesian filtering + exponential decay + risk parity.
    - LLM role: Event classification (macro themes, policy, risk-off/on tags).
    - Track fit: T1 9/10, T2 7/10.
    - Decision: **Keep** (strong belief-state/memory family candidate).
2. **KG-MoE: Knowledge-Graph Mixture-of-Experts Allocator**
    - Core idea: Build an ETF/sector graph (edges from co-movement, industry, supply-chain, policy linkage) and run a GNN whose output routes to specialized allocator experts (trend, value, defensive, policy-sensitive).[^30][^31]
    - Engine: Heterogeneous GNN + MoE gating + constrained optimizer.
    - LLM role: Entity/sector mapping, relation labeling from news.
    - Track fit: T1 7/10, T2 9/10.
    - Decision: **Keep** (graph/knowledge-based design).
3. **DRO-BL: Distributionally Robust Black–Litterman Agent**
    - Core idea: Use text-conditioned views (from news) but plug them into a **Wasserstein-DRO Black–Litterman** allocator, controlling ambiguity radius via 2024 validation.[^13][^16][^14][^18]
    - Engine: Robust BL + CVaR or STARR constraints.
    - LLM role: Map news to structured view vectors (expected sector/macrotile outperformance and uncertainty).
    - Track fit: T1 9/10, T2 8/10.
    - Decision: **Keep** (robust risk-theory core).
4. **TEMA / RAMA‑T: Transformer Event Memory Allocator**
    - Core idea: A temporal transformer with attention over a **memory of recent days’ news embeddings and price signals**, implementing something like a compressed CN‑Buzz2Portfolio CPA pipeline but using a mid-sized transformer.[^2][^3][^24][^1]
    - Engine: Temporal transformer with decaying positional embeddings and cross-attention from ETFs to events.
    - LLM role: Optional pre-trained text encoder; no giant chat LLM in the loop.
    - Track fit: T1 8/10, T2 8/10.
    - Decision: **Keep**, renamed below as RAMA‑T.
5. **LEEQA: LLM-Extracted Event Q-Allocator (Learning-to-Rank)**
    - Core idea: Use an LLM fine-tuned on Chinese financial tasks to convert daily top-20 news into structured **factor signals per ETF** (policy tailwind, earnings risk, regulatory shock, sentiment), then train a gradient-boosted or neural **learning-to-rank** model for ETF/sector ordering.[^5][^6][^8][^4][^45]
    - Engine: Learning-to-rank / listwise scoring + risk/turnover constraints.
    - LLM role: Only event extraction and factor scoring.
    - Track fit: T1 7/10, T2 9/10.
    - Decision: **Keep** (LLM-structured event extraction + ranker).
6. **Regime-HMM-RP: Hidden-Regime Risk-Parity Allocator**
    - Core idea: A hidden Markov model (or semi-HMM) over macro regimes (risk-on/off, reflation, policy tightening, etc.) inferred from returns and news factors; each regime has its own risk-parity or trend-following allocation template.[^26][^27][^28][^29]
    - Engine: HMM or switching Kalman filter + regime-specific optimizer.
    - LLM role: Regime labeling assistance (for interpretable tags), optional.
    - Track fit: T1 9/10, T2 7/10.
    - Decision: **Keep** (regime-switching design).
7. **RAMA: Retrieval Analogue Market Allocator**
    - Core idea: For the current day’s feature vector (news + recent returns), retrieve k similar historical days (2024/2025), look at their realized forward returns for each ETF/sector, and allocate via a **kernel-weighted analogue strategy**; implement retrieval as a differentiable kNN or attention over a memory bank.[^37][^38][^1]
    - Engine: Analogue retrieval + kernel regression + constrained optimizer.
    - LLM role: Embed news into dense vectors; retrieval may be done entirely in vector space.
    - Track fit: T1 7/10, T2 8/10.
    - Decision: **Merge with transformer-inspired RAMA‑T design** (retrieval + transformer).
8. **OMD-Band: Online Mirror Descent Bandit Allocator**
    - Core idea: Treat each ETF as an arm; use online mirror descent / FTRL with transaction-cost-aware switching regularization and possibly bandit feedback to adapt weights daily with regret guarantees.[^46][^47][^19][^20][^21][^22]
    - Engine: Online convex optimization with switching costs.
    - LLM role: None or only for explanations.
    - Track fit: Both 7–8/10.
    - Decision: **Keep** (online-learning/bandit family).
9. **CIGA: Causal Impact Graph Agent**
    - Core idea: Build a causal graph of macro/sector/news drivers; use invariant risk minimization and counterfactual reasoning to choose allocations that are stable across 2024 sub-regimes.[^34][^36][^35]
    - Engine: Causal graph learning + driver-based portfolio optimization.
    - LLM role: Propose candidate causal edges and annotate events but not decide trades.
    - Track fit: T1 8/10, T2 7/10.
    - Decision: **Keep** (causal/counterfactual family).
10. **GNN-ETF-RP: Graph Neural ETF Risk Parity**
    - Core idea: Use a GNN over ETF nodes to estimate a de-noised covariance/graph Laplacian, then perform graph-aware risk parity (penalizing jumps across weakly connected sectors).[^32][^30]
    - Engine: GNN covariance estimator + risk-parity solver.
    - LLM role: None.
    - Track fit: T1 7/10, T2 8/10.
    - Decision: **Merge** with KG-MoE (as its base graph engine).
11. **BL-LM: Plain Black–Litterman with LLM Views**
    - Core idea: Directly map LLM textual opinions to BL views and solve classical BL once per day.
    - Engine: Standard BL; LLM used as view oracle.
    - LLM role: Very strong; borderline “LLM says tilt up/down”.
    - Track fit: Good; Novelty: limited.
    - Decision: **Reject as main design** (too close to naive LLM-allocator); use only as a **baseline**.
12. **LLM-Direct-Agent: “ChatGPT Says Weights”**
    - Core idea: Prompt a large LLM with news and prices, ask for weights.
    - Engine: LLM as allocator.
    - LLM role: Uncontrolled; no explicit optimizer.
    - Decision: **Reject** except as a **negative control baseline**, not worth full implementation.

**Final set** (for Sections D–K):
We consolidate to **8 distinct designs**:

1. BSA‑RP (belief-state memory, risk parity).
2. KG‑MoE (graph/MoE sector/macro allocator).
3. DRO‑BL (robust BL-style agent).
4. LEEQA (LLM event extraction + learning-to-rank allocator).
5. Regime‑HMM‑RP (regime-switching).
6. RAMA‑T (retrieval + transformer-inspired event memory allocator).
7. OMD‑Band (online convex optimization/bandit allocator).
8. CIGA (causal-impact graph agent).

D. Five to Eight Final Design Blueprints
----------------------------------------

I’ll outline each blueprint at a high level here; Section E will give more math.

### D1. BSA‑RP: Belief-State Agent with Risk-Parity Control

1. **Thesis.** Maintain a low-dimensional belief state over macro risk-on/off, growth vs. value, policy-tightening, and liquidity regimes driven by decayed news and returns, then allocate via risk-parity-weighted tilts around a conservative baseline.
2. **Novelty vs. trivial baselines.**
    - Not “LLM says weights”: LLM only converts news into structured thematic scores; the belief state is updated via **Bayesian filtering + exponential decay** and allocation is classical risk parity plus constrained tilts.
    - More subtle than momentum: the belief state is multi-factor and uses both news and cross-asset behavior to infer latent macro state.
    - More structured than sentiment-only: it combines multiple thematic channels (policy, credit, growth, geopolitical) and uses them jointly to update beliefs.
3. **State representation.**
    - Let $z_t \in \mathbb{R}^K$ be a latent belief vector over K macro states (e.g., growth, inflation, policy, risk).^
    - Let $e_t \in \mathbb{R}^M$ be LLM-extracted event features (e.g., policy easing, default risk in property, AI bubble intensity).[^8][^4]
    - Let $r^{(hist)}_{t}$ be recent (past $L$) ETF/index returns from `get_historical_prices` (no current-day leakage).
    - State: $s_t = (z_t, e_t, \phi(r^{(hist)}_{t}))$, where $\phi$ are hand-crafted or learned summary statistics (volatility, cross-correlations, drawdown).
4. **Update rule (sketch).**
    - Prior evolution: $z_t^{prior} = A z_{t-1} + \epsilon_t$, with $A$ diagonal or block-diagonal; $\epsilon_t \sim \mathcal{N}(0, Q)$.
    - Likelihood from events and returns:

$$
p(o_t \mid z_t) \propto \exp\left(-\frac12 \| e_t - W_e z_t\|^2_{\Sigma_e^{-1}} - \frac12 \|\psi(r^{(hist)}_t) - W_r z_t\|^2_{\Sigma_r^{-1}}\right),
$$

where $o_t$ are observations, and $W_e,W_r$ are learned from 2024.[^27][^13]
    - Posterior update approximated by an **extended Kalman or ensemble Kalman filter**, or simply a gated exponential update:

$$
z_t = (1-\alpha) z_{t-1} + \alpha f_\theta(e_t,\psi(r^{(hist)}_t)),
$$

with $\alpha$ decaying with event staleness.
5. **LLM role.**
    - A Chinese financial LLM (e.g. CFGPT, SNFinLLM, ICE-PIXIU) is used offline or in pre-processing to map raw news to structured features $e_t$: sentiment by sector, policy stance, macro theme tags, and uncertainty scores.[^6][^7][^4][^5][^8]
    - Not used at allocation time on B-list; pre-computed feature pipeline runs inside Docker.
6. **Non-LLM engine.**
    - Risk parity core: compute risk budgets for each ETF and solve for weights $w^0_t$ such that contribution to portfolio volatility from each asset matches a target vector (e.g. equal or defensive-overweighted).[^14]
    - Overlay tilts based on belief vector $z_t$ via a small constrained optimizer.
7. **Portfolio construction (high-level).**
    - Compute baseline risk-parity weights $w^0_t$ from estimated covariance $\Sigma_t$ built only from past returns (e.g. shrinkage estimator).
    - Compute thematic scores $g_t \in \mathbb{R}^N$ over N ETFs by mapping $z_t$ through a fixed linear map (e.g. positive growth state supports equity indices, negative risk state boosts bonds/gold).
    - Convert scores to additive tilts: $\Delta w_t = \lambda \cdot \text{proj}_{\mathcal{C}}(g_t)$ with box constraints $|\Delta w_{t,i}| \le c_{max}$ and $\sum_i \Delta w_{t,i}=0$.
    - Final pre-trade target: $w^{target}_t = w^0_t + \Delta w_t$.
    - Turnover minimization: solve

$$
\min_{w \in \mathcal{C}} \; \|w-w^{target}_t\|^2 + \eta \|w - w_{t-1}\|_1
$$

to respect transaction costs and turnover bucket constraints.[^47]
    - Translate $w_t$ to backtest trades: compute desired monetary holding per ETF and execute buys/sells via `submit_trades` (buy by amount, sell by %).
8. **Data use and leakage safety.**
    - Uses only `get_historical_prices` (which hides same-day close/high/low) and `get_news` (news only up to 15:00, top-ranked items).
    - Trained on 2024 only; 2025 used strictly for walk-forward validation and hyperparameter tuning, then frozen before B-list.
    - No external data beyond pre-2026 models and static macro priors.
    - LLM features computed from raw news text that is part of official dataset; no online news calls.
9. **Track fit.**
    - Track 1: **9/10** — direct macro-belief mapping to bond/equity/gold tilts.
    - Track 2: **7/10** — can be extended to sector tilts via sector-level belief but may be less precise than a pure sector-rotation design.
10. **Implementation plan (student-days ballpark).**
    - MVP (8–10 days):
        - Implement classical risk parity and a simple exponentially decayed news sentiment index per ETF (without full latent filter).
    - Strong (15–20 days):
        - Add belief-state filter $z_t$, event-factor mapping via small MLP, and regularized tilt optimizer.
    - Report-ready (20–25 days):
        - Thorough ablations, 2024 sub-window robustness, interpretable plots of belief trajectories and regime annotations.
11. **Failure modes.**
    - Overfitting 2025 via re-tuning $A, W_e, W_r$ too aggressively.
    - Latent state collapsing to one regime (under-regularized).
    - Excessive tilts causing concentration or churn if $\lambda$ and $\eta$ are mis-calibrated.
    - LLM mislabeling major events (e.g. treating tightening as easing).
12. **Ablation plan.**
    - Remove LLM: replace event features with simple bag-of-words TF-IDF or dictionary-based theme counts.
    - Remove news: belief state driven only by returns $\phi(r^{(hist)})$.
    - Remove belief state: use risk parity only (+ simple momentum overlays) — essentially S1 quant baseline.
    - Remove risk control: direct mapping from $z_t$ to weights to demonstrate blow-ups.
    - 2024-tuned vs. 2025-tuned parameters.
13. **Narrative value.**
    - Strong story about **belief-state modeling** and separation of “reasoning” (LLM event parsing) from “decision” (Bayesian+quant).
    - Clear visualizations of macro beliefs and corresponding tilts; good for system report even if Sharpe is only moderately above baseline.

***

### D2. KG‑MoE: Knowledge-Graph Mixture-of-Experts Allocator

1. **Thesis.** Use a sector/ETF **graph** capturing co-movement, industry, and policy linkages, and route each day’s state through a GNN plus Mixture-of-Experts allocator to choose between trend-following, mean-reversion, defensive, and policy-sensitive experts, especially effective for sector rotation.[^30][^32]
2. **Novelty.**
    - Beyond momentum: it models **inter-sector spillovers and contagion** via a graph, not independent assets.
    - Beyond sentiment-only: news affects node features and edge weights, influencing which expert is selected and where tilts propagate.
    - Beyond standard RAG: graph structure acts as a **learned inductive bias** that can generalize under new sector correlations.
3. **State representation.**
    - Graph $G_t = (V,E_t)$ where each node is an ETF, node features include recent returns, realized vol, LLM-derived sector sentiment, policy-exposure indicators, etc.[^4][^30]
    - Edge weights $w_{ij,t}$ capture rolling correlations, co-mention in news, and fundamental linkages (e.g. energy → chemicals, semiconductors → AI).[^41][^30]
    - GNN node embeddings $h_{i,t}$ form the state over which experts operate.
4. **Update rule.**
    - Update edge weights using exponential moving averages of returns correlations and news co-occurrence daily (on 2024–2025 data).
    - Run a few layers of graph convolution or graph attention:

$$
h_{i,t}^{(l+1)} = \sigma\!\left(\sum_{j} \alpha_{ij,t}^{(l)} W^{(l)} h_{j,t}^{(l)}\right)
$$

where $\alpha_{ij,t}$ are attention coefficients based on edge weights.[^31][^30]
5. **LLM role.**
    - Event/entity extraction linking news to sectors and ETFs (e.g., policy in renewables → edges from policy node to `000941.SH` and relevant sector ETFs).
    - Optionally classifying events as supply shocks vs. demand shocks to modulate edge directions.
6. **Non-LLM engine.**
    - MoE allocator: for each node embedding $h_{i,t}$, a gating network selects mixture weights over experts $E_k$ (trend, value, defensive, carry).
    - Each expert outputs a preliminary score $s_{i,t}^{(k)}$; final score $s_{i,t} = \sum_k \pi_{k}(h_{i,t}) s_{i,t}^{(k)}$.
    - Portfolio optimizer converts scores to weights with sector caps and risk parity overlay.
7. **Portfolio construction.**
    - Score-to-weight: use softmax with temperature and risk scaling:

$$
\tilde{w}_i \propto \exp(\beta s_{i,t}) / \hat{\sigma}_{i,t}
$$

where $\hat{\sigma}_{i,t}$ is recent vol (reducing weight on volatile sectors).[^40]
    - Apply **graph Laplacian regularization** to stabilize allocations: penalize large differences between connected sectors:

$$
\min_{w} \; -\tilde{w}^\top \mu_t + \gamma w^\top L_t w + \eta \|w-w_{t-1}\|_1
$$

subject to box and leverage constraints, where $L_t$ is graph Laplacian.[^30]
    - Convert final weights to trades as in D1.
8. **Data \& leakage.** Same pattern: only past returns and pre‑15:00 news via official DataLoader; 2024 train, 2025 validation.
9. **Track fit.**
    - Track 1: 7/10 — graph still helpful (equity vs. bonds vs. gold correlation) but simpler.
    - Track 2: 9/10 — excellent for sector-rotation and inter-sector spillover modeling.
10. **Implementation (days).**
    - MVP (10–12): static correlation-based graph + simple GCN + single expert (trend).
    - Strong (18–22): dynamic graph, multi-expert MoE, Laplacian-regularized optimizer.
    - Report (22–28): interpretability (visualize sector graph, expert routing), robustness checks.
11. **Failure modes.**
    - Overfitting to 2024 graph structure; 2026 correlations may shift.
    - GNN training instability with small sample size (daily data).
    - LLM mis-tagging news to wrong sectors, corrupting edges.
12. **Ablations.**
    - No LLM: edges only from return correlations.
    - No graph: per-ETF MLP (independent).
    - Single expert (no MoE).
    - No Laplacian regularization (risk of concentration).
    - 2024-only vs. 2024+2025 training.
13. **Narrative.**
    - Attractive “**GNN-ETF**” narrative showing cross-sector contagion and MoE routing; pairs well with sector rotation track; offers strong images/tables for the shared-task paper.[^32][^30]

***

### D3. DRO‑BL: Distributionally Robust Black–Litterman Agent

1. **Thesis.** Combine text-conditioned views from news with a **Wasserstein distributionally robust Black–Litterman** allocator, producing stable, risk-aware portfolios that respect uncertainty in news interpretation.[^16][^15][^18][^13][^14]
2. **Novelty.**
    - Moves beyond naive BL with LLM views by **explicitly modeling ambiguity** around news-derived views via DRO; measures sensitivity of allocations to mis-specified beliefs.
    - Bridges LLM event extraction (views) with rigorous robust optimization.
3. **State representation.**
    - Prior equilibrium returns $\pi$ from market weights or long-run risk-premium estimates.
    - View matrix $P_t$ and view vector $q_t$ derived from daily news (e.g., “policy easing in AI” → expected relative outperformance of AI-sector ETF vs. market).
    - Ambiguity set radius $\delta_t$ capturing uncertainty/variance in views, conditioned on how noisy/conflicting the news is.
4. **Update rule.**
    - Standard BL posterior mean (without robustness):

$$
\mu^{BL}_t = \left((\tau \Sigma)^{-1} + P_t^\top \Omega_t^{-1} P_t\right)^{-1}
  \left((\tau \Sigma)^{-1}\pi + P_t^\top \Omega_t^{-1} q_t\right),
$$

where $\Omega_t$ encodes view uncertainty; $\tau$ is a scaling parameter.[^18][^16]
    - DRO adjustment: solve a worst-case mean-variance problem over a Wasserstein ball around the empirical distribution with radius $\delta$.[^15][^13][^14]
        - This adds a **regularization term** to variance or penalizes concentration toward assets with highly uncertain views.
    - $\delta$ and $\Omega_t$ tuned on 2024 via rolling-window CV.
5. **LLM role.**
    - Map daily news to discrete views $q_t$, including sign, magnitude, and **self-reported confidence** (mapped to $\Omega_t$).
    - E.g., “high-confidence policy easing” leads to small $\Omega_{ii}$, while ambiguous news yields large $\Omega_{ii}$.[^8][^4]
    - LLM is not used inside the optimizer.
6. **Engine.**
    - Robust mean-variance under BL posterior:

$$
\max_w \; \mu^{BL}_t{}^\top w - \lambda w^\top \Sigma^{rob}_t w \quad \text{s.t. } w \in \mathcal{C},
$$

where $\Sigma^{rob}_t$ includes a Wasserstein-robust variance inflation.[^13][^14]
    - Additional constraints: sector caps, minimum bond/gold allocation in Track 1, etc.
7. **Portfolio construction.**
    - Convert $w_t$ to target allocations; implement a **no-trade band** around previous weights to limit churn: if $|w_{t,i} - w_{t-1,i}| < \epsilon$, skip trading that asset.
    - Turnover budgeting: include explicit penalty $\eta \sum_i |w_{t,i}-w_{t-1,i}|$ in objective to account for 0.01% cost and evaluation buckets.[^47]
8. **Track fit.**
    - Track 1: 9/10 — text-conditioned macro views (equities vs. bonds vs. gold) are a natural use-case.
    - Track 2: 8/10 — sector-level BL works, though views may be more granular and noisy.
9. **Implementation (days).**
    - MVP (8–10): classical BL with heuristic views from simple sentiment scores.
    - Strong (15–18): add Wasserstein DRO, view-confidence mapping from LLM, and turnover-aware optimizer.
    - Report (18–24): diagnostics on ambiguity radius, view sensitivity, and robustness tests.
10. **Failure modes.**
    - Overconfident views (too small $\Omega$) leading to aggressive tilts.
    - Ambiguity radius mis-tuned → over-conservative portfolios with low Sharpe.
    - LLM hallucinated views that misinterpret idiosyncratic stories as macro.
11. **Ablations.**
    - No DRO (pure BL).
    - No LLM (views from rule-based sentiment and macro indicators).
    - No views (baseline Markowitz or risk parity) — shows incremental value of text-conditioned views.
    - Different ambiguity radii across 2024 subwindows.
12. **Narrative.**
    - Very strong **math story**: BL, Wasserstein DRO, ambiguity sets; aligns well with JPM / Quantitative Finance style work.[^16][^14][^13]
    - High chance of being highlighted as a “risk-aware, robust” system even if performance is modestly above baseline.

***

### D4. LEEQA: LLM Event Extraction + Learning-to-Rank Allocator

1. **Thesis.** Use a Chinese financial LLM to distill each day’s top-20 hot news into structured features per ETF, then train a **learning-to-rank model** to order ETFs/sectors by expected risk-adjusted return, converting ranks into bounded tilts around low-risk baselines.[^1][^2][^4][^8]
2. **Novelty.**
    - Separates **comprehension** (LLM) from **ranking** (supervised learning), using the task’s daily allocation structure to fit a listwise ranking model (e.g., LambdaMART, ListNet, or differentiable sorting networks).
    - Moves beyond naive sentiment by including rich labels (policy, structural theme, earnings, leverage, regulation).
3. **State representation.**
    - For each ETF $i$ at day $t$, feature vector $x_{i,t} = [r^{hist}_{i,t}, vol_{i,t}, sector\_id, macro\_regime\_proxy, e_{i,t}^{(LLM)}]$, where $e_{i,t}^{(LLM)}$ are LLM-derived features (e.g. positive/negative event counts, risk tags, time-to-decay).
    - Ranking label for training (2024): realized forward k-day return or Sharpe from day $t$ to $t+k$ (e.g. 5-day horizon), consistent with daily rebalancing.
4. **Update rule.**
    - Learning-to-rank model $f_\theta(x_{i,t})$ outputs scalar scores; trained to order ETFs by realized forward outcomes across 2024, possibly with **group-wise normalization per day**.
    - Optionally updated online with 2025 as additional training, but freeze before B-list.
5. **LLM role.**
    - Off-line or pre-processing: fine-tuned or prompted LLM extracts per-ETF textual features:
        - Sentiment score, policy tailwind/headwind, idiosyncratic risk flags, cross-asset impact hints.
    - All extraction done using official news dataset; no external web calls.
6. **Engine.**
    - Gradient-boosted trees (XGBoost / LightGBM ranker) or neural ranking model; optionally calibrate scores to predicted excess returns via isotonic regression.[^45]
    - Could incorporate pairwise or listwise losses to directly optimize ranking quality.
7. **Portfolio construction.**
    - Within each day, convert normalized scores $\hat{s}_{i,t}$ to tilt factors:

$$
\tilde{w}_{i,t} = w^{base}_{i,t} \left(1 + \kappa \cdot \frac{\hat{s}_{i,t} - \bar{s}_t}{\sigma_s}\right),
$$

where $w^{base}$ is inverse-vol or equal-weight baseline, $\bar{s}_t$ and $\sigma_s$ are cross-sectional mean/std.[^40]
    - Enforce positivity and re-normalize to sum to 1; apply sector caps and a turnover penalty $\eta \|w_t-w_{t-1}\|_1$.
    - For Track 2, optionally choose top-K sectors (e.g., K=4) to overweight as in two-stage sector rotation literature.[^41][^40]
8. **Track fit.**
    - Track 1: 7/10 — useful but more natural for sector-level tilts.
    - Track 2: 9/10 — fits sector-rotation narrative and aligns with CN‑Buzz2Portfolio’s emphasis on mapping trending news to sector ETFs.[^2][^1]
9. **Implementation (days).**
    - MVP (8–10): simple factor engineering from sentiment and momentum; use off-the-shelf ranker.
    - Strong (14–18): richer LLM-extracted features; multi-horizon labels; separate Track1/Track2 rankers.
    - Report (18–24): calibration plots, factor importance, ablation across textual vs. pure-quant features.
10. **Failure modes.**
    - Overfitting 2024 labels (especially for small N asset universe).
    - LLM feature drift/instability across 2024/2025.
    - High cross-sectional noise in short-horizon labels causing fragile rankings.
11. **Ablations.**
    - No LLM features: ranking purely on price/volume data and naive news counts.
    - No news: ranking based only on quant technicals (momentum, volatility).
    - Rank-only vs. direct regression of returns.
    - Baseline S1-style trend-following vs. LEEQA ranking overlay.
12. **Narrative.**
    - Strong story: **“news-to-ranking”** pipeline, ties directly to CN‑Buzz2Portfolio’s interest in mapping trending news to allocations.[^3][^1][^2]
    - Easy to explain contribution of each textual feature via feature importance; good candidate for system report inclusion.

***

### D5. Regime‑HMM‑RP: Regime-Switching Hidden-State Allocator

1. **Thesis.** Model daily market regimes with a Hidden Markov Model based on cross-asset returns and volatility; each regime has its own risk-parity/trend-following template, and allocation follows filtered regime probabilities.[^29][^26][^27]
2. **Novelty.**
    - Uses **latent discrete regimes** rather than continuous latent factors; supports interpretable “risk-on/off, policy shock” labels.
    - Connects to classic regime-switching asset allocation while integrating news through features or prior on transition probabilities.
3. **State representation.**
    - Hidden state $z_t \in \{1,\dots,K\}$ (e.g. K=3–4 regimes).
    - Observations $o_t$ include 1–5 day index returns, realized volatility, cross-sectional dispersion, and simple news sentiment indices.
    - Filtered probabilities $\gamma_{t,k} = P(z_t=k \mid o_{1:t})$ are the main state.
4. **Update rule.**
    - Standard HMM forward algorithm:

$$
\gamma_{t,k} \propto \left(\sum_j \gamma_{t-1,j} a_{jk}\right) \cdot p(o_t \mid z_t=k),
$$

where $a_{jk}$ is the transition matrix; emission distributions $p(o_t|z_t=k)$ are Gaussian over summarized features.
    - Optionally adjust transition probabilities based on news-coded structural events (e.g. big policy announcement increases probability of moving to a new regime).
5. **LLM role.**
    - Off-line classification of historical major events and their mapping to regime labels, to aid interpretation and potentially to build prior regime labels for supervised learning.
    - Not required in the online filter.
6. **Engine.**
    - For each regime $k$, define a template allocation $w^{(k)}$ based on risk parity, momentum, and defensive preferences (estimated from 2024 data).
    - Daily allocation is mixture: $w_t = \sum_k \gamma_{t,k} w^{(k)}$, then passed through risk and turnover controls.
7. **Portfolio construction.**
    - Use regime-specific vol estimates; scale exposures based on regime risk (e.g. lower total risk budget in high-vol regimes).
    - Add no-trade bands or threshold on regime change: only adjust weights significantly if max $\gamma_{t,k}$ changes by >$\theta$ from previous day.
    - Convert to trades as before.
8. **Track fit.**
    - Track 1: 9/10 — classic macro regime story.
    - Track 2: 7/10 — extend with sector-level HMM, but risk of overfitting due to limited cross-sectional data.
9. **Implementation (days).**
    - MVP (6–8): standard HMM on returns; fixed hand-crafted templates.
    - Strong (12–16): integrate news features into emissions/transition; tune K; regime-specific templates learned via optimization.
    - Report (16–20): regime transition diagrams, regime-labeled performance decomposition.
10. **Failure modes.**
    - Misspecified regime count (K) or transitions; unstable regimes.
    - Regime-switching overfitted to 2024 idiosyncrasies, failing on 2026.
    - Excessive trading around regime boundaries.
11. **Ablations.**
    - No news in HMM (returns only).
    - Single-regime baseline (no regime switching).
    - Hard regime assignments vs. posterior-weighted mixtures.
    - Template vs. direct regime-specific optimizer.
12. **Narrative.**
    - Clear, interpretable story: “**hidden regimes** mapped to macro narratives.”
    - Visuals of regime sequences vs. benchmark index, plus regime-conditioned performance, are compelling for reviewers.

***

### D6. RAMA‑T: Retrieval Analogue Market \& Transformer-Inspired Allocator

1. **Thesis.** For each day, retrieve analogous historical days (based on news and return features), then use a **transformer-style attention mechanism** over the retrieved set to estimate expected asset returns, without calling a large LLM as an oracle.[^24][^38][^3][^1]
2. **Novelty.**
    - Combines **retrieval-augmented** analogues (CN‑Buzz2Portfolio’s CPA philosophy) with an explicit attention-based aggregator, but the model is small and trainable end-to-end.[^38][^24][^1][^2]
    - Uses transformer internals (attention, positional decay) to model news half-life and cross-day event echoes.
3. **State representation.**
    - Current day embedding $u_t$ built from recent returns and news embeddings (news encoded via static text encoder or small LLM encoder offline).
    - Historical memory bank $\{(u_\tau, r^{fwd}_{\tau})\}$ from 2024 (and possibly 2025) where $r^{fwd}_\tau$ are forward returns.
    - Retrieval: nearest neighbors in embedding space or approximate ANN; feed top-K analogues into transformer block.
4. **Update rule.**
    - Compute similarities $k_\tau = u_t^\top u_\tau$; transform into attention scores:

$$
\alpha_\tau = \frac{\exp(k_\tau / \sqrt{d})}{\sum_{\tau'}\exp(k_{\tau'}/\sqrt{d})}.
$$
    - Estimate expected forward return per ETF via weighted combination of retrieved forward returns, possibly with a small feedforward network over concatenated features.
    - Include temporal decay (older analogues get lower weight).
5. **LLM role.**
    - Only as offline encoder from Chinese news to sentence/paragraph embeddings; can use domain-adapted models (CFGPT, SNFinLLM) or a smaller transformer pre-2026.[^5][^6][^8]
    - No interactive LLM in daily decision loop.
6. **Engine.**
    - Attention + MLP to map retrieved analogues to predicted cross-sectional vector of expected returns $\hat{\mu}_t$.
    - Then run a **simple robust optimizer** (e.g. mean-variance with shrinkage covariance + clipping of $\hat{\mu}$).
7. **Portfolio construction.**
    - Convert $\hat{\mu}_t$ to scores; apply volatility scaling and turnover penalty as in previous designs.
    - Could explicitly bound daily change in weights to keep analogues from overreacting.
8. **Track fit.**
    - Track 1: 8/10 — analogues for macro days.
    - Track 2: 8/10 — analogues for sector themes; synergy with CN‑Buzz2Portfolio.
9. **Implementation (days).**
    - MVP (10–12): kNN analogue retrieval + simple kernel regression; no transformer.
    - Strong (16–20): full attention-based aggregator; offline text encoder; integrated optimization.
    - Report (20–26): case studies of retrieved analogues for big macro days.
10. **Failure modes.**
    - Embedding drift leading to poor analogues.
    - Overfitting: analogues may inadvertently memorize 2025.
    - Data sparsity: some rare event types in 2026 have no close analogues.
11. **Ablations.**
    - No retrieval: direct supervised model.
    - Uniform averaging over KNN vs. attention.
    - No news (returns-based analogues only).
    - 2024-only vs. 2024+2025 memory bank.
12. **Narrative.**
    - Highly aligned with CN‑Buzz2Portfolio and LLM RAG research; transformer-inspired but clearly **not just a chat-LLM**.
    - Good cross-disciplinary story (NLP + quant + time-series).

***

### D7. OMD‑Band: Online Mirror Descent Bandit Allocator

1. **Thesis.** Treat daily allocation as an online convex optimization / bandit problem with switching costs, using online mirror descent (OMD) with log-barrier or entropic regularization to adapt weights while controlling turnover.[^19][^21][^22][^48][^46][^47]
2. **Novelty.**
    - Introduces **regret-bound online methods** into LLM-based agent competition; orthogonal to LLM features.
    - Explicitly optimizes log-wealth or other objectives with transaction-cost-aware regret bounds.
3. **State representation.**
    - Weight vector $w_t$ on the simplex; observed return vector $x_t$ (ETF gross returns from t‑1 to t, accessible from historical close data).
    - Optional side-info features $z_t$ (news or technicals) can feed into an optimistic OMD term.
4. **Update rule (conceptual).**
    - Loss at time t: $\ell_t(w) = -\log(w^\top x_t) + \lambda \|w-w_{t-1}\|_1$ to include switching cost.[^19][^21][^46]
    - OMD update:

$$
w_{t+1} = \arg\min_{w \in \Delta} \left\{\eta \nabla \ell_t(w_t)^\top w + D_\psi(w, w_t)\right\},
$$

where $D_\psi$ is Bregman divergence for entropic or log-barrier regularizer.[^22][^19]
    - For bandit feedback variant, use gradient estimator based on observed portfolio return.
5. **LLM role.**
    - Optional: adapt learning rate or incorporate an “optimistic” gradient based on LLM-derived short-term forecasts, but base framework is quant-only.
    - Also used for explanations; not central.
6. **Engine.**
    - OMD/FTRL algorithms with switching cost; optionally universal Dirichlet factor portfolio variant that mixes across factor portfolios.[^49][^20][^21][^22]
    - Implementation in Python with strict adherence to no-future-data.
7. **Portfolio construction.**
    - $w_t$ itself is the target weight; apply additional risk caps (e.g. max 30% single-ETF, min cash/low-risk in Track 1).
    - Convert differences in weights to trades each day, keeping an eye on friction and evaluation turnover buckets.
8. **Track fit.**
    - Track 1 and 2: ~7–8/10 — general method; not news-specific but robust.
9. **Implementation (days).**
    - MVP (6–8): basic universal portfolio / OMD with simple regularizer.
    - Strong (10–14): switching-cost OMD, dynamic learning rate, plus factor portfolios.
    - Report (14–18): regret-style metrics vs. best constant rebalanced portfolio on 2024–2025.
10. **Failure modes.**
    - If markets are highly non-stationary, regret bounds do not guarantee high Sharpe over finite horizon.
    - Excessive sensitivity to learning-rate hyperparameters.
    - Ignoring news could miss macro shocks.
11. **Ablations.**
    - No switching-cost term vs. with term.
    - Pure constant-rebalanced vs. OMD.
    - Factor-mix vs. single-level asset OMD.
12. **Narrative.**
    - Strong theoretical angle (regret bounds, OCO); excellent for reviewers who care about mathematical rigor even if the method doesn’t win Sharpe.[^21][^19][^22]

***

### D8. CIGA: Causal Impact Graph Agent

1. **Thesis.** Learn a small set of **causal drivers** (macro factors and sector-specific textual drivers) and their graph, then choose allocations that are stable across regimes via invariant risk minimization and counterfactual stress-tests.[^36][^35][^34]
2. **Novelty.**
    - Explicit causal-graph angle in a trading competition; uses text and returns to identify drivers whose effect is invariant across 2024 subperiods.
    - Contrasts with purely predictive models; aims for **robustness under 2026 distribution shift**.
3. **State representation.**
    - Driver vector $d_t$ (e.g. credit spread proxy from news, policy easing indicator, climate-policy signal, tech bubble score).
    - Causal adjacency matrix $B$ linking drivers to sector returns learned via causal discovery plus domain priors.[^35][^34][^36]
    - Portfolio states built as functions of driver exposures.
4. **Update rule.**
    - Offline: causal discovery / invariance tests across multiple 2024 environments (e.g., quarters or sub-regimes).
    - Online: update driver scores $d_t$ each day from news and price data; do not re-learn global graph on 2025/2026 (to avoid leakage and overfitting).
    - Optional simple Bayesian update of driver states (e.g. knowledge that “property easing” driver is active).
5. **LLM role.**
    - Extract candidate drivers from news (and their textual justifications) and map them to sectors.
    - Could help propose candidate graphs (edges) to be tested statistically.
6. **Engine.**
    - Driver-based portfolio optimization: choose weights $w$ with exposures $\beta(w)$ to causal drivers aligned with their expected risk premia, while being **invariant** to nuisance variables.
    - For example, estimate driver returns across environments and keep only those with consistent effects; penalize exposures to fragile drivers.
7. **Portfolio construction.**
    - Solve

$$
\max_w \; \theta^\top \beta(w) - \lambda w^\top \Sigma w
$$

with constraints that $\beta(w)$ lies largely in the “invariant” driver subspace.
    - Implement turnover caps similar to other designs.
8. **Track fit.**
    - Track 1: 8/10 — macro drivers like policy, growth, inflation.
    - Track 2: 7/10 — sector-level causal drivers, but more complex.
9. **Implementation (days).**
    - MVP (10–12): simple driver selection + environment-wise regressions.
    - Strong (16–20): causal graph discovery, invariant risk minimization, driver-based allocator.
    - Report (20–25): extensive driver interpretability and counterfactual analysis.
10. **Failure modes.**
    - Mis-specified environments leading to wrong invariance conclusions.
    - Over-pruning drivers and losing signal.
    - Complex pipeline may be fragile under B-list constraints.
11. **Ablations.**
    - Predictive-only model without causal constraints.
    - Use all drivers vs. invariant-only subset.
    - No LLM extraction (drivers from pre-defined quantitative indicators).
12. **Narrative.**
    - Very attractive for **award/creative selection**: explicit link to causal inference, robust finance, and textual drivers; even moderate performance is publishable.[^34][^36][^35]

E. Mathematical Formulation of Each Design
------------------------------------------

Below I formalize the core objects and rules for the 8 designs (concise but explicit).

### Common notation

- $N$: number of assets (ETFs/indices).
- $w_t \in \mathbb{R}^N$: portfolio weights at day $t$, $\sum_i w_{t,i}=1, w_{t,i}\ge0$.
- $x_t \in \mathbb{R}^N$: gross return vector from day $t$ to $t+1$ (observable ex post).
- $\Sigma_t$: covariance estimate based on past returns (e.g., rolling window).
- $\mathcal{C}$: constraint set (box constraints, sector caps, min bond/gold, etc.).
- Turnover: $\text{TO}_t = \sum_i |w_{t,i}-w_{t-1,i}|$.
- Objective: maximize (approx.) daily expected utility or Sharpe with turnover penalty.

For brevity, I show core elements; practical implementations will solve numerically.

***

### E1. BSA‑RP

**State:**

- Belief vector $z_t \in \mathbb{R}^K$.
- Event features $e_t \in \mathbb{R}^M$.
- Price summary $\phi(r^{(hist)}_t) \in \mathbb{R}^P$.

State variable:

$$
s_t = (z_t, e_t, \phi(r^{(hist)}_t)).
$$

**Update:**

Simple gated update (approx. Bayesian):

$$
z_t = (1-\alpha) z_{t-1} + \alpha f_\theta(e_t, \phi(r^{(hist)}_t)).
$$

$f_\theta$ can be a small MLP fitted on 2024 to predict next-day macro proxies (e.g., market index returns) and then calibrated as latent state.

**Score-to-weight:**

1. Risk parity baseline via solving:

$$
\min_{w \in \mathcal{C}} \; w^\top \Sigma_t w \quad \text{s.t. } (w \circ \Sigma_t w) \approx b,
$$

where $b$ is desired risk budget per asset or group (solved via standard RP algorithms).[^14]

2. Tilt from beliefs:

$$
g_t = H z_t \in \mathbb{R}^N,
$$

$$
\Delta w_t = \lambda \cdot \text{proj}_{\mathcal{C}_\Delta}(g_t), \quad \sum_i \Delta w_{t,i} = 0.
$$

3. Pre-trade target:

$$
w^{target}_t = w^0_t + \Delta w_t.
$$

4. Final weights via turnover-aware projection:

$$
w_t = \arg\min_{w \in \mathcal{C}} \|w-w^{target}_t\|^2 + \eta \|w-w_{t-1}\|_1.
$$

**Risk control:**

- Implicit via risk parity and covariance $\Sigma_t$.
- Optional max drawdown control via dynamic volatility scaling $\sigma^{target}_t$.

**Turnover control:**

- $L_1$ penalty $\eta \|w-w_{t-1}\|_1$ and no-trade band thresholds.

***

### E2. KG‑MoE

**State:**

- Graph $G_t=(V,E_t)$ with adjacency matrix $A_t$, edge weights $w_{ij,t}$.
- Node features $x_{i,t}$: returns, vol, sector ID, LLM-based sentiment, etc.

GNN embeddings:

$$
H^{(0)}_t = X_t, \quad H^{(l+1)}_t = \sigma(\tilde{D}_t^{-1/2}\tilde{A}_t \tilde{D}_t^{-1/2} H^{(l)}_t W^{(l)}),
$$

where $\tilde{A}_t = A_t + I$, $\tilde{D}_t$ is degree matrix.[^30]

Final node embedding $h_{i,t} = H^{(L)}_{t,i}$.

**Update:**

- Edge weights updated from correlations and news:

$$
w_{ij,t} = \rho \cdot w_{ij,t-1} + (1-\rho)\cdot \big(\text{corr}_{L}(r_i,r_j) + \text{news\_cooccurrence}_{i,j,t}\big).
$$

**Score-to-weight:**

MoE:

$$
\pi_{k}(h_{i,t}) = \text{softmax}(V h_{i,t})_k,\quad s_{i,t}^{(k)} = f_k(h_{i,t}),
$$

$$
s_{i,t} = \sum_k \pi_{k}(h_{i,t}) s_{i,t}^{(k)}.
$$

Initial weights:

$$
\tilde{w}_i \propto \frac{\exp(\beta s_{i,t})}{\hat{\sigma}_{i,t}}.
$$

**Risk \& turnover control:**

Graph-regularized optimization:

$$
\min_{w \in \mathcal{C}} -\tilde{w}^\top \mu_t + \gamma w^\top L_t w + \eta \|w-w_{t-1}\|_1,
$$

where $L_t$ is Laplacian from $A_t$.[^30]

***

### E3. DRO‑BL

**State:**

- Prior $\pi$, covariance $\Sigma$, views $(P_t,q_t)$, view covariance $\Omega_t$, Wasserstein radius $\delta_t$.[^18][^13][^14]

**Update:**

BL posterior mean (as above):

$$
\mu^{BL}_t = \left((\tau \Sigma)^{-1} + P_t^\top \Omega_t^{-1} P_t\right)^{-1}
       \left((\tau \Sigma)^{-1}\pi + P_t^\top \Omega_t^{-1} q_t\right).
$$

DRO modifies the risk term; for Wasserstein ambiguity one obtains equivalent regularization:

$$
\max_w \; \mu^{BL}_t{}^\top w - \lambda w^\top \Sigma w - \eta \|w\|_2,
$$

where $\eta$ is function of $\delta_t$.[^15][^13][^14]

**Score-to-weight:**

Solve above optimization under $\mathcal{C}$ and turnover penalty $\kappa \|w-w_{t-1}\|_1$.

***

### E4. LEEQA

**State:**

Per asset:

$$
x_{i,t} = [\text{mom}_{i,t}, \text{vol}_{i,t}, \text{sector\_id}_i, \text{macro\_proxy}_t, e_{i,t}^{(LLM)}].
$$

**Update:**

Learning-to-rank model $f_\theta$ trained on $x_{i,t}\rightarrow y_{i,t}$ where $y_{i,t}$ is future k-day performance.
At inference, $s_{i,t}=f_\theta(x_{i,t})$.

**Score-to-weight:**

Normalize scores:

$$
\hat{s}_{i,t} = \frac{s_{i,t} - \bar{s}_t}{\sigma_s}.
$$

$$
\tilde{w}_{i,t} = w^{base}_{i,t} (1 + \kappa \hat{s}_{i,t}).
$$

Project $\tilde{w}_t$ to $\mathcal{C}$ and apply turnover penalty as before.

***

### E5. Regime‑HMM‑RP

**State:**

- Discrete regime $z_t \in \{1,\dots,K\}$.
- Posterior probabilities $\gamma_{t,k} = P(z_t=k | o_{1:t})$.

**Update:**

HMM forward recursion:

$$
\gamma_{t,k} \propto \left(\sum_j \gamma_{t-1,j} a_{jk}\right) \cdot \mathcal{N}(o_t; \mu_k, \Sigma_k).
$$

**Score-to-weight:**

Per regime template $w^{(k)}$ (estimated via regime-wise optimization on 2024).
Mixture:

$$
w_t^{raw} = \sum_k \gamma_{t,k} w^{(k)}.
$$

Then project to $\mathcal{C}$ with turnover penalty.

***

### E6. RAMA‑T

**State:**

- Current embedding $u_t = g(\text{news}_t, r^{hist}_t)$.
- Memory bank $\{(u_\tau, r^{fwd}_\tau)\}_{\tau \in \mathcal{M}}$.

**Update:**

Retrieve top-K analogues by similarity; use attention:

$$
\alpha_\tau = \frac{\exp(u_t^\top u_\tau / \sqrt{d})}{\sum_{\tau' \in \mathcal{N}_t}\exp(u_t^\top u_{\tau'}/\sqrt{d})}.
$$

Estimated forward return:

$$
\hat{\mu}_t = \sum_{\tau \in \mathcal{N}_t} \alpha_\tau r^{fwd}_\tau.
$$

**Score-to-weight:**

Use robust transformation:

$$
s_{i,t} = \text{clip}(\hat{\mu}_{i,t}, -c,c),
$$

then convert to weights via mean-variance or risk-parity overlay as in other designs.

***

### E7. OMD‑Band

**State:**

- Weights $w_t$, observed returns $x_t$.

**Update:**

Loss:

$$
\ell_t(w) = -\log(w^\top x_t) + \lambda \|w-w_{t-1}\|_1.
$$

Gradient approximations:

$$
\nabla \ell_t(w_t) \approx -\frac{x_t}{w_t^\top x_t} + \lambda \cdot \text{sgn}(w_t - w_{t-1}).
$$

OMD update with entropic regularizer:

$$
w_{t+1,i} \propto w_{t,i} \exp(-\eta \nabla_i \ell_t(w_t)).
$$

Normalize to simplex.

**Score-to-weight:** $w_t$ itself.

***

### E8. CIGA

**State:**

- Drivers $d_t \in \mathbb{R}^D$.
- Causal graph $B \in \mathbb{R}^{D \times D}$; driver exposures of assets $\beta_i$.

**Update:**

- Offline: learn $B$ via causal discovery; estimate invariant effects of drivers on sector returns across environments.
- Online: update driver scores $d_t$ from news (LLM mapping) and simple quantitative metrics.

**Score-to-weight:**

- Desired exposure $\theta$ to driver vector; choose w solving:

$$
\max_{w \in \mathcal{C}} \; \theta^\top \left(\sum_i w_i \beta_i\right) - \lambda w^\top \Sigma w
$$

subject to invariance penalty:

$$
\|P_\perp \sum_i w_i \beta_i\|^2 \le \epsilon,
$$

where $P_\perp$ projects onto non-invariant driver subspace.[^36]

Turnover handled as before.

F. Quantitative Comparison Table
--------------------------------

Subjective but conservative 0–10 scores (higher is better except last three risk metrics, where higher is worse per spec). These are expectations from design, not empirical results.

**Designs:**

- D1: BSA‑RP
- D2: KG‑MoE
- D3: DRO‑BL
- D4: LEEQA
- D5: Regime‑HMM‑RP
- D6: RAMA‑T
- D7: OMD‑Band
- D8: CIGA

(0–10, mid-scale ~5)


| Criterion | D1 BSA‑RP | D2 KG‑MoE | D3 DRO‑BL | D4 LEEQA | D5 Reg‑HMM‑RP | D6 RAMA‑T | D7 OMD‑Band | D8 CIGA |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| Track 1 Fit | 9 | 7 | 9 | 7 | 9 | 8 | 8 | 8 |
| Track 2 Fit | 7 | 9 | 8 | 9 | 7 | 8 | 7 | 7 |
| Sharpe Potential | 8 | 8 | 8 | 8 | 7 | 8 | 7 | 7 |
| Drawdown Control | 8 | 7 | 9 | 7 | 8 | 7 | 7 | 8 |
| Turnover Efficiency | 8 | 7 | 8 | 7 | 8 | 7 | 8 | 7 |
| B-list Robustness | 8 | 7 | 9 | 7 | 8 | 7 | 8 | 9 |
| Novelty | 7 | 9 | 8 | 8 | 7 | 8 | 7 | 9 |
| Mathematical Depth | 7 | 7 | 9 | 7 | 8 | 8 | 9 | 9 |
| Interpretability | 8 | 7 | 8 | 8 | 9 | 7 | 6 | 9 |
| Reproducibility | 8 | 7 | 8 | 8 | 8 | 7 | 8 | 7 |
| Implementation Feasibility | 8 | 7 | 7 | 8 | 7 | 7 | 8 | 6 |
| Baseline Beating Probability | 8 | 7 | 8 | 8 | 7 | 8 | 7 | 6 |
| Report / Paper Signal | 8 | 9 | 9 | 9 | 8 | 9 | 8 | 10 |
| Overfit Risk (higher=worse) | 6 | 7 | 5 | 7 | 6 | 7 | 5 | 7 |
| Tool Dependency Risk | 5 | 6 | 5 | 6 | 4 | 6 | 3 | 6 |
| Data Compliance Risk | 3 | 3 | 3 | 4 | 3 | 4 | 2 | 4 |

Now compute **Overall Research-Competition ROI** for each using:

$$
\text{ROI} =
0.12 \cdot \max(T1,T2)
+ 0.12 \cdot \text{Sharpe}
+ 0.08 \cdot \text{DD}
+ 0.07 \cdot \text{Turnover}
+ 0.12 \cdot \text{BList}
+ 0.11 \cdot \text{Novelty}
+ 0.10 \cdot \text{MathDepth}
+ 0.08 \cdot \text{Interp}
+ 0.07 \cdot \text{Reprod}
+ 0.08 \cdot \text{Feas}
+ 0.08 \cdot \text{BaselineProb}
+ 0.10 \cdot \text{ReportSig}
- 0.08 \cdot \text{OverfitRisk}
- 0.04 \cdot \text{ToolRisk}
- 0.03 \cdot \text{DataRisk}
$$

Approximate ROI (0–10):

- **D1 BSA‑RP**: ≈ 8.1
- **D2 KG‑MoE**: ≈ 8.0
- **D3 DRO‑BL**: ≈ 8.5
- **D4 LEEQA**: ≈ 8.1
- **D5 Reg‑HMM‑RP**: ≈ 8.0
- **D6 RAMA‑T**: ≈ 8.2
- **D7 OMD‑Band**: ≈ 7.8
- **D8 CIGA**: ≈ 8.2

(Ranked roughly: D3 ≳ D6 ≈ D8 ≈ D1 ≈ D4 ≈ D2 ≈ D5 > D7.)

G. Competition Score vs Research/Award Score
--------------------------------------------

Define two composite sub-scores (0–10), again approximate:

- **Competition Score** (Sharpe, drawdown, turnover, B-list robustness, baseline beating):
    - D1 BSA‑RP: ~8.3
    - D2 KG‑MoE: ~8.0
    - D3 DRO‑BL: ~8.7
    - D4 LEEQA: ~8.1
    - D5 Reg‑HMM‑RP: ~8.1
    - D6 RAMA‑T: ~8.3
    - D7 OMD‑Band: ~7.7
    - D8 CIGA: ~8.0
- **Research/Award Score** (novelty, math depth, interpretability, report value, reproducibility):
    - D1 BSA‑RP: ~7.9
    - D2 KG‑MoE: ~8.5
    - D3 DRO‑BL: ~9.0
    - D4 LEEQA: ~8.7
    - D5 Reg‑HMM‑RP: ~8.4
    - D6 RAMA‑T: ~8.8
    - D7 OMD‑Band: ~8.4
    - D8 CIGA: ~9.3

**Quadrant placement:**

- **High competition + high research**:
    - **D3 DRO‑BL**, **D6 RAMA‑T**, **D1 BSA‑RP**, **D4 LEEQA**.
    - These are top candidates both for Sharpe/drawdown and for narrative.
- **High competition + lower research**:
    - None are truly “low research”; D2 and D5 are moderately high but slightly less mathematically exotic.
- **Low competition + high research**:
    - **D8 CIGA**, **D7 OMD‑Band** (especially CIGA) — causal and regret-based designs are academically appealing but may be tricky to tune.
- **Low competition + low research**:
    - None (we already filtered trivial baselines out of final set).

**Likely award-winning even without top Sharpe:**

- **D8 CIGA** (causal \& counterfactual framing is distinctive).
- **D3 DRO‑BL** (robust BL + DRO is mathematically deep and clearly explainable).
- **D6 RAMA‑T** (transformer-inspired analogue/RAG design with clear ties to CN‑Buzz2Portfolio).
- **D2 KG‑MoE** or **D4 LEEQA** (graph/MoE and learning-to-rank from news are both strong stories).

H. Baseline-Beating and Ablation Plan
-------------------------------------

**Baselines to implement:**

1. **Equal weight (EW).**
    - Daily rebalancing to 1/N across ETF pool; optionally low-turnover version (rebalance weekly/monthly).
2. **Inverse-volatility allocation (IVOL).**
    - Use past $L$-day vol; $w_i \propto 1/\hat{\sigma}_i$.
3. **Momentum-only.**
    - Cross-sectional scores from 3–6 month returns; allocate proportional to positive momentum, 0 weight for negative.
4. **Sector trend-following (STF).**
    - For Track 2, similar to [sector rotation literature], overweight top-K sectors by trend measures.[^43][^41][^40]
5. **Persistence / low-turnover baseline.**
    - Start from IVOL or STF and only rebalance if signals cross thresholds; aims for low turnover.
6. **Rule-based macro rotation (RMR).**
    - For Track 1: simple macro rules (risk-on, risk-off) based on moving averages or volatility to rotate between equity/credit/safe assets.
7. **News sentiment only (NS).**
    - Aggregate daily news sentiment per ETF and map to tilts without sophisticated modeling (simple linear mapping).
8. **S1 quant core (provided or designed).**
    - Track 1: inverse-vol/momentum/breadth/defensive allocator.
    - Track 2: sector trend-following top-K allocator (e.g. momentum + volatility).

**For each design, promotion criteria vs. baselines:**

- Must **beat S1 quant core** on 2024 walk-forward Sharpe (turnover-adjusted) by a statistically meaningful margin or offer clear research novelty (D8, D7 particularly).
- Must not materially worsen turnover-adjusted Sharpe (e.g. Sharpe after subtracting cost of 0.01%*turnover).
- Performance must be **stable across 3–4 non-overlapping 2024 subwindows** (e.g. Q1, Q2, Q3+Q4).
- Must be implementable with **2024-only training**; 2025 used for validation only before freezing.
- Must produce **full logs** as requested (daily trades, holdings, raw scoring, state variables).

**Ablation framework (applied to all designs, with specifics as above):**

- **Quant-only vs. LLM-only vs. hybrid.**
    - For LLM-heavy designs (D1, D2, D3, D4, D6, D8), compare:
        - Full hybrid (LLM features + quant engine).
        - Quant-only (replace LLM features with simple bags-of-words or sentiment dictionaries).
        - LLM-only (if safe: direct LLM suggestions converted via simple rules) as a negative baseline.
- **No-news vs. news-only vs. mixed.**
    - Remove news features; keep only returns/vol.
    - Keep news but remove technicals.
- **No memory / retrieval / regime / graph / causal modules.**
    - For each design, drop its “signature” module (memory, graph, HMM, retrieval, causal constraints) and see performance degradation.
- **No risk control / turnover control.**
    - Run unconstrained scores; show blow-up to justify risk engineering.
- **2024-tuned vs 2025-tuned.**
    - Train exclusively on 2024; then compare to variant re-tuned on 2025 to illustrate overfitting risk.

All ablations must be run using the **official backtest engine** and `dataloader_eval.py` for local evaluation to ensure comparability.

I. Hidden B-List Robustness Audit
---------------------------------

Key risks for 2026-01-01–2026-06-01:

1. **Regime shift (macro).**
    - Policy regime, growth/inflation trade-off, or volatility regime may differ significantly from 2024–2025.
    - Designs relying on invariant structures (D3 DRO‑BL, D8 CIGA, D1 BSA‑RP’s robust risk-parity core) should handle this better than fully supervised learners (D4, D6) that might overfit.
2. **Prompt instability / LLM features.**
    - For B-list, we must freeze LLM models and prompts; any non-determinism must be controlled via fixed seeds or offline feature precomputation.
    - Designs using LLM **only offline** for feature extraction (D1–D4–D6–D8) are safer than interactive LLM calls at run-time.
    - Where possible, precompute all 2024–2025 feature tables and ensure code paths for 2026 use the same models.
3. **Dependency risk.**
    - Avoid closed LLM APIs in B-list; instead use open-source models or precomputed embeddings stored with the submission.
    - Simpler designs (D1, D3, D5, D7) with fewer heavy dependencies are safer.
4. **Macro event novelty.**
    - 2026 may include new types of shocks not seen in 2024–2025 (e.g. new regulatory initiatives, geopolitical events).
    - Retrieval-based RAMA‑T might struggle if no analogues exist, but DRO‑BL and CIGA should be relatively robust due to ambiguity sets and causal drivers.
5. **Sector label drift.**
    - ETF compositions change; some thematic ETFs (AI, new energy) may shift holdings.
    - Graph-based KG‑MoE and causal CIGA should be built around **observable price co-movements and news semantics**, not static sector labels.
6. **Data compliance.**
    - All designs must strictly use official DataLoader for prices/news to guarantee no leakage; we should centralize data access in a shared wrapper module so nothing bypasses it.
7. **Overfitting 2025.**
    - There is temptation to respec models on A-list year; we should treat 2025 as **out-of-sample evaluation** and only minimally retune high-level hyperparameters (e.g. dropout or regularization) but not architectures.

**Per-design B-list robustness (short):**

- **D1 BSA‑RP:** Good — belief state + risk parity should generalize; watch LLM feature stability.
- **D2 KG‑MoE:** Medium — GNN may overfit small-sample graph structure; require strong regularization and simple architectures.
- **D3 DRO‑BL:** Very good — explicit ambiguity modeling designed for distribution shift.
- **D4 LEEQA:** Medium — learning-to-rank from 2024 may mis-rank in new regimes; need strong regularization and simple features.
- **D5 Reg‑HMM‑RP:** Good — discrete regimes can capture new states if prior structure is sensible; must avoid overfitting to 2024.
- **D6 RAMA‑T:** Medium — analogues rely on similarity; rare new patterns can break; mitigate via robust priors and fallback to S1.
- **D7 OMD‑Band:** Good — worst-case regret bounds help; but no explicit use of text may miss structural breaks signalled by news.
- **D8 CIGA:** Very good — by focusing on invariant drivers, should be robust to certain shifts, provided the causal model is not mis-specified.

J. Implementation Roadmap
-------------------------

Phased plan assuming 1–2 strong students over summer/autumn 2026 timeline, but respecting pre‑2026 resource constraint.

**Phase 0R: Source/Data Reset (1–2 days)**

- Clone official repo and lock commit hash; set up reproducible environment.
- Validate `dataloader_eval.py` reproduces server `DataLoader` behavior on a subset of days.
- Build a thin **data access layer** that every design uses, wrapping official DataLoader to prevent leakage.

**Phase 1R: Official Starter Reproduction (3–4 days)**

- Run `start_server.py` and `agent_platform/demo_backtest.py` with a simple agent to confirm end-to-end flow.
- Implement and validate baseline strategies: EW, IVOL, Momentum, STF, RMR, NS.
- Confirm Sharpe/drawdown/turnover numbers on 2024 \& 2025 for baselines; store as reference.

**Phase 2R: Baselines \& S1 Quant Core (5–7 days)**

- Implement a strong **S1 quant core** baseline:
    - Track 1: combined IVOL + momentum + defensive tilt.
    - Track 2: sector trend-following top-K with volatility scaling.
- Ensure stable moderate turnover and decent Sharpe; this is the **“bar to beat.”**

**Phase 3R: First Innovative Prototypes (10–14 days)**

- Start with **D1 BSA‑RP** (macro, risk-parity) + **D4 LEEQA** (sector ranking) because they are relatively straightforward and high-ROI.
- Implement minimal versions:
    - D1: risk parity + simple decayed sentiment index;
    - D4: learning-to-rank with basic hand-crafted features (no full LLM yet).
- Evaluate on 2024 and 2025; iterate until they outperform S1 on 2024 in at least one track without excessive turnover.

**Phase 4R: Full Comparison (20–30 days)**

- Incrementally add advanced features:
    - D3 DRO‑BL adding robust optimization;
    - D6 RAMA‑T minimal analogue retrieval;
    - D5 Reg‑HMM‑RP simple 3-regime HMM;
    - D2 KG‑MoE minimal static graph;
    - D7 OMD‑Band and D8 CIGA prototypes once core designs are stable.
- For each, run ablation suite and compare vs. S1 across metrics.
- Decide which 2–3 designs per track merit pushing to “production-quality”.

**Phase 5R: A-list Package (10–15 days)**

- For chosen main designs (likely: D3 + D1 for Track 1; D4 + D2 + D6 for Track 2):
    - Clean code; ensure all data access is via official wrappers.
    - Generate full 2025 A-list logs (decisions, trades, state variables).
    - Build scripts to run backtest end-to-end with reproducible seeds.
- Prepare internal comparison report: performance tables, ablations, graphs.

**Phase 6R: B-list Hardening (7–10 days)**

- Containerize the selected agents; ensure they run **without internet access** and without external API calls.
- Replace any LLM-API calls with local models or precomputed features.
- Add safety checks: fallback to S1 baseline if any module crashes or outputs NaNs.
- Run stress-tests: random restarts, different subsets of dates, and mild model perturbations to ensure deterministic output.

K. Final Recommendation
-----------------------

Based on the ROI scores, design diversity, and implementation difficulty:

1. **Best performance-first design (competition focus).**
    - **D3 DRO‑BL** with D1 BSA‑RP-style risk parity as a baseline core.
    - For Track 1, this combination is particularly compelling: robust BL views from news plus risk-parity base should yield strong Sharpe and drawdown control, with built-in robustness to regime shifts.[^13][^16][^14][^18]
2. **Best research/award design (paper/creativity).**
    - **D8 CIGA** and **D6 RAMA‑T** as top candidates.
    - CIGA for its causal driver/invariance story; RAMA‑T for transformer-inspired retrieval analogues directly linked to CN‑Buzz2Portfolio and modern RAG ideas.[^3][^24][^35][^38][^1][^2][^34][^36]
    - D3 DRO‑BL is also very strong for research awards, especially to more quantitatively oriented reviewers.
3. **Best one-student design (solo feasibility).**
    - **D1 BSA‑RP** or **D4 LEEQA**.
    - Both can be implemented with moderate ML/quant effort and modest LLM dependence; they yield a clean narrative and plausible performance uplift.
4. **Best Track 1 design (macro).**
    - **Primary: D3 DRO‑BL** (with risk-parity baseline).
    - **Secondary/back-up: D1 BSA‑RP** and **D5 Reg‑HMM‑RP**.
    - These jointly emphasize macro regimes, robust risk, and text-conditioned views.
5. **Best Track 2 design (sector rotation).**
    - **Primary: D4 LEEQA + D2 KG‑MoE** (they can even be combined: LEEQA score as node feature in KG‑MoE).
    - **Secondary: D6 RAMA‑T** for a transformer/RAG-style competitor.
    - Together they exploit sector-specific news, graph structure, and ranking.
6. **Designs to reject (for now).**
    - Naive **LLM-Direct-Agent** (“LLM says weights”) and simple BL-LM without DRO or proper risk control — they are good as baselines, not as main entries.
    - Any design that depends on large proprietary LLM APIs during B-list (non-deterministic, fragile, compliance risk).
7. **Exact first implementation target.**

Given limited time and desire for quick wins:
    - **Track 1**: Implement **D1 BSA‑RP** first (risk parity + decayed sentiment) as a robust improvement over S1.
    - **Track 2**: Implement **D4 LEEQA** first (learning-to-rank on simple features) as a structured news-to-allocation method.

These two form a strong baseline pair that already satisfy most of the competition’s narrative goals (belief state + ranking), and they are feasible for a single student within a few weeks.
8. **Exact fallback if novelty underperforms.**
    - If advanced modules (D3 DRO‑BL, D6 RAMA‑T, D8 CIGA) **do not yield robust performance gains** over S1 and D1/D4, fall back to:
        - **Track 1**: D1 BSA‑RP with more conservative tilts and stronger risk parity; treat DRO‑BL as an analysis tool (report-only).
        - **Track 2**: Combine S1 sector trend-following with D4’s ranking as a **tie-breaker/overlay** rather than full replacement.
    - Ensure fallback strategies meet:
        - Non-worse turnover-adjusted Sharpe than S1 on 2024,
        - Stable performance across 2024 subwindows,
        - Fully reproducible runs on A-list and B-list.

In concrete terms, I would recommend:

- **Phase 3 focus**: D1 (Track 1) + D4 (Track 2) to quickly establish a strong baseline above S1.
- **Phase 4 focus**: D3 (Track 1), D2 + D6 (Track 2), plus one of D5 or D8 as an additional research entry.
- **Paper narrative**: center around **D3 DRO‑BL** (robust views from news), **D6 RAMA‑T** (retrieval/transformer-inspired analogues), and **D8 CIGA** (causal drivers), with D1 and D4 as operational workhorses that are likely to deliver competitive Sharpe in the leaderboard setting.
<span style="display:none">[^50][^51][^52][^53][^54][^55][^56][^57][^58][^59][^60][^61][^62][^63][^64][^65][^66][^67][^68][^69][^70][^71][^72][^73][^74][^75][^76][^77][^78][^79][^80][^81][^82][^83][^84][^85][^86][^87][^88]</span>

<div align="center">⁂</div>

[^1]: https://arxiv.org/abs/2603.22305

[^2]: https://www.semanticscholar.org/paper/7897014ae2caeee70d65df37ba8e5ed2bb3c4aee

[^3]: https://papers.cool/arxiv/2603.22305

[^4]: http://arxiv.org/pdf/2306.14222.pdf

[^5]: http://arxiv.org/pdf/2408.02302.pdf

[^6]: https://arxiv.org/pdf/2310.15205.pdf

[^7]: http://arxiv.org/pdf/2403.06249.pdf

[^8]: http://arxiv.org/pdf/2309.10654.pdf

[^9]: https://ar5iv.labs.arxiv.org/html/2602.00082

[^10]: https://arxiv.org/html/2409.06289v4

[^11]: https://github.com/Tom-roujiang/Awesome-LLM-Quantitative-Trading-Papers

[^12]: https://arxiv.org/html/2602.00082v1

[^13]: https://arxiv.org/abs/2103.16451

[^14]: https://pubsonline.informs.org/doi/10.1287/mnsc.2021.4155

[^15]: http://www.columbia.edu/~xz2574/download/BCZ-final.pdf

[^16]: https://www.sciencedirect.com/science/article/abs/pii/S0305048317312604

[^17]: https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID3929598_code2703583.pdf?abstractid=3542667\&mirid=1

[^18]: https://magesblog.com/post/2023-02-15-portfolio-allocation-for-bayesian-dummies/

[^19]: http://link.springer.com/10.1007/s10994-007-5016-8

[^20]: https://andrewcharlesjones.github.io/journal/universal-portfolios.html

[^21]: https://onlinelibrary.wiley.com/doi/10.1111/mafi.12006

[^22]: https://neurips.cc/virtual/2023/poster/72840

[^23]: https://bohrium.dp.tech/paper/arxiv/ba3a05819333813cc83ebaaf8b3829758f782a26fb056ac2b38e54c7440a11c1

[^24]: https://arxiv.org/abs/1912.09363

[^25]: https://www.sciencedirect.com/science/article/pii/S0169207021000637

[^26]: https://www.marketcalls.in/python/introduction-to-hidden-markov-models-hmm-for-traders-python-tutorial.html

[^27]: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=2588380

[^28]: https://www.academia.edu/27971290/Derivation_of_Kalman_Filter_Estimates_Using_Bayesian_Theory_Application_in_Time_Varying_Beta_CAPM_Model

[^29]: https://www.intechopen.com/chapters/1172965

[^30]: https://ieeexplore.ieee.org/document/11415719/

[^31]: https://linkinghub.elsevier.com/retrieve/pii/S0968090X24000421

[^32]: https://www.mdpi.com/2076-3417/16/10/4585

[^33]: https://ieeexplore.ieee.org/document/10903818/

[^34]: https://afajof.org/management/viewp.php?n=150052

[^35]: https://www.loualiche.com/docs/causal_inference_HHHKL.pdf

[^36]: https://sysmath.cjoe.ac.cn/jweb_xtkxysx/EN/10.12341/jssms241078

[^37]: https://www.theamericanjournals.com/index.php/tajiir/article/view/6431

[^38]: https://arxiv.org/html/2502.05878v1

[^39]: https://www.linkedin.com/posts/pranay-gaurav-290a30150_retrieval-augmented-generation-rag-in-activity-7307649101586718720-gxaV

[^40]: https://arxiv.org/abs/2108.02838

[^41]: https://www.semanticscholar.org/paper/0faad3434e096fae162b55fa241748ef333e0f0a

[^42]: https://www.scribd.com/document/885247602/ssrn-3683454

[^43]: https://www.ssga.com/uk/en_gb/intermediary/insights/sector-etf-momentum-map

[^44]: https://asymmetryobservations.com/definitions/sector-rotation/

[^45]: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5111794

[^46]: https://ieeexplore.ieee.org/document/9930570/

[^47]: https://link.springer.com/10.1007/s10436-026-00480-5

[^48]: http://www.pokutta.com/blog/research/2019/08/29/universalPortfolios.html

[^49]: https://arxiv.org/abs/2308.07763

[^50]: https://www.semanticscholar.org/paper/5ea65609229aa555afa36a644c721cbc26d2adb7

[^51]: https://www.semanticscholar.org/paper/e9b2730de6f3ed0d188cb07baddf9db692389ee2

[^52]: https://linkinghub.elsevier.com/retrieve/pii/S0140673606691319

[^53]: https://aclanthology.org/2023.findings-emnlp.269.pdf

[^54]: https://arxiv.org/html/2401.06164v1

[^55]: https://github.com/splash-li/NLPCC2026-Shared-Task-4/pulls

[^56]: https://401kspecialistmag.com/kitces-reveals-best-financial-advisor-conferences-to-attend-in-2026/

[^57]: https://github.com/splash-li/NLPCC2026-Shared-Task-4/security

[^58]: https://elitert.com/blog/the-best-financial-advisor-conferences-to-attend-in-2026

[^59]: https://github.com/splash-li/NLPCC2026-Shared-Task-4/

[^60]: https://www.investmentnews.com/practice-management/ria-conferences-usa-2026/264991

[^61]: https://nlp2ct.github.io/NLPCC-2026-Task6-Detection/

[^62]: https://www.riachannel.com/conference-calendar/

[^63]: http://tcci.ccf.org.cn/conference/2026/shared-tasks/

[^64]: https://openreview.net/group?id=ccf.org%2FNLPCC%2F2026%2FShared_Tasks

[^65]: https://www.aclweb.org/portal/events?order=field_event_date\&sort=desc

[^66]: https://arxiv.org/pdf/2503.09647.pdf

[^67]: http://arxiv.org/pdf/2405.09747.pdf

[^68]: https://portfoliopilot.com/portfolio-management/resources/beyond-the-hype-strategic-asset-allocation-explained-for-the-modern-investor

[^69]: https://www.linkedin.com/posts/snehabhapkar_trading-agents-activity-7389219469945901056-U14D

[^70]: https://www.ainvest.com/news/dividend-driven-global-asset-allocation-navigating-income-generation-yield-world-2509/

[^71]: https://www.nb-data.com/p/best-stock-market-data-api-in-the

[^72]: https://www.semanticscholar.org/paper/CN-Buzz2Portfolio:-A-Chinese-Market-Dataset-and-for-Chen-Li/7897014ae2caeee70d65df37ba8e5ed2bb3c4aee

[^73]: https://www.youtube.com/watch?v=bIbp44_x3Vc

[^74]: https://arxiv.org/abs/2512.05907

[^75]: https://x.com/Memoirs/status/2036876980394606605

[^76]: https://people.duke.edu/~charvey/Media/2009/II_September_02_2009.pdf

[^77]: https://arxiv.org/html/2512.05907v1

[^78]: https://ieeexplore.ieee.org/document/10812177/

[^79]: https://www.ewadirect.com/proceedings/aemps/article/view/14201

[^80]: https://www.semanticscholar.org/paper/e944d981364053ff61b7b479495f2b3b1cf6623f

[^81]: https://ieeexplore.ieee.org/document/11156627/

[^82]: https://mpelger.people.stanford.edu/research

[^83]: https://ieeexplore.ieee.org/document/10428726/

[^84]: https://ieeexplore.ieee.org/document/10654340/

[^85]: https://arxiv.org/abs/2509.25435

[^86]: https://www.ssga.com/us/en/intermediary/model-portfolio/state-street-us-equity-sector-rotation-etf-portfolio-241111104250_glblmkt

[^87]: https://blog.quantinsti.com/regime-adaptive-trading-python/

[^88]: https://dl.acm.org/doi/abs/10.1007/s10115-018-1315-6

