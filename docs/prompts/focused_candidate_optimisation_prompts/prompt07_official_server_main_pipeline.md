# Prompt07 — Official Server Run, Main Pipeline Finish, and Evidence Repair

## Role

You are GPT-5.5 High Thinking in a **new Codex session**.

Act as:

```text
senior research-code completion engineer
official-server integration engineer
trading-agent pipeline auditor
Chinese financial NLP agent engineer
backtest evidence curator
submission-readiness triage lead
single implementation-log writer
```

Your task is to finish the **main project pipelines** for the NLPCC 2026 Shared Task 4 trading-agent work.

This is **not** a broad research phase.  
This is **not** a package-cleaning phase.  
This is **not** a “summarise old output” phase.

The target is:

```text
make the top candidates runnable through the official server/platform path,
run actual tests,
capture real CSV/log evidence,
and prepare the repo for a later final-cleaning/submission/env phase.
```

---

## Fresh-Session Context

Previous sessions made good progress but also had repeated evidence failures.

Do **not** assume a task is impossible because a previous session failed or produced incomplete evidence.

Known previous issues:

```text
Prompt06 produced useful official-facing local replay and report drafts.
Prompt06b added two news candidates per track to official-facing replay.
But Prompt06/06b evidence was incomplete:
  wrong implementation log from old phase;
  stale summaries not regenerated from current CSVs;
  Type-D missing A1/B3 in some outputs;
  official-facing local replay existed, but true official server/platform run was not proven;
  actual CSVs were not consistently placed in presented/run_csv/;
  adapter source/diff/log evidence was too thin.
```

Your job is to **fix the main pipeline evidence**, not to repeat old excuses.

---

## What “Official Server Run” Means

You must run through the official server/platform path if present in the repo.

You must inspect and use the official starter files, likely including:

```text
start_server.py
config.py
NLPCC_tasks/server_platform/
NLPCC_tasks/agent_platform/
NLPCC_tasks/agent_platform/agents/
NLPCC_tasks/agent_platform/demo_backtest.py
runner/
runners/
```

Your first job is to discover the actual official server/platform entrypoint.

Valid official-server/platform evidence can include one of:

```text
1. start local official server with start_server.py, then run candidate agents through its API / server flow;
2. use official server_platform + agent_platform runner if that is the intended official path;
3. use official demo_backtest only if it internally invokes the official platform semantics and you prove it.
```

Invalid substitutes:

```text
internal research backtester only
src-only replay only
handwritten proxy metric table
old Prompt06 CSV copied without rerun
summary markdown without server logs
```

If remote official server credentials or hidden 2026 access are required, do **not** fake it. Run the local official server/platform path and mark:

```text
remote_official_server = unavailable_not_required
local_official_server_run = true
official_submission_run = false
```

But do not skip the local official server/platform run.

---

## Phase

Use this exact phase name:

```text
Prompt07 — Official Server Run and Main Pipeline Finish
```

Output folder:

```text
outputs/reports/focused_candidate_optimisation/prompt07_official_server_main_pipeline/
```

Required subfolders:

```text
presented/
presented/run_csv/
reference/
logs/
traces/
server_run/
runner_port/
configs/
tests/
report/
```

All important run CSVs must be copied into:

```text
presented/run_csv/
```

The `presented/` folder must not contain only shallow summaries. It must contain analysis-ready CSVs.

---

## One Implementation Log Only

Write exactly one Prompt07 implementation log:

```text
outputs/reports/focused_candidate_optimisation/prompt07_official_server_main_pipeline/presented/implementation_log.md
```

Do not write:

```text
docs/implementation_logs/*
any other Prompt07 implementation_log.md
```

If the log already exists, update it in place.

The log must state:

```text
implementation_log_count = 1
second_docs_log_written = false
duplicate_prompt07_logs_created = false
```

---

## Hard Rules

```text
Use rtk, rtk python, rtk git.
Use project .venv RTK Python.
No hidden 2026.
No online API for model inference.
No new model download.
No broad method search.
No full 212-row matrix.
No official remote submission unless explicitly available and safe.
No official runtime promotion unless evidence proves local official server/platform pass.
Do not delete prior evidence.
Do not call proxy runs actual.
Do not reuse Prompt06/06b tables as new Prompt07 runs.
Do not spend this phase on pip check or compileall.
```

Explicitly **skip** in this phase:

```text
pip check
compileall
package build
dependency cleanup
LaTeX final packaging
environment polishing
```

Those are next phase.

But **do run tests** required below.

---

## Candidate Set

Keep exactly two news candidates per track plus no-news references.

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

Do not add more candidates unless one of these fails and you need a clearly marked emergency fallback.

---

## Stage 0 — Repo and Prior Evidence Intake

Read the repo and previous output folders.

Look for:

```text
prompt06_tuning_official_runner_report/
prompt06b_evidence_repair_two_news_candidates/
official runner adapter files
official runner replay CSVs
same-window Type-D CSVs
system report drafts
```

Create:

```text
reference/input_evidence_manifest.csv
reference/prior_gap_table.csv
presented/prior_gap_summary.md
```

The gap table must include:

```text
gap_id
gap_description
previous_status
Prompt07_action
expected_artifact
```

Must include these gaps:

```text
wrong implementation log in Prompt06/06b
stale replay summaries
missing or weak official server run evidence
missing presented/run_csv evidence package
adapter source/diff not fully audited
A1/B3 missing from Type-D in prior evidence if true
missing or shallow test logs
system report not final-cleaned
```

---

## Stage 1 — Environment and Entrypoint Discovery

Run and save:

```bash
rtk --version
rtk python -c "import sys; print(sys.executable)"
rtk git status
rtk git diff --name-only
```

Do not run pip check.  
Do not run compileall.

Discover official server/platform entrypoints.

Inspect at minimum:

```text
start_server.py
config.py
README.md
NLPCC_tasks/agent_platform/
NLPCC_tasks/server_platform/
NLPCC_tasks/agent_platform/demo_backtest.py
NLPCC_tasks/agent_platform/agents/
runner/
runners/
```

Create:

```text
server_run/official_server_entrypoint_audit.csv
server_run/official_server_run_plan.md
presented/official_server_entrypoint_summary.md
```

`official_server_entrypoint_audit.csv` columns:

```text
path
exists
type
purpose_inferred
can_execute
selected_for_prompt07
reason
```

You must select one actual official server/platform path.

If there are multiple candidates, prefer the one closest to final official submission/server flow, not the easiest research runner.

---

## Stage 2 — Adapter / Agent Port Audit and Fix

Audit or create thin official-server-compatible agent adapters for:

```text
A0, A2, A1, B0, B2, B3
```

The adapter must live in the official agent/platform location, likely:

```text
NLPCC_tasks/agent_platform/agents/
```

Do not broad-rewrite official starter files.

Required behavior:

```text
select track A or B;
select candidate id;
load frozen config;
call existing research candidate logic through thin adapter if needed;
return valid target weights / actions expected by official platform;
log candidate id, date, input hash, output hash;
avoid hidden 2026;
avoid same-day future leakage.
```

Create:

```text
runner_port/official_adapter_source_audit.csv
runner_port/official_adapter_manifest.csv
runner_port/official_adapter_diff_summary.md
presented/official_adapter_audit_summary.md
```

Must record:

```text
adapter_path
sha256
supported_candidates
supported_tracks
default_build_agent_changed
official_runtime_files_modified
uses_hidden_2026
uses_online_api
rollback_plan
```

If `build_agent.py` must be modified for actual official server loading, do it minimally and record exact diff. If a safer adapter registration method exists, use that instead.

---

## Stage 3 — Forced Official Server / Platform Run

This is the core of Prompt07.

You must actually run the selected official server/platform path.

Minimum run set:

```text
A0, A2, A1
B0, B2, B3
```

Run on public/local 2025 validation data or the closest official demo validation set available.

Required outputs:

```text
server_run/official_server_run_manifest.csv
server_run/official_server_command_log.md
server_run/official_server_healthcheck.md
reference/official_server_replay_results_prompt07.csv
reference/official_server_metric_comparison_prompt07.csv
presented/run_csv/official_server_replay_results_prompt07.csv
presented/run_csv/official_server_metric_comparison_prompt07.csv
presented/official_server_run_summary.md
traces/official_server_<track>_<candidate_id>_daily.csv
logs/official_server_<track>_<candidate_id>.log
```

Each result row must include:

```text
track
candidate_id
candidate
server_entrypoint
agent_path
config_hash
date_start
date_end
num_days
return
sharpe
max_drawdown
turnover
mean_abs_overlay
overlay_nonzero
delta_vs_no_news_sharpe
actual_official_server_or_platform_run
local_official_server_run
remote_official_server_run
official_submission_run
proxy_run
status
error_log_path
notes
```

Required labels:

```text
actual_official_server_or_platform_run = true only if server/platform path was actually invoked
local_official_server_run = true for local start_server/server_platform/demo platform run
remote_official_server_run = false unless real remote official server was used
official_submission_run = false
proxy_run = false for actual server/platform run
```

If one candidate fails, keep the failed row and continue other candidates.

If the server cannot start, do not substitute internal backtester. Instead produce:

```text
blocked_official_server_start
```

with exact command, traceback, and next fix.

---

## Stage 4 — Main Pipeline Tests

Run tests that validate the main project pipelines.

Required:

```bash
rtk python -m pytest tests/test_nlpcc/test_news_overlay -q
rtk python -m pytest tests/test_nlpcc -q
rtk python -m pytest tests -q
```

Also run official server / runner smoke tests if any exist, discovered by search:

```text
test_server*
test_agent*
test_runner*
test_backtest*
```

Do not run:

```text
pip check
compileall
package build
```

Create:

```text
tests/test_command_manifest.csv
tests/test_results_summary.csv
presented/full_test_summary.md
logs/news_overlay_pytest.log
logs/full_pytest_tests_nlpcc.log
logs/full_pytest_tests.log
logs/official_server_smoke_tests.log
```

Each test row must include:

```text
command
purpose
return_code
status
duration_seconds
log_path
failure_summary
```

If tests fail, keep going only if server run already completed; otherwise fix minimal blocking failures required for server run.

---

## Stage 5 — Same-Window Type-D Completion for Two News Candidates Per Track

If A1 and B3 were missing from previous Type-D, run them now.

Use same-window definitions:

```text
D1-H2:
  train/tune = 2024 only
  test = later-half 2025

D2-H2:
  train/tune = 2024 + first-half 2025
  test = same later-half 2025
```

Run or confirm actual/carry-forward for:

```text
A0, A2, A1, B0, B2, B3
```

Required outputs:

```text
reference/typed_same_window_d1_h2_results_prompt07.csv
reference/typed_same_window_d2_h2_results_prompt07.csv
reference/typed_same_window_more_data_comparison_prompt07.csv
presented/run_csv/typed_same_window_d1_h2_results_prompt07.csv
presented/run_csv/typed_same_window_d2_h2_results_prompt07.csv
presented/run_csv/typed_same_window_more_data_comparison_prompt07.csv
presented/typed_same_window_summary.md
```

Rows must include:

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
notes
```

If carried forward, state source file and hash. Do not mark carried-forward rows as fresh.

---

## Stage 6 — Presented CSV Evidence Package

Create:

```text
presented/run_csv_index.md
presented/run_csv_manifest.csv
```

Every important run CSV must be in `presented/run_csv/`.

Minimum required files there:

```text
official_server_replay_results_prompt07.csv
official_server_metric_comparison_prompt07.csv
typed_same_window_d1_h2_results_prompt07.csv
typed_same_window_d2_h2_results_prompt07.csv
typed_same_window_more_data_comparison_prompt07.csv
final_prompt07_decision_table.csv
test_results_summary.csv
```

`run_csv_manifest.csv` columns:

```text
csv_path
row_count
candidate_ids
track_coverage
date_range
actual_run
proxy_run
carried_forward
why_it_matters
```

Do not provide only general markdown summaries.

---

## Stage 7 — System Report Status Only

Do not spend this phase finalizing LaTeX.

Just verify the report files exist and are not misleading.

Check:

```text
system_report_track_a_2page.tex
system_report_track_b_2page.tex
combined draft if present
```

Create:

```text
report/system_report_status_prompt07.csv
presented/system_report_status_summary.md
```

Required checks:

```text
file_exists
uses_llncs
has_abstract
has_method_section
has_experiment_section
mentions_local_public_validation_only
does_not_claim_official_server_result_unless server CSV supports it
does_not_use_hidden_2026
page_count_checked = false unless PDF compile actually run
```

Do not run full LaTeX finalization unless trivial. That is next phase.

---

## Stage 8 — Final Main Pipeline Decision

Create:

```text
reference/final_prompt07_decision_table.csv
presented/run_csv/final_prompt07_decision_table.csv
presented/final_candidate_decision_summary.md
presented/submission_gap_summary.md
presented/final_next_phase_recommendation.md
```

Decision table columns:

```text
track
candidate_id
candidate
role
official_server_status
official_server_sharpe
delta_vs_no_news_sharpe
same_window_typed_status
more_data_helped
test_status
report_status
official_runtime_changed
official_submission_run
final_status
decision
next_action
```

Allowed final statuses:

```text
no_news_reference
official_server_candidate
research_news_candidate
regime_or_ensemble_candidate
report_only_ablation
blocked_official_server_start
blocked_server_run_failed
blocked_tests_failed
blocked_evidence_missing
```

Do not use:

```text
official_promotion_ready
official_parity_ready
submission_ready
```

Unless a real official submission/parity workflow is run and evidenced.

---

## Implementation Log Required Sections

The single Prompt07 implementation log must include:

```text
A. Summary
B. Files Created
C. Files Modified
D. Files Read
E. Commands Run
F. Entrypoint Discovery
G. Adapter / Agent Port Audit
H. Official Server / Platform Run
I. Main Pipeline Tests
J. Same-Window Type-D Completion
K. Presented CSV Evidence Package
L. System Report Status
M. Final Candidate Decision
N. Failed or Blocked Runs
O. Official Runtime Status
P. Hidden 2026 / Leakage Check
Q. Artifacts
R. Caveats
S. Next Steps
```

Every command entry must include:

```text
command
return_code
duration_seconds
log_path
```

Every modified source file entry must include:

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
Prompt07 status:
  <pass/partial/fail/blocked>

Implementation log:
  <path>
  count: <1/other>

Official server/platform entrypoint:
  <path>
  mode:
    <local_server/server_platform/demo_platform/blocked>

Official server/platform run:
  status: <complete/partial/fail/blocked>
  candidates attempted: <list>
  candidates passed: <list>
  rows: <n>
  csv:
    presented/run_csv/official_server_replay_results_prompt07.csv

Main tests:
  pytest news_overlay: <pass/fail/not_run>
  pytest tests_nlpcc: <pass/fail/not_run>
  pytest full tests: <pass/fail/not_run>
  official server smoke tests: <pass/fail/not_found/not_run>

Same-window Type-D:
  status: <complete/partial/fail>
  candidates covered: <list>
  csv:
    presented/run_csv/typed_same_window_more_data_comparison_prompt07.csv

Presented CSV package:
  status: <complete/partial/fail>
  index:
    presented/run_csv_index.md

Two news candidates per track:
  Track A:
    A2: <status>
    A1: <status>
  Track B:
    B2: <status>
    B3: <status>

Best current candidates:
  Track A:
    <candidate + reason>
  Track B:
    <candidate + reason>

Submission-safe references:
  Track A: A0 G00A
  Track B: B0 G00B

System report status:
  Track A: <ok/partial/missing>
  Track B: <ok/partial/missing>

Skipped by design:
  pip check
  compileall
  package build
  LaTeX finalization

Official runtime changed?
  <yes/no + exact files>

Official submission run?
  no

Hidden 2026 used?
  <yes/no>

Main blockers:
  <list>

Best next action:
  <one action>
```
