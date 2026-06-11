# Prompt27 — News Overlay Wrap-Up, Repo Cleanup, and Next-Phase Candidate Preparation

## Role

You are a senior research-code auditor, repo-cleanup engineer, quantitative research lead, Chinese financial NLP engineer, and implementation planner.

You are continuing after the News Overlay exploration, top-8 minor-enhancement phase, and complex-candidate synthetic retest.

This prompt is a **wrap-up and transition prompt**. Its goal is to freeze the final News Overlay candidate pool, clean and summarize the repository state, and prepare the next execution phase for focused enhancement/optimization.

Do **not** reopen broad method discovery.

---

## Goal

Wrap up the current News Overlay phase and prepare the next phase around the selected candidates:

```text
Track A active candidates:
  A1. G12A V3 — N2345/I256/S13 + H4
  A2. G11A V0 — N13/I6/S13
  A0. G00A — no-news fast baseline/reference only

Track B active candidates:
  B1. G15B V0 — N4/I6/S2, baseline/guardrail row
  B2. G15B V4 — N4/I6/S2 + H1+H5, active-enhancement diagnostic candidate
  B3. G21B-repaired / G21B-lite — N2345/I256/S5 with consensus shrink + BL-view confidence cap
  B0. G00B — no-news fast baseline/reference only
```

Important note:

```text
G15B V4 was observed in the 2024 Stage-1 enhancement matrix but was not the previously frozen 2025-selected G15B row. Prompt27 must verify or rerun G15B V4 on frozen 2025 before treating it as a final candidate.
```

Keep these archived but **not active** unless a selected candidate fails:

```text
Track B fallback/archive:
  G14B V4 — N5/I5/S2 + H1+H5
  G10B V5 — N2/I2/S2 + H1+H2+H4+H5

Retired from selection:
  G12B / G12B-lite — keep only for ablation/report reference
  G10A — keep only for simple Track A ablation/reference
```

---

## Why This Candidate Pool

Use the current evidence:

```text
- News Overlay phase generally succeeded.
- Prompt23 completed full fresh 2024 inference matrix and frozen 2025 replay.
- Top-8 minor-enhancement phase completed 48-row 2024 tune and 8-row frozen 2025 matrix.
- G12A and G11A are the main Track A news candidates.
- G15B is the strongest Track B event-label/aspect-impact candidate.
- G21B remains the high-upside complex candidate after synthetic retest; use only repaired/lite form.
- G12B should be retired from selection because synthetic/real evidence was weaker and blockers remain.
- No-news G00A/G00B remain reference baselines only, not final news methods.
```

---

## Non-Negotiable Constraints

```text
- Do not modify official runtime configs.
- Do not promote candidates automatically.
- Do not use hidden 2026 data.
- Do not tune on 2025.
- 2024 may be used for tune/selection.
- 2025 may be used only as frozen test/reporting.
- Do not download new models.
- Do not call online APIs.
- Do not copy Hugging Face model binaries into the repo or package.
- Do not delete raw data, configs, source code, tests, or implementation logs.
- Archive uncertain generated clutter instead of deleting.
- Preserve all Prompt18/19 official runtime evidence separately.
- Preserve all Prompt21–26 News Overlay evidence, but consolidate it into a clean handoff.
```

---

## Output Directory

Create Prompt27 outputs under:

```text
outputs/reports/news_overlay/prompt27_wrapup/presented/
outputs/reports/news_overlay/prompt27_wrapup/reference/
outputs/reports/news_overlay/prompt27_wrapup/progress/
```

Also create/update durable docs:

```text
docs/news_overlay/current_news_overlay_state.md
docs/news_overlay/final_candidate_pool.md
docs/news_overlay/next_phase_execution_plan.md
docs/implementation_logs/<timestamp>_prompt27_news_overlay_wrapup_next_phase_prep.md
```

---

# Stage 1 — Current Repo State Audit

## Tasks

1. Inventory current News Overlay outputs, configs, docs, tests, and implementation logs.
2. Identify final evidence folders versus superseded/interrupted folders.
3. Confirm official runtime configs are unchanged.
4. Confirm raw data and model binaries are untouched.
5. Confirm Prompt18/19 official evidence is preserved separately.
6. Confirm Prompt23/24/25/26 research evidence is preserved.
7. Confirm the selected candidate rows exist or identify exact missing rows.

## Required Outputs

```text
outputs/reports/news_overlay/prompt27_wrapup/reference/repo_state_inventory.csv
outputs/reports/news_overlay/prompt27_wrapup/reference/evidence_preservation_manifest.csv
outputs/reports/news_overlay/prompt27_wrapup/reference/official_runtime_diff_check.csv
outputs/reports/news_overlay/prompt27_wrapup/presented/current_repo_state_summary.md
```

`current_repo_state_summary.md` must answer:

```text
- What is the latest trusted News Overlay evidence?
- Which folders are final/presented?
- Which folders are superseded or partial?
- Which configs are official and must not be changed?
- Which candidates are active, archived, or retired?
```

---

# Stage 2 — Freeze Final Candidate Pool

## Tasks

Create a final candidate manifest with the selected active candidates.

Active candidate pool:

```yaml
track_a:
  - id: A1
    candidate: G12A
    variant: V3
    stack: N2345/I256/S13
    enhancement: H4
    role: main_track_a_novelty_candidate
    status: active_next_phase

  - id: A2
    candidate: G11A
    variant: V0
    stack: N13/I6/S13
    enhancement: off
    role: track_a_empirical_news_candidate
    status: active_next_phase

  - id: A0
    candidate: G00A
    variant: no_news
    stack: N0/I0/S0
    enhancement: off
    role: fast_reference_baseline_only
    status: baseline_reference

track_b:
  - id: B1
    candidate: G15B
    variant: V0
    stack: N4/I6/S2
    enhancement: H1_or_hooks_off
    role: event_label_aspect_impact_anchor
    status: active_next_phase

  - id: B2
    candidate: G15B
    variant: V4
    stack: N4/I6/S2
    enhancement: H1+H5
    role: active_enhancement_diagnostic_candidate
    status: active_but_requires_frozen_2025_verification

  - id: B3
    candidate: G21B_repaired_or_lite
    variant: repaired
    stack: N2345/I256/S5
    enhancement: consensus_shrink_plus_BL_view_confidence_cap
    role: high_upside_complex_candidate
    status: active_repair_candidate

  - id: B0
    candidate: G00B
    variant: no_news
    stack: N0/I0/S0
    enhancement: off
    role: fast_reference_baseline_only
    status: baseline_reference
```

Archived fallback:

```yaml
fallback_archive:
  - G14B V4 — N5/I5/S2 + H1+H5
  - G10B V5 — N2/I2/S2 + H1+H2+H4+H5
```

Retired:

```yaml
retired_from_selection:
  - G12B / G12B_lite — keep for ablation/report only
  - G10A — keep for simple Track A ablation/reference only
```

## Required Outputs

```text
outputs/reports/news_overlay/prompt27_wrapup/reference/final_candidate_manifest.csv
outputs/reports/news_overlay/prompt27_wrapup/reference/final_candidate_metrics.csv
outputs/reports/news_overlay/prompt27_wrapup/presented/final_candidate_pool_summary.md
docs/news_overlay/final_candidate_pool.md
```

`final_candidate_metrics.csv` must include:

```text
candidate_id
track
candidate
variant
stack
enhancement
role
status
2024_return
2024_sharpe
2024_selection_score
2025_return
2025_sharpe
2025_turnover
active_news_days
overlay_active_days
mean_abs_overlay
max_abs_overlay
delta_vs_no_news_return
delta_vs_no_news_sharpe
evidence_source
notes
```

If a candidate row is missing, do not invent metrics. Mark:

```text
missing_requires_rerun
```

Especially check:

```text
G15B V4 frozen 2025 result
G21B-repaired real 2024/2025 result
```

---

# Stage 3 — Verify Candidate Evidence and Gaps

## Tasks

1. Verify G12A V3 and G11A V0 have 2024/2025 evidence.
2. Verify G15B V0 has 2024/2025 evidence and check whether overlay contribution is nonzero.
3. Verify G15B V4 has 2024 evidence; if frozen 2025 evidence is absent, record as `requires_frozen_2025_verification`.
4. Verify G21B repaired/lite has only synthetic/diagnostic evidence unless real 2024/2025 rerun exists.
5. Verify G00A/G00B fast baseline rows exist and can be run quickly.
6. Verify G12B is retired from selection and preserved as ablation/report reference only.

## Required Outputs

```text
outputs/reports/news_overlay/prompt27_wrapup/reference/candidate_gap_analysis.csv
outputs/reports/news_overlay/prompt27_wrapup/presented/candidate_gap_summary.md
```

Gap categories:

```text
complete
requires_frozen_2025_verification
requires_real_2024_2025_retest
requires_overlay_contribution_check
baseline_reference_only
retired_from_selection
```

---

# Stage 4 — Repo Cleanup Plan

## Tasks

1. Inventory generated artifacts and caches.
2. Identify old/superseded prompt folders.
3. Identify large cache folders.
4. Identify incomplete/partial run outputs.
5. Create cleanup action plan.
6. Archive rather than delete if uncertain.
7. Keep final evidence manifests and implementation logs.

Do not delete source evidence unless explicitly safe.

## Required Outputs

```text
outputs/reports/news_overlay/prompt27_wrapup/reference/repo_cleanup_inventory.csv
outputs/reports/news_overlay/prompt27_wrapup/reference/repo_cleanup_actions.csv
outputs/reports/news_overlay/prompt27_wrapup/presented/repo_cleanup_plan.md
```

`repo_cleanup_actions.csv` must include:

```text
path
type
size_mb
status
action
safe_to_delete
archive_target
reason
evidence_preserved
notes
```

Actions:

```text
keep
archive
delete_if_archived
do_not_touch
manual_review
```

---

# Stage 5 — Next Phase Execution Plan

## Objective

Prepare the next phase: focused candidate enhancement and optimization.

Do not run the next phase yet unless this prompt explicitly asks for compact checks.

## Next phase should have three parallel goals:

### Goal A — Track A focused optimization

```text
Candidates:
  G12A V3
  G11A V0
  G00A reference only

Tasks:
  - refine G12A composite stability and H4 macro overlay discipline;
  - lightly validate G11A aspect-tone macro overlay;
  - compare against G00A reference;
  - do not force Track A parity unless improved versus controls.
```

### Goal B — Track B event-label/aspect-impact path

```text
Candidates:
  G15B V0
  G15B V4
  G00B reference only

Tasks:
  - verify G15B V0 overlay contribution is nonzero;
  - run frozen 2025 verification for G15B V4 if missing;
  - compare V0 versus V4;
  - keep the better active G15B version for next parity preparation.
```

### Goal C — G21B repaired complex path

```text
Candidates:
  G21B-repaired / G21B-lite
  G00B reference only
  G14B/G10B optional archived references

Tasks:
  - implement or verify real G21B repaired/lite candidate;
  - add consensus shrink and BL-view confidence cap;
  - run real 2024 tune and frozen 2025 test;
  - compare against G15B and reference baselines;
  - keep only if real-market evidence improves and blockers are reduced.
```

## Required Outputs

```text
outputs/reports/news_overlay/prompt27_wrapup/presented/next_phase_execution_plan.md
outputs/reports/news_overlay/prompt27_wrapup/reference/next_phase_candidate_plan.csv
docs/news_overlay/next_phase_execution_plan.md
```

---

# Stage 6 — Compact Checks

Run compact checks only:

```bash
rtk --version
rtk git status
rtk git diff --name-only
rtk python -m pytest tests/test_nlpcc/test_news_overlay -q
```

If RTK is unavailable, use standard commands and record fallback.

Do not run a full grid.

Do not run official-server parity.

## Required Outputs

```text
outputs/reports/news_overlay/prompt27_wrapup/reference/checks_summary.csv
outputs/reports/news_overlay/prompt27_wrapup/presented/checks_summary.md
```

---

# Final Recommendation Rules

Use one of:

```text
ready_for_next_phase_execution
partial_missing_candidate_evidence
not_ready_repo_state_unclear
blocked_official_runtime_or_data_risk
```

Do not mark official-promotion-ready.

---

## Final Response Format

```text
Prompt27 status:
  <pass/partial/fail>

Current repo state:
  <short summary>

Final active candidate pool:
  Track A:
    A1 <candidate / variant / stack / status>
    A2 <candidate / variant / stack / status>
    A0 <candidate / baseline / status>

  Track B:
    B1 <candidate / variant / stack / status>
    B2 <candidate / variant / stack / status>
    B3 <candidate / repaired stack / status>
    B0 <candidate / baseline / status>

Archived fallback:
  <list>

Retired from selection:
  <list>

Missing evidence:
  <list or none>

Repo cleanup:
  <summary and key action file>

Next phase plan:
  <Goal A / Goal B / Goal C summary>

Official runtime changed?
  <yes/no>

Tests/checks run:
  <commands and pass/fail>

Readiness:
  <allowed readiness label>

Most important next action:
  <specific action>
```
