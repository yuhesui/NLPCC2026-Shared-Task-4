# Prompt10a — Final Audit Repair for Prompt10 Incomplete Evidence

## Role

Act as a strict research-code auditor, final-candidate validation engineer, source-diff reviewer, and single-log evidence repair operator.

This is a **repair-only** phase. Do not add new modelling ideas. Do not retune candidates. Do not broaden the candidate set.

## Objective

Fix the incomplete Prompt10 evidence package so the final candidate decision is audit-grade.

Prompt10 already made this tentative decision:

```text
Track A: keep A0 + bounded A2_real overlay, with A0 as fallback.
Track B: keep B0 no-news base; keep B2_real as report-only/rejected ablation.
```

Your job is to verify, repair, and evidence this decision.

Beating no-news is **not** a strict guard, but every kept candidate must have clear evidence.

## Phase and Output Folder

Use exact phase name:

```text
Prompt10a — Final Candidate Evidence Repair
```

Output folder:

```text
outputs/reports/focused_candidate_optimisation/prompt10a_final_candidate_evidence_repair/
```

Required subfolders:

```text
presented/
presented/run_csv/
reference/
logs/
traces/
server_run/
code_audit/
tests/
report/
```

## One Implementation Log Only

Write exactly one log:

```text
outputs/reports/focused_candidate_optimisation/prompt10a_final_candidate_evidence_repair/presented/implementation_log.md
```

Do not create any other Prompt10a implementation log. If it exists, update it in place.

The log must state:

```text
implementation_log_count = 1
second_docs_log_written = false
duplicate_prompt10a_logs_created = false
```

## Hard Rules

```text
Use rtk, rtk python, rtk git.
No hidden 2026.
No online model/API inference.
No new model download.
No retuning.
No broad candidate search.
No stale summary reuse.
No proxy/fake news runs.
No final submission run.
```

Skip unless trivial:

```text
pip check
compileall
Docker build
LaTeX finalization
```

## Candidate Set

Only test and audit:

```text
Track A:
  A0
  A2_real

Track B:
  B0
  B2_real
```

## Required Fixes

### 1. Repair Prompt10 implementation log

Create a correct Prompt10a log and also produce:

```text
presented/prompt10_incomplete_gap_repair_summary.md
reference/prompt10_gap_repair_table.csv
```

The repair table must include:

```text
gap
Prompt10_status
Prompt10a_fix
artifact
status
```

Must cover:

```text
stale/mismatched Prompt10 implementation log
Prompt10 reused Prompt09 evidence
missing fresh final official-server/HTTP replay
thin intended-vs-actual source audit
thin history audit evidence
A2_real active-vs-shuffled margin tiny
missing final source/config audit
```

### 2. Fresh final official-server/platform replay

Run a fresh local official-server/platform replay for:

```text
A0
A2_real
B0
B2_real
```

Do not reuse Prompt09 rows as the final result.

Create:

```text
reference/final_official_server_replay_prompt10a.csv
reference/final_metric_comparison_prompt10a.csv
presented/run_csv/final_official_server_replay_prompt10a.csv
presented/run_csv/final_metric_comparison_prompt10a.csv
presented/final_official_server_replay_summary.md
traces/final_prompt10a_<track>_<candidate_id>_daily.csv
logs/final_prompt10a_<track>_<candidate_id>.log
```

Each row must include:

```text
track
candidate_id
candidate
date_start
date_end
return
sharpe
max_drawdown
turnover
mean_abs_overlay
overlay_nonzero_days
real_transformer_executed
proxy_mode
heuristic_fallback_used
fixed_target_replay_used
network_attempted
delta_vs_no_news_sharpe
actual_official_server_or_platform_run
fresh_prompt10a_run
official_submission_run
status
notes
```

### 3. Source/config intended-vs-actual audit

Create:

```text
code_audit/intended_vs_actual_method_table_prompt10a.csv
code_audit/final_candidate_source_map_prompt10a.csv
presented/code_vs_intended_method_summary_prompt10a.md
```

For A0, A2_real, B0, B2_real, compare:

```text
intended N/I/S stack
actual source files
actual functions/classes
official agent path
model assets used
news tensor provider
risk/overlay controls
proxy/fixed-target replay status
deviation severity
safe report claim
unsafe report claim
```

Clearly state whether A2_real and B2_real are full intended architectures or compact production implementations.

### 4. Focused A2_real robustness check

Run only a small robustness repair, not a new research sweep:

```text
A2_real active tensor
A2_real zeroed tensor
A2_real date-shuffled tensor with at least 5 shuffle seeds if runtime allows
```

Create:

```text
reference/a2_real_multishuffle_ablation_prompt10a.csv
presented/run_csv/a2_real_multishuffle_ablation_prompt10a.csv
presented/a2_real_robustness_summary_prompt10a.md
```

If runtime is limited, do at least 3 shuffle seeds and mark partial.

### 5. Final decision update

Create:

```text
reference/final_candidate_decision_table_prompt10a.csv
presented/run_csv/final_candidate_decision_table_prompt10a.csv
presented/final_candidate_decision_summary_prompt10a.md
presented/final_methodology_and_candidate_selection_report_prompt10a.md
presented/submission_gap_summary_prompt10a.md
```

Decision statuses:

```text
final_keep
fallback_keep
report_ablation
reject_for_submission
blocked_evidence_missing
```

Expected conservative framing:

```text
Track A:
  final_keep = A0 + bounded A2_real overlay only if fresh run and robustness remain acceptable;
  fallback_keep = A0.

Track B:
  final_keep = B0;
  B2_real = report_ablation or reject_for_submission unless new evidence fixes shuffled-news failure.
```

### 6. Tests

Run:

```bash
rtk python -m pytest tests/test_nlpcc/test_news_overlay -q
rtk python -m pytest tests/test_nlpcc -q
rtk python -m pytest tests -q
```

Run targeted tests if available:

```text
test_real_transformer_no_proxy
test_no_fixed_target_replay
test_final_candidate_server_path
```

Create:

```text
tests/test_results_summary_prompt10a.csv
presented/run_csv/test_results_summary_prompt10a.csv
presented/full_test_summary_prompt10a.md
```

## Presented CSV Package

Create:

```text
presented/run_csv_index.md
presented/run_csv_manifest.csv
```

Minimum CSVs:

```text
final_official_server_replay_prompt10a.csv
final_metric_comparison_prompt10a.csv
a2_real_multishuffle_ablation_prompt10a.csv
final_candidate_decision_table_prompt10a.csv
test_results_summary_prompt10a.csv
```

## Final Response Format

Use exactly:

```text
Prompt10a status:
  <pass/partial/fail/blocked>

Implementation log:
  <path>
  count: <1/other>

Fresh final official-server replay:
  status: <complete/partial/fail>
  rows: <n>
  csv: <path>

Final candidate decision:
  Track A:
    selected: <A0/A2_real/A0_plus_A2_real_overlay>
    fallback: <A0/A2_real/none>
    reason: <short>
  Track B:
    selected: <B0/B2_real/B0_plus_B2_real_overlay>
    fallback: <B0/B2_real/none>
    reason: <short>

A2_real multishuffle robustness:
  status: <pass/partial/fail/not_run>
  active beats shuffled mean: <yes/no/mixed>
  csv: <path>

Actual code vs intended method:
  status: <complete/partial/fail>
  report: <path>

Tests:
  pytest news_overlay: <pass/fail/not_run>
  pytest tests_nlpcc: <pass/fail/not_run>
  pytest full tests: <pass/fail/not_run>
  targeted tests: <pass/fail/not_run>

Official submission run?
  no

Hidden 2026 used?
  <yes/no>

Main remaining blockers:
  <list>

Best next action:
  <one action>
```
