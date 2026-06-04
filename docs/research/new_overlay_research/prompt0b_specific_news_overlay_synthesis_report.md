# Prompt0B Synthesis Report — Specific News Overlay Method Selection

**Generated:** 2026-06-04  
**Scope:** Synthesis of uploaded Prompt20 repository-state files, Prompt0A broad news-overlay research, and Prompt0A-Enhance specific-method reports.  
**Status:** Research synthesis only. No production code, no official-runtime change, no 2025 tuning, and no hidden-2026 assumption.

## 1. Executive Decision

The next implementation phase should **not** begin with transformer embeddings, graph propagation, learned attention, or an LLM allocator. It should begin with a **deterministic, event-study-calibrated, permutation-tested news overlay architecture** that can be audited against preserved baselines.

The selected first-build method is:

> **Event-Study Calibrated News Impact Overlay (ESC-NIO), implemented with a Permutation-Tested News Attention Index (PT-NAI) signal layer and bounded gated overlays.**

This is a method bundle, but the lead method is ESC-NIO because it answers the central question: *which event classes have historically produced measurable ETF/sector responses under 2024-only calibration?* PT-NAI is the canonical intermediate signal; RIC-SNM is the Track B ranking/sizing wrapper; VS-MNRG is the Track A risk-control wrapper.

The selected second-build method is:

> **Transformer-Cached Text-to-Sector Relevance + Rule Impact Gate (TC-TRIG).**

TC-TRIG should be built only after the deterministic lexical/event-study baseline exists and has passed zero-news and shuffled-news ablations. Its purpose is to improve **relevance mapping**, not to replace the deterministic impact, sensitivity, and gating logic.

**Track-specific decision:**

- **Track A:** Use news mainly as a **macro risk gate**, not as a return-chasing allocator. Best method: **Volatility-Scaled Macro News Risk Gate (VS-MNRG)** fed by the macro subset of PT-NAI/ESC-NIO.
- **Track B:** Use news as a **sector-ranking and bounded sector-tilt signal**. Best method: **Rank-IC Gated Sector News Momentum (RIC-SNM)** using ESC-NIO/PT-NAI signals.
- **Shared front end:** Event taxonomy, duplicate clustering, impact scoring, lexical relevance, confidence scoring, and timestamp-safe extraction should be shared.
- **Separate downstream logic:** Track A and Track B must diverge at the sensitivity, gate, and overlay stage.

The official final runtime remains unchanged until a later implementation passes all promotion gates.

## 2. Evidence Used

### 2.1 Uploaded File Summary

| File | Type | Content Summary | Quality | Strength | Weakness |
| --- | --- | --- | --- | --- | --- |
| current_repo_status_report.md | Prompt20 repo-state status dossier | Confirms official runtime is frozen, lists stage status, known risks, claims/non-claims, and recommends next-stage news/text research. | High | Authoritative for current repo state; concise; directly actionable. | No method-level synthesis; does not evaluate new overlays. |
| current_repo_status_table.md | Layer-by-layer repo status table | Condenses official runtime, preserved candidates, Stage 1–4, adapter, replay, and packaging status into one operational table. | High | Best quick map of where a news overlay can plug in. | Only a table; limited narrative and no research-method prioritisation. |
| evidence_inventory_summary.md | Evidence inventory status stub | States that 23 evidence rows are present. | Medium | Useful as a sanity signal that prior evidence inventory exists. | Too short to support method choice or audit logic. |
| executive_summary.md | Prompt20 executive summary | Confirms readiness for human submission review, preserved candidates, package/handoff pass status, and Prompt21A recommendation. | High | Clear executive framing; reinforces that this phase is research-only. | No technical details beyond high-level state. |
| final_wrapup_recommendation.md | Prompt20 final wrap-up recommendation | Reiterates frozen runtime, preserved candidate layer, no NewsEnhance/transformer implementation, and what can/cannot be claimed. | High | Strong constraint source; prevents accidental overclaiming. | Does not provide specific next methods. |
| next_stage_news_text_overlay_workflow.md | News/Text next-stage workflow | Defines staged workflow: discuss, research, localisation, bounded MVP execution, review, ablations, parity, and risk controls. | Very High | Best source for implementation sequencing and promotion discipline. | Does not rank concrete methods from Prompt0A-Enhance. |
| next_stage_prompt_plan.md | Prompt backlog table | Lists proposed Prompt21A–Prompt28 sequence and expected deliverables/constraints. | High | Useful for Prompt0C documentation planning. | Backlog-level only; not method-specific. |
| preserved_candidate_summary.md | Preserved candidate manifest summary | Lists 5 macro and 5 sector candidates, official/fallback/comparator roles, config paths, and preservation reasons. | Very High | Direct baseline map for overlay evaluation. | No performance metrics or overlay design details. |
| news_overlay_deepresearch_gemini.md | Prompt0A broad design-space report + Prompt0A-Enhance response transcript | Covers design families: deterministic rules, taxonomy/impact, NAI, sensitivity, gated overlay, offline transformer cache, hybrid model, lightweight attention. | Medium-High | Strong breadth and constraint awareness; useful for design-family backdrop. | Contains prompt transcript as well as report; some source references are embedded but not normalised; broad rather than final synthesis. |
| news_overlay_deepresearch_perplexity.md | Prompt0A-Enhance specific-method report | Identifies ESC-NIO, RIC-SNM, PT-NAI, VS-MNRG, SESRO, BL-NVO, ES-GPNS, TC-TRIG with algorithms, ablations, and promotion criteria. | High | Best specific-method shortlist; strongest algorithmic detail and direct first-build recommendations. | Ranking sometimes treats multiple first-build components as separate methods, requiring synthesis/cluster collapse. |
| news_overlay_deepresearch_chatgpt.md | Prompt0A-Enhance specific-method report | Provides an expanded, more critical method map with top-ten table, Track A/B split, first-build stack, and promotion discipline. | Very High | Best synthesis-quality input; strongest reasoning on track split, dependency risks, and first-build stack. | Not in the exact requested Prompt0B structure; needs consolidation into one selected architecture. |

### 2.2 Report Quality, Strength, and Weakness Audit

| Report Group | Quality | Strength | Weakness / Caveat |
| --- | --- | --- | --- |
| Prompt20 repo-state documents | Very High for constraints | Ground the frozen runtime, preserved candidates, existing pipeline maturity, and official parity discipline. | Do not contain new method research; must be combined with Prompt0A/0A-Enhance. |
| Prompt0A broad design-space report | Medium-High | Good coverage of design families and staged build logic; warns against online LLM / full neural allocators. | Too broad; method names are not sufficiently implementation-ready without Prompt0A-Enhance. |
| Perplexity Prompt0A-Enhance | High | Strong concrete shortlist, clean formulas, explicit ablations and final recommendation block. | Some choices remain component-level rather than architecture-level; external citation tags are not directly verifiable here. |
| ChatGPT Prompt0A-Enhance | Very High | Most balanced source for selection: event-study first, PT-NAI as canonical signal, VS-MNRG for Track A, RIC-SNM for Track B, TC-TRIG second. | Slightly expansive; still requires a single architecture boundary and promotion gate. |

### 2.3 Main Evidence Synthesis

The repository-state files establish the hard boundary: official runtime is frozen; preserved candidates are available as baselines; Stage 1 news and Stage 2 text stores are still MVP-level; Stage 3 and official-semantics replay are stable enough to support evaluation; and future news overlay work must remain research-only until ablations, replay, and parity checks justify promotion.

The three research/enhancement reports converge on the same architecture:

1. Use deterministic event extraction and event taxonomy as the first layer.
2. Build a transparent News Attention Index rather than an end-to-end allocator.
3. Calibrate event impact and ETF/sector sensitivity on 2024 only.
4. Apply small gated overlays on preserved base allocators.
5. Treat transformer relevance as an optional second-build cache with lexical fallback.
6. Reject full LLM allocators, deep RL, graph RL, and unconstrained neural portfolio systems for this phase.

## 3. Current Baseline Interpretation

The baseline state is disciplined and should be preserved.

**Official runtime:**

| Track | Primary | Fallback | Interpretation |
|---|---|---|---|
| Track A / Macro | `p18_rp_macro_w10_s5` | `p18_rp_macro_w40_s5` | No-news risk-parity family remains strongest and safest. |
| Track B / Sector | `p18_leeqa_sector_k5_temp35` | `p18_s1_sector_t35_v30_w20` | Rule-news LEEQA-style ranking is useful; no-news S1 remains fallback. |

**Preserved baselines for overlay research:**

| Track | Preserved candidates |
|---|---|
| Track A | `p18_rp_macro_w10_s5`, `p18_rp_macro_w40_s5`, `p18_rp_macro_w20_s5`, `p18_bsa_macro_t10_g65`, `p18_rp_macro_w60_s5` |
| Track B | `p18_leeqa_sector_k5_temp35`, `p18_s1_sector_t35_v30_w20`, `p18_leeqa_sector_k5_temp20`, `p18_leeqa_sector_k5_temp70`, `p18_leeqa_sector_k3_temp20` |

**Implication for Prompt0B:** The correct target is not a new allocator. The correct target is a **bounded overlay** that can be disabled to recover the preserved base allocator exactly.

## 4. Specific Method Shortlist from Prompt0A-Enhance

| Method | Core Framework | Track A Fit | Track B Fit | Main Signal | Overlay Type | Text Dependency | Training/Tuning Needs | 2025 Test Plan | Ablation Requirements | Implementation Risk | Promotion Readiness |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| ESC-NIO | Event-study calibrated impact | Moderate-high as macro risk event calibration | Very high for sector event response | Signed abnormal-return response | Bounded active tilt | Lexical/rule first; semantic optional | 2024 event windows, CAAR, sensitivity, gates | Frozen 2025 replay | base/real/zero/shuffle/label/random/window/gate sweeps | Sparse classes, overlapping events | Highest |
| PT-NAI | Permutation-tested attention index | High as macro stress index | High as sector signal layer | Impact × relevance × direction × confidence × sensitivity | Input signal to gates/overlays | Lexical/rule first | 2024 component weights and permutation filters | Frozen 2025 index | component removal, shuffle, zero, sign, regime splits | Weak null design | Very high as intermediate signal |
| RIC-SNM | Rank-IC sector momentum | Low-moderate | Very high | Sector rank adjustment | Top-k / rank-proportional tilt | Uses NAI/event scores | 2024 rank-IC/horizon/lags | Frozen 2025 sector ranking | IC gate on/off, lag sweep, horizon sweep | Noisy IC in small universe | High for Track B only |
| VS-MNRG | Macro news risk gate | Very high | Moderate as global throttle | Risk multiplier / de-risking signal | Risk scaling not alpha tilt | Macro event taxonomy | 2024 stress/easing thresholds | Frozen 2025 risk scaling | vol-only vs news+vol, stress-only vs two-sided | Whipsaw / opportunity cost | High for Track A only |
| TC-TRIG | Offline transformer relevance cache | Moderate | High | Semantic relevance/confidence | Enhancement to NAI/ESC-NIO | Offline model/cache; lexical fallback | 2024 threshold/prototype/cache audit | Frozen 2025 cache logic | lexical vs dense vs hybrid, cache disabled | Dependency and packaging risk | Second-build only |
| SESRO | Sparse event regression | Moderate | High | Predicted event response | Regression-driven tilt | Structured event features | 2024 sparse model + stability selection | Frozen 2025 coefficients | sparse/dense, feature removal, random coeffs | Feature overfit | Ablation/later |
| BL-NVO | Black-Litterman news views | High if views are sparse | Moderate-high | Posterior expected return views | Constrained posterior tilt | Consumes validated signals | 2024 confidence/covariance/view mapping | Frozen 2025 | prior-only, zero views, random views | Matrix/parameter fragility | Ablation/later |
| CW-EG | Exponentiated-gradient overlay | Moderate | Moderate-high | Multiplicative active update | Simplex-preserving overlay | Consumes validated signal | 2024 learning rate/blend/caps | Frozen 2025 | additive vs multiplicative, eta sweep | Compounding false positives | Ablation only |
| ES-GPNS | Entity-sector graph propagation | Low-moderate | High if graph quality good | Propagated relevance score | Relevance enhancement | Entity extraction + graph | 2024 ontology/edge weights | Frozen graph in 2025 | direct vs graph, random edges | Ontology brittleness | Deferred |
| HAN/QKV | Learned attention pooling | Low | Moderate | Learned pooled news vector | Research comparator | Model training | 2024-only tiny/frozen | Frozen 2025 | attention vs deterministic NAI | Overfit and interpretability theatre | Reject for promotion |

## 5. Method Clustering and Redundancy Analysis

| Cluster | Methods Included | Redundancy / Collapse Decision | Synthesis Decision |
| --- | --- | --- | --- |
| Core deterministic signal-and-impact cluster | ESC-NIO, PT-NAI | Merge as first-build architecture: PT-NAI is the transparent daily signal; ESC-NIO calibrates impact/sensitivity; both feed the same gates. | Build first |
| Track B ranking cluster | RIC-SNM, ESC-NIO sector tilts | RIC-SNM is not a separate text model; it is the Track B validation/sizing wrapper for ESC/PT-NAI signals. | Build first for Track B |
| Track A risk-control cluster | VS-MNRG, macro subset of PT-NAI/ESC-NIO | Track A should not imitate sector momentum. It should consume macro stress/easing scores as risk multipliers. | Build first for Track A |
| Second-stage relevance cluster | TC-TRIG, ES-GPNS, BM25/entity maps | TC-TRIG and ES-GPNS address relevance, not impact. They should be benchmarked against lexical/entity maps after the deterministic stack works. | TC-TRIG second; ES-GPNS defer |
| Supervised response cluster | SESRO, event-study response tables | SESRO competes with ESC-NIO for response estimation; it is more flexible but less robust under small samples. | Ablation/later |
| Portfolio-theory overlay cluster | BL-NVO, CW-EG, additive clipped tilts | BL/CW-EG operate after signals exist. They should test whether sophisticated overlay maths beats clipped additive tilts. | Ablation-only initially |
| Neural aggregation cluster | HAN/QKV attention pooling | Mostly a research comparator. Not needed for first implementation and unsafe as a promotion candidate. | Reject for promotion |

The key collapse decision is that **ESC-NIO, PT-NAI, RIC-SNM, and VS-MNRG are not four competing first-build production systems**. They are four layers of a coherent deterministic architecture:

1. **PT-NAI** creates the daily interpretable signal.
2. **ESC-NIO** calibrates event-class and asset/sector sensitivity.
3. **RIC-SNM** validates and sizes Track B sector ranking effects.
4. **VS-MNRG** translates broad macro news into Track A risk scaling.

By contrast, **TC-TRIG** and **ES-GPNS** are relevance-improvement methods. They should not be built before the deterministic relevance baseline, because otherwise there is no clean way to measure their incremental value.

## 6. Comparative Strategy Table

**Scoring scale:**  
For Track A Value, Track B Value, Expected Alpha, Robustness, Interpretability, Ablation Quality, and Official Compatibility, **5 = best** and **1 = worst**.  
For Implementation Cost, Dependency Risk, and Leakage Risk, **1 = lowest / best** and **5 = highest / worst**.  
Overall Score is a synthesis score on a 0–100 scale, penalising cost, leakage risk, dependency risk, and overfitting risk.

| Rank | Method | Method Cluster | Track A Value | Track B Value | Expected Alpha | Robustness | Interpretability | Implementation Cost | Dependency Risk | Leakage Risk | Ablation Quality | Official Compatibility | Overall Score | Decision |
| ---: | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Event-Study Calibrated News Impact Overlay (ESC-NIO) | Event-study CAR/CAAR + bounded additive overlay | 4.2 | 5.0 | 4.7 | 4.6 | 4.8 | 3.0 | 1.0 | 2.0 | 5.0 | 4.8 | 84.0 | build_first |
| 2 | Permutation-Tested News Attention Index (PT-NAI) | Impact × relevance × direction × confidence × sensitivity signal with null filtering | 4.0 | 4.8 | 4.5 | 4.5 | 4.9 | 2.7 | 1.0 | 1.7 | 5.0 | 4.9 | 82.5 | build_first |
| 3 | Rank-IC Gated Sector News Momentum (RIC-SNM) | Cross-sectional sector factor validation and ranking overlay | 2.4 | 5.0 | 4.4 | 4.2 | 4.5 | 2.4 | 1.0 | 2.0 | 4.8 | 4.8 | 78.5 | build_first |
| 4 | Volatility-Scaled Macro News Risk Gate (VS-MNRG) | Macro stress/easing news mapped to risk multiplier | 5.0 | 3.2 | 3.9 | 4.7 | 4.7 | 2.0 | 1.0 | 1.5 | 4.8 | 5.0 | 78.0 | build_first |
| 5 | Transformer-Cached Text-to-Sector Relevance + Rule Impact Gate (TC-TRIG) | Offline embedding/cached relevance, deterministic impact gate | 3.0 | 4.6 | 4.1 | 3.7 | 3.7 | 3.8 | 2.8 | 2.5 | 4.4 | 3.8 | 66.0 | build_second |
| 6 | Sparse Event-Sensitivity Regression Overlay (SESRO) | Elastic-net/LASSO event-feature response model | 3.0 | 4.5 | 4.0 | 3.8 | 4.0 | 3.3 | 1.2 | 2.4 | 4.7 | 4.5 | 65.0 | ablation_only |
| 7 | Black-Litterman News View Overlay (BL-NVO) | Prior-plus-news-views posterior tilting | 4.0 | 3.8 | 3.8 | 3.8 | 4.0 | 3.4 | 1.2 | 2.2 | 4.4 | 4.0 | 63.0 | ablation_only |
| 8 | Confidence-Weighted Exponentiated-Gradient Overlay (CW-EG) | Multiplicative simplex-preserving active overlay | 3.3 | 3.8 | 3.5 | 3.5 | 3.4 | 2.9 | 1.2 | 2.4 | 4.2 | 4.3 | 60.0 | ablation_only |
| 9 | Entity-Sector Graph Propagation News Score (ES-GPNS) | Entity-event-sector graph propagation | 2.5 | 4.1 | 3.6 | 3.0 | 3.1 | 4.1 | 3.0 | 2.8 | 3.8 | 3.4 | 52.0 | defer |
| 10 | Hierarchical Daily News Attention Pooling (HAN/QKV Pooling) | Learned attention pooling over daily news | 2.2 | 3.8 | 3.5 | 2.7 | 2.5 | 4.4 | 3.5 | 3.2 | 3.4 | 2.8 | 44.0 | reject |

## 7. Selected First-Build Method

### 7.1 Method Name

**Event-Study Calibrated News Impact Overlay (ESC-NIO) with Permutation-Tested News Attention Index (PT-NAI).**

Short name for documentation:

```text
esc_nio_ptnai_gated_overlay
```

### 7.2 Why This Method

ESC-NIO is the best first-build method because it is:

- explicit and mathematically grounded;
- compatible with daily Top-20 news and ETF/index histories;
- trainable/tunable on 2024 only;
- testable on frozen 2025;
- modular enough to sit on preserved baselines;
- deterministic at runtime when built with lexical/rule features;
- ablation-friendly through zero-news, shuffled-news, random labels, and gate-on/off tests;
- compatible with official-server validation if dependency footprint is kept minimal.

It also avoids the main failure mode of generic sentiment overlays: treating all news as equally relevant or all sentiment as tradable.

### 7.3 Core Algorithm

For each decision date \(t\):

1. **Collect timestamp-safe news.** Use only Top-20 news items available before the official cutoff.
2. **Deduplicate and cluster near-identical items.** Prevent one policy event from being counted multiple times.
3. **Extract event attributes.** Assign each item:
   - event class \(c_i\);
   - direction \(d_i \in \{-1,0,1\}\);
   - impact score \(I_i\);
   - relevance \(R_{i,j}\) for asset/sector \(j\);
   - confidence \(C_{i,j}\).
4. **Calibrate 2024 event response.** Estimate short-window abnormal responses for each \((j,c)\) pair using 2024 only.
5. **Create PT-NAI signal.** Aggregate impact, relevance, direction, confidence, and sensitivity into a daily signal.
6. **Run null filters.** Use permutation or shuffled-date tests inside 2024 to suppress unstable event-class/asset pairs.
7. **Apply gates.** Require impact, confidence, sensitivity/rank-IC, drawdown, and turnover gates to pass.
8. **Compute bounded overlay.** Apply a clipped tilt relative to the preserved base allocation.
9. **Fallback to base.** If any required input is missing or gates fail, return base weights exactly.

### 7.4 Mathematical Formulation

A simple normal-return model for asset \(j\) is:

\[
R_{j,t} = \alpha_j + \beta_j R_{m,t} + \epsilon_{j,t}.
\]

The abnormal return is:

\[
AR_{j,t} = R_{j,t} - (\hat\alpha_j + \hat\beta_j R_{m,t}).
\]

For event \(e\) in class \(c\), the short-window cumulative abnormal return is:

\[
CAR_{e,j,c}(L,U)=\sum_{\tau=L}^{U} AR_{j,t_e+\tau}.
\]

The 2024 event-class sensitivity is:

\[
Sens_{j,c}=\operatorname{shrink}\left(
\frac{\operatorname{median}_e CAR_{e,j,c}(L,U)}{\sigma_j + \varepsilon}
\right).
\]

The daily raw news attention signal is:

\[
NAI_{t,j}=\sum_{i\in \mathcal N_t}
I_i\,R_{i,j}\,d_i\,C_{i,j}\,Sens_{j,c_i}\,e^{-\lambda\Delta t_i}.
\]

A permutation-tested version is:

\[
\widetilde{NAI}_{t,j}=NAI_{t,j}\cdot
\mathbf 1\{p_{j,c_i}\le \alpha,\; \text{sign stability passes}\}.
\]

The active gate is:

\[
G_{t,j}=\mathbf 1\{
|\widetilde{NAI}_{t,j}|>\tau_S,
C_{t,j}>\tau_C,
Sens_{j,c}>\tau_{sens},
TurnoverBudget_t>0,
DrawdownThrottle_t=0
\}.
\]

The bounded overlay is:

\[
\Delta w_{t,j}=G_{t,j}\cdot
\operatorname{clip}(\kappa_j \widetilde{NAI}_{t,j},-m_j,m_j).
\]

The final portfolio is:

\[
w_t^{final}
=
\operatorname{normalize\_and\_cap}(w_t^{base}+\Delta w_t).
\]

### 7.5 Required Inputs

| Input | Source | Notes |
|---|---|---|
| Daily Top-20 news | Official task feed | Must obey timestamp cutoff. |
| Preserved base weights | Current official/preserved configs | Overlay must recover these weights under zero signal. |
| ETF/index returns | Historical price data | 2024 calibration; 2025 frozen test. |
| Event taxonomy | Deterministic rules first | Macro, sector, policy, regulation, liquidity, crisis, industry categories. |
| Relevance map | Lexical/entity first | Embedding relevance deferred to TC-TRIG. |
| Impact/confidence rules | Deterministic | Frequency, novelty, source agreement, policy-action strength, duplicate control. |
| Turnover/drawdown state | Backtester/replay | Required for promotion-grade gates. |

### 7.6 Output Signal

The first-build method emits:

```text
date, asset_or_sector, raw_nai, filtered_nai, event_class, sensitivity, confidence, gate_state, delta_weight
```

The signal should be written to traceable reports before any portfolio-performance interpretation.

### 7.7 Track A Integration

Track A should use the macro subset of ESC-NIO/PT-NAI through **VS-MNRG**.

Rules:

- Do not use sector-style rank chasing.
- Use only broad macro-policy, liquidity, property-systemic, geopolitical, crisis, and market-stress categories.
- Map the signal to a risk multiplier, not a large return forecast.
- De-risk risky sleeves only when signal strength and confidence pass.
- Reallocate residual exposure to predefined defensive sleeves according to a fixed rule.
- If no strong macro signal exists, return `p18_rp_macro_w10_s5` or the selected preserved macro base unchanged.

### 7.8 Track B Integration

Track B should use ESC-NIO/PT-NAI through **RIC-SNM**.

Rules:

- Use sector-level event classes and relevance maps.
- Validate sector scores through 2024 rank-IC and horizon analysis.
- Apply only small top-k or rank-proportional perturbations to preserved Track B allocators.
- Treat `p18_leeqa_sector_k5_temp35` as the main base and `p18_s1_sector_t35_v30_w20` as a no-news/fallback comparator.
- Add positive tilts only when event impact, relevance, sensitivity, confidence, and rank-IC gates pass.
- Use negative sector news mainly to reduce or exclude weak sectors, subject to turnover caps.

### 7.9 2024 Training / Tuning

All of the following must be fixed using 2024 only:

- event taxonomy granularity;
- duplicate-clustering thresholds;
- normal-return model;
- event windows \(L,U\);
- sensitivity shrinkage rules;
- impact/relevance/confidence thresholds;
- permutation-test p-value threshold;
- Track A risk-gate parameters;
- Track B rank-IC horizons and lag weights;
- overlay strength \(\kappa\);
- maximum active tilt \(m_j\);
- turnover cap;
- drawdown throttle.

No threshold, class, weight, or horizon may be selected using 2025 outcomes.

### 7.10 2025 Frozen Testing

2025 must be a single frozen evaluation:

1. Load the frozen 2024 taxonomy, response tables, gates, and overlay parameters.
2. Replay 2025 under official semantics.
3. Compare against all relevant preserved baselines.
4. Run the full ablation suite.
5. Do not retune after seeing 2025 results.
6. Record trace-level evidence for event extraction, gate state, and final weight deltas.

### 7.11 Required Ablations

Minimum ablation suite:

| Ablation | Purpose |
|---|---|
| Base allocator only | Measures preserved baseline without overlay. |
| Real news overlay | Main candidate. |
| No-news variant | Ensures pipeline can run with news detached. |
| Zero-news signal | Must recover base weights exactly or near-exactly. |
| Shuffled-news dates | Tests whether timing-specific news information matters. |
| Randomised event labels | Tests whether event taxonomy carries directional content. |
| Impact gate disabled | Detects overtrading on trivial news. |
| Sensitivity gate disabled | Tests value of 2024 event-response calibration. |
| Confidence gate disabled | Tests whether low-confidence events are harmful. |
| Lexical relevance vs embedding relevance | Required once TC-TRIG exists. |
| Overlay strength sweep | Finds fragility to tilt scale. |
| Turnover cap sweep | Measures friction sensitivity. |
| Event-category removal | Identifies which categories matter. |
| Track A only / Track B only | Confirms track-specific utility. |
| High-volatility vs low-volatility regimes | Tests stress-period robustness. |

### 7.12 Implementation Boundary

First build may include:

- deterministic event taxonomy;
- lexical/entity relevance;
- duplicate clustering;
- impact/confidence scoring;
- 2024-only event response tables;
- PT-NAI signal generation;
- Track A macro risk gate;
- Track B rank-IC gate;
- bounded additive overlay;
- trace outputs and ablation switches.

First build must not include:

- online LLM/API calls;
- model downloads;
- final-runtime package changes;
- transformer dependency as required runtime path;
- hidden 2026 information;
- 2025 threshold selection;
- direct summary-to-allocation logic;
- deep RL, graph RL, or unconstrained neural allocation.

### 7.13 Risks

| Risk | Severity | Mitigation |
|---|---:|---|
| Sparse event classes produce unstable CAAR estimates | High | Merge rare classes; shrink sensitivity toward zero; require minimum event counts. |
| Duplicate policy headlines overcount one event | High | Add duplicate clustering and event-instance IDs. |
| Same-day timestamp leakage | Critical | Strict cutoff audit and trace event availability. |
| 2024 regime overfit | High | Walk-forward 2024 validation, shuffled-news tests, zero-news tests, frozen 2025 replay. |
| Excess turnover | High | Turnover cap, tilt cap, activation threshold, drawdown throttle. |
| Track A whipsaw | Medium-High | Use news as risk gate only; require strong macro stress/easing confidence. |
| Track B noisy rank changes | Medium-High | Rank-IC gate, lag smoothing, top-k stability constraint. |

## 8. Second-Build Method

The selected second-build method is:

> **Transformer-Cached Text-to-Sector Relevance + Rule Impact Gate (TC-TRIG).**

It should be built only after the deterministic stack has a working lexical/entity relevance baseline and complete ablation reports.

### Second-build role

TC-TRIG should improve \(R_{i,j}\), the news-to-asset/sector relevance term. It should not change:

- event-study impact calibration;
- direction rules unless separately justified;
- 2024-only tuning discipline;
- zero-news fallback;
- official-runtime dependency rules.

### Required design

1. Pin a pre-2026 Chinese embedding or financial-sentiment model.
2. Generate cached news embeddings and sector/ETF prototype embeddings offline.
3. Compute cosine relevance or prototype similarity.
4. Blend with lexical/entity relevance through a 2024-tuned scalar.
5. Keep lexical relevance as mandatory fallback.
6. Test lexical-only, dense-only, and hybrid relevance as separate ablations.

### Promotion posture

TC-TRIG is **not promotion-ready by default**. It becomes promotion-eligible only if it beats lexical/entity relevance under frozen 2025 replay, survives cache-disabled fallback tests, and passes official dependency/package audits.

## 9. Ablation-Only Methods

The following methods should be retained as ablations but not selected as first-build promotion candidates:

| Method | Why retain | Why not first-build |
|---|---|---|
| Sparse Event-Sensitivity Regression Overlay (SESRO) | Tests whether sparse supervised event-response modelling beats event-study tables. | Higher overfitting risk under limited 2024 data; feature engineering can become too rich. |
| Black-Litterman News View Overlay (BL-NVO) | Tests whether Bayesian view integration improves over clipped additive tilts. | Adds covariance/view-confidence complexity before signals are proven. |
| Confidence-Weighted Exponentiated-Gradient Overlay (CW-EG) | Tests multiplicative overlay geometry and simplex preservation. | Can amplify persistent false positives; less transparent than additive tilts. |
| Hierarchical Daily News Attention Pooling | Useful research comparator for learned news aggregation. | Too high overfit/dependency/interpretability risk for promotion. |

## 10. Deferred or Rejected Methods

### Deferred

| Method | Reason |
|---|---|
| Entity-Sector Graph Propagation News Score (ES-GPNS) | Potentially useful for indirect relevance, but ontology errors, graph-edge attribution, and engineering complexity are too high before simple relevance is proven. |
| Cross-encoder reranking | More accurate but heavier; should only appear after lexical/BGE-cache benchmarks exist. |

### Rejected for current phase

| Method class | Reason |
|---|---|
| Online LLM allocator | Violates no online API dependency and is not reproducible enough. |
| Full neural portfolio allocator | Too hard to ablate and too fragile under 2024-only training. |
| Deep RL / graph RL allocator | High overfit, high dependency, poor official compatibility. |
| Unconstrained RAG summary-to-trade system | Converts text into allocation without transparent gates or falsifiable intermediate signals. |
| End-to-end transformer allocation | Not justified by data size, interpretability requirements, or official-server constraints. |

## 11. Track A News Overlay Plan

**Objective:** Improve drawdown and volatility control without weakening the no-news risk-parity base.

Recommended Track A architecture:

```text
base macro risk-parity weights
+ macro PT-NAI / ESC-NIO stress-easing signal
+ VS-MNRG risk multiplier
= final macro weights
```

Track A signal categories:

- monetary/liquidity easing;
- fiscal stimulus;
- property-sector systemic support/stress;
- broad equity risk-on/risk-off sentiment;
- geopolitical/export shock;
- crisis/systemic risk;
- bond/gold defensive demand.

Track A should optimise:

- max drawdown;
- volatility-adjusted return;
- Sharpe stability;
- turnover containment;
- exact fallback to base weights.

Track A should **not** optimise a daily directional news-alpha model first. The preserved winner is no-news risk parity; the overlay must justify itself as a risk-control layer.

## 12. Track B News Overlay Plan

**Objective:** Improve sector selection/ranking while preserving turnover and drawdown discipline.

Recommended Track B architecture:

```text
base sector allocator weights
+ sector PT-NAI / ESC-NIO event response signal
+ RIC-SNM validation and sizing gate
+ bounded sector tilt
= final sector weights
```

Track B signal categories:

- AI / semiconductor / technology policy;
- consumer stimulus;
- healthcare/pharma regulation;
- property policy;
- energy/commodity shock;
- financial regulation;
- export/tariff/geopolitical exposure;
- industry earnings/fundamentals;
- liquidity/risk sentiment.

Track B should optimise:

- rank-IC stability;
- top-k sector inclusion/exclusion quality;
- Sharpe improvement over `p18_leeqa_sector_k5_temp35`;
- no-news fallback against `p18_s1_sector_t35_v30_w20`;
- event-category explainability.

## 13. Evaluation Protocol

The evaluation protocol must be strict enough to prevent accidental promotion of a news proxy that merely overfits 2024.

### 13.1 Training / Tuning

Use 2024 only for:

- event taxonomy;
- event windows;
- sensitivity estimates;
- rank-IC horizons;
- gate thresholds;
- overlay strengths;
- Track A risk multiplier;
- Track B rank-to-weight mapping;
- lexical/dense relevance thresholds if TC-TRIG is later introduced.

### 13.2 Frozen Testing

Use 2025 for exactly one frozen test pass per candidate family. Do not select parameters, thresholds, event classes, embedding blends, or fallback rules based on 2025.

### 13.3 Baseline Comparisons

Every overlay must be compared against:

| Track | Main baseline | Secondary baselines |
|---|---|---|
| Track A | `p18_rp_macro_w10_s5` | `p18_rp_macro_w40_s5`, `p18_rp_macro_w20_s5`, `p18_bsa_macro_t10_g65`, `p18_rp_macro_w60_s5` |
| Track B | `p18_leeqa_sector_k5_temp35` | `p18_s1_sector_t35_v30_w20`, `p18_leeqa_sector_k5_temp20`, `p18_leeqa_sector_k5_temp70`, `p18_leeqa_sector_k3_temp20` |

### 13.4 Metrics

Minimum metrics:

- Sharpe ratio;
- cumulative return;
- max drawdown;
- turnover;
- number of active news-trigger days;
- average absolute tilt;
- gate pass/fail distribution;
- event-category contribution;
- Track A/Track B separate results;
- real-news vs shuffled-news spread;
- real-news vs zero-news spread.

### 13.5 Trace Requirements

Each evaluation should preserve:

```text
date
news_item_id
timestamp_used
event_class
direction
impact
relevance
confidence
sensitivity
gate_states
base_weights
delta_weights
final_weights
turnover
realised return
```

## 14. Promotion Gate

A future implementation may be considered for official-runtime replacement only if **all** of the following pass:

1. **2024-only selection:** All methods, thresholds, gates, and weights selected only on 2024.
2. **Frozen 2025 test:** 2025 used only after freezing.
3. **Baseline improvement:** Improves over the relevant preserved base allocator in risk-adjusted terms.
4. **Null survival:** Real-news performance exceeds zero-news and shuffled-news controls.
5. **Event-label validity:** Randomised labels degrade or neutralise the signal.
6. **Drawdown control:** Max drawdown is not materially worse; Track A should ideally improve drawdown.
7. **Turnover discipline:** Turnover remains acceptable under the 0.01% friction setting.
8. **Dependency discipline:** No online API, no silent downloads, no unpinned required model assets.
9. **Deterministic fallback:** Missing/failed news module returns base allocator behaviour.
10. **Local official-semantics replay:** Passes official-semantics replay on required rows/horizons.
11. **Official-server parity:** Passes official-server smoke/parity validation.
12. **Trace audit:** Event availability, timestamp cutoff, and gate logic are human-readable.
13. **Human approval:** No automatic final-runtime replacement.

The most important single promotion gate is:

> **Frozen 2025 real-news improvement over preserved base while simultaneously surviving zero-news and shuffled-news ablations under official-semantics replay.**

## 15. Documentation Starter Kit Requirements for Prompt0C

Prompt0C should generate a documentation starter kit, not production code. It should include:

| Document | Required content |
|---|---|
| `README_news_overlay.md` | Purpose, non-goals, frozen runtime policy, track split. |
| `architecture_overview.md` | ESC-NIO/PT-NAI first-build architecture; Track A VS-MNRG; Track B RIC-SNM. |
| `baseline_inventory.md` | Preserved Track A/B candidates and comparator protocol. |
| `event_taxonomy.md` | Macro and sector event classes, direction rules, confidence labels, duplicate handling. |
| `news_attention_index_spec.md` | PT-NAI formula, fields, thresholds, trace schema. |
| `event_study_calibration_spec.md` | CAR/CAAR methodology, windows, sensitivity shrinkage, sparse-class rules. |
| `track_a_macro_risk_gate_spec.md` | VS-MNRG formula, stress/easing mapping, risk multiplier, fallback. |
| `track_b_sector_rank_overlay_spec.md` | RIC-SNM formula, rank-IC validation, top-k/tilt rules. |
| `ablation_matrix.md` | Required ablations, expected outputs, pass/fail logic. |
| `evaluation_protocol.md` | 2024 tuning, frozen 2025 test, official-semantics replay, metrics. |
| `promotion_gate.md` | Checklist for official-runtime promotion. |
| `dependency_and_cache_policy.md` | No API, no silent download, TC-TRIG second-build constraints. |
| `trace_and_audit_schema.md` | Per-date event, signal, gate, and weight trace format. |
| `implementation_log_template.md` | Prompt-run implementation log format compatible with existing workflow. |
| `prompt0c_generation_prompt.md` | The starter-kit prompt itself, referencing this Prompt0B decision. |

Prompt0C should explicitly document that **TC-TRIG is second-build**, **ES-GPNS is deferred**, and **learned attention is ablation-only/rejected for promotion**.

## 16. Risks and Mitigations

| Risk | Where it appears | Mitigation |
|---|---|---|
| Timestamp leakage | News cutoff, same-day event construction | Strict timestamp audit; store event availability traces. |
| 2024 overfit | Event windows, sensitivity, IC thresholds | Low-dimensional tuning; walk-forward 2024 checks; frozen 2025 only. |
| Duplicate headline overcount | Daily Top-20 hot news | Duplicate clustering and event-instance IDs. |
| Sparse event classes | Event-study sensitivity | Merge classes; shrink to zero; require minimum counts. |
| Transformer dependency creep | TC-TRIG | Second-build only; cache; lexical fallback; no silent downloads. |
| Track A opportunity cost | Macro risk gate | Use conservative thresholds and two-sided stress/easing tests. |
| Track B turnover spiral | Sector tilts | Turnover cap, top-k stability, lag smoothing, gate thresholds. |
| Interpretability loss | SESRO, BL-NVO, HAN/QKV | Keep as ablations; require trace-level comparison against ESC/PT-NAI. |
| Official-server mismatch | Packaging/runtime | Local official-semantics replay then official-server parity before promotion. |

## 17. Final Recommendation

The recommended next phase is a deterministic first-build architecture:

```text
Rule/title-aware event extraction
→ duplicate clustering
→ deterministic event taxonomy
→ event-study calibration of event/asset sensitivity on 2024
→ permutation-tested News Attention Index
→ Track A VS-MNRG risk gate
→ Track B RIC-SNM sector ranking/tilt gate
→ bounded additive overlay
→ frozen 2025 evaluation and ablation suite
```

Do not start with transformer embeddings. Do not start with graph propagation. Do not start with Black-Litterman or exponentiated-gradient overlays. These are useful ablations or second-stage enhancements only after the deterministic event-study/NAI stack exists.

**Final answer block:**

```text
Selected first-build method:
  Event-Study Calibrated News Impact Overlay (ESC-NIO) with Permutation-Tested News Attention Index (PT-NAI) and bounded gated overlay.

Selected second-build method:
  Transformer-Cached Text-to-Sector Relevance + Rule Impact Gate (TC-TRIG), optional and cache/fallback constrained.

Best Track A method:
  Volatility-Scaled Macro News Risk Gate (VS-MNRG), using macro ESC-NIO/PT-NAI signals as a risk multiplier.

Best Track B method:
  Rank-IC Gated Sector News Momentum (RIC-SNM), using sector ESC-NIO/PT-NAI signals as ranking and bounded-tilt inputs.

Ablation-only methods:
  Sparse Event-Sensitivity Regression Overlay (SESRO);
  Black-Litterman News View Overlay (BL-NVO);
  Confidence-Weighted Exponentiated-Gradient Overlay (CW-EG);
  Hierarchical Daily News Attention Pooling as research comparator only.

Rejected/deferred methods:
  Defer Entity-Sector Graph Propagation News Score (ES-GPNS);
  defer cross-encoder reranking;
  reject online LLM allocators, full neural portfolio allocators, deep RL, graph RL, unbounded end-to-end transformer allocators, and RAG summary-to-trade systems for this phase.

Most important promotion gate:
  Frozen 2025 real-news improvement over preserved base allocator while surviving zero-news and shuffled-news ablations under official-semantics replay, with drawdown and turnover not materially worse.

What Prompt0C should document:
  A documentation starter kit covering baseline inventory, frozen-runtime policy, event taxonomy, ESC-NIO calibration, PT-NAI signal spec, Track A VS-MNRG, Track B RIC-SNM, ablation matrix, evaluation protocol, trace schema, dependency/cache policy, promotion gate, and implementation-log template.
```
