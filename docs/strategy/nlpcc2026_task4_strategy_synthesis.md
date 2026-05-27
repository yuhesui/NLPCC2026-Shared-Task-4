## A. Input Report Quality Audit

The following audit treats each uploaded report as an input to a strategy committee, not as an authority. Scores are 0–10; for **Overclaiming Risk**, higher is worse. Suggested weights sum to **1.00** and reflect how much each report should influence the final build decision.

| Report | Official-Source Fidelity | Research-Citation Quality | Mathematical Specificity | Implementation Realism | Novelty Insight | Robustness Awareness | Scoring Discipline | Overclaiming Risk | Synthesis Utility | Suggested Weight |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| DeepResearch_ChatGPT.md | 9.2 | 8.4 | 8.3 | 9.0 | 7.2 | 9.1 | 8.8 | 2.2 | 9.3 | 0.32 |
| DeepResearch_Perplexity1.md | 8.5 | 8.0 | 8.2 | 8.0 | 8.0 | 8.6 | 7.8 | 3.6 | 8.4 | 0.22 |
| DeepResearch_Perplexity3.md | 8.4 | 7.7 | 8.0 | 7.8 | 8.1 | 8.3 | 7.5 | 4.0 | 8.0 | 0.18 |
| DeepResearch_Perplexity2.md | 6.8 | 7.2 | 8.0 | 6.9 | 8.8 | 8.0 | 6.8 | 5.2 | 7.2 | 0.13 |
| DeepResearch_Gemini-_21.md | 6.6 | 5.4 | 7.5 | 6.4 | 8.0 | 7.2 | 5.6 | 7.0 | 6.9 | 0.15 |


**Audit conclusions.**

1. **Most reliable report:** `DeepResearch_ChatGPT.md`. It is the strongest on official-source fidelity, code-level leakage concerns, implementation sequencing, and conservative promotion logic.
2. **Most creative report:** `DeepResearch_Perplexity2.md`. It pushes graph-based, causal, and policy-transmission ideas hardest; however, it relies more heavily on CN-Buzz2Portfolio-like framing and is less implementation-disciplined.
3. **Most implementation-realistic report:** `DeepResearch_ChatGPT.md`, followed by `DeepResearch_Perplexity1.md`. Both repeatedly return to S1, fallback, Docker, and one-student feasibility.
4. **Most likely to overclaim:** `DeepResearch_Gemini-_21.md`. It is useful for bold prioritisation, especially BSA-RP/CIRM/KG-MoE framing, but its language is too absolute relative to the empirical uncertainty.
5. **Best mathematical ideas:** `DeepResearch_ChatGPT.md` for DRO-BL-RP/HGF-MPC/CEVA-KF formulation; `DeepResearch_Perplexity3.md` for broader BSA/LEEQA/CIGA/OCO coverage.
6. **Best roadmap:** `DeepResearch_ChatGPT.md`. Its sequence — reproduce official environment, build S1, implement DRO-BL-RP, then add ARMOR/CEVA/HGF only if justified — is the least likely to waste time.


## B. Cross-Report Consensus and Disagreement

| Topic | Consensus | Disagreement | Final Synthesis Decision |
| :-- | :-- | :-- | :-- |
| Best Track 1 design | ChatGPT and Gemini converge on DRO-BL / DRO-BL-RP as the strongest macro backbone; the Perplexity reports also keep DRO-BL among the most robust options. | Gemini rates BSA-RP as the performance-first design; Perplexity3 gives more first-build weight to BSA-RP/LEEQA; HGF-MPC appears as an elegant macro alternative but not the dominant first build. | Build DRO-BL-RP first for Track 1. Treat HGF-MPC as a second-wave macro interpretability module, and keep BSA-RP as a conservative regime/risk-parity comparator. |
| Best Track 2 design | All reports recognise Track 2 needs sector/policy/entity structure; KG-MoE or graph-sector methods are the most natural high-upside Track 2 candidate. | ChatGPT demotes KG-MoE to second wave because of implementation burden; Gemini strongly elevates it; Perplexity reports split between KG-MoE, LEEQA, and causal/graph designs. | Do not build full KG-MoE first. Build LEEQA-Rank or KG-MoE-Lite only after S1 and DRO are stable. Use KG-MoE-Lite as the Track 2 report/visual centrepiece if time remains. |
| Best one-student design | DRO-BL is repeatedly identified as the easiest mathematically serious build with clean tooling, reproducible logs, and convex optimisation support. | BSA-RP is also one-student feasible but requires careful regime-state calibration; graph/causal/transformer-memory ideas are heavier. | DRO-BL-RP is the one-student core. BSA-RP and ARMOR-OMD are next; KG-MoE/CEVA/TEMA are not first-cycle solo builds. |
| Best performance-first design | Performance-first designs are robust, low-turnover, and mathematically anchored: DRO-BL-RP, BSA-RP, OCO/OMD, and Regime-HMM variants. | ChatGPT selects DRO-BL-RP; Gemini selects BSA-RP; Perplexity reports distribute support across DRO-BL, BSA-RP, OCO/OMD, and CIGA/CEIG. | DRO-BL-RP ranks first because it combines Sharpe potential, feasibility, and low B-list fragility. BSA-RP is second; ARMOR-OMD is the safe adaptive overlay. |
| Best research/award design | Causal/invariant, graph, belief-state, and memory-based designs provide stronger system-report narratives than simple BL. | ChatGPT nominates CEVA-KF; Gemini nominates CIRM; Perplexity2 emphasises graph/causal knowledge grounding; Perplexity1 emphasises interpretable belief states. | Use CEVA-KF/CIGA as the report-centrepiece narrative, but do not make it the first production engine unless simpler baselines already work. |
| Whether DRO-BL should be built first | Most reports keep DRO-BL near the top for Track 1 and one-student implementation. | Gemini argues BSA-RP may be the safer performance-first design; Perplexity3 suggests first prototyping BSA-RP + LEEQA in one route. | Yes. Build DRO-BL-RP first, beginning with deterministic rule-based views before any LLM extraction. |
| Whether BSA-RP should be built first | BSA-RP is high-quality: interpretable, robust, low-turnover, and report-friendly. | It is less direct for Track 2 and may underperform if regimes are too coarse; DRO-BL has simpler view-to-weight mechanics. | Build as the second conservative comparator if time permits, not before DRO-BL-RP. |
| Whether KG-MoE is worth implementing | Worthwhile for Track 2 narrative and policy-sector transmission logic. | Reports disagree on full GNN/MoE feasibility; ChatGPT is cautious, Gemini is enthusiastic, Perplexity2 is supportive but recognizes regularization needs. | Implement KG-MoE-Lite only if S1 and DRO are already stable. Use static graph + expert router first; defer trainable GNN and deep MoE. |
| Whether TEMA/RAMA-T is implementation-worthy | Memory/analogue search is interesting and visualisable. | TEMA is high novelty but fragile under event embedding drift; retrieval analogues are easier than transformer-memory training. | Do not build TEMA as a core engine. Merge its practical part into ARMOR-OMD retrieval; keep transformer-memory attention plots as report ablations only. |
| Whether causal/invariant models should be core or report-only | Causal/invariant ideas are very report-rich and relevant to hidden B-list robustness. | Implementation feasibility is weak for one student if full SCM/IRM is attempted. | Keep CEVA-KF/CIGA as report-centrepiece and ablation layer. Use only lightweight causal verification in the production stack. |
| Whether online learning/OCO should be a core fallback | OCO/OMD has strong robustness, low dependency, and clean regret/turnover narrative. | It may not exploit text as deeply as graph/causal systems. | Yes. ARMOR-OMD should be the core fallback/meta-allocator over S1, DRO-BL, and sector trend sleeves. |
| Whether direct LLM allocation should be rejected | All reports reject uncontrolled prompt-to-weight allocation. | Some reports use the starter LLM as a baseline or narrative comparator. | Reject as a production design. Use only as a baseline/negative control. |
| Whether API-heavy systems should be avoided for B-list | All reports flag central execution, reproducibility, prompt instability, and pre-2026 resource limits. | Reports differ on how much external LLM use remains acceptable. | Avoid API dependency in the final submission. Cache extraction, use local models if any, and ensure deterministic no-API fallback. |

## C. Design Consolidation Map

The reports use overlapping names for related engines. The table below consolidates them into decision-relevant families.

| Original Design Name(s) | Source Report(s) | Consolidated Name | Status | Reason |
| :-- | :-- | :-- | :-- | :-- |
| DRO-BL, DRO-BL-RP, robust BL, robust Black-Litterman | All five, strongest in ChatGPT/Gemini/P1 | DRO-BL-RP | Core build | Best competition-feasibility trade-off; naturally incorporates LLM view uncertainty, covariance shrinkage, turnover penalty, and fallback to risk-parity/S1. |
| BSA-RP, belief-state risk-parity allocator | Gemini, P1, P2, P3 | BSA-RP | Secondary build | Very robust and interpretable, but first build is less direct than BL and may be coarse for Track 2. |
| Regime-HMM-RP, simple HMM risk-parity, regime templates | P1, P3, Gemini variants | Regime-HMM-RP | Baseline only | Useful as a simple regime/risk comparator and fallback; not sufficiently novel to be the final centrepiece once BSA-RP exists. |
| HGF-MPC, hidden Gaussian drift, Kalman-HMM MPC | ChatGPT, P2/P3 variants | HGF-MPC | Report-centrepiece | Strong macro mathematics and visual filtered drift; burden is higher than DRO-BL and overlap with BSA/HMM is substantial. |
| KG-MoE, graph MoE sector allocator, ETF-sector-policy KG | All five, especially Gemini/P2 | KG-MoE-Lite | Track-specific build | Best Track 2 narrative and visuals; full trainable graph/MoE is too heavy, so build static graph + deterministic router first. |
| TEMA, TEMA-RP, RAMA-T, transformer event memory | ChatGPT, P1, P2, Gemini | TEMA/RAMA-T | Defer | High report value but unstable and costly; practical retrieval-memory component is better absorbed into ARMOR-OMD. |
| ARMOR-SPO, OMD-RAG, retrieval analogue, online update | ChatGPT, P1, P2, Gemini | ARMOR-OMD | Core build | Strong safe fallback and meta-allocator; combines retrieval analogues with online mirror descent and transaction-cost awareness. |
| OCO-Bandit, OCO-Ensemble, bandit-RP router | P1, P2, P3, ChatGPT | OCO-Ensemble | Ablation only | Mathematically clean but too price-only if isolated; best used inside ARMOR-OMD. |
| LEEQA, LLM event extraction + learning-to-rank allocator | P3, partially P1/P2 | LEEQA-Rank | Track-specific build | Most feasible Track 2 model beyond S1; clear ablations and moderate mathematical depth, but ranking labels may overfit 2024/2025. |
| CEVA-KF, CIRM, CIGA, CEIG, causal invariant event-impact | ChatGPT, Gemini, P2, P3 | CEVA-KF/CIGA | Report-centrepiece | Best research narrative; high implementation and identification risk, so use as verifier/report layer rather than first production engine. |
| Pure LLM direct allocator, Baseline-LLM-Oracle, starter prompt-to-trade chain | All five | Pure LLM Allocator | Reject | No deterministic risk engine, high prompt sensitivity, poor B-list reproducibility, and no credible turnover discipline. |
| Simple BL with LLM views, LLM-MV sentiment | Gemini/P1/P2 variants | Simple BL / sentiment-MVO | Baseline only | Useful ablation but insufficient robustness; can over-trust noisy LLM views and unstable covariance estimates. |
| Heavy deep RL, end-to-end graph RL, news-sentiment PPO | ChatGPT/Gemini/P1/P2 | Deep RL / Graph RL | Reject | Overfit-prone, hard to reproduce, too expensive for one-student schedule, and weakly suited to small ETF universes. |
| Generic RAG summariser, RAG-to-weight | All five as negative comparator | Generic RAG Summariser | Reject | Retrieval without formal allocator or online regret control is not materially safer than narrative overfitting. |

## D. Final Design Shortlist

The shortlist is intentionally limited to **seven** designs. These cover performance-first, Track 1, Track 2, report-centrepiece, and safe-fallback roles without forcing all novel ideas into production.

| Final Design | Thesis | Engine | LLM Role | Track 1 Fit | Track 2 Fit | Competition Edge | Report Edge | Burden | Main Risk | Status |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| DRO-BL-RP | Use news only to form bounded views; allocate through robust BL anchored to risk parity/S1. | BL posterior + Wasserstein/ellipsoidal ambiguity + shrinkage covariance + turnover QP. | Structured event/view extraction, confidence scoring, optional explanation; not allocator. | Very high | Medium | Best balance of Sharpe, drawdown, turnover, and one-student feasibility. | Clean formulas, view-confidence maps, strong ablations. | Medium; feasible in 1–2 weeks after baselines. | Weak incremental value if news views are noisy or stale. | Primary core build |
| BSA-RP | Treat news as noisy observations of latent regimes; allocate through regime-conditioned risk parity. | Bayesian/HMM belief update + regime templates + risk parity. | Map news to regime-observation vector and uncertainty level. | High | Medium-low | Low turnover and strong drawdown discipline. | Excellent belief trajectory plots and interpretable regime story. | Medium; feasible but calibration sensitive. | Regimes may be too coarse; can under-react to sector-specific shocks. | Secondary conservative build |
| ARMOR-OMD | Use retrieval analogues and online mirror descent to adaptively weight robust base sleeves. | kNN/analogue retrieval + OMD/Hedge over S1, DRO, trend, defensive sleeves with turnover penalty. | Optional embedding/event-key generation; can run price-only. | Medium-high | High-medium | Best fallback/meta-allocator and low dependency risk. | Regret curves, expert weights, analogue hit-rate plots. | Medium-low; implementable once baseline sleeves exist. | Analogue retrieval may fail during novel 2026 macro events. | Core fallback / second prototype |
| LEEQA-Rank | Convert news and price features into daily ETF rankings, then trade only stable top-k sector tilts. | Learning-to-rank / SPO-style rank loss + volatility scaling + turnover filter. | Event extraction, entity-to-sector mapping, feature generation. | Medium-low | High | Practical Track 2 extension with clear baseline-beating test. | Rank stability, feature attribution, no-news/no-LLM ablations. | Medium-low; easier than KG-MoE. | Ranker overfits 2024/2025 event vocabulary. | Track-specific build if Track 2 is prioritised |
| KG-MoE-Lite | Map policy/entity shocks through a sector ETF graph and route to specialist allocation experts. | Static ETF-sector-policy graph + message passing score + deterministic MoE router; no deep GNN initially. | Entity/policy/sector edge extraction and evidence tagging. | Medium-low | Very high | Potentially captures policy transmission better than raw momentum. | Best graph visual system and Track 2 narrative. | High; only lite version is one-student feasible. | Graph mapping drift, brittle edges, over-engineering before S1 is strong. | Track 2 report build, not first |
| HGF-MPC | Filter hidden asset drift from price/news observations and optimise a short-horizon allocation path. | Kalman/HMM latent drift model + model predictive control + turnover costs. | Noisy expert-opinion vector and event-confidence observations. | High | Medium | Elegant macro smoothing and controlled rebalancing. | Filtered drift, uncertainty bands, MPC trade path visuals. | High-medium; more implementation risk than DRO-BL. | Latent drift model may be mis-specified and over-calibrated. | Macro report-centrepiece / defer until baseline strong |
| CEVA-KF/CIGA | Separate stable causal event-transmission channels from spurious news correlations before allocation. | Typed causal event map + invariant tests + Kalman smoothing / robust allocation overlay. | Typed event extraction, causal hypothesis generation, evidence verifier. | Medium-high | High-medium | Potential hidden B-list robustness if causal map is correct. | Best research thesis: causal views, counterfactual stress tests, invariant ablations. | High; not first-cycle feasible as full system. | Causal identification hallucination and weak empirical validation. | Research/award centrepiece; lightweight verifier only in production |


**Portfolio of roles.**

- **Primary competition candidate:** DRO-BL-RP.
- **Secondary conservative candidate:** BSA-RP.
- **Safe adaptive fallback:** ARMOR-OMD over S1/DRO/trend sleeves.
- **Practical Track 2 extension:** LEEQA-Rank.
- **Track 2 report/visual centrepiece:** KG-MoE-Lite.
- **Macro report-centrepiece:** HGF-MPC.
- **Research/award centrepiece:** CEVA-KF/CIGA.


## E. Quantitative Strategy Benchmark


Scores below are decision-prior scores, not empirical backtest results. They are designed to penalise implementation burden, B-list fragility, data-compliance risk, and vague novelty.

**Competition Score formula**

`0.18 * SharpePotential + 0.14 * DrawdownControl + 0.12 * TurnoverEfficiency + 0.20 * BListRobustness + 0.16 * BaselineBeatingProbability + 0.10 * Reproducibility + 0.10 * Feasibility - 0.10 * OverfitRisk - 0.05 * ToolDependencyRisk - 0.05 * DataComplianceRisk`

**Research/Award Score formula**

`0.18 * Novelty + 0.16 * MathematicalDepth + 0.14 * Interpretability + 0.12 * ReportPaperSignal + 0.10 * Reproducibility + 0.10 * BListRobustness + 0.08 * Feasibility + 0.06 * max(Track1Fit, Track2Fit) + 0.06 * BaselineBeatingProbability - 0.06 * OverfitRisk - 0.04 * ToolDependencyRisk - 0.02 * DataComplianceRisk`

**Overall ROI formula**

`0.45 * Competition Score + 0.40 * Research/Award Score + 0.15 * Feasibility - 0.05 * OverfitRisk - 0.03 * ToolDependencyRisk - 0.02 * DataComplianceRisk`

| Design | Track 1 Fit | Track 2 Fit | Sharpe Potential | Drawdown Control | Turnover Efficiency | B-list Robustness | Novelty | Mathematical Depth | Interpretability | Reproducibility | Feasibility | Baseline-Beating Probability | Report/Paper Signal | Overfit Risk | Tool Dependency Risk | Data Compliance Risk | Competition Score | Research/Award Score | Overall ROI | Final Rank |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| DRO-BL-RP | 9 | 6 | 7.5 | 8.2 | 8.0 | 8.3 | 6.8 | 8.5 | 8.2 | 8.5 | 8.2 | 7.2 | 7.4 | 3.2 | 2.5 | 2.5 | 7.37 | 7.59 | 7.3 | 1 |
| BSA-RP | 8 | 5.5 | 6.9 | 8.5 | 8.2 | 8.0 | 7.2 | 8.0 | 8.4 | 8.0 | 7.5 | 6.8 | 8.0 | 3.8 | 2.8 | 2.5 | 7.01 | 7.41 | 6.92 | 2 |
| ARMOR-OMD | 6.5 | 7 | 7.0 | 7.3 | 8.4 | 8.1 | 6.5 | 7.6 | 7.1 | 8.6 | 8.0 | 7.0 | 7.2 | 3.5 | 2.2 | 3.0 | 7.08 | 7.04 | 6.9 | 3 |
| LEEQA-Rank | 5.5 | 8.0 | 6.8 | 6.8 | 7.2 | 6.8 | 6.2 | 6.8 | 7.6 | 8.0 | 8.0 | 6.6 | 7.0 | 5.0 | 3.0 | 3.0 | 6.26 | 6.62 | 6.26 | 4 |
| HGF-MPC | 8.2 | 5.8 | 6.8 | 7.8 | 7.5 | 7.1 | 7.4 | 8.8 | 8.0 | 7.1 | 6.3 | 6.2 | 8.2 | 5.0 | 3.0 | 3.5 | 6.14 | 7.14 | 6.16 | 5 |
| CEVA-KF | 7.0 | 7.5 | 6.1 | 7.2 | 6.8 | 7.4 | 9.0 | 8.4 | 8.8 | 6.2 | 5.5 | 5.6 | 9.3 | 6.5 | 3.8 | 4.5 | 5.4 | 7.27 | 5.63 | 6 |
| KG-MoE-Lite | 5.5 | 9.0 | 7.0 | 6.7 | 6.4 | 6.3 | 8.6 | 8.1 | 8.2 | 6.3 | 5.6 | 6.3 | 8.8 | 6.3 | 4.5 | 4.0 | 5.37 | 7.04 | 5.54 | 7 |


**Interpretation.**

1. **Why DRO-BL-RP is top-ranked.** It is not the most novel, but it has the best joint profile: high Track 1 fit, clean mathematical engine, robust handling of LLM-view uncertainty, strong drawdown/turnover discipline, and high reproducibility. Its failure mode is also diagnosable: if views add no value, the system collapses toward BL prior / risk parity / S1 instead of becoming unstable.
2. **Why the best research design differs from the best competition design.** CEVA-KF/CIGA and KG-MoE-Lite are more publishable because they create causal/graph narratives and better visuals, but they carry higher identification, implementation, and mapping risks. Competition ranking rewards robust execution under hidden B-list uncertainty; report selection rewards insight and interpretable architecture.
3. **Likely to beat S1 if implemented cleanly:** DRO-BL-RP, ARMOR-OMD, and possibly BSA-RP. LEEQA-Rank can beat S1 in Track 2 if event extraction is stable and rank turnover is controlled.
4. **Unlikely to justify full implementation immediately:** CEVA-KF/CIGA, KG-MoE-Lite, and HGF-MPC as full systems. Their report value is high, but they should not consume first-cycle build time before S1/DRO/ARMOR are working.
5. **Implement only if baseline is already strong:** KG-MoE-Lite, HGF-MPC, and CEVA-KF/CIGA. They should be built as overlays, verifiers, or report-centrepiece modules, not as the only production allocator.


## F. Report / Paper Quality Benchmark


This benchmark is separate from strategy scoring. It evaluates whether a design can become a strong NLPCC system report or shared-task paper contribution even if its Sharpe is not the highest.

**Report Quality Score formula**

`0.16 * CorePaperThesis + 0.12 * Visualisability + 0.14 * AblationCleanliness + 0.14 * MathematicalExplainability + 0.16 * NoveltyBeyondBaselines + 0.10 * FailureCaseInsight + 0.10 * ReproducibilityNarrative + 0.08 * SelectionLikelihood`

| Design | Core Paper Thesis | Visualisability | Ablation Cleanliness | Mathematical Explainability | Novelty Beyond Baselines | Failure-Case Insight | Reproducibility Narrative | Likelihood of Being Selected as Creative/Informative | Report Quality Score |
| :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- | :-- |
| DRO-BL-RP | Constrain noisy LLM-derived market views inside a robust BL/risk-parity allocator. | 7.5 | 8.8 | 8.8 | 6.5 | 7.5 | 8.8 | 7.2 | 7.89 |
| BSA-RP | Represent daily news as observations of latent macro regimes and allocate by regime-conditioned risk parity. | 8.6 | 8.4 | 8.4 | 7.3 | 8.0 | 8.2 | 7.8 | 8.14 |
| ARMOR-OMD | Use retrieval analogues and online mirror descent to adaptively weight robust baseline sleeves. | 8.2 | 8.5 | 7.8 | 7.0 | 7.8 | 8.6 | 7.5 | 7.84 |
| LEEQA-Rank | Convert event extraction into ETF ranking, then trade only rank-stable sector tilts. | 7.8 | 8.6 | 6.8 | 6.2 | 7.2 | 8.3 | 7.0 | 7.35 |
| HGF-MPC | Filter hidden drift with noisy expert/news views and optimise allocation through short-horizon MPC. | 8.8 | 7.6 | 9.0 | 7.6 | 8.3 | 7.1 | 8.0 | 8.09 |
| CEVA-KF | Use causal event-impact maps and invariant checks to separate stable transmission channels from spurious news correlations. | 8.7 | 7.8 | 8.6 | 9.0 | 9.0 | 6.2 | 8.7 | 8.44 |
| KG-MoE-Lite | Map policy/entity shocks onto an ETF-sector graph and route to specialist allocation experts. | 9.2 | 7.5 | 8.0 | 8.8 | 8.2 | 6.4 | 8.6 | 8.24 |


**Report-quality decisions.**

1. **Best report centrepiece:** CEVA-KF/CIGA. It has the clearest non-generic thesis: causal event-impact maps plus invariant filtering for hidden-regime robustness.
2. **Best performance-paper hybrid:** DRO-BL-RP. It is less novel than CEVA/KG, but the mathematics, implementation, and ablations are clean enough for a strong two-page system report.
3. **Best visual system:** KG-MoE-Lite, because graph activations, edge weights, policy-to-sector paths, and expert-routing diagrams are highly legible.
4. **Best ablation story:** DRO-BL-RP and ARMOR-OMD. Both support crisp no-news, no-view, no-DRO, no-turnover-control, no-retrieval, and fallback-only variants.
5. **Best fallback report if performance is weak:** BSA-RP or ARMOR-OMD. Even if Sharpe is modest, belief trajectories and online expert weights can explain why the system avoided catastrophic hidden-period failure.
6. **Sounds novel but weak report if mishandled:** Full TEMA, full KG-MoE, and full causal IRM. Without clean logs and ablations, these become diagrams without evidence.


## G. Competition vs Research Frontier


**Quadrant classification.**

| Quadrant | Designs | Interpretation |
| :-- | :-- | :-- |
| High competition / high research | DRO-BL-RP, BSA-RP, ARMOR-OMD | Best practical set. Build and compare first. |
| High competition / low research | Regime-HMM-RP, S1 quant core, inverse-vol/momentum baselines | Essential fallback and benchmark family, but not enough as the final paper thesis. |
| Low competition / high research | CEVA-KF/CIGA, KG-MoE-Lite, HGF-MPC, TEMA/RAMA-T | Strong narrative/visual value, but should be phased behind stable baselines. |
| Low competition / low research | Pure LLM allocator, simple sentiment-MVO, generic RAG summariser | Useful only as negative controls or rejected baselines. |
| Medium competition / medium research | LEEQA-Rank | Practical Track 2 extension if implementation time allows. |

**Second frontier: x-axis = Competition Score, y-axis = Report Quality Score.**

| Design | Competition Score | Report Quality Score | Frontier Reading |
| :-- | --: | --: | :-- |
| DRO-BL-RP | 7.37 | 7.89 | Best final submission candidate; high competition with adequate report signal. |
| BSA-RP | 7.01 | 8.14 | Very strong conservative/report hybrid; excellent if regime plots validate. |
| ARMOR-OMD | 7.08 | 7.84 | Safest adaptive fallback and strongest meta-allocation story. |
| LEEQA-Rank | 6.26 | 7.35 | Track 2 practical extension; not a full centrepiece. |
| KG-MoE-Lite | 5.37 | 8.24 | Best visual/Track 2 report candidate, but weak immediate ROI. |
| HGF-MPC | 6.14 | 8.09 | Macro-theory rich, implementation-heavy. |
| CEVA-KF/CIGA | 5.40 | 8.44 | Best research thesis, not the first production engine. |

**Named decisions.**

- **Best final submission candidate:** DRO-BL-RP with S1 fallback and ARMOR-OMD optional meta-weighting.
- **Best report centrepiece:** CEVA-KF/CIGA, written as a lightweight causal verification layer around the production allocator.
- **Safest fallback:** S1 quant core + ARMOR-OMD expert weighting.
- **Highest-upside/risk idea:** KG-MoE-Lite for Track 2; CEVA-KF/CIGA for shared-task-paper novelty.
- **Best Track 1 candidate:** DRO-BL-RP.
- **Best Track 2 candidate:** KG-MoE-Lite for report upside; LEEQA-Rank for one-student practical build.


## H. Recommended Final Architecture Stack


The final system should be layered. The production path should be deterministic after structured extraction; agentic behaviour must be constrained to schema-bound text processing and report explanation.

### Layer 0 — Official Data and Leakage Layer

- Use the **official DataLoader only** for in-agent data access.
- Enforce explicit date-split policy:
  - 2024: training and walk-forward model construction.
  - 2025: controlled A-list evaluation; avoid repeated hyperparameter tuning.
  - 2026-01-01 to 2026-06-01: hidden B-list only; no resources created after 2025.
- Enforce same-day news cutoff from official loader.
- Do **not** use current-day close/high/low/return before decision time.
- Add a `DataComplianceGuard`:
  - whitelist allowed fields;
  - assert no future timestamps;
  - block raw CSV access inside the agent loop;
  - log every feature timestamp used for each decision.

### Layer 1 — Baseline and Risk Core

Required baseline sleeves:

- equal weight;
- inverse-volatility;
- momentum;
- sector trend-following;
- S1 quant core:
  - Track 1: inverse-vol + momentum + defensive/breadth logic;
  - Track 2: sector trend-following top-k with volatility scaling;
- drawdown control:
  - cash/defensive sleeve when rolling drawdown or realised volatility breaches threshold;
- turnover control:
  - target-weight smoothing, no-trade band, maximum daily turnover cap;
- fallback-to-S1:
  - if extraction fails, optimizer infeasible, confidence too low, or logs become inconsistent.

### Layer 2 — Information Engine

Use these exact components:

1. **Event extractor**: schema-bound extraction into `{date, topic, asset_tags, sector_tags, macro_tags, direction, magnitude, confidence, evidence_span}`.
2. **View generator**: map event records into BL view matrix `P_t`, view vector `q_t`, and uncertainty `Omega_t`.
3. **Belief-state updater**: maintain regime posterior or confidence state for BSA-RP and risk gating.
4. **Retrieval analogue engine**: retrieve pre-2026 historical event-price analogues for ARMOR-OMD.
5. **Light causal verifier**: check whether proposed event-to-asset impacts agree with a frozen causal/sector map; downweight unsupported views.
6. **Local text encoder**: optional; if used, freeze model weights and cache all derived embeddings.

Do **not** use a free-form multi-agent debate system. If an LLM is used, it is a constrained extractor/verifier, not a portfolio allocator.

### Layer 3 — Mathematical Allocation Engine

Production engines:

- **DRO-BL-RP**:
  - BL prior from S1/risk-parity equilibrium;
  - news views from Layer 2;
  - robust shrinkage/ambiguity penalty;
  - turnover-constrained QP.
- **ARMOR-OMD**:
  - online mirror descent over sleeves: S1, DRO-BL, inverse-vol, momentum, defensive, sector trend.
- **Optional BSA-RP**:
  - regime posterior controls risk budget and defensive tilt.
- **Optional LEEQA-Rank / KG-MoE-Lite**:
  - Track 2-only sector tilts, passed through the same risk/turnover controls.

### Layer 4 — Explanation and Report Engine

For every trading day, export:

- daily decision trace;
- view-confidence maps;
- belief-state / regime posterior plots;
- graph activation diagrams if KG-MoE-Lite is enabled;
- event-to-asset attribution table;
- turnover diagnostics;
- drawdown and risk-budget diagnostics;
- ablation summary by day/window:
  - no-news;
  - no-LLM;
  - no-DRO;
  - no-turnover-control;
  - no-retrieval;
  - S1 fallback only.

### Layer 5 — Submission and Reproducibility Layer

- Docker image with pinned dependency lock.
- Frozen config file and config hash.
- Deterministic seeds for all stochastic routines.
- Local model weights or cached extraction files; no mandatory external API calls.
- Crash fallback:
  - if extraction/optimizer fails, return S1 target weights;
  - if S1 fails, return low-turnover inverse-vol/equal-weight defensive blend.
- Export logs, predictions, intermediate features, and environment manifest.

**Agentic vs deterministic boundary.**

| Component | Agentic? | Rule |
| :-- | :-- | :-- |
| News/event extraction | Limited agentic | Only schema-bound JSON; temperature zero; cache outputs. |
| Causal hypothesis generation | Limited agentic | Candidate-generation only; deterministic verifier decides use. |
| Portfolio optimisation | Deterministic | No LLM decisions; all weights produced by formulas/QP. |
| Turnover/drawdown controls | Deterministic | Hard constraints and thresholds. |
| Final trade adapter | Deterministic | Converts target weights to official buy/sell instructions. |
| Report explanation | Agentic allowed offline | Cannot affect submitted B-list decisions unless cached and compliant. |


## I. Implementation Priority and Phase Plan


The build plan assumes one strong student. The plan deliberately delays high-novelty systems until the baseline ladder is strong.

| Phase | Build | Deliverable | Time | Promotion Criterion | Stop Criterion |
| :-- | :-- | :-- | :-- | :-- | :-- |
| Phase 0R — Source/Data Reset | Official repo audit, data-loader wrapper, leakage whitelist, metric implementation. | `data_guard/`, safe feature API, source audit note, metric tests. | 1–2 days | Can reproduce allowed fields and reject disallowed current-day close/high/low/return. | Any uncertainty in official trade/data semantics remains unresolved. |
| Phase 1R — Official Starter Reproduction | Run official starter/client flow and confirm logs/trade semantics. | Reproducible local run for both tracks; saved daily logs. | 2–4 days | End-to-end backtest runs without manual intervention and logs all decisions. | Cannot reproduce starter or metric calculations. |
| Phase 2R — S0/S1 Baseline Rebuild | Equal weight, inverse-vol, momentum, sector trend, persistence, rule macro, news sentiment, S1 core. | Baseline report with 2024 walk-forward + 2025 locked evaluation. | 4–7 days | S1 beats naive baselines in at least one track and has acceptable turnover/drawdown. | S1 unstable; do not proceed to novelty until baseline is credible. |
| Phase 3R — First Innovative Prototype | **DRO-BL-RP only.** Deterministic rule-based views first; LLM extraction second. | BL prior, view mapping, robust QP, turnover adapter, ablations. | 7–12 days | Beats or matches S1 on 2024 walk-forward with better report signal and no material turnover deterioration. | News views degrade turnover-adjusted Sharpe or optimizer infeasible often. |
| Phase 4R — Second Prototype / Track Extension | **ARMOR-OMD only.** Meta-weight S1/DRO/trend/defensive sleeves using OMD and analogue confidence. | Expert-weight logs, regret curves, no-retrieval/no-online ablations. | 6–10 days | Improves robustness across 2024 subwindows or reduces drawdown without killing return. | Expert weights collapse to noise or turnover rises without Sharpe improvement. |
| Phase 5R — A-list Evaluation and Ablation | Controlled 2025 usage; freeze hyperparameters before final 2025 pass. | A-list result pack, ablation tables, selected submission candidate. | 4–7 days | One candidate beats S1 or gives clearly superior report package with no leakage. | Repeated 2025 tuning required to make results look good. |
| Phase 6R — B-list Hardening and Report Draft | Docker, dependency lock, cached extraction, crash fallback, two-page report draft. | Submission bundle + report figures + reproducibility manifest. | 4–7 days | No external dependency required; fallback passes all dry runs; report story is coherent. | Any mandatory API call, nondeterministic extraction, or unhandled crash path remains. |

**Controlled 2025 usage and overfit guard.**

- Tune hyperparameters only on 2024 subwindows.
- Use 2025 as a locked validation pass; allow at most one small, pre-declared correction round for implementation bugs.
- Report all 2025 experiments in a run ledger; do not silently discard failed attempts.
- Promotion requires stability across multiple 2024 subwindows, not a single 2025 run.

**Why Phase 3R is DRO-BL-RP.** It offers the highest expected competition ROI and the fastest path to a mathematically credible report. It can start with rule-based views, so it is not blocked by LLM extraction quality.

**Why Phase 4R is ARMOR-OMD.** It is the safest second prototype because it reuses all baselines, creates a fallback/meta-allocation layer, and can improve both tracks without requiring a graph or causal system to be perfect.


## J. Rejection, Deferral, and Ablation-Only List

| Design | Status | Reason | Condition for Revival |
| :-- | :-- | :-- | :-- |
| Pure LLM allocator | Reject | Prompt-to-weight lacks deterministic risk, turnover, and leakage controls; high B-list prompt instability. | Never as production. Use only as negative baseline. |
| Simple BL with LLM views but no robustness | Baseline only | Useful to show DRO value, but over-trusts noisy views and fragile covariance estimates. | Can be revived only as an ablation inside DRO-BL-RP. |
| Generic RAG summariser | Reject | Retrieval summaries without formal allocator are narrative overfitting, not portfolio optimisation. | Only if converted into ARMOR-style analogue retrieval with deterministic online update. |
| Multi-agent debate | Reject | High cost, nondeterminism, weak reproducibility, and no direct link to Sharpe/drawdown/turnover. | Offline report commentary only, never inside B-list decision loop. |
| Heavy fine-tuning | Defer / usually reject | One-student burden, resource-submission complexity, and high data-compliance risk. | Only small local extractor fine-tune with full data, scripts, weights, and pre-2026 provenance. |
| Deep RL / graph RL | Reject | Small ETF universe and limited periods make RL overfit-prone; hard to debug under hidden B-list. | Only if a simple policy-gradient ablation is needed for the report, not as submission engine. |
| Overly complex causal model | Defer | Full SCM/IRM may become unverifiable causal storytelling. | Use a small frozen causal map with transparent event-to-sector channels and falsifiable ablations. |
| Full KG-MoE if baseline is weak | Defer | Graph work is only useful after a strong quant baseline; otherwise it masks basic execution weaknesses. | Revive after S1 and DRO-BL-RP are stable; start with KG-MoE-Lite only. |
| Transformer memory if event extraction is unstable | Defer | TEMA/RAMA-T amplifies noisy embeddings and analogue errors. | Revive only after extraction has >90% schema validity and retrieval ablations show value. |
| News sentiment only | Baseline only | Too simple, likely to overreact, but useful as a no-structure text baseline. | Keep only for ablation and report comparison. |
| End-to-end graph neural network | Defer | Implementation and data volume do not justify training a deep graph model first. | Only after static graph scores demonstrate stable incremental value. |

## K. Final Recommendation


### Final Build Plan

- **Primary competition candidate:** DRO-BL-RP with S1 anchor, robust view uncertainty, turnover-constrained QP, and deterministic trade adapter.
- **Primary research / award candidate:** CEVA-KF/CIGA as a lightweight causal/invariant verification layer and report narrative, not as the first production allocator.
- **Safe fallback:** S1 quant core + ARMOR-OMD meta-weighting; if ARMOR is unstable, use S1 alone with inverse-vol/momentum/defensive sleeves.
- **Best Track 1 design:** DRO-BL-RP.
- **Best Track 2 design:** KG-MoE-Lite for report upside; LEEQA-Rank for practical one-student Track 2 implementation.
- **First prototype to implement:** DRO-BL-RP.
- **Second prototype to implement:** ARMOR-OMD.
- **Designs to reject:** pure LLM allocator, generic RAG summariser, multi-agent debate allocator, deep RL / graph RL, heavy fine-tuning as a first-cycle plan.
- **Designs to keep as ablations:** simple BL without robustness, sentiment-only, Regime-HMM-RP, OCO-Ensemble without retrieval, no-news S1, no-DRO BL, no-turnover-control QP.
- **Minimum ablation package:** EW, inverse-vol, momentum, sector trend, S1, news sentiment only, BL prior only, BL + views, BL + views + DRO, DRO-BL-RP without LLM, DRO-BL-RP with LLM/cached extraction, S1 fallback only, ARMOR-OMD without retrieval, ARMOR-OMD without online update, no-turnover-control.
- **Final submission policy:** Submit only the most robust candidate that either beats S1 on 2024 walk-forward and remains stable on locked 2025, or gives a strong report-quality improvement without materially worsening turnover-adjusted Sharpe. If no innovation clears this bar, submit S1 + deterministic fallback rather than a fragile novel system.
- **System report thesis:** “A leakage-safe LLM investment advisor should not let the LLM choose weights; it should convert financial hot news into bounded, auditable views, then let robust portfolio mathematics, online fallback, and deterministic risk controls decide the allocation.”

**Decisive build order.**

1. Build the official safe data layer and baseline ladder.
2. Build DRO-BL-RP first.
3. Add ARMOR-OMD as the cross-track fallback/meta-allocator.
4. Add BSA-RP if regime plots look informative and time permits.
5. Add LEEQA-Rank only if Track 2 needs a practical extension.
6. Add KG-MoE-Lite or CEVA-KF/CIGA only as report-centrepiece modules after the production candidate is stable.
