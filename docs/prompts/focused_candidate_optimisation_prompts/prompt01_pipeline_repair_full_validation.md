## Your Role

You are GPT-5.5 Extended Thinking acting as:

```text
senior quantitative research engineer
Chinese financial NLP architect
pipeline repair engineer
repo-state auditor
test and benchmark lead
model-risk reviewer
submission-safety reviewer
AGENTS.md maintainer
implementation-log writer
```

Your job is to **fix the real pipeline**, not only write summaries.

Be strict.

Distinguish:

```text
implemented vs claimed
configured vs executed
tested vs imported only
sample evidence vs full evidence
local evidence vs official-server evidence
fallback/proxy vs real method execution
cache written vs cache-hit demonstrated
full run vs smoke run
2024 tune vs 2025 frozen test
synthetic diagnostic vs real market result
official runtime preserved vs modified
```

Do not promote any candidate to official runtime.

Do not claim parity-ready unless real parity evidence exists.

---

## Phase Name and Output Folder

Use this phase name everywhere:

```text
Prompt01 — Pipeline Repair and Full Validation Run
```

Use this folder slug everywhere:

```text
focused_candidate_optimisation/prompt01_pipeline_repair_full_validation
```

This is part of the **Focused Candidate Optimisation** phase, which is parallel to `news_overlay`.

Correct reports tree:

```text
outputs/reports/
  news_overlay/
  focused_candidate_optimisation/
    prompt00_focused_candidate_optimisation/     # if already exists, read only
    prompt01_pipeline_repair_full_validation/    # this prompt writes here
```

All new Prompt01 outputs must go under:

```text
outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/
```

Required folder layout:

```text
outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/
  presented/
  reference/
  progress/
  logs/
  traces/
```

Folder meaning:

```text
presented/
  Human-readable final summaries and decision reports.

reference/
  CSV, JSON, YAML, manifests, metric tables, check summaries, config hashes.
  This is the audit source.

progress/
  Intermediate notes, blocker notes, stage-level status logs.

logs/
  Full run logs and command transcripts.
  Keep compact if logs are huge; write manifest if not copied.

traces/
  Daily candidate traces, overlay traces, delta traces, attribution traces.
```

Do not write new Prompt01 outputs under:

```text
outputs/reports/news_overlay/
outputs/reports/focused_candidate_optimisation/        # root only; no loose files
```

Allowed only for reading old evidence:

```text
outputs/reports/news_overlay/**
outputs/reports/focused_candidate_optimisation/prompt00_focused_candidate_optimisation/**
outputs/reports/focused_candidate_optimisation/presented/**
outputs/reports/focused_candidate_optimisation/reference/**
```

Also write durable logs:

```text
docs/implementation_logs/<timestamp>_prompt01_pipeline_repair_full_validation.md
```

The durable log must point back to the Prompt01 folder.

---

## Why Prompt01 Exists

Prompt00 was partial.

Known Prompt00 audit findings:

```text
G15B V0 and G15B V4 both had zero overlay and matched G00B.
G21B repaired/lite exact real 2024/2025 rerun was missing.
Track A overlay changed from Prompt27 false to Prompt00 true but trace proof was missing.
AGENTS.md update was not evidenced.
Many required reference CSVs were not uploaded/evidenced.
Repo was dirty before Prompt00.
No official parity, package, cache-hit, or full-test evidence existed.
```

Prompt01 must fix these pipeline and evidence problems.

---

## Mission

Actually repair and validate the focused candidate pipeline.

Main job:

```text
1. update AGENTS.md and prove it;
2. create full Prompt01 phase folder with presented/reference/progress/logs/traces;
3. make full input/output manifest;
4. debug G15B zero-overlay pipeline;
5. either fix G15B overlay path or retire/block it with proof;
6. run exact G21B repaired/lite 2024 tune and frozen 2025 test;
7. resolve Track A overlay trace inconsistency;
8. generate all required reference CSVs;
9. run full test suite and relevant full backtest runs;
10. write detailed implementation log with changed files, commands, results, failures, and caveats.
```

This is not broad method search.

This is not official promotion.

This is not a full 212-row Prompt23 matrix.

---

## Source of Truth

Read all available current phase and prior phase files first.

Required old evidence to read if present:

```text
docs/news_overlay/current_news_overlay_state.md
docs/news_overlay/final_candidate_pool.md
docs/news_overlay/next_phase_execution_plan.md

outputs/reports/news_overlay/prompt27_wrapup/presented/current_repo_state_summary.md
outputs/reports/news_overlay/prompt27_wrapup/presented/final_candidate_pool_summary.md
outputs/reports/news_overlay/prompt27_wrapup/presented/candidate_gap_summary.md
outputs/reports/news_overlay/prompt27_wrapup/presented/next_phase_execution_plan.md
outputs/reports/news_overlay/prompt27_wrapup/reference/final_candidate_manifest.csv
outputs/reports/news_overlay/prompt27_wrapup/reference/final_candidate_metrics.csv
outputs/reports/news_overlay/prompt27_wrapup/reference/candidate_gap_analysis.csv
outputs/reports/news_overlay/prompt27_wrapup/reference/checks_summary.csv

outputs/reports/news_overlay/prompt26_complex_synthetic_retest/presented/final_complex_retest_recommendation.md
outputs/reports/news_overlay/prompt26_complex_synthetic_retest/reference/complex_lite_variant_results.csv
outputs/reports/news_overlay/prompt26_complex_synthetic_retest/reference/complex_candidate_decision_table.csv

outputs/reports/focused_candidate_optimisation/presented/*
outputs/reports/focused_candidate_optimisation/reference/*
outputs/reports/focused_candidate_optimisation/prompt00_focused_candidate_optimisation/**
```

If some files do not exist, mark missing. Do not invent.

Prompt01 candidate set:

```text
Track A:
  A1 G12A V3 — N2345/I256/S13 + H4
  A2 G11A V0 — N13/I6/S13
  A0 G00A — N0/I0/S0 no-news reference only

Track B:
  B1 G15B V0 — N4/I6/S2
  B2 G15B V4 — N4/I6/S2 + H1+H5
  B3 G21B repaired/lite — N2345/I256/S5 repaired controls
  B0 G00B — N0/I0/S0 no-news reference only

Archived comparison only:
  G14B V4 — N5/I5/S2 + H1+H5
  G10B V5 — N2/I2/S2 + H1+H2+H4+H5

Retired:
  G12B / G12B_lite
  G10A
```

---

## Hard Rules

Do not break these:

```text
No hidden 2026.
No tune on 2025.
2024 = tune / diagnostic only.
2025 = frozen test only.
No official promotion.
No official runtime config edit unless user explicitly approves.
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

## Stage 0 — Create Prompt01 Phase Folder

Create exactly:

```text
outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/presented/
outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/reference/
outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/progress/
outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/logs/
outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/traces/
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
is_parallel_to_news_overlay = true
parent_phase = focused_candidate_optimisation
```

---

## Stage 0A — RTK Preflight and Repo Safety Snapshot

Run:

```bash
rtk --version
rtk git status
rtk git diff --name-only
rtk git ls-files | grep -i "agents.md\|agent.md\|AGENTS.md\|CLAUDE.md\|codex"
```

Also compute file hashes for important no-touch paths if they exist:

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

## Stage 0B — Update AGENTS.md and Prove It

Find agent guidance files.

Use RTK only.

If root `AGENTS.md` exists:

```text
Update it.
Do not overwrite unrelated rules.
Add or update section:
  Focused Candidate Optimisation Phase Rules
```

If root `AGENTS.md` does not exist:

```text
Create AGENTS.md at repo root.
Keep it concise.
Make it agent guidance only.
```

If `CLAUDE.md`, `.codex/AGENTS.md`, or docs-level agent guidance exists:

```text
Add short pointer to root AGENTS.md only if appropriate.
Do not duplicate large text.
```

Required content in root `AGENTS.md` section:

```text
Current phase:
  Prompt01 — Pipeline Repair and Full Validation Run

Output folder:
  outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/

Must use:
  rtk
  rtk python
  rtk git
  rtk python -m pytest

Style:
  caveman English for reports and final response

Must fix:
  G15B zero-overlay pipeline or prove blocked
  exact G21B repaired/lite real 2024/2025 rerun
  Track A overlay trace inconsistency
  missing reference CSV artifacts
  dirty-state manifest and no-touch config hashes

Do not:
  write new Prompt01 outputs under outputs/reports/news_overlay/
  use hidden 2026
  tune on 2025
  edit official runtime configs
  run full 212-row matrix
  promote to official runtime
  download new models
  call online APIs
```

Create:

```text
reference/agent_guidance_files_audit.csv
reference/agents_md_update_manifest.csv
presented/agents_md_update_summary.md
```

`agents_md_update_manifest.csv` columns:

```text
path
action
section_added_or_updated
before_hash
after_hash
notes
```

If no update is needed, say why and still record hashes.

---

## Stage 1 — Input Evidence Manifest

Read all source files.

Create:

```text
reference/input_evidence_manifest.csv
reference/candidate_start_state.csv
reference/prompt00_audit_gap_table.csv
presented/current_state_intake_summary.md
```

`input_evidence_manifest.csv` columns:

```text
path
exists
type
read_status
rows_or_lines
key_facts
notes
```

`candidate_start_state.csv` columns:

```text
candidate_id
track
candidate
variant
stack
role
status_from_previous_phase
has_2024_evidence
has_frozen_2025_evidence
overlay_contribution_nonzero
known_gap
required_action
source_file
notes
```

`prompt00_audit_gap_table.csv` must include:

```text
gap
severity
source
needed_fix
prompt01_stage
```

---

## Stage 2 — Repair G15B Zero-Overlay Pipeline

This is mandatory.

### Candidates

```text
B1 G15B V0 — N4/I6/S2
B2 G15B V4 — N4/I6/S2 + H1+H5
B0 G00B — no-news reference
```

### Required diagnosis

Trace all stages:

```text
raw news loaded
N4 event labels produced
I6 aspect-impact produced
S2 sector overlay produced
H1/H5 hooks applied for V4
overlay gate applied
target weights before overlay
target weights after overlay
trade output after adapter
comparison vs G00B
```

Find exact zero-overlay cause.

Possible cause labels:

```text
news_missing
N4_zero
I6_zero
S2_zero
gate_blocks_all
hook_blocks_all
config_not_loaded
wrong_candidate_mapping
fallback_always_used
trace_instrumentation_bug
pipeline_not_called
same_as_G00B_by_design
unknown
```

### Required fix rule

If bug is found and safe to fix:

```text
Fix it.
Add test.
Run 2024 diagnostic.
Freeze config.
Run 2025 frozen test.
```

If no safe fix:

```text
Do not fake overlay.
Mark blocked.
Give exact cause.
```

### Required runs

Minimum:

```text
G00B 2024 and frozen 2025 reference
G15B V0 2024 and frozen 2025
G15B V4 2024 and frozen 2025
```

Use 2024 for tune/diagnostic only.

Use 2025 frozen only.

No 2025 parameter changes.

### Required outputs

```text
traces/goal_b_g15b_v0_daily_trace.csv
traces/goal_b_g15b_v4_daily_trace.csv
traces/goal_b_g00b_daily_trace.csv
reference/goal_b_zero_overlay_root_cause.csv
reference/goal_b_g15b_repair_actions.csv
reference/goal_b_g15b_2024_2025_metrics.csv
reference/goal_b_g15b_vs_g00b_deltas.csv
reference/goal_b_g15b_tests_added_or_updated.csv
presented/goal_b_g15b_pipeline_repair_report.md
```

Decision labels:

```text
g15b_v0_active_after_fix
g15b_v4_active_after_fix
g15b_blocked_zero_overlay_confirmed
g15b_retire_to_ablation
g15b_inconclusive_needs_manual_debug
```

---

## Stage 3 — Resolve Track A Overlay Trace Inconsistency

Prompt27/P00 state conflict must be fixed.

### Candidates

```text
A1 G12A V3
A2 G11A V0
A0 G00A
```

### Required diagnosis

For A1 and A2, prove or disprove:

```text
overlay contribution nonzero
target weights differ from G00A
trades differ from G00A
news signal actually flows through final allocator
fallback is not always used
```

Run:

```text
G00A 2024 and frozen 2025
G12A V3 2024 and frozen 2025
G11A V0 2024 and frozen 2025
```

### Required outputs

```text
traces/goal_a_g12a_daily_trace.csv
traces/goal_a_g11a_daily_trace.csv
traces/goal_a_g00a_daily_trace.csv
reference/goal_a_overlay_inconsistency_resolution.csv
reference/goal_a_2024_2025_metrics.csv
reference/goal_a_vs_g00a_deltas.csv
presented/goal_a_track_a_overlay_repair_report.md
```

Decision labels per candidate:

```text
continue_active_with_proven_overlay
continue_active_but_overlay_unproven
downgrade_to_ablation
blocked_missing_evidence
```

---

## Stage 4 — Run Exact G21B Repaired/Lite Full Real Validation

This is mandatory.

### Candidate

```text
B3 G21B repaired/lite — N2345/I256/S5
```

### Required repaired/lite controls

Verify actual implementation of:

```text
N2345 consensus shrink
I256 dominance cap
S5 BL-view confidence cap
event/evidence count required before overlay
weak-signal deadband
fallback to safe no-news or S1 behaviour
```

Do not use old G21B V0 as proxy for repaired/lite.

Do not use synthetic-only evidence.

Do not claim repaired/lite if exact repaired/lite config did not run.

### Required runs

Run:

```text
G21B repaired/lite 2024 tune/diagnostic
G21B repaired/lite frozen 2025

G00B 2024 and frozen 2025 reference
G15B selected-or-blocked reference
optional G14B V4 2025 reference
optional G10B V5 2025 reference
```

If full-year run is too slow:

```text
Do not silently downgrade.
First run full-year attempt.
If blocked by time/error, record full error.
Then run smoke as fallback and mark blocked_full_run_failed.
```

### Required outputs

```text
traces/goal_c_g21b_repaired_daily_trace_2024.csv
traces/goal_c_g21b_repaired_daily_trace_2025.csv
reference/goal_c_g21b_repaired_config_audit.csv
reference/goal_c_g21b_repaired_implementation_status.csv
reference/goal_c_g21b_repaired_2024_2025_metrics.csv
reference/goal_c_g21b_vs_references.csv
reference/goal_c_g21b_blocker_resolution.csv
presented/goal_c_g21b_repaired_full_validation_report.md
```

Decision labels:

```text
continue_high_upside_candidate
continue_research_backup_only
simplify_and_retest
retire_from_selection_keep_for_ablation
blocked_full_run_failed
blocked_missing_exact_repaired_implementation
```

---

## Stage 5 — Full Validation and Tests

Run full tests, not only compact news-overlay tests, unless the repo makes full tests impossible.

Required commands:

```bash
rtk --version
rtk git status
rtk git diff --name-only
rtk python -m pytest tests/test_nlpcc/test_news_overlay -q
rtk python -m pytest tests/test_nlpcc -q
rtk python -m pytest tests -q
```

If `tests -q` is too slow or fails because of known unrelated environment issues:

```text
Do not hide it.
Record exact failure.
Run targeted fallback tests.
Mark full_tests = partial.
```

Also run import/package smoke checks if project supports them:

```bash
rtk python -m compileall src tests
rtk python -c "import sys; print(sys.version)"
```

If package build exists, run one of:

```bash
rtk python -m build --sdist --wheel
rtk python -m pip check
```

If package build not supported, mark:

```text
package_build = not_supported
```

Create:

```text
reference/full_checks_summary.csv
reference/test_failures_and_warnings.csv
presented/full_test_summary.md
logs/full_pytest_tests.log
logs/full_pytest_tests_nlpcc.log
logs/news_overlay_pytest.log
```

`full_checks_summary.csv` columns:

```text
command
status
return_code
duration_seconds
log_path
notes
```

---

## Stage 6 — Cache, Output, and Run Manifest

Create complete manifests.

Required outputs:

```text
reference/output_artifact_manifest.csv
reference/cache_and_trace_manifest.csv
reference/run_command_manifest.csv
reference/config_hash_manifest.csv
presented/output_package_status.md
```

`output_artifact_manifest.csv` columns:

```text
path
type
folder
created_or_updated
size_bytes
purpose
final_or_intermediate
notes
```

`run_command_manifest.csv` columns:

```text
run_id
command
candidate
track
year
status
return_code
duration_seconds
output_paths
notes
```

`config_hash_manifest.csv` columns:

```text
path
role
before_hash
after_hash
changed
allowed_to_change
notes
```

Show no-touch paths stayed unchanged.

---

## Stage 7 — Final Candidate Decision

Create:

```text
reference/final_candidate_decision_table.csv
presented/final_candidate_decision_summary.md
```

Columns:

```text
candidate_id
track
candidate
variant
start_status
final_status
2024_return
2024_sharpe
2024_selection_score
2025_return
2025_sharpe
2025_max_drawdown
2025_turnover
overlay_contribution_nonzero
delta_vs_no_news_return
delta_vs_no_news_sharpe
full_run_status
evidence_complete
missing_evidence
decision
reason
next_action
```

Allowed final statuses:

```text
active_next_phase
active_branch_selected
active_but_needs_more_evidence
baseline_reference_only
archived_fallback
retired_ablation_reference
blocked_missing_evidence
blocked_pipeline_noop
blocked_full_run_failed
```

Do not mark official-promotion-ready.

---

## Stage 8 — Detailed Implementation Log

This is mandatory.

Write detailed logs in two places:

```text
outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/presented/implementation_log.md
docs/implementation_logs/<timestamp>_prompt01_pipeline_repair_full_validation.md
```

The logs must include exactly these sections:

```text
A. Summary
B. Files Created
C. Files Modified
D. Files Read
E. Commands Run
F. Candidate Runs Completed
G. Pipeline Bugs Found
H. Pipeline Bugs Fixed
I. Tests Added or Updated
J. Tests Run
K. Failed / Blocked Runs
L. Official Runtime Config Status
M. 2025 Tune Check
N. Hidden 2026 Check
O. Artifacts
P. Caveats
Q. Next Steps
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
Prompt01 status:
  <pass/partial/fail/blocked>

Phase folder:
  outputs/reports/focused_candidate_optimisation/prompt01_pipeline_repair_full_validation/

RTK used?
  <yes/no>

AGENTS.md updated?
  <yes/no/created/blocked>
  evidence:
    <paths>

Pipeline fixed?
  G15B:
    <fixed/blocked/retired/inconclusive>
  Track A:
    <resolved/unresolved>
  G21B:
    <full_run_complete/full_run_failed/missing_exact_impl>

Full runs:
  2024:
    <complete/partial/failed>
  frozen 2025:
    <complete/partial/failed>

Full tests:
  tests/test_nlpcc/test_news_overlay:
    <pass/fail/not_run>
  tests/test_nlpcc:
    <pass/fail/not_run>
  tests:
    <pass/fail/partial/not_run>

Official runtime changed?
  <yes/no>

2025 tuned?
  <yes/no>

Hidden 2026 used?
  <yes/no>

Final candidate decision:
  Track A:
    <summary>
  Track B:
    <summary>

Main blockers:
  <list>

Main artifacts:
  <paths>

Readiness:
  <ready_for_parity_prep / partial_missing_evidence / blocked_pipeline_noop / blocked_full_run_failed / not_ready_repo_state_unclear>

Best next action:
  <one specific action>
```
