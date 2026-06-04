# Prompt20 — Repository Wrap-Up, Deep Cleanup, Current-State Dossier, and News/Text Overlay Workflow Preparation

## Role

You are a senior research-engineering lead, repository auditor, reproducibility reviewer, AI-usage-workflow architect, and technical documentation lead.

You are continuing the NLPCC 2026 Shared Task 4 project after Prompt19.

This prompt is **not** a new model-development prompt. Do **not** implement a new NewsEnhance/transformer overlay in this prompt. Do **not** run another large grid search unless needed for a tiny smoke verification. Do **not** reopen official final candidate selection.

Your job is to wrap up the current repository state, clean the repository/output structure, preserve top methods properly, and produce an in-depth current-status dossier so that a **separate next-stage AI-usage workflow** can be launched for news/text processing and news-overlay research.

Use the uploaded/reference workflow document:

```text
A_Structured_AI_Usage_Workflow_Documentation.tex
```

as a methodological guide for the next-stage workflow. In particular, reflect its staged structure:

```text
Stage 1 — Discuss
Stage 2 — Research
Stage 3 — Project Initialisation
Stage 4 — Execution
Stage 5 — Manual Check, Log Review, and Fixes
```

Adapt that workflow to the next NLPCC news/text/news-overlay phase.

---

## High-Level Objectives

Prompt20 has five objectives.

### Objective A — Freeze the Current Official State

Confirm and preserve the current official runtime state from Prompt18/Prompt19:

```text
Track A primary:
  p18_rp_macro_w10_s5

Track A fallback:
  p18_rp_macro_w40_s5

Track B primary:
  p18_leeqa_sector_k5_temp35

Track B fallback:
  p18_s1_sector_t35_v30_w20
```

Do not change the official runtime selection.

### Objective B — Preserve 3–5 Top Methods per Track

Create a clear preserved-candidate layer for 3–5 top methods per track, separate from the official runtime.

This is for:

```text
- reproducibility;
- later ablation;
- system report;
- future reruns;
- future News/Text/Overlay research baselines.
```

### Objective C — Deep Cleanup of Outputs and Temporary Artifacts

Clean and rationalise the repository/output structure:

```text
- identify stale output folders;
- separate final reports from runtime caches;
- archive or delete generated clutter safely;
- keep essential evidence;
- keep package zips;
- keep final compact reports;
- ensure raw data and source files are not touched.
```

### Objective D — In-Depth Current Repo Status Dossier

Produce a detailed current-state report covering:

```text
- final candidate status;
- preserved methods;
- stage-by-stage implementation status;
- repo/package status;
- report/evidence inventory;
- cleanup inventory;
- known risks;
- what should and should not be claimed;
- exact readiness level.
```

### Objective E — Prepare Next-Stage News/Text/News-Overlay AI Workflow

Do not implement the next stage yet. Instead, prepare a structured plan and prompt kit for a future phase focused on:

```text
- stronger news/text processing;
- transformer-based or hybrid news embeddings;
- news attention index;
- event impact scoring;
- ETF/sector news sensitivity;
- gated news overlay;
- ablations and validation;
- 2024 tune / 2025 test discipline;
- official-server validation if a candidate is promoted.
```

This next-stage workflow should be organised according to the uploaded AI-usage workflow document.

---

## Current Ground Truth to Preserve

Treat this as current ground truth unless repository files prove otherwise.

Prompt19 reported:

```text
Readiness:
  Ready for final human submission review.

Prompt18 verification:
  9/9 Prompt18 claims passed.

2024 tuning/training:
  Prompt19 reused verified Prompt18 320-row full-2024 official-semantics grid.

One-year tune/test:
  Track A research top: p18_rp_macro_w10_s5.
  Track B research top: p18_s1_sector_t35_v30_w20.
  Analytical only.

Official final selection:
  Preserved from Prompt18.
  Prompt19 tuned aliases are research-only.

News usage:
  Track B primary p18_leeqa_sector_k5_temp35 has material rule-based news usage.
  Track A final candidates are no-news.
  Track B fallback is no-news.

Locked 2025:
  26 rows, all strong, no parameter changes after freeze.

Parity:
  Local parity rows: 9.
  Official parity rows: 5.
  Official statuses: pass.

Packages:
  official_runtime package passed.
  reproducibility package passed.
```

Prompt19 package paths were reported as:

```text
.var/prompt19/packages/prompt19_official_runtime_20260603_085804.zip
.var/prompt19/packages/prompt19_reproducibility_20260603_085805.zip
```

The human owner has manually verified the official-server smoke test. Record this fact in Prompt20 reports if confirmed in the current session context.

---

## Official Constraints to Preserve

Preserve exactly:

```text
- 2024 data is for training / construction / tuning only.
- 2025 public-A data is test / locked evaluation only.
- Hidden 2026 data must not be used.
- 2025 must not be used for parameter tuning.
- Current-day close/high/low/return must not be used before decision time.
- Current-day open may be used if officially available.
- Same-day news is usable only under the official timestamp cutoff.
- Transaction friction is 0.01%.
- Raw official data must not be modified or redistributed.
- Final runtime must retain deterministic no-model / no-API fallback.
- Do not silently download models.
- Do not include Hugging Face model binaries in the official runtime package.
- Do not delete source code, configs, tests, docs, official starter files, or raw official data.
```

---

## Mandatory Files to Read First

Read these before changing anything.

### Workflow Reference

```text
A_Structured_AI_Usage_Workflow_Documentation.tex
```

Use it to structure the next-stage AI-usage workflow plan.

### Prompt19 Presented Reports

```text
outputs/reports/prompt19/presented/executive_summary.md
outputs/reports/prompt19/presented/final_readiness_report.md
outputs/reports/prompt19/presented/final_recommendation.md
outputs/reports/prompt19/presented/tuner_training_summary.md
outputs/reports/prompt19/presented/one_year_tune_test_summary.md
outputs/reports/prompt19/presented/news_usage_summary.md
outputs/reports/prompt19/presented/locked_2025_test_summary.md
outputs/reports/prompt19/presented/final_package_summary.md
outputs/reports/prompt19/presented/final_system_report_draft.md
outputs/reports/prompt19/presented/submission_handoff_checklist.md
```

### Prompt19 Reference Reports

```text
outputs/reports/prompt19/reference/tuner_2024_results.csv
outputs/reports/prompt19/reference/tuner_2024_ranking.csv
outputs/reports/prompt19/reference/tuned_candidate_freeze_2024_only.csv
outputs/reports/prompt19/reference/one_year_tune_test_leaderboard.csv
outputs/reports/prompt19/reference/one_year_tune_test_trackA.csv
outputs/reports/prompt19/reference/one_year_tune_test_trackB.csv
outputs/reports/prompt19/reference/news_usage_trace_audit.csv
outputs/reports/prompt19/reference/news_ablation_report.csv
outputs/reports/prompt19/reference/locked_2025_test_results.csv
outputs/reports/prompt19/reference/final_local_parity.csv
outputs/reports/prompt19/reference/final_official_server_parity.csv
outputs/reports/prompt19/reference/package_manifest_audit.csv
outputs/reports/prompt19/reference/final_candidate_paths.csv
```

### Prompt19 Implementation Log

```text
docs/implementation_logs/20260603_165807_prompt19_tuner_news_cleanup_report_handoff.md
```

### Prompt18 Reports for Final Official Evidence

```text
outputs/reports/prompt18/presented/final_submission_readiness_report.md
outputs/reports/prompt18/presented/final_recommendation.md
outputs/reports/prompt18/presented/big_grid_search_summary.md
outputs/reports/prompt18/reference/big_grid_2024_scores.csv
outputs/reports/prompt18/reference/big_grid_trackA_ranking.csv
outputs/reports/prompt18/reference/big_grid_trackB_ranking.csv
outputs/reports/prompt18/reference/locked_2025_scores.csv
outputs/reports/prompt18/reference/official_server_parity.csv
```

### Current Configs / Code

```text
configs/prompt18_final_candidates.json
configs/prompt19_tuned_candidates.json

configs/systems/prompt18_track_a_primary.yaml
configs/systems/prompt18_track_a_fallback.yaml
configs/systems/prompt18_track_b_primary.yaml
configs/systems/prompt18_track_b_fallback.yaml

configs/systems/prompt19_tuned_track_a_primary.yaml
configs/systems/prompt19_tuned_track_a_fallback.yaml
configs/systems/prompt19_tuned_track_b_primary.yaml
configs/systems/prompt19_tuned_track_b_fallback.yaml

NLPCC_tasks/agent_platform/agents/build_agent.py
NLPCC_tasks/server_platform/
NLPCC_tasks/logs.py

src/nlpcc/
src/tools/
scripts/
tests/
docs/
outputs/
.var/
```

---

## Artifact and Reporting Policy

Prompt20 must write reports under:

```text
outputs/reports/prompt20/
```

Use this exact structure:

```text
outputs/reports/prompt20/
  README.md

  progress/
    progress_00_context_reconstruction.md
    progress_01_preserved_candidate_selection.md
    progress_02_preserved_candidate_configs.md
    progress_03_output_inventory.md
    progress_04_cleanup_execution.md
    progress_05_current_repo_status_dossier.md
    progress_06_next_stage_workflow_plan.md
    progress_07_package_and_handoff_check.md
    run_log.md

  presented/
    executive_summary.md
    preserved_candidate_summary.md
    cleanup_summary.md
    current_repo_status_report.md
    current_repo_status_table.md
    evidence_inventory_summary.md
    next_stage_news_text_overlay_workflow.md
    next_stage_prompt_plan.md
    final_wrapup_recommendation.md

  reference/
    candidate_preservation_manifest.md
    candidate_preservation_manifest.csv
    trackA_preserved_candidates.csv
    trackB_preserved_candidates.csv
    preserved_config_audit.md
    preserved_config_audit.csv
    output_folder_inventory.csv
    output_folder_inventory.md
    cleanup_manifest.csv
    cleanup_manifest.md
    evidence_inventory.csv
    evidence_inventory.md
    repo_status_matrix.csv
    repo_status_matrix.md
    package_handoff_audit.csv
    package_handoff_audit.md
    next_stage_workflow_map.md
    next_stage_prompt_backlog.md
```

Large temporary work must go under:

```text
.var/prompt20/
  inventory/
  cleanup_archive/
  preserved_candidates/
  packages/
  logs/
```

Do not create new large files under `outputs/` except compact reports and CSVs.

---

## Required Implementation Log

Create:

```text
docs/implementation_logs/<timestamp>_prompt20_wrapup_cleanup_status_next_workflow.md
```

Use exactly:

```md
# Implementation Log: prompt20 - wrapup_cleanup_status_next_workflow

## Created

## Summary

## Files Changed

## Context Reconstruction

## Preserved Candidate Layer

## Output Inventory

## Cleanup Execution

## Current Repo Status Dossier

## Evidence Inventory

## Package / Handoff Check

## Next-Stage Workflow Plan

## Tests / Checks

## Caveats

## Artifacts

## Next Steps
```

---

# Part A — Context Reconstruction

## Objective

Reconstruct the final Prompt19 state and verify that no new implementation work is needed before wrap-up.

## Tasks

1. Verify official final candidates.
2. Verify Prompt19 readiness report.
3. Verify package paths.
4. Verify manual official-server smoke status if mentioned by the user.
5. Verify final system report draft exists.
6. Verify submission handoff checklist exists.
7. Verify final candidate configs exist and match final recommendation.
8. Verify Prompt19 tuned configs are research-only.
9. Identify which top candidates exist only as CSV/report rows.
10. Identify whether current repo preserves 3–5 top methods per track as runnable configs.

## Required Report

```text
outputs/reports/prompt20/progress/progress_00_context_reconstruction.md
```

Use:

| Item | Expected | Actual | Status | Notes |
|---|---|---|---|---|

Status values:

```text
pass
partial
fail
blocked
not_applicable
```

---

# Part B — Preserve 3–5 Top Methods per Track

## Objective

Create an explicit preserved-candidate layer with runnable configs and metadata for 3–5 top methods per track.

This is a wrap-up and reproducibility task, not an official runtime change.

## Selection Sources

Use:

```text
outputs/reports/prompt18/reference/big_grid_trackA_ranking.csv
outputs/reports/prompt18/reference/big_grid_trackB_ranking.csv
outputs/reports/prompt19/reference/one_year_tune_test_trackA.csv
outputs/reports/prompt19/reference/one_year_tune_test_trackB.csv
outputs/reports/prompt19/reference/tuner_2024_ranking.csv
```

## Required Track A Candidate Pool

Preserve these if available:

```text
p18_rp_macro_w10_s5
p18_rp_macro_w40_s5
p18_rp_macro_w20_s5
p18_bsa_macro_t10_g65
p18_rp_macro_w60_s5
```

If unavailable, choose the next best Track A candidates from verified rankings and document substitutions.

## Required Track B Candidate Pool

Preserve these if available:

```text
p18_leeqa_sector_k5_temp35
p18_s1_sector_t35_v30_w20
p18_leeqa_sector_k5_temp20
p18_leeqa_sector_k5_temp70
p18_leeqa_sector_k3_temp20
```

If unavailable, choose the next best Track B candidates from verified rankings and document substitutions.

## Config Layout

Create or update:

```text
configs/preserved_candidates/
  README.md
  manifest.json
  manifest.csv

  track_a/
    <candidate>.yaml

  track_b/
    <candidate>.yaml
```

Use actual candidate names/config names if they differ from the expected names.

## Manifest Requirements

The manifest must include:

```text
candidate_name
track
family
role
source_prompt
source_rank
source_score
2024_return
2024_sharpe
2025_return
2025_sharpe
text_mode
news_dependency
runtime_dependency
config_path
config_hash
official_runtime_candidate
preserved_for
notes
```

`preserved_for` values:

```text
official_runtime
fallback
ablation
research_comparator
future_news_overlay_baseline
```

## Required Reports

```text
outputs/reports/prompt20/progress/progress_01_preserved_candidate_selection.md
outputs/reports/prompt20/progress/progress_02_preserved_candidate_configs.md
outputs/reports/prompt20/reference/candidate_preservation_manifest.md
outputs/reports/prompt20/reference/candidate_preservation_manifest.csv
outputs/reports/prompt20/reference/trackA_preserved_candidates.csv
outputs/reports/prompt20/reference/trackB_preserved_candidates.csv
outputs/reports/prompt20/reference/preserved_config_audit.md
outputs/reports/prompt20/reference/preserved_config_audit.csv
outputs/reports/prompt20/presented/preserved_candidate_summary.md
```

Use:

| Candidate | Track | Family | Role | 2024 Score | 2025 Test | News Mode | Config Path | Config Exists? | Official Runtime? | Preserve Reason |
|---|---|---|---|---:|---|---|---|---|---|---|

---

# Part C — Output Folder Inventory

## Objective

Inventory all output and runtime-artifact locations so cleanup is deliberate and safe.

## Inspect

```text
outputs/
outputs/reports/
outputs/submissions/
outputs/models/
outputs/pytest_cache/
outputs/pytest_tmp/

.var/
.var/prompt13/
.var/prompt14/
.var/prompt15/
.var/prompt16/
.var/prompt17/
.var/prompt17b/
.var/prompt18/
.var/prompt19/
.var/prompt20/

docs/reports/
docs/implementation_logs/
configs/
configs/preserved_candidates/
```

## Required Classification

Classify each folder/file group as:

```text
keep_final_evidence
keep_historical_evidence
keep_package
archive_to_var_prompt20
delete_generated_cache
delete_temp
manual_review
do_not_touch_raw_data
source_or_config_keep
```

## Required Reports

```text
outputs/reports/prompt20/progress/progress_03_output_inventory.md
outputs/reports/prompt20/reference/output_folder_inventory.csv
outputs/reports/prompt20/reference/output_folder_inventory.md
```

Use:

| Path | Type | Size | File Count | Classification | Reason | Safe Action | Notes |
|---|---|---:|---:|---|---|---|---|

---

# Part D — Cleanup Execution

## Objective

Clean generated clutter without damaging evidence, source, configs, reports, packages, or raw data.

## Cleanup Rules

Do not delete:

```text
raw official data
NLPCC_tasks/dataset/
source code
configs
tests
docs
official starter files
final Prompt18 reports
final Prompt19 reports
Prompt20 reports
official runtime package
reproducibility package
implementation logs
candidate manifests
```

Safe deletion targets:

```text
__pycache__/
*.pyc
.pytest_cache/
.mypy_cache/
.ruff_cache/
.cache/
outputs/pytest_cache/
outputs/pytest_tmp/
temporary package extraction folders
temporary benchmark scratch files
temporary official-server session files
temporary generated logs if already summarised
```

Archive instead of delete when unsure:

```text
.var/prompt20/cleanup_archive/
```

Prior prompt `.var/` folders should generally be kept if they contain evidence, but remain package-excluded. If they are very large and fully summarised, archive or mark for manual deletion rather than silently deleting.

## Required Reports

```text
outputs/reports/prompt20/progress/progress_04_cleanup_execution.md
outputs/reports/prompt20/reference/cleanup_manifest.csv
outputs/reports/prompt20/reference/cleanup_manifest.md
outputs/reports/prompt20/presented/cleanup_summary.md
```

Use:

| Path | Size | Action | Reason | Evidence Preserved? | Risk | Notes |
|---|---:|---|---|---|---|---|

Action values:

```text
keep
delete_generated_cache
delete_temp
archive_to_var_prompt20
manual_review
blocked
```

---

# Part E — Evidence Inventory

## Objective

Create a durable map of all important evidence so the next session does not need to rediscover the whole project.

## Required Evidence Categories

Inventory:

```text
official final configs
preserved candidate configs
official runtime package
reproducibility package
Prompt18 big-grid evidence
Prompt18 official parity evidence
Prompt19 tuner evidence
Prompt19 one-year tune/test evidence
Prompt19 news-usage evidence
Prompt19 locked 2025 evidence
Prompt19 cleanup/package evidence
final system report draft
submission handoff checklist
implementation logs
```

## Required Reports

```text
outputs/reports/prompt20/reference/evidence_inventory.csv
outputs/reports/prompt20/reference/evidence_inventory.md
outputs/reports/prompt20/presented/evidence_inventory_summary.md
```

Use:

| Evidence Item | Category | Path | Status | Why It Matters | Use In Next Stage |
|---|---|---|---|---|---|

---

# Part F — Current Repo Status Dossier

## Objective

Generate a detailed status dossier for future sessions.

## Required Reports

```text
outputs/reports/prompt20/progress/progress_05_current_repo_status_dossier.md
outputs/reports/prompt20/reference/repo_status_matrix.csv
outputs/reports/prompt20/reference/repo_status_matrix.md
outputs/reports/prompt20/presented/current_repo_status_report.md
outputs/reports/prompt20/presented/current_repo_status_table.md
```

## `current_repo_status_report.md` Structure

Use exactly:

```md
# Current Repository Status Report — After Prompt20 Wrap-Up

## 1. Executive Verdict

## 2. Official Final Runtime State

## 3. Preserved Candidate Layer

## 4. Track A Status

## 5. Track B Status

## 6. Stage 1 News Processing Status

## 7. Stage 2 Text Storage Status

## 8. Stage 3 Trade/Price Processing Status

## 9. Stage 4 Agent Status

## 10. Execution and Official Adapter Status

## 11. Backtester / Replay Status

## 12. Tuning / Optimisation Status

## 13. Official-Server Validation Status

## 14. Package Status

## 15. Cleanup Status

## 16. Evidence Inventory

## 17. Known Risks

## 18. What Can Be Claimed

## 19. What Must Not Be Claimed

## 20. Recommended Next Stage
```

## Stage Status Table

Use:

| Layer | Status | Key Files | Evidence | Remaining Risk | Next-Stage Relevance |
|---|---|---|---|---|---|

---

# Part G — Package and Handoff Check

## Objective

Verify final handoff artifacts after cleanup.

## Tasks

1. Confirm official runtime package still exists.
2. Confirm reproducibility package still exists.
3. Confirm preserved-candidate configs are included or scheduled for inclusion in reproducibility package.
4. Confirm official runtime package remains minimal.
5. Confirm no raw data/model binaries are in package manifests if package audits are available.
6. Confirm final system report draft and handoff checklist exist.
7. Record the user’s manual official-server smoke verification if applicable.

## Required Reports

```text
outputs/reports/prompt20/progress/progress_07_package_and_handoff_check.md
outputs/reports/prompt20/reference/package_handoff_audit.csv
outputs/reports/prompt20/reference/package_handoff_audit.md
```

Use:

| Item | Path | Expected | Status | Notes |
|---|---|---|---|---|

---

# Part H — Next-Stage News/Text/Overlay Workflow Plan

## Objective

Prepare a separate next-stage workflow for news/text/news-overlay research, but do not implement it here.

Use the uploaded AI workflow document structure:

```text
Stage 1 — Discuss
Stage 2 — Research
Stage 3 — Project Initialisation
Stage 4 — Execution
Stage 5 — Manual Check, Log Review, and Fixes
```

## Required Next-Stage Theme

The next-stage/round of AI usage should investigate:

```text
- stronger rule-based news extraction;
- transformer-based Chinese financial news embeddings;
- event taxonomy and event magnitude;
- news attention index;
- ETF/sector news sensitivity;
- event-triggered overlay;
- attention mechanism over news items and assets;
- whether news materially improves Track A or Track B;
- strict 2024 tune / 2025 test discipline;
- official-server parity before any promotion.
```

## Required Reports

```text
outputs/reports/prompt20/progress/progress_06_next_stage_workflow_plan.md
outputs/reports/prompt20/reference/next_stage_workflow_map.md
outputs/reports/prompt20/reference/next_stage_prompt_backlog.md
outputs/reports/prompt20/presented/next_stage_news_text_overlay_workflow.md
outputs/reports/prompt20/presented/next_stage_prompt_plan.md
```

## `next_stage_news_text_overlay_workflow.md` Structure

Use:

```md
# Next-Stage Workflow — News/Text Processing and News Overlay

## 1. Purpose

## 2. Starting Point After Prompt20

## 3. Stage 1 — Discuss

## 4. Stage 2 — Research

## 5. Stage 3 — Project Initialisation

## 6. Stage 4 — Execution

## 7. Stage 5 — Manual Check, Log Review, and Fixes

## 8. Candidate Research Questions

## 9. Proposed News/Text Modules

## 10. Proposed News Overlay Modules

## 11. Evaluation Protocol

## 12. Risk Controls

## 13. Prompt Backlog

## 14. Recommended First Next Prompt
```

## Prompt Backlog

Create a backlog with at least:

```text
Prompt21A — News/Text Deep Research and Design Space
Prompt21B — Repo Localisation for News/Text Pipeline
Prompt22 — News Feature Inventory and Trace Audit
Prompt23 — News Attention Index MVP
Prompt24 — Transformer Embedding Offline Cache
Prompt25 — Event Impact and ETF Sensitivity Modelling
Prompt26 — Gated News Overlay Implementation
Prompt27 — 2024 Tune / 2025 Test Evaluation
Prompt28 — Official-Server Validation and Candidate Promotion Audit
```

For each backlog prompt, include:

```text
objective
read-first files
deliverables
do-not-do constraints
expected reports
```

---

# Part I — Final Wrap-Up Recommendation

## Objective

Produce the final Prompt20 recommendation.

## Required Presented Reports

```text
outputs/reports/prompt20/presented/executive_summary.md
outputs/reports/prompt20/presented/final_wrapup_recommendation.md
outputs/reports/prompt20/README.md
```

## `final_wrapup_recommendation.md`

Use:

```md
# Prompt20 Final Wrap-Up Recommendation

## 1. Executive Verdict

## 2. Official Runtime Selection

## 3. Preserved Candidate Layer

## 4. Cleanup Result

## 5. Current Repo Status

## 6. Evidence Inventory

## 7. Package / Handoff Status

## 8. Next-Stage Workflow Prepared

## 9. What Can Be Claimed

## 10. What Must Not Be Claimed

## 11. Recommended Next Prompt
```

---

## Constraints

- Do not implement NewsEnhance in Prompt20.
- Do not run another large grid search.
- Do not reopen official final selection.
- Do not delete raw official data.
- Do not delete source/config/test/docs/official starter files.
- Do not remove final Prompt18/Prompt19 evidence.
- Do not remove package zips.
- Do not remove implementation logs.
- Do not include raw data or model binaries in any package.
- Do not claim new performance improvements.
- Do not claim news overlay exists unless it already exists.
- Archive questionable generated clutter instead of deleting it.
- Preserve official runtime and research reproducibility separation.
- Keep the next-stage news/text/news-overlay plan as a workflow plan, not an implementation.

---

## Expected Final Assistant Response

After completing Prompt20, respond with:

1. readiness verdict;
2. whether official runtime was unchanged;
3. whether 3–5 candidates per track were preserved as runnable configs;
4. preserved Track A list;
5. preserved Track B list;
6. cleanup summary;
7. output-folder inventory summary;
8. current repo status dossier path;
9. evidence inventory path;
10. package/handoff audit status;
11. next-stage news/text/news-overlay workflow path;
12. proposed Prompt21A/21B direction;
13. remaining risks;
14. final recommended action.
