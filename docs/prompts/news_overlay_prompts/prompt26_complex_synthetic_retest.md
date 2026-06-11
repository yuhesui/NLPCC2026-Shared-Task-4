# Prompt26 — Synthetic-Data Stress Retest for Complex News Overlay Candidates G21B and G12B

## Role

You are a senior quantitative research engineer, synthetic-data stress-test designer, Chinese financial NLP engineer, and model-risk auditor.

You are continuing after the top-8 minor-enhancement consolidation. The goal is **not** to promote a candidate. The goal is to test whether the two complex Track B candidates have real potential if their current weakness is caused by insufficient data rather than flawed architecture.

## Target Candidates

Primary retest candidates:

```text
G21B V0
  method_stack: N2345/I256/S5
  architecture: composite BGE/FinBERT/event-label/sector-query news stack + composite impact + BL-style sector overlay

G12B V0
  method_stack: N2345/I256/S126
  architecture: composite BGE/FinBERT/event-label/sector-query news stack + composite impact + composite sensitivity / Rank-IC / attention overlay
```

Reference candidates only:

```text
G14B V4 — N5/I5/S2 + H1+H5
G15B V0 — N4/I6/S2
G10B V5 — N2/I2/S2 + H1+H2+H4+H5
G00B — no-news baseline reference only
G01B — lexical/news rule control reference only
```

Do not replace the top candidate shortlist with baseline/simple candidates. Use references only to judge whether G21B/G12B become competitive.

## Key Hypothesis

The current G21B/G12B weakness may be caused by data scarcity:

```text
real 2024 tune window:
  about 1 trading year

complex candidates:
  many interacting modules:
    N2345 = N2 + N3 + N4 + N5
    I256 = I2 + I5 + I6
    S5 or S126 = complex portfolio/sensitivity layer
```

Prompt26 tests whether more training-like data improves stability, calibration, component attribution, and control deltas.

Synthetic data is for **diagnostic stress testing only**. It must not be used as final competition evidence or hidden leaderboard tuning.

## Non-Negotiable Rules

```text
- Do not tune on real 2025.
- Do not use hidden 2026.
- Do not change official runtime configs.
- Do not promote automatically.
- Do not download new models.
- Do not call online APIs.
- Do not claim synthetic-data performance as real alpha.
- Do not include no-news/simple baselines as top final candidates.
- Synthetic data may calibrate and stress-test only.
- Final real evaluation must still use 2024 tune and frozen 2025 test.
```

## Output Directory

Write all outputs under:

```text
outputs/reports/news_overlay/prompt26_complex_synthetic_retest/presented/
outputs/reports/news_overlay/prompt26_complex_synthetic_retest/reference/
outputs/reports/news_overlay/prompt26_complex_synthetic_retest/progress/
```

## Stage 0 — Preflight

Verify:

```text
- latest top-8 candidate summary exists;
- G21B/G12B configs exist;
- G21B/G12B can run on real 2024/2025 rows;
- no official runtime configs changed;
- no new model downloads;
- previous material-difference and preserved-control blockers are recorded.
```

Required outputs:

```text
reference/preflight_check.csv
presented/preflight_summary.md
```

## Stage 1 — Synthetic Data Generator

Create a deterministic synthetic data generator that produces daily records resembling the available task format:

```text
date
top_news_items
event_labels
sector_tags
aspect_tone
synthetic_price_returns
synthetic_sector_returns
regime_label
shock_label
```

Synthetic regimes must include:

```text
bull_trend
bear_trend
sideways
high_volatility
policy_shock
sector_rotation
news_noise
event_cluster
```

Important: synthetic news/returns must be generated from known simulated latent factors so that expected direction is auditable.

Required outputs:

```text
reference/synthetic_data_schema.csv
reference/synthetic_generation_config.yaml
reference/synthetic_data_quality_report.csv
presented/synthetic_data_summary.md
```

## Stage 2 — Data-Length Stress Test

Run G21B and G12B across increasing synthetic-history sizes.

Minimum required run now:

```text
0.5 synthetic year
```

Also prepare configs for but do not necessarily run unless cheap:

```text
1 synthetic year
2 synthetic years
4 synthetic years
```

For each size, run:

```text
synthetic_train/calibration only:
  G21B
  G12B

real-reference validation:
  real 2024 diagnostic replay
  frozen real 2025 diagnostic replay
```

Do not tune on real 2025.

Required output:

```text
reference/synthetic_length_stress_matrix.csv
presented/synthetic_length_stress_summary.md
```

Columns required:

```text
candidate
synthetic_years
num_synthetic_days
run_status
calibration_mode
real_2024_return
real_2024_sharpe
real_2024_selection_score
real_2025_return
real_2025_sharpe
real_2025_max_drawdown
real_2025_turnover
delta_vs_G14B
delta_vs_G15B
delta_vs_G10B
delta_vs_G00B_reference
component_stability_score
overlay_activity_days
mean_abs_overlay
max_abs_overlay
material_difference_status
preserved_control_delta_status
notes
```

## Stage 3 — Component Attribution

For G21B and G12B, produce component-level attribution:

```text
N2 contribution
N3 contribution
N4 contribution
N5 contribution
I2 contribution
I5 contribution
I6 contribution
S5 contribution for G21B
S1/S2/S6 contribution for G12B
```

Run ablations:

```text
N2345 full
N2 only
N2+N5
N2+N3+N5
I2 only
I2+I5
I2+I6
full I256
S5 confidence cap on/off
S126 reduced to S2 only
S126 reduced to S2+S6
```

Required outputs:

```text
reference/complex_component_attribution.csv
reference/complex_ablation_matrix.csv
presented/component_attribution_summary.md
```

## Stage 4 — G21B-lite and G12B-lite Diagnostic Variants

Create diagnostic variants only:

```text
G21B_lite:
  N2345 with consensus shrink
  I256 with dominance cap
  S5 with BL-view confidence cap
  event/evidence count required before overlay

G12B_lite:
  N2345 with consensus shrink
  I256 with dominance cap
  S126 simplified to S2 plus one sensitivity shrink term
  S6 downweighted or removed if unstable
```

Run only a compact matrix:

```text
G21B V0
G21B_lite
G12B V0
G12B_lite
G14B reference
G15B reference
G10B reference
G00B reference
```

Use:

```text
2024 tune/diagnostic
2025 frozen diagnostic
```

Required outputs:

```text
reference/complex_lite_variant_results.csv
presented/complex_lite_variant_summary.md
```

## Stage 5 — Decision Report

Classify G21B and G12B:

```text
continue_as_top_candidate
continue_as_research_backup
simplify_and_retest
retire_from_selection_keep_for_ablation
```

Do not promote to official runtime.

Decision criteria:

```text
G21B/G12B may continue only if:
  - real 2025 Sharpe/return are competitive with G14B/G15B/G10B references;
  - material-difference blocker improves or is explained;
  - preserved-control deltas no longer fail;
  - component attribution is interpretable;
  - synthetic length curve shows stability improvement, not random overfit.

If synthetic length helps but real 2024/2025 does not improve:
  classify as research-only.

If synthetic length does not help:
  classify as too complex / retire from selection.
```

Required outputs:

```text
reference/complex_candidate_decision_table.csv
reference/synthetic_data_effect_curve.csv
presented/final_complex_retest_recommendation.md
docs/implementation_logs/<timestamp>_prompt26_complex_synthetic_retest.md
```

## Tests and Checks

Run compact checks:

```bash
rtk --version
rtk git status
rtk git diff --name-only
rtk python -m pytest tests/test_nlpcc/test_news_overlay -q
```

If full pytest is too slow, run targeted tests and record exact scope.

Required output:

```text
reference/checks_summary.csv
```

## Final Response Format

```text
Prompt26 status:
  <pass/partial/fail>

Synthetic data generated:
  <0.5y/1y/2y/4y; rows>

G21B result:
  <continue/simplify/retire; summary>

G12B result:
  <continue/simplify/retire; summary>

Synthetic data effect:
  <helped/not helped/inconclusive>

Real 2024/2025 validation:
  <summary>

Comparison references:
  G14B:
  G15B:
  G10B:
  G00B reference only:

Material-difference blocker:
  <resolved/partially resolved/unresolved>

Preserved-control delta blocker:
  <resolved/partially resolved/unresolved>

Official runtime changed?
  <yes/no>

Main artifacts:
  <paths>

Next recommendation:
  <specific next step>
```
