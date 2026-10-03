# Quantitative baseline plan

Goal: a robust, fee-aware quant core against which every NLP variant is measured. No NLP work is
promoted unless it beats the best *comparable* quant baseline on point-in-time, fee-adjusted evidence.

## Baselines (all implemented, `configs/systems/`)

| ID | System | Notes |
|---|---|---|
| Q0 | `q0_cash`, `q0_equal_weight_rebalanced` | sanity: cash is exactly flat; EW with light band |
| Q1 | `q1_buy_and_hold_equal` | one initial allocation then HOLD (turnover ≈ 1/K) — strong on the turnover metric |
| Q2 | `q2_inverse_vol` | 10-day realised vol |
| Q3 | `q3_shrinkage_erc` | Ledoit-Wolf covariance (20 trading days), CCD ERC |
| Q4 | `q4_xs_momentum` | top-k cross-sectional momentum; horizons 1h, 2h, 4h, 1d, 5d, 20d (`momentum_horizons` family) |
| Q5 | `q5_vol_scaled_momentum` | momentum / (σ·√h), top-k softmax with hysteresis |
| Q6 | `q6_multi_horizon_trend` | multi-horizon momentum + trend, tilting an ERC anchor; regime exposure |
| Q7 | `q7_turnover_aware_optimizer` | max α'w − λw'Σw − γ‖w−w₋₁‖₁ (Grinold α = IC·σ·z), per-round/day turnover caps |
| Q8 | `q8_dynamic_exposure` | ERC with vol-target ∧ regime ∧ drawdown gross exposure |

## Evaluation protocol

1. **Metrics**: official four (CR, Sharpe-√1764, MDD on endpoints + closes, two-sided turnover) plus
   gross, names, HHI, round/daily turnover, fees, fee-funding adjustments.
2. **Rank objective**: for a candidate set, compute average-rank scores with
   `competition.evaluation.overall_rank_scores`. Because the score is *relative*, always include
   reference portfolios (Q0 cash, Q1 buy-and-hold, Q3 ERC) in the population.
3. **Periods**: walk-forward windows of 15 trading days (= one Official phase), embargo 1 day,
   over the longest point-in-time history available; report the distribution across windows, not the best one.
4. **Decision timing**: AS_OF = deadline − 5 min; execution at the open of the bar starting at the
   execution time (proxy; see open question Q2).

## Key questions

* Is any rebalancing worth 0.1% per unit turnover at 7 rounds/day? Compare every-round vs
  `rebalance: rounds [1,4]` vs buy-and-hold; expect most value from *not trading*.
* Which momentum horizon survives costs? Intraday horizons (1h–4h) usually turn over far more.
* Does dynamic gross exposure improve Sharpe/MDD enough to offset lower CR in the rank average?
* Shrinkage choice for 30 names on 30-minute bars (sample vs LW vs constant-correlation vs EWMA).

## Status

All Q0–Q8 run end-to-end on the synthetic world (`scripts/experiments/run_matrix.py --families quant_baselines`).
**No baseline has real-market evidence yet**: real point-in-time bars are needed (`docs/data/DATA_PROVENANCE.md`).
The synthetic generator plants momentum (AR(1) drift), so synthetic momentum results are by construction
and must not be read as evidence.
