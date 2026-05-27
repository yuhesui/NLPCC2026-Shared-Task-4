# NLPCC 2026 Shared Task 4 Architecture Research Report

## A. Official Task Constraints and Research Opportunity

The official task is a daily-frequency asset-allocation competition for the Chinese market. It has two tracks: **Track 1: Macro-Asset Allocation**, over a public macro ETF/index pool of roughly 11 instruments, and **Track 2: Sector-Rotation Allocation**, over a larger public sector-ETF pool defined in the starter kit. Agents receive a daily **Top-20 financial hot-news feed** and historical price data, then generate daily rebalancing decisions under a standardised backtesting engine with **0.01% transaction friction**. The public split is **2024** for construction/training, **2025** for the public A leaderboard, and **2026-01-01 to 2026-06-01** for the private B leaderboard, which is run centrally by the organisers. The official README also states that creative or especially informative system reports may be selected into the shared-task paper even beyond the top finishers. citeturn45view0turn45view1

The data and timing rules are unusually constraining in a way that should strongly shape system design. The dataset documentation and loader logic explicitly enforce that, at decision time, agents may use **full history from prior trading days plus only the current-day open**, while the current day’s **close, high, low, change, and return** are hidden; same-day news is truncated to items published **before 15:00**. The organisers also require that participating systems, including models, extra datasets, and knowledge bases, must be limited to resources available **before 2026**, and that submitted code must be reproducible enough to run under central B-list evaluation. citeturn45view1turn8view3turn5view3turn5view4turn9view7turn9view8turn10view0turn10view4

Operationally, the executable API matters as much as the abstract task description. The public starter materials describe “daily rebalancing instructions”, but the actual server schema does **not** accept direct target weights. It accepts **buy trades by cash amount** and **sell trades by current-holding percentage**; execution is at the **same day’s closing price**, there is **no minimum lot size**, and the trade engine applies the 0.01% cost on both buys and sells. In addition, the backtester processes **buys before sells**, so a design cannot assume that planned same-day sells will finance same-day buys. That single implementation detail makes exact target-weight tracking non-trivial and strongly rewards low-turnover or staged-rebalance systems. citeturn45view1turn44view0turn12view1turn42view0

That leads to the main research opportunity. The official starter agent is a three-stage LLM chain that performs news summarisation, sentiment analysis, and then trade generation through `ChatOpenAI`-style calls, which is useful as a baseline but not yet a mathematically serious allocator. For competition-grade systems, the winning direction is not “LLM decides the portfolio”; it is to use the LLM narrowly and reproducibly for **event extraction, denoising, mapping, or confidence estimation**, while the actual allocation engine is a transparent quantitative module such as a robust optimiser, graph model, filtered latent-state model, retrieval-based meta-allocator, or online convex optimiser. citeturn21view8turn22view0turn45view1

Several code-level anomalies deserve conservative handling. The official prose says the main setting uses Top-20 news, but server-side defaults still fall back to `top_rank=10` unless the config overrides it; fortunately, the demo backtest script sets the demo default to `20`, so teams should set that explicitly. There is also a mismatch between `lookback_days` and `pre_k_days`: the demo client correctly calls the `/historical_prices` endpoint with `lookback_days`, but `get_day_data()` internally uses `pre_k_days` when constructing its embedded `market_data`. Most importantly, the public anti-leakage prose conflicts with some starter-server exposures: `/market_data` returns same-day full price fields, and `get_portfolio_status()` inserts current-day `close` prices for held assets into the portfolio payload. A fully compliant system should therefore **ignore `/market_data` and ignore `portfolio.holdings[*].price`**, and instead rely only on the leakage-safe historical-price interface plus timestamp-safe news. Finally, the README says ranking is driven by Sharpe, turnover categories, cumulative return, and drawdown, whereas the public `finish()` result object exposed in the starter code contains only total return, final value, and annualised return; teams should therefore compute Sharpe, drawdown, and turnover themselves from saved logs rather than trusting the minimal public result object. citeturn45view1turn42view0turn24view0turn43view0turn43view5turn43view6turn11view1turn12view1turn9view5turn11view2turn11view4

## B. Research Source Ledger

| Source | Type | What it contributes | Reliability | How it affects design |
|---|---|---|---|---|
| Repository root README citeturn45view0 | Official repo | Task framing, tracks, friction, splits, FAQ, deadlines, paper-selection note | Very high | Sets hard competition constraints and shows report creativity matters |
| `NLPCC_tasks/README.md` citeturn45view1 | Official repo | ETF pools, split dates, backtest rules, APIs, reproducibility requirements | Very high | Forces long-only, close-price execution, central-eval reproducibility |
| `dataset/README.md` citeturn8view3 | Official repo | Dataset schema, price fields, same-day-open-only exposure, 15:00 truncation | Very high | Makes leakage-safe engineering non-negotiable |
| `data_loader.py` findings citeturn5view3turn5view4 | Official repo | Same-day news truncation and source handling | Very high | Makes event time a core modelling object |
| `backtest.py` findings citeturn12view0turn12view1turn42view0 | Official repo | Trade sequence, close-price execution, buy-before-sell, state delivery | Very high | Requires a target-weight-to-trade adapter and favours low-turnover designs |
| `dataloader_eval.py` findings citeturn9view5turn9view7turn9view8turn10view0turn10view4 | Official repo | Concrete anti-leakage implementation, historical slicing, hidden same-day fields | Very high | Encourages reuse of official loader logic and strict feature whitelists |
| `demo_backtest.py` citeturn24view0turn24view1turn24view2turn24view4turn43view0 | Official repo | Public pools, demo config, explicit `historical_prices` call, default Top-20 demo | Very high | Suggests the correct client architecture for reproducible runs |
| `models/backtest.py` citeturn44view0 | Official repo | Exact trade schema and config defaults | Very high | Confirms there is no direct weight API; weight translation is compulsory |
| Starter LLM agent code citeturn21view8turn22view0turn22view5 | Official repo | Reveals the public LLM baseline structure | High | Useful as a rejected control, not as the main architecture |
| FinMem citeturn27search0turn39search8 | Research paper | Layered memory for LLM-based trading agents | Medium-high | Motivates memory-based event-state architectures, but should be quantised and narrowed |
| FinAgent citeturn27search8turn27search15 | Research paper | Tool-augmented multimodal financial agent design | Medium-high | Supports modular tool use, not unconstrained generation |
| LLMFactor citeturn40search0turn40search8 | ACL/Findings paper | Structured factor extraction from news using prompting | High | Strong evidence for “LLM as extractor, quant model as allocator” |
| Trade the Event citeturn28search18 | arXiv / event-trading paper | Event detection beats raw sentiment framing for tradable signals | Medium-high | Supports event extraction over generic sentiment pipelines |
| Stock embeddings from news + price history citeturn28search17turn30search0 | ACL paper | Joint text-price representation learning | High | Useful for retrieval, analogue search, and score regularisation |
| Temporal Relational Ranking citeturn29search0turn29search12 | TOIS/KDD line | Learning-to-rank with temporal graph convolution | High | Strong template for Track 2 graph-rank models |
| MDGNN citeturn29search13 | AAAI paper | Multi-relational dynamic graphs for finance | High | Encourages multi-edge sector/ETF graphs with dynamic news activations |
| Black–Litterman citeturn31search0turn31search11 | Foundational portfolio paper | Bayesian blending of equilibrium returns and views | Very high | Natural backbone for structured-news views |
| Robustifying Conditional Portfolio Decisions via Optimal Transport citeturn31search1 | Research paper | Side-information-aware DRO portfolio optimisation | High | Gives a principled route from news covariates to robust weights |
| Distributionally Robust Mean-Variance Portfolio Selection | Research paper | Wasserstein-regularised mean-variance reformulation | High | Supports robust active tilts under estimation error citeturn32search13 |
| Data-driven DRO risk parity citeturn32search16 | Research paper | Robustification of risk parity under distribution uncertainty | High | Useful for low-fragility competition-first designs |
| Online Portfolio Selection survey citeturn31search3 | Survey | OPS taxonomy and regret-based framing | High | Grounds online-learning/meta-allocation designs |
| Efficient and Near-Optimal Online Portfolio Selection citeturn31search2turn37search6 | Research paper | Modern universal-portfolio style regret guarantee | High | Supports low-fragility online meta-updates |
| Semi-Universal Portfolios with Transaction Costs citeturn37search7turn37search11 | IJCAI paper | Transaction-cost-aware OPS | High | Important because the official engine charges friction and penalises churn |
| Smart Predict, then Optimise citeturn36search0turn36search18 | Management Science/optimisation | Decision-focused learning objective | Very high | Ideal for rankers or meta-allocators evaluated by realised portfolio utility |
| Hamilton regime-switching and HMM allocation papers citeturn35search4turn33search0turn35search5 | Foundational + applied finance | Hidden-state regime modelling for asset allocation | High | Motivates regime-posteriors rather than static signal aggregation |
| Hidden Gaussian drift with expert opinions citeturn35search2 | Research paper | Kalman filtering with noisy expert views | High | Excellent mathematical template for news-as-expert-opinion |
| IRM and causal stock-prediction perspective citeturn33search2turn33search10 | Causal ML papers | OOD invariance and spurious-correlation control | High | Supports causal/news invariance modules for hidden 2026 robustness |
| TFT, Mamba, Transformer-XL, Attention, Switch Transformer, Toolformer citeturn30search2turn30search7turn34search0turn34search1turn34search2turn34search3 | Foundational architecture papers | Attention, recurrence, selective state spaces, sparse routing, tool use | Very high | Provide architecture primitives that can be repurposed quantitatively |

## C. Candidate Design Universe

| Candidate | Core idea | Main engine | LLM role | Likely track fit | Keep / merge / reject / defer | Reason |
|---|---|---|---|---|---|---|
| Starter three-stage LLM trader | Summarise news, infer sentiment, emit trades | Prompted agent chain | Full decision path | Both, weakly | Reject as main design | Too prompt-sensitive, too hard to reproduce, weak mathematical story |
| Equal-weight / inverse-vol | Pure price-only baseline | Static allocation | None | Both | Keep as baseline only | Necessary benchmark, not award-worthy |
| Momentum / sector trend S1 | Trend + breadth + defensive sleeves | Hand-crafted quant rules | None | Strong both | Keep as baseline only | Hard to beat; becomes the minimum credible hurdle |
| TEMA-RP | Event tokens with decayed memory and attention-to-ETF matching | Transformer-style memory + QP | Event extraction only | T1 medium, T2 good | Keep | Strong narrative and modular ablations |
| HGF-MPC | News as noisy expert opinions over latent drift/regime | Kalman/HMM + MPC | Opinion extraction | T1 very strong | Keep | Competition-grade and mathematically clean |
| KG-MoE | ETF/sector/news graph with regime-routed experts | Dynamic GNN + sparse MoE | Entity/sector mapping | T2 very strong | Keep | Best graph-native Track 2 candidate |
| DRO-BL-RP | Structured views blended with equilibrium and robust risk budget | BL + DRO + risk parity | View extraction only | T1 very strong, T2 good | Keep | Best performance-first candidate |
| CEVA-KF | Typed events injected into a causal latent-factor model | SCM + invariance + Kalman smoothing | Event extraction | Both, especially report value | Keep | Excellent paper narrative if executed carefully |
| ARMOR-SPO | Retrieve 2024 analogues, ensemble base allocators, update online | kNN retrieval + SPO+ + OMD | Retrieval query formation / event embedding | Both | Keep | Strong balance of robustness and feasibility |
| Bandit-RP router | Choose among sleeves with cost-aware bandit | EXP/Hedge + RP sleeves | None or minimal | Both | Merge into ARMOR | Better as the online-update layer inside a retrieval meta-model |
| News-sentiment PPO | Sentiment feature added to DRL | PPO / actor-critic | Sentiment scoring | Both | Reject / defer | Hard to stabilise under one-student constraints and hidden regime shift |
| End-to-end graph RL | Joint graph representation and RL decision layer | GNN + RL | Optional | T2 | Defer | Interesting, but high implementation and overfit risk |
| Pure RAG summariser | Retrieve similar news then ask an LLM for weights | Generic RAG | Full decision | Both | Reject | Weak mathematical depth; too close to “LLM says buy/sell” |
| Pure factor-mining via LLM | Ask LLM to invent factors and trade them | Prompt mining + ranking | Factor generation | Both | Defer | Attractive report angle, but a second-cycle research branch, not first implementation |

The practical consolidation is straightforward. For actual implementation priority, the serious set is **DRO-BL-RP**, **ARMOR-SPO**, **HGF-MPC**, **CEVA-KF**, **TEMA-RP**, and **KG-MoE**. That set jointly covers every family the task brief asked to consider: belief-state, graph, robust optimisation, structured event extraction, meta-allocation, regime-switching, retrieval, online learning, causal reasoning, and transformer-inspired design.

## D. Five to Eight Final Design Blueprints

### TEMA-RP

**One-sentence thesis.** Convert daily Chinese financial news into typed event tokens, accumulate them in a leakage-safe decayed key-value memory, and let a lightweight transformer-style attention layer map those event memories into ETF-level active-return forecasts, with final weights produced by a cost-aware risk allocator.

**Novelty claim.** This is more novel than a pure LLM allocator because the LLM never controls weights; more novel than momentum because it models persistent event state rather than recent returns alone; more novel than sentiment because it stores typed event evolution rather than one-shot polarity; and more novel than standard RAG because it uses trainable event-to-ETF attention and half-life dynamics rather than document retrieval alone. It is directly motivated by recent financial-memory work, but repackaged into a compact, reproducible, non-oracular allocator using transformer internals, segment-style recurrence, and decayed event memory. citeturn27search0turn39search0turn34search0turn34search2turn30search7

**Mathematical state representation.** For each asset \(i\), the state is an event memory vector \(m_{i,t}\in\mathbb{R}^d\), plus price-state features \(z_{i,t}\) and a confidence scalar \(c_{i,t}\). Each news item is transformed into a typed event token \((k_e,v_e,\lambda_e,\rho_e)\): key, value, half-life, and reliability. The daily market belief is \(x_t=\{m_{i,t},z_{i,t},c_{i,t}\}_{i=1}^N\).

**Update rule.** Daily, the memory is updated by attention-weighted event insertion with exponential decay. The design should use source weight, recency, and event novelty in the update so that repeated headlines do not dominate. The practical update is deterministic once event tuples are extracted, which is important for B-list reproducibility.

**LLM role.** Only event extraction and denoising: source-normalised summaries, topic typing, dependency target, direction, horizon, and confidence.

**Non-LLM engine.** A small transformer-style or SSM-style event-memory encoder with explicit decay, followed by a convex portfolio layer.

**Portfolio construction.** Convert asset scores to expected-return tilts, divide by predicted volatility, cap concentrations, and solve a long-only quadratic programme with a turnover penalty and a drawdown throttle. The design should include a cash sleeve; in this task, cash is not an embarrassment but a real robustness control because exact same-day rotations are operationally awkward under the buy-first engine. The fallback baseline is inverse-volatility plus medium-term momentum. Official trade translation must stage heavy rotations over multiple days if current cash is insufficient. citeturn45view1turn44view0turn42view0

**Data use and leakage safety.** Use only official historical prices, prior-day closes, current-day open, and same-day news published before 15:00. Ignore same-day close-like exposures in `market_data` and `portfolio.holdings.price`. Build event vocabulary and encoder on 2024; use 2025 as a strict pseudo-out-of-sample stress test; exclude 2026 information from training, retrieval stores, and prompt examples. citeturn45view1turn8view3turn10view0turn12view1

**Track fit.** Track 1: **7/10**. Track 2: **8/10**. It is more naturally useful where policy and theme news propagate differently across sectors.

**Implementation plan.** MVP: deterministic event schema + decayed average memory + shrinkage covariance allocator, about **10 student-days**. Strong version: multi-head attention, event half-life calibration, staged rebalancer, about **22 student-days**. Report-ready version: memory visualisation, attention heatmaps, failure-case narrative, about **30 student-days**.

**Failure modes.** Event over-fragmentation; redundant headlines saturating memory; prompt drift in event tagging; excessive rotation after dense news days; weak marginal gain against a good trend-following baseline.

**Ablation plan.** No LLM extraction; no memory bank; average pooling instead of attention; no news; no turnover penalty; no drawdown throttle; quant-only fallback; LLM-only rejected control; 2024-tuned versus 2025-tuned.

**Paper / award narrative.** Even if it does not top Sharpe, this is one of the strongest “LLM systems” papers because it repurposes attention, recurrence, and selective forgetting as explicit financial event memory rather than treating the LLM as a black-box trader.

### KG-MoE

**One-sentence thesis.** Encode ETFs, sectors, policy themes, and news entities in a dynamic knowledge graph, then let a regime-routed mixture-of-experts model produce sector scores from graph message passing and cross-sector spillovers.

**Novelty claim.** This is materially different from sentiment trading and generic RAG because the object being modelled is not text but a **relation system**: sector co-movement, policy beneficiaries, substitute sectors, supply-chain adjacency, and defensive/risk-on links. It is also more competition-relevant than generic graph stock prediction because the target is **ETF allocation under central evaluation** rather than stock picking. The design stands on strong graph-ranking literature and MoE routing ideas, with a clear Track 2 paper story. citeturn29search0turn29search13turn34search1

**Mathematical state representation.** Let \(G_t=(V,E_t)\) be a time-varying multi-relational graph with ETF nodes, theme nodes, and news-event nodes. Node states are \(h_{v,t}\), relation-specific edges have weights \(a_{uvr,t}\), and the regime-router state is \(r_t\) with mixture weights \(\pi_t\).

**Update rule.** Daily news activates nodes and edges; message passing updates node embeddings; a router maps the day’s macro/price/news state into expert weights. One expert may specialise in policy-beta sectors, another in cyclical trend continuation, another in defensive spillovers, and another in mean-reversion after over-reaction.

**LLM role.** Entity normalisation, sector/theme mapping, and relation labelling from free-form Chinese news. The LLM never emits weights.

**Non-LLM engine.** Multi-relational GNN plus sparse MoE routing, optionally with a simple HMM-based regime posterior feeding the router.

**Portfolio construction.** Use graph-implied ETF scores, penalise portfolios that violate graph smoothness or sector concentration, and impose stronger per-name caps than in Track 1 because correlated sector ETFs can quietly create hidden concentration. A useful refinement is a graph-Laplacian regulariser so neighbouring defensive sectors are not assigned violently inconsistent active tilts absent strong evidence.

**Data use and leakage safety.** Prices come only from the safe historical interface; graph structure is built from pre-2026 sector taxonomies and 2024 training data. No external post-2025 sector ontology updates should be introduced. The graph should be static in schema but dynamic in edge activation to preserve reproducibility.

**Track fit.** Track 1: **6/10**. Track 2: **9/10**. This is the most naturally sector-rotation-native architecture in the set.

**Implementation plan.** MVP: ETF-only graph with hand-built sector and substitution edges, **12 student-days**. Strong version: event nodes, dynamic edge weights, and router, **24 student-days**. Report-ready version: graph visualisations, edge-attribution analysis, and regime-specific expert narratives, **34 student-days**.

**Failure modes.** Brittle graph specification; relation noise from event mapping; MoE expert collapse; overfitting to a small sector universe; difficult debugging.

**Ablation plan.** No graph; static graph only; no router; no news activation; no turnover penalty; no group caps; quant-only ranker; naïve GNN without multi-relational edges.

**Paper / award narrative.** This is the most visually and conceptually distinctive Track 2 paper: policy/news flows become graph activations, and sector allocation becomes graph reasoning instead of mere sentiment scoring.

### DRO-BL-RP

**One-sentence thesis.** Treat news as uncertain portfolio “views”, combine them with equilibrium and price-based priors through Black–Litterman, and allocate through a distributionally robust, risk-parity-anchored optimiser.

**Novelty claim.** This is not an LLM trader. It is a fully quantitative portfolio-construction engine whose only optional LLM function is to express news in the mathematically natural language of **views with confidences**. It is more rigorous than a momentum strategy because it fuses equilibrium, risk, and views; more robust than standard mean-variance because it hedges estimation error; and more reproducible than any prompt-heavy planner. It aligns almost perfectly with this task’s evaluation priorities: Sharpe, drawdown, turnover discipline, and B-list robustness. citeturn31search0turn31search1turn32search13turn32search16

**Mathematical state representation.** The state is \((\Pi_t,\Sigma_t,P_t,q_t,\Omega_t,\epsilon_t)\): equilibrium prior returns, robust covariance, a view-loading matrix, view values, view-confidence matrix, and ambiguity radius. News is converted into view candidates such as “policy easing favours semiconductors relative to banks” or “risk-off increases bond and gold attractiveness”.

**Update rule.** Prices update \(\Sigma_t\) and any prior-return proxy; news updates the view set and confidence matrix; the BL posterior is then robustified by a Wasserstein or regularised ambiguity term, and the final portfolio is anchored to a risk-parity baseline so that the active tilts stay stable.

**LLM role.** Optional and narrow: structured extraction of signed relative views, not direct allocation.

**Non-LLM engine.** Black–Litterman posterior, robust covariance estimation, distributionally robust optimisation, and risk-parity anchoring.

**Portfolio construction.** Start from a low-fragility anchor \(w^{RP}\), compute a robust active portfolio \(w^{act}\), and blend the two with a confidence-scaled coefficient. Impose per-asset caps, cash bounds, drawdown throttles, and an \(L_1\) turnover penalty. This design is unusually well matched to the task’s awkward trade semantics because it naturally produces **small, confidence-weighted active tilts** rather than violent reallocations. citeturn45view1turn44view0turn42view0

**Data use and leakage safety.** Entirely compatible with safe public data. It can be run with no LLM at all by replacing event views with rule-based dictionaries. That makes it the least fragile design under central B-list execution.

**Track fit.** Track 1: **9/10**. Track 2: **7/10**. Best macro candidate overall.

**Implementation plan.** MVP: inverse-vol anchor + shrinkage covariance + rule-based views, **7 student-days**. Strong version: full BL posterior + DRO + dynamic cash sleeve, **15 student-days**. Report-ready version: view attribution, risk-contribution charts, scenario analysis, **22 student-days**.

**Failure modes.** Weak view extraction; over-shrinkage that collapses to the anchor; insufficient activity in high-dispersion 2025 periods; view matrix misspecification.

**Ablation plan.** No views; no LLM; no DRO; no risk-parity anchor; no turnover penalty; no drawdown throttle; pure anchor only; pure active-only BL; 2024-only calibration versus 2024+2025 calibration.

**Paper / award narrative.** This is probably the strongest competition paper of the set because the mathematical story is crisp, the implementation is reproducible, and the failure modes are intelligible.

### CEVA-KF

**One-sentence thesis.** Use an LLM only to extract typed economic shocks from hot news, then pass those shocks through a causal latent-factor model with invariance penalties and Kalman smoothing to obtain ETF-level counterfactual return views.

**Novelty claim.** This is the most ambitious “award narrative” design because it reframes hot-news trading as **causal shock filtering** rather than sentiment following. The core object is not a headline score but a vector of shocks such as liquidity easing, demand uplift, supply squeeze, regulation risk, or safe-haven demand. It goes beyond standard event extraction by asking: what is the ETF impact of this event *relative to a counterfactual in which the event had not happened*? That is a much stronger story than normal prompt engineering. citeturn40search0turn28search18turn33search2turn33search10turn35search2

**Mathematical state representation.** The state is a latent macro-shock vector \(f_t\), a shock-observation vector \(u_t\) extracted from news, and uncertainty matrices on both. ETF expected returns are \(\mu_t = B f_t\), where \(B\) is a learned exposure matrix.

**Update rule.** The state evolves through a linear dynamical system or switching state-space model. News-derived shocks enter as noisy expert observations; prices enter as realised observations on the latent state; invariance penalties are imposed across 2024 sub-environments so that the mapping from structural shocks to ETF returns does not rely on one-quarter artefacts.

**LLM role.** Strictly extraction: identify event type, target sector, sign, horizon, confidence, and whether the article expresses a new shock or merely repeats an already-known narrative.

**Non-LLM engine.** Structural-factor model, invariant regression, and a Kalman-style filter.

**Portfolio construction.** Use posterior mean returns and posterior uncertainty to size active tilts; large uncertainty pushes weight back into the anchor and cash. During high narrative disagreement, this design should explicitly under-trade.

**Data use and leakage safety.** Fully respect the 15:00 news rule and current-day-open-only price rule. In practice, a strong implementation should retain all structured event outputs in a daily cache to make B-list reruns deterministic.

**Track fit.** Track 1: **7.5/10**. Track 2: **8.5/10**. Very compelling where policy news moves specific sectors but also affects macro defensives.

**Implementation plan.** MVP: typed-event schema + linear shock model + covariance-scaling allocator, **10 student-days**. Strong version: invariance penalty + Kalman smoothing + counterfactual effect estimates, **21 student-days**. Report-ready version: shock taxonomies, counterfactual case studies, and invariance diagnostics, **32 student-days**.

**Failure modes.** Hallucinated structure from extraction; false causal confidence; too many latent factors for the small asset universe; unstable cross-environment training.

**Ablation plan.** No LLM extraction; no causal structure; no invariance penalty; no filter; no news; no turnover control; sentiment-only replacement; quant-only replacement; LLM-only trade generator as rejected control.

**Paper / award narrative.** If the organisers want a system report that is mathematically serious and clearly not generic LLM brainstorming, this is the strongest candidate.

### ARMOR-SPO

**One-sentence thesis.** Retrieve 2024 historical analogue days using joint price-news state embeddings, ensemble several simple allocators, and update the ensemble weights online with decision-focused learning and transaction-cost-aware mirror descent.

**Novelty claim.** This is more than a RAG system because the retrieved objects are **market states and allocator outcomes**, not documents for narrative generation. It is more robust than a monolithic predictor because it asks a practical question: when similar conditions appeared in 2024, which base allocator held up best after costs? It also inherits the strongest parts of online portfolio selection: low fragility, explicit adaptation, and relatively graceful behaviour under hidden regime shift. citeturn38search1turn38search6turn31search3turn31search2turn37search7turn36search0

**Mathematical state representation.** The state is a retrieval key \(z_t\), a set of \(K\) nearest historical analogues \(\mathcal N_t\), and meta-weights \(\alpha_t\) over a library of base allocators. The base library should include equal weight, inverse-vol, medium-term momentum, defensive macro rotation, top-\(k\) sector trend, and a persistence sleeve.

**Update rule.** Retrieve analogue windows from 2024 using a hybrid similarity over price path shape, volatility regime, event-topic distribution, and news dispersion. Use analogue outcomes to produce a prior over strategy performance, then update online meta-weights with realised post-cost portfolio utility through mirror descent or Hedge-style exponential weights.

**LLM role.** Optional and restrained: convert news into compact structured embeddings or topic histograms for retrieval; explanation generation only.

**Non-LLM engine.** Historical analogue search, decision-focused rank modelling, and online convex optimisation.

**Portfolio construction.** Construct each base portfolio, combine them by \(\alpha_t\), project back into long-only constraints, and apply a cash-aware turnover cap. This design is especially attractive under the official trade API because the bases can be made deliberately low-turnover and the meta-updates are smooth.

**Data use and leakage safety.** Retrieval memory should be built from 2024 only if prioritising robustness, or from 2024 plus frozen A-list logs if explicitly doing a late-cycle enhancement before final submission. Do not allow any 2026 material into the retrieval store.

**Track fit.** Track 1: **8/10**. Track 2: **8/10**. It is the best all-rounder after DRO-BL.

**Implementation plan.** MVP: six quant sleeves + kNN retrieval + exponential-weights mixer, **9 student-days**. Strong version: decision-focused retraining with SPO+ and analogue confidence scaling, **18 student-days**. Report-ready version: nearest-neighbour case studies, sleeve attribution, and regret-style plots, **26 student-days**.

**Failure modes.** Bad analogue metric; retrieval overfitting to idiosyncratic 2024 events; mixing too many correlated sleeves; slow reaction to unprecedented 2026 shocks.

**Ablation plan.** No retrieval; no online updates; no news in the retrieval key; no SPO layer; best-single-sleeve only; no turnover control; quant-only; LLM-augmented versus no-LLM embeddings.

**Paper / award narrative.** This is the best bridge between competition-first pragmatism and system-report novelty: it is clearly “agentic” in architecture, but entirely quantitative in decision control.

### HGF-MPC

**One-sentence thesis.** Model latent market drift and regime as a hidden state, treat same-day news as noisy expert opinions on that state, and solve a short-horizon, cost-aware model-predictive control problem for the ETF portfolio.

**Novelty claim.** This design sits directly on classic financial mathematics rather than contemporary prompt engineering. It is not as visually novel as CEVA or KG-MoE, but it may be more robust than both. Its advantage is that the task already hands the system exactly the kind of data a filtered belief-state model wants: time-series observations plus timestamped expert-like textual signals. citeturn35search2turn35search4turn33search0turn35search5

**Mathematical state representation.** Let \(x_t\) be latent factor drift, \(r_t\) a discrete regime variable, and \(P_t\) the state covariance. Price history yields noisy observations of state evolution; structured news yields expert-opinion observations about \(x_t\) or \(r_t\).

**Update rule.** Use a Kalman filter, switching linear dynamical system, or HMM filter to update the posterior \(p(x_t,r_t\mid \mathcal F_t)\). The news extractor should emit directional opinions and confidence intervals, not prose. The controller then solves a short-horizon asset-allocation problem using the filtered posterior mean and uncertainty.

**LLM role.** Opinion extraction and uncertainty estimation only.

**Non-LLM engine.** Hidden-state filtering plus model-predictive portfolio control.

**Portfolio construction.** The optimiser chooses a sequence of target weights over a short horizon, but only the first action is executed. Penalties are added for variance, turnover, and drawdown. In Track 1, the filtered state can naturally drive rotation among broad equity, bond, and gold sleeves.

**Data use and leakage safety.** Strongly aligned with official constraints because the model works with prior closes, the current open, and pre-15:00 news. It does not need any unofficial information source.

**Track fit.** Track 1: **8.5/10**. Track 2: **6.5/10**. Better for macro than for fine-grained sector rotation.

**Implementation plan.** MVP: two- or three-state HMM plus low-turnover optimiser, **8 student-days**. Strong version: Kalman filter with news-as-opinions and MPC rebalancer, **17 student-days**. Report-ready version: posterior regime plots, uncertainty decomposition, and scenario simulation, **26 student-days**.

**Failure modes.** State-space misspecification; over-smoothing that misses violent rotations; extracted opinions too noisy; controller complexity not justified by the small ETF universe.

**Ablation plan.** No news opinions; no regime state; HMM only versus Kalman only; static optimiser instead of MPC; no turnover control; no drawdown control; quant-only neutral-opinion variant.

**Paper / award narrative.** This is the best choice if the team wants a rigorous, finance-native paper rather than an NLP-systems paper.

## E. Mathematical Formulation of Each Design

Let there be \(N\) tradable ETFs and one implicit cash sleeve. Let \(w_t\in\mathbb{R}^N_+\) denote end-of-day risky weights, with \(\mathbf 1^\top w_t\le 1\); cash is \(1-\mathbf 1^\top w_t\). Let \(\hat\mu_t\) be model-implied next-period expected returns, \(\hat\Sigma_t\) a shrinkage covariance, and \(w_{t-1}\) yesterday’s post-mark-to-market risky weights.

A common portfolio layer across all six designs is

\[
w_t^{\text{raw}}=\arg\max_{w\in\mathcal C}
\hat\mu_t^\top w-\frac{\gamma_t}{2}w^\top\hat\Sigma_t w
-\lambda_{\mathrm{to}}\|w-w_{t-1}\|_1
-\lambda_{\mathrm{grp}}\sum_{g\in\mathcal G}\max(0,\mathbf 1_g^\top w-u_g)^2,
\]

with constraint set

\[
\mathcal C=\{w\ge 0,\ \mathbf 1^\top w\le 1,\ w_i\le c_i\ \forall i\}.
\]

A drawdown throttle then scales the risky sleeve by

\[
b_t=\max\{b_{\min},\ 1-\kappa\max(0,\mathrm{MDD}_{L,t}-d_0)\},
\qquad
w_t=b_t\, w_t^{\text{raw}}.
\]

This creates a controlled cash reserve, which is especially useful under the official trade protocol. The official schema requires buys by **amount** and sells by **holding percentage**, and the engine executes **buys before sells**. A compliant weight-to-trade adaptor is therefore

\[
\pi^{\text{sell}}_{i,t}
=
\min\left\{
1,\frac{(w^{\text{cur}}_{i,t}-w_{i,t})_+}{w^{\text{cur}}_{i,t}+\varepsilon}
\right\},
\]

and

\[
a^{\text{buy}}_{i,t}
=
V_t\,(w_{i,t}-w^{\text{cur}}_{i,t})_+,
\]

but if \(\sum_i a^{\text{buy}}_{i,t}\) exceeds current cash, the system should submit **sell-only** instructions and stage buys to the following day. That is not stylistic preference; it follows from the public engine implementation. citeturn44view0turn42view0

### TEMA-RP

Define daily extracted event set \(E_t\). Each event \(e\in E_t\) has key \(k_e\), value \(v_e\), and decay rate \(\delta_e=\exp(-\Delta t/\lambda_e)\). For asset query \(q_i\),

\[
\alpha_{i,e,t}
=
\frac{\exp\left(q_i^\top k_e/\sqrt d+\log \rho_e-\eta \Delta t_e\right)}
{\sum_{e'\in E_{\le t}}\exp\left(q_i^\top k_{e'}/\sqrt d+\log \rho_{e'}-\eta \Delta t_{e'}\right)},
\]

and memory updates as

\[
m_{i,t}
=
\beta_i\odot m_{i,t-1}
+
\sum_{e\in E_t}\alpha_{i,e,t}v_e.
\]

The score is

\[
s_{i,t}=u_i^\top[m_{i,t};z_{i,t};\hat\sigma_{i,t}^{-1};c_{i,t}],
\qquad
\hat\mu_{i,t}=\tau_s\,\mathrm{clip}(s_{i,t},-s_{\max},s_{\max}).
\]

### KG-MoE

Let \(G_t=(V,E_t)\) be a relation-labelled graph with relations \(r\in\mathcal R\). A message-passing layer is

\[
h_{i,t}^{(\ell+1)}
=
\phi\!\left(
W_0h_{i,t}^{(\ell)}
+
\sum_{r\in\mathcal R}
\sum_{j\in\mathcal N_r(i)}
\alpha_{ijr,t}W_r h_{j,t}^{(\ell)}
\right).
\]

A router produces expert weights

\[
\pi_t=\mathrm{softmax}(Uz_t),
\]

and ETF scores are

\[
s_{i,t}=\sum_{k=1}^K \pi_{k,t}\,f_k(h_{i,t}^{(L)}).
\]

A graph-smooth portfolio regulariser can be added:

\[
\Omega_G(w)=\lambda_G\sum_{(i,j)\in E^{ETF}}
a_{ij,t}(w_i-w_j)^2.
\]

### DRO-BL-RP

Let \(\Pi_t\) be the equilibrium prior, \(\tau\hat\Sigma_t\) the prior uncertainty, and \(P_t\mu=q_t+\varepsilon_t\) the structured news views with view covariance \(\Omega_t\). The Black–Litterman posterior mean is

\[
\mu_t^{BL}
=
\left[(\tau\hat\Sigma_t)^{-1}+P_t^\top\Omega_t^{-1}P_t\right]^{-1}
\left[(\tau\hat\Sigma_t)^{-1}\Pi_t+P_t^\top\Omega_t^{-1}q_t\right].
\]

A robust active portfolio is then

\[
w_t^{act}
=
\arg\max_{w\in\mathcal C}
(\mu_t^{BL})^\top w
-\frac{\gamma}{2}w^\top\hat\Sigma_t w
-\epsilon_t\|w\|_2
-\lambda_{\mathrm{to}}\|w-w_{t-1}\|_1,
\]

and the final portfolio is blended with a risk-parity anchor \(w_t^{RP}\):

\[
w_t=(1-\beta_t)w_t^{RP}+\beta_t w_t^{act},
\qquad
\beta_t=\mathrm{sigmoid}(\bar c_t-\theta).
\]

### CEVA-KF

Let \(u_t\) be extracted structural shocks and \(f_t\) latent causal factors. The state dynamics are

\[
f_t=A f_{t-1}+G u_t+\xi_t,
\]

and ETF expected returns are

\[
\hat\mu_t=B f_t.
\]

Price and news observations are

\[
y_t^{p}=C f_t+\varepsilon_t^{p},
\qquad
y_t^{n}=H u_t+\varepsilon_t^{n}.
\]

A Kalman-style filter estimates \((\hat f_t,\hat P_t)\). To reduce spurious patterns, the representation \(\phi(\cdot)\) or exposure matrix \(B\) is trained with an invariance penalty across 2024 environment splits \(e\in\mathcal E\):

\[
\mathcal L
=
\sum_{e\in\mathcal E} R_e(\phi,B)
+
\lambda_{IRM}\sum_{e\in\mathcal E}
\left\|\nabla_{w\mid w=1}R_e(w\cdot \phi,B)\right\|^2.
\]

A counterfactual event effect for ETF \(i\) is

\[
\Delta_{i,t}^{(e)}
=
\mathbb E[r_{i,t+1}\mid do(u_t=e),\mathcal F_{t-1}]
-
\mathbb E[r_{i,t+1}\mid do(u_t=0),\mathcal F_{t-1}],
\]

which feeds the active-view vector.

### ARMOR-SPO

Let \(w_t^{(m)}\) be base allocator \(m\)’s proposal and \(\alpha_t\in\Delta^M\) meta-weights. Final weights before projection are

\[
\tilde w_t=\sum_{m=1}^M \alpha_{m,t}w_t^{(m)}.
\]

Meta-weights update online using realised utility \(g_{m,t}\) net of cost:

\[
\alpha_{m,t+1}
\propto
\alpha_{m,t}
\exp\{\eta(g_{m,t}-\lambda_{\mathrm{tc}}\tau_{m,t})\}.
\]

To align learning with downstream portfolio decisions, train the retrieval-ranker or sleeve-scoring model with SPO+ rather than plain prediction loss:

\[
\mathcal L_{SPO+}(\hat c,c)
=
\max_{w\in\mathcal C}(2\hat c-c)^\top w
-
\max_{w\in\mathcal C}\hat c^\top w
+
c^\top w^\star(c),
\]

where \(c\) is the true downstream cost/return vector proxy and \(w^\star(c)\) is the optimiser’s decision. citeturn36search0turn36search18

### HGF-MPC

Let \(r_t\) be a latent regime and \(x_t\) a hidden drift/factor state. A switching linear system is

\[
x_t=A_{r_t}x_{t-1}+\xi_t,
\qquad
r_t\sim \mathrm{Markov}(\Pi).
\]

Prices and news-opinion observations obey

\[
y_t^{p}=C_{r_t}x_t+\varepsilon_t^p,
\qquad
y_t^{n}=H_{r_t}x_t+\varepsilon_t^n.
\]

Filtering yields \(p(x_t,r_t\mid \mathcal F_t)\). Then MPC solves

\[
\max_{\{w_{t+h}\}_{h=0}^{H-1}}
\sum_{h=0}^{H-1}
\left(
\hat\mu_{t+h|t}^\top w_{t+h}
-
\frac{\gamma}{2}w_{t+h}^\top \hat\Sigma_{t+h|t} w_{t+h}
-
\lambda_{\mathrm{to}}\|w_{t+h}-w_{t+h-1}\|_1
\right),
\]

subject to long-only and concentration constraints, executing only \(w_t\).

## F. Quantitative Comparison Table

The table below uses the user-specified 0–10 criteria and the requested ROI formula. Scores are deliberately conservative and relative to this specific shared task, not to finance research in general.

| Design | Track 1 Fit | Track 2 Fit | Sharpe Potential | Drawdown Control | Turnover Efficiency | B-list Robustness | Novelty | Mathematical Depth | Interpretability | Reproducibility | Feasibility | Baseline Beating Probability | Report / Paper Signal | Overfit Risk | Tool Dependency Risk | Data Compliance Risk | Overall ROI |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| TEMA-RP | 7.0 | 8.0 | 7.5 | 7.0 | 6.5 | 7.0 | 8.5 | 8.0 | 7.5 | 7.5 | 6.5 | 7.0 | 8.5 | 5.0 | 2.5 | 2.0 | **7.95** |
| KG-MoE | 6.0 | 9.0 | 7.0 | 6.5 | 6.0 | 6.5 | 8.5 | 8.0 | 7.5 | 7.0 | 6.0 | 6.5 | 8.5 | 5.5 | 3.5 | 2.0 | **7.67** |
| DRO-BL-RP | 9.0 | 7.0 | 8.0 | 8.5 | 8.0 | 8.0 | 7.0 | 9.0 | 8.0 | 9.0 | 8.0 | 8.0 | 7.5 | 3.5 | 1.5 | 1.0 | **8.84** |
| CEVA-KF | 7.5 | 8.5 | 7.5 | 7.0 | 6.5 | 7.0 | 9.0 | 8.5 | 8.5 | 7.0 | 6.5 | 7.0 | 9.0 | 5.0 | 3.0 | 2.5 | **8.17** |
| ARMOR-SPO | 8.0 | 8.0 | 8.0 | 7.5 | 8.5 | 8.5 | 8.0 | 8.0 | 7.5 | 8.5 | 7.0 | 8.0 | 8.0 | 4.0 | 2.0 | 1.5 | **8.56** |
| HGF-MPC | 8.5 | 6.5 | 7.5 | 8.0 | 7.5 | 8.0 | 7.5 | 9.0 | 7.5 | 8.0 | 6.5 | 7.5 | 8.0 | 4.0 | 1.5 | 1.5 | **8.42** |

A clear ranking emerges. **DRO-BL-RP** is the best pure competition design because it is the strongest on drawdown, turnover, robustness, and feasibility at once. **ARMOR-SPO** is the best all-round research-to-competition hybrid. **HGF-MPC** is a close third because hidden-state filtering is unusually well aligned with the official information structure. **CEVA-KF** is slightly less competition-safe, but its report value is extremely high. **TEMA-RP** and **KG-MoE** are both viable, but their implementation burden is harder to justify unless the team strongly values system-paper distinctiveness.

## G. Competition Score vs Research/Award Score

For interpretability, I define two auxiliary scores. The **Competition Score** emphasises track fit, Sharpe, drawdown, turnover, B-list robustness, and baseline-beating probability, with modest penalties for overfit and compliance risk. The **Research/Award Score** emphasises novelty, mathematical depth, interpretability, report value, and reproducibility, again with mild penalties for tool and compliance risk.

| Design | Competition Score | Research / Award Score | Quadrant reading |
|---|---:|---:|---|
| DRO-BL-RP | **8.04** | 8.11 | High competition, high research |
| ARMOR-SPO | **7.77** | 7.81 | High competition, solid research |
| HGF-MPC | **7.58** | 7.97 | High competition, high research |
| CEVA-KF | 6.94 | **8.21** | Moderate competition, very high research |
| TEMA-RP | 6.86 | 7.81 | Moderate competition, high research |
| KG-MoE | 6.63 | 7.89 | Moderate competition, high research |

The most interesting implication is that there is **no need to choose between a competitive system and an award-worthy report**. Three designs sit comfortably in the “high competition + high research” zone: **DRO-BL-RP**, **ARMOR-SPO**, and **HGF-MPC**. The intentionally more experimental designs—**CEVA-KF**, **KG-MoE**, and **TEMA-RP**—are exactly the kinds of systems that could be selected as “creative or especially informative” even if they are not first on Sharpe, because the official FAQ explicitly leaves room for informative and creative reports in the shared-task paper. citeturn45view0

If the goal is **maximum ranking probability**, the safest frontier is **DRO-BL-RP → ARMOR-SPO → HGF-MPC**. If the goal is **paper distinction**, the order shifts to **CEVA-KF → KG-MoE / TEMA-RP → HGF-MPC**.

## H. Baseline-Beating and Ablation Plan

A credible submission should be judged against a transparent baseline ladder. The baseline suite should be:

| Baseline | Exact definition | What an innovative design must prove |
|---|---|---|
| Equal weight | \(w_i=1/N\) | Better Sharpe after costs, not just higher raw return |
| Inverse-volatility | \(w_i\propto 1/\hat\sigma_i\) | Better active timing without materially larger drawdowns |
| Momentum-only | 20/60-day risk-adjusted momentum, long-only | That news or structure adds value beyond trend |
| Sector trend-following | Track 2 top-\(k\) by momentum, equal weight within \(k\) | That graph/event logic improves sector selection |
| Persistence / low-turnover | Only rebalance when score ranks change materially | That the new design is not just churn for no gain |
| Rule-based macro rotation | Equity vs bond/gold sleeves from breadth and risk-off proxies | That macro reasoning beats simple defensive heuristics |
| News sentiment only | Aggregate sentiment by asset mapping; inverse-vol sizing | That typed events or causality beat raw polarity |
| S1 quant core | Track 1: inverse-vol + momentum + breadth + defensive sleeve; Track 2: sector trend top-\(k\) | That the design beats a strong public-style quant implementation, not only naïve baselines |

The public starter LLM agent should also be run as a **rejected-control baseline**, because it gives a natural “LLM-only-ish” comparator: summarise news, infer sentiment, generate trades. That is useful for the paper even if it is not a realistic submission target. citeturn21view8turn22view0

The promotion gate for each final design should be explicit. **TEMA-RP** must show that memory beats plain event averaging and that no-news performance collapses less than a sentiment-only pipeline during regime changes. **KG-MoE** must show incremental value over sector trend-following specifically in policy-sensitive groups such as semiconductors, AI, software, healthcare, and real estate. **DRO-BL-RP** must beat S1 on turnover-adjusted Sharpe and drawdown in at least three non-overlapping 2024 walk-forward windows. **CEVA-KF** must show that structured shock extraction beats sentiment-only and that the causal/invariant layer improves stability across 2024 quarters. **ARMOR-SPO** must beat the best single sleeve, not just the average sleeve, and should show positive utility from retrieval and online updating separately. **HGF-MPC** must show that filtered latent state improves defensive timing relative to plain macro heuristics.

The ablation matrix should be standardised across all models. For every design, run: **no LLM**, **no news**, **no risk control**, **no turnover control**, **baseline fallback only**, **quant-only**, **LLM-only control**, and **2024-tuned versus 2025-tuned**. Then add one design-specific ablation: **no memory** for TEMA-RP, **no graph / no router** for KG-MoE, **no BL / no DRO / no RP anchor** for DRO-BL-RP, **no causal / no invariance / no filter** for CEVA-KF, **no retrieval / no online-updating / no SPO** for ARMOR-SPO, and **no regime state / no MPC / no expert opinions** for HGF-MPC.

The minimum promotion threshold should remain strict. A design is worth continuing only if it either **beats S1 on 2024 walk-forward** or offers clearly superior paper value; **does not materially worsen turnover-adjusted Sharpe**; remains stable across multiple 2024 subwindows; uses no post-2025 resources; produces reproducible logs; and has a clean path to organiser-run B-list execution.

## I. Hidden B-List Robustness Audit

The official B leaderboard is private, centrally executed by the organisers, and limited to resources available before 2026. That makes hidden-period robustness more important than flashy in-sample fitting. citeturn45view0turn45view1

| Risk | Why it matters here | Most exposed designs | Best mitigation |
|---|---|---|---|
| Regime shift in 2026 | Hidden B period can differ sharply from 2024–2025 | TEMA-RP, KG-MoE, CEVA-KF | Strong cash sleeve, shrinkage risk model, 2024 subwindow validation, simple fallbacks |
| Prompt instability | Central evaluation punishes nondeterministic extraction | TEMA-RP, CEVA-KF, KG-MoE | Deterministic JSON extraction, low temperature, full caching, or offline small models |
| Tool dependency risk | External APIs may be fragile or disallowed operationally | Any API-heavy design | Prefer local models, frozen weights, Docker-first packaging |
| Macro novelty / analogue failure | Retrieval and pattern memory may not find good precedents | ARMOR-SPO, TEMA-RP | Confidence-weight retrieval, fallback to robust anchor |
| Sector-label drift | Track 2 themes evolve quickly in Chinese markets | KG-MoE, CEVA-KF | Freeze ETF taxonomy from official pool, hand-check mappings |
| Data compliance risk | Starter code exposes enough anomalies to tempt accidental leakage | All designs | Ignore `/market_data`; ignore `portfolio.holdings.price`; use only safe historical prices and safe news paths citeturn45view1turn11view1turn12view1turn9view5 |
| Overfitting 2025 A-list | Public 2025 can seduce repeated tuning | All designs | Tune on 2024, reserve 2025 for sparse final comparison |
| Excessive turnover under buy-first engine | Full same-day rotations are operationally awkward | CEVA-KF, TEMA-RP, KG-MoE | Staged rebalancing, current-cash-aware buys, turnover penalty citeturn42view0turn44view0 |

The dominant hidden-period lesson is simple: **any architecture that cannot gracefully collapse back to a strong quant anchor should not be trusted on the B-list**. This is why the best designs in this report all have explicit fallback baselines and a cash sleeve.

## J. Implementation Roadmap

| Phase | Objective | Concrete tasks | Deliverable | Estimated effort |
|---|---|---|---|---:|
| Phase 0R: source/data reset | Remove ambiguity from the starter kit | Freeze official repo commit, document safe vs unsafe fields, reproduce dataset loading, write a leakage whitelist | Internal technical note and safe feature API | 2 student-days |
| Phase 1R: official starter reproduction | Reproduce organiser environment | Run official server/client demo for both tracks, save daily logs, verify trade semantics and resume logic | Working local replay of public starter | 3 student-days |
| Phase 2R: baselines | Build the real hurdle | Implement equal weight, inverse-vol, momentum, sector top-\(k\), low-turnover, rule-based macro, news sentiment only, S1 quant core | Baseline report with 2024 walk-forward tables | 5 student-days |
| Phase 3R: first innovative prototype | Start with the highest-ROI architecture | Implement **DRO-BL-RP** first, with rule-based views before any LLM extraction | Prototype with full logs and ablations | 7 student-days |
| Phase 4R: full comparison | Add one competition hybrid and one report-rich design | Implement **ARMOR-SPO** and either **CEVA-KF** or **HGF-MPC** | Comparative matrix on 2024 subwindows | 10–14 student-days |
| Phase 5R: A-list package | Package the public submission candidate | Freeze hyperparameters, run 2025 once or in a very small number of controlled passes, export daily logs and results | A-list-ready package | 4 student-days |
| Phase 6R: B-list hardening | Make central execution safe | Remove external API dependence if possible, cache all structured outputs, pin seeds, write Docker, add fail-safe fallbacks | Organiser-ready reproducible bundle | 4 student-days |

The correct build order is therefore **not** “pick the most novel idea first”. It is: reproduce the starter exactly, beat the baseline ladder, implement the strongest low-fragility innovation first, and only then spend additional cycles on a more decorative research architecture.

## K. Final Recommendation

**Best performance-first design.** **DRO-BL-RP**. It fits the official constraints best, handles estimation error explicitly, respects cost/turnover realities, and is the easiest to make robust under organiser-run B-list evaluation.

**Best research / award design.** **CEVA-KF**. It is the clearest departure from generic LLM-agent design and has the strongest system-report narrative: structured market shocks, causal views, invariance, and filtered uncertainty.

**Best one-student design.** **DRO-BL-RP** again. Its MVP is attainable quickly, and its failure modes are far easier to diagnose than those of graph or causal systems.

**Best Track 1 design.** **DRO-BL-RP**, with **HGF-MPC** as the strongest runner-up. If the team especially wants a macro-interpretability paper, HGF-MPC is the elegant alternative.

**Best Track 2 design.** **KG-MoE** if the team is comfortable with graph modelling; otherwise **CEVA-KF** is the safer sector-sensitive alternative. For raw ranking probability, **ARMOR-SPO** may still outperform both because it is less brittle.

**Designs to reject as main submissions.** Reject the starter-style **pure LLM decision chain**, reject **generic RAG-to-weight** systems, and reject **news-sentiment PPO / end-to-end DRL** as first-cycle builds. They are either too fragile, too hard to reproduce, or too weakly differentiated mathematically.

**Exact first implementation target.** Build **DRO-BL-RP** first, with a rule-based structured-view extractor, shrinkage covariance, risk-parity anchor, turnover-penalised optimiser, and a current-cash-aware staged trade translator. Only after that baseline is stable should you add an optional small-model event extractor.

**Exact fallback if novelty underperforms.** Freeze the system to **S1 quant core + ARMOR-SPO-style online meta-weighting**, with no LLM dependency at all. That fallback preserves most of the execution infrastructure, keeps turnover controllable, and still offers a legitimate shared-task paper story.

The decisive implementation path is therefore:

1. Reproduce the official environment and build the baseline ladder.
2. Implement **DRO-BL-RP** as the primary competitive engine.
3. Add **ARMOR-SPO** if time permits and the baseline gap remains narrow.
4. Add **CEVA-KF** only if the team wants a strong paper narrative beyond pure competition.
5. Use **KG-MoE** and **TEMA-RP** as second-wave research builds, not first-wave competition builds.

If I had to choose a single architecture to implement tomorrow for the highest research-competition return, it would be **DRO-BL-RP with a strict leakage-safe trade adapter and a no-API fallback mode**.