# Prompt19 — Final Tuner, 1-Year Tune / 1-Year Test Ranking, News-Usage Verification, Cleanup, System Report, and Submission Handoff

## Role

You are a senior quantitative research engineer, portfolio-strategy tuner, LLM-systems architect, official-submission auditor, and system-report writer.

You are continuing the NLPCC 2026 Shared Task 4 project after Prompt18. This prompt is designed for a **fresh new session** to avoid overly long context, so you must reconstruct the current state from repository files and reports before acting.

Your job is **not** to invent new strategy families. Your job is to:

```text
1. verify the current Prompt18 final state;
2. add or complete a tuner/trainer layer for all implemented trader families;
3. run a strict 1-year tune / 1-year test protocol:
     tune/train/select parameters on full 2024 construction data;
     test the frozen 2024-tuned candidates on full 2025 public-A data;
4. use the 1-year tune / 1-year test results to rank and analyse top candidates;
5. keep the official final runtime selection as the original Prompt18 full official-server-validated 5-row/final selection unless Prompt19 discovers a correctness defect;
6. explicitly verify whether news is actually used by news-enabled traders;
7. clean temporary files, stale runtime artifacts, and generated clutter;
8. rebuild and audit final official runtime and reproducibility packages;
9. draft final system-report prose and a submission handoff checklist.
```

Be conservative. Do not claim hidden B-list readiness beyond what can be supported by 2024 construction, 2025 public-A testing, official-server parity, package audits, and source-code inspection.

---

## Critical Interpretation of “1-Year Tune / 1-Year Test”

Prompt19 must run and report a disciplined 1-year tune / 1-year test workflow:

```text
Tune / train / parameter-select:
  2024 only

Test / evaluate / generalisation-check:
  2025 only, after 2024 freeze
```

This workflow should produce a **top-candidate leaderboard** and may identify stronger research candidates.

However, the **official final selection remains the original Prompt18 final server-validated selection** unless Prompt19 finds a correctness, package, or official-parity defect.

The original Prompt18 final selection to preserve is:

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

The original Prompt18 official-server validation set also included the required 5 rows:

```text
S0 macro:
  p18_s0_macro_cash02

S1 macro:
  p18_s1_macro_m15_v30_w10_0

S1 sector:
  p18_s1_sector_t35_v20_w10

Track A primary:
  p18_rp_macro_w10_s5

Track B primary:
  p18_leeqa_sector_k5_temp35
```

When reporting Prompt19 results, maintain two separate concepts:

```text
1. 1-year tune/test top candidates:
     candidates ranked by 2024 tuning plus 2025 test performance.

2. Official final runtime selection:
     original Prompt18 final selection, preserved unless there is a correctness defect.
```

Do **not** silently replace the Prompt18 final runtime candidates just because a candidate performs better on 2025. If you propose a replacement, it must be labelled as a **research recommendation**, not the official final submission choice, unless a human explicitly approves reopening the freeze.

---

## Current Project Context

Project:

```text
NLPCC 2026 Shared Task 4:
LLM-based Investment Advisor Agents for Asset Allocation in the Chinese Market
```

Tracks:

```text
Track A / Track 1:
  Macro-Asset Allocation

Track B / Track 2:
  Sector-Rotation Allocation
```

Architecture:

```text
Stage 1 — News Processing
Stage 2 — Quantified Text Storage
Stage 3 — Trade Data Processing
Stage 4 — Final Trading Agent
Execution / Adapter Layer
Official Wrapper / Submission Layer
```

Official-facing wrapper:

```text
NLPCC_tasks/agent_platform/agents/build_agent.py
```

Reusable implementation:

```text
src/nlpcc/
```

---

## Current Ground Truth from Prompt18

Treat this as provisional ground truth until verified from files.

Prompt18 reportedly completed:

```text
- official local server startup/repair;
- Option 1 large grid search;
- 320 candidate rows;
- 160 macro candidates;
- 160 sector candidates;
- all 242 available 2024 construction dates;
- no_news and rule_based text modes;
- NumPy official-semantics batched replay;
- 2024-only candidate freeze;
- locked 2025 public-A evaluation after freeze;
- 242-date local reference-vs-batched parity for 9 selected rows;
- 243-date official-server parity for 5 required rows;
- package split into official runtime and reproducibility packages.
```

Reported final Prompt18 readiness:

```text
Ready for final submission package handoff
```

Reported final packages:

```text
.var/prompt18/packages/prompt18_official_runtime_20260601_215404.zip
.var/prompt18/packages/prompt18_reproducibility_20260601_215404.zip
```

Prompt19 must verify these claims before relying on them.

---

## Official Constraints to Preserve

Preserve exactly:

```text
- 2024 data is for training / construction / tuning only.
- 2025 public-A data is locked evaluation / test only.
- 2025 must not be used for parameter tuning.
- 2025 may be used to rank and analyse top candidates under the explicit 1-year tune / 1-year test protocol, but this must be labelled as test/generalisation analysis.
- The official final runtime selection remains the original Prompt18 final selection unless Prompt19 finds a correctness defect or a human explicitly reopens final selection.
- 2026-01-01 to 2026-06-01 is hidden B-list evaluation.
- B-list is centrally run by organisers using submitted code.
- Current-day close/high/low/return must not be used before decision time.
- Current-day open may be used if officially available.
- Same-day news is usable only under the official timestamp cutoff.
- Transaction friction is 0.01%.
- Raw official data must not be modified or redistributed.
- External models, datasets, or knowledge bases must be available before 2026 and reproducible.
- Final runtime must retain deterministic no-model / no-API fallback.
- Downloaded Hugging Face model binaries must not be included in the official runtime package.
- Do not silently download models.
```

---

## Mandatory Files to Read First

Read the latest Prompt18 reports and implementation logs first.

### Prompt18 Presented Reports

```text
outputs/reports/prompt18/presented/executive_summary.md
outputs/reports/prompt18/presented/big_grid_search_summary.md
outputs/reports/prompt18/presented/final_candidate_selection_report.md
outputs/reports/prompt18/presented/locked_2025_evaluation_summary.md
outputs/reports/prompt18/presented/official_server_validation_summary.md
outputs/reports/prompt18/presented/final_package_summary.md
outputs/reports/prompt18/presented/final_submission_readiness_report.md
outputs/reports/prompt18/presented/final_recommendation.md
```

### Prompt18 Reference Reports

```text
outputs/reports/prompt18/reference/big_grid_candidate_catalog.csv
outputs/reports/prompt18/reference/big_grid_2024_scores.csv
outputs/reports/prompt18/reference/big_grid_2024_ranking.csv
outputs/reports/prompt18/reference/big_grid_trackA_ranking.csv
outputs/reports/prompt18/reference/big_grid_trackB_ranking.csv
outputs/reports/prompt18/reference/locked_2025_scores.csv
outputs/reports/prompt18/reference/locked_2025_evaluation.csv
outputs/reports/prompt18/reference/final_parity_reference_vs_batched.csv
outputs/reports/prompt18/reference/official_server_parity.csv
outputs/reports/prompt18/reference/final_runtime_package_audit.json
outputs/reports/prompt18/reference/reproducibility_package_audit.json
outputs/reports/prompt18/reference/dependency_and_model_manifest.json
```

### Prompt18 Implementation Logs

```text
docs/implementation_logs/20260602_055111_prompt18_official_server_big_grid_final_packaging.md
docs/implementation_logs/20260603_043913_prompt18_full_horizon_rerun_addendum.md
```

### Prompt17b Reports for Historical Comparison

```text
outputs/reports/prompt17b/presented/final_status_report.md
outputs/reports/prompt17b/presented/final_recommendation.md
outputs/reports/prompt17b/presented/candidate_freeze_repair_report.md
outputs/reports/prompt17b/presented/full_horizon_search_summary.md
outputs/reports/prompt17b/presented/official_parity_closure_summary.md
outputs/reports/prompt17b/reference/full_2024_candidate_ranking.csv
outputs/reports/prompt17b/reference/locked_2025_evaluation.csv
```

### Code to Inspect

```text
NLPCC_tasks/agent_platform/agents/build_agent.py
NLPCC_tasks/server_platform/
NLPCC_tasks/logs.py

src/nlpcc/runtime/system_runner.py
src/nlpcc/stage1_news/
src/nlpcc/stage2_text_store/
src/nlpcc/stage3_trade/
src/nlpcc/stage4_agent/
src/nlpcc/execution/

src/tools/backtesting/
src/tools/experiments/
src/tools/optimiser/
src/tools/verification/

scripts/run_prompt18_big_grid.py
scripts/run_official_server_smoke.py
scripts/generate_target_tensors.py
scripts/build_text_feature_cache.py

configs/prompt18_final_candidates.json
configs/systems/prompt18_track_a_primary.yaml
configs/systems/prompt18_track_a_fallback.yaml
configs/systems/prompt18_track_b_primary.yaml
configs/systems/prompt18_track_b_fallback.yaml
configs/
tests/
```

---

## Artifact and Reporting Policy

Prompt19 must store reports under:

```text
outputs/reports/prompt19/
```

Use this exact report tree:

```text
outputs/reports/prompt19/
  README.md

  progress/
    progress_00_context_reconstruction.md
    progress_01_prompt18_verification.md
    progress_02_tuner_design.md
    progress_03_2024_tuning_run.md
    progress_04_news_usage_verification.md
    progress_05_1y_tune_1y_test_ranking.md
    progress_06_locked_2025_test.md
    progress_07_cleanup.md
    progress_08_package_rebuild.md
    progress_09_final_report_draft.md
    run_log.md

  presented/
    executive_summary.md
    prompt18_verification_summary.md
    tuner_training_summary.md
    one_year_tune_test_summary.md
    news_usage_summary.md
    locked_2025_test_summary.md
    cleanup_summary.md
    final_package_summary.md
    final_system_report_draft.md
    submission_handoff_checklist.md
    final_recommendation.md
    final_readiness_report.md

  reference/
    prompt18_claim_verification.md
    prompt18_claim_verification.csv
    final_candidate_config_audit.md
    final_candidate_config_audit.csv
    tuner_design.md
    tuner_parameter_space.csv
    tuner_2024_results.csv
    tuner_2024_ranking.md
    tuner_2024_ranking.csv
    tuned_candidate_freeze_2024_only.md
    tuned_candidate_freeze_2024_only.csv
    one_year_tune_test_leaderboard.md
    one_year_tune_test_leaderboard.csv
    one_year_tune_test_trackA.csv
    one_year_tune_test_trackB.csv
    news_usage_trace_audit.md
    news_usage_trace_audit.csv
    news_ablation_report.md
    news_ablation_report.csv
    locked_2025_test_results.csv
    locked_2025_test_report.md
    locked_2025_test_report.csv
    final_local_parity.csv
    final_official_server_parity.csv
    cleanup_manifest.md
    cleanup_manifest.csv
    package_manifest_audit.md
    package_manifest_audit.csv
    final_runtime_package_audit.json
    reproducibility_package_audit.json
    final_candidate_paths.csv
```

Large generated artifacts must be written under:

```text
.var/prompt19/
  tuner/
  target_tensors/
  generated_configs/
  one_year_tune_test/
  news_usage/
  locked_2025/
  cleanup_archive/
  official_server/
  packages/
  logs/
```

Only compact reports and CSV/JSON summaries should be copied into `outputs/reports/prompt19/`.

---

## Required Implementation Log

Create:

```text
docs/implementation_logs/<timestamp>_prompt19_tuner_news_cleanup_report_handoff.md
```

Use exactly:

```md
# Implementation Log: prompt19 - tuner_news_cleanup_report_handoff

## Created

## Summary

## Files Changed

## Prompt18 Verification

## Tuner / Trainer

## 2024 Tuning

## 1-Year Tune / 1-Year Test Ranking

## 2024 Freeze

## News Usage Verification

## Locked 2025 Test

## Local / Official Parity

## Cleanup

## Package Rebuild

## Final System Report

## Tests / Checks

## Caveats

## Artifacts

## Next Steps
```

---

# Part A — Prompt18 Verification

## Objective

Verify the current Prompt18 state before modifying anything.

## Tasks

1. Read Prompt18 reports and implementation logs.
2. Confirm package paths exist.
3. Confirm final config files exist.
4. Confirm final candidate names match across:
   ```text
   configs/prompt18_final_candidates.json
   configs/systems/prompt18_track_a_primary.yaml
   configs/systems/prompt18_track_a_fallback.yaml
   configs/systems/prompt18_track_b_primary.yaml
   configs/systems/prompt18_track_b_fallback.yaml
   outputs/reports/prompt18/presented/final_recommendation.md
   package manifests
   ```
5. Confirm official-server parity report includes required 5 rows:
   ```text
   S0 macro
   S1 macro
   S1 sector
   Track A primary
   Track B primary
   ```
6. Confirm big-grid evidence uses 2024 only for freeze.
7. Confirm locked 2025 evaluation happened after freeze.
8. Confirm official runtime package excludes raw data, models, `.var/`, `outputs/`, pycache, and accidental notebooks.

## Required Reports

Write:

```text
outputs/reports/prompt19/progress/progress_01_prompt18_verification.md
outputs/reports/prompt19/reference/prompt18_claim_verification.md
outputs/reports/prompt19/reference/prompt18_claim_verification.csv
outputs/reports/prompt19/reference/final_candidate_config_audit.md
outputs/reports/prompt19/reference/final_candidate_config_audit.csv
outputs/reports/prompt19/presented/prompt18_verification_summary.md
```

Use:

| Claim | Evidence Path | Verified? | Status | Notes |
|---|---|---|---|---|

Status values:

```text
pass
partial
fail
blocked
not_applicable
```

## Hard Gate

If final candidate configs or official runtime package are missing, stop and repair them before tuning.

---

# Part B — Tuner / Trainer Design

## Objective

Explicitly add or complete a tuner/trainer layer for all trader families.

The tuner must tune/train using **2024 data only**, freeze parameters, then test/evaluate the frozen candidates on **2025 data only**.

The tuner is not necessarily neural training. It may include:

```text
grid search
random search
successive halving
walk-forward scoring within 2024 only
parameter freezing
candidate metadata logging
config materialisation
```

If any model has a genuine fitting/training procedure, run it only on 2024.

## Trader Families to Tune / Train

At minimum include:

```text
S0 equal weight / cash buffer variants
S1 macro
S1 sector
risk parity
DRO-BL-RP
BSA-RP
ARMOR-OMD
LEEQA-Rank
KG-MoE-Lite
HGF-MPC
CEVA-KF / CIGA
sector rotation
OCO fallback / ensemble fallback
```

For every trader family, define:

```text
parameter space
training/tuning procedure
2024 objective
valid tracks
maturity label
dependency risk
news dependency
fallback behavior
output config path
```

## Required Reports

Write:

```text
outputs/reports/prompt19/progress/progress_02_tuner_design.md
outputs/reports/prompt19/reference/tuner_design.md
outputs/reports/prompt19/reference/tuner_parameter_space.csv
```

Use:

| Trader Family | Track(s) | Parameters Tuned | 2024 Objective | Training Procedure | Output Configs | News Dependency | Maturity | Notes |
|---|---|---|---|---|---|---|---|---|

---

# Part C — Run 2024 Tuning / Training for All Traders

## Objective

Run the tuner/trainer for all implemented trader families on **2024 construction data only**.

## Required Run

Run a real tuning/training pass, not just a description.

Minimum acceptable run:

```text
- all 242 available 2024 construction dates;
- all trader families listed in Part B;
- at least 300 total candidate/config rows if using grid/random search;
- both tracks;
- no_news and rule_based variants where applicable;
- optional cached BGE/FinBERT/hybrid variants only if already available and bounded;
- official-semantics target tensor generation;
- official-semantics batched replay;
- no LocalSmokeBacktester for final tuning evidence.
```

If Prompt18 grid results satisfy part of this, you may reuse them only after verifying:

```text
- they are 2024-only;
- they include the relevant family/parameter rows;
- candidate config hashes match current source/config files;
- no 2025 information was used;
- the output is copied into Prompt19 tuner-specific reports.
```

Prompt19 must produce a **tuner-specific result set**, even if it reuses Prompt18 artifacts.

## Required Outputs

For each tuned family, produce:

```text
best config
fallback config
top-k configs
failed configs
dropped configs
tuning metadata
config hash
runtime
```

Write generated tuned configs under:

```text
.var/prompt19/generated_configs/
```

If the tuner selects new candidates, write them to:

```text
configs/systems/prompt19_tuned_track_a_primary.yaml
configs/systems/prompt19_tuned_track_a_fallback.yaml
configs/systems/prompt19_tuned_track_b_primary.yaml
configs/systems/prompt19_tuned_track_b_fallback.yaml
configs/prompt19_tuned_candidates.json
```

Important:

```text
These prompt19_tuned_* configs are research/tune-test outputs.
They do not automatically replace the Prompt18 official final runtime configs.
```

## Required Reports

Write:

```text
outputs/reports/prompt19/progress/progress_03_2024_tuning_run.md
outputs/reports/prompt19/reference/tuner_2024_results.csv
outputs/reports/prompt19/reference/tuner_2024_ranking.md
outputs/reports/prompt19/reference/tuner_2024_ranking.csv
outputs/reports/prompt19/reference/tuned_candidate_freeze_2024_only.md
outputs/reports/prompt19/reference/tuned_candidate_freeze_2024_only.csv
outputs/reports/prompt19/presented/tuner_training_summary.md
```

Use ranking table:

| Rank | Candidate | Trader Family | Track | Text Mode | Tuned Parameters | 2024 Return | 2024 Sharpe | Max Drawdown | Turnover | Conservative Score | Dependency Risk | News Dependency | Promote? | Notes |
|---:|---|---|---|---|---|---:|---:|---:|---:|---:|---|---|---|---|

## Hard Rule

Do not evaluate 2025 until the 2024 freeze report is written.

---

# Part D — 1-Year Tune / 1-Year Test Leaderboard

## Objective

Create a dedicated top-candidate ranking using:

```text
Tune/train/freeze:
  full 2024

Test/evaluate:
  full 2025 public-A
```

This is the explicit “1 year tune, 1 year test” analysis.

## Candidate Set

Include:

```text
Prompt19 tuned Track A primary/fallback
Prompt19 tuned Track B primary/fallback
top 10 Track A 2024-tuned candidates
top 10 Track B 2024-tuned candidates
Prompt18 official final candidates
Prompt18 official-server 5-row validation candidates
S0 macro
S0 sector
S1 macro
S1 sector
best news-enabled candidate per track
best no-news candidate per track
best rule-based candidate per track
```

## Ranking Philosophy

Produce two rankings:

### Ranking A — Official Discipline Ranking

This ranks candidates using 2024 tune metrics as the selection basis and 2025 as generalisation confirmation.

Do not allow 2025 to override 2024 freeze.

### Ranking B — Research Tune/Test Leaderboard

This ranks candidates by combined train/test quality, for analysis only.

Suggested combined score:

```text
one_year_tune_test_score =
  0.40 * 2024_conservative_score
+ 0.35 * 2025_generalisation_score
+ 0.10 * stability_score
+ 0.10 * simplicity_score
+ 0.05 * parity_score
- dependency_penalty
- overfit_gap_penalty
```

This score may be used to identify top research candidates, but the official final runtime selection remains Prompt18 unless a correctness defect is found.

## Required Reports

Write:

```text
outputs/reports/prompt19/progress/progress_05_1y_tune_1y_test_ranking.md
outputs/reports/prompt19/reference/one_year_tune_test_leaderboard.md
outputs/reports/prompt19/reference/one_year_tune_test_leaderboard.csv
outputs/reports/prompt19/reference/one_year_tune_test_trackA.csv
outputs/reports/prompt19/reference/one_year_tune_test_trackB.csv
outputs/reports/prompt19/presented/one_year_tune_test_summary.md
```

Use:

| Rank | Candidate | Track | Family | Text Mode | Role | 2024 Return | 2024 Sharpe | 2024 Score | 2025 Return | 2025 Sharpe | 2025 Score | Generalisation Gap | Combined Tune/Test Score | Official Runtime Candidate? | Research Top Candidate? | Notes |
|---:|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|---|

Explicitly state:

```text
The one-year tune/test leaderboard is analytical evidence.
It does not automatically replace the Prompt18 official final selection.
```

---

# Part E — News Usage Verification

## Objective

Explicitly verify whether news is actually used by each news-enabled trader, rather than merely passing through the pipeline.

## Questions to Answer

For each relevant trader/family:

```text
1. Does the config enable news?
2. Does Stage 1 process news for this candidate?
3. Does Stage 2 store news-derived features?
4. Does Stage 4 read news-derived features?
5. Do target weights change when news is removed or perturbed?
6. Do decision traces contain news-derived fields?
7. Are news signals nonzero/nonempty on real 2024 dates?
8. Is the news effect material or negligible?
9. Is the candidate selected despite news, because of news, or without news?
```

## Required News Tests

Run at least:

### Test 1 — Trace Audit

Inspect decision traces for:

```text
news_items_seen
event_tags
macro_tags
sector_tags
asset_tags
sentiment_score
embedding/relevance score if enabled
news_signal
stage1_mode
stage2_news_state
stage4_news_weight
```

### Test 2 — No-News Ablation

For each news-enabled candidate:

```text
same parameters + no_news
same dates
same backend
compare metrics and target weights
```

### Test 3 — News Perturbation / Shuffle

For representative candidates:

```text
shuffle news dates or zero news signal
keep price data unchanged
compare target weights and metrics
```

### Test 4 — Weight-Difference Materiality

Compute:

```text
mean absolute target weight difference
max target weight difference
fraction of dates with changed target
metric difference
```

## Required Candidate Coverage

At minimum:

```text
Prompt18 Track A primary
Prompt18 Track A fallback
Prompt18 Track B primary
Prompt18 Track B fallback
Prompt19 tuned Track A primary
Prompt19 tuned Track B primary
best BSA-RP rule/news candidate
best DRO-BL-RP rule/news candidate
best CEVA candidate
best KG-MoE-Lite candidate
best LEEQA-Rank candidate
best sector-rotation rule/news candidate
```

If final selected candidate is no-news, explicitly state:

```text
final selected candidate does not require news
```

If final selected candidate is rule-based/news-enabled, prove that its decision path consumes news features.

## Required Reports

Write:

```text
outputs/reports/prompt19/progress/progress_04_news_usage_verification.md
outputs/reports/prompt19/reference/news_usage_trace_audit.md
outputs/reports/prompt19/reference/news_usage_trace_audit.csv
outputs/reports/prompt19/reference/news_ablation_report.md
outputs/reports/prompt19/reference/news_ablation_report.csv
outputs/reports/prompt19/presented/news_usage_summary.md
```

Use trace audit table:

| Candidate | Family | Track | Text Mode | News Enabled? | Stage1 Ran? | Stage2 News Stored? | Stage4 Reads News? | Trace Fields Present? | Nonzero News Signal Days | Status | Notes |
|---|---|---|---|---|---|---|---|---|---:|---|---|

Use ablation table:

| Candidate | Track | Family | Baseline Text Mode | Ablation Mode | Mean Abs Weight Diff | Max Weight Diff | Changed-Date Fraction | Return Diff | Sharpe Diff | News Materiality | Conclusion |
|---|---|---|---|---|---:|---:|---:|---:|---:|---|---|

News materiality values:

```text
material
small
negligible
not_used
blocked
```

Important:

```text
If news is not actually used by final candidates, say so honestly.
A deterministic no-news allocator is acceptable if that is what evidence supports.
```

---

# Part F — Locked 2025 Test of Frozen/Tuned Candidates

## Objective

After 2024 tuning and freeze, evaluate tuned/frozen candidates on 2025 public-A data.

This overlaps with the 1-year tune/test leaderboard but should remain a formal locked-test report.

## Candidate Set

Evaluate:

```text
Prompt19 tuned Track A primary
Prompt19 tuned Track A fallback
Prompt19 tuned Track B primary
Prompt19 tuned Track B fallback
top 5 Track A tuned candidates
top 5 Track B tuned candidates
Prompt18 official final candidates
S0 macro
S0 sector
S1 macro
S1 sector
best news-enabled candidate per track if different
```

## Rules

```text
- no parameter changes after 2024 freeze;
- no automatic switching of final official candidates because of 2025;
- report 2025 as test/generalisation evidence;
- record if a tuned candidate collapses out-of-sample;
- keep Prompt18 official candidates as comparison.
```

## Required Reports

Write:

```text
outputs/reports/prompt19/progress/progress_06_locked_2025_test.md
outputs/reports/prompt19/reference/locked_2025_test_results.csv
outputs/reports/prompt19/reference/locked_2025_test_report.md
outputs/reports/prompt19/reference/locked_2025_test_report.csv
outputs/reports/prompt19/presented/locked_2025_test_summary.md
```

Use:

| Candidate | Track | Role | 2024 Rank | 2024 Return | 2024 Sharpe | 2025 Return | 2025 Sharpe | 2025 Drawdown | 2025 Turnover | Generalisation | Frozen? | Notes |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|

---

# Part G — Final Parity and Official Server Check

## Objective

Confirm that official Prompt18 final candidates and any Prompt19 tuned candidates still pass validation.

## Local Parity

Run local reference-vs-batched parity for:

```text
Prompt18 Track A primary
Prompt18 Track A fallback
Prompt18 Track B primary
Prompt18 Track B fallback
Prompt19 tuned Track A primary if different
Prompt19 tuned Track B primary if different
S0 macro
S1 macro
S1 sector
```

Use all 242 2024 dates if feasible.

## Official Server Parity

Run official-server parity for:

```text
S0 macro
S1 macro
S1 sector
Prompt18 Track A primary
Prompt18 Track B primary
Prompt19 tuned Track A primary if different and feasible
Prompt19 tuned Track B primary if different and feasible
```

Use the widest feasible official 2025 window. Prefer all 243 public-A dates if runtime is acceptable. Otherwise run a shorter window and clearly state coverage.

## Required Reports

Write:

```text
outputs/reports/prompt19/reference/final_local_parity.csv
outputs/reports/prompt19/reference/final_official_server_parity.csv
```

Include a summary in:

```text
outputs/reports/prompt19/presented/final_readiness_report.md
```

Use:

| Candidate | Track | Window | Reference Value | Batched Value | Official Value | Local Diff | Official Diff | Trade Match | Status | Notes |
|---|---|---|---:|---:|---:|---:|---:|---|---|---|

---

# Part H — Cleanup and Temporary File Removal

## Objective

Clean the repository before final packaging.

## Cleanup Targets

Inventory and remove/archive unnecessary generated files:

```text
__pycache__/
*.pyc
.pytest_cache/
outputs/pytest_cache/
outputs/pytest_tmp/
.mypy_cache/
.ruff_cache/
.var/prompt13/
.var/prompt14/
.var/prompt15/
.var/prompt16/
.var/prompt17/
.var/prompt17b/
temporary package extraction folders
stale benchmark outputs
large target tensor caches no longer needed
temporary official server user/session files
temporary logs
accidental notebooks
accidental copied package directories
```

Do **not** delete:

```text
raw official data
source code
configs
tests
docs
official starter files
final Prompt18/Prompt19 compact reports
final package zips
necessary manifests
```

Archive if risky:

```text
.var/prompt19/cleanup_archive/
```

## Required Cleanup Reports

Write:

```text
outputs/reports/prompt19/progress/progress_07_cleanup.md
outputs/reports/prompt19/reference/cleanup_manifest.md
outputs/reports/prompt19/reference/cleanup_manifest.csv
outputs/reports/prompt19/presented/cleanup_summary.md
```

Use:

| Path | Type | Size | Action | Reason | Preserved Elsewhere? | Notes |
|---|---|---:|---|---|---|---|

Action values:

```text
keep
delete_generated
archive_to_var
ignore_only
manual_review
blocked
```

Verify `.gitignore` covers:

```text
.var/
outputs/pytest_cache/
outputs/pytest_tmp/
__pycache__/
*.pyc
models/huggingface/
outputs/models/
.cache/
```

Update `.gitignore` only if necessary.

---

# Part I — Final Package Rebuild and Audit

## Objective

Rebuild clean final packages after tuning, news audit, parity, and cleanup.

## Package 1 — Official Runtime Package

Official final runtime package should preserve the original Prompt18 final selection unless a correctness defect was found.

Include:

```text
NLPCC_tasks/agent_platform/agents/build_agent.py
src/nlpcc/
configs/
configs/prompt18_final_candidates.json
configs/systems/prompt18_track_a_primary.yaml
configs/systems/prompt18_track_a_fallback.yaml
configs/systems/prompt18_track_b_primary.yaml
configs/systems/prompt18_track_b_fallback.yaml
requirements.txt or dependency files
README_SUBMISSION.md
dependency manifest
```

If Prompt19 tuned configs are included, include them only as clearly labelled optional/research configs unless a human approved replacing Prompt18 final configs.

Exclude:

```text
raw official data
NLPCC_tasks/dataset/
outputs/
.var/
src/tools/ unless build_agent/runtime imports it
models/
models/huggingface/
outputs/models/
HF binaries
__pycache__/
*.pyc
notebooks
large logs
test caches
```

## Package 2 — Reproducibility Package

Include:

```text
official runtime package contents
src/tools/ if required for backtesting/reports
scripts used for Prompt18/Prompt19
compact reports under outputs/reports/prompt18/ and outputs/reports/prompt19/
candidate catalogs
score CSVs
README_REPRODUCIBILITY.md
dependency/model manifest
```

Exclude:

```text
raw official data
large target tensor caches
large `.var/` runtime artifacts
HF model binaries
pycache
temporary logs
```

## Required Reports

Write:

```text
outputs/reports/prompt19/progress/progress_08_package_rebuild.md
outputs/reports/prompt19/reference/package_manifest_audit.md
outputs/reports/prompt19/reference/package_manifest_audit.csv
outputs/reports/prompt19/reference/final_runtime_package_audit.json
outputs/reports/prompt19/reference/reproducibility_package_audit.json
outputs/reports/prompt19/reference/final_candidate_paths.csv
outputs/reports/prompt19/presented/final_package_summary.md
```

Use:

| Package | Archive Path | Entry Count | Raw Data Issues | Model Binary Issues | Pycache Issues | Output/Var Issues | Status | Notes |
|---|---|---:|---|---|---|---|---|---|

---

# Part J — Final System Report Draft

## Objective

Draft final system-report prose based on verified evidence.

Create:

```text
outputs/reports/prompt19/presented/final_system_report_draft.md
```

Use this structure:

```md
# System Report Draft — NLPCC 2026 Shared Task 4

## Abstract

## 1. Task and Constraints

## 2. System Overview

## 3. Four-Stage Architecture

## 4. Data Availability and Leakage Prevention

## 5. Trader Families Considered

## 6. 2024 Tuning / Training Protocol

## 7. One-Year Tune / One-Year Test Results

## 8. News Processing and News-Usage Verification

## 9. Final Track A System

## 10. Final Track B System

## 11. Backtesting and Official-Server Validation

## 12. Locked 2025 Evaluation

## 13. Ablation Studies

## 14. Package and Reproducibility

## 15. Limitations and Hidden B-List Risks

## 16. Conclusion
```

Must mention:

```text
- 2024-only tuning/freeze;
- 2025 one-year test only after freeze;
- official-server parity status;
- original Prompt18 final candidates and fallbacks;
- Prompt19 one-year tune/test top candidates;
- whether final candidates use news or not;
- no external API dependency;
- deterministic fallback;
- no raw official data redistributed;
- method maturity caveats.
```

Must not claim:

```text
- hidden 2026 results;
- 2025 was used for training;
- BGE/FinBERT final dependency unless true;
- full causal discovery if CEVA is MVP;
- full GNN/MoE if KG-MoE-Lite is graph-lite;
- full MPC if HGF-MPC is simplified;
- news is used if ablation says it is not material;
- CUDA superiority unless final benchmarks support it.
```

---

# Part K — Submission Handoff Checklist

Create:

```text
outputs/reports/prompt19/presented/submission_handoff_checklist.md
```

Use:

```md
# Submission Handoff Checklist

## 1. Final Candidate Configs

## 2. Official Runtime Package

## 3. Reproducibility Package

## 4. Required Reports

## 5. Official Server Parity

## 6. One-Year Tune / One-Year Test Evidence

## 7. News Usage Evidence

## 8. Cleanup Status

## 9. Manual Checks Before Upload

## 10. Do-Not-Submit Items

## 11. Final Human Sign-Off
```

Include final human checks:

```text
- unzip official runtime package in a clean directory;
- inspect build_agent.py imports;
- run minimal official server smoke if possible;
- confirm package excludes raw data;
- confirm final configs match final recommendation;
- confirm no local absolute paths are required;
- confirm no HF model binary dependency is required;
- confirm docs do not overclaim;
- confirm Prompt19 tuned candidates did not silently replace Prompt18 official final configs.
```

---

# Part L — Final Recommendation and Readiness

Create:

```text
outputs/reports/prompt19/presented/final_recommendation.md
outputs/reports/prompt19/presented/final_readiness_report.md
outputs/reports/prompt19/presented/executive_summary.md
outputs/reports/prompt19/README.md
```

## `final_readiness_report.md`

Use exactly:

```md
# Prompt19 Final Readiness Report

## 1. Readiness Verdict

Choose exactly one:

- Ready for final human submission review
- Locally ready, official-server validation incomplete
- Not ready; tuning failed
- Not ready; news usage unresolved
- Not ready; package audit failed
- Not ready; cleanup incomplete

## 2. Prompt18 Verification

## 3. 2024 Tuning / Training Result

## 4. One-Year Tune / One-Year Test Result

## 5. Official Final Selection Preservation

## 6. News Usage Verification

## 7. Locked 2025 Test

## 8. Local / Official Parity

## 9. Cleanup Status

## 10. Package Rebuild Status

## 11. Final Track A Candidate

## 12. Final Track B Candidate

## 13. System Report Status

## 14. Remaining Risks

## 15. Recommended Next Action
```

## `final_recommendation.md`

Use:

```md
# Prompt19 Final Recommendation

## 1. Executive Verdict

## 2. Official Final Track A Candidate

- Primary:
- Fallback:
- 2024 evidence:
- 2025 test evidence:
- News usage:
- Official parity:
- Risks:

## 3. Official Final Track B Candidate

- Primary:
- Fallback:
- 2024 evidence:
- 2025 test evidence:
- News usage:
- Official parity:
- Risks:

## 4. Prompt19 1-Year Tune/Test Top Candidates

## 5. Should Prompt18 Official Selection Be Reopened?

Choose one:
- No, preserve Prompt18 official final selection.
- Yes, but only as a human-approved research change.
- Blocked because of correctness defect.

## 6. Runtime Package

## 7. Reproducibility Package

## 8. What Can Be Claimed

## 9. What Must Not Be Claimed

## 10. Remaining Human Checks

## 11. Final Next Action
```

---

## Constraints

- Do not add new strategy families.
- Do not use 2025 for parameter tuning.
- Do not use hidden 2026 data.
- Do not use LocalSmokeBacktester for final evidence.
- Do not silently download models.
- Do not include raw official data or model binaries in final runtime package.
- Do not overclaim news usage.
- Do not overclaim advanced method maturity.
- Do not overclaim CUDA.
- Do not delete raw official data, source code, configs, tests, docs, or official starter files.
- Clean temporary artifacts and generated clutter.
- If cleanup is risky, archive to `.var/prompt19/cleanup_archive/` instead of deleting.
- If tuner/training fails for some trader families, report failure honestly and continue with successful families only if final readiness remains justified.
- If final package audit fails, do not claim readiness.
- Preserve Prompt18 official final selection unless Prompt19 identifies a correctness defect or the human explicitly approves replacement.
- The 1-year tune/test leaderboard is analytical evidence, not automatic final-submission replacement.

---

## Expected Final Assistant Response

After completing Prompt19, respond with:

1. readiness verdict;
2. whether Prompt18 claims were verified;
3. tuner/trainer status;
4. 2024 tuning coverage;
5. 1-year tune / 1-year test top candidates;
6. whether the original Prompt18 official final selection was preserved;
7. final official Track A candidate;
8. final official Track B candidate;
9. news-usage verification result;
10. locked 2025 test summary;
11. official-server parity status;
12. cleanup status;
13. package rebuild status;
14. final system-report draft path;
15. submission handoff checklist path;
16. exact final package paths;
17. remaining risks;
18. final recommended human action.
