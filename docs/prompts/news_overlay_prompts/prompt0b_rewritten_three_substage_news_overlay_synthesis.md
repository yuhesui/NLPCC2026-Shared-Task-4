# Prompt0B Revised Synthesis Report — Three-Substage News Overlay Architecture

**Generated:** 2026-06-04  
**Purpose:** Rewrite the Prompt0B synthesis by separating the method universe into three explicit substages: **(1) news analysis / embedding**, **(2) news impact estimation**, and **(3) ETF/news sensitivity modelling**.  
**Status:** Research synthesis and implementation planning only. No production code, no official-runtime change, no 2025 tuning, no hidden-2026 assumption.

---

## 1. Executive Decision

The earlier Prompt0B synthesis selected a first-build bundle around:

```text
Event-Study Calibrated News Impact Overlay (ESC-NIO)
+ Permutation-Tested News Attention Index (PT-NAI)
+ Rank-IC Gated Sector News Momentum (RIC-SNM) for Track B
+ Volatility-Scaled Macro News Risk Gate (VS-MNRG) for Track A
```

That selection remains valid, but the architecture should be rewritten more cleanly as a **three-substage pipeline** rather than as a flat list of competing methods.

The corrected decomposition is:

```text
Substage 1 — Analyse / Embed / Map News
  Question: What does the news say, and which asset/sector is it about?
  Output: structured news features, event labels, tone, entities, relevance matrix.

Substage 2 — Estimate News Impact
  Question: How important, directional, novel, and persistent is this news event?
  Output: event impact score, direction, confidence, novelty, decay, raw NAI.

Substage 3 — Estimate ETF Sensitivity to News
  Question: Which ETF/sector historically reacts to this type of news, and should the overlay trust it?
  Output: ETF-event sensitivity table, rank-IC gate, macro risk gate, bounded overlay signal.
```

The most important correction is conceptual:

> **News impact is event-intrinsic. ETF sensitivity is asset-specific. They should not be collapsed into one score too early.**

A headline can be high-impact in the market narrative but irrelevant to a particular ETF. Conversely, a modest news item can matter if a sector has high historical sensitivity to that specific event class. The revised architecture therefore keeps the three objects separate:

```text
News Analysis / Relevance:    R_{i,j}
Event Impact:                 I_i, D_i, C_i
ETF Sensitivity:              Sens_{j,c,h}
Final usable signal:           I_i × D_i × C_i × R_{i,j} × Sens_{j,c,h}
```

---

## 2. Evidence and Constraint Basis

The repository state and workflow constraints remain unchanged:

- The official runtime is frozen.
- Track A primary remains `p18_rp_macro_w10_s5`; Track A fallback remains `p18_rp_macro_w40_s5`.
- Track B primary remains `p18_leeqa_sector_k5_temp35`; Track B fallback remains `p18_s1_sector_t35_v30_w20`.
- Stage 1 news processing is currently deterministic and MVP-level.
- Optional local model paths exist conceptually but are not final dependencies.
- Preserved candidates provide the baseline set for overlay research.
- Any new overlay must be tuned only on 2024, frozen before 2025 replay, and evaluated on 2025 without parameter selection.
- No hidden 2026 data, no online API dependency, no silent downloads, and no official-runtime replacement without parity and human approval.

The deep research reports converge on the same design logic:

1. deterministic event extraction and taxonomy first;
2. transparent News Attention Index rather than end-to-end allocation;
3. event impact and ETF sensitivity estimated from 2024 only;
4. bounded overlay on preserved base allocators;
5. transformer / attention methods treated as optional, cached, second-build, or ablation-only;
6. full LLM allocators, deep RL, graph RL, and unconstrained neural allocators rejected for this phase.

---

## 3. Revised Architecture Overview

### 3.1 Pipeline Diagram

```text
Raw Top-20 News before official cutoff
        │
        ▼
Substage 1 — News Analysis / Embedding / Relevance
        │
        ├─ event label c_i
        ├─ direction/tone preliminary d_i
        ├─ entity/theme tags
        ├─ relevance R_{i,j}
        └─ confidence q_i
        │
        ▼
Substage 2 — Event Impact / Importance / Persistence
        │
        ├─ impact I_i
        ├─ novelty/duplication adjustment
        ├─ attention/breadth score
        ├─ temporal decay
        └─ raw or filtered NAI component
        │
        ▼
Substage 3 — ETF Sensitivity / Validation / Overlay Use
        │
        ├─ Sens_{j,c,h} from 2024 event studies / IC / sparse regression
        ├─ Track A macro risk multiplier
        ├─ Track B sector rank/tilt score
        ├─ gates: impact, relevance, sensitivity, confidence, turnover, drawdown
        └─ bounded Δw added to preserved base allocator
```

### 3.2 Correct Output Contracts

| Object | Created In | Meaning | Example Fields |
|---|---|---|---|
| `NewsFeatureRecord` | Substage 1 | Structured representation of each news item | timestamp, text, event class, entities, tone, preliminary direction, confidence |
| `RelevanceMatrix` | Substage 1 | Mapping from each news item to each ETF/sector | `R[i,j]`, lexical score, embedding score, entity-map score |
| `EventImpactRecord` | Substage 2 | Intrinsic importance of each event independent of ETF | impact, novelty, duplication penalty, breadth, persistence, decay |
| `RawNAI` | Substage 2 | Pre-sensitivity news attention score | `sum impact × direction × confidence × relevance` |
| `SensitivityTable` | Substage 3 | Historical response of ETF/sector to event class | `Sens[j,c,h]`, CAR/CAAR, Rank-IC, hit rate, volatility response |
| `OverlaySignal` | Substage 3 | Final bounded tradable signal | Track A risk multiplier, Track B sector tilt, gate states |

---

## 4. Substage 1 — Analyse / Embed / Map News

### 4.1 Substage Objective

Substage 1 should answer:

```text
What is this news item about?
Which event class does it belong to?
Which sector or ETF is it relevant to?
What is its preliminary direction or tone?
How confident is the extraction?
```

It should **not** decide how large the market impact is, and it should **not** decide whether a portfolio should trade. Its job is text understanding, event structuring, and text-to-asset mapping.

### 4.2 First-Build Methods

| Method | Role | Track A Value | Track B Value | Decision |
|---|---|---:|---:|---|
| Deterministic Policy/Event Taxonomy Extractor | Assign event class, policy action, sector/theme tags | High | High | build_first |
| BM25 / TF-IDF Sector Relevance | Lexical relevance baseline | Moderate | High | build_first |
| Entity-Sector Mapping | Map entities/themes to sectors and ETFs | Moderate | High | build_first |
| Dictionary / Rule-Based Tone and Direction | Preliminary sentiment/direction score | Moderate | High | build_first |
| Duplicate / Cluster Detection | Avoid overcounting repeated headlines | High | High | build_first |

### 4.3 Second-Build Transformer / Attention Methods

| Method | Role | Track A Value | Track B Value | Decision |
|---|---|---:|---:|---|
| TC-TRIG — Transformer-Cached Text-to-Sector Relevance + Rule Impact Gate | Offline dense relevance cache; semantic relevance improvement | Moderate | High | build_second |
| Bi-Encoder Sector Prototype Retrieval Cache | Encode news and sector prototypes, compute cosine similarity | Low-moderate | High | build_second |
| Frozen FinBERT Aspect-Tone Classifier | Aspect-level tone: policy, demand, regulation, liquidity | Moderate | High | build_second |
| Cross-Encoder Sector Reranker Gate | Rerank top-k candidate sectors after BM25/BGE retrieval | Low | High | ablation_only / build_later |
| Label-Attention Event Taxonomy Classifier | Match news to fixed event-label embeddings | Moderate | High | ablation_only / build_later |
| Hierarchical Daily News Attention Pooling | Learned pooling over daily Top-20 news | Low | Moderate | ablation_only |

### 4.4 Recommended Substage 1 First Build

The first implementation should be:

```text
Deterministic event taxonomy
+ entity-sector map
+ BM25/TF-IDF relevance
+ rule-based tone/direction
+ duplicate clustering
```

The second implementation should add:

```text
Offline BGE/Chinese embedding cache
+ optional FinBERT-style aspect-tone features
+ lexical fallback always preserved
```

### 4.5 Mathematical Formulation

For news item `i` and ETF/sector `j`, define:

```math
R^{lex}_{i,j} = BM25(text_i, proto_j)
```

If an offline embedding cache is available:

```math
R^{emb}_{i,j} = \cos(Enc(text_i), Enc(proto_j))
```

The hybrid relevance score is:

```math
R_{i,j} = \alpha R^{lex}_{i,j} + (1-\alpha)R^{emb}_{i,j}
```

For first build, set:

```math
\alpha = 1
```

For second build, tune `alpha` on 2024 only and freeze before 2025.

### 4.6 Substage 1 Ablations

| Ablation | Purpose |
|---|---|
| lexical relevance only | baseline relevance map |
| entity-sector mapping only | test whether entity rules beat BM25 |
| BM25 + entity mapping | first-build production candidate |
| embedding relevance only | test transformer value alone |
| lexical + embedding hybrid | test semantic improvement |
| cross-encoder reranker on/off | test reranker marginal benefit |
| duplicate clustering on/off | test overcounting risk |
| randomised sector prototypes | null test for semantic relevance |
| transformer cache disabled | official fallback test |

### 4.7 Substage 1 Risks

| Risk | Mitigation |
|---|---|
| semantic relevance overfits 2024 terminology | keep lexical fallback and freeze prototypes |
| transformer dependency fails official server | cache features offline; no silent downloads; disable model path by default |
| duplicate headlines inflate impact | cluster before impact scoring |
| event taxonomy too coarse | trace event class and confidence separately |
| event taxonomy too fine | merge sparse event classes before sensitivity estimation |

---

## 5. Substage 2 — Estimate News Impact

### 5.1 Substage Objective

Substage 2 should answer:

```text
How important is this news item or event cluster?
Is it positive, negative, or neutral?
Is it novel or already stale?
Is it broad or narrow?
How long should its influence persist?
```

This stage produces **event-intrinsic impact**. It should not yet assert that a specific ETF will react. ETF response belongs to Substage 3.

### 5.2 Methods Assigned to Substage 2

| Method | Role | Track A Value | Track B Value | Decision |
|---|---|---:|---:|---|
| PT-NAI — Permutation-Tested News Attention Index | Canonical transparent news attention / impact signal | High | High | build_first |
| Deterministic Event Magnitude Scorer | Event importance from source count, event class, policy strength, novelty | High | High | build_first |
| Novelty / Staleness Decay Model | Penalise repeated narratives, preserve recent event persistence | High | High | build_first |
| Duplicate-Cluster Event Consolidation | Treat repeated headlines as one event cluster | High | High | build_first |
| Impact-Gated Attention Pooling | Use attention only after deterministic impact filtering | Moderate | Moderate-high | ablation_only |
| Title2Event-Inspired Event Tagger | Better title-level event category and argument extraction | Moderate | High | build_later |

### 5.3 Recommended Substage 2 First Build

The first-build impact model should be deterministic and transparent:

```text
Event impact = event-class base weight
             + policy-action strength
             + source/news-count breadth
             + novelty
             + cross-news directional agreement
             - duplication/staleness penalty
```

Do **not** start with a learned impact model. Use learning only for validation, not first-pass impact generation.

### 5.4 Mathematical Formulation

For each event/news cluster `i`, define:

```math
I_i = w_c BaseClass(c_i)
    + w_a ActionStrength_i
    + w_b Breadth_i
    + w_n Novelty_i
    + w_g Agreement_i
    - w_d DupPenalty_i
```

Direction and confidence:

```math
D_i \in \{-1,0,+1\}, \qquad C_i \in [0,1]
```

Temporal decay:

```math
Decay_i(\Delta t) = \exp(-\lambda_{c_i}\Delta t)
```

Raw pre-sensitivity News Attention Index:

```math
RawNAI_{t,j} = \sum_{i \in \mathcal{N}_t} I_i \cdot D_i \cdot C_i \cdot R_{i,j} \cdot Decay_i
```

This is still not the final tradable signal because it does not yet include ETF sensitivity.

### 5.5 How ESC-NIO Is Split in This Revised Architecture

The earlier method name **Event-Study Calibrated News Impact Overlay** mixes three functions:

```text
1. event classification / relevance;
2. event impact scoring;
3. asset-specific response calibration and overlay.
```

In the revised report, split ESC-NIO as follows:

| ESC-NIO Component | New Substage | Meaning |
|---|---|---|
| event taxonomy and relevance | Substage 1 | identify what the news is about and which ETF/sector it maps to |
| event magnitude and direction | Substage 2 | estimate how important the news event is |
| CAR/CAAR response table and overlay gate | Substage 3 | estimate whether the ETF historically reacts and whether to trade |

This separation prevents the system from treating all high-impact news as automatically tradable.

### 5.6 Substage 2 Ablations

| Ablation | Purpose |
|---|---|
| equal impact for all events | test whether impact scoring helps |
| class-weighted impact only | test taxonomy value |
| novelty on/off | test stale narrative handling |
| duplicate clustering on/off | test overcounting |
| direction randomised | check sign dependence |
| event labels randomised | check taxonomy dependence |
| attention/breadth removed | test whether headline frequency matters |
| decay on/off | test event persistence |
| shuffled-news dates | main temporal null |
| zero-impact signal | fallback and equivalence test |

### 5.7 Substage 2 Risks

| Risk | Mitigation |
|---|---|
| popular but irrelevant news gets high impact | require relevance gate before ETF use |
| repeated syndicated headlines inflate event size | cluster before scoring |
| event impact tuned to 2024 buzz patterns | keep low-dimensional score and test shuffled-news nulls |
| positive and negative events treated symmetrically when they are not | allow direction-specific thresholds and asymmetric impact only if validated on 2024 |
| same-day timestamp leakage | enforce official cutoff before event scoring |

---

## 6. Substage 3 — Estimate ETF Sensitivity to News

### 6.1 Substage Objective

Substage 3 should answer:

```text
Given this event class and this ETF/sector, is there historical evidence that the ETF reacts?
Is the response directional, volatile, short-lived, or persistent?
Should the news signal be allowed to influence the base allocator?
```

This is the most important stage for avoiding overtrading. It transforms news features into **validated tradable signals**.

### 6.2 Methods Assigned to Substage 3

| Method | Role | Track A Value | Track B Value | Decision |
|---|---|---:|---:|---|
| Event-Study CAR/CAAR Sensitivity Table | Estimate ETF-event abnormal response by class and horizon | Moderate | Very High | build_first |
| RIC-SNM — Rank-IC Gated Sector News Momentum | Validate sector ranking value of news signals | Low-moderate | Very High | build_first for Track B |
| VS-MNRG — Volatility-Scaled Macro News Risk Gate | Convert macro news into risk multiplier | Very High | Moderate as global throttle | build_first for Track A |
| SESRO — Sparse Event-Sensitivity Regression Overlay | Learn sparse event-feature response | Moderate | High | build_second / ablation |
| BL-NVO — Black-Litterman News View Overlay | Convert validated news into portfolio views | Moderate-high | Moderate-high | ablation / build_later |
| Confidence-Weighted EG Overlay | Multiplicative active overlay around base weights | Moderate | Moderate-high | ablation_only |
| ES-GPNS — Entity-Sector Graph Propagation | Indirect relevance/sensitivity through entity-sector graph | Low-moderate | High | defer |

### 6.3 Recommended Substage 3 First Build

Use two different downstream models by track:

```text
Track A:
  Volatility-Scaled Macro News Risk Gate (VS-MNRG)
  using macro RawNAI + event-study volatility/drawdown response.

Track B:
  Rank-IC Gated Sector News Momentum (RIC-SNM)
  using sector RawNAI + CAR/CAAR sensitivity + rank-IC validation.
```

The shared sensitivity primitive should be:

```text
ETF-event-class-horizon response table estimated only on 2024.
```

### 6.4 Event-Study Sensitivity Formulation

For ETF/sector `j`, event class `c`, and horizon `h`, estimate normal return on 2024:

```math
R_{j,t} = \alpha_j + \beta_j R_{m,t} + \epsilon_{j,t}
```

Abnormal return:

```math
AR_{j,t} = R_{j,t} - (\hat{\alpha}_j + \hat{\beta}_j R_{m,t})
```

Cumulative abnormal return around event `e`:

```math
CAR_{e,j,c,h} = \sum_{\tau=0}^{h} AR_{j,t_e+\tau}
```

Sensitivity table:

```math
Sens_{j,c,h} = \frac{median_e(CAR_{e,j,c,h})}{\sigma_j}
```

This table is frozen after 2024.

### 6.5 Final Sector Signal Formulation

The sector signal should multiply Substage 1 relevance, Substage 2 impact, and Substage 3 sensitivity:

```math
S_{t,j} = \sum_{i \in \mathcal{N}_t}
          I_i \cdot D_i \cdot C_i \cdot R_{i,j} \cdot Sens_{j,c_i,h^*}
```

The signal is tradable only if all gates pass:

```math
Gate_{t,j} = 1\{ |S_{t,j}| > \theta_S \}
             1\{ I_i > \theta_I \}
             1\{ R_{i,j} > \theta_R \}
             1\{ |Sens_{j,c_i,h^*}| > \theta_{Sens} \}
             1\{ C_i > \theta_C \}
             1\{ TurnoverBudget_t > 0 \}
             1\{ DrawdownState_t \text{ allows overlay} \}
```

Final bounded tilt:

```math
\Delta w_{t,j} = Gate_{t,j} \cdot clip(\kappa S_{t,j}, -m_j, m_j)
```

Final weight:

```math
w^{final}_{t,j} = Normalize(w^{base}_{t,j} + \Delta w_{t,j})
```

If `Gate = 0`, then:

```math
w^{final}_{t,j} = w^{base}_{t,j}
```

### 6.6 Track A Use: VS-MNRG

Track A should not use sector-style rank momentum as its first deployment. The macro universe is smaller and less naturally cross-sectional, and the preserved no-news risk-parity baseline is already strong.

Track A should aggregate macro stress and easing news into a risk multiplier:

```math
RI_t = b_1(-Tone_t) + b_2 Attention_t + b_3 Dispersion_t + b_4 StressEvent_t + b_5 Vol_t
```

Risk multiplier:

```math
\kappa_t = clip(1 - \gamma RI_t, \kappa_{min}, \kappa_{max})
```

Risky sleeve adjustment:

```math
w^{final}_{t,risky} = \kappa_t w^{base}_{t,risky}
```

Residual allocation should go to predefined defensive sleeves according to fixed 2024-tuned rules.

### 6.7 Track B Use: RIC-SNM

Track B should use news as a sector ranking and tilt signal.

For candidate news factor `f`, estimate 2024 rank IC:

```math
RankIC^{(h)}_{f,t} = \rho_{Spearman}(Rank(f_{t,\cdot}), Rank(r_{t+h,\cdot}))
```

Keep the factor only if:

```math
mean(RankIC_f) > \theta_{IC}
```

and its sign is stable across 2024 folds.

The Track B overlay should then:

1. adjust sector ranks, or
2. apply small top-k tilts, or
3. suppress sectors with high negative event sensitivity.

It should not directly replace the base LEEQA/S1 allocator.

### 6.8 Substage 3 Ablations

| Ablation | Purpose |
|---|---|
| base allocator only | benchmark |
| real news + sensitivity | full candidate |
| real news but uniform sensitivity | test ETF sensitivity value |
| sensitivity gate disabled | detect overtrading |
| CAR sensitivity vs Rank-IC sensitivity | compare response estimators |
| CAR window sweep | test horizon dependence |
| shuffled-news dates | main temporal null |
| randomised event labels | taxonomy null |
| randomised ETF mapping | relevance/sensitivity null |
| zero-news signal | exact fallback check |
| overlay strength sweep | calibrate risk of signal |
| turnover cap sweep | estimate friction robustness |
| Track A only / Track B only | isolate track-specific value |
| high-volatility / low-volatility split | stress robustness |
| event-category removal | identify fragile event classes |

### 6.9 Substage 3 Risks

| Risk | Mitigation |
|---|---|
| sparse event classes create unstable sensitivity | merge sparse classes or shrink sensitivity to zero |
| 2024 event response does not generalise | require fold stability and frozen 2025 test |
| sensitivity gate admits noisy sectors | require Rank-IC and shuffled-news survival |
| Track A over-de-risks and misses rebound | cap risk multiplier and test opportunity cost |
| Track B churns on noisy sector headlines | turnover cap, top-k stability, event persistence filter |
| overlay is profitable only because of leakage | timestamp audit, zero-news, shuffled-news, random-label tests |

---

## 7. Reassigned Method Map

| Original Method | Revised Primary Substage | Secondary Substage | Why |
|---|---|---|---|
| Deterministic Rule/Event Extraction | Substage 1 | Substage 2 | It identifies event classes and directions; class base weights feed impact. |
| BM25 / TF-IDF Relevance | Substage 1 | — | Pure text-to-sector mapping. |
| Entity-Sector Mapping | Substage 1 | Substage 3 if graph weights are learned | Maps news entities to tradable sectors. |
| Transformer-Cached Text-to-Sector Relevance (TC-TRIG) | Substage 1 | — | It improves relevance, not impact or sensitivity. |
| FinBERT Aspect-Tone | Substage 1 | Substage 2 | Primary role is tone/aspect extraction; its tone probabilities can feed impact. |
| Title2Event-Inspired Event Tagger | Substage 1 | Substage 2 | Extracts event type and arguments; impact is downstream. |
| PT-NAI | Substage 2 | Substage 3 | Main role is transparent impact/attention index; it becomes tradable only after sensitivity filtering. |
| Event Magnitude / Novelty / Decay Scorer | Substage 2 | — | Pure event-intrinsic impact logic. |
| ESC-NIO | Split | Split | Event taxonomy in Stage 1; impact in Stage 2; CAR sensitivity and overlay in Stage 3. |
| CAR/CAAR Event Study | Substage 3 | — | Estimates ETF-specific response to event classes. |
| Rank-IC Gated Sector News Momentum | Substage 3 | — | Validates sector ranking value and controls Track B use. |
| Volatility-Scaled Macro News Risk Gate | Substage 3 | — | Converts macro news sensitivity into Track A risk scaling. |
| Sparse Event-Sensitivity Regression Overlay | Substage 3 | — | Estimates ETF response from event features. |
| Black-Litterman News View Overlay | Substage 3 | Portfolio-use layer | Consumes validated signals as views; not a text method. |
| Exponentiated-Gradient Overlay | Substage 3 | Portfolio-use layer | Consumes validated scores; not a news analysis method. |
| Hierarchical Daily News Attention Pooling | Substage 1 | Substage 2 | Learned news aggregation; ablation only. |
| Graph-Attention Entity-Sector Propagation | Substage 1 | Substage 3 | Graph relevance and indirect sensitivity; defer. |

---

## 8. Revised Comparative Strategy Table

Scores use a 1–5 scale. For value/robustness/interpretability/ablation/compatibility, 5 is best. For implementation cost, dependency risk, and leakage risk, 5 means worse. The decision is based on first-stage suitability under frozen-runtime constraints.

| Rank | Method | Primary Substage | Track A Value | Track B Value | Expected Alpha | Robustness | Interpretability | Implementation Cost | Dependency Risk | Leakage Risk | Ablation Quality | Official Compatibility | Decision |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | Deterministic Taxonomy + BM25/Entity Relevance | 1 | 4.0 | 4.8 | 3.8 | 4.8 | 5.0 | 2.0 | 1.0 | 1.5 | 5.0 | 5.0 | build_first |
| 2 | PT-NAI Intrinsic Impact Index | 2 | 4.2 | 4.7 | 4.3 | 4.5 | 4.8 | 2.5 | 1.0 | 1.8 | 5.0 | 5.0 | build_first |
| 3 | CAR/CAAR ETF Sensitivity Table | 3 | 3.8 | 5.0 | 4.5 | 4.2 | 4.8 | 3.0 | 1.0 | 2.0 | 5.0 | 4.8 | build_first |
| 4 | VS-MNRG Macro Risk Gate | 3 | 5.0 | 2.8 | 3.8 | 4.5 | 4.7 | 2.2 | 1.0 | 1.8 | 5.0 | 5.0 | build_first_track_a |
| 5 | RIC-SNM Sector Ranking Gate | 3 | 2.0 | 5.0 | 4.4 | 4.2 | 4.5 | 2.5 | 1.0 | 2.0 | 4.8 | 5.0 | build_first_track_b |
| 6 | TC-TRIG / Bi-Encoder Relevance Cache | 1 | 2.8 | 4.5 | 4.0 | 3.7 | 3.7 | 3.5 | 2.8 | 2.5 | 4.5 | 3.8 | build_second |
| 7 | FinBERT Aspect-Tone Cache | 1 | 3.2 | 4.2 | 3.8 | 3.6 | 3.5 | 3.5 | 2.8 | 2.5 | 4.3 | 3.8 | build_second |
| 8 | SESRO Sparse Event-Sensitivity Regression | 3 | 3.0 | 4.6 | 4.2 | 3.8 | 4.0 | 3.5 | 1.5 | 2.5 | 4.7 | 4.5 | ablation_then_build_later |
| 9 | BL-NVO Black-Litterman Views | 3 | 4.0 | 4.0 | 3.7 | 3.7 | 4.0 | 3.5 | 1.5 | 2.3 | 4.3 | 4.0 | ablation_only_initially |
| 10 | Cross-Encoder Reranker Gate | 1 | 2.0 | 4.2 | 3.8 | 3.3 | 3.2 | 4.0 | 3.5 | 2.8 | 4.0 | 3.0 | ablation_only |
| 11 | Entity-Sector Graph / Graph Attention | 1/3 | 2.5 | 4.2 | 3.6 | 3.0 | 3.0 | 4.2 | 3.0 | 3.0 | 3.8 | 3.2 | defer |
| 12 | Hierarchical / QKV Daily News Attention | 1/2 | 2.2 | 3.8 | 3.5 | 2.8 | 2.8 | 4.3 | 3.2 | 3.2 | 3.5 | 3.0 | ablation_only_no_promotion |

---

## 9. Revised First-Build Architecture

### 9.1 Build First: Deterministic Three-Substage MVP

```text
Substage 1:
  deterministic event taxonomy
  + BM25/entity-sector relevance
  + rule tone/direction
  + duplicate clustering

Substage 2:
  deterministic event impact score
  + novelty / breadth / agreement / decay
  + raw PT-NAI

Substage 3:
  2024-only CAR/CAAR sensitivity table
  + Track A VS-MNRG
  + Track B RIC-SNM
  + bounded gated overlay
```

### 9.2 Build Second: Optional Semantic Enhancement

```text
Substage 1 upgrade:
  TC-TRIG / BGE-style bi-encoder cache
  + optional FinBERT aspect-tone cache
  + lexical fallback

Substage 2/3 unchanged:
  event impact, sensitivity, and gates remain deterministic and frozen.
```

### 9.3 Build Later / Ablation Only

```text
Substage 1/2 ablations:
  cross-encoder reranker
  label-attention event classifier
  hierarchical daily news attention pooling

Substage 3 ablations:
  sparse event-sensitivity regression
  Black-Litterman view overlay
  exponentiated-gradient active overlay

Defer:
  entity-sector graph attention
  end-to-end neural allocators
  graph RL / deep RL
  online LLM or RAG summary-to-trade systems
```

---

## 10. Track-Specific Revised Plan

## 10.1 Track A — Macro Allocation

Track A should share Substage 1 and Substage 2 with Track B, but its Substage 3 should be different.

**Use news as:**

```text
macro risk / volatility / drawdown regime signal
```

**Do not use news first as:**

```text
directional return-chasing macro forecast
```

**Recommended Track A stack:**

```text
Substage 1:
  macro-policy taxonomy + macro relevance map

Substage 2:
  macro PT-NAI: stress, easing, liquidity, property, crisis, policy uncertainty

Substage 3:
  VS-MNRG macro risk gate
  + optional event-study volatility/drawdown response table
  + bounded de-risk/re-risk multiplier on p18_rp_macro_w10_s5 / w40_s5
```

**Best Track A method:**

```text
Volatility-Scaled Macro News Risk Gate (VS-MNRG)
```

## 10.2 Track B — Sector Rotation

Track B should use news as a sector-ranking and sector-tilt signal.

**Use news as:**

```text
sector relevance + event impact + sector sensitivity + Rank-IC gate
```

**Recommended Track B stack:**

```text
Substage 1:
  sector taxonomy + entity-sector map + BM25 relevance

Substage 2:
  sector/event PT-NAI with duplicate clustering, novelty, direction, confidence

Substage 3:
  event-class/sector CAR sensitivity
  + Rank-IC Gated Sector News Momentum
  + bounded top-k or rank-proportional overlay on p18_leeqa_sector_k5_temp35
```

**Best Track B method:**

```text
Rank-IC Gated Sector News Momentum (RIC-SNM)
```

---

## 11. Revised Evaluation Protocol by Substage

### 11.1 Substage 1 Evaluation

| Test | Metric |
|---|---|
| rule extraction trace audit | event-class coverage, confidence, unknown-rate |
| relevance sanity check | top-k sector relevance interpretability |
| lexical vs entity vs embedding | incremental improvement in downstream 2024 validation |
| duplicate clustering | reduction in overcounted events |
| transformer disabled | exact fallback path |

### 11.2 Substage 2 Evaluation

| Test | Metric |
|---|---|
| impact score distribution | concentration, event-class balance |
| novelty/decay test | stale narrative suppression |
| shuffled-news dates | should lose predictive value |
| randomised labels | should lose directional value |
| component removal | identify useful impact components |

### 11.3 Substage 3 Evaluation

| Test | Metric |
|---|---|
| CAR/CAAR stability | event-class response sign stability |
| Rank-IC stability | sector ranking value across 2024 folds |
| sensitivity gate on/off | turnover and performance change |
| 2025 frozen test | true generalisation |
| official-semantics replay | execution equivalence |
| official-server parity | promotion precondition |

---

## 12. Revised Promotion Gate

A future implementation may be considered for official-runtime replacement only if all conditions hold:

```text
1. Substage 1 extraction/relevance rules are frozen after 2024.
2. Substage 2 impact and decay parameters are tuned only on 2024.
3. Substage 3 sensitivity tables and gates are estimated only on 2024.
4. 2025 is used once as frozen out-of-sample test, not for threshold selection.
5. The method improves over the relevant preserved baseline.
6. It survives zero-news and shuffled-news tests.
7. It survives random-label and random-sector mapping tests.
8. Drawdown is not materially worse.
9. Turnover remains acceptable under 0.01% friction.
10. Dependency footprint is pinned and optional.
11. Deterministic fallback exactly recovers the base allocator when news is unavailable or gates fail.
12. Local official-semantics replay passes.
13. Official-server parity passes.
14. Final human approval is granted.
```

The most important promotion gate remains:

```text
Frozen 2025 improvement over preserved base allocator
while surviving shuffled-news and zero-news ablations
under official-semantics replay, with no material drawdown or turnover deterioration.
```

---

## 13. Revised Prompt0C Documentation Requirements

Prompt0C should generate a documentation starter kit around the three substages rather than around a flat method list.

### 13.1 Required Documentation Files

```text
docs/news_overlay/README.md
  Overall three-substage architecture and frozen-runtime constraints.

docs/news_overlay/substage1_news_analysis_embedding.md
  Event taxonomy, entity-sector mapping, lexical relevance, optional embedding cache.

docs/news_overlay/substage2_news_impact.md
  Impact score, novelty, duplicate clustering, temporal decay, raw PT-NAI.

docs/news_overlay/substage3_etf_news_sensitivity.md
  CAR/CAAR sensitivity, Rank-IC validation, macro risk gate, sector overlay use.

docs/news_overlay/track_a_macro_news_plan.md
  VS-MNRG Track A plan.

docs/news_overlay/track_b_sector_news_plan.md
  RIC-SNM Track B plan.

docs/news_overlay/ablation_matrix.md
  Zero-news, shuffled-news, random labels, random mappings, gate-disabled tests.

docs/news_overlay/evaluation_protocol.md
  2024 tune, frozen 2025 test, official replay, official parity.

docs/news_overlay/dependency_and_cache_policy.md
  No silent downloads, transformer cache optional, lexical fallback required.

docs/news_overlay/promotion_gate.md
  Exact promotion checklist.

docs/news_overlay/trace_schema.md
  NewsFeatureRecord, EventImpactRecord, SensitivityRecord, OverlaySignal.

docs/implementation_logs/<timestamp>_news_overlay_three_substage_rewrite.md
  Audit trail for this redesign.
```

### 13.2 Prompt0C Should Explicitly State

```text
Substage 1 decides what the news means and which asset it maps to.
Substage 2 decides how important the event is.
Substage 3 decides whether an ETF historically reacts and whether the overlay may trade.
```

This sentence should be repeated in the README because it prevents architecture drift.

---

## 14. Final Recommendation

### 14.1 Revised First-Build Method

The first-build method should be renamed from a single monolithic method to:

```text
Three-Substage Deterministic News Overlay MVP
```

with components:

```text
Substage 1:
  Deterministic Event Taxonomy + BM25/Entity Relevance

Substage 2:
  Permutation-Tested News Attention Index with deterministic event impact

Substage 3:
  Event-Study CAR/CAAR ETF Sensitivity
  + Track A VS-MNRG
  + Track B RIC-SNM
  + bounded gated overlay
```

### 14.2 Revised Second-Build Method

```text
Transformer-Cached Text-to-Sector Relevance + Rule Impact Gate (TC-TRIG)
```

but now explicitly assigned to **Substage 1 only**. It should improve relevance and tone/aspect extraction, not replace impact estimation, sensitivity estimation, or the portfolio overlay.

### 14.3 Best Track A Method

```text
Volatility-Scaled Macro News Risk Gate (VS-MNRG)
```

Track A consumes macro event impact and macro sensitivity as a risk multiplier.

### 14.4 Best Track B Method

```text
Rank-IC Gated Sector News Momentum (RIC-SNM)
```

Track B consumes sector event impact and ETF sensitivity as a ranking/tilt adjustment.

### 14.5 Ablation-Only Methods

```text
Sparse Event-Sensitivity Regression Overlay
Black-Litterman News View Overlay
Confidence-Weighted Exponentiated-Gradient Overlay
Cross-Encoder Reranker Gate
Label-Attention Event Taxonomy Classifier
Hierarchical Daily News Attention Pooling
```

### 14.6 Deferred / Rejected Methods

```text
Entity-Sector Graph Attention / heavy graph propagation: defer.
End-to-end neural allocation transformer: reject for this phase.
Deep RL / graph RL: reject.
Online LLM allocator: reject.
RAG summary-to-trade allocator: reject.
Any method requiring 2025 tuning or hidden 2026 information: reject.
```

### 14.7 Main Implementation Risk

```text
Mixing event impact and ETF sensitivity too early.
```

If these are collapsed, the system may overtrade high-attention but non-actionable news. The revised three-substage architecture is designed specifically to prevent that failure.

### 14.8 One-Line Final Decision

```text
Build a deterministic three-substage news overlay first:
news understanding/relevance → event impact → ETF sensitivity/gated use;
then add transformer embeddings only as a Substage-1 relevance upgrade after ablations prove the deterministic stack is meaningful.
```
