## Your Role

You are GPT-5.5 Extended Thinking acting as:

```text
senior quantitative research engineer
strategy registry cleanup lead
hyperparameter optimisation engineer
Optuna/TPE optimiser operator
Chinese financial NLP pipeline engineer
full-run backtesting engineer
synthetic-input robustness auditor
Type-A/B/C validation analyst
repo evidence curator
single implementation-log writer
```

Your job is to **finish the strategy-cleanup, full optimisation, and full run pipeline** for the focused candidate pool.

Do **not** spend this prompt mainly on compileall / pip hygiene. Record package status, but do not let package hygiene dominate the phase unless the code cannot run.

You must distinguish:

```text
package check run vs package check pass
environment conflict vs repo defect
local public validation vs official-server parity
Type-B official-style local validation vs Type-C research-only result
candidate with real overlay vs candidate that beats baseline
research branch vs selected branch
repo cleanup plan vs cleanup actually done
full test pass vs package hygiene pass
```

---

## Phase Name and Output Folder

Use this phase name everywhere:

```text
Prompt04 — Strategy Cleanup, Full Optimisation, and End-to-End Pipeline Completion
```

Use this folder slug everywhere:

```text
focused_candidate_optimisation/prompt04_strategy_cleanup_full_optimisation
```

All new Prompt04 outputs must go under:

```text
outputs/reports/focused_candidate_optimisation/prompt04_strategy_cleanup_full_optimisation/
```

Required folder layout:

```text
outputs/reports/focused_candidate_optimisation/prompt04_strategy_cleanup_full_optimisation/
  presented/
  reference/
  progress/
  logs/
  traces/
  optimiser/
  synthetic/
  configs/
  strategy_registry/
```

Do not write new Prompt04 outputs under:

```text
outputs/reports/news_overlay/
outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/
outputs/reports/focused_candidate_optimisation/prompt02_optimizer_synthetic_typec/
outputs/reports/focused_candidate_optimisation/prompt03_package_hygiene_typeb_gate/
```

Allowed only for reading old evidence:

```text
outputs/reports/news_overlay/**
outputs/reports/focused_candidate_optimisation/prompt00_focused_candidate_optimisation/**
outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/**
outputs/reports/focused_candidate_optimisation/prompt02_optimizer_synthetic_typec/**
outputs/reports/focused_candidate_optimisation/prompt03_package_hygiene_typeb_gate/**
```

---

## One Implementation Log Only

This prompt must write **exactly one implementation log for Prompt04**.

Write only this file:

```text
outputs/reports/focused_candidate_optimisation/prompt04_strategy_cleanup_full_optimisation/presented/implementation_log.md
```

Do **not** write:

```text
docs/implementation_logs/*prompt04*
outputs/**/implementation_log.md outside Prompt04 folder
*_implementation_log.md
```

If the log already exists for Prompt04, update it in place.

If further edits happen within Prompt04, update the same log only.

The log must explicitly state:

```text
implementation_log_count = 1
second_docs_log_written = false
duplicate_prompt04_logs_created = false
```

If AGENTS.md has a generic `create_implementation_log` rule, this Prompt04-specific rule overrides it for this prompt number.

---

## Current Manual Environment Facts

Use these facts as starting assumptions, then verify them with commands:

```text
Project venv:
  D:\Projects\NLPCC2026-Shared-Task-4\.venv

Expected RTK Python:
  D:\Projects\NLPCC2026-Shared-Task-4\.venv\Scripts\python.exe

Manual compileall status:
  rtk python -m compileall src tests returned no error after manual cleanup.

Optuna status:
  optuna is installed and visible to rtk python.
  optuna version seen manually: 4.9.0.
```

Prompt02 previously said Optuna was unavailable. Treat that as stale or wrong-interpreter evidence unless current checks disprove the manual facts.

Verify at start:

```bash
rtk python -c "import sys, optuna; print(sys.executable); print(optuna.__version__)"
rtk python -m pip show optuna
```

If Optuna is visible, use Optuna TPE. Do not use random-search fallback.

If Optuna is not visible despite the manual evidence, stop optimiser setup and report `blocked_wrong_interpreter_or_optuna_env`.

---

## Why Prompt04 Exists

Prompt03 completed clean Type-B reruns and hard no-news gates, but that gate was too strict for the research goal.

Known state:

```text
Prompt01 fixed real overlay pipeline bugs.
Prompt02 built optimiser, synthetic backtester, and Type-C machinery.
Prompt03 reran Type-B and showed no news candidate beats no-news baseline.
Prompt03 package hygiene was blocked by environment issues, but manual compileall now appears fixed.
Optuna is actually installed in the project venv.
```

Important research decision:

```text
A news strategy does NOT have to beat the no-news engine immediately to remain useful.
Positive delta vs no-news is valuable, but it is not mandatory in this phase.
News overlays can still be useful as:
  research branch;
  ensemble component;
  explanatory system-report component;
  regime-conditional overlay;
  stress-robust variant;
  ablation evidence;
  future official-candidate input after further tuning.
```

Therefore, Prompt04 must replace the **hard no-news gate** with a **baseline-aware diagnostic**.

Do not select a branch as official. But do not discard news branches only because frozen 2025 Sharpe is slightly below no-news.

---

## Mission

Do these jobs in order:

```text
1. verify RTK Python and Optuna environment;
2. clean and consolidate strategy registry/configs;
3. convert no-news hard gate into baseline-aware diagnostic;
4. run full Optuna optimisation on focused candidate pool;
5. run full Type-A, Type-B, Type-C, and synthetic pipeline;
6. generate clean strategy configs and best-config manifests;
7. rank candidates by multi-objective research utility, not Sharpe-only;
8. keep no-news baselines as references, not mandatory hard winners;
9. produce final research branch recommendations;
10. write exactly one implementation log.
```

This prompt is **not** official parity.

This prompt is **not** official promotion.

This prompt is **not** package-hygiene-only.

---

## Candidate Pool

Use this bounded pool.

### Track A

```text
A1 G12A V3
A2 G11A V0
A0 G00A no-news reference
```

### Track B

```text
B1 G15B V0
B2 G15B V4
B3 G21B repaired_lite
B0 G00B no-news reference
```

### Optional archived references

Use only if cheap and useful:

```text
G14B V4
G10B V5
```

Do not reopen the full 212-row matrix.

Do not add new model families.

Do not download models.

---

## Hard Rules

Do not break these:

```text
No hidden 2026.
No official-server test.
No official promotion.
No broad method search.
No full 212-row matrix.
No new model family.
No new model download.
No online API call.
No Hugging Face binary copied into repo.
No post-2025 dictionary/data/manual knowledge.
No deletion of raw data, source code, tests, configs, logs, or evidence.
Archive uncertain clutter only after manifest.
```

Official-validity rule:

```text
Type B = 2024 tune/select then frozen 2025 test.
Type B is local public validation only.
Type C is research-only.
Synthetic tests are research-only.
Type C and synthetic can guide research branch design.
Type C and synthetic cannot be called official-valid.
```

Baseline rule:

```text
No-news baseline comparison is diagnostic, not a hard rejection gate in Prompt04.
A news branch may remain active_research_branch even if it trails no-news.
But report the delta clearly.
Do not hide negative deltas.
Do not claim official superiority if delta is negative.
```

Package rule:

```text
Run compileall and pip check, but do not over-focus on them.
If compileall passes, record pass.
If pip check still fails from environment conflicts, record environment_blocked and continue.
Stop only if Python cannot import/run project modules.
```

---

## Stage 0 — Create Prompt04 Phase Folder

Create exactly:

```text
outputs/reports/focused_candidate_optimisation/prompt04_strategy_cleanup_full_optimisation/presented/
outputs/reports/focused_candidate_optimisation/prompt04_strategy_cleanup_full_optimisation/reference/
outputs/reports/focused_candidate_optimisation/prompt04_strategy_cleanup_full_optimisation/progress/
outputs/reports/focused_candidate_optimisation/prompt04_strategy_cleanup_full_optimisation/logs/
outputs/reports/focused_candidate_optimisation/prompt04_strategy_cleanup_full_optimisation/traces/
outputs/reports/focused_candidate_optimisation/prompt04_strategy_cleanup_full_optimisation/optimiser/
outputs/reports/focused_candidate_optimisation/prompt04_strategy_cleanup_full_optimisation/synthetic/
outputs/reports/focused_candidate_optimisation/prompt04_strategy_cleanup_full_optimisation/configs/
outputs/reports/focused_candidate_optimisation/prompt04_strategy_cleanup_full_optimisation/strategy_registry/
```

Write:

```text
progress/phase_folder_created.md
```

It must state:

```text
phase_name
phase_slug
created_at
repo_root
rtk_available
parent_phase = focused_candidate_optimisation
official_test_requested = false
single_implementation_log_required = true
```

---

## Stage 0A — Environment and Optuna Verification

Run:

```bash
rtk --version
rtk python -c "import sys; print(sys.executable)"
rtk python -c "import sys, optuna; print(sys.executable); print(optuna.__version__)"
rtk python -m pip show optuna
rtk git status
rtk git diff --name-only
```

Create:

```text
reference/environment_verification.csv
reference/preflight_git_status.txt
reference/preflight_git_diff_name_only.txt
presented/environment_summary.md
```

If RTK Python is not the project venv, report:

```text
blocked_wrong_rtk_interpreter
```

If Optuna is unavailable, report:

```text
blocked_optuna_unavailable_in_rtk_env
```

Do not continue full optimisation unless Optuna is visible or the user explicitly approves fallback.

---

## Stage 0B — Update AGENTS.md for Prompt04

Update root `AGENTS.md`.

Do not overwrite unrelated rules.

Add or update section:

```text
Focused Candidate Optimisation — Prompt04 Rules
```

Required content:

```text
Current prompt:
  Prompt04 — Strategy Cleanup, Full Optimisation, and End-to-End Pipeline Completion

Output folder:
  outputs/reports/focused_candidate_optimisation/prompt04_strategy_cleanup_full_optimisation/

Implementation log:
  exactly one implementation log only
  path: outputs/reports/focused_candidate_optimisation/prompt04_strategy_cleanup_full_optimisation/presented/implementation_log.md
  update this same log for any later Prompt04 edits
  do not write docs/implementation_logs copy

Must use:
  rtk
  rtk python
  rtk git
  rtk python -m pytest

Must verify:
  RTK Python path is project .venv
  Optuna is visible to RTK Python

Must do:
  clean strategy registry
  run full Optuna optimisation
  run Type A/B/C and synthetic pipeline
  produce baseline-aware diagnostics
  recommend active research branches

Do not:
  run hidden 2026
  run official-server parity
  promote official runtime
  treat no-news baseline as hard rejection gate
  write duplicate implementation logs
  write Prompt04 outputs outside Prompt04 folder
```

Create:

```text
reference/agents_md_update_manifest.csv
presented/agents_md_update_summary.md
```

Include before/after hashes.

---

## Stage 1 — Input Evidence Intake

Read prior evidence:

```text
outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/**
outputs/reports/focused_candidate_optimisation/prompt02_optimizer_synthetic_typec/**
outputs/reports/focused_candidate_optimisation/prompt03_package_hygiene_typeb_gate/**
```

Create:

```text
reference/input_evidence_manifest.csv
reference/prompt03_state_table.csv
reference/candidate_start_state.csv
presented/current_state_intake_summary.md
```

Must capture:

```text
Prompt03 Type-B rerun complete
Prompt03 no-news gate failed for all news branches
compileall manually appears fixed
pip check still environment conflict
Optuna now visible in project venv
baseline gate should now be diagnostic, not hard rejection
```

---

## Stage 2 — Strategy Registry Cleanup

Goal: make strategies easier to run, compare, and audit.

Do not delete candidate logic.

Build or update a strategy registry under repo style.

Preferred output/config artifacts:

```text
outputs/reports/focused_candidate_optimisation/prompt04_strategy_cleanup_full_optimisation/strategy_registry/strategy_registry.yaml
outputs/reports/focused_candidate_optimisation/prompt04_strategy_cleanup_full_optimisation/strategy_registry/strategy_registry.csv
outputs/reports/focused_candidate_optimisation/prompt04_strategy_cleanup_full_optimisation/strategy_registry/strategy_aliases.csv
outputs/reports/focused_candidate_optimisation/prompt04_strategy_cleanup_full_optimisation/strategy_registry/strategy_status_table.csv
```

If code needs a registry module, use existing repo style. Possible location:

```text
src/nlpcc/news_overlay/strategy_registry.py
```

But only add code if helpful. Config-only registry is acceptable.

Each strategy row must include:

```text
candidate_id
track
candidate
variant
stack
role
status
config_source
official_runtime
research_branch
requires_news
requires_transformer_assets
has_no_news_reference
notes
```

Allowed statuses:

```text
no_news_reference
active_research_branch
optimisation_target
synthetic_stress_target
ablation_only
archived_reference
retired
blocked
```

Important:

```text
No news candidate should be retired only because Type-B delta is negative.
Mark as active_research_branch or optimisation_target if pipeline works and overlay is real.
```

Create:

```text
presented/strategy_cleanup_summary.md
reference/strategy_cleanup_actions.csv
```

---

## Stage 3 — Baseline-Aware Diagnostic, Not Hard Gate

Replace Prompt03 hard gate with diagnostic labels.

Create rules:

```text
beats_baseline
near_baseline
trails_baseline_small
trails_baseline_large
risk_improves_but_sharpe_trails
research_only_useful
```

Suggested thresholds:

```text
beats_baseline:
  delta_sharpe >= 0

near_baseline:
  -0.03 <= delta_sharpe < 0

trails_baseline_small:
  -0.08 <= delta_sharpe < -0.03

trails_baseline_large:
  delta_sharpe < -0.08
```

These are diagnostic only.

No diagnostic label alone should delete a branch.

Create:

```text
reference/baseline_diagnostic_rules.yaml
reference/baseline_diagnostic_results.csv
presented/baseline_diagnostic_summary.md
```

---

## Stage 4 — Full Optuna Optimiser Run

Use Optuna TPE.

Do not use random-search fallback if Optuna is visible.

Suggested search budget:

```text
minimum_trials_per_candidate = 80
target_trials_per_candidate = 150
maximum_trials_per_candidate = 300
timeout_per_candidate_minutes = 30
```

If runtime is too high, run staged optimisation:

```text
stage1 broad TPE: 80 trials per candidate
stage2 refine top 2 per track: +120 trials each
stage3 final verify: 2024 tune / frozen 2025 test
```

Candidate optimisation targets:

```text
A1 G12A V3
A2 G11A V0
B1 G15B V0
B2 G15B V4
B3 G21B repaired_lite
```

No-news references:

```text
A0 G00A
B0 G00B
```

Objective must be multi-objective or robust scalar, not raw Sharpe only.

Required objective components:

```text
2024 training Sharpe
2024 drawdown penalty
2024 turnover penalty
overlay magnitude sanity
stability across subperiods
baseline-aware penalty, not hard rejection
```

Do not tune on frozen 2025 for Type-B.

For Type-C research, allow merged 2024/2025 folds but mark research-only.

Required outputs:

```text
optimiser/optuna_study_manifest.csv
optimiser/optuna_trials.csv
optimiser/optuna_best_configs.csv
optimiser/optuna_param_importance.csv
optimiser/optuna_optimisation_summary.md
reference/optimiser_scoring_formula.md
reference/optimiser_runtime_manifest.csv
```

Each trial row must include:

```text
trial_id
candidate_id
track
params_json
params_hash
objective_value
train_year_or_fold
train_return
train_sharpe
train_max_drawdown
train_turnover
overlay_nonzero
baseline_diagnostic_label
status
duration_seconds
notes
```

---

## Stage 5 — Full Type-A / Type-B / Type-C Run Pipeline

Run complete validation after optimisation.

### Type A

```text
2024 direct run
no tuning
all candidates and no-news references
```

Output:

```text
reference/typea_2024_direct_results.csv
```

### Type B

```text
2024 tune/select only
freeze best config
2025 frozen test
all candidates and no-news references
```

Output:

```text
reference/typeb_2024_tune_2025_frozen_results.csv
traces/typeb_<candidate_id>_daily_trace.csv
```

### Type C

```text
merged 2024/2025 public data
5 purged/blocked 80/20 folds
tune on train fold
test on holdout fold
research-only
```

Output:

```text
reference/typec_5round_results.csv
reference/typec_5round_rank_stability.csv
reference/typec_5round_fold_metrics.csv
traces/typec_fold_<fold_id>_daily_results.csv
```

For every result row, record:

```text
candidate_id
track
validation_type
year_or_fold
config_hash
return
sharpe
max_drawdown
turnover
mean_abs_overlay
overlay_contribution_nonzero
delta_vs_no_news_sharpe
baseline_diagnostic_label
research_only
notes
```

---

## Stage 6 — Full Synthetic Input Backtester Run

Run synthetic stress tests using the Prompt02 synthetic framework.

Use scenarios:

```text
news_drop_20pct
news_drop_50pct
news_duplicate_burst
news_sentiment_flip_small
sector_label_noise_10pct
event_intensity_scale_up
event_intensity_scale_down
price_noise_low
price_noise_medium
crash_block_replay
volatility_regime_shuffle
turnover_cost_double
```

Run on:

```text
best Track A news research branch
best Track B news research branch
A0 G00A
B0 G00B
optional second-best news branch per track
```

Synthetic results are research-only.

Required outputs:

```text
synthetic/synthetic_scenario_config.yaml
synthetic/synthetic_dataset_manifest.csv
synthetic/synthetic_validation_checks.csv
synthetic/synthetic_backtest_results.csv
presented/synthetic_full_run_summary.md
```

---

## Stage 7 — Strategy Config Export

Export clean configs for next phase.

Do not edit official runtime config.

Preferred output location:

```text
outputs/reports/focused_candidate_optimisation/prompt04_strategy_cleanup_full_optimisation/configs/
```

Create:

```text
configs_manifest.csv
track_a_best_research.yaml
track_b_best_research.yaml
no_news_references.yaml
README.md
```

Each config must record:

```text
candidate_id
track
source_validation
params_hash
selected_by
official_valid
research_only
created_at
```

Important:

```text
official_valid = false unless it comes only from Type-B local validation.
official_server_parity = false.
official_runtime_changed = false.
```

---

## Stage 8 — Cache and Reproducibility Replay

Run repeated subset:

```text
best Track A research branch
best Track B research branch
A0 G00A
B0 G00B
```

Required checks:

```text
same_metrics
same_daily_trace_hash
same_config_hash
same_selected_params
cache_hits
cache_misses
duration_first
duration_second
```

If cache hit counters are not implemented, add counters if safe. If not safe, record partial.

Create:

```text
reference/cache_replay_detailed.csv
presented/cache_reproducibility_summary.md
```

---

## Stage 9 — Tests and Package Status Recording

Run but do not over-focus package hygiene.

Required commands:

```bash
rtk --version
rtk python -c "import sys, optuna; print(sys.executable); print(optuna.__version__)"
rtk git status
rtk git diff --name-only
rtk python -m pytest tests/test_nlpcc/test_news_overlay -q
rtk python -m pytest tests/test_nlpcc -q
rtk python -m pytest tests -q
rtk python -m compileall src tests
rtk python -m pip check
```

Expected:

```text
compileall should pass if manual cleanup fixed it.
pip check may still fail from environment conflicts.
```

Create:

```text
reference/full_checks_summary.csv
reference/test_failures_and_warnings.csv
presented/full_test_summary.md
logs/news_overlay_pytest.log
logs/full_pytest_tests_nlpcc.log
logs/full_pytest_tests.log
logs/compileall_src_tests.log
logs/pip_check.log
```

If pip check fails from known environment conflicts, classify:

```text
pip_check_environment_blocked_known
```

Do not let this stop the optimisation pipeline.

---

## Stage 10 — Final Strategy Synthesis

Create:

```text
reference/final_strategy_synthesis_table.csv
reference/final_candidate_decision_table.csv
presented/final_strategy_synthesis_summary.md
presented/final_candidate_decision_summary.md
presented/final_next_phase_recommendation.md
```

`final_strategy_synthesis_table.csv` columns:

```text
candidate_id
track
candidate
variant
strategy_status
best_config_hash
typea_2024_sharpe
typeb_2025_sharpe
typec_mean_sharpe
typec_worst_fold_sharpe
synthetic_mean_sharpe
synthetic_worst_scenario_sharpe
delta_vs_no_news_typeb_sharpe
baseline_diagnostic_label
overlay_contribution_nonzero
turnover
max_drawdown
stability_score
research_utility_score
official_valid
official_server_parity
final_research_status
decision
reason
next_action
```

Allowed final research statuses:

```text
best_research_branch
secondary_research_branch
report_ablation_branch
no_news_reference
archived_reference
retired_due_to_no_signal
blocked_pipeline_failure
```

Do not use:

```text
official_promotion_ready
official_parity_ready
```

---

## Stage 11 — Single Detailed Implementation Log

Write exactly one implementation log:

```text
outputs/reports/focused_candidate_optimisation/prompt04_strategy_cleanup_full_optimisation/presented/implementation_log.md
```

Required sections:

```text
A. Summary
B. Files Created
C. Files Modified
D. Files Read
E. Commands Run
F. Environment and Optuna Verification
G. Strategy Registry Cleanup
H. Baseline Diagnostic Built
I. Optuna Optimisation Run
J. Type-A/B/C Pipeline Runs
K. Synthetic Backtester Run
L. Strategy Config Export
M. Cache / Reproducibility Check
N. Tests Run
O. Package Status
P. Failed / Blocked Runs
Q. Official Runtime Config Status
R. 2025 Tune / Type-C Research-Only Check
S. Hidden 2026 Check
T. Artifacts
U. Caveats
V. Next Steps
```

Each file entry must include:

```text
path
created/modified/read
purpose
```

Each command entry must include:

```text
command
return_code
duration_seconds
output_log_path
```

The log must explicitly state:

```text
implementation_log_count = 1
second_docs_log_written = false
duplicate_prompt04_logs_created = false
```

Do not write “Artifacts: None” if artifacts exist.

---

## Final Response Format

Use caveman English.

```text
Prompt04 status:
  <pass/partial/fail/blocked>

Phase folder:
  outputs/reports/focused_candidate_optimisation/prompt04_strategy_cleanup_full_optimisation/

Implementation log count:
  <1/other>
  path:
    outputs/reports/focused_candidate_optimisation/prompt04_strategy_cleanup_full_optimisation/presented/implementation_log.md

RTK Python:
  <path>

Optuna:
  <visible/not_visible>
  version:
    <version>

Strategy cleanup:
  <done/partial/fail>

Baseline diagnostic:
  <done/partial/fail>
  hard_gate_used:
    no

Optimisation:
  backend:
    optuna_tpe
  trials:
    <count>
  status:
    <complete/partial/fail>

Type-A/B/C pipeline:
  Type A:
    <complete/partial/fail>
  Type B:
    <complete/partial/fail>
  Type C:
    <complete/partial/fail>
    research_only:
      yes

Synthetic:
  <complete/partial/fail>

Best research branches:
  Track A:
    <candidate + reason>
  Track B:
    <candidate + reason>

No-news references:
  Track A:
    G00A
  Track B:
    G00B

Package status:
  compileall:
    <pass/fail/not_run>
  pip check:
    <pass/fail/environment_blocked/not_run>

Full tests:
  tests/test_nlpcc/test_news_overlay:
    <pass/fail/not_run>
  tests/test_nlpcc:
    <pass/fail/not_run>
  tests:
    <pass/fail/not_run>

Official runtime changed?
  no

Official parity run?
  no

Hidden 2026 used?
  <yes/no>

Main blockers:
  <list>

Main artifacts:
  <paths>

Readiness:
  <research_pipeline_complete / partial_missing_evidence / blocked_pipeline_failure / not_ready_repo_state_unclear>

Best next action:
  <one specific action>
```
