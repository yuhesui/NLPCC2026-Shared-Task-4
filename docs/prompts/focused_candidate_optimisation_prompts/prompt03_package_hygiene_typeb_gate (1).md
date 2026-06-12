## Your Role

You are GPT-5.5 Extended Thinking acting as:

```text
senior quantitative research engineer
package hygiene repair engineer
Chinese financial NLP pipeline engineer
backtest validation auditor
baseline-gated selection reviewer
repo cleanup lead
test/package hygiene reviewer
implementation-log writer
```

Your job is to fix Prompt02 blockers and produce a clean local candidate-selection state.

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

## Phase Name and Output Folder

Use this phase name everywhere:

```text
Prompt03 — Package Hygiene, Clean Type-B Rerun, and Baseline-Gated Selection
```

All new Prompt03 outputs must go under:

```text
outputs/reports/focused_candidate_optimisation/prompt03_package_hygiene_typeb_gate/
```

Required folder layout:

```text
outputs/reports/focused_candidate_optimisation/prompt03_package_hygiene_typeb_gate/
  presented/
  reference/
  progress/
  logs/
  traces/
```

Do not write new Prompt03 outputs under:

```text
outputs/reports/news_overlay/
outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/
outputs/reports/focused_candidate_optimisation/prompt02_optimizer_synthetic_typec/
```

Allowed only for reading old evidence:

```text
outputs/reports/news_overlay/**
outputs/reports/focused_candidate_optimisation/prompt00_focused_candidate_optimisation/**
outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/**
outputs/reports/focused_candidate_optimisation/prompt02_optimizer_synthetic_typec/**
```

## One Implementation Log Only

This prompt must write exactly one implementation log:

```text
outputs/reports/focused_candidate_optimisation/prompt03_package_hygiene_typeb_gate/presented/implementation_log.md
```

Do not write a second durable log under:

```text
docs/implementation_logs/
```

Do not create any other file named:

```text
implementation_log.md
*_implementation_log.md
*_prompt03*.md
```

If automation would normally write a second implementation log, disable it for Prompt03 or mark:

```text
blocked_duplicate_implementation_log_risk
```


## Why Prompt03 Exists

Prompt02 built useful research tools but stayed blocked.

Known Prompt02 state:

```text
bounded optimiser built with random_search_fallback
synthetic backtester built with 12 scenarios
actual Type-C ran with real news-overlay target weights
Type-C is research-only
no official parity was run
all pytest scopes passed
compileall failed from pycache write permission
pip check failed from environment dependency conflicts
no news candidate beats no-news on Type B
B2 G15B V4 remains research branch only
repo was dirty before Prompt02
```

Prompt03 must fix practical blockers before any official parity work.

## Mission

Do these jobs in order:

```text
1. fix package hygiene or prove exact blockers;
2. clean or isolate repo dirty state;
3. rerun selected Type-B configs after hygiene work;
4. add hard no-news baseline gates;
5. produce a final baseline-gated candidate table;
6. improve cache/reproducibility proof;
7. prepare a clear next-step recommendation;
8. write exactly one detailed implementation log.
```

No official-server parity is required.

Do not promote official runtime.
Do not use hidden 2026.
Do not treat Type-C or synthetic as official-valid.

## Candidate Pool

Use only this bounded pool.

Track A:

```text
A1 G12A V3
A2 G11A V0
A0 G00A no-news reference
```

Track B:

```text
B1 G15B V0
B2 G15B V4
B3 G21B repaired_lite
B0 G00B no-news reference
```

Optional archived references, only if cheap and useful:

```text
G14B V4
G10B V5
```

Do not reopen broad 212-row search.
Do not add new model family.

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
Type C and synthetic are research-only.
No Type C or synthetic result may override Type B.
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


## Stage 0 — Create Prompt03 Phase Folder

Create exactly:

```text
outputs/reports/focused_candidate_optimisation/prompt03_package_hygiene_typeb_gate/presented/
outputs/reports/focused_candidate_optimisation/prompt03_package_hygiene_typeb_gate/reference/
outputs/reports/focused_candidate_optimisation/prompt03_package_hygiene_typeb_gate/progress/
outputs/reports/focused_candidate_optimisation/prompt03_package_hygiene_typeb_gate/logs/
outputs/reports/focused_candidate_optimisation/prompt03_package_hygiene_typeb_gate/traces/
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

## Stage 0A — RTK Preflight and Repo Safety Snapshot

Run:

```bash
rtk --version
rtk git status
rtk git diff --name-only
rtk git ls-files | grep -i "agents.md\|agent.md\|AGENTS.md\|CLAUDE.md\|codex"
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

## Stage 0B — Update AGENTS.md for Prompt03

Update root `AGENTS.md`. Do not overwrite unrelated rules.

Add or update section:

```text
Focused Candidate Optimisation — Prompt03 Rules
```

Required content:

```text
Current prompt:
  Prompt03 — Package Hygiene, Clean Type-B Rerun, and Baseline-Gated Selection

Output folder:
  outputs/reports/focused_candidate_optimisation/prompt03_package_hygiene_typeb_gate/

Implementation log:
  exactly one implementation log only
  path: outputs/reports/focused_candidate_optimisation/prompt03_package_hygiene_typeb_gate/presented/implementation_log.md
  do not write docs/implementation_logs copy

Must use:
  rtk
  rtk python
  rtk git
  rtk python -m pytest

Must fix or prove:
  compileall pycache permission issue
  pip check dependency conflict
  dirty worktree attribution
  Type-B rerun after hygiene work
  no-news baseline gate

Do not:
  run hidden 2026
  run official-server parity
  promote official runtime
  write Prompt03 outputs outside Prompt03 folder
  download new models
  call online APIs
```

Create:

```text
reference/agents_md_update_manifest.csv
presented/agents_md_update_summary.md
```

Include before/after hashes.

## Stage 1 — Input Evidence Intake

Read current repo state and prior Prompt01/Prompt02 outputs.

Create:

```text
reference/input_evidence_manifest.csv
reference/prompt02_audit_gap_table.csv
reference/candidate_start_state.csv
presented/current_state_intake_summary.md
```

`prompt02_audit_gap_table.csv` must include:

```text
gap
severity
source
needed_fix
prompt03_stage
```

Minimum gaps:

```text
compileall failed from pycache write permission
pip check failed from dependency conflicts
no news candidate beats no-news on Type B
Type C and synthetic are research-only
cache-hit proof bounded to trace fields only
repo dirty before Prompt02
Optuna unavailable
```


## Stage 2 — Package Hygiene Repair

This stage is first priority.

### 2.1 Diagnose compileall

Inspect Prompt02 logs if present:

```text
outputs/reports/focused_candidate_optimisation/prompt02_optimizer_synthetic_typec/logs/compileall_before_or_recheck.log
outputs/reports/focused_candidate_optimisation/prompt02_optimizer_synthetic_typec/logs/compileall_src_tests.log
```

Run:

```bash
rtk python -m compileall src tests
rtk python -B -m compileall src tests
```

If pycache write permission is the only failure, test a safe writable cache prefix.

Use an RTK Python helper script if needed to set:

```text
PYTHONPYCACHEPREFIX=<prompt03_tmp_cache_dir>
```

Then run compileall through the helper.

Do not change source logic only to silence compileall.

### 2.2 Diagnose pip check

Inspect Prompt02 logs if present:

```text
outputs/reports/focused_candidate_optimisation/prompt02_optimizer_synthetic_typec/logs/pip_check_before_or_recheck.log
outputs/reports/focused_candidate_optimisation/prompt02_optimizer_synthetic_typec/logs/pip_check.log
```

Run:

```bash
rtk python -m pip check
```

If conflicts are environment-only and not caused by repo metadata:

```text
mark pip_check_blocked_environment_conflict
do not edit pyproject/requirements blindly
```

If conflicts are caused by repo dependency metadata and fix is safe:

```text
make minimal dependency metadata fix
rerun pip check
```

No heavy install.
No internet.
No online package query.

Required outputs:

```text
reference/package_hygiene_diagnosis.csv
reference/package_hygiene_fix_actions.csv
reference/package_hygiene_checks.csv
presented/package_hygiene_summary.md
logs/compileall_initial.log
logs/compileall_no_bytecode.log
logs/compileall_pycacheprefix.log
logs/pip_check_initial.log
logs/pip_check_final.log
```

Allowed package status labels:

```text
package_hygiene_pass
compileall_pass_pip_check_blocked_environment
compileall_blocked_pycache_permission
pip_check_blocked_environment_conflict
blocked_package_hygiene
```

Do not claim package readiness unless compileall and pip check pass, or unless pip check is clearly environment-only and a clean isolated-env path is documented.

## Stage 3 — Dirty Worktree Attribution and Repo Cleanup

Do not blindly clean or delete.

Create a manifest first.

Run:

```bash
rtk git status --short
rtk git diff --name-only
```

Classify each changed/untracked/deleted file:

```text
prompt01_change
prompt02_change
prompt03_change
pre_existing_dirty
generated_output
cache_artifact
safe_to_ignore
needs_review
must_keep
must_revert
```

Do not revert source changes needed for Prompt01/Prompt02 fixes.
Do not delete raw data, source code, tests, configs, or evidence.

Create:

```text
reference/dirty_worktree_inventory.csv
reference/repo_cleanup_actions.csv
presented/repo_cleanliness_summary.md
```

If cleanup is performed, record:

```text
path
action
reason
before_status
after_status
safe
rollback_path
```


## Stage 4 — Build No-News Baseline Gate

Implement or configure a hard candidate-selection gate.

Purpose:

```text
A news candidate can have real overlay and still be bad.
Do not select it unless it beats or clearly justifies trailing no-news.
```

Gate rules:

```text
For Track A:
  compare candidate to G00A on Type B frozen 2025.

For Track B:
  compare candidate to G00B on Type B frozen 2025.

Candidate passes baseline gate only if:
  delta_vs_no_news_sharpe >= 0
  OR robust justification exists and downside is small

Default:
  if delta_vs_no_news_sharpe < 0, status cannot be active_branch_selected.
  It may be active_but_needs_more_evidence or research_branch_only.
```

Optional stricter rule:

```text
candidate must also have max_drawdown not materially worse
candidate must also have turnover not materially worse
candidate must have nonzero overlay if claiming news use
```

Create:

```text
reference/baseline_gate_rules.yaml
reference/baseline_gate_results.csv
presented/baseline_gate_summary.md
```

## Stage 5 — Clean Type-B Rerun After Hygiene Work

Rerun Type B only.

No official parity.
No hidden 2026.
No Type-C tuning reuse for official-valid claims.

Use configs selected by:

```text
Prompt01 fixed baseline configs
Prompt02 best configs only if selected using 2024-only Type-B logic
No Type-C-only config may be treated as official-valid
```

Required candidates:

```text
A0 G00A
A1 G12A V3
A2 G11A V0
B0 G00B
B1 G15B V0
B2 G15B V4
B3 G21B repaired_lite
```

Optional if cheap:

```text
G14B V4
G10B V5
```

Run:

```text
2024 train/tune/select
freeze config
2025 frozen test
```

For each run, record:

```text
candidate_id
candidate
variant
track
config_source
config_hash
typeb_train_year
typeb_test_year
2024_return
2024_sharpe
2024_max_drawdown
2024_turnover
2025_return
2025_sharpe
2025_max_drawdown
2025_turnover
mean_abs_overlay
overlay_contribution_nonzero
delta_vs_no_news_return
delta_vs_no_news_sharpe
baseline_gate_status
notes
```

Required outputs:

```text
reference/typeb_clean_rerun_results.csv
reference/typeb_selected_config_manifest.csv
traces/typeb_<candidate_id>_<variant>_daily_trace.csv
presented/typeb_clean_rerun_summary.md
```

If full Type-B rerun fails:

```text
do not use old Type-B as fresh evidence
mark blocked_full_typeb_rerun_failed
record exact command and error
```

## Stage 6 — Cache and Reproducibility Proof

Improve Prompt02 cache proof.

Run a repeated Type-B subset:

```text
best Track A candidate after baseline gate
best Track B candidate after baseline gate
their no-news references
```

Record:

```text
cache files before
cache files after
cache hits
cache misses
duration_first
duration_second
same_metrics
same_trades
same_daily_trace_hash
```

Required outputs:

```text
reference/cache_replay_detailed.csv
presented/cache_reproducibility_summary.md
```

If cache-hit tracking is still partial:

```text
mark cache_proof_partial
do not claim full cache validation
```


## Stage 7 — Tests and Checks

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

Also run any compileall workaround check from Stage 2 if normal compileall remains blocked by pycache permission.

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

## Stage 8 — Final Candidate Decision

Create:

```text
reference/final_candidate_decision_table.csv
presented/final_candidate_decision_summary.md
presented/final_next_phase_recommendation.md
```

`final_candidate_decision_table.csv` columns:

```text
candidate_id
track
candidate
variant
config_source
package_status
typeb_2025_return
typeb_2025_sharpe
typeb_2025_max_drawdown
typeb_2025_turnover
overlay_contribution_nonzero
delta_vs_no_news_return
delta_vs_no_news_sharpe
baseline_gate_status
cache_replay_status
test_status
official_runtime_changed
final_status
decision
reason
next_action
```

Allowed final statuses:

```text
baseline_reference_only
active_next_phase
active_but_needs_more_evidence
research_branch_only
archived_fallback
retired_ablation_reference
blocked_package_hygiene
blocked_full_typeb_rerun_failed
not_ready_repo_state_unclear
```

Do not use:

```text
official_promotion_ready
official_parity_ready
```

No branch may be `active_next_phase` if:

```text
compileall failed without acceptable documented workaround
pip check failed without acceptable environment-only classification
baseline gate failed
full Type-B rerun failed
```

## Stage 9 — Final Report

Create:

```text
presented/executive_summary.md
presented/final_readiness_summary.md
```

Final readiness must be exactly one:

```text
ready_for_official_parity_prep
partial_missing_evidence
blocked_package_hygiene
blocked_full_typeb_rerun_failed
not_ready_repo_state_unclear
```

Do not run official parity in this prompt.

If readiness is `ready_for_official_parity_prep`, it means only:

```text
local package hygiene and Type-B gate are good enough to prepare next official parity prompt
```

It does not mean official ready.


## Stage 10 — Single Detailed Implementation Log

Write exactly one implementation log:

```text
outputs/reports/focused_candidate_optimisation/prompt03_package_hygiene_typeb_gate/presented/implementation_log.md
```

The log must include exactly these sections:

```text
A. Summary
B. Files Created
C. Files Modified
D. Files Read
E. Commands Run
F. Package Hygiene Diagnosis
G. Package Hygiene Fixes
H. Dirty Worktree Inventory
I. Repo Cleanup Actions
J. Baseline Gate Built
K. Type-B Reruns Completed
L. Cache / Reproducibility Check
M. Tests Added or Updated
N. Tests Run
O. Failed / Blocked Runs
P. Official Runtime Config Status
Q. 2025 Tune Check
R. Hidden 2026 Check
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

The log must explicitly state:

```text
implementation_log_count = 1
second_docs_log_written = false
```

Do not write “Artifacts: None” if artifacts exist.

## Final Response Format

Use caveman English.

```text
Prompt03 status:
  <pass/partial/fail/blocked>

Phase folder:
  outputs/reports/focused_candidate_optimisation/prompt03_package_hygiene_typeb_gate/

Implementation log count:
  <1/other>
  path:
    outputs/reports/focused_candidate_optimisation/prompt03_package_hygiene_typeb_gate/presented/implementation_log.md

RTK used?
  <yes/no>

AGENTS.md updated?
  <yes/no/created/blocked>
  evidence:
    <paths>

Package hygiene:
  compileall:
    <pass/fail/workaround_pass/not_run>
  pip check:
    <pass/fail/environment_blocked/not_run>
  package_status:
    <label>

Repo cleanliness:
  <clean/dirty_known/dirty_blocked>

Type-B clean rerun:
  <complete/partial/failed/not_run>

Baseline gate:
  Track A:
    <summary>
  Track B:
    <summary>

Cache proof:
  <pass/partial/fail/not_run>

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

2025 tuned outside Type-B rule?
  <yes/no>

Hidden 2026 used?
  <yes/no>

Main blockers:
  <list>

Main artifacts:
  <paths>

Readiness:
  <ready_for_official_parity_prep / partial_missing_evidence / blocked_package_hygiene / blocked_full_typeb_rerun_failed / not_ready_repo_state_unclear>

Best next action:
  <one specific action>
```
