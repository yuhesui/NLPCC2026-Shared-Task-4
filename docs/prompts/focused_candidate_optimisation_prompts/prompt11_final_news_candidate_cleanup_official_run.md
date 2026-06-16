# Prompt11 — Final News-Candidate Selection, Repo Cleanup, Official Run, and Methodology Report

## Role

Act as:

```text
senior research-code stabilisation engineer
official trading-agent integration engineer
Chinese financial NLP methodology writer
repo-cleanliness and submission-readiness auditor
real-transformer news-overlay engineer
single implementation-log writer
```

This is a **final news-candidate consolidation and cleanup phase**.

Do not reopen candidate selection.

The selected final news candidates are fixed for this phase:

```text
Track A selected candidate: A2_real / G11A real-transformer news overlay
Track B selected candidate: B2_real / G15B real-transformer news overlay
```

No-news baselines are **not allowed to be selected as final candidates** in this phase.

They may be used only as:

```text
benchmark
diagnostic reference
fallback safety comparison
ablation/control
```

Do not switch final selection back to A0/B0 because of public-validation metrics. The purpose is to make A2_real and B2_real clean, official-run capable, documented, and ready for next-phase fine-tuning experiments.

---

## Core Objective

Finish and clean the project around the selected real-transformer news candidates:

```text
A2_real for Track A
B2_real for Track B
```

You must:

```text
1. clean and stabilise the repo around A2_real/B2_real;
2. remove stale/fake/proxy/frozen-target pathways from the production candidate path;
3. run the official local server/platform path for A2_real and B2_real;
4. keep A0/B0 only as benchmark references, not selected candidates;
5. produce a full methodology report for A2_real and B2_real;
6. produce a source/config/hash audit;
7. run tests and final package sanity checks where feasible;
8. prepare a next-phase plan for experimenting with different fine-tuning methods.
```

This phase is not for broad method search or adding new candidate families.

---

## Phase

Use exact phase name:

```text
Prompt11 — Final News Candidate Cleanup and Official Run
```

Output folder:

```text
outputs/reports/focused_candidate_optimisation/prompt11_final_news_candidate_cleanup_official_run/
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
repo_cleanup/
configs/
tests/
report/
fine_tuning_plan/
```

All important CSVs must also be copied to:

```text
presented/run_csv/
```

---

## One Implementation Log Only

Write exactly one implementation log:

```text
outputs/reports/focused_candidate_optimisation/prompt11_final_news_candidate_cleanup_official_run/presented/implementation_log.md
```

Do not create any other Prompt11 implementation log.

The log must state:

```text
implementation_log_count = 1
second_docs_log_written = false
duplicate_prompt11_logs_created = false
```

---

## Hard Rules

```text
Use rtk, rtk python, rtk git.
No hidden 2026.
No online inference/API.
No new model download.
No remote official submission unless explicitly available and safe.
No broad 212-row matrix.
No new candidate family.
No proxy/fake news.
No heuristic news fallback in production path.
No fixed target replay as news.
No old research target-weight CSV replay as news.
No stale summary reuse.
```

Real-NLP production rules for A2_real/B2_real:

```text
real_transformer_executed = true
proxy_mode = false
heuristic_fallback_used = false
fixed_target_replay_used = false
network_attempted = false
local_files_only = true
```

No-news rule:

```text
A0/B0 must not be selected as final candidates.
A0/B0 may be used only as reference rows.
Final selected candidates must remain A2_real and B2_real.
```

---

## Candidate Set

Final selected candidates:

```text
Track A:
  A2_real = G11A real-transformer news overlay, compact production N13/I6/S13 implementation

Track B:
  B2_real = G15B real-transformer news overlay, compact production N4/I6/S2 implementation
```

Reference-only baselines:

```text
A0 = G00A no-news benchmark only
B0 = G00B no-news benchmark only
```

Do not retest A1/B3 unless needed only for historical report context. Do not select them.

---

## Stage 0 — Intake and Gap Confirmation

Read repo and previous output folders, especially:

```text
outputs/reports/focused_candidate_optimisation/prompt09_real_transformer_news_overlay/
outputs/reports/focused_candidate_optimisation/prompt10_final_candidate_methodology_audit/
outputs/reports/focused_candidate_optimisation/prompt10a_final_candidate_evidence_repair/
docs/news_overlay/**
NLPCC_tasks/**
src/**
tests/**
README.md
AGENTS.md
```

Create:

```text
reference/input_artifact_manifest_prompt11.csv
reference/prompt10a_gap_followup_table.csv
presented/input_state_summary_prompt11.md
```

Must explicitly check these known gaps:

```text
wrong/stale Prompt10a implementation log
HTTP/server parity not yet fully proven
source/config/hash audit incomplete
package/env cleanup incomplete
A2 active-vs-shuffled margin small
B2 previously failed shuffled-news ablation but is still selected by user instruction
methodology report needs final A2/B2-focused version
fine-tuning experiment plan missing
```

---

## Stage 1 — Repo Cleanup and Production Path Stabilisation

Clean the repo around A2_real/B2_real without deleting useful evidence.

Tasks:

```text
1. identify production candidate source files;
2. identify obsolete/proxy/fallback code paths;
3. isolate old experimental candidates from final production path;
4. ensure official adapter loads A2_real/B2_real configs cleanly;
5. ensure A0/B0 remain available only as reference;
6. ensure production mode blocks proxy/fallback/fixed replay;
7. remove stale generated files only if safe, otherwise quarantine/list them;
8. update README/AGENTS or final docs with clear final candidate paths.
```

Create:

```text
repo_cleanup/repo_cleanup_manifest.csv
repo_cleanup/stale_or_quarantined_artifacts.csv
repo_cleanup/final_candidate_file_map.csv
presented/repo_cleanup_summary.md
```

`repo_cleanup_manifest.csv` columns:

```text
path
action
reason
safe_to_delete
deleted_or_quarantined
kept_for_evidence
candidate_affected
notes
```

Do not delete evidence unless clearly safe. Prefer quarantine or manifest.

---

## Stage 2 — Source / Config / Hash Audit

Create a complete audit for A2_real and B2_real.

Required outputs:

```text
code_audit/final_news_candidate_source_map.csv
code_audit/final_news_candidate_config_audit.csv
code_audit/final_news_candidate_hash_manifest.csv
code_audit/no_proxy_production_path_audit.csv
presented/source_config_hash_audit_summary.md
```

For each selected candidate, include:

```text
track
candidate_id
official_agent_path
config_path
model_paths
tensor_provider_path
overlay_source_path
risk_control_source_path
server_entrypoint
source_sha256
config_sha256
uses_real_transformer
proxy_forbidden
fixed_replay_forbidden
local_files_only
network_attempted
deviation_from_intended_architecture
safe_report_claim
unsafe_report_claim
```

State clearly:

```text
A2_real and B2_real are compact production real-transformer tensor implementations.
Do not claim full original N/I/S research architecture is exactly implemented unless source proves it.
```

---

## Stage 3 — Official Local Server / HTTP Parity Run

Run official local server/platform path for:

```text
A2_real
B2_real
```

Also run A0/B0 only as reference rows:

```text
A0 reference only
B0 reference only
```

Prefer strict HTTP/server path if available:

```text
start_server.py
server_platform API
agent_platform adapter
HTTP backtest endpoint
```

If strict HTTP path is impossible, run closest official local server/platform path and mark why.

Required outputs:

```text
server_run/official_http_or_server_run_manifest.csv
server_run/official_run_command_log.md
reference/final_news_candidates_official_run_prompt11.csv
reference/final_news_candidates_metric_comparison_prompt11.csv
presented/run_csv/final_news_candidates_official_run_prompt11.csv
presented/run_csv/final_news_candidates_metric_comparison_prompt11.csv
presented/final_news_candidates_official_run_summary.md
traces/prompt11_<track>_<candidate_id>_daily.csv
logs/prompt11_<track>_<candidate_id>.log
```

Each result row must include:

```text
track
candidate_id
candidate
role
selected_final_candidate
server_entrypoint
official_agent_path
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
local_files_only
actual_official_server_or_platform_run
strict_http_path_used
fresh_prompt11_run
official_submission_run
delta_vs_reference_no_news_sharpe
status
notes
```

Important:

```text
A2_real and B2_real must have selected_final_candidate = true.
A0/B0 must have selected_final_candidate = false and role = reference_only.
```

---

## Stage 4 — Final A2/B2 Methodology Report

Write a full methodology report focused on A2_real and B2_real:

```text
presented/final_A2_B2_methodology_report_prompt11.md
```

Required sections:

```text
1. Executive Summary
2. Final Candidate Policy
3. Why No-News Is Reference-Only in This Phase
4. Track A Final Method: A2_real / G11A
5. Track B Final Method: B2_real / G15B
6. Data Flow and Official Agent Integration
7. Real Transformer News Tensor Construction
8. Local Model Assets and No-Proxy Policy
9. Portfolio Overlay and Risk Controls
10. Intended Architecture vs Actual Code
11. Official Local Server Results
12. Ablations and Known Weaknesses
13. Why A2_real Is Kept
14. Why B2_real Is Kept Despite Weaknesses
15. Claims Allowed in System Report
16. Claims Not Allowed
17. Remaining Submission Cleanup
18. Next-Phase Fine-Tuning Experiment Plan
```

The report must be honest:

```text
No-news baselines were stronger or safer in some metrics, but are not selected by user policy.
B2_real has known weakness from shuffled-news ablation.
A2_real has small active-vs-shuffled margin.
A2/B2 are selected for real-transformer methodology, interpretability, and final news-agent focus, not because no-news is always worse.
```

---

## Stage 5 — Prepare Next-Phase Fine-Tuning Experiment Plan

Do not execute fine-tuning in this phase.

Prepare a clear next-phase plan for different fine-tuning methods.

Create:

```text
fine_tuning_plan/next_phase_fine_tuning_plan.md
fine_tuning_plan/fine_tuning_method_table.csv
fine_tuning_plan/experiment_grid_seed_prompt.md
presented/fine_tuning_plan_summary.md
```

Methods to compare:

```text
1. frozen encoder + calibrated logistic/regression head;
2. LoRA / parameter-efficient fine-tuning for FinBERT tone/aspect head;
3. contrastive asset-news relevance fine-tuning for BGE embeddings;
4. event-label weak supervision / pseudo-label fine-tuning for N4;
5. pairwise ranking / cross-encoder reranker fine-tuning if local model exists;
6. temporal contrastive fine-tuning on news-to-next-return sign buckets;
7. calibration-only temperature scaling / isotonic calibration;
8. no-training hyperparameter-only control.
```

For each method include:

```text
objective
labels needed
data window
leakage risk
compute cost
expected benefit
risk
validation protocol
stop rule
```

Validation protocol must avoid hidden 2026 and avoid overfitting 2025 full public test.

---

## Stage 6 — Tests and Sanity Checks

Run:

```bash
rtk python -m pytest tests/test_nlpcc/test_news_overlay -q
rtk python -m pytest tests/test_nlpcc -q
rtk python -m pytest tests -q
```

Also run targeted tests if present or cheap to add:

```text
test_final_news_candidate_selection_policy
test_a2_b2_official_agent_path
test_no_news_not_selected
test_real_transformer_no_proxy
test_no_fixed_target_replay
test_official_http_or_server_run
```

Because this is a cleanup phase, also run if feasible:

```bash
rtk python -m compileall src NLPCC_tasks tests
```

Run `pip check` only if cheap; if it fails because of known environment conflicts, mark `environment_blocked`, not a candidate blocker.

Create:

```text
tests/test_results_summary_prompt11.csv
presented/run_csv/test_results_summary_prompt11.csv
presented/full_test_summary_prompt11.md
logs/prompt11_tests.log
logs/prompt11_compileall.log
logs/prompt11_pip_check.log
```

---

## Stage 7 — Final Decision and Submission Gap Summary

Create:

```text
reference/final_selected_news_candidate_decision_prompt11.csv
presented/run_csv/final_selected_news_candidate_decision_prompt11.csv
presented/final_selected_news_candidate_summary_prompt11.md
presented/submission_gap_summary_prompt11.md
presented/final_next_phase_recommendation_prompt11.md
```

Decision table columns:

```text
track
selected_candidate
reference_candidate
official_run_status
strict_http_path_used
real_transformer_status
proxy_status
return
sharpe
max_drawdown
turnover
delta_vs_reference_no_news_sharpe
known_weakness
why_selected
next_phase_need
final_status
```

Allowed final statuses:

```text
selected_news_candidate
selected_with_caveat
reference_only_not_selected
blocked_official_run
blocked_real_transformer_path
blocked_tests
```

Do not use:

```text
submission_ready
top3_ready
official_hidden_ready
```

unless final official submission/package checks are complete.

---

## Stage 8 — Presented CSV Package

Create:

```text
presented/run_csv_index.md
presented/run_csv_manifest.csv
```

Minimum CSVs in `presented/run_csv/`:

```text
final_news_candidates_official_run_prompt11.csv
final_news_candidates_metric_comparison_prompt11.csv
final_selected_news_candidate_decision_prompt11.csv
test_results_summary_prompt11.csv
```

Manifest columns:

```text
csv_path
row_count
candidate_ids
tracks
selected_final_candidate_rows
reference_only_rows
actual_run
official_server_or_platform_run
strict_http_path_used
real_transformer_executed
proxy_run
why_it_matters
```

---

## Final Response Format

Use exactly:

```text
Prompt11 status:
  <pass/partial/fail/blocked>

Implementation log:
  <path>
  count: <1/other>

Final selected candidates:
  Track A:
    selected: A2_real
    reference only: A0
  Track B:
    selected: B2_real
    reference only: B0

Repo cleanup:
  status: <complete/partial/fail>
  summary: <path>

Official local server / HTTP run:
  status: <complete/partial/fail/blocked>
  strict HTTP path used: <yes/no>
  rows: <n>
  csv: <path>

Source/config/hash audit:
  status: <complete/partial/fail>
  summary: <path>

Methodology report:
  path: presented/final_A2_B2_methodology_report_prompt11.md

Fine-tuning next-phase plan:
  path: <path>

Tests:
  pytest news_overlay: <pass/fail/not_run>
  pytest tests_nlpcc: <pass/fail/not_run>
  pytest full tests: <pass/fail/not_run>
  compileall: <pass/fail/not_run>
  pip check: <pass/fail/environment_blocked/not_run>

Official submission run?
  no

Hidden 2026 used?
  <yes/no>

Main caveats:
  <list>

Best next action:
  <one action>
```
