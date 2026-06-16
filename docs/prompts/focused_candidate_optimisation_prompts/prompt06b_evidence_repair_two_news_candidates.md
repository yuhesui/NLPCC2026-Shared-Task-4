## Your Role

You are GPT-5.5 Extended Thinking acting as:

```text
senior quantitative research engineer
official-runner local replay engineer
Chinese financial NLP pipeline engineer
evidence-package repair auditor
NLPCC LNCS report-prep reviewer
single implementation-log writer
```

Your job is to finish the incomplete Prompt06 items with **real evidence**, not broad new research.

Focus on:

```text
1. two news candidates per track;
2. official-facing local replay;
3. actual run CSVs placed in presented/ for analysis;
4. correct Prompt06b implementation log and checks;
5. report draft compile/page-readiness evidence.
```

Do not write long generic summaries. Every important claim must point to an actual CSV, log, or TeX file.

---

## Phase

```text
Prompt06b — Evidence Repair, Two-News-Candidate Replay, and Report Readiness
```

Output folder:

```text
outputs/reports/focused_candidate_optimisation/prompt06b_evidence_repair_two_news_candidates/
```

Required subfolders:

```text
presented/
presented/run_csv/
reference/
logs/
traces/
runner_port/
report/
```

`presented/run_csv/` is mandatory. It must contain copies of the important run CSVs, not only short markdown summaries.

---

## One Implementation Log Only

Write exactly one Prompt06b implementation log:

```text
outputs/reports/focused_candidate_optimisation/prompt06b_evidence_repair_two_news_candidates/presented/implementation_log.md
```

Do not write `docs/implementation_logs/` copy.  
Do not create duplicate Prompt06b logs.  
If edits continue within Prompt06b, update this same file.

The log must state:

```text
implementation_log_count = 1
second_docs_log_written = false
duplicate_prompt06b_logs_created = false
```

---

## Hard Rules

```text
Use rtk, rtk python, rtk git, rtk python -m pytest.
Use project .venv RTK Python.
No hidden 2026.
No online API for model inference.
No new model download.
No official-server submission.
No official runtime promotion.
Do not delete prior evidence.
Do not call a proxy run actual.
Do not reuse Prompt06 tables as fresh Prompt06b runs unless marked carried_forward.
```

Package checks:

```text
Run tests and compileall.
Run pip check; if it fails from known environment conflicts, record environment_blocked and continue.
Do not make pip check the main task.
```

---

## Candidate Pool

Use exactly two news candidates per track.

### Track A

```text
A0 G00A no-news reference
A2 G11A V0 primary news candidate
A1 G12A V3 secondary news candidate
```

### Track B

```text
B0 G00B no-news reference
B2 G15B V4 primary news candidate
B3 G21B repaired_lite secondary news candidate
```

Do not add B1 unless a run fails and you need an emergency fallback.  
Do not run the old full 212-row matrix.

---

## Stage 1 — Read Previous Prompt06 State

Read Prompt06 outputs if present:

```text
prompt06_tuning_official_runner_report/**
final_next_phase_recommendation.md
official_runner_replay_summary.md
official_runner_replay_metric_comparison.csv
final_prompt06_decision_table.csv
final_prompt06_candidate_synthesis.csv
typed_same_window_*.csv
system_report_track_a_2page.tex
system_report_track_b_2page.tex
```

Create:

```text
reference/input_evidence_manifest.csv
reference/prompt06_gap_table.csv
presented/prompt06_gap_summary.md
```

`prompt06_gap_table.csv` must include at least:

```text
wrong_or_missing_prompt06_implementation_log
wrong_or_stale_full_checks_summary
official_adapter_source_not_audited
runner_logs_not_uploaded
run_csvs_not_visible_enough_in_presented
system_report_not_compile_checked
system_report_page_count_not_checked
official_server_not_run
news_candidates_trail_no_news_reference
```

---

## Stage 2 — Repair Evidence Packaging

This stage is mandatory.

Copy or regenerate all important run CSVs into:

```text
presented/run_csv/
```

Required files in `presented/run_csv/`:

```text
official_runner_replay_metric_comparison.csv
final_prompt06_decision_table.csv
final_prompt06_candidate_synthesis.csv
typed_same_window_d1_h2_results.csv
typed_same_window_d2_h2_results.csv
typed_same_window_more_data_comparison.csv
```

Also put fresh Prompt06b run CSVs there after Stage 4.

For each CSV copied or generated, create a short paired markdown index:

```text
presented/run_csv_index.md
```

Index columns:

```text
csv_path
row_count
candidate_ids
date_range
actual_run
proxy_run
why_it_matters
```

Do not upload only shallow markdown summaries. The actual CSVs must be visible under `presented/run_csv/`.

---

## Stage 3 — Official Adapter Source and Runner Location Audit

Find and inspect official-facing agent files:

```text
NLPCC_tasks/agent_platform/agents/
NLPCC_tasks/agent_platform/demo_backtest.py
NLPCC_tasks/server_platform/
runner/
runners/
```

Audit whether the Prompt06 adapter exists, and whether default official runtime files were changed.

Create:

```text
runner_port/official_runner_location_audit.csv
runner_port/official_adapter_source_audit.csv
runner_port/official_adapter_diff_summary.md
presented/official_adapter_audit_summary.md
```

If the adapter file exists, record:

```text
path
sha256
imports
candidate_ids_supported
tracks_supported
uses_hidden_2026
uses_online_api
modifies_default_build_agent
rollback_path
```

If the adapter is missing, mark:

```text
blocked_official_adapter_missing
```

---

## Stage 4 — Fresh Official-Facing Local Replay

Run fresh official-facing local replay for all six candidates:

```text
A0, A2, A1
B0, B2, B3
```

Use the official-facing local runner / adapter path, not only internal research backtester.

Run on:

```text
2025 public local replay
same date range for candidates within same track
frozen configs
```

Required outputs:

```text
reference/official_runner_replay_results_prompt06b.csv
reference/official_runner_replay_metric_comparison_prompt06b.csv
presented/run_csv/official_runner_replay_results_prompt06b.csv
presented/run_csv/official_runner_replay_metric_comparison_prompt06b.csv
presented/official_runner_replay_summary.md
traces/official_runner_<track>_<candidate_id>_daily.csv
logs/official_runner_<track>_<candidate_id>.log
```

Each row must include:

```text
track
candidate_id
candidate
runner_path
config_hash
date_start
date_end
return
sharpe
max_drawdown
turnover
mean_abs_overlay
overlay_nonzero
delta_vs_no_news_sharpe
actual_official_runner_replay
proxy_run
official_server_run
official_valid
notes
```

Required labels:

```text
actual_official_runner_replay = true only if official-facing local runner / adapter path was used
proxy_run = false for actual runs
official_server_run = false
official_valid = local_public_validation_only
```

If replay fails for a candidate, keep the row with:

```text
status = failed
error_log_path
```

---

## Stage 5 — Same-Window Type-D Evidence Repair for Two News Candidates Per Track

If previous same-window Type-D CSVs only include A0/A2/B0/B2, extend them to include A1 and B3.

Run or carry forward with clear labels:

```text
D1-H2:
  train/tune = 2024 only
  test = later-half 2025

D2-H2:
  train/tune = 2024 + first-half 2025
  test = same later-half 2025
```

Required outputs:

```text
reference/typed_same_window_d1_h2_results_prompt06b.csv
reference/typed_same_window_d2_h2_results_prompt06b.csv
reference/typed_same_window_more_data_comparison_prompt06b.csv
presented/run_csv/typed_same_window_d1_h2_results_prompt06b.csv
presented/run_csv/typed_same_window_d2_h2_results_prompt06b.csv
presented/run_csv/typed_same_window_more_data_comparison_prompt06b.csv
presented/typed_same_window_summary.md
```

Each comparison row must include:

```text
candidate_id
track
d1_h2_sharpe
d2_h2_sharpe
d2_minus_d1_h2_sharpe
d1_h2_return
d2_h2_return
d2_minus_d1_h2_return
more_data_helped_sharpe
more_data_helped_return
actual_run
carried_forward
proxy_run
official_valid
research_only
interpretation
```

---

## Stage 6 — System Report Readiness Check

Use official template files from:

```text
docs/NLPCC2026 - Template/
```

Check:

```text
system_report_track_a_2page.tex
system_report_track_b_2page.tex
system_report_combined_short.tex if present
```

Try to compile Track A and Track B drafts if LaTeX tools are available.

If LaTeX tools are not available, still run a structural check:

```text
uses llncs class
has title
has abstract
has architecture/method section
has experiment/results section
has reflection/future work
has no hidden 2026 claim
has no official result claim
mentions local public validation only
intended page_count <= 2
```

Create:

```text
report/system_report_readiness_check.csv
report/system_report_compile_or_structure_log.md
presented/system_report_readiness_summary.md
```

Do not claim page-count pass unless a PDF compile/page-count check actually passed.

---

## Stage 7 — Correct Prompt06b Checks

Run:

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

Write Prompt06b-specific checks only:

```text
reference/full_checks_summary_prompt06b.csv
presented/full_test_summary.md
logs/news_overlay_pytest.log
logs/full_pytest_tests_nlpcc.log
logs/full_pytest_tests.log
logs/compileall_src_tests.log
logs/pip_check.log
```

Do not reuse Prompt01 / Prompt05 check CSVs as Prompt06b evidence.

---

## Stage 8 — Final Decision and Submission Gap Summary

Create:

```text
reference/final_prompt06b_decision_table.csv
presented/run_csv/final_prompt06b_decision_table.csv
presented/final_candidate_decision_summary.md
presented/submission_gap_summary.md
presented/final_next_phase_recommendation.md
```

Final decision table columns:

```text
track
candidate_id
candidate
role
official_runner_replay_status
official_runner_sharpe
delta_vs_no_news_sharpe
same_window_typed_status
more_data_helped
report_status
test_status
official_runtime_changed
official_server_run
final_status
decision
next_action
```

Allowed statuses:

```text
no_news_reference
official_runner_candidate
research_news_candidate
regime_or_ensemble_candidate
report_only_ablation
blocked_official_adapter_missing
blocked_runner_replay_failed
blocked_evidence_missing
```

Do not use:

```text
official_promotion_ready
official_parity_ready
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
F. Prompt06 Gap Repair
G. Presented CSV Evidence Package
H. Official Adapter Audit
I. Fresh Official-Facing Replay
J. Same-Window Type-D Repair
K. System Report Readiness Check
L. Tests and Package Checks
M. Failed or Blocked Runs
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
Prompt06b status:
  <pass/partial/fail/blocked>

Implementation log:
  <path>
  count: <1/other>

Presented run CSVs:
  status: <complete/partial/fail>
  folder: presented/run_csv/
  files:
    <list>

Official adapter audit:
  status: <pass/partial/fail/blocked>
  adapter path: <path>

Fresh official-facing replay:
  status: <complete/partial/fail/blocked>
  candidates: <list>
  rows: <n>
  csv: <path>

Two news candidates per track:
  Track A:
    <A2 and A1 status>
  Track B:
    <B2 and B3 status>

Same-window Type-D:
  status: <complete/partial/fail>
  csv: <path>

System report readiness:
  Track A: <pass/partial/fail>
  Track B: <pass/partial/fail>

Tests:
  pytest news_overlay: <pass/fail/not_run>
  pytest tests_nlpcc: <pass/fail/not_run>
  pytest full tests: <pass/fail/not_run>
  compileall: <pass/fail/not_run>
  pip check: <pass/fail/environment_blocked/not_run>

Official runtime changed?
  no

Official server run?
  no

Hidden 2026 used?
  <yes/no>

Main caveats:
  <list>

Best next action:
  <one action>
```
