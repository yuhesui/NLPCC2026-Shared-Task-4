## Your Role

You are GPT-5.5 Extended Thinking acting as:

```text
senior quantitative research engineer
Optuna hyperparameter tuning lead
Chinese financial NLP pipeline engineer
official-agent local runner
time-split backtest auditor
evidence-quality auditor
single implementation-log writer
```

Your job is to run **actual full optimisation and actual Type-C / Type-D backtests** for the current top News Overlay candidates.

Keep this prompt focused. Do not spend this phase on compileall / pip hygiene unless Python cannot run. Do not write long generic reports. Produce concrete CSV evidence and short summaries.

---

## Phase

```text
Prompt05 — Actual Type-C and Type-D Full Optimisation Runs
```

Output folder:

```text
outputs/reports/focused_candidate_optimisation/prompt05_actual_typecd_full_optimisation/
```

Use only needed subfolders:

```text
presented/
reference/
logs/
traces/
optimiser/
configs/
```

---

## One Implementation Log Only

Write exactly one Prompt05 implementation log:

```text
outputs/reports/focused_candidate_optimisation/prompt05_actual_typecd_full_optimisation/presented/implementation_log.md
```

Do not write a `docs/implementation_logs/` copy. Do not create duplicate Prompt05 logs. If further edits happen in Prompt05, update this same log in place.

The log must state:

```text
implementation_log_count = 1
second_docs_log_written = false
duplicate_prompt05_logs_created = false
```

---

## Hard Rules

```text
Use rtk, rtk python, rtk git, rtk python -m pytest.
Use project .venv RTK Python.
Use Optuna TPE if visible.
No hidden 2026.
No online API.
No new model download.
No official-server submission.
No official runtime promotion.
Do not delete prior evidence.
Do not reuse old Type-C or Type-D result tables as if freshly run.
```

Package checks:

```text
Run pytest, compileall, and pip check.
If pip check fails from known environment conflicts, record it and continue.
Do not make pip check the main task.
```

---

## Candidate Pool

Run all these candidates:

```text
A0 G00A no-news reference
A1 G12A V3
A2 G11A V0

B0 G00B no-news reference
B1 G15B V0
B2 G15B V4
B3 G21B repaired_lite
```

Optional only if cheap:

```text
G14B V4
G10B V5
```

Do not run the old full 212-row matrix.

---

## Required Environment Check

Run and save logs:

```bash
rtk --version
rtk python -c "import sys, optuna; print(sys.executable); print(optuna.__version__)"
rtk git status
rtk git diff --name-only
```

If Optuna is not visible, stop and mark:

```text
blocked_optuna_env
```

Do not fallback silently.

---

## Backtest Definitions

### Type B — 2024 tune, 2025 test

```text
Tune/select on 2024 only.
Freeze config.
Test on full 2025.
```

Purpose: main local public validation before official parity.

### Type C — actual merged 2024/2025 robustness test

```text
Merge public 2024 + public 2025.
Create 5 purged/blocked 80/20 folds.
For each fold:
  tune on the 80% train slice;
  freeze best fold config;
  test on the 20% holdout slice;
  run actual target-weight backtest, not proxy table math.
```

Official-valid: no. Type C is research-only.

### Type D — more-data-vs-less-data study

Run two local official-agent paths and compare them.

D1:

```text
Tune/select on 2024.
Freeze config.
Run local official-agent / official-facing wrapper on full 2025.
```

D2:

```text
Use 2024 + first-half-2025 as train/tune data.
Freeze config.
Run local official-agent / official-facing wrapper on later-half-2025.
```

Purpose:

```text
Study whether more public training data improves later-2025 outcome or overfits/hurts.
```

Official-valid:

```text
no, because D2 uses part of 2025 for tuning.
```

Use exact split:

```text
first_half_2025 = earliest 50% trading dates in 2025
later_half_2025 = remaining 50% trading dates in 2025
```

Record exact split dates.

---

## Optimisation Requirements

Use Optuna TPE.

Minimum budget:

```text
80 trials per news candidate for Type B tuning
80 trials per news candidate for each Type-C fold unless runtime forces cap
80 trials per news candidate for Type-D D2 tuning
```

No-news references do not need Optuna unless they have tunable parameters.

If runtime is high, use this cap order:

```text
1. finish Type B for all candidates;
2. finish Type C for A1, A2, B1, B2, B3 plus no-news references;
3. finish Type D for A1, B2, B3 plus no-news references;
4. optionally extend to B1/A2 if time remains.
```

Do not call a smoke run “full”. If trials are capped, say capped.

Objective must include:

```text
Sharpe
max drawdown
turnover
overlay magnitude sanity
subperiod stability
baseline diagnostic delta
```

Baseline beating is useful but not mandatory. Negative delta is allowed for research branches if the method is stable, interpretable, or useful for ensemble/regime analysis.

---

## Actual-Run Evidence Rule

Every claimed run must have CSV evidence.

For each Type B / C / D result, write:

```text
reference/<result_table>.csv
presented/<short_summary>.md
```

Presented summaries must include:

```text
actual CSV path
row count
candidate list
date range
actual_run yes/no
proxy_run yes/no
top rows or compact metric table
clear caveats
```

Required CSVs:

```text
reference/typeb_full_2024_tune_2025_test_results.csv
reference/typec_actual_5fold_results.csv
reference/typec_actual_fold_metrics.csv
reference/typec_actual_rank_stability.csv
reference/typed_d1_2024_train_2025_test_results.csv
reference/typed_d2_2024_plus_h1_2025_train_h2_2025_test_results.csv
reference/typed_more_data_comparison.csv
reference/final_typecd_candidate_synthesis.csv
reference/final_candidate_decision_table.csv
```

Required traces:

```text
traces/typeb_<candidate_id>.csv
traces/typec_fold<k>_<candidate_id>.csv
traces/typed_d1_<candidate_id>.csv
traces/typed_d2_<candidate_id>.csv
```

Each result row must include:

```text
candidate_id
track
candidate
validation_type
train_start
train_end
test_start
test_end
trial_count
config_hash
return
sharpe
max_drawdown
turnover
mean_abs_overlay
overlay_nonzero
delta_vs_no_news_sharpe
actual_run
proxy_run
official_valid
research_only
notes
```

Type D comparison rows must include:

```text
candidate_id
track
d1_sharpe
d2_sharpe
d2_minus_d1_sharpe
d1_return
d2_return
d2_minus_d1_return
d1_max_drawdown
d2_max_drawdown
d1_turnover
d2_turnover
more_data_helped
interpretation
```

---

## Strategy Selection Output

Allowed statuses:

```text
no_news_reference
best_research_branch
secondary_research_branch
ensemble_candidate
regime_candidate
ablation_only
blocked_run_failed
```

Do not use:

```text
official_promotion_ready
official_parity_ready
```

Required final files:

```text
presented/final_typecd_synthesis_summary.md
presented/final_candidate_decision_summary.md
presented/final_next_phase_recommendation.md
reference/final_typecd_candidate_synthesis.csv
reference/final_candidate_decision_table.csv
```

The final summary must answer:

```text
Did Type C actually run for all top candidates?
Which candidates are stable across folds?
Does Type D suggest more data helps or hurts?
Which branch should be kept for Track A research?
Which branch should be kept for Track B research?
Which no-news references remain strongest?
What should be rerun before official parity prep?
```

---

## Tests and Checks

Run:

```bash
rtk python -m pytest tests/test_nlpcc/test_news_overlay -q
rtk python -m pytest tests/test_nlpcc -q
rtk python -m pytest tests -q
rtk python -m compileall src tests
rtk python -m pip check
```

Write:

```text
reference/full_checks_summary.csv
presented/full_test_summary.md
logs/*.log
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
F. Environment / Optuna Status
G. Optimisation Runs
H. Type-B Actual Runs
I. Type-C Actual Runs
J. Type-D More-Data Study
K. Strategy Decisions
L. Tests and Package Checks
M. Failed or Capped Runs
N. Official Runtime Status
O. Hidden 2026 / Leakage Check
P. Artifacts
Q. Caveats
R. Next Steps
```

---

## Final Response Format

Use this exact structure:

```text
Prompt05 status:
  <pass/partial/fail/blocked>

Implementation log:
  <path>
  count: <1/other>

Optuna:
  <visible/not_visible>
  version: <version>
  backend: optuna_tpe

Type B:
  status: <complete/partial/fail>
  rows: <n>
  csv: <path>

Type C:
  status: <complete/partial/fail>
  actual_run: <yes/no>
  folds: <n>
  rows: <n>
  csv: <path>

Type D:
  status: <complete/partial/fail>
  D1 rows: <n>
  D2 rows: <n>
  comparison csv: <path>
  more data helped:
    <yes/no/mixed>

Best research branches:
  Track A: <candidate + reason>
  Track B: <candidate + reason>

No-news references:
  Track A: G00A
  Track B: G00B

Tests:
  pytest news_overlay: <pass/fail/not_run>
  pytest tests_nlpcc: <pass/fail/not_run>
  pytest full tests: <pass/fail/not_run>
  compileall: <pass/fail/not_run>
  pip check: <pass/fail/environment_blocked/not_run>

Official runtime changed?
  no

Official parity run?
  no

Hidden 2026 used?
  <yes/no>

Main caveats:
  <list>

Best next action:
  <one action>
```
