# Prompt0A-Enhance Research Report — Specific Frameworks for News Overlay

## 1. Executive Summary

This report identifies eight concrete, named methodologies for the next News Overlay stage of the NLPCC 2026 shared task, with explicit algorithms, mathematical formulations, data requirements, validation protocols, and promotion criteria.[cite:47][cite:40][cite:105] The methods are designed for a constrained setting in which 2024 is the only tuning year, 2025 is a frozen generalization test, the official runtime must preserve a deterministic fallback, and any text processing must remain reproducible and compatible with official-server validation.[cite:47][cite:40]

The strongest first-build stack is a deterministic combination of **Event-Study Calibrated News Impact Overlay (ESC-NIO)**, **Permutation-Tested News Attention Index (PT-NAI)**, and **Rank-IC Gated Sector News Momentum (RIC-SNM)** for Track B, plus **Volatility-Scaled Macro News Risk Gate (VS-MNRG)** for Track A.[cite:47][cite:40][cite:62] This stack is recommended because it is interpretable, modular, ablation-friendly, and grounded in well-established frameworks: event studies quantify post-event abnormal returns, Chinese news-sentiment research shows predictive value for both returns and volatility, and IC/rank-IC are standard diagnostics for factor usefulness and stability.[cite:47][cite:40][cite:64]

The best second-build method is **Transformer-Cached Text-to-Sector Relevance + Rule Impact Gate (TC-TRIG)**, which uses an offline Chinese FinBERT-style model only to precompute sentiment and relevance features, while preserving a pure lexical/rule path for the final runtime.[cite:19][cite:22][cite:105] By contrast, heavier methods such as end-to-end attention allocators, deep RL, graph RL, and unbounded transformer portfolio models should be deferred or rejected because they raise dependency, interpretability, and overfitting risks that are misaligned with the competition’s reproducibility and ablation requirements.[cite:61][cite:105]

## 2. Method Discovery Scope

The method search covered six required areas: event-study finance, financial news sentiment and event extraction, text-to-asset relevance, attention and aggregation, signal validation, and portfolio overlay design.[cite:47][cite:40][cite:61] Priority was given to methods that can be implemented with the task’s daily Top-20 news plus ETF/index history, tuned only on 2024, and evaluated out of sample on 2025 without hidden data or runtime model downloads.[cite:40][cite:47]

The literature base used here emphasizes four particularly relevant strands. First, classical event-study methodology defines abnormal return, CAR, and CAAR in a way that naturally transfers to event-class impact calibration for ETFs and sectors.[cite:47][cite:54][cite:104] Second, Chinese market research based on GDELT-style media measures shows that tone, optimism, attention, and tone dispersion predict next-day returns and volatility, with especially strong asymmetric responses to negative news.[cite:40][cite:45][cite:94] Third, FinBERT-style models outperform dictionary methods on contextual financial sentiment tasks and can be adapted to Chinese finance, but they introduce deployment and reproducibility trade-offs that matter for this shared task.[cite:105][cite:22][cite:19] Fourth, IC/rank-IC and related factor diagnostics are useful not as alpha generators by themselves, but as gates that determine whether a news signal is stable enough to deserve portfolio influence.[cite:62][cite:64][cite:69]

## 3. Current Baselines and Why Specific Methods Are Needed

The current validated runtime is effectively frozen around a no-news risk-parity solution for Track A and a deterministic rule-based LEEQA-style sector-ranking solution for Track B, with additional preserved candidates retained only as future comparators rather than active promotion targets.[cite:13][cite:14] That baseline state means the next-stage research problem is not “find any interesting news idea,” but “identify explicit, bounded overlay methods that can sit on top of preserved allocators without breaking determinism, interpretability, or official-server compatibility.”[cite:13][cite:14]

General design families such as “use event scoring,” “use embeddings,” or “use a news attention index” are not sufficient because they do not specify how impact is calibrated, how relevance is computed, how gates are set, how training is restricted to 2024, or how false positives are ruled out with placebo tests.[cite:47][cite:40][cite:64] The methods in this report are therefore written as implementation-ready research blueprints: each one has a methodology name, a formula or algorithm, defined inputs and outputs, track-specific use cases, a required ablation suite, and a promotion decision category.[cite:47][cite:40]

## 4. Search / Literature Map

The literature map for this report has five anchor nodes. **Event-study methodology** provides the most defensible framework for converting news events into measurable ETF or sector responses via abnormal returns, CAR, and CAAR.[cite:47][cite:54][cite:104] **Chinese media-sentiment studies** provide evidence that tone, optimism, attention, and dispersion matter for predicting both market returns and volatility, and that negative sentiment effects are stronger than positive ones.[cite:40][cite:45][cite:94]

**Financial transformer models** such as FinBERT provide evidence that contextual models can materially outperform dictionary approaches in financial sentiment classification, especially when context matters and training samples are limited.[cite:105][cite:22] **Chinese financial NLP datasets** such as DocFEE and FEED show that document-level financial event extraction and event-argument structuring are feasible and useful for downstream modeling.[cite:32][cite:65] **Attention models** such as Hierarchical Attention Networks show how importance-weighted aggregation can be useful for long documents, but they become risky when elevated from feature extraction to end-to-end portfolio control.[cite:61]

Finally, **factor validation and overlay theory** provide two complementary tools: IC/rank-IC help decide whether a signal deserves trust, and Black-Litterman gives a principled way to translate signals into views layered over a prior portfolio.[cite:62][cite:64][cite:48] Together, these sources support a design philosophy in which event studies estimate impact, sentiment and event extraction provide text features, IC screens protect against fragile signals, and overlays remain bounded and subordinate to preserved base allocators.[cite:47][cite:40][cite:48]

## 5. Method Shortlist Overview

The eight shortlisted methods are summarized below.

1. **ESC-NIO — Event-Study Calibrated News Impact Overlay**: directly usable; strongest general first-build method.[cite:47][cite:54]
2. **RIC-SNM — Rank-IC Gated Sector News Momentum**: directly usable; best Track B signal-validation and sizing layer.[cite:62][cite:64]
3. **PT-NAI — Permutation-Tested News Attention Index**: directly usable; strongest shared intermediate signal layer.[cite:40][cite:45]
4. **VS-MNRG — Volatility-Scaled Macro News Risk Gate**: directly usable; best Track A-specific method.[cite:40][cite:94]
5. **SESRO — Sparse Event-Sensitivity Regression Overlay**: adaptable but higher overfitting risk; useful for ablation and later builds.[cite:36][cite:30]
6. **BL-NVO — Black-Litterman News View Overlay**: adaptable and elegant, but more parameter-sensitive; best as a second-stage overlay theory branch.[cite:48][cite:56][cite:51]
7. **ES-GPNS — Entity-Sector Graph Propagation News Score**: adaptable; potentially powerful for text-to-sector mapping, but requires more engineering and audit controls.[cite:32][cite:65]
8. **TC-TRIG — Transformer-Cached Text-to-Sector Relevance + Rule Impact Gate**: adaptable but dependency-sensitive; best transformer-related method if kept offline and optional.[cite:19][cite:22][cite:105]

## 6. Method 1 — Event-Study Calibrated News Impact Overlay

### 6.1 Core Idea

ESC-NIO converts structured news events into ETF or sector tilts by first estimating the historical abnormal return response of each asset to each event class, then using those calibrated responses as impact scalars in a daily overlay signal.[cite:47][cite:54] The method is strong because it ties every event weight to an explicit event-study estimate rather than to heuristic scoring alone.[cite:47][cite:104]

### 6.2 Literature / Framework Basis

Classical event studies define abnormal return as the difference between observed return and expected return under a normal model, most often the market model.[cite:47][cite:54] They then aggregate abnormal returns over an event window into CAR and average across repeated events into CAAR, which is exactly the quantity needed for a reusable event impact estimate.[cite:47][cite:52][cite:104] This methodology is directly usable for ETFs and sector indices, not only single stocks, so long as the expected-return model is defined against an appropriate market benchmark.[cite:47][cite:95]

### 6.3 Inputs

- Daily ETF or sector returns for the tradable universe.[cite:47]
- A reference market return series for the expected-return model, such as a broad China equity index.[cite:47]
- Timestamped Top-20 daily news items filtered to the official cutoff.[cite:47]
- A deterministic event taxonomy assigning each news item to classes such as monetary easing, property support, AI policy support, export/tariff shock, regulation, earnings/fundamentals, or crisis event.[cite:32][cite:65]
- A deterministic relevance score from event to ETF/sector, initially lexical or entity based.[cite:32][cite:65]

### 6.4 Algorithm

For each date \(t\) and asset \(j\):

1. Collect all news items available before the daily cutoff.[cite:47]
2. Assign each news item \(i\) to an event class \(c_i\), direction \(d_i \in \{-1,0,1\}\), and confidence \(q_i\) using deterministic rules.[cite:32][cite:65]
3. On 2024 data only, estimate a market-model expected return for each asset \(j\): \(R_{j,t}=\alpha_j+\beta_jR_{m,t}+\epsilon_{j,t}\).[cite:47]
4. For every historical event instance of class \(c\) relevant to asset \(j\), compute abnormal returns and a chosen event-window CAR such as \([-1,+3]\) or \([0,+5]\).[cite:47][cite:52]
5. Average CAR across all 2024 events of class \(c\) for asset \(j\) to obtain \(CAAR_{j,c}\), and scale by recent volatility to obtain an impact coefficient \(I_{j,c}\).[cite:47][cite:104]
6. At runtime, compute the daily signal \(S_{t,j}=\sum_{i\in D_t} I_{j,c_i}\,R_{i,j}\,d_i\,q_i\), where \(R_{i,j}\) is the event-to-asset relevance score.[cite:47]
7. Apply activation gates: signal magnitude, confidence, turnover budget, and drawdown/risk controls must all pass before any tilt is active.[cite:47][cite:40]
8. Convert the signal into a bounded overlay \(\Delta w_{t,j}=k_j\,S_{t,j}\) with clipping, turnover limits, and re-normalization relative to the base allocator.[cite:47]

### 6.5 Mathematical Formulation

The market model is:

\[
R_{j,t}=\alpha_j+\beta_jR_{m,t}+\epsilon_{j,t}
\]

The abnormal return is:

\[
AR_{j,t}=R_{j,t}-(\hat\alpha_j+\hat\beta_jR_{m,t})
\]

The event-window cumulative abnormal return is:

\[
CAR_{j,k}(t_1,t_2)=\sum_{\tau=t_1}^{t_2} AR_{j,\tau}
\]

The class-level average event response is:

\[
CAAR_{j,c}=\frac{1}{N_{j,c}}\sum_{k=1}^{N_{j,c}} CAR_{j,k}
\]

A volatility-scaled impact coefficient can then be defined as:

\[
I_{j,c}=\frac{CAAR_{j,c}}{\sigma_j}
\]

The daily overlay signal is:

\[
S_{t,j}=\sum_{i\in D_t} I_{j,c_i}\,R_{i,j}\,d_i\,q_i
\]

### 6.6 Track A Use Case

For Track A, ESC-NIO should focus on broad macro event classes such as monetary policy, liquidity stress, fiscal stimulus, property support, and crisis news.[cite:40][cite:47] The signal should mainly modulate risk-on versus risk-off exposure among equity, bond, and gold sleeves rather than attempt aggressive directional macro forecasting.[cite:40][cite:94]

### 6.7 Track B Use Case

For Track B, ESC-NIO is a natural fit because sector ETFs can exhibit more direct post-event responses to industry policy, regulation, thematic support, and sector-specific fundamentals.[cite:33][cite:40] It is especially suited to ranking adjustments and bounded sector tilts layered on top of the preserved LEEQA/S1 baselines rather than replacing them.[cite:33]

### 6.8 2024 Training / Tuning Protocol

All event windows, class definitions, expected-return benchmarks, impact clipping ranges, activation thresholds, and tilt scales must be selected using 2024 only.[cite:47][cite:104] Parameter search should be deliberately low-dimensional, and classes with too few observations should be merged or shrunk toward zero to avoid unstable CAAR estimates.[cite:47][cite:102]

### 6.9 2025 Test Protocol

On 2025 data, event classes, expected-return specifications, impact coefficients, and gates are frozen.[cite:47] The method is evaluated only as a bounded overlay on preserved baseline allocators, with official-semantics replay and no parameter adaptation using 2025 outcomes.[cite:47]

### 6.10 Required Ablations

- Base allocator only.[cite:47]
- ESC-NIO with real news.[cite:47]
- No-news and zero-news overlays.[cite:47]
- Shuffled-news dates and randomized event labels.[cite:47]
- Impact gate on versus off.[cite:47]
- Confidence gate on versus off.[cite:47]
- Relevance source swap: lexical only versus richer mapping.[cite:32]
- Overlay-strength and turnover-cap sweeps.[cite:47]
- Track A only, Track B only, and regime splits.[cite:40]
- Event-category removal tests.[cite:40]

### 6.11 Implementation Complexity

Implementation cost is **medium** because the method requires event labeling, benchmark estimation, CAR aggregation, and gated overlay logic, but no heavy models or complicated training loops.[cite:47][cite:54]

### 6.12 Risks and Failure Modes

The main risks are sparse event counts, unstable CAAR estimates for rare classes, overlapping events that contaminate windows, and the possibility that a market-model benchmark is too crude for some ETFs.[cite:47][cite:102][cite:104] Another risk is that China-specific asymmetry, where negative news has a stronger volatility effect than positive news, may be under-modeled if the same windows and scaling are used symmetrically for both directions.[cite:40][cite:45]

### 6.13 Verdict

**Directly usable.** ESC-NIO is the best first-build method because it is interpretable, mathematically disciplined, and naturally compatible with deterministic overlay design.[cite:47][cite:54]

## 7. Method 2 — Rank-IC Gated Sector News Momentum

### 7.1 Core Idea

RIC-SNM treats sector-level news scores as factors and asks a simple question: do sectors with stronger news scores on day \(t\) actually outperform on days \(t+1\) to \(t+h\) in 2024?[cite:62][cite:64] Only factors with stable IC or rank-IC and acceptable information ratio are allowed to drive a Track B overlay.[cite:62][cite:69]

### 7.2 Literature / Framework Basis

Information coefficient is a standard factor-evaluation concept measuring the relationship between factor values and subsequent returns.[cite:62][cite:64] Rank-IC, often computed as a Spearman correlation, is particularly suitable when the goal is relative sector ranking rather than exact return prediction.[cite:62][cite:69] This framework is directly usable because the competition already resembles a daily ranking-and-weighting problem over a small ETF universe.[cite:62]

### 7.3 Inputs

- Daily sector-level signals such as ESC-NIO outputs, NAI components, or sector sentiment scores.[cite:40][cite:47]
- Future sector ETF returns over chosen horizons such as 1, 3, and 5 trading days.[cite:62]
- Turnover and weight constraints from the base allocator design.[cite:62]

### 7.4 Algorithm

For each day \(t\):

1. Compute candidate sector news factors \(f_{k,t,j}\) for each sector \(j\) and factor family \(k\).[cite:62][cite:40]
2. For each horizon \(h\), compute future sector return \(r_{t+h,j}\) or cumulative forward return.[cite:62]
3. In 2024, compute daily cross-sectional rank-IC values \(IC_{k,t}^{(h)}=\rho_s(f_{k,t,*},r_{t+h,*})\).[cite:62][cite:69]
4. Compute each factor’s average IC and information ratio \(IR_k^{(h)}=\overline{IC}/\sigma(IC)\).[cite:64]
5. Keep only factors and horizons that exceed minimum IC and IR thresholds selected on 2024.[cite:62][cite:64]
6. Form a composite sector score \(S_{t,j}=\sum_k \omega_k f_{k,t,j}\), with weights based on 2024 IC or IR.[cite:62]
7. Apply activation gates: only if the composite score and historical IC confidence are both strong enough does the overlay activate.[cite:62]
8. Convert the score into a bounded sector tilt and apply turnover caps relative to the base Track B allocator.[cite:62]

### 7.5 Mathematical Formulation

For factor \(k\) and horizon \(h\), define:

\[
IC_{k,t}^{(h)}=\rho_s(f_{k,t,*},r_{t+h,*})
\]

Then compute:

\[
\overline{IC}_{k}^{(h)}=\frac{1}{T}\sum_t IC_{k,t}^{(h)}
\]

and

\[
IR_k^{(h)}=\frac{\overline{IC}_{k}^{(h)}}{\sigma(IC_{k,t}^{(h)})}
\]

A composite score can be defined as:

\[
S_{t,j}=\sum_k \omega_k f_{k,t,j}, \quad \omega_k \propto \max(IR_k,0)
\]

### 7.6 Track A Use Case

For Track A, RIC-SNM is only moderately suitable because the asset universe is small and relative ranking carries less information than broad risk-state detection.[cite:62][cite:40] It can still be used as a gate for macro sleeves if factors are defined at the equity-versus-defensive level.[cite:62]

### 7.7 Track B Use Case

For Track B, RIC-SNM is one of the strongest methods because sector rotation is naturally a ranking problem.[cite:33][cite:62] It is especially powerful as a guardrail: even if many sector news ideas are generated, only those with positive and stable 2024 rank-IC are allowed to move the portfolio.[cite:62][cite:69]

### 7.8 2024 Training / Tuning Protocol

Choose factor families, prediction horizons, IC/IR thresholds, factor-combination weights, and tilt mappings using 2024 only.[cite:62][cite:64] To limit overfitting, the number of retained factors should remain small, and overlapping factor definitions should be merged or regularized.[cite:62]

### 7.9 2025 Test Protocol

Freeze factors, thresholds, and weights after 2024.[cite:62] On 2025, compute the composite score and activate tilts only through the frozen IC-gating logic.[cite:62]

### 7.10 Required Ablations

- Base allocator only.[cite:62]
- Real-news RIC-SNM.[cite:62]
- No-news and zero-news controls.[cite:62]
- Shuffled-news dates.[cite:62]
- IC gate on versus off.[cite:62]
- Rank-IC versus Pearson-IC.[cite:62]
- Single-horizon versus multi-horizon composite.[cite:62]
- Overlay-strength and turnover sweeps.[cite:62]
- Factor-family removal tests.[cite:62]

### 7.11 Implementation Complexity

Implementation cost is **low to medium** because the method uses simple correlations and score combinations, but it does require a robust daily factor-evaluation pipeline.[cite:62][cite:64]

### 7.12 Risks and Failure Modes

The biggest risk is sample noise: 2024 may make some factors look useful by chance, especially with a small sector universe.[cite:64] Another risk is that the IC filter becomes too strict and suppresses useful signals, or too loose and admits noisy ones.[cite:62]

### 7.13 Verdict

**Directly usable.** RIC-SNM is the best signal-validation and sizing layer for Track B, and one of the highest-priority methods after ESC-NIO.[cite:62][cite:69]

## 8. Method 3 — Permutation-Tested News Attention Index

### 8.1 Core Idea

PT-NAI constructs a transparent News Attention Index for each asset or sector using tone, optimism, attention, and tone dispersion, then validates whether that index has predictive content beyond chance using permutation and shuffled-date tests.[cite:40][cite:45][cite:94] It is designed as a shared intermediate signal, not as a direct end-to-end allocator.[cite:40]

### 8.2 Literature / Framework Basis

Chinese news-media sentiment research based on GDELT constructs several interpretable sentiment measures and finds that higher tone and optimism, lower attention, and smaller dispersion are associated with better next-day returns, while low sentiment, high attention, and high dispersion are associated with higher volatility.[cite:40][cite:45][cite:94] Those findings make PT-NAI directly usable as a financially interpretable signal family, especially because the competition already provides daily curated hot-news items.[cite:40]

### 8.3 Inputs

- Daily Top-20 news items and timestamps.[cite:40]
- A sentiment engine, initially dictionary-based or rule-based, optionally replaced later by cached transformer sentiment.[cite:105][cite:19]
- Asset or sector relevance mappings for assigning each news item to one or more targets.[cite:32][cite:65]

### 8.4 Algorithm

For each day \(t\) and asset \(j\):

1. Map relevant news items to asset \(j\).[cite:40]
2. Compute article-level tone scores and positivity indicators.[cite:40]
3. Define component series:
   - \(Tone_{t,j}\): average tone.
   - \(Opt_{t,j}\): share of positive items.
   - \(Attn_{t,j}\): news count or weighted news count.
   - \(Disp_{t,j}\): standard deviation of tone across relevant items.[cite:40][cite:45]
4. Construct a composite index \(NAI_{t,j}=a_1 Tone_{t,j}+a_2 Opt_{t,j}+a_3 Attn_{t,j}+a_4 Disp_{t,j}\).[cite:40]
5. Use 2024 only to estimate sign choices and weights \(a_k\) by IC, regression, or simple grid search.[cite:40]
6. Run permutation tests by shuffling dates within appropriate blocks and recomputing predictive statistics; reject specifications that fail to outperform permuted benchmarks.[cite:40]
7. Feed the accepted NAI into Track A risk gates or Track B ranking overlays.[cite:40]

### 8.5 Mathematical Formulation

A simple composite specification is:

\[
NAI_{t,j}=a_1 Tone_{t,j}+a_2 Opt_{t,j}+a_3 Attn_{t,j}+a_4 Disp_{t,j}
\]

A significance check can be built from empirical permutation distributions of IC, Sharpe improvement, or predictive-regression t-statistics under date-shuffled NAI series.[cite:40]

### 8.6 Track A Use Case

For Track A, PT-NAI should be aggregated at a market-wide level and interpreted mainly as a risk-state proxy rather than a directional alpha forecast.[cite:40][cite:94] High attention plus negative tone and high dispersion is especially useful as a defensive or de-risking signal.[cite:40]

### 8.7 Track B Use Case

For Track B, PT-NAI works best at the sector level, where attention and tone are more directly tied to rotation opportunities.[cite:33][cite:40] It should typically be combined with event impact or IC gating rather than used alone.[cite:33][cite:62]

### 8.8 2024 Training / Tuning Protocol

Use 2024 only to define sentiment scoring choices, relevance rules, aggregation formulas, component weights, and permutation-test acceptance thresholds.[cite:40] Negative-news asymmetry should be explicitly modeled because the Chinese literature shows stronger overreaction to negative sentiment shocks.[cite:40][cite:45]

### 8.9 2025 Test Protocol

On 2025, the component definitions and weights remain fixed.[cite:40] The method is evaluated both as a standalone intermediate signal and as an input to ESC-NIO, RIC-SNM, or VS-MNRG overlays.[cite:40]

### 8.10 Required Ablations

- Base allocator only.[cite:40]
- Real PT-NAI.[cite:40]
- Zero-news PT-NAI.[cite:40]
- Shuffled-date PT-NAI.[cite:40]
- Component removal: tone only, attention only, dispersion only.[cite:40]
- Symmetric versus asymmetric negative-news weighting.[cite:40]
- Lexical sentiment versus cached transformer sentiment.[cite:19][cite:105]
- Overlay-strength and regime-split tests.[cite:40]

### 8.11 Implementation Complexity

Implementation cost is **low to medium** because the method mainly requires aggregation, validation, and discipline around permutation tests rather than complex model fitting.[cite:40]

### 8.12 Risks and Failure Modes

The biggest risk is building an index that looks intuitive but is actually just measuring news volume noise.[cite:40] Another risk is incorrectly transferring market-level sentiment relationships to sector-level behavior without validating sector-specific relevance and sensitivity.[cite:40][cite:62]

### 8.13 Verdict

**Directly usable.** PT-NAI is the best shared intermediate signal layer and should be part of the first-build stack.[cite:40][cite:45]

## 9. Method 4 — Volatility-Scaled Macro News Risk Gate

### 9.1 Core Idea

VS-MNRG is a Track A-specific overlay that transforms macro news sentiment into a risk-scaling coefficient rather than a direct return forecast.[cite:40][cite:94] The method is intentionally conservative: when macro news becomes broadly negative, attention-heavy, and dispersion-rich, equity exposure is scaled down and defensive sleeves are scaled up.[cite:40]

### 9.2 Literature / Framework Basis

Chinese news-sentiment research finds that low tone and optimism, high attention, and high tone dispersion are associated with larger subsequent volatility.[cite:40][cite:45] That evidence supports the view that macro news is often more useful for risk management than for point-return prediction in a small macro ETF universe.[cite:40]

### 9.3 Inputs

- Market-wide PT-NAI components.[cite:40]
- Realized portfolio or equity-sleeve volatility.[cite:40]
- Recent drawdown and turnover state variables.[cite:40]
- Base Track A weights from the preserved allocator.[cite:13]

### 9.4 Algorithm

1. Build market-wide tone, optimism, attention, and dispersion measures from the day’s news.[cite:40]
2. Construct a risk index such as \(RI_t=b_1(-Tone_t)+b_2 Attn_t+b_3 Disp_t+b_4 DD_t+b_5 \sigma_t\), with all coefficients chosen on 2024 only.[cite:40]
3. Define trigger zones using empirical 2024 quantiles or thresholds.[cite:40]
4. If risk is elevated and confidence is adequate, scale equity exposure by a factor \(\kappa_t\in[\kappa_{min},1]\) and reallocate the difference to bond or gold sleeves according to a fixed rule.[cite:40]
5. If the trigger does not fire, leave the base risk-parity weights unchanged.[cite:13]

### 9.5 Mathematical Formulation

A simple macro risk gate is:

\[
RI_t=b_1(-Tone_t)+b_2 Attn_t+b_3 Disp_t+b_4 DD_t+b_5\sigma_t
\]

with equity scaling:

\[
w_{t,eq}^{final}=\kappa_t w_{t,eq}^{base}, \quad \kappa_t = g(RI_t)
\]

where \(g(\cdot)\) is a clipped monotone function chosen using 2024 only.[cite:40]

### 9.6 Track A Use Case

This method is built for Track A.[cite:40] It uses news to decide whether the macro portfolio should become more defensive, not which cyclical sector should lead tomorrow.[cite:40]

### 9.7 Track B Use Case

Track B can use the same risk state as a portfolio-level throttle, but VS-MNRG is not its primary alpha method.[cite:40] At most, it should act as a regime-aware cap on sector-overlay strength during panic news states.[cite:40]

### 9.8 2024 Training / Tuning Protocol

Calibrate component definitions, coefficients, scaling rules, thresholds, and maximum de-risking intensity on 2024 only.[cite:40] Use simple forms and few parameters so that the method remains auditable and robust.[cite:40]

### 9.9 2025 Test Protocol

On 2025, the risk index and scaling function are frozen.[cite:40] The method is evaluated only as a bounded risk-scaling add-on to preserved Track A allocators.[cite:13]

### 9.10 Required Ablations

- Base allocator only.[cite:40]
- VS-MNRG active.[cite:40]
- News-only risk gate versus volatility-only risk gate.[cite:40]
- Zero-news macro risk index.[cite:40]
- Shuffled macro news dates.[cite:40]
- Drawdown gate on versus off.[cite:40]
- Equity-scaling intensity sweep.[cite:40]

### 9.11 Implementation Complexity

Implementation cost is **low to medium** because the method uses simple scalars and deterministic reweighting.[cite:40]

### 9.12 Risks and Failure Modes

The main failure mode is whipsaw: the portfolio may repeatedly de-risk during noisy news bursts and then lag during rebounds.[cite:40] Another failure mode is overfitting the threshold structure to 2024’s stress patterns.[cite:40]

### 9.13 Verdict

**Directly usable.** VS-MNRG is the best Track A-specific method and should be included in the first-build macro overlay plan.[cite:40][cite:94]

## 10. Method 5 — Sparse Event-Sensitivity Regression Overlay

### 10.1 Core Idea

SESRO estimates which event features actually matter by fitting sparse regressions from structured event features to subsequent asset returns, then using predicted event response as the overlay signal.[cite:36][cite:30] It tries to go one level beyond simple event averages by allowing combinations of event class, direction, intensity, and attention to matter jointly.[cite:36]

### 10.2 Literature / Framework Basis

Event-driven trading systems often regress post-event returns on structured event features to estimate conditional event response.[cite:36][cite:30] Sparse methods such as LASSO are adaptable here because they can zero out unstable or redundant event features when the sample is limited.[cite:36]

### 10.3 Inputs

- Structured event features from deterministic labeling, including class, direction, source count, tone bucket, attention bucket, novelty bucket, and relevance score.[cite:32][cite:65]
- Future asset returns over chosen horizons.[cite:36]
- Base allocator weights and overlay constraints.[cite:36]

### 10.4 Algorithm

1. For every 2024 event instance relevant to asset \(j\), create a feature vector \(x_{k,j}\).[cite:36]
2. Define forward-return target \(y_{k,j}^{(h)}\) over horizon \(h\).[cite:36]
3. Fit a sparse model such as LASSO using only 2024 events.[cite:36]
4. Retain the resulting coefficient vector \(\beta^{(h)}\) and zero out unstable small coefficients.[cite:36]
5. For a new event in 2025, compute predicted response \(\hat y=x^\top\beta\).[cite:36]
6. Aggregate predicted responses across same-day events into \(S_{t,j}\).[cite:36]
7. Activate a bounded overlay only if magnitude, confidence, and turnover gates pass.[cite:36]

### 10.5 Mathematical Formulation

For horizon \(h\), the core estimation problem is:

\[
\min_{\beta}\sum_k (y_k^{(h)}-x_k^\top\beta)^2 + \lambda \lVert \beta \rVert_1
\]

The daily signal is then:

\[
S_{t,j}=\sum_{i\in D_t} x_{i,j}^\top\hat\beta
\]

### 10.6 Track A Use Case

For Track A, SESRO is only moderately useful because the universe is small and macro events are often better handled with simple risk gates.[cite:40][cite:36] It may still be useful if macro event classes are very carefully constrained.[cite:36]

### 10.7 Track B Use Case

For Track B, SESRO is more promising because sector events are richer and more numerous.[cite:33][cite:36] It can learn which combinations of event class and tone are consistently associated with positive or negative sector responses.[cite:36]

### 10.8 2024 Training / Tuning Protocol

Choose feature families, horizons, penalty strength, coefficient pruning rules, and signal-to-tilt mappings using only 2024.[cite:36] Because event samples may be small, nested validation within 2024 should be conservative and avoid elaborate feature interactions.[cite:36]

### 10.9 2025 Test Protocol

Freeze coefficients, pruning rules, and overlay gates after 2024.[cite:36] Evaluate only as an add-on to preserved baseline allocators.[cite:13]

### 10.10 Required Ablations

- Base allocator only.[cite:36]
- Full SESRO.[cite:36]
- Zero-coefficient and random-coefficient controls.[cite:36]
- Shuffled event-feature rows.[cite:36]
- Sparse versus dense regression.[cite:36]
- Feature-family removal tests.[cite:36]
- Overlay-strength and turnover sweeps.[cite:36]

### 10.11 Implementation Complexity

Implementation cost is **medium to high** because the method requires structured feature engineering, regression management, and careful regularization.[cite:36]

### 10.12 Risks and Failure Modes

The main risk is overfitting: with limited 2024 data, sparse regression can still find unstable patterns if the feature space is too rich.[cite:36] Another risk is reduced interpretability when feature interactions accumulate.[cite:36]

### 10.13 Verdict

**Adaptable but risky.** SESRO is a useful later-build or ablation method, but not a top first-build choice.[cite:36]

## 11. Method 6 — Black-Litterman News View Overlay

### 11.1 Core Idea

BL-NVO converts validated news signals into explicit portfolio views and then feeds them into a Black-Litterman layer on top of a prior portfolio generated by the preserved allocator.[cite:48][cite:56] This method is attractive because it translates signals into views with confidence rather than directly forcing raw scores into portfolio weights.[cite:48]

### 11.2 Literature / Framework Basis

Black-Litterman combines prior equilibrium returns with a set of investor views and a confidence structure to produce posterior expected returns and implied portfolio weights.[cite:48] Recent finance research uses BERT or sentiment-derived scores as inputs to Black-Litterman view formation, which makes the method adaptable to news-overlay construction.[cite:56][cite:51]

### 11.3 Inputs

- A prior portfolio from the preserved baseline allocator.[cite:13]
- A return covariance estimate for the ETF universe.[cite:48]
- Validated news views, ideally from ESC-NIO or PT-NAI after IC-style screening.[cite:47][cite:40][cite:62]
- A confidence specification, ideally tied to 2024 factor stability.[cite:48][cite:56]

### 11.4 Algorithm

1. Start with prior weights \(w_t^{base}\) and a covariance matrix \(\Sigma_t\).[cite:48]
2. Convert validated news signals into a small set of views \(Q_t\), with mapping matrix \(P_t\).[cite:48]
3. Define a diagonal view-uncertainty matrix \(\Omega_t\), where stronger 2024 evidence implies tighter uncertainty.[cite:48][cite:56]
4. Compute posterior expected returns from the Black-Litterman formula.[cite:48]
5. Solve for posterior weights or a posterior active tilt.[cite:48]
6. Clip the active tilt by risk, turnover, and weight caps before combining it with the base allocator.[cite:48]

### 11.5 Mathematical Formulation

A standard Black-Litterman posterior is:

\[
\mu^{BL}=\Pi + \tau\Sigma P^\top (P\tau\Sigma P^\top + \Omega)^{-1}(Q-P\Pi)
\]

where \(\Pi\) is the prior implied return vector, \(Q\) is the news-view vector, and \(\Omega\) captures confidence.[cite:48]

### 11.6 Track A Use Case

For Track A, BL-NVO can encode macro views such as “equity expected return is below prior due to elevated macro risk” or “gold expected return is above prior due to crisis news.”[cite:48][cite:40] It is more elegant than necessary for a first build, but usable.[cite:48]

### 11.7 Track B Use Case

For Track B, BL-NVO can encode sector-overweight and underweight views derived from validated sector news signals.[cite:48][cite:62] This is conceptually attractive, but only after the underlying news signals are already trusted.[cite:48]

### 11.8 2024 Training / Tuning Protocol

Calibrate view scaling, confidence mapping, covariance regularization, and tilt caps using only 2024.[cite:48][cite:56] Keep the number of active views small so that the method remains stable and interpretable.[cite:48]

### 11.9 2025 Test Protocol

Freeze view-construction rules and confidence mappings after 2024.[cite:48] Evaluate only as a bounded overlay over preserved baseline weights.[cite:13]

### 11.10 Required Ablations

- Base allocator only.[cite:48]
- BL-NVO with real views.[cite:48]
- BL-NVO with zero views, which should collapse toward the prior.[cite:48]
- Randomized views.[cite:48]
- Confidence mapping variants.[cite:48]
- Prior covariance variants.[cite:48]
- Overlay-strength and turnover sweeps.[cite:48]

### 11.11 Implementation Complexity

Implementation cost is **medium to high** because the method introduces more matrix-parameter choices than simpler tilt layers.[cite:48]

### 11.12 Risks and Failure Modes

The main risks are parameter sensitivity, excessive complexity relative to the small asset universe, and weak interpretability if too many views are active at once.[cite:48][cite:56]

### 11.13 Verdict

**Adaptable but not first priority.** BL-NVO is best treated as a second-stage overlay-theory branch or an ablation-only enhancement.[cite:48][cite:56]

## 12. Method 7 — Entity-Sector Graph Propagation News Score

### 12.1 Core Idea

ES-GPNS improves text-to-sector relevance by extracting entities and event arguments from Chinese financial news, mapping those entities to sectors and ETFs, and propagating event scores through a fixed graph.[cite:32][cite:65] The method is designed to improve thematic and indirect relevance where simple keyword matching is too brittle.[cite:32]

### 12.2 Literature / Framework Basis

DocFEE and FEED show that document-level Chinese financial event extraction can identify event triggers and arguments in structured ways.[cite:32][cite:65] That makes it feasible to move from “headline contains semiconductor” to “policy body announced support affecting entity cluster X, which maps to sector Y and ETF Z.”[cite:32][cite:65] The method is adaptable rather than directly usable because graph quality depends heavily on engineering and ontology completeness.[cite:32]

### 12.3 Inputs

- Chinese financial event extraction rules or models that output event type and entity arguments.[cite:32][cite:65]
- Static entity-to-sector and sector-to-ETF mappings.[cite:32]
- Event-level polarity and impact signals from ESC-NIO or PT-NAI.[cite:47][cite:40]

### 12.4 Algorithm

1. Parse each news item into event class plus participating entities.[cite:32][cite:65]
2. Assign an event score to each extracted entity based on class, direction, and confidence.[cite:32]
3. Propagate entity scores to sector nodes using exposure-weighted mappings.[cite:32]
4. Propagate sector scores to ETF nodes using fixed constituent or thematic mappings.[cite:32]
5. Aggregate daily node scores into an ETF or sector overlay signal.[cite:32]
6. Apply the usual activation, turnover, and drawdown gates before trading.[cite:47]

### 12.5 Mathematical Formulation

Let \(s_e\) be entity scores, \(W_{ES}\) the entity-to-sector matrix, and \(W_{SJ}\) the sector-to-ETF matrix. Then:

\[
s_{sector}=W_{ES}s_e
\]

and

\[
s_{ETF}=W_{SJ}s_{sector}
\]

The final daily score is the sum of propagated event contributions over all same-day news items.[cite:32]

### 12.6 Track A Use Case

Track A can use ES-GPNS for policy-to-macro sleeve transmission, but the benefit is limited because the macro universe is coarse.[cite:32] The method is therefore only moderately suitable for Track A.[cite:32]

### 12.7 Track B Use Case

Track B benefits more because sector ETFs often respond to indirect thematic and policy relevance, which graph propagation can capture better than pure keywords.[cite:32][cite:65] This is particularly valuable for multi-entity policy headlines that mention ministries, industries, and representative firms together.[cite:32]

### 12.8 2024 Training / Tuning Protocol

Use 2024 only to define ontology scope, edge weights, propagation depth, and pruning rules.[cite:32][cite:65] Keep the graph fixed thereafter to avoid hidden adaptation.[cite:32]

### 12.9 2025 Test Protocol

On 2025, event parsing rules and graph weights are frozen.[cite:32] Use ES-GPNS only as a relevance-enhancement layer feeding deterministic overlay methods, not as a standalone allocator.[cite:32]

### 12.10 Required Ablations

- Base allocator only.[cite:32]
- Direct keyword mapping versus graph propagation.[cite:32]
- Uniform versus weighted graph edges.[cite:32]
- Entity extraction on versus off.[cite:32]
- Randomized graph edges.[cite:32]
- Overlay-strength and turnover sweeps.[cite:32]

### 12.11 Implementation Complexity

Implementation cost is **medium to high** because ontology management, entity normalization, and graph maintenance are nontrivial.[cite:32][cite:65]

### 12.12 Risks and Failure Modes

The main failure modes are incomplete entity coverage, brittle normalization, and graph rules that look sensible but do not materially improve predictive quality over simpler relevance maps.[cite:32][cite:65]

### 12.13 Verdict

**Adaptable.** ES-GPNS is a strong second-build relevance method, but too engineering-heavy for the first build.[cite:32][cite:65]

## 13. Method 8 — Transformer-Cached Text-to-Sector Relevance + Rule Impact Gate

### 13.1 Core Idea

TC-TRIG uses a Chinese FinBERT-style model offline to precompute article embeddings and contextual sentiment, then combines those cached features with deterministic event impact and gating logic.[cite:19][cite:105] The key design principle is that the model never needs to run on the official server if that creates dependency or packaging problems.[cite:19]

### 13.2 Literature / Framework Basis

FinBERT and related financial transformer models outperform dictionary-based methods in contextual financial sentiment classification and capture finance-domain semantics better than general-purpose BERT.[cite:105][cite:22] A Chinese financial sentiment model based on BERT has also been published and is available as a pretrained sentiment classifier for Chinese finance text.[cite:19] This makes TC-TRIG adaptable and attractive, but dependency-sensitive, which is why it should be used first as an offline cache rather than as an online runtime dependency.[cite:19][cite:105]

### 13.3 Inputs

- A pre-2026 Chinese financial sentiment model such as finbert-tone-chinese.[cite:19]
- A curated 2024–2025 news corpus from the task feed.[cite:19]
- Sector or ETF prototype texts or prototype embedding centroids.[cite:19][cite:22]
- Deterministic event scores from ESC-NIO or PT-NAI.[cite:47][cite:40]

### 13.4 Algorithm

1. Offline, compute contextual embeddings and sentiment distributions for every news item in the 2024–2025 corpus.[cite:19][cite:105]
2. Construct prototype vectors for sectors or ETFs from descriptive texts or historical linked news embeddings.[cite:22]
3. Compute cosine relevance between each news item and each asset prototype.[cite:19]
4. Cache the resulting relevance matrix and article-level polarity scores.[cite:19]
5. At daily runtime, read only cached scalar features and combine them with deterministic event impacts, confidence rules, and turnover/drawdown gates.[cite:19][cite:47]
6. If the model cache is unavailable or disabled, fall back to lexical relevance and rule sentiment with no change to the overlay logic.[cite:19]

### 13.5 Mathematical Formulation

Let \(e_i\) be the news embedding and \(p_j\) the sector prototype. Define cached relevance as:

\[
R_{i,j}^{emb}=\frac{e_i^\top p_j}{\lVert e_i\rVert \lVert p_j\rVert}
\]

Then plug this into a deterministic signal such as:

\[
S_{t,j}=\sum_{i\in D_t} I_{i}\,R_{i,j}^{emb}\,d_i\,q_i
\]

where \(I_i\) and \(d_i\) come from the rule-based impact layer.[cite:19][cite:47]

### 13.6 Track A Use Case

For Track A, TC-TRIG can help distinguish whether a macro headline is more relevant to broad equities, defensives, bonds, or gold when lexical matching is ambiguous.[cite:19] The value is modest but real.[cite:19]

### 13.7 Track B Use Case

For Track B, TC-TRIG is more valuable because sector relevance can be nuanced and semantic rather than purely lexical.[cite:19][cite:22] It is especially useful for thematic stories such as AI, semiconductors, or regulation where exact sector keywords may not appear.[cite:19]

### 13.8 2024 Training / Tuning Protocol

Use 2024 only to choose the sector-prototype construction method, similarity thresholds, combination weights with lexical relevance, and confidence cutoffs.[cite:19] Any embedding-based tuning must be benchmarked against a lexical baseline and kept low-dimensional.[cite:19][cite:105]

### 13.9 2025 Test Protocol

On 2025, all cached features and thresholds are frozen.[cite:19] Evaluate the method only as a relevance-refinement layer within a deterministic overlay, not as a separate end-to-end model.[cite:19]

### 13.10 Required Ablations

- Base allocator only.[cite:19]
- Lexical relevance only.[cite:19]
- Cached embedding relevance only.[cite:19]
- Lexical plus cached embeddings.[cite:19]
- Zero-news and shuffled-news tests.[cite:19]
- Impact gate on versus off.[cite:47]
- Confidence gate on versus off.[cite:19]
- Transformer cache disabled fallback.[cite:19]

### 13.11 Implementation Complexity

Implementation cost is **high relative to first-build methods** because offline feature generation, cache management, and audit controls are required.[cite:19][cite:105]

### 13.12 Risks and Failure Modes

The main risks are dependency friction, opaque relevance scores, distribution mismatch between model training data and the competition feed, and accidental reliance on a path that cannot be cleanly packaged for official evaluation.[cite:19][cite:105] These are manageable only if the lexical fallback remains first-class and every improvement is shown in ablations.[cite:19]

### 13.13 Verdict

**Adaptable but dependency-sensitive.** TC-TRIG is the best transformer-related method, but it should be built second and kept optional.[cite:19][cite:105]

## 14. Comparative Method Table

Scores are on a 1–5 scale, where 5 is best. For **Expected Value**, **Robustness**, **Interpretability**, **Ablation Quality**, and **Official Compatibility**, a higher number is better.[cite:47][cite:40] For **Implementation Cost**, **Dependency Risk**, and **Leakage Risk**, a higher number means lower burden or lower risk, so 5 is best and 1 is worst.[cite:47][cite:19] The **Overall Score** is a qualitative synthesis rather than a purely mechanical formula.[cite:47][cite:40]

| Rank | Method | Core Framework | Track A Fit | Track B Fit | Expected Value | Robustness | Interpretability | Implementation Cost | Dependency Risk | Leakage Risk | Ablation Quality | Official Compatibility | Overall Score | Decision |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | Event-Study Calibrated News Impact Overlay (ESC-NIO) | Event study / CAR / CAAR | 4[cite:47] | 5[cite:47] | 4[cite:47] | 4[cite:47] | 5[cite:47] | 4[cite:47] | 5[cite:47] | 4[cite:47] | 5[cite:47] | 5[cite:47] | 4.6 | build_first |
| 2 | Permutation-Tested News Attention Index (PT-NAI) | Chinese sentiment index / permutation validation | 4[cite:40] | 4[cite:40] | 4[cite:40] | 4[cite:40] | 5[cite:40] | 4[cite:40] | 5[cite:40] | 5[cite:40] | 5[cite:40] | 5[cite:40] | 4.5 | build_first |
| 3 | Rank-IC Gated Sector News Momentum (RIC-SNM) | IC / rank-IC / factor gating | 3[cite:62] | 5[cite:62] | 4[cite:62] | 4[cite:64] | 4[cite:62] | 4[cite:62] | 5[cite:62] | 5[cite:62] | 5[cite:62] | 5[cite:62] | 4.4 | build_first |
| 4 | Volatility-Scaled Macro News Risk Gate (VS-MNRG) | News-volatility risk gate | 5[cite:40] | 2[cite:40] | 4[cite:40] | 4[cite:40] | 4[cite:40] | 4[cite:40] | 5[cite:40] | 5[cite:40] | 5[cite:40] | 5[cite:40] | 4.3 | build_first |
| 5 | Transformer-Cached Text-to-Sector Relevance + Rule Impact Gate (TC-TRIG) | Offline transformer relevance cache | 3[cite:19] | 4[cite:19] | 3[cite:19] | 3[cite:19] | 3[cite:105] | 2[cite:19] | 2[cite:19] | 4[cite:19] | 4[cite:19] | 3[cite:19] | 3.1 | build_second |
| 6 | Entity-Sector Graph Propagation News Score (ES-GPNS) | Event extraction + graph propagation | 3[cite:32] | 4[cite:32] | 3[cite:32] | 3[cite:32] | 3[cite:32] | 3[cite:32] | 3[cite:32] | 4[cite:32] | 4[cite:32] | 4[cite:32] | 3.4 | build_second |
| 7 | Sparse Event-Sensitivity Regression Overlay (SESRO) | Sparse regression on event features | 2[cite:36] | 4[cite:36] | 3[cite:36] | 3[cite:36] | 3[cite:36] | 3[cite:36] | 4[cite:36] | 4[cite:36] | 4[cite:36] | 4[cite:36] | 3.3 | build_later |
| 8 | Black-Litterman News View Overlay (BL-NVO) | Black-Litterman posterior tilting | 3[cite:48] | 3[cite:48] | 3[cite:48] | 3[cite:48] | 3[cite:48] | 2[cite:48] | 4[cite:48] | 4[cite:48] | 3[cite:48] | 3[cite:48] | 3.0 | ablation_only |

## 15. Top 5 Recommended Methods

1. **ESC-NIO** — best first-build method overall because it calibrates impact with explicit event-study evidence rather than heuristic intuition.[cite:47][cite:54]
2. **PT-NAI** — best shared intermediate signal because it is interpretable and supported by Chinese return-and-volatility evidence.[cite:40][cite:45]
3. **RIC-SNM** — best Track B validation and sizing layer because sector rotation naturally benefits from IC-based ranking quality control.[cite:62][cite:69]
4. **VS-MNRG** — best Track A method because macro news is most useful as a risk-scaling input rather than a directional alpha signal.[cite:40]
5. **TC-TRIG** — best transformer-related method if kept offline and optional.[cite:19][cite:105]

## 16. Top 10 Extended Candidate Methods

The eight fully developed methods above cover the strongest candidates.[cite:47][cite:40] If two additional extended candidates are needed for later exploration, the most defensible additions are:

- **Hierarchical Daily News Attention Pooling**: a HAN-inspired document-aggregation layer used only as an offline feature extractor or scoring aid, not as a portfolio controller; this is adaptable but too heavy for first build.[cite:61]
- **Granger-Screened News Sensitivity Filter**: a secondary diagnostic that tests whether certain news indices Granger-cause returns or volatility, used only as a validation screen and not as the core trading method.[cite:37][cite:40]

## 17. Track A Recommendation

Track A should prioritize **VS-MNRG** as the main active news method and use **PT-NAI** plus coarse **ESC-NIO** as upstream signal sources.[cite:40][cite:47] The practical design principle is simple: Track A should use news to adjust risk level and defensive posture, not to override the no-news risk-parity core with aggressive directional views.[cite:40]

A sensible Track A research stack is therefore: market-wide PT-NAI components, macro event buckets inside ESC-NIO, and a volatility/drawdown-aware gate that scales equity risk only when multiple conditions agree.[cite:40][cite:47] This preserves the strength of the existing Track A baseline while giving news a clearly bounded and interpretable role.[cite:13]

## 18. Track B Recommendation

Track B should prioritize **ESC-NIO + PT-NAI + RIC-SNM** as the core overlay stack.[cite:47][cite:40][cite:62] ESC-NIO provides event-class impact estimates, PT-NAI provides a transparent sector-level news state, and RIC-SNM determines whether those signals are actually strong enough to deserve live portfolio influence.[cite:47][cite:62]

Only after this deterministic stack is validated should Track B add **ES-GPNS** for richer entity-to-sector relevance or **TC-TRIG** for offline semantic relevance refinement.[cite:32][cite:19] That ordering is important because it makes later complexity accountable to a simpler baseline.[cite:32][cite:19]

## 19. Recommended First Build

The recommended first build is a deterministic four-part stack:

1. **PT-NAI** to create asset or sector-level news attention and tone features.[cite:40]
2. **ESC-NIO** to convert structured event classes into volatility-scaled impact coefficients.[cite:47]
3. **RIC-SNM** to gate and size Track B sector tilts using 2024 IC evidence.[cite:62]
4. **VS-MNRG** to gate Track A macro risk using market-wide news stress states.[cite:40]

This stack is favored because all four components are interpretable, trainable on 2024 only, compatible with deterministic runtime operation, and easy to probe with placebo and shuffled-news ablations.[cite:47][cite:40][cite:62]

## 20. Methods to Defer or Reject

The following methods should be **deferred** rather than prioritized:

- **TC-TRIG**, because offline transformer caching is useful but dependency-sensitive.[cite:19][cite:105]
- **ES-GPNS**, because graph relevance adds engineering burden before its incremental value is proven.[cite:32][cite:65]
- **SESRO**, because sparse event regression is informative but more fragile under limited 2024 samples.[cite:36]
- **BL-NVO**, because Black-Litterman adds parameter complexity before the underlying news views are fully proven.[cite:48]

The following methods should be **rejected for the current phase**:

- Full LLM portfolio allocators.[cite:105]
- Deep RL and graph RL allocators.[cite:61]
- Unbounded end-to-end transformer allocators and black-box summarize-to-trade systems.[cite:61][cite:105]

These approaches are not aligned with the task’s need for deterministic fallback, modular ablations, and clean official-server reproducibility.[cite:47][cite:19]

## 21. Required Ablation Suite

Every promotion-seeking method must pass the following suite:

- Base allocator only.[cite:47]
- Real-news overlay.[cite:47]
- No-news and zero-news overlays.[cite:47]
- Shuffled-news dates.[cite:47]
- Randomized event labels.[cite:47]
- Lexical relevance versus embedding relevance when embeddings are used.[cite:19]
- Impact gate on versus off.[cite:47]
- Sensitivity or IC gate on versus off.[cite:62][cite:36]
- Confidence gate on versus off.[cite:47]
- Overlay-strength sweep.[cite:47]
- Turnover-cap sweep.[cite:47]
- Track A only and Track B only tests.[cite:13]
- High-volatility versus low-volatility regime splits.[cite:40]
- Event-category removal tests.[cite:40]

The single most important ablation is the combination of **zero-news and shuffled-news controls with gate on/off tests**, because that combination directly answers whether gains come from correctly timed news information or from structural portfolio changes and 2024 overfitting.[cite:47][cite:62]

## 22. Promotion Criteria

Before any method is considered for official runtime promotion, all of the following must be true:

- The method is selected and tuned only on 2024.[cite:47]
- The method is frozen before 2025 evaluation.[cite:47]
- It improves over the relevant preserved base allocator on 2025 in Sharpe and/or drawdown-adjusted terms without unacceptable turnover deterioration.[cite:47]
- It survives zero-news and shuffled-news ablations.[cite:47]
- It does not materially worsen maximum drawdown.[cite:40]
- Its turnover remains acceptable under the task’s friction setting.[cite:47]
- Dependency footprint is acceptable, with no runtime API calls or silent downloads.[cite:19]
- A deterministic fallback exists.[cite:19]
- Local official-semantics replay passes.[cite:47]
- Official-server parity passes.[cite:47]
- Final human approval is granted after trace review and audit.[cite:47]

## 23. Open Questions for Synthesis

Several questions remain open and should be answered empirically rather than by intuition.[cite:47][cite:40] First, what is the right granularity for Chinese event taxonomy before the class counts become too sparse for stable CAAR estimation?[cite:47][cite:32] Second, how much of the gain in Track B comes from improved relevance mapping versus improved impact calibration?[cite:32][cite:47] Third, does transformer-cached relevance produce enough incremental value over lexical relevance to justify packaging and audit costs?[cite:19][cite:105]

A fourth question is whether Track A should have its own macro-specific NAI and event taxonomy rather than reusing the Track B sector taxonomy with only minor aggregation.[cite:40] A fifth is whether graph propagation adds enough out-of-sample value to justify its engineering complexity when compared against simpler lexical or prototype-based mappings.[cite:32][cite:65]

## 24. Final Recommendation Block

Best first-build method:

Event-Study Calibrated News Impact Overlay (ESC-NIO).[cite:47][cite:54]

Second-best method:

Rank-IC Gated Sector News Momentum (RIC-SNM).[cite:62][cite:64]

Best Track A method:

Volatility-Scaled Macro News Risk Gate (VS-MNRG).[cite:40][cite:94]

Best Track B method:

ESC-NIO combined with PT-NAI and RIC-SNM as the core Track B overlay stack.[cite:47][cite:40][cite:62]

Best transformer-related method:

Transformer-Cached Text-to-Sector Relevance + Rule Impact Gate (TC-TRIG).[cite:19][cite:105]

Methods to reject/defer:

Defer ES-GPNS and TC-TRIG; build SESRO later; keep BL-NVO as ablation-only; reject full LLM allocators, deep RL, graph RL, and unbounded end-to-end transformer portfolio methods for the current phase.[cite:32][cite:19][cite:48][cite:61][cite:105]

Most important ablation:

Zero-news and shuffled-news controls combined with gate on/off tests.[cite:47][cite:62]

Main implementation risk:

Overfitting 2024-specific Chinese news and regime patterns so that a method appears strong in development but fails to generalize on 2025 and hidden 2026 evaluation.[cite:40][cite:47]
