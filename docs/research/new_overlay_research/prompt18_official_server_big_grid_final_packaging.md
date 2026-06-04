# Prompt18 — Official Server Validation, Full Overnight Grid Search, Final Candidate Selection, and Submission Package Polish

## Role

You are a senior quantitative research engineer, GPU/backtesting systems engineer, LLM-systems architect, optimiser engineer, official-submission reliability auditor, and shared-task paper strategist.

You are continuing the NLPCC 2026 Shared Task 4 repository after Prompt17b.

Prompt17b repaired the major Prompt17 evidence gaps by adding:

```text
- target-tensor trace/data-version auditing;
- leakage-safety audit;
- broad reference-vs-batched parity gate;
- full 2024 replay over all 242 available construction dates for the 24 no-news/rule-based Prompt17 candidate slice;
- corrected 2024-only candidate freeze;
- locked 2025 public-A evaluation over 243 dates;
- 485-date research-only five-fold robustness;
- text-cache/runtime evidence;
- package audit;
- required report tree under outputs/reports/prompt17b/.
```

However, Prompt17b still left important blockers:

```text
1. official server spotcheck remains blocked;
2. full 2024 search used only the 24-candidate Prompt17 no-news/rule-based slice, not a true large grid;
3. optional local text modes were cache-tested only on a bounded sample and were not used in final ranking;
4. CUDA was not claimed; NumPy remained the reliable backend;
5. the final package was locally clean, but final official-runtime vs reproducibility-package split still needs polish;
6. the final readiness is only provisionally ready except official server.
```

Prompt18 is intended to be a **full overnight run**. You must run at least one genuinely large grid search, subject to safety, checkpointing, and correctness gates. Do not turn this into another small smoke test.

---

## Core Objective

By the end of Prompt18, the repository should either be:

```text
A. ready for final official-submission packaging and system-report polish,
```

or have a precise, evidence-backed blocker report explaining why it is not.

Prompt18 must:

```text
1. attempt to start/fix the official local server and rerun official-server parity;
2. run at least one large full-horizon official-semantics grid search;
3. produce final 2024-only candidate selection from the large grid;
4. run locked 2025 evaluation only after the 2024 candidate freeze;
5. update or confirm Track A and Track B final candidates;
6. produce final runtime and reproducibility package split;
7. produce submission-readiness reports under outputs/reports/prompt18/;
8. preserve honest maturity labels and avoid overclaiming.
```

---

## Mandatory Context to Read First

Read all available Prompt16–Prompt17b artifacts before changing code or running long jobs.

### Prompt17b Presented Reports

```text
outputs/reports/prompt17b/presented/executive_readiness_report.md
outputs/reports/prompt17b/presented/final_status_report.md
outputs/reports/prompt17b/presented/final_recommendation.md
outputs/reports/prompt17b/presented/candidate_freeze_repair_report.md
outputs/reports/prompt17b/presented/full_horizon_search_summary.md
outputs/reports/prompt17b/presented/locked_2025_evaluation_summary.md
outputs/reports/prompt17b/presented/five_fold_robustness_summary.md
outputs/reports/prompt17b/presented/official_parity_closure_summary.md
```

### Prompt17b Reference Reports

```text
outputs/reports/prompt17b/reference/prompt17_gap_matrix.md
outputs/reports/prompt17b/reference/target_tensor_audit.md
outputs/reports/prompt17b/reference/target_tensor_audit.csv
outputs/reports/prompt17b/reference/leakage_safety_audit.md
outputs/reports/prompt17b/reference/leakage_safety_audit.csv
outputs/reports/prompt17b/reference/parity_spotcheck_full.md
outputs/reports/prompt17b/reference/parity_spotcheck_full.csv
outputs/reports/prompt17b/reference/full_2024_candidate_scores.csv
outputs/reports/prompt17b/reference/full_2024_candidate_ranking.md
outputs/reports/prompt17b/reference/full_2024_candidate_ranking.csv
outputs/reports/prompt17b/reference/full_2024_trackA_ranking.csv
outputs/reports/prompt17b/reference/full_2024_trackB_ranking.csv
outputs/reports/prompt17b/reference/locked_2025_candidate_scores.csv
outputs/reports/prompt17b/reference/locked_2025_evaluation.md
outputs/reports/prompt17b/reference/locked_2025_evaluation.csv
outputs/reports/prompt17b/reference/five_fold_485d_scores.csv
outputs/reports/prompt17b/reference/five_fold_485d_report.md
outputs/reports/prompt17b/reference/text_feature_cache_report.md
outputs/reports/prompt17b/reference/text_feature_cache_report.csv
outputs/reports/prompt17b/reference/runtime_benchmark_report.md
outputs/reports/prompt17b/reference/runtime_benchmark_report.csv
outputs/reports/prompt17b/reference/official_server_spotcheck.md
outputs/reports/prompt17b/reference/official_server_spotcheck.csv
outputs/reports/prompt17b/reference/package_audit_report.md
outputs/reports/prompt17b/reference/package_audit.json
```

### Prompt17b Implementation Log

```text
docs/implementation_logs/20260602_003440_prompt17b_full_horizon_validation_candidate_freeze_repair.md
```

### Prompt17 Reports

Read Prompt17 reports only as historical context, especially for understanding what Prompt17b corrected:

```text
docs/reports/prompt17/final_status_report.md
docs/reports/prompt17/overnight_search_results.md
docs/reports/prompt17/backtester_parity_spotcheck_report.md
docs/reports/prompt17/winner_freeze_report.md
docs/reports/prompt17/final_recommendation.md
```

If these were stored under `outputs/reports/prompt17/`, use the latest available equivalent.

### Prompt16 Reports

```text
docs/reports/prompt16/final_status_report.md
docs/reports/prompt16/backtester_semantics_audit.md
docs/reports/prompt16/cuda_backtester_report.md
docs/reports/prompt16/official_equivalence_report.md
docs/reports/prompt16/optimisation_engine_report.md
docs/reports/prompt16/five_fold_split_plan.md
docs/reports/prompt16/grid_search_runtime_estimate.md
docs/reports/prompt16/package_cleanliness_report.md
docs/implementation_logs/20260531_144835_prompt16_repo_cleanup_backtester_optimisation.md
```

### Code to Inspect

```text
NLPCC_tasks/agent_platform/agents/build_agent.py
NLPCC_tasks/server_platform/
NLPCC_tasks/agent_platform/demo_backtest.py

src/nlpcc/runtime/system_runner.py
src/nlpcc/stage1_news/
src/nlpcc/stage2_text_store/
src/nlpcc/stage3_trade/
src/nlpcc/stage4_agent/
src/nlpcc/execution/

src/tools/backtesting/reference_official_semantics.py
src/tools/backtesting/cuda_vectorized_backtester.py
src/tools/backtesting/batched_grid_backtester.py
src/tools/backtesting/backtester_parity.py

src/tools/experiments/leakage_safe_input_builder.py
src/tools/experiments/candidate_factory.py
src/tools/experiments/strategy_config_expander.py
src/tools/experiments/target_tensor_cache.py
src/tools/experiments/target_tensor_generator.py

src/tools/optimiser/
src/tools/verification/submission_package.py

scripts/run_prompt17b_validation.py
scripts/run_prompt17_overnight_search.py
scripts/run_official_server_smoke.py
scripts/generate_target_tensors.py
scripts/build_text_feature_cache.py

configs/
tests/
```

---

## Official Constraints to Preserve

Preserve these constraints exactly:

```text
- Track A / Track 1: Macro-Asset Allocation.
- Track B / Track 2: Sector-Rotation Allocation.
- Agents receive daily Top-20 financial hot news and historical ETF/index price data.
- 2024 data is for training / construction.
- 2025 data is public A-list / locked evaluation only.
- 2026-01-01 to 2026-06-01 is hidden B-list evaluation.
- B-list is centrally run by organisers using submitted code.
- Current-day close/high/low/return must not be used before decision time.
- Same-day news is usable only under the official timestamp cutoff.
- Transaction friction is 0.01%.
- Evaluation emphasises Sharpe ratio, cumulative return, max drawdown, and turnover categories.
- External models, datasets, and knowledge bases must be available before 2026.
- Any training, fine-tuning, retrieval, or knowledge construction must be reproducible.
- Raw official data must not be modified or redistributed.
- Final runtime must retain deterministic no-model / no-API fallback.
- 2025 public A must not be used to select or tune final parameters.
```

---

## Artifact and Reporting Policy

Prompt18 must write reports under:

```text
outputs/reports/prompt18/
```

Use this folder structure exactly:

```text
outputs/reports/prompt18/
  README.md

  progress/
    progress_00_context_and_readiness_review.md
    progress_01_official_server_startup.md
    progress_02_pre_grid_integrity_gate.md
    progress_03_big_grid_plan.md
    progress_04_big_grid_run_status.md
    progress_05_candidate_freeze.md
    progress_06_locked_2025_evaluation.md
    progress_07_official_server_parity.md
    progress_08_package_split.md
    run_log.md

  presented/
    executive_summary.md
    official_server_validation_summary.md
    big_grid_search_summary.md
    final_candidate_selection_report.md
    locked_2025_evaluation_summary.md
    final_package_summary.md
    final_submission_readiness_report.md
    final_recommendation.md

  reference/
    context_gap_review.md
    official_server_startup_report.md
    official_server_startup_report.csv
    pre_grid_integrity_gate.md
    pre_grid_integrity_gate.csv
    big_grid_plan.md
    big_grid_plan.csv
    big_grid_candidate_catalog.csv
    big_grid_runtime_benchmark.md
    big_grid_runtime_benchmark.csv
    big_grid_2024_scores.csv
    big_grid_2024_ranking.md
    big_grid_2024_ranking.csv
    big_grid_trackA_ranking.csv
    big_grid_trackB_ranking.csv
    big_grid_ablation_report.md
    big_grid_ablation_report.csv
    candidate_freeze_2024_only.md
    candidate_freeze_2024_only.csv
    locked_2025_scores.csv
    locked_2025_evaluation.md
    locked_2025_evaluation.csv
    final_parity_reference_vs_batched.md
    final_parity_reference_vs_batched.csv
    official_server_parity.md
    official_server_parity.csv
    final_runtime_package_audit.md
    final_runtime_package_audit.json
    reproducibility_package_audit.md
    reproducibility_package_audit.json
    dependency_and_model_manifest.md
    dependency_and_model_manifest.json
```

Large runtime artifacts must go under:

```text
.var/prompt18/
  cache/
  target_tensors/
  generated_configs/
  grid_runs/
  checkpoints/
  benchmarks/
  official_server/
  packages/
  logs/
```

Only compact `.md`, `.csv`, and audit `.json` summaries should be copied into `outputs/reports/prompt18/`.

---

## Required Implementation Log

Create:

```text
docs/implementation_logs/<timestamp>_prompt18_official_server_big_grid_final_packaging.md
```

Use exactly:

```md
# Implementation Log: prompt18 - official_server_big_grid_final_packaging

## Created

## Summary

## Files Changed

## Context Review

## Official Server Startup / Repair

## Pre-Grid Integrity Gate

## Big Grid Search

## Candidate Freeze

## Locked 2025 Evaluation

## Final Local Parity

## Official Server Parity

## Package Split

## Tests / Checks

## Caveats

## Artifacts

## Next Steps
```

---

# Part A — Context Review and Remaining Blocker Confirmation

## Objective

Confirm exactly what remains after Prompt17b.

## Tasks

1. Read Prompt17b reports and implementation log.
2. Summarise what is already fixed.
3. Confirm remaining blockers:
   ```text
   - official server not reachable;
   - grid search not yet truly large;
   - local text modes not used in final freeze;
   - final package split not fully polished;
   - official runtime package not yet independently validated through server.
   ```
4. Confirm current provisional candidates:
   ```text
   Track A primary: bsa_rp_macro_tilt25
   Track A fallback: bsa_rp_macro_rule
   Track B primary: armor_omd_sector_default
   Track B fallback: s0_sector_cash02
   ```

## Required Reports

Write:

```text
outputs/reports/prompt18/progress/progress_00_context_and_readiness_review.md
outputs/reports/prompt18/reference/context_gap_review.md
```

Use:

| Issue | Prompt17b Status | Prompt18 Required Action | Severity |
|---|---|---|---|

Severity values:

```text
critical
high
medium
low
resolved
```

---

# Part B — Official Server Startup / Repair

## Objective

Resolve the official-server blockage if possible.

Prompt17 and Prompt17b both failed because `http://localhost:6207` refused connection. Prompt18 must explicitly inspect, start, or repair the local official server workflow before final readiness can be claimed.

## Tasks

1. Inspect official server files:

```text
NLPCC_tasks/server_platform/
NLPCC_tasks/agent_platform/demo_backtest.py
NLPCC_tasks/agent_platform/
scripts/run_official_server_smoke.py
README.md
official task docs
```

2. Identify the expected server startup command.

3. Try to start the server if possible.

4. Check port `6207` or the configured server port.

5. Run official server smoke after startup.

6. If startup fails:
   - capture exact command;
   - capture stdout/stderr;
   - capture import/path/dependency errors;
   - record whether failure is due to missing dependencies, port conflict, missing data, or unknown server contract.

## Required Reports

Write:

```text
outputs/reports/prompt18/progress/progress_01_official_server_startup.md
outputs/reports/prompt18/reference/official_server_startup_report.md
outputs/reports/prompt18/reference/official_server_startup_report.csv
```

Use:

| Attempt | Command | Port | Result | Error | Probable Cause | Next Action |
|---:|---|---:|---|---|---|---|

Status values:

```text
started
already_running
blocked_dependency
blocked_missing_data
blocked_port
blocked_unknown
not_applicable
```

## Important

If the official server cannot be started within reasonable effort, continue with the local big grid search, but final readiness must remain conditional.

Do not fabricate official-server parity.

---

# Part C — Pre-Grid Integrity Gate

## Objective

Before launching the overnight grid, rerun a compact but broad integrity gate.

## Required Checks

1. Target tensor generation still works.
2. Leakage safety still passes.
3. Reference-vs-batched parity still passes for representative candidates.
4. Package helper still excludes raw official data.
5. Candidate factory can generate large candidate catalog.
6. Target tensor cache keys include:
   ```text
   data version / root fingerprint
   track
   date range
   text mode
   config hash
   candidate family
   ```

## Required Candidates for Integrity Gate

```text
S0 macro
S1 macro
bsa_rp_macro_tilt25
bsa_rp_macro_rule
risk_parity_macro
DRO-BL-RP macro
S0 sector
S1 sector
armor_omd_sector_default
s0_sector_cash02
sector_rotation_graph15
LEEQA-Rank
KG-MoE-Lite
CEVA sector
```

## Required Reports

Write:

```text
outputs/reports/prompt18/progress/progress_02_pre_grid_integrity_gate.md
outputs/reports/prompt18/reference/pre_grid_integrity_gate.md
outputs/reports/prompt18/reference/pre_grid_integrity_gate.csv
outputs/reports/prompt18/reference/final_parity_reference_vs_batched.md
outputs/reports/prompt18/reference/final_parity_reference_vs_batched.csv
```

Use:

| Check | Candidate | Track | Dates | Status | Evidence | Notes |
|---|---|---|---:|---|---|---|

Status values:

```text
pass
minor_diff
fail
blocked
not_run
```

## Hard Gate

Do not launch the big grid if any of these fail:

```text
S0 macro parity
S1 macro parity
S1 sector parity
bsa_rp_macro_tilt25 parity
armor_omd_sector_default parity
current-day close/high/low/return masking
candidate catalog generation
```

If a hard gate fails, stop and write failure reports.

---

# Part D — Big Grid Plan

## Objective

Design a large overnight grid search.

This prompt explicitly requires running at least one big grid search. It is acceptable for it to run overnight, but it must be checkpointed, resumable, and reported honestly.

## Minimum Required Big Grid

At least one of the following must be run:

### Option 1 — Medium-Large Grid

```text
Dates:
  all available 2024 construction dates

Candidates:
  at least 300 candidate configurations total
  at least 100 macro candidates
  at least 100 sector candidates

Text modes:
  no_news
  rule_based

Backend:
  NumPy official-semantics batched replay by default
  CUDA only if benchmarked useful

Expected:
  required minimum if local machine is constrained
```

### Option 2 — Large Grid

```text
Dates:
  all available 2024 construction dates

Candidates:
  at least 1000 candidate configurations total
  at least 300 macro candidates
  at least 300 sector candidates

Text modes:
  no_news
  rule_based
  optional cached local text modes if bounded

Backend:
  NumPy official-semantics batched replay by default
  CUDA only if benchmarked useful

Expected:
  preferred overnight search
```

### Option 3 — Very Large Grid

```text
Dates:
  all available 2024 construction dates

Candidates:
  at least 3000 candidate configurations total

Text modes:
  no_news
  rule_based
  cached bge_small_zh
  cached finbert_tone_chinese
  cached hybrid_rule_bge_finbert if feasible

Backend:
  auto backend
  benchmark CUDA vs NumPy
  use fastest correct backend

Expected:
  only if machine and cache make it feasible
```

You must run at least Option 1 unless a hard gate fails.

If Option 1 cannot be completed, write a failure report explaining exactly why, including runtime, memory, exception, and partial coverage. Do not pretend that a smaller smoke run satisfies the big-grid requirement.

## Candidate Families

The big grid must include parameter variations for:

```text
S0:
  cash buffer / max target sum variants

S1:
  momentum weight
  volatility weight
  trend window
  turnover cap
  max weight

Risk parity:
  lookback window
  shrinkage
  max weight
  cash buffer

DRO-BL-RP:
  tau
  confidence_scale
  rp_anchor_weight
  turnover_cap
  max_weight
  view_scale

BSA-RP:
  regime_decay
  risk_budget_floor
  belief_smoothing
  drawdown_throttle
  tilt_strength

ARMOR-OMD:
  eta
  expert_floor
  regret_decay
  transaction_penalty
  turnover_cap
  expert pool variants

LEEQA-Rank:
  feature weights
  top_k
  softmax_temperature
  turnover_cap
  max_weight

KG-MoE-Lite:
  graph_decay
  router_temperature
  expert weights
  sector_cap
  news impact weight

HGF-MPC:
  kalman_process_var
  kalman_obs_var
  horizon
  turnover_penalty
  drift window

CEVA-KF/CIGA:
  stability_threshold
  causal_confidence_scale
  impact_decay
  overlay_weight
  max tilt

Sector rotation:
  graph weight
  trend window
  sector cap
  turnover cap

OCO fallback:
  base weights over S0/S1/risk parity/advanced candidates
  drawdown trigger
  turnover penalty
```

Do not add new strategy families.

## Candidate Catalog

Create a candidate catalog before running the grid:

```text
outputs/reports/prompt18/reference/big_grid_candidate_catalog.csv
```

Fields:

```text
candidate_id
candidate_name
track
family
text_mode
base_config
parameter_json
config_hash
dependency_level
maturity_label
expected_runtime_class
include_in_grid
reason
```

## Required Reports

Write before running the grid:

```text
outputs/reports/prompt18/progress/progress_03_big_grid_plan.md
outputs/reports/prompt18/reference/big_grid_plan.md
outputs/reports/prompt18/reference/big_grid_plan.csv
outputs/reports/prompt18/reference/big_grid_candidate_catalog.csv
```

Use:

| Stage | Candidate Count | Tracks | Text Modes | Date Range | Backend | Estimated Runtime | Run? | Notes |
|---|---:|---|---|---|---|---:|---|---|

---

# Part E — Runtime Benchmark and Backend Choice

## Objective

Choose the backend for the big grid based on correctness and speed.

## Required Benchmark

Benchmark on the actual candidate/date tensor shapes where possible:

```text
candidate batches:
  24
  100
  300
  1000 if generated

date windows:
  20 dates
  full 2024 if feasible
```

Backends:

```text
reference loop
NumPy batched official-semantics replay
Torch CPU if available
Torch CUDA if available
```

## Backend Decision Rules

```text
- Use NumPy if it is fastest correct.
- Use CUDA only if it is both correct and materially faster on the relevant large batch.
- Do not use LocalSmokeBacktester for final evidence.
- If CUDA fails or is slower, mark it not recommended.
```

## Required Reports

Write:

```text
outputs/reports/prompt18/reference/big_grid_runtime_benchmark.md
outputs/reports/prompt18/reference/big_grid_runtime_benchmark.csv
```

Use:

| Backend | Device | Candidates | Dates | Runtime Seconds | Candidates Per Second | Max Metric Diff | Correct? | Recommended? | Notes |
|---|---|---:|---:|---:|---:|---:|---|---|---|

---

# Part F — Run the Big Grid Search

## Objective

Run the full-horizon big grid on 2024 construction data.

## Required Run

You must run at least one big grid satisfying Option 1, Option 2, or Option 3 from Part D.

The run must use:

```text
all available 2024 construction dates
official-semantics target tensor generation
official-semantics batched replay
checkpointing
candidate metadata
config hashes
fallback tracking
runtime logging
```

## Checkpointing Requirements

Save checkpoints under:

```text
.var/prompt18/checkpoints/
.var/prompt18/grid_runs/
```

At minimum checkpoint:

```text
candidate catalog
generated configs
target tensor bundle metadata
completed candidate chunks
partial score tables
failed candidate logs
runtime logs
```

If interrupted, resume from checkpoints rather than starting from zero where possible.

## Required Metrics

For every candidate, compute:

```text
final_value
cumulative_return
annualized_return if applicable
Sharpe
max_drawdown
turnover
trade_count_proxy
cash_utilisation
fallback_days
fallback_rate
failed_days
target_nonzero_days
mean_target_sum
max_target_sum
official_score
research_score
conservative_score
dependency_risk
overfit_risk
parity_risk
implementation_complexity
runtime_seconds
```

## Required Reports

Write:

```text
outputs/reports/prompt18/progress/progress_04_big_grid_run_status.md
outputs/reports/prompt18/reference/big_grid_2024_scores.csv
outputs/reports/prompt18/reference/big_grid_2024_ranking.md
outputs/reports/prompt18/reference/big_grid_2024_ranking.csv
outputs/reports/prompt18/reference/big_grid_trackA_ranking.csv
outputs/reports/prompt18/reference/big_grid_trackB_ranking.csv
outputs/reports/prompt18/reference/big_grid_ablation_report.md
outputs/reports/prompt18/reference/big_grid_ablation_report.csv
outputs/reports/prompt18/presented/big_grid_search_summary.md
```

Ranking table:

| Rank | Candidate | Track | Family | Text Mode | 2024 Return | 2024 Sharpe | Max Drawdown | Turnover | Fallback Rate | Official Score | Conservative Score | Runtime | Promote? | Notes |
|---:|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|---|

## Big Grid Success Criteria

A big grid run is successful only if:

```text
- at least 300 total candidates were evaluated;
- all 2024 construction dates were used;
- both tracks were included, unless one track failed and is reported;
- final evidence used official-semantics replay;
- failed candidate rate is reported;
- no LocalSmokeBacktester was used;
- output score CSVs were written.
```

---

# Part G — 2024-Only Candidate Freeze After Big Grid

## Objective

Select final candidates using only 2024 big-grid evidence.

## Freeze Rules

Use:

```text
full 2024 big-grid ranking
broad parity result
fallback rate
leakage-safety audit
maturity label
dependency risk
simplicity / package risk
```

Do **not** use 2025 results.

## Required Outputs

Freeze:

```text
Track A primary
Track A fallback
Track B primary
Track B fallback
Candidates for ablation/system report only
Candidates to drop
```

## Required Comparison

Compare against Prompt17b freeze:

```text
Prompt17b Track A primary: bsa_rp_macro_tilt25
Prompt17b Track A fallback: bsa_rp_macro_rule
Prompt17b Track B primary: armor_omd_sector_default
Prompt17b Track B fallback: s0_sector_cash02
```

## Required Reports

Write:

```text
outputs/reports/prompt18/progress/progress_05_candidate_freeze.md
outputs/reports/prompt18/reference/candidate_freeze_2024_only.md
outputs/reports/prompt18/reference/candidate_freeze_2024_only.csv
outputs/reports/prompt18/presented/final_candidate_selection_report.md
```

Use:

| Track | Role | Prompt17b Candidate | Prompt18 Candidate | Changed? | 2024 Evidence | Risk | Decision |
|---|---|---|---|---|---|---|---|

---

# Part H — Locked 2025 Evaluation After Freeze

## Objective

Evaluate only the frozen candidates and selected baselines on 2025 public A after candidate freeze.

## Candidate Set

Evaluate:

```text
Track A primary
Track A fallback
Track B primary
Track B fallback
top 5 Track A big-grid candidates
top 5 Track B big-grid candidates
S0 macro
S0 sector
S1 macro
S1 sector
risk parity macro
Prompt17b primary/fallback candidates if not already included
```

## Locked-Evaluation Rules

```text
- no parameter changes after viewing 2025;
- no switching final candidates based on 2025 unless freeze is explicitly reopened as research-only;
- report 2025 failures honestly;
- 2025 is evidence of generalisation, not selection/tuning.
```

## Required Reports

Write:

```text
outputs/reports/prompt18/progress/progress_06_locked_2025_evaluation.md
outputs/reports/prompt18/reference/locked_2025_scores.csv
outputs/reports/prompt18/reference/locked_2025_evaluation.md
outputs/reports/prompt18/reference/locked_2025_evaluation.csv
outputs/reports/prompt18/presented/locked_2025_evaluation_summary.md
```

Use:

| Candidate | Track | Frozen Role | 2024 Rank | 2024 Return | 2024 Sharpe | 2025 Return | 2025 Sharpe | 2025 Max Drawdown | 2025 Turnover | Generalisation | Promote Status | Notes |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|

Generalisation values:

```text
strong
acceptable
weak
failed
not_run
```

---

# Part I — Final Local Parity and Official Server Parity

## Objective

After the big-grid freeze, run final parity for the frozen candidates.

## Local Reference-vs-Batched Parity

Required candidates:

```text
S0 macro
S1 macro
S1 sector
Track A primary
Track A fallback
Track B primary
Track B fallback
best big-grid Track A candidate
best big-grid Track B candidate
```

Required report:

```text
outputs/reports/prompt18/reference/final_parity_reference_vs_batched.md
outputs/reports/prompt18/reference/final_parity_reference_vs_batched.csv
```

Use:

| Candidate | Track | Dates | Reference Final Value | Batched Final Value | Abs Diff | Max Daily Diff | Metric Diff | Status | Notes |
|---|---|---:|---:|---:|---:|---:|---:|---|---|

## Official Server Parity

If server is running, compare:

```text
official server
local reference official-semantics replay
batched official-semantics replay
```

Required candidates:

```text
S0 macro
S1 macro
S1 sector
Track A primary
Track B primary
```

Required reports:

```text
outputs/reports/prompt18/progress/progress_07_official_server_parity.md
outputs/reports/prompt18/reference/official_server_parity.md
outputs/reports/prompt18/reference/official_server_parity.csv
outputs/reports/prompt18/presented/official_server_validation_summary.md
```

Use:

| Candidate | Track | Window | Official Server Value | Local Reference Value | Batched Value | Official-Local Diff | Local-Batched Diff | Trade Match | Status | Notes |
|---|---|---|---:|---:|---:|---:|---:|---|---|---|

Status values:

```text
pass
minor_diff
fail
blocked
not_run
```

## Rule

Do not claim final official readiness unless official server parity passes for at least:

```text
S0 macro
S1 macro
S1 sector
Track A primary
Track B primary
```

If official server remains blocked, final readiness must say:

```text
locally ready, official-server validation blocked
```

---

# Part J — Final Package Split

## Objective

Create two final package variants.

### Package 1 — Official Runtime Package

Purpose: minimal official submission runtime.

Include:

```text
NLPCC_tasks/agent_platform/agents/build_agent.py
src/nlpcc/
configs/
requirements.txt or lock/dependency files
README_SUBMISSION.md
final frozen configs
dependency manifest
```

Exclude:

```text
src/tools/ unless absolutely required by runtime
raw official data
NLPCC_tasks/dataset/
outputs/
.var/
models/
outputs/models/
models/huggingface/
__pycache__
*.pyc
large logs
HF model binaries
notebooks
research-only reports
```

### Package 2 — Research Reproducibility Package

Purpose: system report / evidence reproducibility.

Include:

```text
official runtime package contents
src/tools/ if required for replay/reporting
scripts used for Prompt18
compact reports under outputs/reports/prompt18/
README_REPRODUCIBILITY.md
candidate catalog
final score CSVs
dependency and model manifest
```

Exclude:

```text
raw official data
large caches
large target tensors
.var/ large runtime artifacts unless explicitly small manifest only
HF model binaries
```

## Required Reports

Write:

```text
outputs/reports/prompt18/progress/progress_08_package_split.md
outputs/reports/prompt18/reference/final_runtime_package_audit.md
outputs/reports/prompt18/reference/final_runtime_package_audit.json
outputs/reports/prompt18/reference/reproducibility_package_audit.md
outputs/reports/prompt18/reference/reproducibility_package_audit.json
outputs/reports/prompt18/reference/dependency_and_model_manifest.md
outputs/reports/prompt18/reference/dependency_and_model_manifest.json
outputs/reports/prompt18/presented/final_package_summary.md
```

Use:

| Package | Archive Path | Entry Count | Raw Data Issues | Model Binary Issues | Pycache Issues | Status | Notes |
|---|---|---:|---|---|---|---|---|

Status values:

```text
pass
partial
fail
blocked
```

---

# Part K — Documentation and System-Report Evidence Polish

## Objective

Prepare the evidence needed for final system-report writing, without overclaiming.

Update or create concise docs describing:

```text
- final Track A candidate;
- final Track B candidate;
- fallback candidates;
- full big-grid search setup;
- 2024-only freeze discipline;
- locked 2025 evaluation;
- official parity status;
- local reference-vs-batched parity status;
- Stage 1 text-mode decision;
- package split;
- method maturity caveats.
```

Do not overclaim:

```text
KG-MoE-Lite as full GNN/MoE
CEVA-KF/CIGA as full causal discovery
ARMOR-OMD as fully proven online learning
HGF-MPC as full MPC if still one-step/simplified
BGE/FinBERT as final if not selected by evidence
CUDA as useful if NumPy is faster
official parity if server is blocked
```

---

# Part L — Final Status and Recommendation

## Required Presented Reports

Write:

```text
outputs/reports/prompt18/presented/executive_summary.md
outputs/reports/prompt18/presented/final_submission_readiness_report.md
outputs/reports/prompt18/presented/final_recommendation.md
outputs/reports/prompt18/README.md
```

### `final_submission_readiness_report.md`

Use exactly:

```md
# Prompt18 Final Submission Readiness Report

## 1. Readiness Verdict

Choose exactly one:

- Ready for final submission package handoff
- Locally ready, official-server validation blocked
- Not ready; big-grid evidence insufficient
- Not ready; parity failed
- Not ready; package failed

## 2. Remaining Prompt17b Blockers

## 3. Official Server Status

## 4. Big Grid Search Coverage

## 5. Big Grid Top Candidates

## 6. 2024-Only Candidate Freeze

## 7. Locked 2025 Evaluation

## 8. Final Local Parity

## 9. Final Official Server Parity

## 10. Final Track A Candidate

## 11. Final Track B Candidate

## 12. Stage 1 / Text Model Decision

## 13. Runtime / CUDA Decision

## 14. Package Split Status

## 15. Evidence for System Report

## 16. Remaining Risks

## 17. Recommended Next Prompt
```

### `final_recommendation.md`

Use:

```md
# Prompt18 Final Recommendation

## 1. Executive Verdict

## 2. Final Track A Recommendation

- Primary:
- Fallback:
- Evidence:
- Locked 2025:
- Official parity:
- Risks:

## 3. Final Track B Recommendation

- Primary:
- Fallback:
- Evidence:
- Locked 2025:
- Official parity:
- Risks:

## 4. Candidates for Runtime Package

## 5. Candidates for Reproducibility / System Report Only

## 6. Candidates to Drop

## 7. Package Decision

## 8. What Can Be Claimed

## 9. What Must Not Be Claimed

## 10. Next Prompt
```

---

## Constraints

- This is not a new-method prompt.
- You must run at least one big grid search unless a hard gate fails.
- Do not call a small smoke run a big grid.
- Do not use 2025 public A to select or tune final candidates.
- Do not use `LocalSmokeBacktester` for final evidence.
- Do not claim official readiness unless official server parity passes.
- Do not modify or redistribute raw official data.
- Do not include raw official data in packages.
- Do not include large caches or HF model binaries in official runtime package.
- Do not silently download models.
- Do not overclaim method maturity.
- Do not overclaim CUDA.
- Prefer correctness and reproducibility over speed.
- Checkpoint long runs.
- If interrupted, preserve partial artifacts and write an incomplete status report.
- If a hard gate fails, stop and report the failure rather than continuing to produce misleading final rankings.

---

## Expected Final Assistant Response

After completing Prompt18, respond with:

1. readiness verdict;
2. whether official server was started/fixed;
3. official server parity status;
4. big grid option actually run: Option 1, 2, or 3;
5. candidate count, date count, tracks, text modes, backend, runtime;
6. top Track A candidates from big grid;
7. top Track B candidates from big grid;
8. final 2024-only Track A freeze;
9. final 2024-only Track B freeze;
10. locked 2025 evaluation summary;
11. local reference-vs-batched parity status;
12. runtime/CUDA decision;
13. package split status;
14. exact report paths;
15. remaining blockers;
16. recommended next prompt.
