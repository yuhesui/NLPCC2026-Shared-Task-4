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
Prioritise designs likely to produce a strong system report or shared-task paper:

- interpretable belief-state architecture,
- clear ablations,
- novel but reproducible agent design,
- mathematical structure,
- visualisable daily reasoning traces,
- explainable risk control.
Performance still matters, but novelty and insight are weighted more heavily.

A. Official Task Constraints and Research Opportunity
----------------------------------------------------

NLPCC 2026 Task 4 is a two‑track daily rebalancing competition where agents allocate among predefined ETF pools using a Top‑20 financial hot‑news feed and historical OHLCV price data in a leakage‑safe backtesting environment. Officially there are Track 1 (macro‑asset allocation over ~11 index/macro ETFs) and Track 2 (sector‑rotation over ~16 industry ETFs), with public 2024 data for training, public 2025 data for A‑list evaluation, and private 2026‑01‑01–2026‑06‑01 data for B‑list evaluation executed centrally on submitted code. The backtester uses 100,000 CNY initial capital, daily trading at (back‑adjusted) close, ETF‑style fractionable units, and a 0.01% transaction friction per trade, and it updates holdings based on daily pctchange while hiding current‑day close/high/low/change from the agent to avoid future leakage.[^1]

The official DataLoader exposes only past days’ full OHLCV and the current day’s open, and its `get_news` API returns only news from specified sources (Caixin, Sina, Tencent, Tiantian) within a sliding pre‑k‑day trading window truncated at 15:00 on the decision day and filtered by ranking (Top‑N) to define the “Top‑20 hot news” setting. Agents interact via a server API (`/api/backtest/*`) that provides per‑day market data, news, and portfolio status and collects trades in cash‑amount (buy) or percentage‑of‑holding (sell) form, with all decisions and results logged to JSON and resumable via session IDs. Models, external datasets, and knowledge bases must be limited to resources available before 2026, and final ranking is based on Sharpe ratio with turnover‑aware categories, plus cumulative return and drawdown; system reports will cover top‑performing and “creative or especially informative” systems.[^1]

**Inferred implications.** Because current‑day returns are hidden and news is truncated at 15:00, any supervised label that directly uses same‑day close or return for training must treat it as a *future* label and cannot be used inside the agent at decision time; instead, you can train offline on 2024/2025 and then run pure inference on 2025/2026 using only allowed features. The B‑list evaluation running centrally on Dockerized code implies that heavy online fine‑tuning or complex external retrieval systems are possible but must be fully reproducible, dependency‑pinned, and prepared without any post‑2025 data, and the log structure allows very detailed ablation and interpretability analysis if designed into the agent. The explicit recommendation to reuse the official DataLoader for both prices and news means that any “clever” data slicing implemented by the team will be scrutinized for leakage risk and likely disfavoured compared to mathematically novel but *input‑compatible* designs.

**Still‑uncertain points.** The organizers have not fully specified: (i) exact Sharpe and drawdown computation horizons and whether turnover tiers are hard constraints or only for sub‑ranking, (ii) whether B‑list includes ETF additions/delistings beyond the starter pool, and (iii) whether there is any penalty or distinct track category for agents that call external LLM APIs during B‑list execution, as long as those models existed pre‑2026. It is also not yet explicit whether multiple submissions per team are allowed or how macro vs sector tracks are weighted in the final shared‑task paper, but the FAQ suggests code + A‑list logs are mandatory and system reports are selected based on both performance and creativity.[^1]

B. Research Source Ledger
-------------------------

| Source | Type | What it contributes | Reliability | How it affects design |
| :-- | :-- | :-- | :-- | :-- |
| Task 4 GitHub root README | Official repo | Defines task scope, tracks, A/B‑list protocol, data split (2024 train, 2025 A, 2026‑H1 B), resource‑before‑2026 rule, system report expectations. | High | Hard constraints for data usage, evaluation metrics, and paper narrative goals. |
| `NLPCC_tasks/README.md` | Official starter kit | Details ETF pools, backtest rules, APIs, evaluation emphasis on Sharpe and turnover tiers, and expected submission artifacts. | High | Fixes ETF universe, motivates turnover control and standardized logs; defines what must be reproducible. |
| `dataset/README.md` | Official dataset doc | Specifies OHLCV fields, adjusted vs raw prices, news sources, ranking‑based Top‑N selection, and reasoning behind the leakage‑safe DataLoader. | High | Governs how we construct features from OHLCV and news; anchors leakage constraints and Top‑20 news definition. |
| `server_platform/app/core/data_loader.py` | Official code | Concrete anti‑leakage implementation: only historical full prices + current open; news truncated at 15:00; pre‑k‑day windows and ranking filters. | High | Guarantees what the agent actually sees in B‑list; informs state definitions and how to align event half‑life with data. |
| `server_platform/app/core/backtest.py` | Official code | Defines portfolio representation (monetary values), trade execution (buy by cash, sell by percentage), 0.01% friction, daily pctchange update, JSON result schema. | High | Constrains portfolio update equations and risk/turnover metrics; suggests logging hooks and ablation possibilities. |
| `dataset/dataloader_eval.py` | Official local DataLoader | Replicates leakage‑safe price \& news APIs for offline 2024/2025 experiments, including trading date handling. | High | Enables local walk‑forward evaluation and ablation on A‑list; supports our design of research protocols. |
| NLPCC 2026 shared‑tasks page | Conference site | Confirms high‑level description of Task 4, organizer list, registration deadlines, and general shared‑tasks schedule.[^1] | High | Aligns timeline with implementation roadmap and clarifies certification / paper selection process. |
| CN‑Buzz2Portfolio | ArXiv 2026 | Chinese‑market dataset and benchmark for news‑to‑portfolio agents; proposes Tri‑Stage Compression‑Perception‑Allocation agent workflow.[^2] | Medium‑High | Inspires multi‑stage architectures where LLM compresses news, a perception module embeds events, and a separate allocator builds portfolios. |
| SPIN (Sparse Portfolio with Irregular News) | Journal/IEEE 2025 | News‑driven sparse portfolio strategy that exploits industry group structure and irregular news timing in fluctuating markets.[^3][^4] | High | Motivates sparse allocations, sector‑aware regularization, and handling irregular, bursty financial news streams. |
| GNN‑ETF | Conf. paper | Graph neural network framework modelling relationships among ETFs from different sectors for asset allocation.[^5] | High | Supports graph‑based sector relation modelling and MoE routing over sectors in a knowledge‑graph agent. |
| LLM top‑down sector allocation | ArXiv 2025 | Uses LLMs to interpret macro narratives for sector allocation, integrating sentiment and topic structure with quant features.[^6] | Medium‑High | Justifies LLM‑based event extraction to sector tilts, but suggests separation between textual reasoning and quantitative allocation. |
| Agentic Trading (LLM agents meet markets) | ArXiv 2026 | Surveys LLM trading agents, including news‑driven LLM‑RL for portfolio management and multi‑agent architectures.[^7] | Medium‑High | Highlights pitfalls of LLM‑only traders and motivates constrained LLM roles plus tool‑based allocators. |
| Portfolio mgmt with AI | Review 2024 | Reviews text mining and sentiment for enhancing portfolio decisions; notes that news can reveal latent risk factors and improve timing.[^8] | High | Supports using news‑derived factors as inputs to classical or robust portfolio optimizers rather than raw sentiment rules. |
| Temporal transformers / SSMs | Multiple papers | Show that temporal transformers and state‑space models capture long‑range financial dependencies efficiently and robustly.[^9][^10][^11][^12] | High | Motivates transformer‑inspired event memory modules (e.g., decayed attention, SSM filters) in TEMA‑like designs. |
| Black–Litterman and Bayesian extensions | Journal/monograph | Original BL and Bayesian generalizations for combining prior equilibrium returns with investor views under covariance uncertainty.[^13][^14] | High | Basis for robust BL‑style agents combining prior ETF views with news‑derived return views and ambiguity sets. |
| Universal portfolios \& OCO | Classic work | Online portfolio selection as online convex optimization; universal portfolios and regret bounds for log‑optimal allocation.[^15][^16] | High | Provides mathematically principled bandit/OCO allocators that can sit under an LLM‑driven feature layer. |
| Invariant Risk Minimization | ArXiv + slides | Introduces IRM to learn representations whose optimal classifier is invariant over environments, linking to causal robustness.[^17][^18] | High | Motivates causal/invariant event‑impact models that seek news features predictive across 2024 sub‑regimes, improving B‑list robustness. |
| Metadata‑driven RAG for finance | ArXiv 2025 | Studies RAG on long financial filings and shows gains from metadata‑rich embeddings and reranking.[^19] | Medium‑High | Informs analogue‑market retrieval design and argues for structured metadata (dates, sectors, macro tags) in retrieval indices. |

C. Candidate Design Universe
----------------------------

Below are 12 candidate designs before consolidation; “Final?” reflects keep/merge decisions for later sections.

1. **BSA‑RP: Belief‑State Agent with Risk‑Parity Control**
    - Core idea: Maintain a low‑dimensional belief state over macro/sector conditions updated by news and prices, feed it into a risk‑parity style allocator with drawdown and turnover constraints.
    - Engine: Bayesian filter over latent factors + risk‑parity / volatility‑targeted allocation.
    - LLM role: Structured event extraction and macro/sector tagging from news.
    - Track fit: Strong for Track 1, moderate for Track 2.
    - Final? **Keep** – main belief‑state / memory‑based agent.
2. **KG‑MoE: Knowledge‑Graph Mixture‑of‑Experts Allocator**
    - Core idea: Build a sector/ETF relation graph (industry, supply chain, style) and route inputs to specialized allocators per subgraph using MoE gating.
    - Engine: GNN over ETF graph + MoE of linear/risk‑parity experts.[^5]
    - LLM role: Entity/sector mapping and relation enrichment from news and ETF descriptions.
    - Track fit: Strong for Track 2, decent for Track 1.
    - Final? **Keep** – graph/knowledge‑based design.
3. **DRO‑BL: Distributionally Robust Black–Litterman Agent**
    - Core idea: Use BL to combine equilibrium ETF returns with news‑derived views under a distributionally robust ambiguity set, then allocate via robust mean‑variance subject to turnover constraints.[^13][^14]
    - Engine: Robust BL + convex optimization.
    - LLM role: Translate news into structured views (sign, magnitude, confidence).
    - Track fit: Strong for both tracks.
    - Final? **Keep** – robust portfolio‑optimization anchor.
4. **TEMA: Transformer Event Memory Allocator**
    - Core idea: Use a transformer/SSM‑style event memory over the last K days of news and price shocks to produce time‑decayed event embeddings that feed into a parametric scoring layer for each ETF.[^9][^10][^11]
    - Engine: Temporal transformer / SSM with attention decay over events.
    - LLM role: Event compression (headline→event tokens) and denoising; allocator is non‑LLM.
    - Track fit: Strong especially for Track 2.
    - Final? **Keep** – transformer‑inspired architecture.
5. **Rank‑Meta: Learning‑to‑Rank Meta‑Allocator**
    - Core idea: Train a model that ranks candidate portfolios (or tilts) produced by several base allocators (equal‑weight, inverse‑vol, momentum, BL, etc.) given state features, effectively learning a meta‑allocation rule.
    - Engine: Gradient‑boosted ranking or neural LTR over portfolio candidates.[^20]
    - LLM role: Feature enrichment (e.g., policy tags, regime labels) but not scoring.
    - Track fit: Balanced for both tracks.
    - Final? **Keep** – learning‑to‑rank / meta‑allocation family.
6. **Regime‑HMM: Hidden‑State Regime‑Switching Allocator**
    - Core idea: Fit an HMM or Markov‑switching model on macro and sector returns, maintain posterior regime probabilities, and condition allocations on regime (e.g., defensive in “recession” state).[^21][^22]
    - Engine: HMM or switching state‑space model; rule‑based allocation per regime.
    - LLM role: Optional regime labelling/explanation only; core filter is quant.
    - Track fit: Strong for Track 1, reasonable for Track 2.
    - Final? **Keep** – regime/hidden‑state family.
7. **RAM‑IRM: Retrieval Analogue Market with Invariant Risk Minimization**
    - Core idea: For each day, retrieve analogue historical windows based on news and price patterns, then learn news factors that are predictive of returns across multiple “environments” (2024 subperiods) via IRM for causal robustness, and map them to tilts.[^2][^17][^19]
    - Engine: k‑NN / metric learning retrieval + IRM‑trained linear allocator.
    - LLM role: Generate metadata and embeddings for retrieval index (topics, policy, sectors).
    - Track fit: Balanced.
    - Final? **Merge into Retrieval‑Causal** – see Design 7.
8. **OCO‑Ensemble: Online Convex Optimization Ensemble Allocator**
    - Core idea: Use online mirror descent / regret‑minimizing updates on 2024/2025 walk‑forward, with multiple regularized experts (e.g., entropy‑regularized universal portfolio with turnover penalties) combined using exponentially weighted forecasters.[^16][^15]
    - Engine: Online convex optimization and expert aggregation.
    - LLM role: None or only explanations.
    - Track fit: Strong and symmetric.
    - Final? **Keep** – online/bandit family.
9. **Causal‑Event‑BL: Causal/Counterfactual Event‑Impact Black–Litterman**
    - Core idea: Use causal representation learning / IRM to identify news features whose predictive effect on returns is invariant across 2024 environments, use those as BL views, and project counterfactual “no‑event” scenarios to stress‑test allocations.[^17][^18]
    - Engine: IRM‑style representation + BL; causal graphs over sectors.
    - LLM role: Graph skeleton proposal and causal variable naming; optimizer is quant.
    - Track fit: Good for both tracks; may be research‑heavy.
    - Final? **Keep but merge with Retrieval** – becomes **Retrieval‑Causal BL**.
10. **Vanilla LLM Trader (rejected baseline)**
    - Core idea: Prompt an LLM with news and recent returns and ask it to output daily ETF weights directly.
    - Engine: None beyond LLM; no formal risk model.
    - LLM role: Full allocator.
    - Track fit: Unknown; likely unstable.[^7][^6]
    - Final? **Reject** – useful only as a diagnostic baseline and anti‑pattern.
11. **Pure RL Agent (Deep RL Allocator)**
    - Core idea: End‑to‑end actor–critic RL on 2024 data using price and news embeddings, optimizing Sharpe with penalties for turnover and drawdown.[^23][^21]
    - Engine: DRL policy network; LLM possibly for event embedding.
    - Final? **Defer / reject for now** – too data‑hungry and fragile on B‑list given limited horizon.
12. **News‑Only Sentiment Allocator**
    - Core idea: Classic sentiment aggregation from news mapped to ETF long/short tilts; minimal price features.[^8]
    - Engine: Sentiment scoring and threshold rules.
    - Final? **Reject as main design** – serves as ablation/baseline component only.

**Final design set (for D–K):**

1. BSA‑RP (belief‑state / memory).
2. KG‑MoE (graph / knowledge).
3. DRO‑BL (robust BL).
4. TEMA (transformer event memory).
5. Rank‑Meta (learning‑to‑rank meta allocator).
6. Regime‑HMM (hidden‑state / regime).
7. Retrieval‑Causal BL (merging RAM‑IRM + Causal‑Event‑BL).
8. OCO‑Ensemble (online / bandit).

D. Five to Eight Final Design Blueprints
----------------------------------------

Below, each design follows the required 14‑item template; detailed math is expanded in Section E.

### Design 1: BSA‑RP – Belief‑State Agent with Risk‑Parity Control

1. **One‑sentence thesis**
Maintain a low‑dimensional latent belief state over macro and sector conditions updated by prices and news, then allocate via risk‑parity with explicit drawdown and turnover controls.
2. **Novelty claim**
Unlike pure LLM allocators, simple momentum, sentiment scoring, or generic RAG, BSA‑RP formalizes “market understanding” as a Bayesian belief state over factors and uses it only as an input to a transparent risk‑parity optimizer with mathematically defined constraints and half‑life, giving a clean separation between text perception and allocation.[^6][^8]
3. **Mathematical state representation**
    - Let $f_t \in \mathbb{R}^K$ be latent macro factors (growth, inflation, policy support, risk‑aversion) and $s_t \in \mathbb{R}^S$ be sector tilt factors.
    - The combined belief state is $b_t = [\mu_{f,t}, \Sigma_{f,t}, \mu_{s,t}, \Sigma_{s,t}]$, where $\mu$ are posterior means and $\Sigma$ posterior covariances.
    - News embedding $e_t \in \mathbb{R}^d$ is derived from LLM‑structured event extraction.
4. **Update rule**
    - Prior: $\mu_{f,t|t-1} = A_f \mu_{f,t-1},\ \Sigma_{f,t|t-1} = A_f \Sigma_{f,t-1} A_f^\top + Q_f$.
    - Observation from returns $r_t$ and news features $z_t = g(e_t, r_{t-1:t-L})$ via linear observation $y_t = H_f f_t + \epsilon_t$ with Kalman‑style update to $\mu_{f,t},\Sigma_{f,t}$.[^22]
    - Similar updates for $s_t$; see Section E.
5. **LLM role**
    - Event extraction: convert each news article into structured tuples (macro theme, sector, direction, confidence, horizon).
    - Entity/sector mapping: tag ETFs to sectors and macro themes.
    - No direct control of weights; can produce human‑readable rationales post‑hoc.
6. **Non‑LLM engine**
    - Bayesian/Kalman filter for belief state.
    - Risk‑parity / volatility‑targeted portfolio optimization using covariance estimated from recent returns and factor beliefs.[^8][^20]
7. **Portfolio construction**
    - Target risk contributions $RC_i = w_i (\Sigma w)_i \propto h_i(b_t)$, where $h_i$ is a non‑negative function mapping beliefs to desired risk budgets (e.g., overweight sectors with positive $s_t$).
    - Solve for $w_t$ such that $RC_i \approx \bar{RC}_i$ under constraints $\sum_i w_i = 1,\ 0 \le w_i \le w_{\max}$, with volatility scaling to meet target $\sigma^*$ and transaction cost penalty in the objective.
    - Turnover control by adding $\lambda \|w_t - w_{t-1}\|_1$ or capping daily turnover; drawdown control via max‑drawdown trigger reducing overall risk budget if cumulative drawdown exceeds threshold.
8. **Data use and leakage safety**
    - Uses `get_historical_prices(..., current_date, lookback_days)` which returns only past full OHLCV and current open, plus `get_news(..., current_date)` which ensures Top‑N news truncated at 15:00; 2024 is train, 2025 walk‑forward validation, 2026 B‑list only via organizers.
    - LLM models and embeddings must come from pre‑2026 checkpoints; no future labels (same‑day returns) used at decision time.
9. **Track fit**
    - Track 1: **9/10** – belief over macro factors, risk‑parity suits macro ETFs.
    - Track 2: **7/10** – sector factors can be added but sector rotations may need more granularity.
10. **Implementation plan (student‑days)**
    - MVP (8–10): simple exponential‑decay factor model with heuristic mapping from news sentiment to factor tilts; static risk‑parity.
    - Strong (15–20): full Kalman filter, news‑derived features from offline finetuned Chinese news encoder, explicit risk contributions and turnover constraints.
    - Report‑ready (5–7 extra): interpretable factor dashboards, day‑by‑day belief trajectories, ablation runs, and rationales.
11. **Failure modes**
    - Overfitting 2025 via excessive tuning of factor mapping; mis‑specification of factor dynamics.
    - Hallucinated causal reasoning if LLM‑based feature mapping is overtrusted.
    - Excessive turnover if risk budgets respond too aggressively to belief updates.
    - Regime shift where macro factors change behaviour in 2026.
    - Non‑reproducibility if LLM outputs are not cached and prompts change.
12. **Ablation plan**
    - No LLM: replace event features with simple numeric news features (TF‑IDF, dictionary sentiment).
    - No news: factors updated only from returns.
    - No memory: static mapping from 20‑day momentum/vol to allocations.
    - No risk control: drop risk‑parity, use simple proportional tilt; expect worse drawdown.
    - Quant‑only vs LLM‑only vs mixed; 2024‑tuned vs 2025‑retuned hyperparameters.
13. **Baseline justification**
    - Must show higher risk‑adjusted returns and lower drawdown than equal‑weight, inverse‑vol, momentum, and S1 macro allocator on 2024→2025 walk‑forward, *without* large turnover increases.
    - Must show that adding belief state and news improves Sharpe vs pure price‑based risk‑parity.
14. **Paper / award narrative**
    - Strong story: interpretable belief‑state over macro/sector conditions, explicit link between news events and changing risk budgets, and neat visualizations of belief trajectories and allocations, ideal for a 2‑page system note and as an example of “LLM‑enhanced but quant‑controlled” design.[^6][^8]

### Design 2: KG‑MoE – Knowledge‑Graph Mixture‑of‑Experts Allocator

1. **One‑sentence thesis**
Represent ETFs as nodes in a sector/supply‑chain/style graph and route daily signals through a GNN + mixture‑of‑experts allocator to produce sector‑aware tilts.
2. **Novelty claim**
Goes beyond sentiment/momentum by using a learned ETF relation graph and gating between multiple allocation experts per subgraph (e.g., growth, value, policy‑sensitive clusters), inspired by GNN‑ETF and MoE routing, rather than a monolithic allocator.[^5]
3. **State representation**
    - Graph $G = (V,E)$ with nodes $i$ as ETFs and edges reflecting sector similarity, co‑movement, and news co‑mentions.[^3][^5]
    - Node features $x_{i,t}$ include price factors (momentum, volatility, carry) and news embeddings aggregated per ETF.
    - Hidden node embeddings $h_{i,t}$ from GNN, plus expert weights $\alpha_{k,t}$ from a gating network.
4. **Update rule**
    - At each day, update node features $x_{i,t}$ with new price and news aggregates; run $L$ GNN layers $h_{t} = \text{GNN}(G, x_t)$.[^5]
    - Gating network computes expert weights from global summary $g_t = \text{pool}(h_t)$, outputting $\alpha_t = \text{softmax}(W_g g_t)$.
    - Experts produce preliminary weights $w^{(k)}_t$; final weights $w_t = \sum_k \alpha_{k,t} w^{(k)}_t$.
5. **LLM role**
    - Entity and sector mapping: parse ETF names and descriptions into sectors, themes, and styles.
    - News relation extraction: build edges where ETFs are jointly impacted by policies or supply‑chain links.
    - Optional: explain daily gating behaviour in natural language.
6. **Non‑LLM engine**
    - GNN (e.g., graph attention network) + MoE gating; experts may be simple risk‑parity, BL, or trend allocations specialized to subgraphs.[^5]
7. **Portfolio construction**
    - Each expert $k$ outputs normalized weights $w^{(k)}_t$ subject to constraints per track (e.g., sector caps).
    - The final $w_t$ inherits those constraints, plus global turnover penalty:
$\min_{w^{(k)}_t} \sum_k \alpha_{k,t} L^{(k)}(w^{(k)}_t) + \lambda \|w_t - w_{t-1}\|_1$, with $L^{(k)}$ e.g. negative risk‑adjusted forecast.
    - Volatility scaling and max position per ETF; possible sparsity via $\ell_1$ regularization to encourage focused sector bets.
8. **Data \& leakage**
    - Same DataLoader usage as BSA‑RP; node features built from historical returns and pre‑15:00 news mapped to ETFs, with no same‑day close/high/low.
    - Graph and expert parameters trained on 2024; hyperparameters tuned only on 2024 or cross‑validated across 2024 folds to avoid 2025 overfitting.
9. **Track fit**
    - Track 1: **7/10** – macro ETFs form a small graph, still useful.
    - Track 2: **9/10** – sector relations are rich; GNN captures policy spillovers and thematic clusters.
10. **Implementation plan**
    - MVP (7–9): static graph from ETF metadata + simple 2‑layer GCN; two experts (trend‑following and mean‑reversion); hand‑tuned gating.
    - Strong (14–18): learned edges from correlation and co‑mention, attention GNN, 3–4 experts including defensive and aggressive; gating trained via 2024 cross‑entropy or Sharpe surrogate.[^3][^5]
    - Report‑ready (5–7 extra): visualization of ETF graph, expert activity timelines, case studies of policy shocks.
11. **Failure modes**
    - Graph mis‑specification: wrong edges amplify noise; structural overfitting to 2024 correlation patterns.
    - Overly confident gating causing mode collapse on one expert.
    - Turnover spikes if experts disagree strongly across days.
    - 2026 regime shift where sector relations change.
12. **Ablation plan**
    - No LLM: edges from hardcoded sectors and correlations only.
    - No graph: per‑ETF MLP ignoring relations.
    - No MoE: single GNN allocator.
    - No news: only price‑based features.
    - No turnover/risk control: unconstrained MoE as high‑risk baseline.
13. **Baseline justification**
    - Must beat sector trend‑following and S1 sector allocator in Track 2 on Sharpe and drawdown without excessive turnover; must show that graph connections improve performance vs independent per‑ETF models.
14. **Paper narrative**
    - Clear story about modelling ETF relations via a knowledge graph and using MoE for adaptive sector strategies, with visual graphs and expert routing patterns – highly appealing for system‑report selection.[^3][^5]

### Design 3: DRO‑BL – Distributionally Robust Black–Litterman Agent

1. **One‑sentence thesis**
Combine equilibrium returns with news‑derived views within a distributionally robust BL framework, then solve a robust mean‑variance allocation with explicit turnover and risk constraints.
2. **Novelty claim**
Builds on classical BL but adds (i) news‑derived views from structured LLM extraction, (ii) an ambiguity set for expected returns and covariance to hedge model uncertainty, and (iii) explicit transaction cost and turnover‑aware optimization, going beyond naive sentiment or standard BL.[^14][^13]
3. **State representation**
    - Prior equilibrium returns $\pi_t$ (e.g., from long‑run CAPM or risk‑parity implied returns).
    - View matrix $P_t$ and view vector $q_t$ with confidence $\Omega_t$.
    - Ambiguity set $\mathcal{U}_t = \{(\mu,\Sigma) : \|\mu - \mu_t\|_{\Sigma^{-1}} \leq \delta_t\}$.
4. **Update rule**
    - Compute sample returns and covariances over a rolling window; map news events to views $q_t$ (e.g., “pro‑new‑energy policy” → higher expected return for relevant ETFs).
    - Apply robust BL update to get posterior mean $\mu_t^{\text{rob}}$ lying in $\mathcal{U}_t$, solving a convex inner problem that shrinks views when confidence is low.[^14]
5. **LLM role**
    - Event extraction and mapping to numerical views (sign, magnitude, horizon, affected ETFs) plus view confidence estimation based on historical analogues and textual intensity.
    - No direct control over weights; human‑readable explanation of current views.
6. **Non‑LLM engine**
    - Robust BL + robust mean‑variance optimization under ambiguity sets and turnover constraints.[^13][^14]
7. **Portfolio construction**
    - Solve $\min_{w} w^\top \Sigma_t w - \lambda_\mu \mu_t^{\text{rob}\top} w + \lambda_T \|w - w_{t-1}\|_1$ s.t. $\sum_i w_i = 1,\ 0 \le w_i \le w_{\max},\ \sigma(w) \le \sigma^*$.
    - Optionally incorporate worst‑case expected returns over $\mathcal{U}_t$ in the objective; drawdown control via dynamic $\sigma^*$ based on realised drawdown.
8. **Data \& leakage**
    - Uses only historical returns and pre‑15:00 news; views are formed from 2024‑trained mapping functions plus some hand rules; no 2025 data in training beyond validation.
    - The 0.01% friction is respected by the turnover penalty and by multi‑day view horizons.
9. **Track fit**
    - Track 1: **9/10** – macro ETFs are classical BL territory.
    - Track 2: **8/10** – sector tilts also suit BL, though noise may be higher.
10. **Implementation plan**
    - MVP (6–8): classical BL with hand‑crafted views from rule‑based news tags, no robust ambiguity set.
    - Strong (12–16): robust BL with learned confidence and ambiguity, plus sharpe‑oriented mean‑variance with turnover and drawdown limits.
    - Report‑ready (4–5): scenario analyses, worst‑case vs nominal allocations, and ablations with/without robustness.
11. **Failure modes**
    - Overconfident views causing concentrated positions.
    - Ambiguity set too large → nearly revert to prior; too small → overfitting.
    - Incorrect mapping from news to views, especially in novel 2026 policy regimes.
12. **Ablation plan**
    - No LLM: views from simple keyword rules.
    - No news: pure equilibrium allocation.
    - No robustness: standard BL only.
    - No turnover constraints: high‑turnover BL baseline.
    - Compare to equal‑weight, inverse‑vol, momentum, and rule‑based macro rotation.
13. **Baseline justification**
    - Must show that BL with news views and robustness improves Sharpe and drawdown relative to static BL and S1 macro allocator, while not increasing turnover beyond cost‑efficient bands.
14. **Paper narrative**
    - A clean “classical quant enhanced by LLM‑structured views” story with robust optimization is mathematically deep, interpretable, and easy to present with formulas and case studies, making it a strong system‑report candidate.[^13][^14]

### Design 4: TEMA – Transformer Event Memory Allocator

1. **One‑sentence thesis**
Use a transformer/SSM‑style event memory over recent news and price shocks to produce decayed event embeddings that drive a non‑LLM scoring function for ETF allocations.
2. **Novelty claim**
Instead of calling an LLM as the allocator, this design borrows *internal* transformer ideas (multi‑head attention, positional decay, state‑space filtering) to build an event memory module specialized to news‑driven investing, feeding a simple scoring layer, akin to CN‑Buzz2Portfolio’s perception/ allocation split but without an LLM in the allocation.[^10][^9][^2]
3. **State representation**
    - For each day $t$ and ETF $i$, construct tokens representing (news event, affected ETF set, price shock) with embeddings $x_{i,t,\tau}$ over the last $L$ days.
    - Event memory $m_{i,t}$ is the final state of a transformer/SSM over these tokens.
4. **Update rule**
    - At each day, build a sequence of tokens for the last $L$ trading days from DataLoader’s news and price windows, including only pre‑15:00 news; feed through a temporal transformer with learnable positional decay; maintain SSM‑style recurrent state if computationally needed.[^9][^10]
    - $m_{i,t} = \text{Transformer}(x_{i,t-L+1:t})$ or $m_{i,t} = \text{SSM}(m_{i,t-1}, x_{i,t})$.
5. **LLM role**
    - Compress raw Chinese news into event tokens (issuer, sector, theme, surprise direction) and assign them to ETFs; this can use an offline LLM or specialized Chinese financial NLU model.[^8][^6]
    - No online LLM calls needed during B‑list if compression is precomputed.
6. **Non‑LLM engine**
    - Temporal transformer / S4‑like SSM with decayed attention over events, followed by a linear or shallow neural scoring head per ETF.
7. **Portfolio construction**
    - For each ETF, compute score $s_{i,t} = u^\top m_{i,t}$ and transform into raw desired weights via softmax with temperature:
$w^{\text{raw}}_{i,t} = \exp(s_{i,t}/\tau) / \sum_j \exp(s_{j,t}/\tau)$.
    - Apply volatility scaling and cap changes per day to enforce turnover limits; optionally encourage sparsity using entropic or $\ell_1$ regularization on weights.
8. **Data \& leakage**
    - Uses the same DataLoader and respects 15:00 cutoff; transformer is trained offline on 2024 (maybe 2025 A‑list for validation) using next‑day risk‑adjusted returns as labels.
    - No 2026 data used; event compression must be built from pre‑2026 models.
9. **Track fit**
    - Track 1: **7/10** – macro events still matter but may be less frequent.
    - Track 2: **8/10** – sector news is abundant; transformer can exploit irregular sequences well.[^2][^3]
10. **Implementation plan**
    - MVP (8–10): simple one‑layer temporal attention over last 5–10 days’ aggregated news and price shocks.
    - Strong (15–20): deeper transformer/SSM, multi‑head attention, cross‑asset attention for spillovers; well‑tuned event half‑life and capacity.
    - Report‑ready (5–7): visualizations of attention weights over events, case studies of how specific news sequences affected allocations.
11. **Failure modes**
    - Overfitting to rare patterns in 2024 news; poor robustness to 2026 novel events.
    - Unstable event‑to‑asset mapping if event assignment is noisy.
    - Excessive sensitivity to prompt design for the event compression LLM if used online.
12. **Ablation plan**
    - No LLM: event tokens from rule‑based heuristics.
    - No news: only price shock tokens.
    - No transformer: replace with simple exponential decays over hand‑crafted factors.
    - No turnover constraints: examine pure transformer‑driven rotations.
    - Compare to momentum and news‑only baselines.
13. **Baseline justification**
    - Must show improved Sharpe or reduced drawdown over momentum/trend‑following and SPIN‑like news strategies with controlled turnover.[^4][^3]
    - Must demonstrate that attention patterns align with intuitive event half‑lives.
14. **Paper narrative**
    - A clearly “transformer‑inspired but not LLM‑oracle” design that focuses on event memory over financial news, with clean visualizations of attention and event impacts, is highly publishable and novel within this shared task.[^10][^9][^2]

### Design 5: Rank‑Meta – Learning‑to‑Rank Meta‑Allocator

1. **One‑sentence thesis**
Learn to rank and combine outputs from multiple base allocators (quant and rule‑based) given state features, producing a meta‑allocation that adapts to market regimes and news.
2. **Novelty claim**
Rather than training yet another end‑to‑end allocator, this approach treats portfolios themselves as candidates and uses LTR to select or blend them, leveraging ensemble wisdom and enabling clean ablations.
3. **State representation**
    - Set of base portfolios $\{w^{(k)}_t\}_{k=1}^K$ from equal‑weight, inverse‑vol, momentum, BL, BSA‑RP, etc.
    - Features $\phi_t$ summarizing state: regime indicators, realized vol/trend, news sentiment/volume, dispersion measures.
4. **Update rule**
    - Offline, treat each day’s realized performance of each portfolio as label $y^{(k)}_t$ and learn a ranking model $f(\phi_t, \text{stats}(w^{(k)}_t))$ that predicts relative performance; train using pairwise or listwise LTR on 2024.[^20]
    - Online, compute scores $s^{(k)}_t = f(\phi_t, \cdot)$ and mixture weights via softmax.
5. **LLM role**
    - Generate high‑level regime tags and textual features (e.g., “policy tightening”, “tech crackdown easing”) that are embedded into $\phi_t$.
    - Explanation of why a given base allocator was preferred on a given day.
6. **Non‑LLM engine**
    - Gradient‑boosted trees or small MLP for ranking; optional regularized linear blender.
7. **Portfolio construction**
    - Mixture weights $\beta^{(k)}_t = \exp(s^{(k)}_t)/\sum_j \exp(s^{(j)}_t)$.
    - Final portfolio $w_t = \sum_k \beta^{(k)}_t w^{(k)}_t$, inheriting each base’s constraints and adding turnover penalty on $w_t$.
    - May include a “persistence” baseline among candidates to encourage low turnover.
8. **Data \& leakage**
    - Uses only historical candidate performance and features built from allowed DataLoader outputs; training on 2024 only.
    - 2025 used as pseudo‑live walk‑forward to calibrate LTR hyperparameters but not re‑trained to avoid overfitting.
9. **Track fit**
    - Track 1: **7/10** – can blend macro allocators.
    - Track 2: **8/10** – can switch among sector‑trend and mean‑reversion strategies.
10. **Implementation plan**
    - MVP (6–8): small set of base strategies + simple gradient boosting ranker.
    - Strong (12–15): more diverse base allocators (including BSA‑RP and DRO‑BL) plus richer feature set and mixture controls.
    - Report‑ready (5–6): detailed ablations on removing each base, SHAP‑style analysis on features influencing meta‑choices.
11. **Failure modes**
    - Overfitting to which base did well in 2024; meta model may simply mirror one base.
    - Degenerate mixtures (always equal‑weight).
    - Miscalibration of mixture leading to undue switching and turnover.
12. **Ablation plan**
    - No LLM features: purely numeric states.
    - No news features: meta only sees price‑based states.
    - Single‑best base vs learned mixture; check whether mixture actually adds value.
    - Removal of each base allocator in turn.
13. **Baseline justification**
    - Must show that mixtures beat the best single quant baseline in risk‑adjusted return and that meta‑allocation remains stable across 2024 subwindows and 2025.
14. **Paper narrative**
    - Elegant narrative around “meta‑allocation over quant agents” with clear interpretability and modularity; fits very well with the shared task’s framing of LLM‑**based** advisors orchestrating quant tools.[^7]

### Design 6: Regime‑HMM – Hidden‑State Regime‑Switching Allocator

1. **One‑sentence thesis**
Model latent market regimes via an HMM over ETF returns and allocate according to regime‑specific policies, optionally annotated by LLM‑generated descriptions.
2. **Novelty claim**
While regime switching is classical, combining it with news‑derived observation features and explicit, interpretable regime‑conditioned policies produces a robust, explainable allocator distinct from generic momentum or sentiment strategies.[^22]
3. **State representation**
    - Hidden regime variable $z_t \in \{1,\dots,R\}$ (e.g., bull, bear, volatile sideways).
    - Regime posterior $\gamma_t = P(z_t | \mathcal{F}_t)$ where $\mathcal{F}_t$ is history of returns and news features.
4. **Update rule**
    - Standard HMM filtering: forward algorithm with emission probabilities incorporating returns and possibly aggregated news sentiment or topic indicators.[^22]
    - $P(z_t | \mathcal{F}_t) \propto P(r_t | z_t, \text{features}_t) \sum_{z_{t-1}} P(z_t|z_{t-1}) P(z_{t-1}|\mathcal{F}_{t-1})$.
5. **LLM role**
    - Post‑hoc regime labelling (e.g., “policy easing growth regime”) and human‑readable explanations; optionally feature engineering for emission models.
    - Not used in inference loop for B‑list.
6. **Non‑LLM engine**
    - HMM / Markov‑switching model + regime‑specific allocation rules (e.g., risk‑on vs risk‑off tilts).
7. **Portfolio construction**
    - For each regime $r$, define a base portfolio $w^{(r)}$; daily target $w_t = \sum_r \gamma_{t,r} w^{(r)}$ smoothed with turnover constraints.
    - Risk controls: defensive regimes with lower target volatility and higher bond/gold weights; aggressive regimes with higher equity/sector weights.
8. **Data \& leakage**
    - Fit HMM on 2024 returns (and possibly news features) using only historical data per DataLoader; regime identification uses past returns only.
    - Regime transitions and emissions are fixed for B‑list.
9. **Track fit**
    - Track 1: **9/10** – macro regimes natural.
    - Track 2: **7/10** – sector rotation may prefer more granular states.
10. **Implementation plan**
    - MVP (5–7): 2–3 regime HMM with simple regime portfolios.
    - Strong (10–12): include news‑dependent emissions and more nuanced regime‑conditioned allocations.
    - Report‑ready (4–5): regime timeline plots, case study of regime switches in 2025.
11. **Failure modes**
    - Misidentified regimes due to short 2024 history; poor robustness to 2026 macro shifts.
    - Regime stickiness causing slow reaction; or too volatile regime switching causing churn.
12. **Ablation plan**
    - No news in emission; only returns.
    - Fixed regime portfolios vs learned ones.
    - Different regime counts (2 vs 3 vs 4).
    - Compare to rule‑based macro rotation baseline.
13. **Baseline justification**
    - Must demonstrate better drawdown control vs trend‑following and rule‑based rotation, and some Sharpe improvement without extreme turnover.
14. **Paper narrative**
    - Classical yet well‑packaged design with clear regime panels and human descriptions; good “anchor” method demonstrating that simple hidden‑state models remain competitive under news‑rich inputs.[^22]

### Design 7: Retrieval‑Causal BL – Analogue‑Market Retrieval + Causal Views

1. **One‑sentence thesis**
Retrieve historical analogue market episodes based on news and prices, learn invariant event‑impact representations via IRM, and inject those as causally robust BL views.
2. **Novelty claim**
Goes beyond standard RAG by treating retrieval as analogue market matching and combining it with IRM‑based causal representation learning and BL, rather than using retrieval only to stuff prompts.[^19][^17][^2]
3. **State representation**
    - Index of windows $w$ in 2024 with metadata (dates, sectors, news topics, macro indicators).
    - For current day $t$, retrieved set $\mathcal{N}_t$ of similar windows, plus IRM representation $h_t$ learned across training environments (e.g., quarterly splits).
    - BL prior and views as in DRO‑BL, but views derived from causally stable features of $h_t$.
4. **Update rule**
    - Offline: train IRM representation such that linear predictors from $h_t$ to future returns are invariant across environments; build retrieval index with metadata (LLM‑generated topic/sector tags).[^18][^17][^19]
    - Online: for each day, retrieve $\mathcal{N}_t$ to estimate event‑conditioned expected returns and confidence, applying BL with views weighted by causal stability.
5. **LLM role**
    - Generate metadata (topics, policy labels, sectors) for news and windows to improve retrieval, following metadata‑aware RAG insights.[^19]
    - Possibly help define environment splits (regime labels) for IRM training; no direct allocation.
6. **Non‑LLM engine**
    - k‑NN / similarity search, IRM‑trained representation, BL with causal views.
7. **Portfolio construction**
    - Similar to DRO‑BL but with view vector $q_t$ derived from causal IRM features and analogue episodes:
$q_t = \sum_{w\in\mathcal{N}_t} \omega_w r_{w+1}$, where $\omega_w$ depends on causal feature similarity.
    - Robust mean‑variance with turnover and drawdown controls as in Design 3.
8. **Data \& leakage**
    - Index and IRM representation trained solely on 2024; retrieval uses only past windows relative to each decision day when building features and metadata.
    - No 2025/2026 data used in training; 2025 used only for offline evaluation.
9. **Track fit**
    - Track 1: **8/10** – macro analogues useful.
    - Track 2: **8/10** – sector policy episodes repeat; retrieval shines.
10. **Implementation plan**
    - MVP (8–10): simple similarity on numeric features + retrieval‑averaged returns; basic BL.
    - Strong (15–20): full IRM training, rich metadata, and robust BL; approximate nearest‑neighbour index.
    - Report‑ready (6–8): case studies of retrieved analogues for big 2025 events, visualizing causal features.
11. **Failure modes**
    - Sparse or unrepresentative analogues for novel 2026 events.
    - IRM underfitting or failing to isolate causal features, leading to spurious views.
    - Overreliance on retrieval causing slow adaptation in new regimes.
12. **Ablation plan**
    - No IRM: simple regression on features.
    - No retrieval: global mapping from features to views.
    - No BL: direct mapping to weights.
    - No LLM metadata: retrieval only on numeric signals.
13. **Baseline justification**
    - Must show that analogue retrieval plus causal views outperform both plain BL and purely price‑based analogues, especially in B‑list‑like 2025 splits.
14. **Paper narrative**
    - Strong research‑award candidate: explicit causal and retrieval structure, visualizable analogue episodes, and robust BL mathematics; aligns with IRM literature and goes well beyond generic RAG.[^17][^2][^19]

### Design 8: OCO‑Ensemble – Online Convex Optimization Ensemble Allocator

1. **One‑sentence thesis**
Run an ensemble of simple expert strategies updated via online convex optimization to minimize regret in log wealth, with explicit turnover and risk regularization.
2. **Novelty claim**
Brings universal portfolio and OCO theory into the LLM‑advisor setting, where LLMs are optional explainers and the core engine is a provably motivated online allocator over ETF pools.[^15][^16]
3. **State representation**
    - Current weights $w_t$, cumulative returns, and expert predictions $w^{(k)}_t$ from simple strategies (momentum, equal‑weight, inverse‑vol, BL, etc.).
    - OCO state includes convex loss functions (e.g., negative log return plus penalties) and gradient history.
4. **Update rule**
    - Online mirror descent or exponentiated gradient:
$w_{t+1} \propto w_t \odot \exp(-\eta \nabla \ell_t(w_t))$, with $\ell_t$ including turnover penalties and cross‑entropy vs expert suggestions.[^16][^15]
    - Optionally treat each expert as action in exp‑weights forecaster.
5. **LLM role**
    - Not needed in core loop; can generate explanations (“today we lean towards defensive expert due to volatility and negative news”).
    - Keeps tool‑dependency risk low.
6. **Non‑LLM engine**
    - OCO algorithms with convex constraints; universal portfolio ideas and regret analysis.
7. **Portfolio construction**
    - Daily optimization in simplex with box constraints and turnover penalty; risk control via volatility target and capital allocation to experts with lower estimated regret.
    - Drawdown control can be implemented as a state‑dependent cap on leverage or maximal risky allocation.
8. **Data \& leakage**
    - Uses only past returns (and possibly features) as permitted; no news required though it can be added as context to experts’ signals.
    - Trained/initialised on 2024, then run walk‑forward on 2025; B‑list is pure online.
9. **Track fit**
    - Track 1: **8/10** – macro ETFs fit OCO well.
    - Track 2: **8/10** – sector ETFs also workable; might require more careful turnover control.
10. **Implementation plan**
    - MVP (5–7): exponentiated gradient over 3–4 simple experts; fixed learning rate.
    - Strong (10–14): adaptive learning rates, risk‑sensitive loss, and expert expansion.
    - Report‑ready (4–6): plots of regret vs baselines, demonstration that OCO maintains performance even under shifts.
11. **Failure modes**
    - Poor learning rate selection leads to either inertia or overreaction.
    - Experts themselves might be weak; ensemble can’t outperform best single if mis‑configured.
    - Drawdown controls may conflict with regret minimization.
12. **Ablation plan**
    - No turnover penalty; pure OCO vs cost‑aware variant.
    - No risk controls; unconstrained universal portfolio.
    - Different expert sets (with/without news‑aware experts).
    - Compare against static equal‑weight and S1 core.
13. **Baseline justification**
    - Must show consistently competitive Sharpe and lower regret vs static baselines on 2024→2025; must not materially worsen turnover‑adjusted Sharpe; emphasise theoretical guarantees.
14. **Paper narrative**
    - While less flashy, a well‑explained OCO implementation with proofs and empirical regret plots can be compelling, especially combined with LLM‑generated natural‑language rationales tying online updates to news and regimes.[^15][^16]

E. Mathematical Formulation of Each Design
------------------------------------------

For brevity, I focus on core mathematical parts; all designs share the same basic return and constraint structure.

### Common notation

- $N$: number of ETFs in the track.
- $r_{t+1} \in \mathbb{R}^N$: vector of gross returns from $t$ to $t+1$.
- $w_t \in \mathbb{R}^N$: portfolio weights at day $t$ with $\sum_i w_{i,t} = 1,\ 0 \le w_{i,t} \le w_{\max}$.
- Portfolio return: $R_{p,t+1} = w_t^\top r_{t+1}$.
- Turnover: $\text{TO}_t = \sum_i |w_{i,t} - w_{i,t-1}|$.
- Drawdown: $D_t = 1 - \frac{V_t}{\max_{s\le t} V_s}$, where $V_t$ is portfolio value.


### BSA‑RP

- **State**: belief $b_t = (\mu_{f,t},\Sigma_{f,t},\mu_{s,t},\Sigma_{s,t})$.
- **Update** (macro factors):
$\mu_{f,t|t-1} = A_f \mu_{f,t-1}$,
$\Sigma_{f,t|t-1} = A_f \Sigma_{f,t-1} A_f^\top + Q_f$.
With observation $y_t = H_f f_t + \epsilon_t$, the Kalman gain is
$K_t = \Sigma_{f,t|t-1} H_f^\top (H_f \Sigma_{f,t|t-1} H_f^\top + R_f)^{-1}$.
Posterior: $\mu_{f,t} = \mu_{f,t|t-1} + K_t (y_t - H_f \mu_{f,t|t-1})$.
- **Score‑to‑weight**: risk budgets $c_i = h_i(b_t)$ with $\sum_i c_i = 1$; risk contributions $RC_i = w_i (\Sigma w)_i$. Solve
$\min_w \sum_i (RC_i - c_i)^2 + \lambda_T \text{TO}_t$ s.t. standard constraints.
- **Risk control**: impose $\sqrt{w_t^\top \Sigma_t w_t} \le \sigma^*$; if drawdown $D_t > D_{\max}$, reduce $\sigma^*$.
- **Turnover control**: $\text{TO}_t \le \text{TO}_{\max}$ or penalty $\lambda_T \text{TO}_t$.


### KG‑MoE

- **State**: graph $G$, node embeddings $h_{i,t}$, expert weights $\alpha_{k,t}$.
- **GNN update**:
$h_{i,t}^{(l+1)} = \sigma\left(W^{(l)} h_{i,t}^{(l)} + \sum_{j\in \mathcal{N}(i)} a_{ij}^{(l)} U^{(l)} h_{j,t}^{(l)}\right)$.
- **Gating**:
$g_t = \text{pool}_i(h_{i,t}^{(L)})$,
$\alpha_{k,t} = \frac{\exp(v_k^\top g_t)}{\sum_j \exp(v_j^\top g_t)}$.
- **Experts**: each expert $k$ outputs $w^{(k)}_t$ via its own mapping (e.g., BL, momentum).
- **Final weights**: $w_t = \sum_k \alpha_{k,t} w^{(k)}_t$.
- **Risk \& turnover**: same as above; optionally add $\lambda_{\text{sparse}} \sum_i |w_{i,t}|$ to encourage few active sectors.


### DRO‑BL

- **Prior**: mean $\pi_t$, covariance $\Sigma_t$.
- **Views**: $P_t \mu = q_t + \epsilon,\ \epsilon \sim \mathcal{N}(0,\Omega_t)$.
- **Classical BL posterior**:
$\mu_t^{\text{BL}} = \left[(\tau\Sigma_t)^{-1} + P_t^\top \Omega_t^{-1} P_t \right]^{-1} \left[(\tau\Sigma_t)^{-1} \pi_t + P_t^\top \Omega_t^{-1} q_t \right]$.[^14][^13]
- **Robustness**: ambiguity set $\mathcal{U}_t = \{\mu: (\mu-\mu_t^{\text{BL}})^\top \Sigma_t^{-1} (\mu-\mu_t^{\text{BL}}) \le \delta_t\}$.
Worst‑case expected return of portfolio $w$:
$\inf_{\mu \in \mathcal{U}_t} \mu^\top w = \mu_t^{\text{BL}\top} w - \sqrt{\delta_t} \sqrt{w^\top \Sigma_t w}$.
- **Optimization**:
$\min_w w^\top \Sigma_t w - \lambda_\mu \left(\mu_t^{\text{BL}\top} w - \sqrt{\delta_t} \sqrt{w^\top \Sigma_t w}\right) + \lambda_T \text{TO}_t$ s.t. constraints.


### TEMA

- **State**: event memory $m_{i,t}$.
- **Transformer**: for tokens $x_{i,\tau}$, attention:
$a_{\tau,\kappa} = \frac{(Q x_{i,\tau})^\top (K x_{i,\kappa})}{\sqrt{d}} + b(\tau-\kappa)$ with positional bias $b$ decaying with lag;
$m_{i,t} = \sum_{\kappa} \text{softmax}_\kappa(a_{t,\kappa}) V x_{i,\kappa}$.[^9][^10]
- **Score‑to‑weight**:
$s_{i,t} = u^\top m_{i,t}$,
$w^{\text{raw}}_{i,t} = \frac{\exp(s_{i,t}/\tau)}{\sum_j \exp(s_{j,t}/\tau)}$.
- **Risk \& turnover**: same as earlier; add penalty $\lambda_s \sum_i s_{i,t}^2$ to avoid extreme logits.


### Rank‑Meta

- **State**: candidate weights $\{w^{(k)}_t\}$ and features $\phi_t$.
- **LTR model**: score $s^{(k)}_t = f(\phi_t, \psi(w^{(k)}_t))$, trained to minimize ranking loss $\mathcal{L}(\{s^{(k)}_t\}, \{y^{(k)}_t\})$.
- **Mixture**: $\beta^{(k)}_t = \exp(s^{(k)}_t)/\sum_j \exp(s^{(j)}_t)$, $w_t = \sum_k \beta^{(k)}_t w^{(k)}_t$.
- **Risk \& turnover**: as before; note that constraints can be enforced at candidate level as well as on mixture.


### Regime‑HMM

- **State**: hidden regimes $z_t$, posterior $\gamma_t$.
- **Forward update**: with transition matrix $A$ and emission likelihoods $p(r_t|z_t)$:
$\alpha_t(j) = p(r_t|z_t=j) \sum_i \alpha_{t-1}(i) A_{ij}$,
$\gamma_t(j) = \frac{\alpha_t(j)}{\sum_k \alpha_t(k)}$.
- **Allocation**: $w_t = \sum_r \gamma_t(r) w^{(r)}$.
- **Risk \& turnover**: as before; $w^{(r)}$ can encode regime‑specific risk appetite.


### Retrieval‑Causal BL

- **State**: representation $h_t = \Phi(x_t)$ trained via IRM; retrieved analogues $\mathcal{N}_t$.
- **IRM objective**:[^17]
$\min_{\Phi, w} \sum_{e\in \mathcal{E}} R_e(w \circ \Phi)$ s.t. $\nabla_w R_e(w \circ \Phi) = 0\ \forall e$, where environments $e$ are 2024 subperiods.
- **Views**:
$q_t = \sum_{w\in \mathcal{N}_t} \omega_w r_{w+1}$ with $\omega_w \propto \exp(-\|h_t - h_w\|^2 / \sigma^2)$; $P_t$ selects affected ETFs.
- **BL update**: same as DRO‑BL, but with view confidence scaled by IRM invariance metrics.


### OCO‑Ensemble

- **State**: weights $w_t$.
- **Loss** (per day): $\ell_t(w) = -\log(w^\top r_{t+1}) + \lambda_T \text{TO}_t + \lambda_\sigma (\sqrt{w^\top \Sigma_t w} - \sigma^*)_+^2$.
- **Mirror descent**:
$w_{t+1} = \arg\min_{w\in \Delta} \eta \nabla \ell_t(w_t)^\top w + D_\psi(w, w_t)$,
with $\psi(w) = \sum_i w_i \log w_i$ giving exponentiated gradient update.[^16][^15]
- **Risk \& turnover**: encoded in loss; constraints enforced on simplex $\Delta$.

F. Quantitative Comparison Table
--------------------------------

Subjective 0–10 scores (higher is better except risk columns subtracted in ROI). ROI uses the formula you specified, with pre‑computed values.


| Design | Track1 Fit | Track2 Fit | Sharpe Pot. | DD Control | Turnover Eff. | B‑list Robust. | Novelty | Math Depth | Interp. | Reprod. | Feasib. | Baseline Beat Prob. | Report Signal | Overfit Risk | Tool‑Dep Risk | Data‑Risk | Overall ROI |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| BSA‑RP | 9 | 7 | 8 | 8 | 7 | 8 | 7 | 8 | 9 | 8 | 7 | 8 | 9 | 4 | 4 | 2 | 8.54 |
| KG‑MoE | 7 | 9 | 8 | 7 | 6 | 7 | 9 | 8 | 7 | 7 | 6 | 7 | 9 | 6 | 3 | 3 | 7.95 |
| DRO‑BL | 9 | 8 | 7 | 9 | 8 | 8 | 8 | 9 | 8 | 8 | 7 | 7 | 8 | 3 | 3 | 2 | 8.64 |
| TEMA | 7 | 8 | 8 | 6 | 5 | 6 | 9 | 8 | 6 | 6 | 5 | 7 | 9 | 7 | 4 | 3 | 7.21 |
| Rank‑Meta | 7 | 8 | 7 | 7 | 7 | 7 | 7 | 7 | 7 | 8 | 8 | 8 | 7 | 5 | 4 | 2 | 7.64 |
| Regime‑HMM | 9 | 7 | 7 | 9 | 8 | 8 | 7 | 8 | 8 | 8 | 7 | 7 | 8 | 4 | 3 | 2 | 8.35 |
| Retrieval‑Causal BL | 8 | 8 | 7 | 7 | 6 | 7 | 9 | 8 | 8 | 6 | 6 | 7 | 9 | 5 | 5 | 3 | 7.72 |
| OCO‑Ensemble | 8 | 8 | 7 | 7 | 7 | 9 | 8 | 8 | 7 | 9 | 8 | 8 | 8 | 3 | 2 | 2 | 8.50 |

(Values are relative; you can adjust after initial prototyping.)

G. Competition Score vs Research/Award Score
-------------------------------------------

Using derived sub‑scores:

- **Competition Score** (Sharpe, drawdown, turnover, B‑list robustness, baseline‑beat, track fit, penalized by overfit):
    - Highest: **DRO‑BL (~6.5)**, **OCO‑Ensemble (~6.17)**, **BSA‑RP (~6.0)**, **Regime‑HMM (~6.0)**.
    - Lower: TEMA (~3.17) due to higher overfit risk and turnover.
- **Research/Award Score** (novelty, math depth, interpretability, reproducibility, report signal):
    - Top cluster: **BSA‑RP (~8.2)**, **DRO‑BL (~8.2)**, **KG‑MoE (~8.0)**, **Retrieval‑Causal BL (~8.0)**, **OCO‑Ensemble (~8.0)**.
    - Slightly lower: TEMA (~7.6), Regime‑HMM (~7.8), Rank‑Meta (~7.2).

**Quadrants:**

- **High competition + high research:**
    - **DRO‑BL, BSA‑RP, OCO‑Ensemble, Regime‑HMM.** These are your strongest all‑round bets.
- **High competition + lower research:**
    - None clearly; perhaps a pure tuned OCO with minimal news would sit here.
- **Low competition + high research:**
    - **Retrieval‑Causal BL, KG‑MoE, TEMA** – especially Retrieval‑Causal BL and KG‑MoE are strong awards candidates even if Sharpe isn’t top.
- **Low competition + low research:**
    - Designs we rejected (Vanilla LLM trader, news‑only sentiment) sit here conceptually.

From a shared‑task paper standpoint, **Retrieval‑Causal BL, KG‑MoE, TEMA, and BSA‑RP** offer the richest qualitative narratives; DRO‑BL and OCO‑Ensemble provide robust quantitative anchors.

H. Baseline-Beating and Ablation Plan
--------------------------------------

**Baselines to implement (both tracks where relevant):**

1. **Equal weight:** $w_i = 1/N$.
2. **Inverse volatility:** $w_i \propto 1/\hat{\sigma}_i$ using past 60‑day vol.
3. **Momentum‑only:** weights proportional to recent 20‑day or 60‑day returns, with caps.
4. **Sector trend‑following:** Track 2 top‑k sectors by trend; equal weight among them.
5. **Persistence / low‑turnover:** only rebalance when state changes beyond threshold (e.g., vol or drawdown triggers).
6. **Rule‑based macro rotation:** defensive vs offensive portfolios chosen from simple signals (e.g., index trend, bond vs equity).
7. **News‑sentiment only:** aggregate sentiment per ETF and sign‑tilt weights with small magnitudes.[^8]
8. **S1 quant core (approximation):**
    - Track 1: inverse‑vol/momentum/breadth/defensive allocator (we can build a reasonable reproduction).
    - Track 2: sector trend‑following top‑k allocator.

**Each final design must, at minimum:**

- Beat *or* match S1 on 2024→2025 walk‑forward **Sharpe net of friction** without much worse turnover.
- Show stability across 2024 subwindows (e.g., Q1, Q2–Q3, Q4) in Sharpe and drawdown.
- Demonstrate incremental value over a strong “quant‑only” variant of the same design (e.g., BL without LLM views vs DRO‑BL).

**Ablation axes (applied per design, but systematically):**

- **No LLM:** Replace any LLM‑derived features with simple textual heuristics or drop them.
- **No news:** Use price data only.
- **No memory:** Remove temporal transformers/filters/belief states; use static factors.
- **No risk control:** Remove volatility/ drawdown constraints to see impact.
- **No turnover control:** Allow free rebalancing; quantify cost impact.
- **No graph / retrieval / regime modules:** For KG‑MoE, Retrieval‑Causal and Regime‑HMM, drop those components and compare.
- **Baseline fallback only:** Use only the best baseline (e.g., S1) inside Rank‑Meta or OCO ensemble.
- **Quant‑only vs LLM‑only vs mixed:** E.g., for DRO‑BL, BL with hand‑crafted vs LLM‑derived views; for BSA‑RP, factor update with vs without news.
- **2024‑tuned vs 2025‑tuned:** show that retuning on 2025 worsens B‑list risk (simulate via 2024 subwindows).

These ablations should be run locally using `dataloader_eval.py` on 2024/2025 data, logging Sharpe, drawdown, turnover, and stability.

I. Hidden B-List Robustness Audit
---------------------------------

Key 2026 risks and how designs respond:

- **Regime shift (macro and sector):**
    - *Best prepared:* Regime‑HMM (explicit regimes), OCO‑Ensemble (online updates), BSA‑RP (belief updating), DRO‑BL (robustness).
    - *More fragile:* TEMA (may overfit event patterns), KG‑MoE (graph edges may stale), Retrieval‑Causal BL (analogues may fail for novel events).
    - Mitigation: use multiple environments in training (sub‑periods of 2024) and penalize over‑reliance on rare patterns (IRM, shrinkage).
- **Prompt / LLM instability:**
    - Designs with LLM only in offline pre‑processing (event tokens, metadata) and with cached outputs (TEMA, Retrieval‑Causal BL, BSA‑RP) are safer.
    - Avoid online API calls in B‑list; pin models and prompts; dump LLM outputs to JSON as part of pipeline.
- **Dependency risk (Docker \& infra):**
    - OCO‑Ensemble, Regime‑HMM, basic BL components are “lightweight” and easy to containerize.
    - Heavy transformers/GNNs require careful version pinning and resource constraints; consider CPU‑friendly SSM variants or small models.
- **Macro event novelty:**
    - Retrieval‑Causal BL using IRM representations and regime‑agnostic features may generalize better than pattern‑matching event types.
    - Belief‑state models with conservative priors (BSA‑RP) may avoid catastrophic over‑reaction.
- **Sector label drift and ETF changes:**
    - KG‑MoE should rely on robust, broad sector definitions rather than fine‑grained labels; maintain fallbacks when mapping fails.
    - All designs should degrade gracefully to price‑only factors when sector mapping is missing.
- **Data compliance \& leakage:**
    - Strictly call official DataLoader and avoid loading raw CSVs directly in the agent loop; any offline training must use only 2024/2025 and be demonstrably separate from B‑list evaluation.
    - For retrieval designs, ensure that “future windows” relative to each day are not used as analogues.

Overall, **DRO‑BL, BSA‑RP, Regime‑HMM, and OCO‑Ensemble** look safest for B‑list robustness; **KG‑MoE, TEMA, and Retrieval‑Causal BL** have higher upside but also higher regime‑shift and complexity risk.

J. Implementation Roadmap
-------------------------

**Phase 0R: Source/data reset (1–2 days)**

- Clone official repo; verify environment using `requirements.txt` and `start_server.py`.
- Run sample backtest with provided demo agent to confirm DataLoader/backtest behaviour.
- Build a small evaluation harness over `dataloader_eval.py` for offline 2024/2025 tests.

**Phase 1R: Official starter reproduction (2–3 days)**

- Reproduce the demo LLM‑based agent on short 2025 spans; log allocations and backtest results.
- Implement and log all baseline strategies (equal‑weight, inverse‑vol, momentum, sector trend, persistence, rule‑based macro).
- Confirm Sharpe/drawdown/turnover calculations matched with official metrics.

**Phase 2R: Baselines + S1 reproduction (3–5 days)**

- Build strong S1‑style quant core for each track:
    - Track 1: inverse‑vol + momentum + defensive tilt vs bonds/gold.
    - Track 2: sector trend‑following top‑k with caps.
- These become reference points for “baseline beating”.

**Phase 3R: First innovative prototypes (5–10 days)**

- Implement **DRO‑BL** (without robustness initially) and **OCO‑Ensemble** (simple experts).
- In parallel, implement a light **Regime‑HMM** or simple 2‑regime switching.
- Evaluate 2024→2025; pick the most promising of these as the quantitative backbone.

**Phase 4R: Full comparison \& mid‑tier innovation (10–15 days)**

- Add **BSA‑RP** (Kalman‑style belief state with basic news features).
- Implement **Rank‑Meta** over baselines and early quant designs.
- Begin offline LLM preprocessing (event tokens, metadata) for news; cache outputs.

**Phase 5R: High‑novelty modules (15–20 days)**

- Implement **KG‑MoE** and **TEMA**, using precomputed event tokens / node features.
- Implement **Retrieval‑Causal BL** with simple retrieval first, then IRM if time allows.
- Run ablations across all designs on 2024 and 2025.

**Phase 6R: A‑list package (5–7 days)**

- Select 2–3 primary submissions per track (likely one robust quant, one belief/BL hybrid, one high‑novelty).
- Produce clean Docker images with pinned dependencies and reproducible scripts.
- Generate/export logs, decision traces, and ablation reports for A‑list.

**Phase 7R: B‑list hardening (5–7 days)**

- Remove any online, non‑deterministic LLM calls from B‑list runtime; switch to cached features.
- Stress‑test for long horizon, out‑of‑sample 2025; ensure memory limits and runtime are safe.
- Write the system‑report story; decide which design(s) to highlight for award narrative.

This roadmap is feasible for one strong student if scope is reduced (e.g., focus on DRO‑BL, BSA‑RP, and one high‑novelty design) or for a small team to cover all eight designs.

K. Final Recommendation
-----------------------

**1. Best performance‑first design**

- **DRO‑BL** is the most promising performance‑first candidate: robust, mathematically grounded, aligns with ETF allocation practice, and can integrate news without over‑reliance on LLMs.
- For Track 1, pair DRO‑BL with **Regime‑HMM** as a regime overlay (e.g., adjusting risk appetite by regime).
- For Track 2, consider **KG‑MoE** as a complement if time permits, but DRO‑BL alone is already strong.

**2. Best research/award design**

- **Retrieval‑Causal BL** is the most award‑oriented: analogue‑market retrieval + IRM + BL yields a highly novel, theory‑informed architecture with clear causal and retrieval narratives.
- Close second: **KG‑MoE** and **TEMA**; both are architecturally rich and visually appealing but more fragile.

**3. Best one‑student design**

- **BSA‑RP** is the best single‑researcher target: manageable complexity, interpretable belief state, clear risk‑parity math, and strong narrative value.
- A student could realistically implement BSA‑RP + a simpler version of DRO‑BL within the timeline.

**4. Best Track 1 design**

- **DRO‑BL + Regime‑HMM overlay**, possibly with a light BSA‑RP to generate macro views, is the best macro‑asset allocator.
- If time is short, DRO‑BL alone should be the Track 1 workhorse.

**5. Best Track 2 design**

- **KG‑MoE** (sector graph + MoE) combined with a simpler BL or BSA‑RP‑style sector view layer is best suited for sector rotation.
- TEMA is a strong alternative or complementary module for sector news.

**6. Designs to reject (for now)**

- **Vanilla LLM trader**, **news‑only sentiment**, and a full **DRL agent** should remain as baselines or deferred experiments; they are either brittle, weakly interpretable, or hard to harden for B‑list.

**7. Exact first implementation target**
If you start tomorrow with limited bandwidth, I recommend:

- Implement **DRO‑BL** (Track 1 + Track 2) and **BSA‑RP** (Track 1 emphasis) as your first serious systems.
- In parallel, build solid baselines and S1 core reproductions to quantify gains.

**8. Exact fallback if novelty underperforms**

- If KG‑MoE, TEMA, or Retrieval‑Causal BL do not deliver robust Sharpe on 2025, fall back to:
    - **Primary submission:** DRO‑BL + Regime‑HMM + Rank‑Meta meta‑allocator over DRO‑BL, BSA‑RP, and S1.
    - **Secondary (“award story”) submission:** A simplified **BSA‑RP** with very strong interpretability and ablation results.

This mix maximizes your probability of strong Sharpe/drawdown/turnover performance *and* positions you for selection in the shared‑task system report as a team that contributed mathematically structured, interpretable, and reproducible LLM‑based investment advisor agents tailored to the Chinese ETF market.[^2][^15][^3][^17][^5]
<span style="display:none">[^24][^25][^26][^27][^28][^29][^30][^31][^32][^33][^34][^35][^36][^37][^38][^39][^40][^41][^42][^43]</span>

<div align="center">⁂</div>

[^1]: http://tcci.ccf.org.cn/conference/2026/shared-tasks/

[^2]: https://arxiv.org/pdf/2603.22305.pdf

[^3]: https://www.computer.org/csdl/journal/tk/2025/06/10902141/24AYE7adgTm

[^4]: http://ieeexplore.ieee.org/document/10902141/

[^5]: https://www.computer.org/csdl/proceedings-article/ccnis/2025/724700a555/2eBN7kGPxYI

[^6]: https://arxiv.org/html/2503.09647v4

[^7]: https://arxiv.org/html/2605.19337v1

[^8]: https://pmc.ncbi.nlm.nih.gov/articles/PMC11033520/

[^9]: https://www.sciencedirect.com/science/article/pii/S0957417424004032

[^10]: https://dl.acm.org/doi/10.1145/3746252.3761246

[^11]: https://dl.acm.org/doi/abs/10.1007/s10844-024-00851-2

[^12]: https://arxiv.org/html/2404.00424v1

[^13]: https://people.duke.edu/~charvey/Teaching/BA453_2006/Black_Litterman_Global_Portfolio_Optimization_1992.pdf

[^14]: https://cims.nyu.edu/~ritter/kolm2021black.pdf

[^15]: https://isl.stanford.edu/~cover/portfolio-theory.html

[^16]: http://proceedings.mlr.press/v125/van-erven20a/van-erven20a.pdf

[^17]: https://arxiv.org/abs/1907.02893

[^18]: https://bayesgroup.github.io/bmml_sem/2019/Kodryan_Invariant%20Risk%20Minimization.pdf

[^19]: https://arxiv.org/abs/2510.24402

[^20]: https://ideas.repec.org/a/jfr/afr111/v10y2021i4p34.html

[^21]: https://www.sciencedirect.com/science/article/pii/S2666764926000081

[^22]: https://www.emergentmind.com/topics/market-regime-filtering

[^23]: https://openreview.net/pdf/7d89ed6d7e661bfee901c946316b1e319b0a296d.pdf

[^24]: https://easychair.org/cfp/FINLLM-IJCAI2026

[^25]: https://github.com/NLP2CT/NLPCC-2026-Task10-Science

[^26]: https://quantumobile.com/portfolio/llm-based-financial-investment-advisory-chatbot/

[^27]: https://yjump.github.io

[^28]: https://github.com/NLP2CT/NLPCC-2026-Task6-Detection/actions

[^29]: https://arxiv.org/html/2603.22305v1

[^30]: https://github.com/splash-li/NLPCC2026-Shared-Task-4/

[^31]: https://github.com/ResearAI/NLPCC-2026-Task9-AISB

[^32]: https://pmc.ncbi.nlm.nih.gov/articles/PMC12421730/

[^33]: https://github.com/NLP2CT/NLPCC-2026-Task6-Detection

[^34]: https://aws.amazon.com/blogs/machine-learning/part-3-building-an-ai-powered-assistant-for-investment-research-with-multi-agent-collaboration-in-amazon-bedrock-and-amazon-bedrock-data-automation/

[^35]: https://openreview.net/group?id=ccf.org%2FNLPCC%2F2026%2FShared_Tasks

[^36]: https://github.com/patrick-tssn/NLPCC-2022-Shared-Task-4/issues

[^37]: https://global.fujitsu/en-cn/insight/tl-aiagents-financial-industry-20250418

[^38]: https://www.cxoadvisory.com/investing-expertise/managing-ai-researchers/

[^39]: https://arxiv.org/abs/2511.13251

[^40]: https://www.youtube.com/watch?v=g0b8bQUIqsc

[^41]: https://huggingface.co/papers?q=financial+agents

[^42]: https://www.linkedin.com/posts/william-mann-cfa_the-llm-revolution-in-quantitative-investment-activity-7295424277619634176-2Gu5

[^43]: https://www.youtube.com/watch?v=K9rBFb4xC54

