# Prompt00 — Focused Candidate Optimisation and Evidence Repair

## Phase Name

Use this phase name everywhere:

```text
Prompt00 — Focused Candidate Optimisation and Evidence Repair
```

Use this folder slug everywhere:

```text
focused_candidate_optimisation
```

This is the next phase **after News Overlay**.

It must be parallel to `news_overlay`, not inside it.

Correct reports tree:

```text
outputs/reports/
  news_overlay/
  focused_candidate_optimisation/
```

All phase outputs must go under:

```text
outputs/reports/focused_candidate_optimisation/
```

Required folder layout:

```text
outputs/reports/focused_candidate_optimisation/
  presented/
  reference/
  progress/
```

Folder meaning:

```text
presented/
  Human-readable final summaries.
  Markdown reports only unless a chart is needed.
  No raw huge logs.

reference/
  CSV, JSON, YAML, manifests, metric tables, check summaries.
  This is the audit source.

progress/
  Intermediate notes, run logs, partial debug outputs, scratch run records.
  This is not final evidence unless later copied into reference or presented.
```

Do not create new phase outputs under:

```text
outputs/reports/news_overlay/
```

Allowed only for reading old evidence:

```text
outputs/reports/news_overlay/prompt27_wrapup/**
outputs/reports/news_overlay/prompt26_complex_synthetic_retest/**
outputs/reports/news_overlay/prompt25_top8_minor_enhancement/**
outputs/reports/news_overlay/prompt23/**
```

Allowed durable docs exception:

```text
docs/implementation_logs/<timestamp>_prompt00_focused_candidate_optimisation.md
```

This implementation log may be written as a durable index only. It must point back to:

```text
outputs/reports/focused_candidate_optimisation/
```

---

## Role

You are GPT-5.5 Extended Thinking / xhigh acting as a senior quantitative research engineer, Chinese financial NLP engineer, repo-state auditor, and model-risk reviewer.

This is a repo execution prompt.

Use **caveman English** in all reports and final response:

```text
Short words.
Clear verbs.
No fancy claim.
Say pass, fail, missing, blocked.
If evidence not there, say missing.
If code not run, say not run.
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

Do not ask broad questions. Do best effort with repo state.

---

## Mission

Start the next phase after News Overlay Prompt27.

This phase is:

```text
Focused Candidate Optimisation and Evidence Repair
```

Not broad search.

Not official promotion.

Not full Prompt23 rerun.

Main job:

```text
1. repair missing evidence;
2. verify real news overlay contribution;
3. run focused 2024-only tune/diagnostic;
4. run frozen 2025 only after config freeze;
5. decide next candidate status;
6. write clean CSV/MD evidence in the new parallel phase folder.
```

---

## Source of Truth

Read these first if present:

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
```

If file missing, mark missing. Do not invent.

Prompt27 local truth:

```text
Track A active:
  A1 G12A V3 — N2345/I256/S13 + H4
  A2 G11A V0 — N13/I6/S13
  A0 G00A — N0/I0/S0 no-news reference only

Track B active:
  B1 G15B V0 — N4/I6/S2
  B2 G15B V4 — N4/I6/S2 + H1+H5
  B3 G21B repaired/lite — N2345/I256/S5 with consensus shrink + BL-view confidence cap
  B0 G00B — N0/I0/S0 no-news reference only

Archived fallback:
  G14B V4 — N5/I5/S2 + H1+H5
  G10B V5 — N2/I2/S2 + H1+H2+H4+H5

Retired:
  G12B / G12B_lite — ablation/report only
  G10A — simple Track A ablation/reference only
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
No official runtime config edit.
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

Do not edit unless explicitly needed:

```text
configs/preserved_candidates/**
NLPCC_tasks/agent_platform/agents/build_agent.py
raw data
model binaries
official runtime evidence folders
```

If official runtime config changes by accident, revert or mark blocked.

---

## Stage 0 — Create Parallel Phase Folder

Create exactly:

```text
outputs/reports/focused_candidate_optimisation/presented/
outputs/reports/focused_candidate_optimisation/reference/
outputs/reports/focused_candidate_optimisation/progress/
```

Write first file:

```text
outputs/reports/focused_candidate_optimisation/progress/phase_folder_created.md
```

It must state:

```text
phase_name
phase_slug
created_at
repo_root
rtk_available
is_parallel_to_news_overlay = true
```

Do not write new phase outputs inside:

```text
outputs/reports/news_overlay/
```

---

## RTK Preflight

Run first:

```bash
rtk --version
rtk git status
rtk git diff --name-only
```

Record into:

```text
outputs/reports/focused_candidate_optimisation/reference/preflight_checks.csv
outputs/reports/focused_candidate_optimisation/presented/preflight_summary.md
```

If `rtk --version` fails:

```text
status = blocked_rtk_unavailable
stop before repo changes except the phase folder if already made
final response must say blocked_rtk_unavailable
```

---

## Stage 1 — Repo and Evidence Intake

Read Prompt27 and Prompt26 outputs.

Create:

```text
outputs/reports/focused_candidate_optimisation/reference/input_evidence_manifest.csv
outputs/reports/focused_candidate_optimisation/reference/candidate_start_state.csv
outputs/reports/focused_candidate_optimisation/presented/current_state_intake_summary.md
```

`candidate_start_state.csv` must include:

```text
candidate_id
track
candidate
variant
stack
role
status_from_prompt27
has_2024_evidence
has_frozen_2025_evidence
overlay_contribution_nonzero
known_gap
required_action
source_file
notes
```

Use exact values if present. If not present, write:

```text
missing
```

---

## Stage 2 — Goal B First: G15B Evidence Repair

Run this before Goal A and Goal C.

Reason:

```text
G15B is Track B anchor.
G15B V0 has 2024/2025 metric evidence but overlay contribution recorded as zero.
G15B V4 has 2024 evidence but missing exact frozen 2025.
```

### Candidates

```text
B1 G15B V0 — N4/I6/S2
B2 G15B V4 — N4/I6/S2 + H1+H5
B0 G00B — no-news reference
```

### Tasks

1. Inspect G15B V0 daily traces.
2. Confirm whether overlay is truly zero or only instrumentation missing.
3. Required trace fields:

```text
date
active_news_days
overlay_active
mean_abs_overlay
max_abs_overlay
raw_news_signal_nonzero
post_gate_signal_nonzero
final_weight_delta_vs_G00B
trade_delta_vs_G00B
fallback_used
fallback_reason
```

4. If V0 overlay is truly zero, rerun or fix trace instrumentation only if safe and bounded.
5. Run exact G15B V4 frozen 2025 test.
6. Do not tune V4 on 2025.
7. Compare V0, V4, and G00B.

### Required outputs

```text
outputs/reports/focused_candidate_optimisation/reference/goal_b_g15b_v0_trace_audit.csv
outputs/reports/focused_candidate_optimisation/reference/goal_b_g15b_v4_frozen_2025.csv
outputs/reports/focused_candidate_optimisation/reference/goal_b_g15b_comparison.csv
outputs/reports/focused_candidate_optimisation/presented/goal_b_g15b_branch_decision.md
```

### Decision labels

Use exactly one:

```text
g15b_v0_active
g15b_v4_active
g15b_inconclusive_missing_evidence
g15b_blocked_zero_overlay
```

Success gate:

```text
V0 or V4 must show real nonzero overlay contribution.
V0 or V4 must have frozen 2025 metric evidence.
V0 or V4 must not be worse than G00B by unexplained material amount.
```

---

## Stage 3 — Goal A: Track A Focused Optimisation

### Candidates

```text
A1 G12A V3 — N2345/I256/S13 + H4
A2 G11A V0 — N13/I6/S13
A0 G00A — no-news reference
```

### Tasks

1. Validate G12A composite stability.
2. Validate H4 macro overlay discipline.
3. Validate G11A aspect-tone macro overlay behaviour.
4. Compare each to G00A.
5. Inspect whether overlay contribution is actually nonzero.
6. If overlay is zero, do not overclaim news usage.
7. Tune only on 2024 if any tiny safe parameter needs repair.
8. Run frozen 2025 only after config freeze.

### Required outputs

```text
outputs/reports/focused_candidate_optimisation/reference/goal_a_track_a_metrics.csv
outputs/reports/focused_candidate_optimisation/reference/goal_a_overlay_trace_audit.csv
outputs/reports/focused_candidate_optimisation/reference/goal_a_vs_g00a_deltas.csv
outputs/reports/focused_candidate_optimisation/presented/goal_a_track_a_summary.md
```

### Decision labels

Use exactly one per candidate:

```text
continue_active
continue_but_news_contribution_unproven
downgrade_to_ablation
blocked_missing_evidence
```

---

## Stage 4 — Goal C: G21B Repaired/Lite Real Validation

Run after Goal B baseline evidence is done.

### Candidates

```text
B3 G21B repaired/lite — N2345/I256/S5
B0 G00B — no-news reference
optional archived references:
  G14B V4
  G10B V5
```

Use G14B/G10B only for comparison. Do not activate them unless active candidate fails and evidence says so.

### Required repaired/lite controls

Verify or implement only if missing:

```text
N2345 consensus shrink
I256 dominance cap
S5 BL-view confidence cap
event/evidence count required before overlay
weak-signal deadband
fallback to G00B-like no-news / S1-safe behaviour
```

Do not add new architecture.

Do not add new model.

Do not widen N2345/I256 weight search.

### Runs

```text
2024 real tune / diagnostic
freeze config
2025 frozen test
```

No 2025 tune.

### Required outputs

```text
outputs/reports/focused_candidate_optimisation/reference/goal_c_g21b_repaired_config_audit.csv
outputs/reports/focused_candidate_optimisation/reference/goal_c_g21b_repaired_2024_2025.csv
outputs/reports/focused_candidate_optimisation/reference/goal_c_g21b_component_trace.csv
outputs/reports/focused_candidate_optimisation/reference/goal_c_g21b_vs_references.csv
outputs/reports/focused_candidate_optimisation/presented/goal_c_g21b_repaired_validation.md
```

### Decision labels

Use exactly one:

```text
continue_high_upside_candidate
continue_research_backup_only
simplify_and_retest
retire_from_selection_keep_for_ablation
blocked_missing_real_evidence
```

G21B can continue only if:

```text
real 2025 evidence exists
real overlay contribution is nonzero
comparison versus G15B/G00B is credible
blockers reduce or are explained
component attribution is interpretable
turnover/drawdown not materially worse without reason
```

Synthetic-only evidence is not enough.

---

## Stage 5 — Final Candidate Decision Table

Create:

```text
outputs/reports/focused_candidate_optimisation/reference/final_candidate_decision_table.csv
outputs/reports/focused_candidate_optimisation/presented/final_candidate_decision_summary.md
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
```

Do not mark official-promotion-ready.

---

## Stage 6 — Checks

Run compact checks using RTK:

```bash
rtk --version
rtk git status
rtk git diff --name-only
rtk python -m pytest tests/test_nlpcc/test_news_overlay -q
```

If targeted tests are needed for new code, add them and run:

```bash
rtk python -m pytest <exact_test_path> -q
```

Create:

```text
outputs/reports/focused_candidate_optimisation/reference/checks_summary.csv
outputs/reports/focused_candidate_optimisation/presented/checks_summary.md
```

`checks_summary.csv` columns:

```text
command
status
return_code
duration_seconds
notes
```

---

## Stage 7 — Final Report

Create:

```text
outputs/reports/focused_candidate_optimisation/presented/executive_summary.md
outputs/reports/focused_candidate_optimisation/presented/final_next_phase_recommendation.md
outputs/reports/focused_candidate_optimisation/presented/implementation_log.md
```

Also create durable index log:

```text
docs/implementation_logs/<timestamp>_prompt00_focused_candidate_optimisation.md
```

The durable index log must be short and must point back to:

```text
outputs/reports/focused_candidate_optimisation/
```

Final recommendation must say one of:

```text
ready_for_parity_prep
partial_missing_evidence
blocked_rtk_unavailable
blocked_official_runtime_or_data_risk
not_ready_repo_state_unclear
```

Use only one.

Do not say ready for official promotion.

---

## Final Response Format

Use caveman English.

```text
Prompt00 status:
  <pass/partial/fail/blocked>

Phase folder:
  outputs/reports/focused_candidate_optimisation/

Parallel to news_overlay?
  <yes/no>

RTK used?
  <yes/no>

Current state:
  <short summary>

Goal B - G15B:
  V0 overlay:
    <nonzero/zero/missing/inconclusive>
  V4 frozen 2025:
    <run/missing/failed>
  branch decision:
    <label>

Goal A - Track A:
  G12A:
    <decision>
  G11A:
    <decision>
  G00A:
    reference only

Goal C - G21B:
  repaired real evidence:
    <complete/missing/failed>
  decision:
    <label>

Official runtime changed?
  <yes/no>

2025 tuned?
  <yes/no>

Hidden 2026 used?
  <yes/no>

Tests/checks:
  <summary>

Main artifacts:
  <paths under outputs/reports/focused_candidate_optimisation/ only>

Readiness:
  <one allowed label>

Best next action:
  <one specific action>
```
