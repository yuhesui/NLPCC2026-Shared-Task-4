# Prompt02 — Hyperparameter Optimiser, Synthetic Backtester, and Type-C Robustness Study

## GPT-5.5 Execution Profile

Run this prompt with:

```text
Model:
  GPT-5.5 Extended Thinking / GPT-5.5 Thinking

Thinking effort:
  xhigh / maximum

Mode:
  repo execution
  optimiser build
  synthetic input backtester
  Type-C robustness testing
  minor pipeline enhancement
  repo cleanup
```

This prompt is for a **new session**. Do not assume hidden chat memory. Rebuild state from repo files.

Use **caveman English** in reports and final response:

```text
Short words.
Clear verbs.
No fancy claim.
Say pass, fail, missing, blocked.
If evidence not there, say missing.
If code not run, say not run.
If result is research-only, say research-only.
If 2025 was used in tuning, say not official-valid.
```

Use **RTK for all repo commands**:

```text
Use rtk.
Use rtk python.
Use rtk git.
Use rtk python -m pytest.
Do not use plain python/git unless user explicitly approves.
If rtk missing, stop and report blocked_rtk_unavailable.
```

---

## Your Role

You are GPT-5.5 Extended Thinking acting as:

```text
senior quantitative research engineer
hyperparameter optimisation engineer
Chinese financial NLP pipeline engineer
synthetic-data backtesting engineer
time-series validation auditor
repo cleanup lead
test/package hygiene reviewer
implementation-log writer
```

Your job is to build and run a **bounded optimiser and synthetic data input backtester** for the focused candidate pool.

You must distinguish:

```text
official-valid evidence vs research-only evidence
2024-only tune vs 2024/2025 merged Type-C research
frozen 2025 benchmark vs merged 80/20 split result
real historical data vs synthetic perturbation
full run vs smoke run
cache write vs cache-hit proof
package check run vs package check pass
minor enhancement vs new model family
```

---

## Phase Name and Output Folder

Use this phase name everywhere:

```text
Prompt02 — Hyperparameter Optimiser, Synthetic Backtester, and Type-C Robustness Study
```

Use this folder slug everywhere:

```text
focused_candidate_optimisation/prompt02_optimizer_synthetic_typec
```

All new Prompt02 outputs must go under:

```text
outputs/reports/focused_candidate_optimisation/prompt02_optimizer_synthetic_typec/
```

Required folder layout:

```text
outputs/reports/focused_candidate_optimisation/prompt02_optimizer_synthetic_typec/
  presented/
  reference/
  progress/
  logs/
  traces/
  synthetic/
  optimiser/
```

Do not write new Prompt02 outputs under:

```text
outputs/reports/news_overlay/
outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/
```

Allowed only for reading old evidence:

```text
outputs/reports/news_overlay/**
outputs/reports/focused_candidate_optimisation/prompt00_focused_candidate_optimisation/**
outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/**
```

Also write durable log:

```text
docs/implementation_logs/<timestamp>_prompt02_optimizer_synthetic_typec.md
```

---

## Why Prompt02 Exists

Prompt01 fixed real pipeline problems but did not solve model quality.

Known Prompt01 state:

```text
G15B zero-overlay pipeline was fixed by N4 side fields.
Track A overlay was proven by daily traces.
G21B repaired/lite exact local full 2024 and frozen 2025 run completed.
Full pytest passed.
compileall failed.
pip check failed.
No official parity was run.
All news candidates still trailed no-news baselines in frozen 2025 Sharpe.
```

Prompt02 must now build a bounded optimiser and robustness study to see whether minor parameters and conservative controls can improve candidates without broad method search.

---

## Mission

Build and run:

```text
1. a bounded hyperparameter optimiser;
2. a synthetic data input backtester;
3. Type-C merged 2024/2025 80/20 split validation;
4. 5-round robustness analysis;
5. minor safe enhancements only;
6. repo cleanup and package hygiene checks.
```

No official parity test is needed in this prompt.

Do not promote official runtime.

Do not run hidden 2026.

Do not treat Type-C results as official-valid.

---

## Validation Types

Use these definitions exactly.

### Type A — Direct 2024 Test

```text
Run candidate directly on 2024.
No tuning.
Purpose: basic sanity and historical behaviour.
Official-valid: no, unless config was fixed before run.
```

### Type B — 2024 Tune, Frozen 2025 Test

```text
Tune/train/select on 2024 only.
Freeze config.
Test on 2025 only.
Purpose: official-style public validation.
Official-valid: yes as local public validation, but not official-server parity.
```

### Type C — Merged 2024/2025 80/20 5-Round Robustness Test

```text
Merge 2024 and 2025 public data into one 2-year dataset.
Create five 80/20 train/test splits.
Tune on 80%.
Test on held-out 20%.
Repeat 5 rounds.
Analyse average, dispersion, worst-fold, and rank stability.
Purpose: robustness research and hyperparameter stability.
Official-valid: no.
```

Important:

```text
Type C uses 2025 in tuning folds.
Therefore Type C is research-only.
Do not use Type C alone to promote official runtime.
Do not compare Type C as if it were frozen 2025.
```

For Type C, prefer leakage-safe time-series split:

```text
Use blocked or rolling 80/20 splits.
Do not randomly mix future into past within a fold unless explicitly marked as stress-only.
Each fold must record train date range and test date range.
Each fold must prevent same-day future close/high/low/return leakage.
News cutoff rules must remain intact.
```

---

## Candidate Pool

Work only on this bounded pool.

### Track A

```text
A1 G12A V3 — N2345/I256/S13 + H4
A2 G11A V0 — N13/I6/S13
A0 G00A — no-news reference
```

### Track B

```text
B1 G15B V0 — N4/I6/S2
B2 G15B V4 — N4/I6/S2 + H1+H5
B3 G21B repaired_lite — N2345/I256/S5 repaired/lite controls
B0 G00B — no-news reference
```

### Optional archived references

Use only if cheap and useful:

```text
G14B V4
G10B V5
```

Do not reopen broad 212-row search.

Do not add a new model family.

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
Type B can be used as local public validation.
Type C is research-only.
Synthetic tests are research-only.
No Type C or synthetic result may be called official-valid.
```

Do not edit unless required and safe:

```text
configs/preserved_candidates/**
NLPCC_tasks/agent_platform/agents/build_agent.py
raw data
model binaries
official runtime evidence folders
```

If official runtime config changes by accident:

```text
revert it
record it
mark official_runtime_change_incident = true
```

---

## Stage 0 — Create Prompt02 Phase Folder

Create exactly:

```text
outputs/reports/focused_candidate_optimisation/prompt02_optimizer_synthetic_typec/presented/
outputs/reports/focused_candidate_optimisation/prompt02_optimizer_synthetic_typec/reference/
outputs/reports/focused_candidate_optimisation/prompt02_optimizer_synthetic_typec/progress/
outputs/reports/focused_candidate_optimisation/prompt02_optimizer_synthetic_typec/logs/
outputs/reports/focused_candidate_optimisation/prompt02_optimizer_synthetic_typec/traces/
outputs/reports/focused_candidate_optimisation/prompt02_optimizer_synthetic_typec/synthetic/
outputs/reports/focused_candidate_optimisation/prompt02_optimizer_synthetic_typec/optimiser/
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
```

---

## Stage 0A — RTK Preflight and Repo Safety Snapshot

Run:

```bash
rtk --version
rtk git status
rtk git diff --name-only
rtk git ls-files | grep -i "agents.md\\|agent.md\\|AGENTS.md\\|CLAUDE.md\\|codex"
```

Compute hashes for no-touch paths if present:

```text
configs/preserved_candidates/**
NLPCC_tasks/agent_platform/agents/build_agent.py
```

Create:

```text
reference/preflight_checks.csv
reference/preflight_git_status.txt
reference/preflight_git_diff_name_only.txt
reference/no_touch_file_hashes_before.csv
presented/preflight_summary.md
```

If `rtk --version` fails:

```text
status = blocked_rtk_unavailable
stop before repo changes except phase folder and preflight note
final response must say blocked_rtk_unavailable
```

---

## Stage 0B — Update AGENTS.md for Prompt02

Update root `AGENTS.md`.

Do not overwrite unrelated rules.

Add or update section:

```text
Focused Candidate Optimisation — Prompt02 Rules
```

Required section content:

```text
Current prompt:
  Prompt02 — Hyperparameter Optimiser, Synthetic Backtester, and Type-C Robustness Study

Output folder:
  outputs/reports/focused_candidate_optimisation/prompt02_optimizer_synthetic_typec/

Must use:
  rtk
  rtk python
  rtk git
  rtk python -m pytest

Validation:
  Type A = 2024 direct
  Type B = 2024 tune then frozen 2025
  Type C = merged 2024/2025 80/20 5-round research-only test

Do not:
  run hidden 2026
  run official-server parity
  promote official runtime
  write Prompt02 outputs outside Prompt02 folder
  download new models
  call online APIs

Must do:
  build bounded optimiser
  build synthetic input backtester
  fix compileall and pip check if possible
  write full implementation log
```

Create:

```text
reference/agents_md_update_manifest.csv
presented/agents_md_update_summary.md
```

Include before/after hashes.

---

## Stage 1 — Input Evidence Intake

Read current repo state and prior Prompt01 outputs.

Create:

```text
reference/input_evidence_manifest.csv
reference/prompt01_audit_gap_table.csv
reference/candidate_start_state.csv
presented/current_state_intake_summary.md
```

`prompt01_audit_gap_table.csv` must include:

```text
gap
severity
source
needed_fix
prompt02_stage
```

Minimum gaps to include:

```text
compileall failed
pip check failed
G15B fixed but underperforms no-news
Track A overlays proven but underperform no-news
G21B repaired_lite local full run complete but weak
no cache-hit proof
no official parity requested
```

---

## Stage 2 — Fix Package and Repo Hygiene First

Before optimiser work, fix hygiene issues if possible.

### Required fixes / checks

1. Inspect `compileall` failure log from Prompt01 if present.
2. Re-run compileall.
3. Fix compile/syntax/import issues if safe.
4. Inspect `pip check` failure log from Prompt01 if present.
5. Re-run pip check.
6. Fix dependency metadata issues if safe and bounded.
7. Do not install new heavy packages unless already declared or clearly safe.
8. If impossible, record exact blocker.

Commands:

```bash
rtk python -m compileall src tests
rtk python -m pip check
```

Create:

```text
reference/package_hygiene_fix_actions.csv
reference/package_hygiene_checks.csv
presented/package_hygiene_summary.md
logs/compileall_before_or_recheck.log
logs/pip_check_before_or_recheck.log
```

`package_hygiene_fix_actions.csv` columns:

```text
issue
source_log
root_cause
file_changed
fix_action
status
notes
```

Do not continue to claim package readiness unless both pass.

---

## Stage 3 — Build Bounded Hyperparameter Optimiser

Build or extend optimiser under existing project style.

Preferred location:

```text
src/nlpcc/news_overlay/optimisation/
```

Suggested files:

```text
src/nlpcc/news_overlay/optimisation/__init__.py
src/nlpcc/news_overlay/optimisation/search_space.py
src/nlpcc/news_overlay/optimisation/typec_splitter.py
src/nlpcc/news_overlay/optimisation/study_runner.py
src/nlpcc/news_overlay/optimisation/scoring.py
```

Script:

```text
scripts/run_prompt02_optimizer_synthetic_typec.py
```

### Optimiser method

Use bounded optimiser.

If `optuna` is already installed and legal in repo:

```text
Use Optuna TPE sampler.
```

If `optuna` not installed:

```text
Do not install unless safe.
Use deterministic random search + local refinement fallback.
Record optimiser_backend = random_search_fallback.
```

No online services.

No GPU requirement.

### Search objective

Use a conservative robust score, not raw Sharpe only.

Example score:

```text
score =
  mean_test_sharpe
  - 0.40 * std_test_sharpe
  - 0.25 * max_drawdown_penalty
  - 0.15 * turnover_penalty
  - 0.20 * no_news_underperformance_penalty
  - 0.10 * instability_penalty
```

Record exact formula in:

```text
reference/optimiser_scoring_formula.md
```

### Search spaces

Keep search spaces narrow and safe.

For all news candidates:

```text
overlay_scale
gate_threshold
deadband
confidence_cap
turnover_penalty_weight
fallback_threshold
max_abs_overlay
```

For G15B:

```text
n4_relevance_floor
n4_label_smoothing
i6_aspect_weight
s2_sector_shrink
h1_hook_strength
h5_hook_strength
```

For G21B repaired_lite:

```text
consensus_shrink
dominance_cap
bl_confidence_cap
event_count_floor
weak_signal_deadband
safe_fallback_weight
```

For Track A:

```text
macro_overlay_scale
h4_strength
composite_shrink
aspect_tone_weight
signal_deadband
```

Do not expand to new architectures.

### Required outputs

```text
optimiser/search_space.yaml
optimiser/optimiser_config.yaml
optimiser/optimiser_trials.csv
optimiser/optimiser_best_configs.csv
optimiser/optimiser_study_summary.md
reference/optimiser_backend_status.csv
reference/optimiser_scoring_formula.md
```

---

## Stage 4 — Build Synthetic Data Input Backtester

Build a synthetic input backtester for stress tests only.

Preferred location:

```text
src/nlpcc/news_overlay/synthetic/
```

Suggested files:

```text
src/nlpcc/news_overlay/synthetic/__init__.py
src/nlpcc/news_overlay/synthetic/generator.py
src/nlpcc/news_overlay/synthetic/scenarios.py
src/nlpcc/news_overlay/synthetic/backtester.py
src/nlpcc/news_overlay/synthetic/validators.py
```

### Synthetic scenarios

Generate bounded synthetic variants from public 2024/2025 only.

Do not use hidden 2026.

Suggested scenarios:

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

Each synthetic dataset must have:

```text
source_years
random_seed
scenario_name
date_range
rows
assets
news_count_before
news_count_after
price_count_before
price_count_after
leakage_checks_passed
```

Synthetic tests are research-only.

Required outputs:

```text
synthetic/synthetic_scenario_config.yaml
synthetic/synthetic_dataset_manifest.csv
synthetic/synthetic_validation_checks.csv
synthetic/synthetic_backtest_results.csv
presented/synthetic_backtester_summary.md
```

---

## Stage 5 — Build Type-C Splitter and Merged 2-Year Backtester

Merge 2024 and 2025 public data into a two-year public dataset.

Do not mutate raw data.

Create derived data under Prompt02 folder only, or use in-memory views.

### Type-C split rule

Make 5 folds.

Preferred:

```text
blocked time-series 80/20 split
```

Each fold:

```text
train = 80% of dates
test = 20% of dates
no same-day future leakage
news cutoff preserved
record train/test date ranges
```

Acceptable split designs:

```text
rolling blocked folds
anchored expanding folds
purged blocked folds
```

Do not use pure random day split unless also clearly marked:

```text
stress_random_split_not_time_valid
```

Required outputs:

```text
reference/typec_split_manifest.csv
reference/typec_leakage_checks.csv
traces/typec_fold_<fold_id>_daily_results.csv
presented/typec_split_summary.md
```

`typec_split_manifest.csv` columns:

```text
fold_id
split_method
train_start
train_end
test_start
test_end
train_days
test_days
train_pct
test_pct
purge_gap_days
leakage_check_status
notes
```

---

## Stage 6 — Run Type A, Type B, and Type C Experiments

Run bounded experiments for:

```text
A1 G12A V3
A2 G11A V0
A0 G00A
B1 G15B V0
B2 G15B V4
B3 G21B repaired_lite
B0 G00B
optional G14B V4
optional G10B V5
```

### Type A

Run direct 2024.

Output:

```text
reference/typea_2024_direct_results.csv
```

### Type B

Run 2024 tune/select and frozen 2025 test.

Use original Prompt01 fixed configs as baseline.

Use optimiser best configs only if chosen from 2024.

Output:

```text
reference/typeb_2024_tune_2025_frozen_results.csv
```

### Type C

Run merged 2024/2025 80/20 5-round test.

Tune on each fold train set.

Test on fold holdout.

Output:

```text
reference/typec_5round_results.csv
reference/typec_5round_rank_stability.csv
reference/typec_5round_fold_metrics.csv
```

For each trial/fold/candidate, record:

```text
candidate_id
candidate
variant
fold_id
validation_type
train_start
train_end
test_start
test_end
params_hash
return
sharpe
max_drawdown
turnover
mean_abs_overlay
overlay_contribution_nonzero
delta_vs_no_news_sharpe
robust_score
rank_in_fold
notes
```

---

## Stage 7 — Minor Enhancements Only

Based on optimiser and synthetic findings, implement only minor safe enhancements.

Allowed examples:

```text
stronger overlay shrink
weak-signal deadband
turnover-aware overlay cap
fallback to no-news if overlay confidence low
rank stability penalty
event-count floor
clip extreme overlay on high-vol days
```

Not allowed:

```text
new model family
new transformer download
new LLM API
new broad search over all methods
new official runtime promotion
hidden 2026 usage
```

Each enhancement must have:

```text
reason
file changed
parameter changed
before result
after result
risk
rollback path
```

Required outputs:

```text
reference/minor_enhancement_actions.csv
reference/minor_enhancement_before_after.csv
presented/minor_enhancement_summary.md
```

---

## Stage 8 — Cache-Hit and Reproducibility Check

Run one repeated experiment subset to prove cache behavior.

Minimum:

```text
repeat best Type-C fold for best Track A candidate
repeat best Type-C fold for best Track B candidate
```

Record:

```text
cache files before
cache files after
cache hits
cache misses
duration first
duration second
same metrics
```

Required outputs:

```text
reference/cache_hit_replay_summary.csv
presented/cache_reproducibility_summary.md
```

If cache-hit tracking is not implemented:

```text
mark cache_hit_tracking_missing
do not claim cache reuse
```

---

## Stage 9 — Tests and Checks

Run:

```bash
rtk --version
rtk git status
rtk git diff --name-only
rtk python -m pytest tests/test_nlpcc/test_news_overlay -q
rtk python -m pytest tests/test_nlpcc -q
rtk python -m pytest tests -q
rtk python -m compileall src tests
rtk python -m pip check
```

Add targeted tests for new optimiser/synthetic/type-C modules.

Expected test files:

```text
tests/test_nlpcc/test_news_overlay/test_prompt02_optimiser.py
tests/test_nlpcc/test_news_overlay/test_prompt02_synthetic.py
tests/test_nlpcc/test_news_overlay/test_prompt02_typec_splitter.py
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

If a command fails:

```text
do not hide it
record exact failure
summarise root cause
mark readiness accordingly
```

---

## Stage 10 — Final Robustness Synthesis

Create:

```text
reference/final_typeabc_synthesis_table.csv
reference/final_candidate_decision_table.csv
presented/final_typeabc_synthesis_summary.md
presented/final_candidate_decision_summary.md
presented/final_next_phase_recommendation.md
```

`final_typeabc_synthesis_table.csv` columns:

```text
candidate_id
track
candidate
variant
typea_2024_sharpe
typeb_2025_frozen_sharpe
typec_mean_sharpe
typec_std_sharpe
typec_worst_fold_sharpe
typec_mean_rank
typec_rank_std
synthetic_mean_sharpe
synthetic_worst_scenario_sharpe
overlay_contribution_nonzero
beats_no_news_typeb
beats_no_news_typec_mean
robust_score
research_only_typec_used
final_status
decision
reason
```

Allowed final statuses:

```text
active_next_phase
active_branch_selected_research_only
active_but_needs_more_evidence
baseline_reference_only
archived_fallback
retired_ablation_reference
blocked_package_hygiene
blocked_pipeline_noop
blocked_full_run_failed
```

Do not mark official-promotion-ready.

---

## Stage 11 — Detailed Implementation Log

This is mandatory.

Write detailed logs in two places:

```text
outputs/reports/focused_candidate_optimisation/prompt02_optimizer_synthetic_typec/presented/implementation_log.md
docs/implementation_logs/<timestamp>_prompt02_optimizer_synthetic_typec.md
```

The logs must include exactly these sections:

```text
A. Summary
B. Files Created
C. Files Modified
D. Files Read
E. Commands Run
F. Optimiser Built
G. Synthetic Backtester Built
H. Type-C Splitter Built
I. Candidate Runs Completed
J. Minor Enhancements Implemented
K. Tests Added or Updated
L. Tests Run
M. Failed / Blocked Runs
N. Package Hygiene Status
O. Official Runtime Config Status
P. 2025 Tune / Type-C Research-Only Check
Q. Hidden 2026 Check
R. Cache / Reproducibility Status
S. Artifacts
T. Caveats
U. Next Steps
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

Do not write “Artifacts: None” if artifacts exist.

---

## Final Response Format

Use caveman English.

```text
Prompt02 status:
  <pass/partial/fail/blocked>

Phase folder:
  outputs/reports/focused_candidate_optimisation/prompt02_optimizer_synthetic_typec/

RTK used?
  <yes/no>

AGENTS.md updated?
  <yes/no/created/blocked>
  evidence:
    <paths>

Package hygiene:
  compileall:
    <pass/fail/not_run>
  pip check:
    <pass/fail/not_run>

Optimiser:
  built:
    <yes/no>
  backend:
    <optuna/random_search_fallback/other>
  trials:
    <count>
  best candidates:
    <short list>

Synthetic backtester:
  built:
    <yes/no>
  scenarios:
    <count>
  status:
    <pass/partial/fail>

Type-C test:
  merged_2024_2025:
    <yes/no>
  split:
    <blocked/rolling/purged/anchored/random_stress>
  folds:
    <count>
  research_only:
    yes

Type A/B/C result:
  Track A:
    <short summary>
  Track B:
    <short summary>

Minor enhancements:
  <summary>

Full tests:
  tests/test_nlpcc/test_news_overlay:
    <pass/fail/not_run>
  tests/test_nlpcc:
    <pass/fail/not_run>
  tests:
    <pass/fail/not_run>

Official runtime changed?
  <yes/no>

Official parity run?
  no

Hidden 2026 used?
  <yes/no>

Main blockers:
  <list>

Main artifacts:
  <paths>

Readiness:
  <active_next_phase / partial_missing_evidence / blocked_package_hygiene / blocked_full_run_failed / not_ready_repo_state_unclear>

Best next action:
  <one specific action>
```
