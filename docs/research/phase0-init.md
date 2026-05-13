## A. Strategy Consolidation Map

| Original Strategy                                    | Status                         | Merged Into                                      | Reason                                                                                                                                                                                                                                                                                                                        |
| ---------------------------------------------------- | ------------------------------ | ------------------------------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Pure LLM end-to-end allocation                       | Reject                         | —                                                | Too prompt-sensitive; high turnover risk; weak cash/trade-format control; likely inferior to deterministic baselines. The repo describes daily target-weight rebalancing, but the starter environment exposes concrete trade APIs and execution constraints, so direct LLM allocation is operationally fragile. ([GitHub][1]) |
| LLM regime classifier + rule-based allocator         | Keep as core strategy          | **S2: Structured LLM Regime-to-Rules Allocator** | Strong interpretability; good Track 1 fit; uses LLM for bounded classification rather than direct trading.                                                                                                                                                                                                                    |
| LLM news summarizer + quantitative optimizer         | Merge                          | **S3: Risk-Budgeted LLM Alpha-Tilt Optimizer**   | Best used as structured score extraction feeding deterministic allocation, not as a standalone “summarizer strategy.”                                                                                                                                                                                                         |
| Retrieval-augmented macro / sector scoring           | Defer                          | Optional extension to S3/S5                      | Potentially useful for report narrative, but small public history makes false analogies likely. Not Version 1 material.                                                                                                                                                                                                       |
| Multi-agent debate / committee allocation            | Reject                         | —                                                | Expensive, non-deterministic, prompt-sensitive, and unlikely to add stable alpha over a small daily ETF universe.                                                                                                                                                                                                             |
| Event-to-ETF exposure mapping                        | Merge                          | **S4: Event-to-Exposure Sector Mapper**          | Useful mainly for Track 2; should be a bounded exposure matrix, not a free-form agent.                                                                                                                                                                                                                                        |
| Classical non-LLM baseline                           | Keep as core strategy          | **S1: Robust Quant Core Allocator**              | Must be built first; likely hard to beat; low leakage and low prompt risk.                                                                                                                                                                                                                                                    |
| Hybrid momentum / mean-reversion + LLM override      | Merge                          | **S3** and **S6**                                | Strong idea, but best implemented as a bounded overlay on a risk-budgeted baseline, not a separate system.                                                                                                                                                                                                                    |
| Risk-budgeting allocator with LLM alpha scores       | Keep as core strategy          | **S3: Risk-Budgeted LLM Alpha-Tilt Optimizer**   | Highest implementation-adjusted ROI; LLM provides weak alpha only, while quant layer controls risk and turnover.                                                                                                                                                                                                              |
| Ranking model over ETFs using news + market features | Defer                          | **S5: Simple ETF Ranking Model**                 | Potentially strong for Track 2, but sample size and public-overfit risk are material.                                                                                                                                                                                                                                         |
| Hierarchical top-down allocator                      | Merge                          | **S2/S3**                                        | Useful architecture pattern; should be embedded as block-level allocation inside regime/risk-budget systems.                                                                                                                                                                                                                  |
| Ensemble of weak allocators                          | Keep as final-stage strategy   | **S6: Small Conservative Ensemble**              | Good final submission layer after components are validated; not a first build.                                                                                                                                                                                                                                                |
| Equal weight baseline                                | Baseline only                  | **S0: Baseline Battery**                         | Required benchmark and regression test.                                                                                                                                                                                                                                                                                       |
| Volatility-scaled equal weight baseline              | Baseline only / core component | **S0/S1**                                        | Strong baseline; also useful as S1 base weight.                                                                                                                                                                                                                                                                               |
| Momentum-only baseline                               | Baseline only / core component | **S0/S1**                                        | Required to determine whether LLM/news signals add anything beyond price trend.                                                                                                                                                                                                                                               |
| Rule-based macro rotation                            | Merge                          | **S1/S2**                                        | Strong Track 1 component; can be purely quant or regime-conditioned.                                                                                                                                                                                                                                                          |
| Sector trend-following baseline                      | Baseline only / component      | **S0/S1/S5**                                     | Core Track 2 benchmark; should be used before building complex sector-news systems.                                                                                                                                                                                                                                           |
| Persistence / previous-weight baseline               | Baseline only / risk control   | **S0/S1/S6**                                     | Important because turnover uncertainty makes inertia valuable.                                                                                                                                                                                                                                                                |
| Defensive / cash allocation if allowed               | Merge                          | **S1/S3/S6**                                     | Cash appears implicitly allowed in the engine via free capital accounting, but final rules should still be verified. Use as defensive fallback, not as a standalone alpha strategy. ([GitHub][2])                                                                                                                             |

---

## B. Final Strategy List

The final strategy universe should be **seven strategies**, with only **three true submission candidates**: S1, S3, and S6. S2 is the first LLM experiment. S4 and S5 are Track 2 or high-upside extensions.

| Final Strategy                                   | Type                              | Track 1 Fit | Track 2 Fit | Expected Edge Source                                                        | Main Risk                                | Priority                   |
| ------------------------------------------------ | --------------------------------- | ----------: | ----------: | --------------------------------------------------------------------------- | ---------------------------------------- | -------------------------- |
| **S0: Baseline Battery**                         | Baseline only                     |           8 |           8 | Equal weight, inverse-vol, momentum, trend, persistence, random lower bound | Mistakenly treating baselines as trivial | Baseline only              |
| **S1: Robust Quant Core Allocator**              | Core baseline / backup submission |           9 |           7 | Inverse-volatility, momentum breadth, defensive sleeve, turnover discipline | Underuses news signal                    | Build first                |
| **S2: Structured LLM Regime-to-Rules Allocator** | Core LLM candidate                |           9 |           6 | LLM maps news to coarse regimes; deterministic rule map allocates           | Regime labels unstable or too coarse     | Build second               |
| **S3: Risk-Budgeted LLM Alpha-Tilt Optimizer**   | Primary candidate                 |           9 |           8 | Quant baseline plus bounded LLM alpha scores and risk budgeting             | LLM tilt adds noise rather than alpha    | Build second / main target |
| **S4: Event-to-Exposure Sector Mapper**          | Track 2 overlay                   |           5 |           8 | Structured event extraction mapped to sector ETF exposure matrix            | Exposure map brittle and regime-specific | Build if time permits      |
| **S5: Simple ETF Ranking Model**                 | High-upside candidate             |           6 |           8 | Price features + bounded text features predict ETF ranking                  | Small-sample overfitting                 | Defer                      |
| **S6: Small Conservative Ensemble**              | Final submission layer            |           9 |           8 | Median/weighted blend of S1, S2, S3 with fallback rules                     | Averaging correlated noise               | Build if components pass   |

---

## C. Enhanced Architecture for Each Final Strategy

### S0: Baseline Battery

#### Purpose

Establish the minimum performance bar and expose implementation errors. In this task, baselines are strategically important because the official task is daily ETF allocation with Sharpe as the primary metric and transaction friction in the backtest. ([GitHub][1])

#### Inputs

* Historical ETF returns.
* Rolling volatility.
* Previous portfolio weights.
* Current cash and holdings.
* Allowed ETF universe.
* Transaction-cost assumption: 0.01% friction, as stated in the repo overview. ([GitHub][1])

#### Processing Logic

1. Generate equal-weight target.
2. Generate inverse-volatility target.
3. Generate momentum-only target.
4. Generate sector trend-following target for Track 2.
5. Generate persistence target: previous day/week weights.
6. Generate random constrained allocation as lower-bound sanity check.
7. Convert each target into valid buy/sell actions.
8. Run all under the same metric and turnover reporter.

#### LLM Role

None.

#### Quant Role

* Return calculation.
* Rolling volatility.
* Momentum.
* Turnover measurement.
* Sharpe, drawdown, cost drag, concentration.

#### Portfolio Construction

Examples:

[
w_i^{EW}=\frac{1}{N},
]

[
w_i^{IVOL}=\frac{1/\hat{\sigma}_i}{\sum_j 1/\hat{\sigma}_j},
]

[
w_i^{MOM} \propto \mathbf{1}(r_{i,L}>0)\cdot \operatorname{rankscore}(r_{i,L})\cdot \frac{1}{\hat{\sigma}_i}.
]

#### Risk Controls

* Maximum single ETF weight.
* Maximum daily turnover.
* Cash buffer for commission.
* No-trade band.
* Defensive fallback for weak momentum breadth.

#### Failure Modes

* Wrong date alignment.
* Lookahead leakage.
* Inconsistent target-weight-to-trade conversion.
* Turnover omitted from comparison.

#### Minimum Viable Version

Equal weight, inverse-vol, 20-day momentum, and persistence.

#### Enhanced Version

Add volatility targeting, drawdown filter, and cost-stress reports.

---

### S1: Robust Quant Core Allocator

#### Purpose

Build the strongest non-LLM system. This is the **backup submission** and the anchor for every advanced system.

#### Inputs

* Historical ETF returns.
* Rolling volatility.
* Momentum over multiple horizons, e.g. 5/20/60 trading days.
* Drawdown.
* Previous weights.
* Cash and holdings.
* ETF pool by track.
* Risk limits.

The public starter kit lists Track 1 as 11 macro/broad assets including CSI 300, CSI 500, ChiNext, STAR 50, consumer, new energy, media, nonferrous metals, energy, Treasury Bond Index, and Gold ETF; Track 2 lists 16 industry-themed ETFs. ([GitHub][3])

#### Processing Logic

1. Compute legal historical features using only visible history.
2. Estimate rolling volatility.
3. Compute absolute and cross-sectional momentum.
4. Compute momentum breadth:
   [
   B_t=\frac{1}{N}\sum_i \mathbf{1}(r_{i,L}>0).
   ]
5. Define base inverse-volatility weights.
6. Tilt toward positive-momentum assets.
7. In Track 1, increase Treasury/gold/cash sleeve when breadth is weak.
8. Smooth target weights:
   [
   w_t^{target}=(1-\rho)w_{t-1}+\rho w_t^{signal}.
   ]
9. Apply max-weight and turnover constraints.
10. Convert target weights into valid trades.

#### LLM Role

None.

#### Quant Role

Primary.

* Inverse volatility.
* Trend filter.
* Momentum breadth.
* Drawdown control.
* Turnover cap.
* Constraint projection.

#### Portfolio Construction

A practical Track 1 version:

[
s_i = a\cdot z(r_{i,20}) + b\cdot z(r_{i,60}) - c\cdot z(\sigma_{i,20}),
]

[
\tilde{w}_i = \frac{\exp(\tau s_i)/\sigma_i}{\sum_j \exp(\tau s_j)/\sigma_j}.
]

Then apply:

[
w_t = \Pi_{\mathcal{C}}\left((1-\rho)w_{t-1}+\rho \tilde{w}_t\right),
]

where (\Pi_{\mathcal{C}}) enforces weight caps, turnover caps, and cash/defensive constraints.

#### Risk Controls

* Max single ETF: 25–35%.
* Max daily turnover: 10–25%, depending on validation.
* No-trade zone: ignore target changes below 2–5%.
* Defensive sleeve: Treasury/gold/cash when momentum breadth is poor.
* Drawdown de-risking: reduce risky sleeve after portfolio drawdown threshold.
* Cost stress: test at 2× and 5× friction.

#### Failure Modes

* Momentum whipsaw.
* Defensive sleeve underperforms in strong equity rallies.
* Over-smoothed weights miss sharp reversals.
* Excessive parameter tuning on public 2025.

#### Minimum Viable Version

Inverse-volatility allocation with 20-day momentum filter and turnover cap.

#### Enhanced Version

Multi-horizon momentum, breadth-conditioned defensive sleeve, volatility target, and drawdown de-risking.

---

### S2: Structured LLM Regime-to-Rules Allocator

#### Purpose

Use the LLM only where it is plausibly useful: compressing daily financial news into a small, stable regime label. The LLM should **not** emit portfolio weights directly.

#### Inputs

* Daily Top-20 news.
* Recent ETF returns.
* Rolling volatility.
* Momentum breadth.
* Previous weights.
* Current holdings and cash.
* Regime taxonomy.
* Risk limits.

The task explicitly provides hot financial news and historical price data to agents, and asks them to generate daily allocation instructions in a standard backtest environment. ([GitHub][1])

#### Processing Logic

1. Parse daily news.
2. Feed the LLM a compact, fixed schema.
3. Ask for one regime label from a closed set:

   * `risk_on`
   * `risk_off`
   * `policy_easing`
   * `growth_slowdown`
   * `inflation_commodity`
   * `sector_policy_positive`
   * `uncertain`
4. Ask for confidence (c_t\in[0,1]).
5. Map regime to deterministic sleeve weights.
6. Shrink toward S1 if confidence is low:
   [
   w_t=(1-\lambda_t)w_t^{S1}+\lambda_t w_t^{regime},
   ]
   where:
   [
   \lambda_t=\min(\lambda_{\max}, c_t\cdot \mathbf{1}*{c_t>c*{\min}}).
   ]
7. Apply turnover cap and trade converter.

#### LLM Role

* Summarization.
* Regime detection.
* Optional confidence scoring.
* No direct allocation ownership.

#### Quant Role

* Validate whether regime output agrees with price context.
* Convert regime to target weights.
* Risk control.
* Turnover control.
* Baseline fallback.

#### Portfolio Construction

Example Track 1 regime table:

| Regime              | Equity Sleeve | Commodity/Gold | Treasury/Cash | Notes                           |
| ------------------- | ------------: | -------------: | ------------: | ------------------------------- |
| risk_on             |        70–85% |          5–15% |        10–20% | Tilt to broad equity and growth |
| risk_off            |        20–40% |         15–30% |        40–60% | Defensive                       |
| inflation_commodity |        35–55% |         25–45% |        10–25% | Energy, metals, gold            |
| policy_easing       |        60–80% |          5–15% |        15–30% | Broad equity + growth           |
| uncertain           |   S1 baseline |    S1 baseline |   S1 baseline | No LLM tilt                     |

#### Risk Controls

* LLM confidence threshold.
* Price confirmation rule.
* Max regime-induced turnover.
* Regime persistence filter: require same regime for 2 days unless confidence is high.
* Fallback to S1 on malformed JSON or contradictory output.

#### Failure Modes

* Regime label changes too often.
* LLM over-interprets generic policy news.
* Regime table is too coarse.
* Prompt paraphrase changes outputs.

#### Minimum Viable Version

One prompt, seven regimes, deterministic allocation table, confidence-gated blend with S1.

#### Enhanced Version

Add sector sub-scores and Track 2 block-level regime mapping.

---

### S3: Risk-Budgeted LLM Alpha-Tilt Optimizer

#### Purpose

This is the **primary recommended strategy**. It keeps the robust quant allocator in control, while using LLM-derived signals only as bounded alpha tilts.

#### Inputs

* Historical ETF returns.
* Rolling volatility.
* Momentum features.
* Drawdown.
* Macro/sector news.
* LLM-generated ETF or block scores.
* LLM confidence.
* Previous weights.
* Risk limits.
* Transaction-cost assumptions.

#### Processing Logic

1. Generate S1 base weights:
   [
   w_t^{base}.
   ]
2. Use LLM to produce bounded scores:
   [
   a_{i,t}\in[-1,1],
   ]
   plus confidence:
   [
   c_{i,t}\in[0,1].
   ]
3. Shrink noisy LLM signals:
   [
   \hat{a}*{i,t}=a*{i,t}\cdot c_{i,t}\cdot \gamma,
   ]
   where (\gamma) is small, e.g. 0.05–0.20.
4. Combine with quant score:
   [
   q_{i,t}=z(\text{momentum}*{i,t})-\eta z(\sigma*{i,t})+\beta \hat{a}_{i,t}.
   ]
5. Convert scores to target weights using inverse-vol softmax:
   [
   \tilde{w}*{i,t}\propto \frac{\exp(\tau q*{i,t})}{\hat{\sigma}_{i,t}}.
   ]
6. Blend with base:
   [
   w_t=(1-\lambda)w_t^{base}+\lambda \tilde{w}_t.
   ]
7. Apply constraint projection.
8. Apply turnover cap.
9. Convert target weights into trade list.

#### LLM Role

* News summarization.
* ETF/block-level scoring.
* Confidence estimation.
* No direct weight generation.
* No final trade generation.

#### Quant Role

Dominant.

* Momentum.
* Volatility scaling.
* Score normalization.
* Risk budgeting.
* Weight smoothing.
* Turnover-aware projection.
* Baseline fallback.

#### Portfolio Construction

Recommended formulation:

[
w_t^{final}
===========

\Pi_{\mathcal{C}}
\left[
(1-\lambda)w_t^{S1}
+
\lambda\cdot
\operatorname{RiskBudgetSoftmax}(q_t,\sigma_t)
\right],
]

where (\lambda) should be small initially, e.g. 0.15–0.30.

#### Risk Controls

* Maximum single ETF: 25–35%.
* LLM tilt budget: no more than 10–25% deviation from S1.
* Daily turnover cap.
* Volatility targeting.
* Prompt failure fallback.
* Confidence-weighted shrinkage.
* Ignore LLM score if it conflicts with strong negative price trend unless explicitly defensive.

#### Failure Modes

* LLM scores add noise.
* Alpha score scale is unstable.
* Optimizer amplifies small score differences.
* Overfitting (\lambda), (\tau), and confidence thresholds to 2025.

#### Minimum Viable Version

S1 base + LLM (-1,0,+1) score per block + small capped tilt.

#### Enhanced Version

ETF-level scores, block hierarchy, confidence decay, prompt-ensemble averaging, and ablation-tested optimizer.

---

### S4: Event-to-Exposure Sector Mapper

#### Purpose

Exploit Track 2 policy/industry news by mapping structured events into sector exposures.

#### Inputs

* Sector news.
* Macro news.
* ETF sector taxonomy.
* Event categories.
* Hand-built exposure matrix.
* Recent sector ETF returns and volatility.
* Previous weights.

#### Processing Logic

1. Extract event tuples:

   * category,
   * affected sector,
   * direction,
   * magnitude,
   * time horizon,
   * confidence.
2. Map events into ETF exposures:
   [
   e_t = M^\top v_t,
   ]
   where (M) is the event-to-ETF exposure matrix.
3. Aggregate same-day events.
4. Decay stale events over 3–10 trading days.
5. Combine with sector trend-following:
   [
   s_{i,t}=q_{i,t}^{trend}+\beta e_{i,t}.
   ]
6. Allocate top-k sectors using inverse volatility.
7. Apply concentration and turnover caps.

#### LLM Role

* Event extraction.
* Event classification.
* Direction and confidence scoring.

#### Quant Role

* Exposure matrix.
* Sector trend filter.
* Score aggregation.
* Risk and turnover control.

#### Portfolio Construction

Top-k sector allocation:

[
w_i \propto \mathbf{1}(s_i \in \text{top } k)\cdot \frac{\max(s_i,0)}{\sigma_i}.
]

#### Risk Controls

* Max sector ETF weight.
* Top-k cap.
* Event confidence threshold.
* No trade on low-confidence events.
* Require trend confirmation for large positive exposure.
* Fallback to sector trend-following baseline.

#### Failure Modes

* Wrong event-sector mapping.
* Sector label drift.
* Policy news already priced in.
* LLM over-classifies generic news as sector-positive.

#### Minimum Viable Version

Hand-built matrix for 8–12 event categories and 16 sector ETFs.

#### Enhanced Version

Event decay, sector-block hierarchy, prompt paraphrase voting, and sector trend confirmation.

---

### S5: Simple ETF Ranking Model

#### Purpose

Attempt a lightweight supervised ranking model using price and structured text features. This is a **deferred high-upside strategy**, especially for Track 2.

#### Inputs

* Historical ETF returns.
* Momentum and volatility features.
* LLM-generated news tags.
* Sector/block labels.
* Future return labels from training period only.
* Chronological validation splits.

#### Processing Logic

1. Build daily ETF feature matrix.
2. Generate labels such as next-day or next-5-day excess return rank.
3. Train low-capacity model:

   * ridge regression,
   * logistic rank classifier,
   * gradient boosting with strict depth limit.
4. Convert predictions into rank scores.
5. Allocate to top-ranked ETFs with inverse-vol scaling.
6. Apply turnover and concentration controls.
7. Compare against momentum-only and sector trend-following.

#### LLM Role

Optional feature extraction only.

#### Quant Role

* Feature engineering.
* Walk-forward training.
* Ranking model.
* Portfolio construction.
* Validation discipline.

#### Portfolio Construction

[
s_{i,t}=f_\theta(x_{i,t}),
]

[
w_i \propto \mathbf{1}(s_i \in \text{top } k)\cdot \frac{s_i^+}{\sigma_i}.
]

#### Risk Controls

* Low model capacity.
* Strict chronological validation.
* No tuning on public 2025 except final confirmation.
* Top-k diversification.
* Weight smoothing.
* Fallback to S1.

#### Failure Modes

* Too little data.
* Public leaderboard overfit.
* Text features duplicate momentum.
* Model learns 2024-specific sector episodes.

#### Minimum Viable Version

Linear ranker using only momentum, volatility, and LLM sector tags.

#### Enhanced Version

Walk-forward ensemble of simple rankers with stability selection.

---

### S6: Small Conservative Ensemble

#### Purpose

Final submission layer that reduces variance by combining only validated components.

#### Inputs

* S1 target weights.
* S2 target weights.
* S3 target weights.
* Optional S4/S5 weights if validated.
* Fold performance statistics.
* Turnover statistics.
* Prompt-stability statistics.

#### Processing Logic

1. Run all candidate strategies through identical validation.
2. Disqualify unstable models.
3. Convert each candidate to target weights.
4. Blend with conservative weights:
   [
   w_t^{ens}=\sum_k \alpha_k w_{k,t},
   ]
   with (\alpha_k) fixed from 2024 validation.
5. Apply final risk projection.
6. Apply final turnover cap.
7. Fallback to S1 if ensemble members disagree sharply.

#### LLM Role

Only through S2/S3/S4 components. The ensemble controller should not be agentic.

#### Quant Role

* Model selection.
* Ensemble weighting.
* Reliability filtering.
* Risk projection.
* Submission choice.

#### Portfolio Construction

Recommended default:

[
w_t^{ens}=0.50w_t^{S1}+0.25w_t^{S2}+0.25w_t^{S3},
]

then adjust only if validation strongly supports different weights.

#### Risk Controls

* Ensemble disagreement cap:
  [
  |w^{S2}-w^{S1}|_1,\ |w^{S3}-w^{S1}|_1
  ]
  must remain below a threshold.
* Final single-ETF caps.
* Turnover cap after blending.
* Cost-stress validation.
* Prompt-stability validation.

#### Failure Modes

* Correlated components.
* Ensemble dilutes the best model.
* Overfitting ensemble weights.
* False sense of robustness.

#### Minimum Viable Version

Average S1, S2, and S3 with fixed weights.

#### Enhanced Version

Reliability-weighted ensemble using 2024 walk-forward ranks only.

---

## D. Final Quantitative Comparison Table

Scoring is conservative. The requested formula is used directly:

[
\begin{aligned}
\text{Overall ROI}=&0.14\max(T1,T2)+0.18S+0.16R+0.14P\
&+0.10I+0.10G+0.08Q\
&-0.07O-0.05E-0.02L.
\end{aligned}
]

No rescaling is applied because the raw scores are already interpretable on a 0–10-like scale.

| Strategy                                         | Role                       | Track 1 Fit | Track 2 Fit | Sharpe Potential | Robustness | Overfit Risk | Engineering Burden | LLM Dependency | Quant Dependency | Interpretability | Private-Test Reliability | Paper Signal | Overall ROI | Final Rank |
| ------------------------------------------------ | -------------------------- | ----------: | ----------: | ---------------: | ---------: | -----------: | -----------------: | -------------: | ---------------: | ---------------: | -----------------------: | -----------: | ----------: | ---------: |
| **S3: Risk-Budgeted LLM Alpha-Tilt Optimizer**   | Primary candidate          |           9 |           8 |              8.0 |        8.0 |            4 |                  6 |              4 |                9 |                8 |                        8 |            9 |    **7.11** |      **1** |
| **S1: Robust Quant Core Allocator**              | Backup / core baseline     |           9 |           7 |              7.2 |        8.5 |            2 |                  4 |              0 |                9 |                8 |                        8 |            6 |    **7.03** |      **2** |
| **S6: Small Conservative Ensemble**              | Final submission layer     |           9 |           8 |              7.8 |        8.0 |            4 |                  7 |              3 |                9 |                7 |                        8 |            8 |    **6.91** |      **3** |
| **S2: Structured LLM Regime-to-Rules Allocator** | First LLM candidate        |           9 |           6 |              6.8 |        7.5 |            4 |                  5 |              5 |                7 |                9 |                        7 |            8 |    **6.51** |      **4** |
| **S4: Event-to-Exposure Sector Mapper**          | Track 2 overlay            |           5 |           8 |              6.8 |        5.8 |            6 |                  6 |              6 |                7 |                8 |                      5.5 |            8 |    **5.59** |      **5** |
| **S5: Simple ETF Ranking Model**                 | High-upside deferred model |           6 |           8 |              7.2 |        5.5 |            7 |                  7 |              3 |                9 |                6 |                      5.5 |            8 |    **5.48** |      **6** |
| **S0: Baseline Battery**                         | Benchmark only             |           8 |           8 |              5.5 |        8.0 |            1 |                  3 |              0 |                6 |                9 |                        8 |            4 |    **6.34** |  Benchmark |

### Interpretation

1. **Why S3 is top-ranked:** It offers the best balance of LLM relevance and portfolio discipline. It can beat S1 only if the text signal has incremental value, but it is still protected by risk budgeting, shrinkage, and fallback rules.

2. **Why sophisticated strategies were downgraded:** Pure LLM, RAG-heavy, and multi-agent methods add variance, prompt sensitivity, and implementation complexity without clear evidence of incremental signal. This task’s official setup rewards daily, reproducible, low-leakage allocation under transaction friction, not unconstrained reasoning. ([GitHub][1])

3. **Highest upside:** S3 if LLM alpha scores are genuinely predictive; S5 if Track 2 has stable price-news interactions, but S5 is much more overfit-prone.

4. **Safest:** S1.

5. **Best one-student implementation:** S1 first, then S2, then S3 only after S1 and S2 are stable.

---

## E. Baseline Challenge and Ablation Plan

### Baseline Challenge

| Baseline                                     | Why it matters                  | What it tests                                    | What advanced strategies must beat          | Failure it can expose                |
| -------------------------------------------- | ------------------------------- | ------------------------------------------------ | ------------------------------------------- | ------------------------------------ |
| Equal weight                                 | Simplest diversified allocation | Basic portfolio and trade conversion correctness | Better Sharpe and drawdown after costs      | Broken rebalancing or data alignment |
| Inverse-vol / volatility-scaled equal weight | Strong risk-adjusted baseline   | Whether risk scaling alone explains performance  | Higher Sharpe without excessive turnover    | Overstated LLM alpha                 |
| Momentum-only                                | Hard-to-beat price baseline     | Whether trend explains returns                   | Incremental return beyond price persistence | News system just follows momentum    |
| Sector trend-following                       | Core Track 2 baseline           | Whether sector rotation works without text       | Better sector timing after costs            | Brittle event mapping                |
| Persistence baseline                         | Tests value of doing less       | Turnover discipline                              | Improvement over low-trade inertia          | Churn-heavy agents                   |
| Rule-based macro/sector rotation             | Tests simple economic logic     | Whether coarse rules are enough                  | Cleaner timing or risk control              | Over-complex LLM system              |
| News sentiment only                          | Tests raw text value            | Whether news polarity has standalone alpha       | Better structured use of text               | LLM summaries add no signal          |
| Random constrained allocation                | Lower bound                     | Backtest sanity                                  | Must dominate consistently                  | Leakage if random looks good         |

### Required Ablations

| Ablation                     | Purpose                          | Expected Result                   | Red Flag if...                                                  |
| ---------------------------- | -------------------------------- | --------------------------------- | --------------------------------------------------------------- |
| No LLM                       | Measures pure quant contribution | S1 remains strong                 | LLM system only wins because quant baseline is weak             |
| LLM scores only              | Tests raw text signal            | Weak to moderate                  | It beats all quant baselines suspiciously without risk controls |
| Quant features only          | Tests price/risk signal          | Strong baseline                   | LLM layer adds no statistically meaningful improvement          |
| No turnover control          | Measures churn damage            | Sharpe falls after cost           | Sharpe improves only by overtrading public data                 |
| No volatility scaling        | Tests risk-budget value          | Drawdown and volatility worsen    | Vol scaling is irrelevant, suggesting bug or weak risk model    |
| No news input                | Tests whether news matters       | Small degradation if LLM useful   | No difference from full model                                   |
| No momentum input            | Tests price-trend dependence     | Performance drops                 | News alone dominates unrealistically                            |
| No regime classifier         | Tests S2’s value                 | S2 loses interpretability/edge    | Regime labels add no stability                                  |
| No ensemble                  | Tests S6 value                   | Ensemble should reduce variance   | Ensemble only improves one public period                        |
| Baseline fallback only       | Tests fallback frequency         | Slightly lower but stable         | Full model collapses without fallback                           |
| Public-data tuned vs untuned | Detects overfit                  | Untuned should remain competitive | Tuned version wins only on 2025                                 |

Minimum promotion thresholds:

| Metric                                | Threshold                                             |
| ------------------------------------- | ----------------------------------------------------- |
| Sharpe improvement over best baseline | At least +0.20 on walk-forward validation             |
| Turnover increase                     | No more than +25% unless Sharpe gain is large         |
| Cost robustness                       | Still positive edge at 2× friction                    |
| Prompt stability                      | Same model rank under at least 2–3 prompt paraphrases |
| Public/private discipline             | No major hyperparameter refit to public 2025          |

---

## F. Recommended Strategy Stack

### Layer 0 — Data and Validation Layer

Build first.

* Schema validation.
* Date alignment check.
* No current-day close/high/low leakage.
* News timestamp validation.
* Missing data handling.
* Trade-action validator.
* Benchmark reproducer.
* Metric reproducer.
* Turnover reporter.
* Cost-stress reporter.

The starter kit exposes server/API files and endpoints such as start, trade, status, next-day, day-data, historical-prices, news, and results APIs; the build should stay close to those interfaces. ([GitHub][3])

### Layer 1 — Robust Baseline Layer

Use S1 as the base:

* Inverse-volatility allocation.
* Multi-horizon momentum tilt.
* Momentum breadth filter.
* Track 1 defensive sleeve: Treasury/gold/cash.
* Track 2 sector trend-following.
* Turnover cap.
* No-trade zone.
* Previous-weight persistence.

This layer is also the **backup submission**.

### Layer 2 — LLM Signal Layer

Use the safest LLM role:

* News-to-regime classifier.
* News-to-sector/block exposure mapper.
* Structured JSON output only.
* Confidence score.
* No direct portfolio allocation.
* No free-form trade recommendation.
* No multi-agent debate.

Recommended output schema:

```json
{
  "regime": "risk_on | risk_off | policy_easing | inflation_commodity | sector_policy_positive | uncertain",
  "confidence": 0.0,
  "asset_scores": {
    "ETF_CODE": {
      "direction": -1,
      "confidence": 0.0,
      "horizon": "short | medium",
      "reason_tag": "policy | macro | liquidity | commodity | earnings | risk"
    }
  }
}
```

### Layer 3 — Quantitative Portfolio Layer

Use deterministic post-processing:

* Score aggregation.
* Volatility adjustment.
* Risk-budget allocation.
* Rank weighting if Track 2.
* Weight smoothing.
* Transaction-cost-aware turnover cap.
* Constraint projection.
* Target-weight-to-trade conversion.

Core formula:

[
w_t^{final}
===========

\Pi_{\mathcal{C}}
\left[
(1-\lambda)w_t^{S1}
+
\lambda w_t^{LLM\text{-}tilt}
\right].
]

### Layer 4 — Ensemble / Submission Layer

Use only validated systems:

* S1 always included.
* S2 included if regime labels improve stability.
* S3 included if LLM alpha passes ablations.
* S4/S5 included only for Track 2 if they beat sector trend-following.
* Final model selected by median walk-forward rank, not best public curve.
* Fallback to S1 on invalid LLM output or excessive disagreement.

What should **not** be agentic:

* Final portfolio construction.
* Trade sizing.
* Risk constraint enforcement.
* Ensemble selection.
* Submission validation.

---

## G. Implementation Priority and Timeline

### Day 1–2: Reproduction and Baselines

**Target output**

* Starter kit runs end-to-end.
* Official backtest API interaction works.
* Baseline Battery S0 implemented.
* Results table includes Sharpe, return, max drawdown, turnover, trade count, cash ratio, and cost drag.

**Success criterion**

* Equal weight, inverse-vol, momentum, persistence, and random baselines run without invalid trades.
* No obvious date leakage.
* Trade logs reconcile with portfolio history.

**Stop criterion**

* If the backtest or trade conversion is not reproducible, do not build LLM systems.

**What not to do yet**

* Do not prompt-engineer.
* Do not tune public 2025.
* Do not build ranking models.

---

### Day 3–5: Strong Quant Baseline

**Target output**

* S1 implemented for Track 1.
* Optional Track 2 version using sector trend-following.
* Full risk and turnover controls.

**Success criterion**

* S1 beats equal weight and inverse-vol in at least some robust walk-forward settings.
* S1 has lower drawdown or better Sharpe stability than momentum-only.
* Turnover is controlled.

**Stop criterion**

* If S1 does not beat inverse-vol or momentum, refine S1 before adding LLMs.

**What not to do yet**

* Do not build RAG.
* Do not build multi-agent systems.
* Do not add supervised models.

---

### Week 2: LLM-Structured Signal System

**Target output**

* S2 implemented.
* Structured regime prompt.
* Regime allocation table.
* Confidence-gated blend with S1.
* Prompt paraphrase tests.

**Success criterion**

* S2 improves S1 or reduces drawdown without materially increasing turnover.
* Regime labels are stable under prompt paraphrase.
* Invalid JSON rate is near zero after parser correction.

**Stop criterion**

* If S2 fails to improve S1 or causes turnover spikes, keep it only as an ablation.

**What not to do yet**

* Do not let LLM output raw trades.
* Do not optimize regime tables against public 2025.
* Do not add multi-agent debate.

---

### Week 3: Hybrid Ensemble and Robustness Testing

**Target output**

* S3 implemented.
* LLM alpha scores integrated with risk-budget optimizer.
* S1/S2/S3 compared under identical validation.
* S6 preliminary ensemble tested.

**Success criterion**

* S3 beats S1 by at least +0.20 Sharpe on internal walk-forward validation, or improves drawdown materially without higher turnover.
* S6 has better median fold rank than individual components.
* Cost-stress and prompt-stability tests pass.

**Stop criterion**

* If S3’s improvement disappears under ablations, submit S1 or S1+S2 instead.

**What not to do yet**

* Do not build S5 unless S1–S3 are stable.
* Do not include Track 2 unless Track 1 is already reliable.

---

### Final Week: Submission Selection and Report

**Target output**

* Frozen candidate set.
* Reproducible runtime.
* Final logs.
* Ablation tables.
* System report outline.

**Success criterion**

* Final candidate is selected by robust validation, not public leaderboard peak.
* Runtime is deterministic enough for organiser evaluation.
* Report has clear baseline and ablation evidence.

**Stop criterion**

* No last-minute architecture changes unless fixing a verified bug.

**What not to do yet**

* Do not add new LLM prompts.
* Do not change risk parameters based on one public run.
* Do not introduce new dependencies without necessity.

---

## H. Final Decision

1. **Final recommended primary strategy:**
   **S3: Risk-Budgeted LLM Alpha-Tilt Optimizer.** It is the best balance between quant discipline and LLM relevance.

2. **Backup strategy:**
   **S1: Robust Quant Core Allocator.** This is also the first system to build.

3. **High-upside strategy:**
   **S6: Small Conservative Ensemble** if S1/S2/S3 all pass validation. For Track 2 specifically, S4 or S5 can be tested later, but neither should be early priority.

4. **Baseline that must not be ignored:**
   **Inverse-volatility plus momentum plus persistence.** This is likely much harder to beat than an equal-weight baseline.

5. **Strategies to reject:**

   * Pure LLM end-to-end allocation.
   * Multi-agent debate.
   * Heavy RAG as an early system.
   * LLM direct trade generation.
   * Public-leaderboard-tuned prompt systems.

6. **Strategies to use only as ablations:**

   * News sentiment only.
   * LLM scores only.
   * Rule-based macro rotation without quant risk controls.
   * Defensive/cash-only allocator.
   * Random constrained allocation.

7. **Track choice:**
   Prioritize **Track 1**. Attempt Track 2 only after S1–S3 are stable and reusable. Track 1 has a smaller, cleaner macro universe with explicit defensive assets, while Track 2’s 16-sector universe is more exposed to sector-label drift and public-overfit risk. ([GitHub][3])

8. **Build first:**
   Data validator + S0 + S1.

9. **Postpone:**
   S4, S5, RAG, multi-agent systems, and any supervised model requiring heavy tuning.

10. **System report content:**
    Write up:

* official task mechanics and leakage controls,
* baseline battery,
* target-weight-to-trade conversion,
* risk-budget construction,
* LLM structured-signal schema,
* no-LLM and no-news ablations,
* turnover/cost stress,
* prompt-stability analysis,
* public/private robustness policy.

## Final Build Recommendation

* **Primary build:** S3 — Risk-Budgeted LLM Alpha-Tilt Optimizer.
* **Backup build:** S1 — Robust Quant Core Allocator.
* **High-upside extension:** S6 — Small Conservative Ensemble of S1/S2/S3.
* **Baseline to beat:** Inverse-volatility + momentum + persistence.
* **Track priority:** Track 1 first; Track 2 only after Track 1 stack is stable.
* **Do not build:** Pure LLM allocator, multi-agent debate, early RAG, direct LLM trade generator.
* **First implementation task:** Reproduce the starter backtest and implement S0/S1 with leakage checks and turnover reporting.
* **Final submission policy:** Submit S1 if LLM signals are weak; submit S3 if it passes ablations; submit S6 only if the ensemble improves median walk-forward rank without increasing turnover materially.

[1]: https://github.com/splash-li/NLPCC2026-Shared-Task-4/ "GitHub - splash-li/NLPCC2026-Shared-Task-4 · GitHub"
[2]: https://raw.githubusercontent.com/splash-li/NLPCC2026-Shared-Task-4/refs/heads/main/NLPCC_tasks/server_platform/app/core/backtest.py "raw.githubusercontent.com"
[3]: https://github.com/splash-li/NLPCC2026-Shared-Task-4/tree/main/NLPCC_tasks "NLPCC2026-Shared-Task-4/NLPCC_tasks at main · splash-li/NLPCC2026-Shared-Task-4 · GitHub"
