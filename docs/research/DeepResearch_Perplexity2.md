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

Emphasis tag:
Prioritise graph-based, causal, and knowledge-grounded systems:

- ETF-sector-policy knowledge graphs,
- graph neural networks,
- causal event-impact maps,
- counterfactual event stress tests,
- invariant risk minimisation,
- policy-to-sector transmission channels,
- cross-source event validation.

A. Official Task Constraints and Research Opportunity
-----------------------------------------------

**Verified official facts (from CN-Buzz2Portfolio paper, which underlies this shared task):**

- The task is a **Chinese-market benchmark mapping daily trending financial news (“Buzz”) to macro and sector ETF allocation**, with two asset universes: Task A (macro/thematic) and Task B (sector rotation).[^1]
- The dataset aggregates **Top‑20 daily trending topics** from **four major Chinese financial platforms** (Caixin, Sina Finance, Tencent Stock, Tiantian Fund), treated as a public attention stream rather than entity-filtered news.[^1]
- At each day $t$, the agent’s observation includes news $N_t$, historical prices and trades $(P_{\text{hist}}, T_{\text{hist}})$, and current holdings $H_t$, and issues a rebalancing instruction $w_{t+1}$ executed at the **close of day $t$**.[^1]
- **Strict timestamp filtering:** only news published **before market close on day $T$** is available to decide allocations for day $T$, explicitly to avoid look‑ahead bias.[^1]
- Simulation environment: **retail investor setting** with **100,000 RMB** initial capital, **ETF feeder funds** as asset proxies, **daily close execution**, and **transaction fee 0.01%** (1 bp) per trade, used as a turnover penalty.[^1]
- Asset universes:
    - **Task A / Track 1 analogue (Macro \& Thematic Allocation):** 11 broad assets including equity indices (e.g., CSI 300, CSI 500, ChiNext), bonds, gold, and style/thematic indices.[^1]
    - **Task B / Track 2 analogue (Sector Rotation):** 14 sector ETFs (e.g., New Energy, TMT, Financials, Real Estate, Liquor, Healthcare, Semiconductors), chosen by liquidity/AUM criteria.[^1]
- Evaluation periods in the benchmark: **full year 2024** (high-volatility bear→policy-rally regime) and **H1 2025** (sideways, oscillatory regime).[^1]
- Reported baseline metrics include **cumulative return, Sharpe ratio, max drawdown, volatility**, with classic quant baselines (Momentum and MVO), market indices (CSI 300) and equal-weight portfolios.[^1]
- The paper explicitly frames the system as a **Tri‑Stage CPA multi-agent workflow (Compression–Perception–Allocation)** and emphasizes that numeric execution is handled by a deterministic engine, with **budget-based buys** and **ratio-based sells**.[^1]

**Highly likely but not directly verifiable here (due to current inability to fetch the GitHub repo):**

- Naming and structure “NLPCC2026-Shared-Task-4” and the specific task title “LLM-based Investment Advisor Agents for Asset Allocation in the Chinese Market” come from external references and the user prompt.
- That **public 2024 data is provided for training**, **public 2025 for Phase A / A‑list evaluation**, and **2026‑01‑01 to 2026‑06‑01 as private B‑list blind evaluation**, is consistent with how CN‑Buzz2Portfolio rolls 2024–H1 2025 and with typical shared-task setups, but I cannot see the competition README to fully confirm the 2026 dates and split.

**Reasonable implications for system design (inferred, not stated verbatim in official text):**

- The environment is **daily frequency**; intraday forecasts or microstructure alpha are *out of scope* for this task.[^1]
- The asset universes (macro vs sector) are small (11 and 14), which makes **full covariance modelling, Black‑Litterman, DRO, HMMs, and bandit-style allocators computationally feasible**.
- The presence of a **Momentum baseline and MVO baseline** with non-trivial Sharpe shows that **purely quant systems already perform reasonably**, so incremental Sharpe must be earned with disciplined risk and turnover, not naive “LLM magic”.[^1]
- The paper’s own results show:
    - In 2024, **quantitative MVO beats most LLM agents in macro allocation**, while LLM agents shine more in **sector rotation**.[^1]
    - In 2025 H1, **Top‑0 (no news, price‑only) sometimes outperforms news-augmented agents** (“Top‑0 paradox”), highlighting the risk of over‑reacting to noisy narratives.[^1]

**Still-uncertain points (must be handled conservatively in design):**

- Exact official **cutoff time for same‑day decision** (the paper states “before market close”, but competition may enforce a concrete timestamp such as 14:30; without the repo we must design to respect **no access to close/high/low/return of day $t$** before issuing orders).
- Detailed **submission protocol, Docker expectations, and on‑server evaluation hooks** in `backtest.py` / `data_loader.py` – we must assume a pure Python interface where our allocator receives a standardized state and returns normalized target weights.
- Any **limits on external models/data** beyond “no post‑2025 knowledge” and Chinese regulatory considerations – we should design under the safe assumption:
    - **All models must be fully downloadable or trainable from pre‑2026 data**,
    - No online APIs during B‑list evaluation,
    - No use of future macro announcements or non-public datasets.

**Research opportunity:**

- CN‑Buzz2Portfolio itself criticizes end‑to‑end LLM trading as irreproducible and regime‑fragile, and explicitly promotes **logic‑driven, interpretable asset allocation under a standardized backtest engine**.[^1]
- The paper exposes several deep phenomena (information utility curve, Top‑0 paradox, scaling-law paradox) that can be *directly addressed* by mathematically structured agents: e.g., **filtering noisy news, regime‑adaptive use of news, and robust portfolio construction**.[^2][^1]
- Combining this benchmark with advances in **LLM trading agents, news-driven portfolio construction, DRO/Black‑Litterman, IRM/causal representations, and temporal transformers/SSMs** offers a rich space for award‑worthy architectures.[^3][^4][^5][^6][^7][^8][^9][^2]

B. Research Source Ledger
-------------------------

| Source | Type | What it contributes | Reliability | How it affects design |
| :-- | :-- | :-- | :-- | :-- |
| CN-Buzz2Portfolio arXiv paper (2603.22305) | Official benchmark paper | Formal task definition, asset universes, Top‑20 Buzz, 0.01% cost, 2024 \& 2025 periods, Tri‑Stage CPA baseline, baseline results | Very high[^1] | Primary constraint and baseline reference; all designs must be compatible with its environment and metrics |
| “Large Language Model Agent in Financial Trading: A Survey” (arXiv 2408.06361) | Survey | Taxonomy of LLM trading agents, common architecture patterns, limitations (over‑fitting, hallucinations, evaluation issues) | High[^2] | Guides which LLM roles are credible (event extraction, reasoning, verification) vs risky (direct order generation) |
| “Agentic Trading: When LLM Agents Meet Financial Markets” (arXiv 2605.19337) | Research | Patterns for multi‑agent LLM trading systems, evaluation protocols, and guardrails | High[^10] | Motivates multi‑module and verifier/critic designs instead of monolithic LLM traders |
| TradingAgents: Multi-Agents LLM Financial Trading Framework (arXiv 2412.20138) | Research code+paper | Multi‑role agents (fundamental, sentiment, risk manager), debate, and risk controls in LLM trading | High[^11] | Inspires structured role separation (analyst vs allocator vs risk controller) |
| Text-based portfolio selection via stock–news embeddings (STED) | Journal article | Joint embedding of stocks, news, events for portfolio optimization with better tail risk handling | High[^4] | Underpins event‑to‑asset embedding and attention design (news→ETF impact matrices) |
| Conditional Asset Pricing with Text-Managed Portfolios | SSRN paper | Text-conditioned managed portfolios from earnings call texts; text adds covariance information beyond characteristics | High[^5] | Motivates using text as a factor that changes **covariance structure**, not only expected returns |
| Distributionally Robust Portfolio Optimization | CDC paper | Wasserstein/DRO framing for portfolio selection under distributional uncertainty | High[^3] | Justifies DRO/robust‑BL engines for B‑list robustness to 2026 regime shifts |
| Black-Litterman Model overview | Practitioner article | Clear BL formulae, equilibrium prior plus views with confidence, known implementation pitfalls | Medium–high[^12] | Provides concrete parameterization for view-based macro \& sector tilts driven by news |
| Invariant Risk Minimization \& follow‑ups | Theory papers | IRM/ICRL frameworks linking invariant representations to causal structure and OOD generalization | High[^13][^14][^8][^15] | Basis for causal event–impact graph and regime‑robust feature learning from multiple environments (2024 vs 2025 vs synthetic regimes) |
| Time Series Forecasting with Transformer Models in Finance | SSRN \& arXiv | Transformer architectures for financial forecasting, attention over long time horizons | High[^7][^16] | Inspires transformer-like event memory allocator (TEMA) with explicit time-decay, state-space ideas |
| Modality-aware Transformer for Financial Time Series | arXiv | Multimodal transformer combining numeric series and categorical/textual signals with intra/inter-modal attention | High[^9] | Supports combining news embeddings with price features via modality-aware attention |
| Two-Stage Sector Rotation Methodology Using ML \& DL | arXiv | ML-based sector rotation: macro indicators + RNN forecasts + ranking sectors by predicted returns | High[^17][^6] | Forms baseline for learning-to-rank sector allocator and informs ranking‑based portfolio rules |
| LLM in trading \& portfolio surveys (“The New Quant” etc.) | Surveys | Design patterns, evaluation pitfalls, and guardrails for LLM-assisted asset management | Medium–high[^18] | Encourages using LLMs as **copilots** (signal generation, explanation, consistency checks) rather than autonomous allocators |

C. Candidate Design Universe
----------------------------

Below are **12 candidate designs**, then later we will consolidate to 7 final blueprints.

For each: name, core idea, engine, LLM role, track fit, decision.

1. **BSA-RP: Belief-State Regime \& Risk-Parity Allocator**
    - Core idea: Bayesian latent macro‑regime posterior $p(z_t \mid \text{prices}, \text{news})$ updated daily; use regime‑specific expected returns and covariance plugged into a **risk‑parity / risk‑budgeting** allocator.
    - Engine: HMM/Kalman filter (belief state) + risk‑parity optimization.
    - LLM role: Map each day’s Buzz to **likelihood over regimes** and to regime‑specific factor shocks.
    - Track fit: Strong for Track 1 (macro regimes); moderate for Track 2 (if regimes partly sectoral).
    - Keep/merge? **Keep** — core belief‑state/memory agent.
2. **KG-MoE: Knowledge-Graph Mixture-of-Experts Allocator**
    - Core idea: Build **ETF–sector–policy knowledge graph**, run GNN to propagate event signals, and route to different expert allocators per structural pattern (e.g., policy support vs crackdown).
    - Engine: Graph neural network over ETF/sector/policy nodes + mixture-of-experts allocator.
    - LLM role: Event extraction, entity \& policy tagging, edge creation, and occasional route explanations.
    - Track fit: Good for both; especially Track 2.
    - Keep/merge? **Keep** — flagship graph/knowledge-grounded system.
3. **DRO-BL: Distributionally Robust Black-Litterman Agent**
    - Core idea: Use **news-derived views** on macro \& sectors to tilt a Black‑Litterman prior, but embed BL into a **distributionally robust optimization** (min‑max over Wasserstein ball), with turnover and drawdown penalties.
    - Engine: BL + DRO mean–variance / CVaR optimizer.[^12][^3]
    - LLM role: Structured extraction of qualitative “views” (sign, magnitude, confidence) on assets/regimes; no direct weights.
    - Track fit: Very strong for Track 1; decent for Track 2.
    - Keep/merge? **Keep** — main robust portfolio-theoretic design.
4. **TEMA: Transformer Event Memory Allocator**
    - Core idea: Train a **small, task-specific transformer / hybrid state-space model** over sequences of event embeddings and price factors to maintain a latent **event memory state** $h_t$, then map to portfolio weights via a deterministic layer.[^7][^16][^9]
    - Engine: Custom transformer/SSM with explicit time-decay and news gating; no external LLM at inference.
    - LLM role: Offline **pre‑training of event encoders** \& lexicons only (pre‑2026), or none.
    - Track fit: Strong for both; especially robust if overfitting controlled.
    - Keep/merge? **Keep** — transformer‑inspired, non‑API design.
5. **RAL-Rank: Retrieval-Augmented Learning-to-Rank Meta Allocator**
    - Core idea: For each day, **retrieve analogous historical days** (by joint news+price embeddings), then train a **learning-to-rank model** over assets or candidate base strategies (EW, vol‑inv, momentum, BL, etc.), learning which ones performed best in matched analogues.
    - Engine: k‑NN retrieval + gradient-boosted / neural ranker taking analogue statistics as features.[^4][^17]
    - LLM role: Event embedding and event-type tagging; optional commentary.
    - Track fit: Strong for Track 2 (pattern-rich sectors); good for Track 1.
    - Keep/merge? **Keep** — covers learning-to-rank, meta-allocation, retrieval-agent family.
6. **OCO-Bandit: Online Convex / Bandit Allocator with News Features**
    - Core idea: Treat ETFs or sector tilts as arms in a **combinatorial bandit / online convex optimization** framework; linear (or kernel) bandits with contextual features from news factors and price factors, with explicit regret-minimizing updates and turnover penalties.[^3]
    - Engine: Online mirror descent / EXP3-style updates with constraints.
    - LLM role: Map news into low‑dimensional, bounded **context vectors**; no direct action.
    - Track fit: Good for both tracks; especially for stable incremental adaptation.
    - Keep/merge? **Keep** — covers online/bandit family.
7. **CEIG: Causal Event-Impact Graph Allocator (IRM-based)**
    - Core idea: Learn a **causal graph** between policy events, sectors, and macro factors by exploiting multiple environments (2024 vs 2025 sub‑regimes) and IRM/ICRL, then allocate by stress‑testing counterfactual shocks along this graph (e.g., “policy easing in green energy”).[^13][^8][^15]
    - Engine: Causal representation learning + IRM constraints + robust optimizer.
    - LLM role: Event typing into causal variable categories; proposing candidate edges; human‑audited.
    - Track fit: Very strong research angle; moderate performance expectation.
    - Keep/merge? **Keep** — this is the main causal/counterfactual design.
8. **EM-HMM: Event-Driven Hidden Markov Model Allocator**
    - Core idea: HMM with transition probabilities modulated by event scores (e.g., supportive vs restrictive policy), mapping hidden regimes to sector tilts.
    - Engine: HMM + simple mean–variance or risk‑parity allocations per regime.[^19]
    - LLM role: News sentiment / policy sign scoring.
    - Track fit: Decent; but conceptually overlaps with BSA-RP belief-state approach.
    - Keep/merge? **Merge into BSA-RP** as a special case.
9. **KG-Only GNN Allocator (no LLM)**
    - Core idea: Purely data-driven GNN over sector/ETF correlation/beta graph for propagation of historical factor shocks into allocations.
    - Engine: Static graph + message passing + portfolio head.
    - LLM role: None.
    - Track fit: Reasonable, but duplicates part of KG-MoE without LLM‑driven event wiring.
    - Keep/merge? **Merge** into KG-MoE as an ablation (“no LLM edges”).
10. **Pure CPA LLM Agent (Tri-Stage) with Hard Risk Wrapper**
    - Core idea: Re‑implement Tri‑Stage CPA pipeline with a strong LLM (DeepSeek/Qwen/GPT) but wrap its allocations with a hard risk/turnover projection layer.
    - Engine: LLM-in-the-loop decision; post‑projection onto feasible region.
    - LLM role: Essentially allocator; risk wrapper may veto.
    - Track fit: As shown in CN‑Buzz2Portfolio, LLMs can be competitive but fragile.[^1]
    - Keep/merge? **Reject as primary design** (kept as baseline for comparison only).
11. **IR-PRP: Invariant Risk Parity under Multi-Environment Training**
    - Core idea: Learn factor representations whose contribution to Sharpe is invariant across 2024 sub‑regimes using IRM, then apply risk‑parity allocation in that stable factor space.
    - Engine: IRM representation + risk‑parity.
    - LLM role: None or minor.
    - Track fit: Reasonable; but conceptually close to CEIG and BSA-RP.
    - Keep/merge? **Defer**; CEIG covers better story.
12. **SSM-PriceOnly Universal Portfolio (Transformer-lite)**
    - Core idea: Transformer/SSM that only sees prices and volume, learning universal portfolio weights; no news.
    - Engine: Transformer TS model.[^16][^20]
    - LLM role: None.
    - Track fit: Good quant baseline but lacks news usage.
    - Keep/merge? **Use as quant baseline**, not as one of the novel blueprints.

**Final selection:** We will carry forward **7 designs**:

1. BSA-RP (belief-state / memory agent)
2. KG-MoE (graph / KG agent)
3. DRO-BL (robust portfolio-theoretic agent)
4. TEMA (transformer-inspired, small model)
5. RAL-Rank (learning-to-rank, retrieval agent)
6. OCO-Bandit (online/bandit allocator)
7. CEIG (causal / counterfactual agent)

D. Five to Eight Final Design Blueprints
----------------------------------------

Below I outline each blueprint briefly; Section E gives the math in detail.

### 1. BSA-RP: Belief-State Regime \& Risk-Parity Allocator

- **Thesis:** Maintain a **Bayesian belief state over macro/semi‑structural regimes**, updated using both prices and LLM‑extracted event signals, and allocate via **regime‑conditioned risk‑parity** with drawdown and turnover controls.
- **Novelty vs naive systems:**
    - Not “LLM says buy/sell”; LLM supplies structured likelihoods (e.g., “regime likely easing‑policy, high policy support for infra/green sectors”) feeding a **filter**.
    - Goes beyond momentum/sentiment by modeling a **latent Markovian regime** and using that as state for portfolio optimization.
    - Draws directly on **HMM/Kalman filtering and state-space models** with explicit portfolio risk‑parity mapping.
- **State:** $s_t = (p_t(z), \hat{\mu}_t(z), \hat{\Sigma}_t(z))_{z \in \mathcal{Z}}$, where $\mathcal{Z}$ is a small set of regimes (e.g., easing, tightening, risk‑off, risk‑on, sector‑rotation).[^19]


### 2. KG-MoE: Knowledge-Graph Mixture-of-Experts Allocator

- **Thesis:** Construct a **policy–macro–sector–ETF knowledge graph**, encode events as signals on this graph, propagate via GNN, and let a **mixture-of-experts router** choose among specialized allocators conditioned on graph embeddings.
- **Novelty:**
    - Strongly **knowledge‑grounded**: uses sector taxonomies, ETF constituents, and historical policy–sector impact relations.
    - MoE router borrows from **transformer MoE routing** but routes between *financial allocators* (e.g., BL, risk parity, trend‑following) based on graph conditions.
    - Goes beyond standard sentiment or RAG: the graph structure itself expresses causal/structural relations between policies and sectors.
- **State:** $G_t = (V, E_t, X_t)$ with node embeddings $h_t(v)$ from a GNN; router state $r_t$ determining expert mixing weights.


### 3. DRO-BL: Distributionally Robust Black-Litterman Agent

- **Thesis:** Use news-derived views to tilt a **Black-Litterman prior** over ETF returns, but solve a **distributionally robust optimization** over a Wasserstein ball around the historical return distribution, plus explicit turnover and drawdown controls.[^12][^3]
- **Novelty:**
    - Combines **LLM-structured views** with rigorous **DRO** to hedge estimation and regime risk.
    - Text modifies both expected returns and, via text-managed portfolios, indirectly the covariance structure.[^5]
    - Produces clean ablations: BL‑only, BL+LLM views, BL+DRO, etc.
- **State:** Ambiguity set $\mathcal{P}_t$ over returns, BL prior mean $\pi_t$, view matrix $P_t$, view vector $Q_t$, view uncertainty $\Omega_t$.


### 4. TEMA: Transformer Event Memory Allocator

- **Thesis:** Train a **compact transformer / SSM** that maintains a **latent event memory** summarizing recent Buzz and price history, then map to allocations via deterministic heads with built‑in volatility and turnover controls.[^9][^7]
- **Novelty:**
    - Uses **transformer internals (attention, positional decay, residual memory)** for event half‑life modeling, but **does not call big external LLM APIs**.
    - End‑to‑end trainable on 2024 data only, with clear regularization and OOD checks.
    - Supports clean experiments on **context length, decay structure, and memory gating** (as in SSMs).[^21]
- **State:** $h_t$, the final transformer hidden state after processing a rolling window of $(x_{t-L+1}, \dots, x_t)$, where $x_t$ concatenates price factors and fixed event embeddings.


### 5. RAL-Rank: Retrieval-Augmented Learning-to-Rank Meta Allocator

- **Thesis:** For each day, **retrieve analogous historical days** using joint news/price embeddings, then train a **learning-to-rank model** that chooses among candidate allocations (or assets) given analogue performance patterns.
- **Novelty:**
    - Moves from “LLM decides portfolio” to “**meta‑allocator** chooses among robust baselines using evidence from analogue markets”.
    - Directly operationalizes the **event-based trading \& analogue regime** literature; text is used to define similarity, not to hallucinate trades.[^22][^23]
    - Supports event‑specific case studies (e.g., how past “policy easing for property” analogues behaved).
- **State:** $a_t$: feature vector summarizing k‑nearest historical analogues (e.g., average subsequent returns of each baseline strategy, dispersion, regime tags).


### 6. OCO-Bandit: Online Convex / Bandit Allocator with News Features

- **Thesis:** Interpret ETF weights as an action in a **simplex**, and update daily via **online mirror descent / FTRL** with loss functions shaped by realized returns and turnover, using **news‑derived features** to modulate learning rates or arm biases.
- **Novelty:**
    - Brings **online convex optimization \& universal portfolio theory** into the Buzz2Portfolio setting, with provable regret bounds against the best fixed or slowly‑varying portfolio.[^3]
    - LLM only supplies low‑dimensional, bounded features (e.g., news factor scores); allocator remains fully deterministic.
    - Clean ablations: pure OCO vs OCO+news contexts vs OCO+regime gating.
- **State:** Past cumulative gradients $g_{1:t}$, current weight vector $w_t$, context features $c_t$.


### 7. CEIG: Causal Event-Impact Graph Allocator (IRM-based)

- **Thesis:** Learn a **causal event→factor→sector graph** using IRM/ICRL across multiple environments (2024 vs 2025 sub‑regimes), then allocate by computing **counterfactual sector returns under current event set**, with conservative risk controls.[^8][^15]
- **Novelty:**
    - Explicitly targets **invariant, causal signal extraction** from news, not just predictive correlations.
    - Leverages IRM/ICRL theory for **OOD robustness**, directly addressing B‑list regime shift risk.[^14][^13]
    - Enables compelling counterfactual stress tests (“what if policy had not been announced?”) and rich narrative for the system report.
- **State:** Structural model with latent factors $F_t$, sector returns $R_t$, and event variables $E_t$; causal parameters $\theta$ estimated under constraints of invariance across environments.

E. Mathematical Formulation of Each Design
------------------------------------------

I’ll now specify for each design:

- State variable
- Update rule
- Score-to-weight rule
- Risk control
- Turnover control

All formulas are schematic and would be instantiated separately for Track 1 vs Track 2 (different assets, covariances, priors).

### 1. BSA-RP: Belief-State Regime \& Risk-Parity Allocator

**State representation**

Let regimes $z_t \in \{1,\dots,K\}$. For each regime $k$:

- Conditional return distribution for asset vector $R_t$: $R_t \mid z_t = k \sim \mathcal{N}(\mu_k, \Sigma_k)$.
- State at time $t$:

$$
s_t = \left( p_t(k) \right)_{k=1}^K, \quad \text{with } \sum_k p_t(k) = 1.
$$

We define **regime-averaged mean and covariance**:

$$
\bar{\mu}_t = \sum_{k} p_t(k)\,\mu_k, \quad
\bar{\Sigma}_t = \sum_k p_t(k)\,\Sigma_k + \sum_k p_t(k) (\mu_k - \bar{\mu}_t)(\mu_k - \bar{\mu}_t)^\top.
$$

**Update rule**

- HMM transitions: $p(z_t = j \mid z_{t-1} = i) = A_{ij}$.
- Likelihood from **price**: $L^{\text{price}}_k \propto \mathcal{N}(R_{t-1}; \mu_k, \Sigma_k)$.
- Likelihood from **news** (LLM-derived): for each day we extract a vector of *event features* $e_t$, then LLM (or smaller classifier) outputs $\ell_k(e_t)$, interpreted as $\log$ likelihood contribution for regime $k$.

Bayesian filter:

$$
\tilde{p}_t(k) \propto \sum_i A_{ik}\,p_{t-1}(i), \quad
p_t(k) \propto \tilde{p}_t(k) \cdot L^{\text{price}}_k \cdot \exp(\ell_k(e_t)).
$$

Normalization ensures $\sum_k p_t(k)=1$.

**Score-to-weight rule (risk parity)**

Define risk contributions under $\bar{\Sigma}_t$. Risk-parity target $w_t^\star$ solves:

$$
\min_{w \in \mathcal{W}} \left\| R(w) - \frac{1}{n}\mathbf{1} \right\|_2^2
$$

where $R(w) = (w_i (\bar{\Sigma}_t w)_i / (w^\top \bar{\Sigma}_t w))_{i=1}^n$ are fractional risk contributions, and $\mathcal{W}$ is the feasible set (weights sum to 1, non‑negative, per‑asset caps).

We adjust for expected return by **regime‑weighted tilt**:

$$
\hat{w}_t = \arg\max_{w \in \mathcal{W}} \left\{ 
  \alpha\,w^\top \bar{\mu}_t - (1-\alpha)\, w^\top \bar{\Sigma}_t w
\right\}
$$

for a small $\alpha$ (risk‑parity‑tilted). This can be solved as QP.

Then blend:

$$
\tilde{w}_t = (1-\beta)\,w_t^\star + \beta\,\hat{w}_t.
$$

**Risk control**

- **Volatility target:** enforce $w_t^\top \bar{\Sigma}_t w_t \le \sigma_{\max}^2$.
- **Max asset weight:** $0 \le w_{t,i} \le c_{\max}$.
- **Cash buffer:** add a pseudo asset “cash” to absorb risk reductions.

**Turnover control**

Given previous weights $w_{t-1}$, we project $\tilde{w}_t$ onto a turnover ball:

$$
w_t = \arg\min_{w \in \mathcal{W}} \frac{1}{2}\|w - \tilde{w}_t\|_2^2 \quad \text{s.t.}\quad \|w - w_{t-1}\|_1 \le \tau_{\max}.
$$

This is a convex projection (SOCP / QP), directly controlling daily fraction rebalanced.

### 2. KG-MoE: Knowledge-Graph Mixture-of-Experts Allocator

**State representation**

- Nodes $V$: ETFs, sectors, macro factors, policy themes.
- Edges $E_t$: structural edges (ETF–sector, sector–macro factor) + **time‑varying event edges** (policy $p$ → sector $s$ with sign/strength derived from LLM).
- Node features $X_t(v)$: price-factor summary, sector metrics, event-type indicators.

GNN layer (e.g., GraphSAGE / GAT):

$$
h_t^{(l+1)}(v) = \sigma\left(
W_1 h_t^{(l)}(v) + \sum_{u \in \mathcal{N}(v)} \alpha_{uv}^{(l)} W_2 h_t^{(l)}(u)
\right),
$$

with attention coefficients $\alpha_{uv}^{(l)}$ depending on edge type and LLM-derived sign.

Final node embeddings $h_t(v)$. Collect ETF embeddings into matrix $H_t^{\text{ETF}}$.

**Mixture-of-experts routing**

We define **expert allocators** $f_m$, $m=1,\dots,M$ (e.g., BL, risk parity, trend, defensive):

$$
w_t^{(m)} = f_m(\text{quant features at } t).
$$

Router logits:

$$
u_m = g\left( \text{pool}(H_t^{\text{ETF}}) \right),
$$

where $\text{pool}$ is e.g. mean or attention pooling; $g$ is an MLP.
Mixture weights:

$$
\lambda_m = \frac{\exp(u_m)}{\sum_j \exp(u_j)}.
$$

Final **pre‑risk** weights:

$$
\tilde{w}_t = \sum_m \lambda_m w_t^{(m)}.
$$

**Risk \& turnover controls**

Same projection as BSA-RP:

$$
w_t = \Pi_{\mathcal{W}, \tau_{\max}}(\tilde{w}_t; w_{t-1}),
$$

where $\Pi$ denotes projection with volatility, concentration, and turnover constraints.

### 3. DRO-BL: Distributionally Robust Black-Litterman Agent

**State representation**

- Equilibrium prior implied returns $\pi_t$ (e.g., CAPM/market‑cap implied).[^12]
- Covariance $\Sigma_t$ estimated from rolling window.
- Views: matrices $P_t$ (each row a view portfolio), $Q_t$ (view expected returns), and diagonal uncertainty $\Omega_t$.

Standard BL posterior mean:

$$
\mu_t^{\text{BL}} = \left[(\tau \Sigma_t)^{-1} + P_t^\top \Omega_t^{-1} P_t \right]^{-1}
\left[ (\tau \Sigma_t)^{-1} \pi_t + P_t^\top \Omega_t^{-1} Q_t \right].
$$

LLM provides **structured** $P_t, Q_t, \Omega_t$ given daily news — e.g., “New energy policy support strong” → a view $P_t$ that is long new‑energy ETF vs market with $Q_t>0$, moderate confidence (larger $\Omega_t$).[^5][^12]

**Distributionally robust objective**

Define Wasserstein ambiguity set $\mathcal{P}_\delta$ around empirical distribution $\hat{\mathbb{P}}$ of returns.[^3]

Robust mean–variance objective:

$$
\max_{w \in \mathcal{W}} \left\{
\inf_{P \in \mathcal{P}_\delta} \mathbb{E}_P[R]^\top w - \frac{\gamma}{2} w^\top \text{Cov}_P(R) w
\right\}
- \eta \|w - w_{t-1}\|_1.
$$

Standard results give a tractable reformulation as QP with additional penalty terms in mean and variance for small Wasserstein balls.[^3]

Approximation: adjust $\mu_t^{\text{BL}}$ and $\Sigma_t$ to **worst‑case shrunk** values $\tilde{\mu}_t, \tilde{\Sigma}_t$, then solve:

$$
\max_{w \in \mathcal{W}} \left\{ \tilde{\mu}_t^\top w - \frac{\gamma}{2} w^\top \tilde{\Sigma}_t w - \eta \|w - w_{t-1}\|_1 \right\}.
$$

Risk and turnover constraints as before.

### 4. TEMA: Transformer Event Memory Allocator

**State representation**

At each day $t$:

- Price/time-series feature vector $p_t$ (e.g., returns, vol, momentum, trend filters).
- Event embedding $e_t$ from a **frozen** encoder trained offline (could be a small FinBERT‑like model or a simpler sentence‑BERT on Chinese financial text).[^24][^4]

Combine: $x_t = [p_t; e_t]$.

We feed a window $(x_{t-L+1}, \dots, x_t)$ into a transformer encoder:

Multi‑head self‑attention:

$$
\text{Attention}(Q,K,V) = \text{softmax}\left( \frac{QK^\top}{\sqrt{d}} + M_{\text{mask}} \right) V,
$$

with learnable positional encodings that incorporate **time decay** (e.g., exponential or learned SSM filter).[^7][^9]

Let final hidden corresponding to last token be $h_t$.

**Score-to-weight head**

We map $h_t$ to a *return score* $s_t \in \mathbb{R}^n$:

$$
s_t = W_s h_t + b_s.
$$

Convert to **pre‑risk weights** via softmax with temperature and risk scaling:

$$
\tilde{w}_{t,i} = \frac{\exp(s_{t,i} / \tau)}{\sum_j \exp(s_{t,j} / \tau)}.
$$

Then adjust for volatility:

$$
\hat{w}_{t,i} \propto \frac{\tilde{w}_{t,i}}{\hat{\sigma}_{t,i}},
$$

with $\hat{\sigma}_{t,i}$ estimated rolling vol; then renormalize to sum to 1.

**Risk and turnover control**

Same projection to $\mathcal{W}$ with turnover bound $\tau_{\max}$. Training includes explicit penalty terms:

$$
\mathcal{L} = -\text{Sharpe}_{\text{train}} + \lambda_{\text{DD}} \text{MaxDD} + \lambda_{\text{TO}} \text{Turnover}.
$$

Training only on **2024**, with calibration checks on 2025.

### 5. RAL-Rank: Retrieval-Augmented Learning-to-Rank Meta Allocator

**State representation**

Let $\phi_t$ be a **joint embedding** of (Buzz, prices, macro factors) at day $t$, built by concatenating news and price embeddings and passing through an MLP.[^25][^4]

For current day $t$, retrieve **k nearest neighbors** in 2024 training set:

$$
\mathcal{N}_t = \{ j : j < t,\ \text{kNN in } \|\phi_t - \phi_j\|_2 \}.
$$

For each base strategy $b \in \mathcal{B}$ (e.g., EW, inv‑vol, momentum, MVO, BL, etc.), compute **analogue performance features** from $\mathcal{N}_t$, such as:

- Mean next‑day (or next‑few‑days) return $\bar{r}_{b,t}$.
- Volatility $\sigma_{b,t}$.
- Hit rate (fraction of positive returns).

Gather into feature vector $f_{b,t}$.

**Learning-to-rank**

Train a ranker $F_\theta$ (e.g., pairwise or listwise LTR model) that outputs scores:

$$
\text{score}_{b,t} = F_\theta(f_{b,t}).
$$

Convert scores over base strategies into mixture weights:

$$
\alpha_{b,t} = \frac{\exp(\text{score}_{b,t})}{\sum_{b'} \exp(\text{score}_{b',t})}.
$$

Final pre‑risk weights:

$$
\tilde{w}_t = \sum_{b \in \mathcal{B}} \alpha_{b,t} w_t^{(b)}.
$$

**Risk and turnover**

As before: projection to $\mathcal{W}$ with volatility and turnover caps.

### 6. OCO-Bandit: Online Convex / Bandit Allocator

**State representation**

Weights $w_t \in \Delta^n$ (simplex), losses $\ell_t(w) = -R_t^\top w + c \cdot \text{turnover}_t$. Context features $c_t$ from news (e.g., K‑dim factor vector with bounded norm).

**Online mirror descent / FTRL**

Use entropic mirror descent:

$$
w_{t+1,i} \propto w_{t,i} \exp(-\eta_t g_{t,i}),
$$

where $g_t = \nabla_w \ell_t(w_t) = -R_t + c\,\text{sgn}(w_t - w_{t-1})$.

We may modulate learning rate $\eta_t$ by a function of context $c_t$ (e.g., higher in “high signal” regimes, lower in noisy regimes) but keep this mapping **fixed after training** on 2024.[^3]

Bandit variant: COMID‑like algorithm that respects non‑stochastic adversary but we interpret returns as adversarial.

**Risk control**

Include soft penalty in loss:

$$
\ell_t(w) = -R_t^\top w + \lambda_{\text{vol}} w^\top \hat{\Sigma}_t w + \lambda_{\text{DD}} \text{DD}_t(w),
$$

and project onto caps $w_{t,i} \le c_{\max}$ each step.

Turnover is **implicitly controlled** by small $\eta_t$ and explicit turnover term.

### 7. CEIG: Causal Event-Impact Graph Allocator

**State representation**

We posit a structural model:

$$
F_t = g(E_t, U_F), \quad
R_t = B F_t + \epsilon_t,
$$

where:

- $E_t$ are event variables (policy types, macro shocks), with values built from **LLM-tagged categories** (e.g., “monetary easing”, “property support”, “tech crackdown”).
- $F_t$ are latent factors (e.g., growth, inflation, policy, ESG),
- $B$ is factor loading matrix mapping factors to asset returns $R_t$.

We assume multiple environments $e \in \mathcal{E}$ (e.g., 2024‑Q1, 2024‑Q2, 2024‑Q3‑4, 2025‑H1), each with different distribution of $E_t$ but **invariant causal parameters** $g, B$.[^15][^8]

**IRM-style objective**

We learn a representation $\phi(E_t)$ and parameters $\theta$ such that the optimal predictor $\hat{R}_t = f_\theta(\phi(E_t))$ is consistent across environments:

$$
\min_{\phi, \theta} \sum_{e \in \mathcal{E}} \mathcal{R}^e(f_\theta \circ \phi)
\quad \text{s.t.} \quad
\nabla_\theta \mathcal{R}^e(f_\theta \circ \phi) = 0,\ \forall e.
$$[^8][^15]

Here $\mathcal{R}^e$ is prediction loss (e.g., squared error or directional loss of sector returns). This (approximate) IRM encourages **invariant causal features**.

Once we have $\phi(E_t)$ and mapping to expected returns $\hat{\mu}_t$, we combine with historical covariance $\hat{\Sigma}_t$ and solve a robust optimization similar to DRO-BL but with **prior mean zero** (neutral) and text-driven causal shifts.

**Counterfactual stress**

We can compute counterfactual factors $F_t^{\text{cf}}$ by intervening on $E_t$ (e.g., removing a policy shock) and evaluating $\Delta R_t = B(F_t - F_t^{\text{cf}})$. Use $\Delta R_t$ to adjust risk budgets (e.g., down‑weight sectors that are over‑dependent on a single fragile policy channel).

**Score-to-weight rule**

Construct:

$$
\tilde{\mu}_t = \hat{\mu}_t - \lambda_{\text{frag}} |\Delta R_t|,
$$

penalizing sectors whose returns rely heavily on a *single* policy channel.

Optimize:

$$
\max_{w \in \mathcal{W}} \left\{ \tilde{\mu}_t^\top w - \frac{\gamma}{2} w^\top \hat{\Sigma}_t w \right\}
- \eta \|w - w_{t-1}\|_1.
$$

Risk and turnover controls as above.

F. Quantitative Comparison Table
--------------------------------

The following scores are **expert priors**, not empirical results. They assume careful implementation and tuning. Scores: 0–10, higher better, except risk metrics at bottom (Overfit/Tool/Data risk: higher is worse).

I then compute the **Overall Research-Competition ROI** using the formula you gave, and two sub-scores: **Competition Score** and **Research/Award Score** (explained underneath).

### Score definitions

- Competition Score =
$0.30 \cdot \text{SharpePotential} + 0.20 \cdot \text{DrawdownControl} + 0.15 \cdot \text{TurnoverEfficiency} + 0.20 \cdot \text{BListRobustness} + 0.15 \cdot \text{BaselineBeatingProb}$.
- Research/Award Score =
$0.25 \cdot \text{Novelty} + 0.25 \cdot \text{MathematicalDepth} + 0.20 \cdot \text{Interpretability} + 0.15 \cdot \text{Reproducibility} + 0.15 \cdot \text{ReportSignal}$.


### Table

| Design | Track1 Fit | Track2 Fit | Sharpe Pot. | Drawdown Ctrl | Turnover Eff. | B‑list Robust | Novelty | Math Depth | Interp. | Reprod. | Feasibility | Baseline Beat Prob. | Report Signal | Overfit Risk | Tool Dep. Risk | Data Compliance Risk | ROI (approx) | Competition Score | Research Score |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| **BSA-RP** | 9 | 7 | 8 | 8 | 7 | 8 | 7 | 8 | 7 | 8 | 7 | 8 | 8 | 6 | 3 | 2 | **8.2** | **7.9** | 8.1 |
| **KG-MoE** | 8 | 9 | 8 | 7 | 7 | 7 | 9 | 8 | 7 | 6 | 6 | 8 | 9 | 7 | 5 | 3 | **8.1** | **7.6** | 8.5 |
| **DRO-BL** | 9 | 8 | 8 | 9 | 7 | 9 | 7 | 9 | 7 | 8 | 7 | 8 | 8 | 5 | 3 | 2 | **8.6** | **8.3** | 8.3 |
| **TEMA** | 8 | 8 | 8 | 7 | 6 | 7 | 8 | 8 | 6 | 7 | 7 | 7 | 8 | 7 | 2 | 2 | **8.0** | **7.5** | 7.9 |
| **RAL-Rank** | 7 | 9 | 7 | 7 | 8 | 8 | 8 | 7 | 7 | 7 | 8 | 7 | 8 | 6 | 3 | 3 | **7.9** | **7.5** | 8.1 |
| **OCO-Bandit** | 8 | 7 | 7 | 8 | 9 | 8 | 7 | 7 | 7 | 9 | 9 | 7 | 7 | 5 | 2 | 2 | **8.3** | **8.1** | 7.6 |
| **CEIG** | 7 | 8 | 7 | 8 | 6 | 9 | 9 | 9 | 8 | 6 | 6 | 6 | 10 | 7 | 4 | 3 | **8.2** | **7.7** | 8.9 |

Notes on relative scores:

- **Sharpe Potential:** DRO-BL and BSA-RP slightly ahead due to robust risk modeling; TEMA also strong but more overfit risk.
- **Drawdown Control:** DRO-BL best; OCO-Bandit, CEIG strong; KG-MoE slightly less disciplined.
- **Turnover Efficiency:** OCO-Bandit best; RAL-Rank likely good (meta‑rotation); TEMA riskier.
- **B-list Robustness:** DRO-BL and CEIG highest (DRO + causal invariance), BSA-RP and RAL-Rank also strong.
- **Novelty \& Math Depth:** CEIG and KG-MoE top for novelty; DRO-BL and CEIG top for math depth.
- **Interpretability:** CEIG, BSA-RP, DRO-BL, RAL-Rank strong; TEMA weaker but still explainable via attention maps.
- **Reproducibility \& Feasibility:** OCO-Bandit, BSA-RP, RAL-Rank relatively easy for one student; CEIG and KG-MoE moderate to hard.
- **Overfit Risk:** Higher for KG-MoE, TEMA, CEIG; lower for DRO-BL and OCO-Bandit.
- **Tool Dependency Risk:** All designs are implementable with local models; worst for KG-MoE (if heavy LLM pre‑processing) and CEIG; best for TEMA/OCO-Bandit which can run entirely offline.
- **Data Compliance Risk:** All low if we constrain to pre‑2026 public data; causal/graph designs risk misusing external knowledge if not careful.

On this scoring, **DRO-BL** edges out as strongest overall ROI, followed closely by **OCO-Bandit, CEIG, BSA-RP, KG-MoE**.

G. Competition Score vs Research/Award Score
-------------------------------------------

Using the computed sub-scores:

- **High Competition + High Research**
    - **DRO-BL**: Competition ≈ 8.3, Research ≈ 8.3. Strong on Sharpe, drawdown, robustness, and has deep BL+DRO math and LLM-structured views.
    - **BSA-RP**: Comp ≈ 7.9, Research ≈ 8.1. Slightly less “fancy” than CEIG, but belief-state + risk parity is a very publishable pattern.
    - **KG-MoE**: Comp ≈ 7.6, Research ≈ 8.5. Very strong narrative (KG+GNN+MoE), solid but not maximal competition score.
- **High Competition + Lower Research (but still OK)**
    - **OCO-Bandit**: Comp ≈ 8.1, Research ≈ 7.6. Algorithmically strong and robust, but somewhat less “novel” to reviewers than CEIG/KG-MoE.
    - **TEMA**: Comp ≈ 7.5, Research ≈ 7.9. Good transformer variant but many transformer‑in‑finance papers already exist.[^16][^9][^7]
- **Lower Competition + High Research**
    - **CEIG**: Comp ≈ 7.7, Research ≈ 8.9. Potentially harder to tune to top Sharpe, but extremely rich for causal/OOD/invariance narrative, ideal for system paper.
    - **RAL-Rank**: Comp ≈ 7.5, Research ≈ 8.1. Strong story about analogue retrieval and meta-allocation; competition performance will depend heavily on base strategy diversity.
- **Low Competition + Low Research**
    - None of the 7 blueprints fall here; rejected designs (Pure CPA LLM agent, IR‑PRP, SSM PriceOnly) would sit closer to this quadrant from a novelty standpoint, which is why they’re relegated to baselines/ablations.

**Conclusion for awards:** Even if Sharpe is not top, **CEIG, KG-MoE, and DRO-BL** are the most likely to yield award‑worthy reports due to:

- explicit causal/graphical structure and sector‑policy knowledge grounding (CEIG, KG-MoE).[^4][^13][^8][^5]
- mathematically clean integration of LLM views and robust portfolio theory (DRO-BL).[^12][^3]

H. Baseline-Beating and Ablation Plan
-------------------------------------

### Baselines to implement (per Track)

1. **Equal Weight (EW):** fixed $w_i = 1/n$.
2. **Inverse Volatility:** $w_i \propto 1/\hat{\sigma}_{i,t}$, normalized.
3. **Momentum-only:** rank assets by past $N$-day return; allocate EW to top $k$ or proportionally to rank.
4. **Sector Trend-Following:** trend filters (e.g., moving average crossovers) at sector level; overweight sectors with positive trend, underweight or zero others.[^17][^6]
5. **Persistence / Low-Turnover Baseline:** e.g., once-a-week rebalancing of inverse-vol or momentum; daily decisions default to “hold unless signal crosses threshold”.
6. **Rule-Based Macro Rotation:** discrete mapping from macro indicators (bond yields, equity index trend, FX proxies) into 4–5 canonical macro regimes and associated static allocations.
7. **News sentiment only:** event-level sentiment aggregation (e.g., FinBERT-style) mapped linearly into sector tilts.[^24][^4]
8. **S1 Quant Core (from CN-Buzz2Portfolio):**
    - Track 1: inverse-vol / momentum / breadth / defensive allocator.[^1]
    - Track 2: trend-following top‑k sector allocator.[^1]

Each proposed design must **beat or at least match S1** on:

- **2024 walk-forward Sharpe** after 0.01% cost.[^1]
- **Turnover-adjusted Sharpe**: we can compute Sharpe penalized by trading cost or by an explicit turnover penalty term.
- **Stability across 2024 subwindows** (e.g., Q1 vs Q2 vs Q3+Q4): no collapse in one subperiod.


### Ablations per design

For each blueprint, we define consistent ablations:

- **No LLM:** Replace LLM-generated inputs with simple rules: sentiment scores from a small classifier, or dummy neutral views. Tests the incremental value of LLM modules.
- **No news:** Use price/history only; compare to “Top‑0” behaviour documented in CN‑Buzz2Portfolio.[^1]
- **No memory / no belief-state:** For BSA-RP and TEMA, reduce to Markovian or myopic allocator ignoring latent state or long-range attention.
- **No risk control:** Allow unconstrained mean–variance optimization; observe drawdown blow‑ups.
- **No turnover control:** Remove turnover penalty / projection; observe cost‑adjusted Sharpe deterioration under 0.01% fee.
- **No graph / retrieval / regime module:**
    - KG-MoE → single expert or no GNN edges.
    - RAL-Rank → no retrieval; ranker only uses global averages.
    - BSA-RP → no regime filter; just risk parity + news‑tilted means.
- **Quant-only:** Use the sub‑engine (HMM, BL, OCO, transformer) with prices only.
- **LLM-only (CPA baseline):** Tri‑Stage LLM agent making full allocation decisions (as in CN‑Buzz2Portfolio) but wrapped in hard caps; use as a comparison to highlight structured approaches.[^1]
- **2024‑tuned vs 2025‑tuned:**
    - Primary models trained/calibrated on 2024 only.
    - Secondary experiments allow tuning on 2024+early‑2025 to show overfit risk; B‑list uses the 2024‑only version.

Each design must justify implementation by showing, at minimum:

- **Statistically significant improvement** over EW + inverse‑vol + S1 quant core in 2024 (and ideally not worse in 2025).
- **No catastrophic turnover‑induced Sharpe drop** (within a small tolerance vs S1).
- Clear ablation story: LLM/graph/causal modules add measurable value beyond quant core.

I. Hidden B-List Robustness Audit
---------------------------------

Key 2026 hidden-period risks and how each design addresses them:

1. **Regime shift (e.g., new policy styles, emergent sectors):**
    - **BSA-RP:** regime model can be expanded (with priors) and will shift posterior $p_t(z)$ when observed returns and event likelihoods disagree; robust if priors are broad.
    - **KG-MoE:** adding new policy nodes/sectors to the graph is possible, but extrapolating GNN parameters to unseen nodes is risky; need regularization + fallback to base experts when embeddings are too far from training manifold.
    - **DRO-BL:** DRO ambiguity set explicitly protects against shifts in return distribution; BL views soften when LLM confidence is low.
    - **TEMA:** highest overfit risk if trained only on 2024; must rely on strong regularization and compression to avoid memorizing patterns specific to 2024/early‑2025.
    - **RAL-Rank:** retrieval naturally searches for close analogues; if 2026 is novel, distances will be high, and the ranker can be designed to fall back to S1 when analogue quality is low.
    - **OCO-Bandit:** regret guarantees give some robustness; it will slowly adapt to new regimes, but early performance may lag.
    - **CEIG:** IRM/ICRL learns invariant relationships, so if causal structure is stable but distributions shift, CEIG should be robust; if causal structure changes, performance may degrade.
2. **Prompt instability / LLM behaviour changes:**
    - All designs must **avoid any online API** in B‑list; use frozen local models and deterministic pipelines.
    - Prompt sensitivity mainly affects **training‑time extraction** of events; mitigate via schema‑based extraction with rule‑based validators (e.g., check that view signs \& magnitudes are within sane bounds).
3. **Dependency risk (tools, APIs, external knowledge):**
    - Prefer small, local Chinese financial models (FinBERT‑style) trained on pre‑2026 corpora or static embeddings, not remote APIs.
    - TEMA, OCO-Bandit, and quant cores can be built with **no LLM at runtime**.
4. **Macro event novelty and sector label drift:**
    - CEIG and KG-MoE explicitly encode **policy-to-sector channels**; updating the KG with new nodes/edges is feasible but must be done *prior to B‑list* and only using historical data.
    - For new sector ETFs, treat them as combinations of existing sectors via holdings, mapping to graph as linear combination or new nodes with inherited edges.
5. **Data compliance \& leakage:**
    - Strictly limit text sources to the **Top‑20 Buzz list provided**; no ingestion of later news, social media, or 2026‑only corpora.
    - All offline pretraining done with data **published no later than 2025‑12‑31**; document data sources explicitly.
    - Verify that no fields from day $t$’s close/high/low/return are used in the decision for day $t$ — decisions must use up to $t-1$ prices and pre‑close news for $t$.[^1]

Overall, **DRO-BL, BSA-RP, OCO-Bandit, and CEIG** provide the best B‑list robustness stories. KG-MoE and TEMA need more careful regularization and strong fallback baselines.

J. Implementation Roadmap
-------------------------

Assuming one strong MSc‑level student with some quant and ML background.

**Phase 0R: Source/Data Reset (1–2 days)**

- Clone official repo (once accessible), verify SHA, inspect `backtest.py`, `data_loader.py`, `dataloader_eval.py`.
- Verify that our reading of task constraints from CN‑Buzz2Portfolio aligns with their implementation.[^1]
- Build a minimal local backtest harness replicating their evaluation metrics.

**Phase 1R: Official Starter Reproduction (3–5 days)**

- Run the official Tri‑Stage CPA baseline agents on 2024 and 2025; reproduce reported numbers within tolerance.[^1]
- Implement S0 baselines (EW, inverse‑vol, pure momentum, simple sector trend-following) inside their backtester.

**Phase 2R: Baselines \& Quant Core (5–8 days)**

- Implement S1 quant core for both tracks: inverse‑vol/momentum/breadth/defensive macro, and sector trend-following top‑k.
- Implement SSM PriceOnly transformer baseline (no news).
- Implement OCO-Bandit without news context as a strong quant online baseline (this is also a piece of the final design).

**Phase 3R: First Innovative Prototype (10–14 days)**

- Start with **DRO-BL** (performance-first) and **BSA-RP** (belief-state) as they have high ROI and clear math.
    - Build view-extraction pipeline: templated extraction from Buzz into per-ETF and per-sector views (sign, magnitude, confidence).
    - Implement BL posterior + QP allocator; then extend to simple DRO adjustment.
    - Implement HMM/Belief filter and risk-parity allocator for BSA-RP.
- Evaluate on 2024 walk-forward with ablations:
    - BL prior only vs BL + news views vs BL + DRO.
    - Risk-parity only vs belief‑state BSA-RP.

**Phase 4R: Full Comparison (15–20 days)**

- Implement **KG-MoE** with a minimal KG (ETF–sector–policy themes) and one or two experts (e.g., BL, risk parity).
- Implement **TEMA** (small transformer), starting with price+simple sentiment features; then add richer event embeddings if time permits.
- Implement **RAL-Rank** with small base strategy set and simple analogue retrieval.
- Implement **CEIG** in a simplified form: start with 2–3 event types and 2–3 latent factors; use IRM‑style constraints across 3–4 environments.
- For each design, run full 2024 and 2025 evaluation (without 2025 in training).
- Log all ablations systematically.

**Phase 5R: A-list Package (5–7 days)**

- Select **2–3 top-performing designs** (likely DRO-BL, BSA-RP, and one of KG-MoE / OCO-Bandit / RAL-Rank) for A‑list submission.
- Harden code: remove randomness where unnecessary, seed PRNGs, ensure deterministic CPU operations.
- Add configuration flags to run ablations quickly through the same harness.
- Produce initial system report draft focusing on design philosophy, math, and ablation results.

**Phase 6R: B-list Hardening (7–10 days)**

- Stress-test on alternative 2024 slices (rolling subwindows) and synthetic noise injections (e.g., randomly shuffled news days).
- Implement strict **fallback layers**: e.g., if view confidence low or analogue distance high, shrink weights toward S1 core.
- Optimize performance: remove heavy LLM components from runtime; precompute all event embeddings, graphs, and features.
- Finalize B‑list submission Docker/image and run dry‑runs with the official evaluation harness.

K. Final Recommendation
-----------------------

1. **Best performance-first design:**
    - **DRO-BL**
        - Strong Sharpe and drawdown potential on both tracks due to BL + robust optimization.
        - Naturally handles news in the form of structured views; supports risk parity / MVO hybrids.
        - Relatively implementable, with mature convex optimization libraries.
2. **Best research/award design:**
    - **CEIG (Causal Event-Impact Graph)**, closely followed by **KG-MoE**
        - CEIG: causal/IRM framing, counterfactual stress tests, invariant reasoning across 2024/2025 — very attractive to reviewers.
        - KG-MoE: ETF–sector–policy KG + GNN + MoE experts embodies the competition’s emphasis on knowledge‑grounded, policy‑sensitive sector rotation.
3. **Best one-student design (balance of impact and feasibility):**
    - **BSA-RP** plus an **OCO-Bandit** baseline
        - BSA-RP: HMM + risk parity is classical and well-documented; LLM role limited to view likelihoods.
        - OCO-Bandit: minimal moving parts, strong quant story, easy to debug and ablate.
4. **Best Track 1 (Macro) design:**
    - **DRO-BL**, with **BSA-RP** as co-winner
        - BL’s equilibrium prior fits macro ETFs very naturally; belief-state BSA-RP captures macro regimes explicitly.
5. **Best Track 2 (Sector) design:**
    - **KG-MoE**, with **RAL-Rank** as complementary
        - KG-MoE uses ETF–sector–policy graph structure to map event types to sector tilts.
        - RAL-Rank meta-selects among trend/BL/defensive sector strategies in a way well-suited to sector rotation.
6. **Designs to reject as primary focus:**
    - **Pure CPA LLM agent with risk wrapper**: too close to CN‑Buzz2Portfolio baseline; high tool-dependency risk and weaker novelty.[^1]
    - **SSM PriceOnly universal portfolio** as a main contribution: valuable quant baseline but lacks news/LLM integration and knowledge-grounding.
    - **IR-PRP** (invariant risk parity) beyond what CEIG already covers: complexity cost without clear incremental narrative.
7. **Exact first implementation target:**

Given limited time and desire for both strong Sharpe and publishable structure, I recommend:
    - **Primary Track 1 \& Track 2 engine:** **DRO-BL** (with per-track calibration).
    - **Secondary complementary design for Track 2:** **KG-MoE** (with small, curated KG) if time allows; otherwise **BSA-RP**.

Minimum viable package:
    - Implement **DRO-BL** with robust BL + turnover constraints and the full ablation suite.
    - Implement **BSA-RP** as alternative engine and as a “belief‑state vs static prior” comparison.
8. **Fallback if novelty underperforms in backtests:**
    - If DRO-BL + BSA-RP do **not** beat S1 in 2024 after careful tuning:
        - Use **OCO-Bandit** as the **core competition entry**: it is highly robust and easy to tune for turnover and drawdown.
        - Reposition CEIG and KG-MoE as **research/analysis modules** feeding diagnostics (e.g., causal importance scores, policy‑impact graphs) while the trade engine remains OCO‑Bandit or BL‑lite.
    - Even in this fallback, you can write a strong system report centered on:
        - empirical demonstration of **Top‑0 paradox** and regime‑dependent news value on your own architectures,[^1]
        - how causal/graph modules explained failures and guided robust quant design,
        - how invariant/robust methods (DRO-BL, CEIG) improved B‑list robustness even if Sharpe gains were modest.

Overall, I would start implementation with **DRO-BL + BSA-RP + OCO-Bandit**, then layer in **KG-MoE** for Track 2 and **CEIG** for the system-report narrative as time permits. This combination gives you a credible shot at **competitive backtest performance**, a **rigorous mathematical core**, and **distinctive graph/causal contributions** that stand out in the shared task.
<span style="display:none">[^100][^101][^102][^103][^104][^105][^106][^107][^108][^109][^110][^111][^112][^113][^114][^115][^116][^26][^27][^28][^29][^30][^31][^32][^33][^34][^35][^36][^37][^38][^39][^40][^41][^42][^43][^44][^45][^46][^47][^48][^49][^50][^51][^52][^53][^54][^55][^56][^57][^58][^59][^60][^61][^62][^63][^64][^65][^66][^67][^68][^69][^70][^71][^72][^73][^74][^75][^76][^77][^78][^79][^80][^81][^82][^83][^84][^85][^86][^87][^88][^89][^90][^91][^92][^93][^94][^95][^96][^97][^98][^99]</span>

<div align="center">⁂</div>

[^1]: https://arxiv.org/pdf/2603.22305.pdf

[^2]: https://arxiv.org/abs/2408.06361

[^3]: https://pmc.ncbi.nlm.nih.gov/articles/PMC7956065/

[^4]: https://www.sciencedirect.com/science/article/abs/pii/S0950705122004397

[^5]: https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5111794

[^6]: https://arxiv.org/abs/2108.02838

[^7]: https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID4375798_code2346809.pdf?abstractid=4375798\&mirid=1

[^8]: https://arxiv.org/abs/1907.02893

[^9]: https://arxiv.org/html/2310.01232v2

[^10]: https://arxiv.org/html/2605.19337v1

[^11]: https://arxiv.org/abs/2412.20138

[^12]: https://www.fe.training/free-resources/portfolio-management/black-litterman-model/

[^13]: https://bayesgroup.github.io/bmml_sem/2019/Kodryan_Invariant%20Risk%20Minimization.pdf

[^14]: https://www.inference.vc/invariant-risk-minimization/

[^15]: https://www.semanticscholar.org/paper/Nonlinear-Invariant-Risk-Minimization:-A-Causal-Lu-Wu/0af062522c790b068014365ae144b329d5f2386a

[^16]: https://arxiv.org/abs/2304.04912

[^17]: https://www.summarizepaper.com/en/arxiv-id/2108.02838v1/

[^18]: https://arxiv.org/html/2510.05533v1

[^19]: https://www.marketcalls.in/python/introduction-to-hidden-markov-models-hmm-for-traders-python-tutorial.html

[^20]: https://github.com/ddz16/TSFpaper

[^21]: https://www.sciencedirect.com/science/article/abs/pii/S0957417425024625

[^22]: https://medium.com/@pta.forwork/event-driven-trading-building-algorithms-that-react-to-news-and-earnings-ea428e3cb850

[^23]: https://www.scribd.com/document/885247602/ssrn-3683454

[^24]: https://pmc.ncbi.nlm.nih.gov/articles/PMC10280559/

[^25]: https://backoffice.biblio.ugent.be/download/01GX3SPY4VR556GGAK87NXPYA3/01GYF7C8T38NYN5V16R4RYDA25

[^26]: https://github.com/NLP2CT/NLPCC-2026-Task10-Science

[^27]: https://arxiv.org/abs/2603.22305v1

[^28]: https://blog.csdn.net/weixin_39597399/article/details/116854872

[^29]: https://github.com/mind-network/Awesome-LLM-based-AI-Agents-Knowledge/blob/main/4-concept.md

[^30]: https://openreview.net/group?id=ccf.org%2FNLPCC%2F2026%2FShared_Tasks

[^31]: https://juejin.cn/post/6844903487612911624

[^32]: https://yjump.github.io

[^33]: https://nlp2ct.github.io/NLPCC-2026-Task6-Detection/

[^34]: https://github.com/FudanNLP/nlpcc2017_news_headline_categorization

[^35]: https://github.com/splash-li/NLPCC2026-Shared-Task-4/

[^36]: http://tcci.ccf.org.cn/conference/2024/taskdata.php

[^37]: https://huggingface.co/datasets/qgyd2021/chinese_ner_sft/blob/main/chinese_ner_sft.py

[^38]: http://tcci.ccf.org.cn/conference/2026/shared-tasks/

[^39]: https://arxiv.org/html/2603.22305v1

[^40]: https://huggingface.co/datasets/qgyd2021/chinese_ner_sft/commit/30c44b9483cca14a6f3625763c9c2eb35c9ebd96

[^41]: https://pmc.ncbi.nlm.nih.gov/articles/PMC12421730/

[^42]: https://arxiv.org/html/2508.07408v1

[^43]: https://arxiv.org/html/2503.00900v1

[^44]: https://pub.towardsai.net/knowledge-graphs-and-their-applications-to-investing-in-ai-af7cb8222103

[^45]: https://www.aimsciences.org/article/doi/10.3934/mfc.2023043

[^46]: https://www.semanticscholar.org/paper/Open-Problem:-Fast-and-Optimal-Online-Portfolio-Erven-Hoeven/c9f3516c2a9c615c37f48a5f556345c339c7295e

[^47]: https://arxiv.org/abs/2505.12506

[^48]: https://rpc.cfainstitute.org/research/the-automation-ahead-content-series/retrieval-augmented-generation

[^49]: https://andrew-hyde.medium.com/the-ensemble-of-hidden-markov-bayesian-models-for-regime-switching-in-equity-markets-a2a7dc109a39

[^50]: https://arxiv.org/html/2408.06361v2

[^51]: https://arxiv.org/html/2603.09085v1

[^52]: https://jonathankinlay.com/2026/03/state-space-models-for-market-microstructure-can-mamba-replace-transformers-in-high-frequency-finance/

[^53]: https://arxiv.org/pdf/2212.09624.pdf

[^54]: http://www.columbia.edu/~xz2574/download/BCZ-final.pdf

[^55]: https://ink.library.smu.edu.sg/context/sis_research/article/3263/viewcontent/Online_Portfolio_Selection__A_Survey_afv.pdf

[^56]: https://github.com/nanduan/NLPCC-KBQA

[^57]: https://ncce-site.pages.dev/results

[^58]: https://kernc.github.io/backtesting.py/doc/backtesting/backtesting.html

[^59]: https://github.com/Sparsh-Kumar/backtesting.py

[^60]: https://github.com/ResearAI/NLPCC-2026-Task9-AISB

[^61]: https://algotrading101.com/learn/backtesting-py-guide/

[^62]: https://huggingface.co/datasets/NbAiLab/NCC/blame/857a5832b73ef33c66b5674d970777c39d991c0e/README.md

[^63]: https://github.com/kernc/backtesting.py

[^64]: https://github.com/palm2333/nlpcc-2024-shared-task-3

[^65]: https://www.mintlify.com/kernc/backtesting.py/guides/optimization

[^66]: https://www.quantconnect.com/forum/discussion/13589/inaccurate-prices-for-open-high-low-close/

[^67]: http://tcci.ccf.org.cn/conference/2018/papers/EV48.pdf

[^68]: https://stackoverflow.com/a/61843921

[^69]: https://in.tradingview.com/script/9c3xAAOV-JL-DWM-OHLC/

[^70]: http://arxiv.org/abs/1706.02883

[^71]: https://docs.openbb.co/python/reference/equity/price/historical

[^72]: https://www.bloomberg.com

[^73]: https://www.tradingview.com/script/siA2nDco-Open-Close-High-Low-AlecVosika/

[^74]: https://wanxiaojun.github.io/NLPCC2017-Overview.pdf

[^75]: https://lumibot.lumiwealth.com/entities.bars.html

[^76]: https://www.wsj.com

[^77]: https://kite.trade/forum/discussion/9485/date-of-ohlc-quote

[^78]: https://lileicc.github.io/pubs/li2018overview.pdf

[^79]: https://blog.51cto.com/u_14940497/10720583

[^80]: https://github.com/AntonioAlgaida/Learn2Race_Challenge

[^81]: https://www.kaggle.com/datasets/sayelabualigah/high-quality-financial-news-dataset-for-nlp-tasks/versions/18

[^82]: https://stratbase.ai/en/blog/transaction-cost-erosion

[^83]: https://github.com/Zdong104/FNSPID_Financial_News_Dataset

[^84]: https://www.linkedin.com/posts/dhanushtummala-its-me_stop-trusting-your-backtests-until-youve-activity-7343872582640701442-XvpV

[^85]: https://www.kaggle.com/datasets/sayelabualigah/high-quality-financial-news-dataset-for-nlp-tasks

[^86]: https://www1.se.cuhk.edu.hk/~hccl/publications/pub/NLPCC_overview_jyzhou.pdf

[^87]: https://github.com/The-Swarm-Corporation/BackTesterAgent

[^88]: https://www.kaggle.com/datasets/notlucasp/financial-news-headlines

[^89]: https://papers.cool/arxiv/2603.22305

[^90]: https://thu-coai.github.io/cotk_docs/dataloader.html

[^91]: https://ajdillhoff.github.io/notes/dataloader/

[^92]: https://github.com/NLP2CT/NLPCC-2026-Task6-Detection/actions

[^93]: https://sw.cs.wwu.edu/~tuora/hutchwiki/dataNotes/dataloader.pdf

[^94]: https://velog.io/@nkw011/nlp-dataset-dataloader

[^95]: https://github.com/NLP2CT/NLPCC-2026-Task6-Detection

[^96]: https://nkw011.github.io/nlp/nlp-Dataset_Dataloader/

[^97]: https://finance.yahoo.com/news/glovista-investments-debuts-china-sector-185414320.html

[^98]: https://papers.ssrn.com/sol3/Delivery.cfm/SSRN_ID3929598_code2703583.pdf?abstractid=3542667\&mirid=1

[^99]: https://www.barchart.com/story/news/31010019/etfs-to-bet-big-on-china-amid-fund-rotation

[^100]: https://www.sciencedirect.com/science/article/abs/pii/S0305048317312604

[^101]: https://247wallst.com/investing/2026/05/07/the-china-rotation-is-real-3-etfs-capturing-19-gains-in-2026/

[^102]: https://www.etftrends.com/investors-rotate-equities-iran-war-fears-ease/

[^103]: https://www.blackrock.com/us/individual/insights

[^104]: https://rkbookreviews.wordpress.com/2011/11/02/robust-portfolio-optimization-management-summary/

[^105]: https://www.parnassus.com/insights/article/news_resistant_stocks

[^106]: https://www.linkedin.com/posts/ayush-jha-75674b197_demystifying-finbert-how-transformer-models-activity-7380357007473782784-ep55

[^107]: https://www.linkedin.com/posts/vettafi_assetmanagement-etfmarketing-assetmanager-activity-7369728543062183940-qwqQ

[^108]: https://www.nature.com/articles/s40494-025-02167-y

[^109]: https://abouttrading.substack.com/p/representation-learning-in-financial

[^110]: https://sites.udel.edu/eportfolios/2011/11/29/should-i-use-a-template-when-creating-a-google-site-for-my-portfolio/

[^111]: https://www.interactivebrokers.com/campus/traders-insight/ibkr-toolbox/using-the-ai-scanner-to-identify-news-driven-investment-opportunities/

[^112]: https://www.linkedin.com/posts/taylor-sparks-4ba98b30_crystext-a-generative-ai-approach-for-text-conditioned-activity-7273036929602863104-cW0x

[^113]: https://medium.com/@deepml1818/python-for-machine-learning-based-sector-rotation-strategies-69d7f97b5e29

[^114]: https://github.com/Dreeseaw/Sector-Rotation-RNN

[^115]: https://openreview.net/forum?id=MTWFfKw3sd

[^116]: https://ideas.repec.org/p/arx/papers/2108.02838.html

