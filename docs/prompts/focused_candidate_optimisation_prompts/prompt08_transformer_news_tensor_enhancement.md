# Prompt08 — Overnight Transformer News Tensor Enhancement and Official-Server Re-evaluation

## Role

You are GPT-5.5 Extended Thinking in a **fresh Codex session**.

Act as:

```text
senior quantitative research engineer
transformer-based financial NLP engineer
portfolio risk-control engineer
official-server integration engineer
overnight optimisation operator
evidence-quality auditor
single implementation-log writer
```

This is an **overnight major enhancement prompt**.

Your mission is to improve the current top news-overlay candidates by replacing weak/discrete news handling with a more robust **transformer-style continuous tensor news signal**, while preserving the strong no-news baseline as the production-safe base.

This is not a broad method-search phase.
This is not a report-writing phase.
This is not a package-cleaning phase.
This is not a “copy old summaries” phase.

Main goal:

```text
Keep A0/B0 as production-safe base engines.
Enhance A2/B2 with bounded transformer/tensor news overlays.
Run overnight optimisation and official-server/platform re-evaluation.
Produce actual CSV evidence in presented/run_csv/.
Decide whether news becomes:
  1. bounded production overlay candidate;
  2. regime/ensemble candidate;
  3. report-only ablation;
  4. rejected in favour of no-news baseline.
```

---

## Starting Interpretation

Use this as the initial hypothesis:

```text
A0 / G00A and B0 / G00B appear closest to production-grade.
A2 / G11A V0 and B2 / G15B V4 are the strongest news candidates but still trail no-news.
A1 / G12A V3 and B3 / G21B repaired_lite are secondary news candidates.
```

Latest known local official-server result pattern:

```text
Track A:
  A0 no-news reference slightly beats A2/A1.
  A2 is the closest news candidate.

Track B:
  B0 no-news reference slightly beats B2/B3.
  B2 is the closest news candidate.

Conclusion:
  Do not replace baseline with news directly.
  Add news only as a bounded, confidence-gated overlay.
```

Do not assume current news processing is good. Audit it first.

---

## Phase

Use this exact phase name:

```text
Prompt08 — Overnight Transformer News Tensor Enhancement
```

Output folder:

```text
outputs/reports/focused_candidate_optimisation/prompt08_transformer_news_tensor_enhancement/
```

Required subfolders:

```text
presented/
presented/run_csv/
reference/
logs/
traces/
server_run/
optimiser/
configs/
news_audit/
features/
ablations/
tests/
```

All important result CSVs must be copied to:

```text
presented/run_csv/
```

Do not leave useful data only in `reference/`.

---

## One Implementation Log Only

Write exactly one Prompt08 implementation log:

```text
outputs/reports/focused_candidate_optimisation/prompt08_transformer_news_tensor_enhancement/presented/implementation_log.md
```

Do not write:

```text
docs/implementation_logs/*
any other Prompt08 implementation_log.md
```

If the log already exists, update it in place.

The log must state:

```text
implementation_log_count = 1
second_docs_log_written = false
duplicate_prompt08_logs_created = false
```

---

## Hard Rules

```text
Use rtk, rtk python, rtk git.
Use project .venv RTK Python.
Use local official server/platform path discovered in Prompt07 if available.
No hidden 2026.
No online API for model inference.
No new model download unless already approved and cached.
No broad 212-row matrix.
No remote official submission.
No fake/proxy results.
No stale summary reuse.
No unbounded news overlay.
No large rewrite of official starter/server code.
No discrete-only sentiment method as final enhancement.
```

Allowed model assets:

```text
Use already-downloaded/cached HF models if present.
Prefer existing local Chinese encoder/sentence-transformer/FinBERT assets.
If model asset missing, fall back to deterministic continuous encoder proxy,
but label it clearly as encoder_proxy, not transformer_real.
```

Skip by design:

```text
pip check
compileall
package build
LaTeX finalization
dependency cleanup
```

Run tests listed later.

---

## Candidate Set

### Production-safe references

```text
A0 G00A no-news reference
B0 G00B no-news reference
```

### Primary news candidates to enhance

```text
A2 G11A V0
B2 G15B V4
```

### Secondary candidates for ablation only if time allows

```text
A1 G12A V3
B3 G21B repaired_lite
```

Do not add more candidates unless all primary stages finish.

---

## Overnight Runtime Budget

This is intended to run overnight.

Target budget:

```text
total wall-clock budget: 6 to 10 hours
minimum useful run: 2 hours
checkpoint every 30 minutes
write progress heartbeat every 30 minutes
```

Create:

```text
logs/overnight_progress_heartbeat.md
reference/runtime_budget_manifest.csv
```

If budget is limited, priority order is:

```text
1. news status audit;
2. implement continuous news tensor for A2/B2;
3. official-server run A0/A2-enhanced/B0/B2-enhanced;
4. ablations for gated vs ungated;
5. extended optimisation;
6. secondary A1/B3 experiments.
```

Do not spend the night on packaging/env cleanup.

---

## Stage 0 — Input Evidence and Current News Status Audit

Before implementing anything, inspect the current news pipeline.

Find and document:

```text
where daily Top-20 news is loaded;
what text fields are used;
whether title/body/summary is used;
whether news is actually reaching A2/B2;
whether sentiment is discrete label, scalar, embedding, or tensor;
whether FinBERT/transformer models are actually imported and executed;
whether GPU/CUDA is used;
whether cache is used;
how news maps to assets/sectors;
how overlay magnitude is computed;
how time decay is handled;
how turnover/risk guards are applied;
where official adapter calls the news code.
```

Required outputs:

```text
news_audit/current_news_pipeline_audit.csv
news_audit/current_news_feature_schema.csv
news_audit/current_news_usage_trace_sample.csv
presented/current_news_status_summary.md
```

`current_news_pipeline_audit.csv` columns:

```text
component
file_path
function_or_class
current_method
uses_transformer
uses_discrete_sentiment
uses_continuous_tensor
uses_cache
uses_gpu
used_by_A2
used_by_B2
used_by_official_adapter
evidence
gap
```

You must explicitly answer:

```text
Is the current news status transformer-real, encoder-proxy, discrete-sentiment, or heuristic?
Is news actually used in official-server runs?
Is the overlay continuous-valued or discrete bucketed?
Is the overlay bounded?
What is missing for production-grade news processing?
```

---

## Stage 1 — Build Continuous Transformer/Tensor News Feature Layer

Implement or repair a bounded continuous news feature layer.

Target design:

```text
daily_news_tensor[d, asset_or_sector, feature_dim]
```

Minimum continuous dimensions:

```text
relevance_score
sentiment_intensity
sentiment_confidence
event_intensity
novelty_score
source_agreement_or_cluster_count
recency_decay_weight
asset_or_sector_affinity
uncertainty_score
```

If a real transformer encoder is available locally, use it to produce:

```text
embedding_vector
query_asset_similarity
event_cluster_similarity
continuous sentiment/regression-style score if available
```

If only FinBERT-like classifier is available, do not stop at positive/neutral/negative. Convert logits/probabilities to continuous scores:

```text
sentiment_score = p_positive - p_negative
confidence = max(probabilities)
entropy = -sum(p_i log p_i)
intensity = abs(sentiment_score) * confidence
```

If only deterministic proxy is available, implement:

```text
encoder_proxy_continuous = true
discrete_sentiment_final = false
```

but label clearly.

Required feature safeguards:

```text
no future data leakage;
no same-day future price leakage;
no hidden 2026;
date-aligned caches;
cache key includes model/config/hash;
missing news produces zero/neutral tensor;
duplicate news does not explode signal;
extreme news capped by robust quantile clipping;
```

Required outputs:

```text
features/news_tensor_schema.yaml
features/news_tensor_build_manifest.csv
features/news_tensor_daily_stats.csv
features/news_tensor_sample_rows.csv
features/news_tensor_cache_manifest.csv
presented/news_tensor_feature_summary.md
```

---

## Stage 2 — Build Bounded News Overlay Enhancements

Do not replace the baseline allocator.

Use this architecture:

```text
final_weight = baseline_weight + gated_news_overlay
```

where:

```text
baseline_weight = A0 or B0 engine output
gated_news_overlay = small bounded correction from A2/B2 continuous news tensor
```

Overlay requirements:

```text
bounded L1 norm;
per-asset cap;
turnover cap;
deadband threshold;
confidence gate;
regime gate;
drawdown guard;
recency decay;
source/event agreement gate;
fallback to baseline if news tensor low-confidence;
```

Implement at least three enhancement variants:

```text
E1_tensor_confidence_gate:
  continuous news tensor + confidence threshold + overlay cap

E2_tensor_regime_gate:
  E1 + volatility/drawdown/regime state gate

E3_tensor_ensemble_shrink:
  E1 + shrink overlay toward zero based on uncertainty and turnover pressure
```

Optional if time:

```text
E4_event_cluster_confirmation:
  requires repeated/clustered event support before nonzero overlay

E5_asset_query_attention:
  asset/sector query vector attends to news embeddings
```

Primary enhanced candidates:

```text
A2_E1, A2_E2, A2_E3
B2_E1, B2_E2, B2_E3
```

Optional:

```text
A1_Ebest
B3_Ebest
```

Required outputs:

```text
configs/enhanced_candidate_manifest.csv
configs/A2_E1.yaml
configs/A2_E2.yaml
configs/A2_E3.yaml
configs/B2_E1.yaml
configs/B2_E2.yaml
configs/B2_E3.yaml
presented/enhancement_design_summary.md
```

---

## Stage 3 — Overnight Optimisation

Use Optuna if available.

Do not optimise on 2025 full test for official-valid selection.

Recommended scheme:

```text
Type-B style:
  tune on 2024 only;
  freeze config;
  test on full 2025.

Auxiliary robustness:
  same-window Type-D H2;
  Type-C folds if runtime allows;
  synthetic stress only for robustness, not final ranking.
```

Optimise these parameters:

```text
overlay_cap
per_asset_cap
confidence_threshold
entropy_threshold
relevance_threshold
deadband
turnover_penalty
drawdown_guard_threshold
recency_half_life
event_confirmation_threshold
shrink_strength
regime_gate_threshold
```

Minimum overnight budget:

```text
A2_E1/E2/E3: at least 100 trials each if runtime allows
B2_E1/E2/E3: at least 100 trials each if runtime allows
secondary A1/B3: optional after primary complete
```

If runtime is insufficient, prioritise:

```text
A2_E3 and B2_E3 first
then A2_E1/B2_E1
then A2_E2/B2_E2
```

Objective:

```text
score =
  Sharpe
  + small return reward
  - drawdown penalty
  - turnover penalty
  - negative baseline delta penalty
  - overlay instability penalty
  - too-frequent-trading penalty
```

Important:

```text
Do not require news to beat no-news in every trial.
But final production-candidate status requires:
  no worse than baseline by a small epsilon,
  or better drawdown/turnover/risk with near-equal Sharpe.
```

Required outputs:

```text
optimiser/overnight_trial_manifest.csv
optimiser/overnight_trials.csv
optimiser/overnight_best_configs.csv
optimiser/overnight_param_importance.csv
presented/overnight_optimisation_summary.md
presented/run_csv/overnight_best_configs.csv
```

---

## Stage 4 — Actual Backtests and Official Server Runs

Run all enhanced candidates through both research backtester and local official server/platform.

Minimum run set:

```text
A0
A2 original
A2_E1
A2_E2
A2_E3

B0
B2 original
B2_E1
B2_E2
B2_E3
```

Optional:

```text
A1 original
A1_Ebest
B3 original
B3_Ebest
```

Required validation modes:

```text
Type-B:
  2024 tune / frozen 2025 test

Same-window Type-D:
  D1-H2 = 2024 train -> later-half 2025
  D2-H2 = 2024 + first-half 2025 train -> later-half 2025

Official-server/platform:
  local official server/platform run on public 2025
```

Required outputs:

```text
reference/typeb_enhanced_results_prompt08.csv
reference/typed_same_window_enhanced_results_prompt08.csv
reference/official_server_enhanced_results_prompt08.csv
reference/official_server_enhanced_metric_comparison_prompt08.csv

presented/run_csv/typeb_enhanced_results_prompt08.csv
presented/run_csv/typed_same_window_enhanced_results_prompt08.csv
presented/run_csv/official_server_enhanced_results_prompt08.csv
presented/run_csv/official_server_enhanced_metric_comparison_prompt08.csv

presented/enhanced_backtest_summary.md
presented/official_server_enhanced_summary.md

traces/official_server_<track>_<candidate_id>_daily.csv
logs/official_server_<track>_<candidate_id>.log
```

Each result row must include:

```text
track
candidate_id
candidate
variant
uses_transformer_real
uses_encoder_proxy
uses_continuous_tensor
uses_discrete_sentiment_final
uses_confidence_gate
uses_regime_gate
uses_turnover_guard
uses_drawdown_guard
server_entrypoint
config_hash
date_start
date_end
num_days
return
sharpe
max_drawdown
turnover
mean_abs_overlay
overlay_nonzero_days
overlay_l1_mean
delta_vs_no_news_sharpe
delta_vs_no_news_return
delta_vs_no_news_drawdown
actual_run
proxy_run
official_server_or_platform_run
official_submission_run
research_only
status
notes
```

---

## Stage 5 — Ablation and News-Use Proof

You must prove the news tensor is actually used.

Run ablations:

```text
baseline_no_news
original_news_candidate
enhanced_news_tensor
enhanced_news_tensor_zeroed
enhanced_news_tensor_shuffled_by_date
enhanced_news_tensor_no_confidence_gate
enhanced_news_tensor_no_turnover_guard
```

At least for:

```text
A2_Ebest
B2_Ebest
```

Required outputs:

```text
ablations/news_use_ablation_results.csv
ablations/news_tensor_zeroed_vs_active.csv
ablations/news_shuffle_leakage_check.csv
presented/news_use_ablation_summary.md
presented/run_csv/news_use_ablation_results.csv
```

Required proof columns:

```text
candidate_id
variant
ablation_type
news_tensor_active
news_tensor_zeroed
news_tensor_shuffled
same_config_hash
return
sharpe
turnover
mean_abs_overlay
overlay_nonzero_days
delta_active_minus_zeroed_sharpe
delta_active_minus_shuffled_sharpe
leakage_suspected
actual_run
proxy_run
notes
```

Interpretation rule:

```text
If active news is indistinguishable from zeroed news, the news overlay is not materially used.
If shuffled news improves more than active news, suspect overfit/leakage/noise.
```

---

## Stage 6 — Production Readiness Decision

Create final decision files:

```text
reference/final_prompt08_decision_table.csv
reference/final_prompt08_candidate_synthesis.csv
presented/run_csv/final_prompt08_decision_table.csv
presented/final_candidate_decision_summary.md
presented/production_readiness_assessment.md
presented/submission_gap_summary.md
presented/final_next_phase_recommendation.md
```

Decision categories:

```text
production_safe_base
bounded_news_overlay_candidate
regime_or_ensemble_candidate
research_only_candidate
report_only_ablation
rejected_news_noise
blocked_run_failed
```

Required decision questions:

```text
Is A0/B0 already production-grade relative to current evidence?
Did A2/B2 enhanced news tensor beat or nearly match A0/B0?
Did news improve drawdown/turnover/risk even if Sharpe is similar?
Is continuous tensor news actually used?
Is the method transformer-real or encoder-proxy?
Is the official server/platform run clean?
What is the safest submission architecture?
What exact cleanup remains for final phase?
```

Allowed final recommendation forms:

```text
A0/B0 only
A0/B0 + bounded A2/B2 news overlay
A0/B0 + regime-gated A2/B2 overlay
A2/B2 enhanced standalone
report-only news ablation
```

Do not use:

```text
submission_ready
official_promotion_ready
top3_ready
```

unless directly supported by server results and final package checks.

---

## Stage 7 — Main Tests

Run:

```bash
rtk python -m pytest tests/test_nlpcc/test_news_overlay -q
rtk python -m pytest tests/test_nlpcc -q
rtk python -m pytest tests -q
```

Also run server/agent smoke tests if available:

```text
test_server*
test_agent*
test_runner*
test_backtest*
```

Do not run pip check or compileall in this phase.

Required outputs:

```text
tests/test_command_manifest.csv
tests/test_results_summary.csv
presented/full_test_summary.md
logs/news_overlay_pytest.log
logs/full_pytest_tests_nlpcc.log
logs/full_pytest_tests.log
logs/official_server_smoke_tests.log
```

---

## Stage 8 — Presented CSV Package

Create:

```text
presented/run_csv_index.md
presented/run_csv_manifest.csv
```

`presented/run_csv_manifest.csv` columns:

```text
csv_path
row_count
candidate_ids
variants
track_coverage
date_range
actual_run
proxy_run
official_server_or_platform_run
why_it_matters
```

Minimum files in `presented/run_csv/`:

```text
overnight_best_configs.csv
typeb_enhanced_results_prompt08.csv
typed_same_window_enhanced_results_prompt08.csv
official_server_enhanced_results_prompt08.csv
official_server_enhanced_metric_comparison_prompt08.csv
news_use_ablation_results.csv
final_prompt08_decision_table.csv
test_results_summary.csv
```

---

## Implementation Log Sections

The single implementation log must include:

```text
A. Summary
B. Files Created
C. Files Modified
D. Files Read
E. Commands Run
F. Current News Status Audit
G. Continuous News Tensor Implementation
H. Bounded Overlay Enhancements
I. Overnight Optimisation
J. Backtests and Official Server Runs
K. News-Use Ablations
L. Production Readiness Decision
M. Tests
N. Presented CSV Package
O. Failed or Blocked Runs
P. Official Runtime Status
Q. Hidden 2026 / Leakage Check
R. Artifacts
S. Caveats
T. Next Steps
```

Every command entry must include:

```text
command
return_code
duration_seconds
log_path
```

Every source modification must include:

```text
path
why modified
safety classification
rollback path
```

---

## Final Response Format

Use this exact structure:

```text
Prompt08 status:
  <pass/partial/fail/blocked>

Implementation log:
  <path>
  count: <1/other>

Current news status:
  method before:
    <discrete/heuristic/encoder_proxy/transformer_real/unknown>
  news actually used before:
    <yes/no/unclear>
  main gaps:
    <list>

Continuous news tensor:
  status: <implemented/partial/blocked>
  transformer_real: <yes/no>
  encoder_proxy: <yes/no>
  tensor schema: <path>

Enhancement variants:
  Track A:
    <variants>
  Track B:
    <variants>

Overnight optimisation:
  status: <complete/partial/fail>
  trials: <n>
  best A variant: <candidate>
  best B variant: <candidate>
  csv: <path>

Official server/platform enhanced run:
  status: <complete/partial/fail/blocked>
  rows: <n>
  csv: <path>

News-use ablation:
  status: <complete/partial/fail>
  active beats zeroed?
    Track A: <yes/no/mixed>
    Track B: <yes/no/mixed>

Best production-safe base:
  Track A: <candidate>
  Track B: <candidate>

Best news overlay candidate:
  Track A: <candidate/none>
  Track B: <candidate/none>

Production readiness:
  <production_safe_base_only / bounded_news_overlay_candidate / research_only / blocked>

Top-3 outlook:
  <low/uncertain/improved but unproven>

Tests:
  pytest news_overlay: <pass/fail/not_run>
  pytest tests_nlpcc: <pass/fail/not_run>
  pytest full tests: <pass/fail/not_run>
  official server smoke tests: <pass/fail/not_found/not_run>

Skipped by design:
  pip check
  compileall
  package build
  LaTeX finalization

Official submission run?
  no

Hidden 2026 used?
  <yes/no>

Main caveats:
  <list>

Best next action:
  <one action>
```
