# PromptOA-Enhance Research Report — Specific Frameworks for News Overlay

## Executive Summary

The validated runtime remains frozen. Track A still centres on no-news risk-parity baselines, while Track B still centres on the deterministic LEEQA-style sector news ranker, with preserved candidates retained for future research rather than immediate promotion. Stage 1 news processing remains MVP-level and rule-based, and the prepared workflow explicitly treats stronger text processing, event impact modelling, embedding caches, and gated overlays as later modular work rather than runtime changes. fileciteturn0file0 fileciteturn0file1 fileciteturn0file4 fileciteturn0file5 fileciteturn0file6 fileciteturn0file7

The literature points to a clear conclusion. News is rarely a stable always-on return forecaster, but it can be useful when treated as **sparse, high-impact, short-horizon, regime-dependent information**. Classical event-study work is still the cleanest starting point for calibrating abnormal return or abnormal volatility reactions, while recent causal critiques warn against long event windows and poorly specified factor models, especially in volatile periods. Evidence from Chinese markets strengthens the case for short-horizon, policy-aware modelling: positive PMI news in China showed asymmetric response patterns lasting up to roughly three days, and economic policy uncertainty appears to lead the Chinese stock market more than the reverse. citeturn25academia5turn29academia4turn29academia9turn39search0turn39search1

Financial NLP research also offers a practical hierarchy. Interpretable lexicons remain valuable as deterministic fallbacks, but contextual financial models such as FinBERT generally improve domain sentiment classification. For Chinese text, title-level extraction is especially relevant here because the shared task distributes daily top news rather than full corporate filings; Title2Event is therefore closer to the task’s input shape than heavier document-level event extractors, while Doc2EDAG and Text2Event remain useful references for structured schemas and argument design. Chinese financial benchmarks show that even strong language models still face substantial difficulty on domain tasks, which argues against black-box end-to-end allocators and in favour of modular, ablatable signal layers. citeturn0academia0turn0academia1turn10academia0turn10academia1turn10academia2turn6academia0turn6academia2

On that basis, the strongest immediate candidates are not generic “use embeddings” or “use attention” ideas. They are specific frameworks: **Event-Study Calibrated News Impact Overlay**, **Permutation-Tested News Attention Index**, **Volatility-Scaled Macro News Risk Gate**, **Rank-IC Gated Sector News Momentum**, and **Sparse Event-Sensitivity Regression Overlay**. Among these, the best first-build method is the event-study-calibrated overlay because it directly connects news classes to measured asset responses under the project’s 2024-only tuning and 2025 frozen-testing discipline. For Track A, the best standalone method is the macro risk gate; for Track B, the best deployment method is the rank-IC-gated sector news momentum layer built on top of event-aware signals. citeturn38academia2turn17academia2turn29academia8turn29academia9turn26academia0

Transformer methods should not be first-build dependencies. The most defensible transformer use is an **offline, cached relevance layer** built from Chinese embedding models such as BGE-family encoders, with lexical BM25 and deterministic entity mapping as the mandatory fallback. Official documentation from the BGE project explicitly frames embeddings as retrieval features and the reranker as a more accurate but less efficient second stage; retrieval literature also shows that reranker fine-tuning can improve the training domain while harming generalisation outside it. That profile fits an optional, ablated, second-build relevance module—not a first-layer production dependency. citeturn40view0turn40view1turn40view2turn23academia2turn23academia3turn7academia0

## Method Discovery Scope

This report focuses on **specific named frameworks** that can be built modularly on top of preserved baselines and evaluated under the project’s frozen-runtime, deterministic-fallback, 2024-tune/2025-test discipline. The design filter is narrower than the general Prompt0A design-space phase: each shortlisted method must produce an explicit signal, expose controllable gates, support credible null ablations, and preserve official-server compatibility if later promoted. fileciteturn0file0 fileciteturn0file4 fileciteturn0file5

The search space was organised into six literature clusters. First, classical and modern **event studies** were reviewed for abnormal return, cumulative abnormal return, short-window response curves, and misspecification risk. Second, **financial news sentiment and event extraction** were reviewed across dictionary methods, FinBERT-style classifiers, aspect-based sentiment, structured event extraction, and Chinese title/document event datasets. Third, **text-to-sector relevance** work was reviewed across BM25, dense embeddings, and reranking. Fourth, **attention-based aggregation** was reviewed, not as a production allocator, but as a possible research comparator for daily news pooling. Fifth, **signal validation** work was reviewed for rank IC, sparse Granger-style screening, and robustness testing. Sixth, **portfolio overlay** literature was reviewed to identify bounded methods for turning news signals into controlled tilts rather than unconstrained allocations. citeturn28news0turn25academia5turn0academia0turn0academia1turn30academia0turn10academia0turn10academia1turn23academia2turn40view2turn20academia0turn20academia3turn38academia1turn43search0turn35academia0turn35academia3

The main **suitability verdicts** from the literature are as follows. Short-window event studies are directly usable; long-horizon or fully causal event-study frameworks are informative but overly heavy for a first build. Dictionary and rule-based sentiment remain directly usable as interpretable fallbacks; FinBERT-style classification is adaptable but should not become the first dependency. Title2Event is directly adaptable to hot-news workflows; Doc2EDAG and Text2Event are useful schema references but heavier than necessary for an MVP overlay. BM25 is directly usable as a lexical baseline; BGE-family embeddings are adaptable in an offline cache; cross-encoder rerankers are second-stage only. Hierarchical attention is research-only. Black-Litterman is adaptable for bounded news views; exponentiated-gradient overlays are build-later options; full neural portfolio allocators and online LLM allocators remain unsuitable. citeturn10academia0turn10academia1turn10academia2turn0academia1turn41academia3turn23academia2turn40view1turn40view2turn20academia0turn20academia3turn43search0turn35academia0turn27academia0turn27academia2turn27academia3

## Current Baselines and Why Specific Methods Are Needed

The current baseline state is unusually disciplined for a research transition. The official runtime is already validated and frozen. Track A’s official primary and fallback are risk-parity variants without news, and Track B’s official primary remains a deterministic rule-news LEEQA-style ranker with a no-news fallback. Five preserved candidates per track exist precisely to support future overlay analysis without reopening selection prematurely. fileciteturn0file0 fileciteturn0file3 fileciteturn0file4 fileciteturn0file7

That repository state has two research consequences. First, any next-stage news work must be **incremental and modular**, because it is being evaluated against preserved base allocators rather than designed into a greenfield portfolio engine. Second, general design families are now too coarse. “Use event impact”, “use attention”, or “use embeddings” does not resolve what should actually be built next, where to train it, what signal it emits, how to gate it, or how to falsify it. The prepared workflow already points toward a modular sequence—news-attention index, optional embedding cache, event impact and ETF sensitivity, gated overlay, then frozen 2024/2025 evaluation—which is exactly why the next phase needs named, algorithmic frameworks rather than conceptual families. fileciteturn0file5 fileciteturn0file6

Specific methods are also needed because the task’s input regime is narrow and leakage-sensitive. The shared task uses daily Top-20 hot news and historical ETF/index prices, not an unrestricted full news firehose or limitless text corpus. That makes the data budget too small for unconstrained end-to-end neural allocators, but still large enough for structured event studies, sparse regressions, rank-based validation, and cached relevance models. Recent finance-LLM work further underscores the danger of temporal leakage and parametric memorisation in historical backtests, which is precisely why the news layer here must remain modular, frozen, and aggressively ablated. citeturn10academia0turn25academia5turn27academia0turn27academia2turn27academia3

## Search and Literature Map

The event-study literature remains the most useful backbone for a first implementation. The standard toolkit—expected-return model, abnormal return, cumulative abnormal return, and event windows—maps naturally onto daily ETF and sector data. It is also unusually compatible with the project’s reproducibility requirements because it yields compact response tables instead of opaque latent states. At the same time, recent causal critiques matter: they show that factor-model misspecification can bias event studies, especially in volatile periods and over longer horizons. The implication for this project is straightforward: calibrate **short** event-response curves, prefer robust medians to long-horizon means, and never treat event studies as proof of causality beyond the permitted signal horizon. citeturn28news0turn39search0turn39search1turn25academia5

Financial sentiment and event extraction research supports a layered rather than monolithic design. FinBERT papers show that domain-pretrained language models improve financial sentiment tasks relative to generic baselines, while more recent explainable lexicon work argues that transformer-aided lexicons can recover some of the interpretability and speed advantages of rules. Aspect-based sentiment is attractive because it gives explainable sentiment at the level of themes such as policy, demand, or financing conditions, rather than collapsing all tone into one label. That is especially useful for Chinese sector rotation, where a headline may be positive for one sector and neutral or negative for another. citeturn0academia0turn0academia1turn30academia0turn41academia3

Chinese event extraction research is directly relevant. Title2Event was built specifically for Chinese news titles and documents that title-form extraction is still challenging even with a sizeable, manually annotated dataset; that matters because the shared task provides daily hot news rather than long corporate documents. Doc2EDAG, by contrast, shows how Chinese financial events can be represented with structured arguments at document level, including a no-trigger-word formulation that can simplify labelling. Text2Event adds a sequence-to-structure paradigm for end-to-end event extraction, but it is heavier than is justified for a first build in this competition setting. The practical implication is to use **Title2Event-inspired schema design and rule templates first**, while treating Doc2EDAG and Text2Event as references for event slots, not as runtime dependencies. citeturn10academia0turn10academia1turn10academia2

For text-to-sector relevance, the most important discovery is not that embeddings exist, but that the literature already suggests the correct sequencing. BM25 remains a strong lexical first-stage retriever. Multistage retrieval work continues to pair lexical first stages with bi-encoders or cross-encoders for better precision, while the BGE project’s own documentation explicitly describes the reranker as more accurate but less efficient, and recommends it only as a top-k second stage. Separate retrieval work also shows a particularly relevant caution: reranker fine-tuning can help the training domain but degrade other domains. In this project, that means lexical relevance and entity-sector rules should be built first; embeddings should be added as a cached second build; rerankers should remain optional, heavily ablated, and preferably offline. citeturn23academia2turn23academia3turn40view0turn40view1turn40view2turn7academia0

The Chinese-market reaction literature strongly supports a **track split**. Policy uncertainty appears to lead the Chinese stock market, sector connectedness rises around extreme risk events, and BERT-derived Chinese investor sentiment shows stronger short-term relationships with liquidity and volatility than with a clean, stable directional return edge. Positive PMI announcements in China have also displayed asymmetric response dynamics, including multi-day persistence under favourable conditions. This body of evidence argues that Track A should use news primarily for **risk scaling and drawdown control**, while Track B should use it for **sector ranking, sector tilt, and avoidance of weak sectors under negative policy or demand shocks**. citeturn29academia9turn29academia8turn17academia2turn29academia4

Finally, the overlay literature separates what is promotion-plausible from what is not. Black-Litterman is still one of the clearest frameworks for turning sparse qualitative views into bounded posterior expected returns and constrained active tilts. Exponentiated-gradient and mirror-descent methods are attractive for multiplicative overlay updates under simplex constraints, but their sensitivity to learning rates and compounding behaviour makes them better build-later options than first-line promotion candidates. Attention-based pooling and graph propagation remain useful research comparators, but the available task data and the need for deterministic fallback both materially reduce their first-build appeal. citeturn43search0turn43search3turn19academia1turn35academia0turn35academia3turn20academia0turn20academia3turn34academia0turn34academia3

## Method Shortlist Overview

The shortlisted methods below were selected because they can all emit an explicit daily signal, can all be trained or tuned on 2024 only, and can all be disabled cleanly for null ablations.

| Method | Core framework | Primary fit | Output signal | Build sequence |
|---|---|---|---|---|
| Event-Study Calibrated News Impact Overlay | Classical short-window event studies + gated tilt | Track B first, Track A second | Signed event-response score per asset/sector | build_first |
| Permutation-Tested News Attention Index | Structured additive news score + permutation filtering | Both tracks | Stable, transparent intermediate NAI signal | build_first |
| Rank-IC Gated Sector News Momentum | Cross-sectional ranking using lagged NAI | Track B | Sector ranking adjustment score | build_first |
| Sparse Event-Sensitivity Regression Overlay | Elastic-net or adaptive-lasso event response model | Both tracks | Sparse predicted response score | build_second |
| Volatility-Scaled Macro News Risk Gate | Macro news mapped to risk multiplier | Track A | Risk-on/risk-off multiplier | build_first |
| Black-Litterman News View Overlay | Bayesian portfolio views | Both tracks | Posterior return views and bounded active tilt | build_second |
| Transformer-Cached Text-to-Sector Relevance plus Rule Impact Gate | Offline embeddings or reranker + deterministic event layer | Track B | Relevance/confidence score | build_second |
| Confidence-Weighted Exponentiated-Gradient Overlay | Multiplicative active overlay | Track B first | Active weight update around base | build_later |
| Hierarchical Daily News Attention Pooling | HAN-style or label-attention pooling | Research comparator | Learned daily sector-aware news vector | ablation_only |

## Specific Methods

### Event-Study Calibrated News Impact Overlay

#### Core Idea

This method converts daily news into **event-class-specific expected asset reactions** by calibrating short response curves from 2024 data only. It does not ask a model to “understand the market” end to end. Instead, it measures how specific event classes historically moved a sector ETF or macro sleeve over short horizons, then uses that measured response as a bounded overlay on top of preserved base weights.

#### Literature and Framework Basis

The framework is rooted in classical event studies: estimate a normal return model, compute abnormal returns around an event, aggregate into cumulative abnormal returns, then use the observed response profile as a calibration target. That logic is still directly usable here. The main caution comes from newer work showing that long or volatile-period event studies are vulnerable to model misspecification, which is why this method should confine itself to short windows such as one, three, and five trading days. For Chinese text structure, Title2Event is the closest public benchmark to the task’s hot-news-title regime, while Doc2EDAG is informative for event-slot design but heavier than necessary for a first build. citeturn28news0turn39search0turn39search1turn25academia5turn10academia0turn10academia1

#### Inputs

The required inputs are daily news items available before the official cutoff; deterministic event labels and directions; relevance from lexical or semantic mapping; preserved base allocator weights; and historical ETF or index returns for the sectors or macro sleeves being evaluated.

#### Algorithm

1. Extract all news items available before the decision cutoff on day \(t\).
2. Map each item to an event class \(c_i\), direction \(d_i \in \{-1,0,1\}\), impact score \(I_i\), and asset relevance \(R_{i,j}\).
3. For each asset or sector \(j\), estimate a normal-return model on 2024 training data.
4. For each historical event class \(c\), compute short-horizon abnormal-return response curves for asset \(j\).
5. Collapse those curves into a calibrated sensitivity statistic for each \((j,c)\) pair.
6. On live replay, combine current event signals with the calibrated sensitivity and convert the result into a clipped additive tilt \(\Delta w_{t,j}\).
7. Apply turnover, drawdown, and max-tilt gates; otherwise fall back to the base allocator unchanged.

#### Mathematical Formulation

A simple version is:

\[
\widehat r^{\text{exp}}_{j,t}=\widehat \alpha_j+\widehat \beta_j r^{\text{mkt}}_t
\]

\[
AR_{e,j,\tau}=r_{j,t_e+\tau}-\widehat r^{\text{exp}}_{j,t_e+\tau}
\]

\[
CAR_{j,c}(L,U)=\operatorname{median}_{e\in c}\sum_{\tau=L}^{U} AR_{e,j,\tau}
\]

\[
S_{t,j}=\sum_{i\in \mathcal N_t} I_i \cdot d_i \cdot R_{i,j} \cdot \text{Conf}_{i,j}\cdot \text{Sens}_{j,c_i} \cdot e^{-\lambda \Delta t_i}
\]

\[
\Delta w_{t,j}=\operatorname{clip}(\kappa S_{t,j},-m_j,m_j)
\]

where \(\text{Sens}_{j,c}\) is derived from the 2024 event-study response curve, \(\kappa\) is overlay strength, and \(m_j\) is the sector or sleeve tilt cap. This is conceptually identical to using event-time abnormal responses as the calibration layer for a live overlay. citeturn28news0turn39search0turn25academia5

#### Track A Use Case

For Track A, this method should be narrow. It is not well suited to daily directional macro timing. Its best use is to calibrate the response of broad sleeves—equity, defensive bonds, or cash-like allocations—to major monetary, fiscal, liquidity, property, and shock events.

#### Track B Use Case

For Track B, this is one of the strongest methods in the entire shortlist. It can directly measure whether, for example, chip-policy news, healthcare regulation, or export-tariff news consistently produces positive or negative short-horizon abnormal performance in related sectors.

#### 2024 Training and Tuning Protocol

The full event taxonomy, normal-return benchmark choice, event windows, decay parameter, overlay strength, and tilt caps should be tuned on 2024 only. Selection should rely on walk-forward 2024 validation, not pooled hindsight. Sparse event classes should be merged or zeroed rather than forced into unstable estimates.

#### 2025 Test Protocol

Freeze the entire response table, gates, and overlay strength at the end of 2024. Replay 2025 public-A once under official semantics. No event-class additions, no coefficient updates, and no threshold retuning should occur during 2025.

#### Required Ablations

In addition to the global suite, this method specifically needs benchmark-model ablations—market model versus constant-mean versus base-relative excess return—plus event-window ablations, class-merging ablations, and decay-on versus decay-off comparisons.

#### Implementation Complexity

Medium. The method requires disciplined event taxonomies and response tables, but it does not require online model inference or large neural training.

#### Risks and Failure Modes

The main risks are sparse class counts, unstable responses for rarely observed events, and false confidence from noisy CAR estimates. A second risk is accidental duplication: if multiple headlines describe the same policy act, the overlay can overcount the event unless clustering is done first.

#### Verdict

**Build first.** This is the best first-build method because it is interpretable, leakage-auditable, well matched to 2024-only calibration, and naturally compatible with preserved base allocators.

### Permutation-Tested News Attention Index

#### Core Idea

This method builds a transparent **intermediate signal** rather than a portfolio rule. It aggregates impact, relevance, direction, confidence, and historical sensitivity into a daily per-asset or per-sector index, then uses permutation tests and shuffle nulls to zero out pairings that look predictive only because of regime coincidence or overfitting.

#### Literature and Framework Basis

The strongest motivation for this method comes from two places. First, finance-text event work often finds weak unconditional correlations but more informative behaviour around **attention peaks** and clustered events. Second, explainable finance work increasingly favours structured intermediate variables—aspect sentiment, event classes, named themes—over raw black-box predictions. That combination makes a permutation-filtered attention index a pragmatic bridge between rules and overlays. The general logic also fits Chinese-market asymmetry evidence, where responses vary by regime and event type rather than behaving like a stable universal sentiment factor. citeturn38academia2turn30academia0turn17academia2turn29academia4turn29academia9

#### Inputs

The required inputs are impact-scored news items, direction tags, relevance scores, confidence scores, and a sensitivity table estimated from 2024 only.

#### Algorithm

1. For each day \(t\) and asset \(j\), aggregate all available news into a raw index score.
2. Estimate a validation statistic on 2024 for each event-class and asset pair, such as mean short-horizon CAR, hit rate, or rank IC.
3. Generate null distributions by shuffling news dates, randomising labels, or permuting asset mappings inside 2024.
4. Retain only event-class/asset combinations that pass a significance or stability threshold.
5. Use the filtered index as a ranking signal, risk gate, or overlay input.
6. If the filtered index is missing or unstable, fall back to zero-news behaviour.

#### Mathematical Formulation

A transparent form is:

\[
NAI_{t,j}=\sum_{i\in \mathcal N_t} I_i \cdot R_{i,j}\cdot D_{i,j}\cdot C_{i,j}\cdot \text{Sens}_{j,c_i}
\]

Let \(T_{j,c}\) denote the chosen validation statistic, for example average \(CAR_{j,c}(1,3)\) or rolling rank IC. Then use a permutation p-value

\[
p_{j,c}=\frac{1+\sum_{b=1}^{B}\mathbf 1\{|T^{(b)}_{j,c}|\ge |T_{j,c}|\}}{B+1}
\]

and set

\[
\widetilde{NAI}_{t,j}=NAI_{t,j}\cdot \mathbf 1\{p_{j,c_i}\le \alpha \ \text{and sign stability passes}\}.
\]

This keeps the index interpretable and null-testable. citeturn38academia2turn30academia0

#### Track A Use Case

For Track A, the best use is to aggregate only macro and broad-risk categories into a compact daily macro attention index that feeds a risk multiplier rather than a directional allocator.

#### Track B Use Case

For Track B, this method is highly attractive because it emits a clean, sector-level transparent signal that can be turned into ranking adjustments, top-k inclusion or exclusion, or bounded sector tilts.

#### 2024 Training and Tuning Protocol

Tune impact-weighting rules, permutation count, significance thresholds, class-merging rules, and sensitivity normalisation on 2024 only. Stability should be judged across multiple 2024 folds, not merely full-year pooled performance.

#### 2025 Test Protocol

Freeze the retained event-class/asset map and all thresholds at 2024 year-end. Compute the index on 2025 using only the frozen components.

#### Required Ablations

In addition to the global suite, this method specifically needs permutation-count sensitivity, class-retention threshold sweeps, and raw NAI versus permutation-filtered NAI comparisons.

#### Implementation Complexity

Low to medium. The arithmetic is straightforward, but the validation layer must be carefully engineered.

#### Risks and Failure Modes

The largest risk is false security from weak permutation design. If shuffles do not preserve the relevant seasonality or sector structure, the null can be too weak. There is also a risk that strict filtering removes too much signal and leaves the index inert.

#### Verdict

**Build first.** This is the best platform signal in the shortlist, even if it is not the single best first overlay method. It should be treated as the canonical intermediate variable for later methods.

### Rank-IC Gated Sector News Momentum

#### Core Idea

This method turns the news-attention signal into an explicitly **cross-sectional sector-ranking framework**. Rather than predicting levels, it asks a narrower question: does the sector news signal rank the next one to five trading days better than chance, and only in the regimes where that rank information survives validation?

#### Literature and Framework Basis

Rank IC is widely used in cross-sectional finance because it measures whether predicted scores align with realised return ordering rather than with noisy levels. Recent work that directly optimises rank IC reflects how central the statistic remains for asset ranking tasks. The Chinese sector literature, which documents dynamic connectedness and risk transmission between sectors, supports the idea that cross-sectional sector effects are more plausible than stable index-level directionality. citeturn26academia0turn29academia8

#### Inputs

The required inputs are the filtered news-attention index, lagged versions of that index, sector returns, and rolling validation statistics for rank IC.

#### Algorithm

1. Compute a daily sector signal from the filtered NAI.
2. Form lagged combinations, for example same day after cutoff, one-day lag, and three-day lag.
3. Estimate 2024 rolling rank IC by horizon for the candidate lag combinations.
4. Keep only lag structures whose sign and rank IC remain stable in 2024 folds.
5. On each replay day, apply the ranking model only if the impact and confidence gates and the ex ante rank-IC gate are all satisfied.
6. Convert the sector ranking into a bounded perturbation of the base sector weights.

#### Mathematical Formulation

Let

\[
M_{t,j}=\sum_{\ell \in \{0,1,3\}} \omega_\ell \widetilde{NAI}_{t-\ell,j}
\]

and define the rank information coefficient at horizon \(h\) as

\[
RankIC_h=\rho_{\text{Spearman}}(M_{t,\cdot}, r_{t+h,\cdot}).
\]

Then the active signal can be written as

\[
S_{t,j}=M_{t,j}\cdot \mathbf 1\{ \widehat{RankIC}_{h^\star,t-1} > \theta_{IC}\}\cdot \mathbf 1\{ \text{Impact}_{t,j}>\theta_I\}\cdot \mathbf 1\{\text{Conf}_{t,j}>\theta_C\}.
\]

The final overlay is applied as a rank-based adjustment, not as a free-form optimiser output. citeturn26academia0

#### Track A Use Case

This method is not a natural Track A choice, except perhaps for coarse ranking among a very small number of macro sleeves. Its real home is Track B.

#### Track B Use Case

This is the strongest **deployment method** for Track B because the actual task is cross-sectional sector allocation. It can sit naturally on top of the preserved LEEQA-style base and directly answer whether news improves sector ordering.

#### 2024 Training and Tuning Protocol

Tune horizon choice, lag weights, minimum rolling rank-IC threshold, and top-k perturbation strength on 2024 only. The target metric should be rank stability first, portfolio PnL second.

#### 2025 Test Protocol

Freeze all lag weights, rank-IC thresholds, and ranking-to-weight rules at the end of 2024. Replay 2025 with no reselection of horizons or top-k.

#### Required Ablations

Beyond the global suite, this method needs lag-set ablations, same-day-only versus lagged-only comparisons, rank-IC gate on/off tests, and equal-weight versus rank-proportional perturbation tests.

#### Implementation Complexity

Low to medium. It is simpler than a full supervised return model and fits the sector task naturally.

#### Risks and Failure Modes

The signal can decay quickly under regime change. It can also become too concentrated if top-k rules are overly aggressive, creating turnover and drawdown problems after short-lived news bursts.

#### Verdict

**Build first for Track B.** This is the best Track B-specific deployment method, provided it is built on top of a transparent attention or event-response signal rather than raw sentiment.

### Sparse Event-Sensitivity Regression Overlay

#### Core Idea

This method estimates a sparse predictive map from event features to future ETF or sector returns. It is a supervised counterpart to the event-study method: instead of hand-aggregating event responses, it learns a sparse coefficient vector over event-class, direction, intensity, lag, and regime features.

#### Literature and Framework Basis

Elastic-net and lasso methods remain standard ways to handle sparse, correlated predictors, and adaptive-lasso Granger-style procedures have already been used in high-dimensional sentiment and industry forecasting problems. The rationale is directly relevant here because daily event features are sparse, correlated, and likely to exhibit unstable marginal effects unless regularised. Aspect-based sentiment work is also relevant because it suggests that richer, interpretable feature families—policy tone, demand tone, financing tone—can be statistically more informative than one coarse sentiment score. citeturn38academia1turn37academia8turn37search0turn37search1turn30academia0

#### Inputs

The inputs are daily event feature vectors, optionally including class counts, class intensity sums, positive and negative direction splits, lagged features, regime flags, and sector-specific relevance aggregates.

#### Algorithm

1. Construct a feature vector \(x_{t,j}\) for each date \(t\) and asset or sector \(j\).
2. Choose a target horizon such as next-day, next-three-day, or next-five-day excess return.
3. Estimate a regularised regression using 2024 data only.
4. Retain only coefficients that are stable across 2024 folds and economically sensible in sign.
5. Use the fitted value as a sparse response score.
6. Apply the score only when magnitude, confidence, and turnover gates are satisfied.

#### Mathematical Formulation

A basic elastic-net specification is

\[
\widehat \beta = \arg\min_{\beta}\sum_t \left(y_{t+h,j}-x_{t,j}^{\top}\beta\right)^2+\lambda_1 \|\beta\|_1+\lambda_2 \|\beta\|_2^2.
\]

The live signal is then

\[
S_{t,j}=x_{t,j}^{\top}\widehat \beta.
\]

A stronger variant first screens predictors through adaptive-lasso or bootstrap Granger selection and only then estimates the final sparse regression. citeturn38academia1turn37academia8

#### Track A Use Case

For Track A, the feature set should be very small and macro-only: policy easing, property stress, crisis/shock events, liquidity events, and broad-risk sentiment. Anything more granular is likely to overfit.

#### Track B Use Case

For Track B, this method can work either as a pooled sector model with sector interactions or as separate per-sector regressions. It is especially useful when one wants data-driven sensitivity estimates rather than event-study response tables.

#### 2024 Training and Tuning Protocol

Tune the regularisation path, feature family, lag family, and regime interaction terms on 2024 only. Stability selection should matter more than raw in-sample fit.

#### 2025 Test Protocol

Freeze the feature set and coefficients after the 2024 tuning sweep. Run 2025 as a fixed model, without coefficient refresh or threshold revisions.

#### Required Ablations

This method specifically needs lasso versus elastic-net comparisons, pooled versus separate sector models, lag-family removal, and sparse-feature-family removal. It should also be tested with and without adaptive-lasso pre-screening.

#### Implementation Complexity

Medium to high. The method is still reproducible and deterministic at inference, but it requires careful feature engineering and regularisation discipline.

#### Risks and Failure Modes

The main risks are unstable signs, multicollinearity, and the temptation to over-expand the feature set. If too many event classes are included, the model may remain sparse on paper but effectively tuned to 2024 noise.

#### Verdict

**Build second.** This is one of the strongest follow-up methods after the event-study and NAI layers exist, but it is not the cleanest first build.

### Volatility-Scaled Macro News Risk Gate

#### Core Idea

This method uses macro and broad-risk news not to forecast returns directly, but to forecast **near-term portfolio risk**. It gates the gross risk of a preserved macro base allocator by mapping major policy, liquidity, crisis, or property shocks into a bounded volatility or downside-risk multiplier.

#### Literature and Framework Basis

This is the best supported Track A-specific idea in the literature map. Chinese work using BERT-based sentiment and TVP-VAR methods found particularly strong short-run links between sentiment, liquidity, and volatility. Separate Chinese studies show that economic policy uncertainty leads the stock market, and PMI announcements generate asymmetric market reactions. Those findings make a risk gate much more defensible than a daily directional macro forecaster. citeturn17academia2turn29academia9turn29academia4

#### Inputs

The method needs macro-tagged and broad-risk-tagged news items, a macro impact score, a broadness score, plus realised volatility, downside semivariance, or drawdown proxies for the risky sleeves in Track A.

#### Algorithm

1. Restrict the news universe to macro and broad-risk classes.
2. Aggregate those news items into one or more stress scores, such as easing, tightening, crisis, or liquidity-stress scores.
3. Estimate on 2024 whether those scores predict future realised volatility, downside semivariance, or drawdown risk.
4. Map the predicted risk into a bounded gross-risk multiplier.
5. Multiply risky sleeves by that multiplier and renormalise the preserved base.
6. If the gate is not triggered, keep the preserved macro allocator unchanged.

#### Mathematical Formulation

A simple two-sided version is:

\[
Stress_t=\sum_{i\in \mathcal M_t} I_i\cdot D_i^{-}\cdot C_i,\qquad
Ease_t=\sum_{i\in \mathcal M_t} I_i\cdot D_i^{+}\cdot C_i
\]

\[
\widehat{Risk}_{t+h}=a+b^- Stress_t+b^+ Ease_t
\]

\[
g_t=\operatorname{clip}\left(1-\gamma^- \widehat{Stress}_t+\gamma^+ \widehat{Ease}_t,\ g_{\min}, g_{\max}\right).
\]

Then risky-sleeve weights become \(g_t w^{\text{base}}_{t,\text{risky}}\), with the residual assigned to safer sleeves or cash-like exposure. citeturn17academia2turn29academia9

#### Track A Use Case

This is the best standalone Track A method in the shortlist. It respects the fact that the current winning Track A baseline is a no-news risk-parity system and uses news only where it is most justifiable: risk scaling and drawdown control.

#### Track B Use Case

For Track B, the method can still be useful as a top-level risk throttle, especially in broad market stress events, but it should not replace sector ranking logic.

#### 2024 Training and Tuning Protocol

Tune the macro taxonomy, easing versus stress decomposition, forecast horizon, clipping bounds, and throttle strength on 2024 only. Stress and easing should be calibrated separately because the literature suggests asymmetry.

#### 2025 Test Protocol

Freeze the risk-mapping coefficients and all gates at end-2024. Replay 2025 with no updates.

#### Required Ablations

The method specifically needs volatility-target versus drawdown-target comparisons, stress-only versus two-sided gates, asymmetric versus symmetric mapping, and one-day versus three-day risk-horizon ablations.

#### Implementation Complexity

Low. This is one of the easiest methods to implement and audit once the macro taxonomy exists.

#### Risks and Failure Modes

The main risk is over-throttling: if supportive policy headlines trigger de-risking instead of sensible re-risking, the method will create opportunity cost. It can also be late if macro events are only partially reflected in daily hot-news lists.

#### Verdict

**Build first for Track A.** This is the best Track A method because it complements the preserved risk-parity winner rather than trying to replace it.

### Black-Litterman News View Overlay

#### Core Idea

This method turns news signals into sparse **portfolio views** with explicit uncertainty and then folds them into a constrained Black-Litterman posterior. It is a disciplined way to convert macro or sector news into return tilts without letting the news engine directly dictate portfolio weights.

#### Literature and Framework Basis

Black-Litterman is attractive here because it was designed to combine a stable prior with subjective views and confidence, precisely the problem faced by a news overlay on top of a preserved base allocator. The Bayesian interpretation literature strengthens that fit, particularly when views arrive with varying confidence levels. However, Black-Litterman is not a first build here because it adds another layer of covariance and view-uncertainty modelling, which raises complexity without solving the front-end event extraction problem. citeturn43search0turn43search3turn19academia1

#### Inputs

The inputs are prior expected returns implied by the base allocator, an asset covariance matrix, a pick matrix selecting the assets or relative views affected by a news event, and a view vector derived from the news signal, together with a confidence matrix.

#### Algorithm

1. Take the preserved base weights as the prior allocation anchor.
2. Convert event or NAI signals into sparse views \(q_t\), such as “sector A should outperform sector B”.
3. Build a pick matrix \(P_t\) describing which assets each view affects.
4. Map confidence and sensitivity into view uncertainty \(\Omega_t\).
5. Compute the posterior Black-Litterman expected return vector.
6. Feed the posterior into a constrained mean-variance or active-risk solver with strict tilt and turnover caps.

#### Mathematical Formulation

A standard posterior is

\[
\mu_t = \left[(\tau \Sigma)^{-1}+P_t^\top \Omega_t^{-1}P_t\right]^{-1}
\left[(\tau \Sigma)^{-1}\pi_t+P_t^\top \Omega_t^{-1}q_t\right].
\]

The active overlay is then obtained from a constrained optimiser around the base allocation, not from unconstrained mean-variance optimisation. Confidence enters through \(\Omega_t\), which should widen when news relevance, event confidence, or historical sensitivity is weak. citeturn43search0turn43search3

#### Track A Use Case

Track A is where this method is most defensible: a small number of broad relative views—equity versus bonds, cyclical versus defensive, property-sensitive versus safe—can be expressed cleanly.

#### Track B Use Case

Track B can also use this method for sparse relative sector views, but the benefit over a simpler ranking overlay is less obvious unless relative-value structure matters.

#### 2024 Training and Tuning Protocol

Tune \(\tau\), confidence mapping, covariance shrinkage choice, and active-risk cap on 2024 only. View families should be intentionally sparse.

#### 2025 Test Protocol

Freeze the view-construction mapping and uncertainty scaling at 2024 year-end. No view family or covariance-regularisation changes in 2025.

#### Required Ablations

Key ablations are prior-only versus posterior, diagonal versus structured \(\Omega_t\), absolute versus relative views, and Black-Litterman posterior versus simpler additive tilts.

#### Implementation Complexity

Medium. The formulas are standard, but the confidence layer and covariance handling require care.

#### Risks and Failure Modes

This method can become cosmetically elegant but practically fragile if the prior, confidence map, and covariance model are all estimated imperfectly. It is also easy to make the uncertainty matrix appear principled when it is actually just another tuned hyperparameter layer.

#### Verdict

**Build second.** This is a plausible promotion candidate only after the front-end event and relevance signals are already proven robust.

### Transformer-Cached Text-to-Sector Relevance plus Rule Impact Gate

#### Core Idea

This method confines transformer use to the **text-to-sector relevance problem** and keeps direction, impact, and gating tied to deterministic rules. The core proposal is to precompute or cache semantic relevance scores between Chinese news and sector definitions, sector prototypes, or ETF-theme descriptions, then combine those scores with rule-based event extraction.

#### Literature and Framework Basis

The BGE family is particularly relevant because its official documentation positions the models explicitly for retrieval, clustering, and semantic search, distinguishes embeddings from rerankers, notes that the reranker is more accurate but less efficient, and recommends reranking only after a cheaper first-stage retrieval. The BGE M3 paper further shows the family’s retrieval versatility. At the same time, retrieval results from other domains show a warning that is highly relevant here: reranker fine-tuning can slightly improve the training domain and worsen other domains. Combined with Chinese financial benchmarks showing that domain tasks remain challenging even for strong models, the correct conclusion is that transformer relevance can be **adaptable and useful**, but only as an offline, second-build, ablated feature layer. citeturn40view0turn40view1turn40view2turn7academia0turn23academia2turn23academia3turn6academia0turn6academia2

#### Inputs

The method needs sector prototype texts, ETF theme descriptions, canonical keyword glosses, news titles or snippets, and a pinned offline Chinese embedding model. Optional inputs include a reranker for top-k candidate sectors.

#### Algorithm

1. Construct sector prototype texts and entity glossaries before 2026.
2. Encode the news texts and the sector prototypes offline with a pinned Chinese embedding model.
3. Compute coarse relevance by cosine similarity, nearest-centroid assignment, or top-k prototype retrieval.
4. Optionally rerank only the coarse top-k candidates with a cached or pre-approved cross-encoder.
5. Combine the semantic relevance score with deterministic direction, impact, and confidence gates.
6. If semantic relevance is unavailable or unstable, fall back to BM25 and entity-sector lexicons.

#### Mathematical Formulation

A practical version is

\[
Rel^{\text{dense}}_{i,j}=\cos(e_i, c_j)
\]

where \(e_i\) is the news embedding and \(c_j\) is the sector centroid or prototype embedding. If a reranker is available, replace or blend the score with a second-stage cross-encoder score:

\[
Rel_{i,j}=\alpha \, Rel^{\text{lex}}_{i,j} + (1-\alpha)\, Rel^{\text{dense}}_{i,j},
\]

or use the reranker only for the top-k candidates returned by lexical or dense retrieval. This is squarely in line with the documented embedding-plus-reranker retrieval pipeline. citeturn40view1turn40view2turn23academia2

#### Track A Use Case

Track A can use this only lightly—for mapping macro-policy headlines to a small set of sleeves or themes. The dimensional benefit is limited.

#### Track B Use Case

Track B is the natural target. This method can materially improve relevance mapping for ambiguous or metaphorical news headlines, which is often the weakest part of deterministic sector overlays.

#### 2024 Training and Tuning Protocol

Tune only the relevance-combination rule, similarity thresholds, top-k depth, and lexical-versus-dense blending on 2024. Any manual prototype text set must be frozen before 2025 testing.

#### 2025 Test Protocol

Freeze the chosen model, cache scheme, similarity thresholds, and fallbacks at the end of 2024. Re-encode 2025 with the same pinned artefacts only.

#### Required Ablations

This method specifically needs lexical-only versus dense-only versus hybrid relevance comparisons, reranker on/off, duplicate-cluster on/off, and prototype-set ablations. It also needs a strict deterministic fallback ablation.

#### Implementation Complexity

Medium. It is still manageable if the encoder is cached offline, but significantly more complex than pure lexical relevance.

#### Risks and Failure Modes

The largest risks are hidden dependency creep, semantic threshold instability, and accidental domain overfitting in reranker fine-tuning. A second risk is operational: if model assets are not pinned and cached reproducibly, the method is disqualified in spirit even if not in code.

#### Verdict

**Build second.** This is the best transformer-related method, but only after a lexical, event-study, and NAI baseline is already functioning.

### Confidence-Weighted Exponentiated-Gradient Overlay

#### Core Idea

This method applies multiplicative, simplex-preserving active tilts around the base portfolio. It is a portfolio-overlay method, not a news-extraction method: once a signed news score exists, the overlay updates active weights via exponentiated gradients while scaling the magnitude by confidence and turnover budgets.

#### Literature and Framework Basis

Exponentiated-gradient and mirror-descent approaches are well established in online portfolio selection, and recent work continues to develop their regret properties and transaction-cost behaviour. That makes them a credible overlay candidate. Their weakness in this project is not theoretical legitimacy; it is **practical interpretability**. Compared with clipped additive tilts or Black-Litterman views, multiplicative updates are harder to explain when many small sector signals accumulate over time. citeturn35academia0turn35academia2turn35academia3

#### Inputs

The method needs base weights, a signed news score for each asset or sector, a confidence score, and a turnover budget.

#### Algorithm

1. Start from preserved base weights.
2. Compute a confidence-scaled news score for each asset.
3. Apply an exponentiated-gradient update around the base.
4. Blend the active portfolio with the base using a confidence-dependent mixing weight.
5. Clip the resulting active deviation under max-tilt and turnover caps.
6. If news confidence is low, set the mixing weight to zero.

#### Mathematical Formulation

A constrained version is

\[
u_{t,j}=w^{\text{base}}_{t,j}\exp(\eta \, c_{t,j}\, s_{t,j}),
\qquad
\widetilde w_{t,j}=\frac{u_{t,j}}{\sum_k u_{t,k}}
\]

\[
w_{t}=(1-\rho_t)w^{\text{base}}_{t}+\rho_t \widetilde w_t
\]

with \(\eta\) the learning rate and \(\rho_t\) a bounded confidence-driven blend weight. The attraction is simplex preservation; the risk is cumulative sensitivity to noisy \(s_{t,j}\). citeturn35academia0turn35academia3

#### Track A Use Case

It is usable for Track A only in very low dimension, where the number of broad sleeves is tiny and the learning-rate problem is easier to interpret.

#### Track B Use Case

Track B is the better fit because multiplicative overlays map naturally onto sector allocations. Even so, the method is better as a later overlay experiment than as a first-line production candidate.

#### 2024 Training and Tuning Protocol

Tune learning rate, blend weight, tilt cap, and decay in 2024 only. The search grid should be intentionally small.

#### 2025 Test Protocol

Freeze the update rule and all hyperparameters after 2024. No online adaptation in 2025.

#### Required Ablations

The main additional ablations are additive tilt versus multiplicative tilt, learning-rate sweeps, blend-weight sweeps, and persistence versus no-persistence variants.

#### Implementation Complexity

Medium. The formulas are simple, but real robustness depends heavily on good gating.

#### Risks and Failure Modes

The method can amplify strings of small false positives, especially when sector scores are mildly noisy but persistent. It is also less intuitive than additive tilts for post-hoc audit.

#### Verdict

**Build later.** This is a credible overlay family, but it is not the clearest first or second build.

### Hierarchical Daily News Attention Pooling

#### Core Idea

This method uses a small hierarchical attention architecture to pool words into news-level vectors and news items into a daily sector-aware representation. It is not proposed as a final allocator. It is proposed only as a research comparator to test whether learned pooling adds anything beyond deterministic aggregation or simple dense relevance.

#### Literature and Framework Basis

Hierarchical attention networks and label-based attention models remain strong, interpretable architectures for document and hierarchical multi-label classification, and label-attention work explicitly shows that attention can align text evidence to labels in explainable ways. Those are appealing properties. The problem is sample size and task mismatch. The shared task offers only one year of tuning data and daily Top-20 news, while Chinese financial benchmarks still show that the underlying domain is challenging even for much larger models. In that context, a learned attention pooler is informative as an ablation, but too risky as an early production candidate. citeturn20academia0turn20academia3turn6academia0turn6academia2

#### Inputs

The method needs tokenised news text, sector labels or sector query embeddings, and daily grouped news sets.

#### Algorithm

1. Encode each news item at token level.
2. Apply word-level attention to obtain a news-item vector.
3. Apply news-level attention across the daily set.
4. Optionally condition the second attention layer on the target sector query.
5. Emit a daily sector-aware relevance or sentiment score.
6. Compare it against deterministic NAI and lexical/dense relevance baselines.

#### Mathematical Formulation

A sector-conditioned variant is

\[
\alpha_{i,j}=\operatorname{softmax}\left(\frac{q_j^\top K_i}{\sqrt d}\right),\qquad
s_{t,j}=\sum_{i\in \mathcal N_t}\alpha_{i,j}V_i
\]

where \(q_j\) is a sector query and \(K_i,V_i\) are keys and values derived from news-item encodings. This is standard query-key-value attention applied to daily news aggregation rather than to sequence generation. citeturn32search5turn20academia3

#### Track A Use Case

Track A can use this only as a compressed macro-news representation for ablation. It is not the right Track A production path.

#### Track B Use Case

Track B is the only plausible deployment target, but even there it should remain research-only until it proves clear incremental value over deterministic aggregation.

#### 2024 Training and Tuning Protocol

If tested at all, training should be tiny, fixed, and 2024-only. The encoder should ideally be frozen or lightly adapted to minimise hidden capacity.

#### 2025 Test Protocol

Freeze the architecture and weights at the end of 2024 and run a single 2025 replay. No architecture search in 2025.

#### Required Ablations

This method requires transformer-free attention versus HAN-style attention, query-conditioned versus unconditioned attention, frozen versus lightly tuned encoders, and direct comparisons against deterministic NAI and lexical/dense relevance.

#### Implementation Complexity

High relative to expected first-build value.

#### Risks and Failure Modes

The biggest risk is that the model learns a compact but unstable proxy for 2024 regimes rather than a true sector-news relevance function. A second risk is explainability theatre: attention visualisations can look interpretable without guaranteeing stable trading value.

#### Verdict

**Ablation only.** Useful as a research comparator, not as a promotion target.

## Comparative Assessment and Recommendations

### Comparative Method Table

All scores below use a 1–5 scale. For desirability dimensions, **5 is best**. For cost and risk dimensions, **5 is worst**. Overall Score is a 0–100 rescaling of the user-specified desirability-minus-risk formula; runtime simplicity is computed internally as \(6 - \text{Implementation Cost}\), and an internal overfitting-risk penalty is applied in the overall score even though it is not shown as a separate table column.

| Rank | Method | Core Framework | Track A Fit | Track B Fit | Expected Value | Robustness | Interpretability | Implementation Cost | Dependency Risk | Leakage Risk | Ablation Quality | Official Compatibility | Overall Score | Decision |
|---:|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 1 | Event-Study Calibrated News Impact Overlay | Short-window event study + bounded tilt | 3.5 | 5.0 | 4.7 | 4.5 | 4.8 | 3.0 | 1.0 | 2.0 | 5.0 | 4.8 | 81.8 | build_first |
| 2 | Permutation-Tested News Attention Index | Transparent additive signal + null filtering | 3.4 | 4.8 | 4.6 | 4.4 | 4.7 | 2.8 | 1.0 | 1.8 | 5.0 | 4.8 | 81.4 | build_first |
| 3 | Volatility-Scaled Macro News Risk Gate | Macro-news risk multiplier | 5.0 | 3.5 | 3.9 | 4.7 | 4.6 | 2.0 | 1.0 | 1.5 | 5.0 | 5.0 | 81.0 | build_first |
| 4 | Rank-IC Gated Sector News Momentum | Cross-sectional sector ranking | 2.0 | 5.0 | 4.5 | 4.2 | 4.5 | 2.2 | 1.0 | 2.0 | 4.8 | 4.9 | 77.8 | build_first |
| 5 | Sparse Event-Sensitivity Regression Overlay | Elastic-net or adaptive-lasso event model | 3.0 | 4.7 | 4.2 | 4.1 | 4.3 | 3.2 | 1.0 | 2.2 | 4.9 | 4.7 | 74.2 | build_second |
| 6 | Black-Litterman News View Overlay | Bayesian prior-plus-views overlay | 4.0 | 4.0 | 3.8 | 3.9 | 4.0 | 3.2 | 1.0 | 2.0 | 4.5 | 4.1 | 70.7 | build_second |
| 7 | Confidence-Weighted Exponentiated-Gradient Overlay | Multiplicative active overlay | 3.6 | 3.8 | 3.5 | 3.8 | 3.4 | 2.7 | 1.0 | 2.0 | 4.4 | 4.4 | 67.2 | build_later |
| 8 | Transformer-Cached Text-to-Sector Relevance plus Rule Impact Gate | Offline embeddings or reranker + deterministic event gate | 2.8 | 4.5 | 4.1 | 3.7 | 3.8 | 3.6 | 2.5 | 2.5 | 4.3 | 3.9 | 64.4 | build_second |
| 9 | Entity-Sector Graph Propagation News Score | Entity-sector graph diffusion | 2.4 | 4.2 | 3.6 | 3.1 | 3.0 | 4.1 | 2.8 | 2.8 | 3.8 | 3.4 | 53.0 | defer |
| 10 | Hierarchical Daily News Attention Pooling | Learned hierarchical attention | 2.5 | 4.0 | 3.7 | 2.9 | 2.6 | 4.3 | 3.0 | 3.0 | 3.5 | 3.0 | 48.8 | ablation_only |

### Top Recommended Methods

The top five methods, in build priority order rather than abstract novelty order, are:

1. **Event-Study Calibrated News Impact Overlay**
2. **Permutation-Tested News Attention Index**
3. **Volatility-Scaled Macro News Risk Gate**
4. **Rank-IC Gated Sector News Momentum**
5. **Sparse Event-Sensitivity Regression Overlay**

The logic behind this ordering is architectural. Method one gives the cleanest first bridge from news to a bounded overlay. Method two supplies the canonical transparent signal layer. Method three is the single best Track A adaptation path. Method four is the strongest Track B deployment wrapper. Method five is the strongest higher-capacity follow-up once the feature layer is already disciplined.

### Extended Candidate Methods

A top-ten extended list is appropriate for later prompts and ablation work:

1. Event-Study Calibrated News Impact Overlay  
2. Permutation-Tested News Attention Index  
3. Volatility-Scaled Macro News Risk Gate  
4. Rank-IC Gated Sector News Momentum  
5. Sparse Event-Sensitivity Regression Overlay  
6. Black-Litterman News View Overlay  
7. Confidence-Weighted Exponentiated-Gradient Overlay  
8. Transformer-Cached Text-to-Sector Relevance plus Rule Impact Gate  
9. Hierarchical Daily News Attention Pooling  
10. Entity-Sector Graph Propagation News Score  

The last two belong in research-comparator territory, not in the first promotion band. Hypergraph and graph-news work is intellectually interesting, and financial graph studies do capture higher-order dependence, but the resulting systems are much harder to make leakage-safe, deterministic, and audit-friendly in this shared-task setting. citeturn34academia0turn34academia3turn29academia8

### Track A Recommendation

Track A should **share the front-end news module** but not share the same downstream logic as Track B. The front end can share event taxonomy, duplicate clustering, macro-policy tags, relevance, and impact scoring. The downstream layer should be different: Track A should prioritise **Volatility-Scaled Macro News Risk Gate** first, with a possible later **Black-Litterman News View Overlay** for sparse broad-asset views. Track A should not start with sector-style ranking logic or heavy embedding dependence. The existing no-news risk-parity win makes a modest, risk-aware overlay much more credible than a return-chasing one. fileciteturn0file0 fileciteturn0file7 citeturn17academia2turn29academia9turn29academia4

### Track B Recommendation

Track B is the natural home for stronger news processing. The recommended stack is: **Event-Study Calibrated News Impact Overlay** for measured sector response, **Permutation-Tested NAI** as the intermediate daily signal, and **Rank-IC Gated Sector News Momentum** as the actual deployment mechanism on top of preserved sector baselines. A transformer-cached relevance module is sensible only after lexical and event-study baselines are already stable, because the main Track B weakness is relevance precision, not the absence of deep neural sequence modelling. fileciteturn0file0 fileciteturn0file7 citeturn29academia8turn40view2turn23academia3

### Recommended First Build

The recommended first build is a **four-layer stack**:

1. Rule- and title-aware event extraction inspired by Title2Event-style schema design.  
2. Event-study calibration of short-horizon sector and sleeve responses.  
3. Permutation-tested NAI as the canonical daily signal layer.  
4. A gated additive overlay for Track B and a separate macro risk gate for Track A.  

That ordering matches the prepared project workflow unusually well: the repository already anticipates separate steps for attention-index work, embedding cache work, event impact and ETF sensitivity, overlay implementation, and then frozen 2024/2025 evaluation. fileciteturn0file5 fileciteturn0file6

### Methods to Defer or Reject

The following should be deferred or rejected for promotion consideration. **Hierarchical Daily News Attention Pooling** should remain an ablation-only comparator unless it clearly outperforms deterministic baselines under frozen 2025 tests. **Entity-Sector Graph Propagation News Score** should be deferred because graph construction error, dependency footprint, and attribution complexity are too high for the first overlay phase. Full online LLM allocators, end-to-end transformer portfolio allocators, deep RL, graph RL, and unconstrained summary-to-trade systems should be rejected outright for this project phase. Chinese financial benchmarks still show large room for improvement on domain tasks, and recent finance work documents severe look-ahead problems for generic LLM backtests, which is exactly the wrong risk profile for a centrally evaluated 2026 hidden test. citeturn6academia0turn6academia2turn27academia0turn27academia2turn27academia3

## Validation, Promotion Criteria, and Open Questions

### Required Ablation Suite

The global ablation suite should be common across all top methods:

- preserved base allocator only  
- real news overlay  
- no-news variant  
- zero-news signal  
- shuffled-news dates  
- randomised event labels  
- lexical relevance versus embedding relevance  
- impact gate on and off  
- sensitivity gate on and off  
- confidence gate on and off  
- overlay strength sweep  
- turnover-cap sweep  
- Track A only  
- Track B only  
- high-volatility versus low-volatility regimes  
- event-category removal  

The single most important ablation is **shuffled-news dates while preserving the actual price path, official trade semantics, and turnover controls**. That test most directly answers whether the method is exploiting time-aligned information rather than generic market regimes or accidental 2024 structure. The second most important is zero-news, because it reveals how much of the measured value is coming from the preserved base allocator rather than the overlay. Those nulls matter because event-study estimates can degrade under misspecification and finance workflows remain highly vulnerable to temporal leakage. citeturn25academia5turn27academia0turn27academia2

### Promotion Criteria

No method should be considered for official-runtime replacement unless **all** of the following are true:

- it is selected and tuned only on 2024;  
- all parameters are frozen before 2025 replay;  
- it improves over the relevant preserved base allocator on frozen 2025 public-A evaluation;  
- it survives shuffled-news and zero-news ablations;  
- it does not materially worsen max drawdown;  
- its turnover remains acceptable under the task’s friction assumptions;  
- its dependency footprint is acceptable and pinned;  
- a deterministic no-model fallback exists;  
- local official-semantics replay passes;  
- official-server parity passes;  
- final human approval is granted.  

Given the current repository status, this promotion discipline is not optional. The current validated runtime is already sufficient for submission review, and the next-stage workflow explicitly separates research, localisation, implementation, frozen evaluation, and parity auditing. fileciteturn0file0 fileciteturn0file4 fileciteturn0file5

### Open Questions for Synthesis

Several synthesis questions remain genuinely open.

The first is whether Track B signal is better modelled as **event study plus ranking** or as **sparse regression plus ranking**. The former is more interpretable; the latter may compress interactions better. The second is whether Track A macro news is genuinely useful for downside control beyond what risk parity already captures from prices. The third is whether Chinese title-level semantic relevance can be improved enough by an offline embedding cache to justify the extra dependency risk over lexical plus entity rules. The fourth is whether sector sensitivity is stable enough across 2024 folds to support event-class-specific coefficients without overfitting. The fifth is how aggressively duplicate clustering should collapse multi-headline coverage of the same policy action. The sixth is whether a two-stage architecture—deterministic event extraction first, semantic relevance second—can materially outperform a purely deterministic baseline without increasing turnover or audit burden. citeturn10academia0turn10academia1turn40view2turn23academia3turn29academia8turn29academia9

Best first-build method:  
**Event-Study Calibrated News Impact Overlay**

Second-best method:  
**Permutation-Tested News Attention Index**

Best Track A method:  
**Volatility-Scaled Macro News Risk Gate**

Best Track B method:  
**Rank-IC Gated Sector News Momentum**

Best transformer-related method:  
**Transformer-Cached Text-to-Sector Relevance plus Rule Impact Gate**

Methods to reject or defer:  
**Hierarchical Daily News Attention Pooling as a promotion candidate; Entity-Sector Graph Propagation News Score; online LLM allocators; full neural portfolio allocators; deep RL; graph RL**

Most important ablation:  
**Shuffled-news dates with the original price path, official trade semantics, and turnover controls preserved**

Main implementation risk:  
**Timestamp leakage from same-day news/event-state construction, especially when duplicate headlines and lagged gates silently amplify a single event**

Track A and Track B should use the same news module only at the **front end**. Event taxonomy, duplicate clustering, relevance logic, and impact scoring should be shared. Sensitivity modelling, risk mapping, and overlay rules should diverge by track.

Transformer embeddings should be a **second-build** capability, not a first-build dependency.

A gated overlay should be implemented **after** sensitivity modelling is at least minimally estimated, because an ungated overlay without sensitivity is too close to “headline-to-trade” logic.

Before any official runtime replacement is considered, the method must prove frozen 2025 improvement over preserved baselines, survive zero-news and shuffled-news nulls, maintain acceptable turnover and drawdown, preserve deterministic fallback, and pass both local official-semantics replay and official-server parity.