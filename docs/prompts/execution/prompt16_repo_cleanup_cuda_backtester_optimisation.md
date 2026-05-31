# Prompt 16 — Repo Cleanup, Strategy Verification, Official-Equivalent CUDA Backtester, and Optimisation Engine

## Role

You are a senior quantitative research engineer, GPU/backtesting systems engineer, competition submission architect, and shared-task reliability auditor.

You are working on the NLPCC 2026 Shared Task 4 repository after Prompt15 implemented functional MVPs for the major strategy families and integrated offline local text models.

This prompt is **not** a new strategy-brainstorming prompt and **not** a full long-running grid-search prompt.

Your task is to clean and harden the repository, verify that all implemented strategies are genuinely runnable and correctly wired, inspect and repair the current local backtester, add real vectorised/CUDA-parallel acceleration if feasible, align the accelerated local backtester with official semantics, build the optimisation/fine-tuning engine, and prepare a five-fold 80/20 evaluation workflow.

When testing, keep every invoked test/run under **10 minutes**. If a full run would exceed this, run a bounded smoke/benchmark and estimate the full runtime instead of running it.

---

## 0. Mandatory Context to Read First

Read the latest Prompt13–Prompt15 artifacts before changing code:

```text
outputs/reports/prompt13/full_audit_report.md
outputs/reports/prompt13/final_recommendation.md
outputs/reports/prompt13/official_local_parity_report.md
outputs/reports/prompt13/stage1_trace_report.md
outputs/reports/prompt13/module_maturity_matrix.md
outputs/reports/prompt13/full_year_ablation_report.md
outputs/reports/prompt13/public_a_2025_evaluation_report.md

outputs/reports/prompt14/final_recommendation.md
outputs/reports/prompt14/pipeline_repair_report.md
outputs/reports/prompt14/track_status_matrix.md
outputs/reports/prompt14/stage_status_matrix.md
outputs/reports/prompt14/model_status_matrix.md
outputs/reports/prompt14/official_wrapper_repair_report.md
outputs/reports/prompt14/official_local_parity_rerun_report.md
outputs/reports/prompt14/huggingface_model_audit.md
outputs/reports/prompt14/package_rebuild_report.md

outputs/reports/prompt15/final_recommendation.md
outputs/reports/prompt15/top5_candidate_pipelines.md
outputs/reports/prompt15/wrapper_parity_validation.md
outputs/reports/prompt15/final_system_evidence_pack.md
outputs/reports/prompt15/stage1_local_model_integration_report.md
outputs/reports/prompt15/model_implementation_status.md
outputs/reports/prompt15/final_package_report.md
```

If some outputs are missing because the repo has already been cleaned, read the corresponding copied summaries under `docs/reports/`, `docs/implementation_logs/`, or the latest available path.

Also inspect:

```text
AGENTS.md
README.md
METHODOLOGY.md
WORKFLOW.md
docs/
configs/
src/nlpcc/
src/tools/
scripts/
tests/
NLPCC_tasks/
NLPCC_tasks/agent_platform/agents/build_agent.py
NLPCC_tasks/server_platform/
NLPCC_tasks/dataset/
```

---

## 1. Current Ground Truth

Treat the following as the current status unless the repository proves otherwise:

```text
Prompt14:
  - official wrapper, portfolio adapter, order planner, trade validator, and SystemRunner were repaired.
  - S0/S1 macro and S1 sector wrapper parity passed.
  - robust BL still required additional parity work.

Prompt15:
  - all seven major strategy families have functional MVP code paths:
      DRO-BL-RP
      BSA-RP
      ARMOR-OMD
      LEEQA-Rank
      KG-MoE-Lite
      HGF-MPC
      CEVA-KF / CIGA
  - BAAI/bge-small-zh-v1.5 and yiyanghkust/finbert-tone-chinese were integrated offline for Stage 1.
  - default Stage 1 remains rule-based / no-LLM fallback unless configs enable local text models.
  - Prompt15 grid evidence was runtime-bounded and not final full-year evidence.
  - package hygiene was good, but further clean extraction and final validation remain needed.
```

The focus now is:

```text
1. clean the repository;
2. verify actual strategy implementations;
3. fix and accelerate the local backtester;
4. make local backtester semantics match the official engine;
5. build optimisation/fine-tuning helpers;
6. prepare five-fold 80/20 validation across 2024–2025;
7. estimate full grid-search runtime without launching long runs.
```

---

## 2. Official Constraints to Preserve

Preserve:

- Track A / Track 1: Macro-Asset Allocation.
- Track B / Track 2: Sector-Rotation Allocation.
- Agents receive daily Top-20 financial hot news and historical ETF/index price data.
- 2024 data is for training / construction.
- 2025 data is public A-list / Phase A evaluation.
- 2026-01-01 to 2026-06-01 is hidden B-list evaluation.
- B-list is centrally run by organisers using submitted code.
- Current-day close/high/low/return must not be used before decision time.
- Same-day news is usable only under the official timestamp cutoff.
- Transaction friction is 0.01%.
- Evaluation emphasises Sharpe ratio, cumulative return, max drawdown, and turnover categories.
- External models, datasets, and knowledge bases must be available before 2026.
- Any training, fine-tuning, retrieval, or knowledge construction must be reproducible if used.
- Raw official data must not be modified or redistributed.
- Default final runtime must retain a deterministic no-model / no-API fallback.
- Do not tune final parameters based on 2025 public A unless the report explicitly labels it as a research-only experiment.

---

## 3. Runtime Rule

All tests and command runs in this prompt must obey:

```text
Maximum wall-clock per command: 10 minutes
```

If an operation would exceed 10 minutes:

1. run a bounded smoke/sample benchmark instead;
2. estimate full runtime from the sample;
3. write the estimate to the report;
4. do not launch the long run.

This is especially important for:

```text
CUDA benchmarks
full grid search
Hugging Face model inference
five-fold optimisation
official server parity
```

---

## 4. Required Deliverables

Create:

```text
docs/implementation_logs/<timestamp>_prompt16_repo_cleanup_backtester_optimisation.md

docs/reports/prompt16/repo_cleanup_report.md
docs/reports/prompt16/method_implementation_audit.md
docs/reports/prompt16/backtester_semantics_audit.md
docs/reports/prompt16/cuda_backtester_report.md
docs/reports/prompt16/official_equivalence_report.md
docs/reports/prompt16/optimisation_engine_report.md
docs/reports/prompt16/five_fold_split_plan.md
docs/reports/prompt16/grid_search_runtime_estimate.md
docs/reports/prompt16/package_cleanliness_report.md
docs/reports/prompt16/final_status_report.md
```

Use `.var/` or another ignored runtime directory for large temporary outputs:

```text
.var/prompt16/
.var/prompt16/archive_outputs/
.var/prompt16/benchmarks/
.var/prompt16/smoke_results/
```

Avoid creating large new files under `outputs/`. The goal is to clean the repo, not make another huge output tree.

If existing tooling requires `outputs/`, either:
1. redirect it to `.var/prompt16/`, or
2. run it temporarily and then move/delete generated artifacts after preserving small summary reports.

---

# Part A — Repository Cleanup

## Objective

Clean the repo into a submission/development-ready state.

## Tasks

1. Inventory all generated artifacts and large folders:
   ```text
   outputs/
   .var/
   __pycache__/
   .pytest_cache/
   .mypy_cache/
   .ruff_cache/
   models/
   outputs/models/
   temporary benchmark outputs
   copied package directories
   generated old reports that are not needed
   ```

2. Remove or archive generated outputs:
   - If `outputs/` is untracked/generated, remove it after copying key summaries into `docs/reports/`.
   - If some `outputs/` artifacts are needed as evidence, copy small `.md` / `.csv` summaries into `docs/reports/prompt16/reference/`.
   - Do **not** delete raw official data.
   - Do **not** delete source code, configs, tests, docs, or official starter files.

3. Update `.gitignore` to ensure generated artifacts stay out of the repo:
   ```text
   outputs/
   .var/
   .pytest_cache/
   __pycache__/
   *.pyc
   outputs/models/
   models/huggingface/
   .cache/
   ```

4. Ensure docs are not mixed with runtime artifacts.

5. Create a cleanup manifest.

## Required Report

Write:

```text
docs/reports/prompt16/repo_cleanup_report.md
```

Use:

| Path | Type | Action | Reason | Preserved Summary? | Notes |
|---|---|---|---|---|---|

Use action values:

```text
keep
move_to_var
delete_generated
ignore_only
manual_review
```

---

# Part B — Verify All Strategy Implementations

## Objective

Check that all claimed strategies are actually implemented, importable, runnable, tested, and registered.

## Required Methods

Audit:

```text
S0 equal weight
S1 quant core
DRO-BL-RP
BSA-RP
ARMOR-OMD
LEEQA-Rank
KG-MoE-Lite
HGF-MPC
CEVA-KF / CIGA
risk parity
sector rotation
OCO fallback
rule-based Stage 1
BGE-small extractor
FinBERT Chinese extractor
hybrid local text extractor
no-LLM fallback
```

## Required Checks

For each method, verify:

```text
code path exists
config exists
registry entry exists
minimal synthetic run passes
local wrapper run passes
SystemRunner can call it
tests exist
stage dependencies exist
fallback behavior works
no future data access
method maturity label is honest
```

## Required Report

Write:

```text
docs/reports/prompt16/method_implementation_audit.md
```

Use:

| Method | Code Path | Config | Registry | Tests | Minimal Run | Wrapper Run | Future-Leakage Check | Maturity | Status | Fix Needed |
|---|---|---|---|---|---|---|---|---|---|---|

Status values:

```text
pass
partial
fail
missing
```

## Repair Rule

If a method is currently only a superficial MVP or broken, fix it enough that:

```text
1. it imports;
2. it runs on a short bounded sample;
3. it returns valid target weights/trades;
4. it does not crash the SystemRunner;
5. its maturity is labelled honestly.
```

Do not add new strategy families.

---

# Part C — Audit Current Backtester Usage

## Objective

Determine exactly which backtester is currently being used in each path.

## Tasks

Inspect:

```text
src/tools/backtesting/
src/tools/backtesting/local_backtester.py
src/tools/backtesting/vectorized_backtester.py
src/tools/backtesting/cuda_backend.py
src/tools/backtesting/official_server_runner.py
scripts/run_experiment.py
scripts/run_local_smoke.py
scripts/run_prompt13_audit.py
scripts/run_prompt14_audit.py
scripts/run_prompt15_*.py
```

Identify:

```text
which backtester is used by grid search;
which backtester is used by wrapper validation;
which backtester is closest to official semantics;
which one, if any, uses CUDA;
whether vectorized_backtester is truly vectorized or only a wrapper;
whether cuda_backend is real or placeholder;
where semantics differ from official server;
whether buy-before-sell, no same-day sell proceeds, transaction cost, and current-day field masking are implemented consistently.
```

## Required Report

Write:

```text
docs/reports/prompt16/backtester_semantics_audit.md
```

Use:

| Backtester / Runner | Path | Used By | CUDA? | Vectorised? | Official Semantics Match? | Known Differences | Status | Required Fix |
|---|---|---|---|---|---|---|---|---|

---

# Part D — Build or Repair CUDA-Accelerated Parallel Local Backtester

## Objective

The current project seems to claim vectorized/CUDA support, but it may not be actually implemented. Build or repair a genuinely parallel local backtester where feasible, using the current laptop GPU class, e.g. NVIDIA RTX 4060 / 4070-class CUDA.

## Requirements

Implement a backend with this policy:

```text
Preferred:
  PyTorch CUDA tensor backend, because it is widely installed and easier to fallback to CPU.

Fallback:
  NumPy CPU vectorized backend.

Optional:
  Numba/CuPy only if already available and not disruptive.
```

Do not introduce fragile dependencies unless necessary.

## Required Backend Behavior

The accelerated local backtester should:

1. batch-evaluate many parameter/config combinations;
2. preserve official execution semantics;
3. support CPU fallback;
4. support CUDA if `torch.cuda.is_available()`;
5. produce numerically equivalent results to the reference local official-semantics backtester for S0/S1 within a strict tolerance;
6. never use current-day close/high/low/return before decision time;
7. apply transaction cost;
8. respect buy-before-sell or the official execution order exactly;
9. preserve no same-day sell proceeds for buys;
10. support macro and sector tracks;
11. expose benchmark timing.

## Important

If full CUDA implementation is too large, implement the acceleration at the level most useful for grid search:

```text
batch scoring / portfolio-value replay / parameter grid evaluation
```

But still keep the official-compatible reference path as the source of truth.

## Suggested Files

Use current repo conventions, likely:

```text
src/tools/backtesting/reference_official_semantics.py
src/tools/backtesting/cuda_vectorized_backtester.py
src/tools/backtesting/batched_grid_backtester.py
src/tools/backtesting/backtester_parity.py
tests/test_tools/test_backtesting/test_prompt16_cuda_backtester.py
scripts/benchmark_backtester.py
```

## Required Tests

Add tests proving:

```text
CPU reference and CUDA/parallel backend match S0 on small sample
CPU reference and CUDA/parallel backend match S1 on small sample
CUDA backend falls back to CPU if unavailable
official execution semantics are preserved
batch results match single-run loop results
```

## Required Report

Write:

```text
docs/reports/prompt16/cuda_backtester_report.md
```

Use:

| Check | Result | Evidence | Notes |
|---|---|---|---|

Also include benchmark table:

| Backend | Device | Candidates | Dates | Runtime Seconds | Speedup vs Reference | Max Metric Diff | Status |
|---|---|---:|---:|---:|---:|---:|---|

## Runtime Limit

Do not benchmark more than 10 minutes. Use small candidate/date samples and extrapolate.

---

# Part E — Official Equivalence Repair

## Objective

Make the local reference backtester and accelerated backtester match official server semantics as closely as possible.

## Tasks

Using short deterministic windows only, compare:

```text
official server
reference local official-semantics backtester
accelerated local backtester
```

For at least:

```text
S0 macro
S1 macro
S1 sector
one advanced macro candidate, preferably DRO-BL-RP or robust BL
```

If official server is unavailable, mark official comparison as blocked and still compare reference vs accelerated local.

## Required Report

Write:

```text
docs/reports/prompt16/official_equivalence_report.md
```

Use:

| Strategy | Track | Window | Official Value | Reference Local Value | CUDA/Parallel Value | Official-Local Diff | Local-CUDA Diff | Trade Match | Status | Notes |
|---|---|---|---:|---:|---:|---:|---:|---|---|---|

Status:

```text
pass
minor_diff
fail
blocked
not_run
```

## Rule

If official equivalence fails, do not hide it. State exact mismatch and likely cause.

---

# Part F — Build Optimisation / Fine-Tuning Engine

## Objective

Build an optimisation engine for strategy/config parameters and optional local text-model feature settings.

This is not necessarily neural fine-tuning. It should include:

```text
strategy parameter optimisation
grid search
random search
successive halving / early stop
walk-forward / cross-validation
five-fold 80/20 validation
optional local text-model feature toggles
result storage
config freeze
```

If actual neural fine-tuning is included, it must be optional, disabled by default, and fully reproducible.

## Required Split Scheme

Prepare a five-fold 80/20 validation scheme over the combined available 2024–2025 timeline:

```text
1. Combine eligible 2024–2025 trading dates.
2. Split into 5 chronological chunks.
3. Run 5 folds.
4. For each fold:
   - validation chunk = 20%;
   - training/construction chunks = remaining 80%;
   - train/optimise parameters on the 80%;
   - evaluate on the held-out 20%;
5. Record fold metrics.
```

Because 2025 public A should not be overfit for final claims, label this as:

```text
research cross-validation / robustness analysis
```

and keep a separate final no-tuning 2025 evaluation policy.

## Required Optimisation Targets

The optimiser should support:

```text
DRO-BL-RP parameters:
  tau, confidence_scale, rp_anchor_weight, turnover_cap, max_weight

BSA-RP parameters:
  regime_decay, risk_budget_floor, belief_smoothing, drawdown_throttle

ARMOR-OMD parameters:
  eta, expert_floor, regret_decay, transaction_penalty

LEEQA-Rank parameters:
  feature weights, top_k, softmax_temperature, turnover_cap

KG-MoE-Lite parameters:
  graph_decay, router_temperature, expert_weights, sector_cap

HGF-MPC parameters:
  kalman_process_var, kalman_obs_var, horizon, turnover_penalty

CEVA-KF/CIGA parameters:
  stability_threshold, causal_confidence_scale, impact_decay, overlay_weight

Text model parameters:
  stage1_mode in {rule_based, bge_small_zh, finbert_tone_chinese, hybrid_rule_bge_finbert}
  sentiment_weight
  embedding_relevance_weight
```

## Required Files

Likely:

```text
src/tools/optimiser/parameter_space.py
src/tools/optimiser/five_fold_split.py
src/tools/optimiser/cross_validation.py
src/tools/optimiser/successive_halving.py
src/tools/optimiser/optimisation_engine.py
src/tools/optimiser/runtime_estimator.py
configs/tools/optimisation/prompt16_search_space.yaml
configs/tools/optimisation/prompt16_five_fold.yaml
scripts/run_optimisation.py
tests/test_tools/test_optimiser/test_prompt16_optimisation_engine.py
```

## Required Report

Write:

```text
docs/reports/prompt16/optimisation_engine_report.md
docs/reports/prompt16/five_fold_split_plan.md
```

Use for split plan:

| Fold | Train Chunks | Validation Chunk | Train Date Range(s) | Validation Date Range | Notes |
|---:|---|---|---|---|---|

Use for optimiser:

| Component | Status | Path | Test | Notes |
|---|---|---|---|---|

## Runtime Limit

Do not run the full optimiser if it exceeds 10 minutes.

Run:

```text
a tiny smoke optimisation
+ runtime estimate for full search
```

---

# Part G — Full Grid Search Runtime Estimate

## Objective

Estimate how long a full grid search would take using:

```text
reference local backtester
CPU vectorized backend
CUDA/parallel backend
```

Do not run the full grid.

## Required Estimate Dimensions

Estimate runtime for:

```text
number of stage combinations
number of parameter combinations
number of dates
number of tracks
number of folds
with and without local HF inference
with cached HF features
```

## Required Report

Write:

```text
docs/reports/prompt16/grid_search_runtime_estimate.md
```

Use:

| Scenario | Candidates | Dates | Folds | Backend | HF Mode | Estimated Runtime | Feasible Overnight? | Notes |
|---|---:|---:|---:|---|---|---:|---|---|

Also recommend:

```text
1. quick search under 30 minutes;
2. medium search under 3 hours;
3. overnight search;
4. full research search if time permits.
```

---

# Part H — Package Cleanup and Rebuild

## Objective

Rebuild a clean candidate package after cleanup and helper repairs.

The package should include:

```text
NLPCC_tasks/agent_platform/agents/build_agent.py
src/nlpcc/
src/tools/ only if required for runtime or documented support
configs/
requirements.txt or lock file
README_SUBMISSION.md
minimal smoke script if appropriate
```

The package must exclude:

```text
raw official data
NLPCC_tasks/dataset/
outputs/
.var/
outputs/models/
models/
__pycache__
.pyc
large logs
notebooks unless required
```

## Required Report

Write:

```text
docs/reports/prompt16/package_cleanliness_report.md
```

Use:

| Package Item | Required? | Included? | Status | Notes |
|---|---|---|---|---|

---

# Part I — Final Status Report

Create:

```text
docs/reports/prompt16/final_status_report.md
```

Use exactly:

```md
# Prompt16 Final Status Report

## 1. Readiness Verdict

Choose one:
- Ready for full grid search
- Not ready, but helper layer is close
- Not ready

## 2. Repo Cleanup Status

## 3. Strategy Implementation Status

| Method | Status | Remaining Issue |
|---|---|---|

## 4. Backtester Status

- Current reference backtester:
- Current grid-search backtester:
- CUDA/parallel backend:
- Official equivalence status:

## 5. Optimisation Engine Status

- Grid search:
- Random search:
- Successive halving:
- Five-fold split:
- Runtime estimator:

## 6. Five-Fold 80/20 Split Status

## 7. Runtime Estimate Summary

## 8. Package Status

## 9. Recommended Next Step

Do not propose a full long run unless the helper layer is ready.
```

---

## Required Implementation Log

Create:

```text
docs/implementation_logs/<timestamp>_prompt16_repo_cleanup_backtester_optimisation.md
```

Use:

```md
# Implementation Log: prompt16 - repo_cleanup_backtester_optimisation

## Created

<timestamp>

## Summary

## Files Changed

## Repo Cleanup

## Strategy Verification

## Backtester Audit

## CUDA / Parallel Backtester

## Official Equivalence

## Optimisation Engine

## Five-Fold Split

## Runtime Estimate

## Package

## Tests / Checks

## Caveats

## Artifacts

## Next Steps
```

---

## Constraints

- Do not run any command for more than 10 minutes.
- Do not run the full grid search in this prompt.
- Do not tune final parameters based on 2025 public A without labelling it research-only.
- Do not remove source code, configs, tests, docs, or official starter files.
- Do not delete raw official data.
- Do not include raw official data in packages.
- Do not include Hugging Face model files in packages.
- Do not silently download models.
- Do not overclaim CUDA if backend only falls back to CPU.
- Do not claim official equivalence unless official server comparison or exact reference semantics support it.
- If CUDA is unavailable or PyTorch is CPU-only, implement CPU vectorization and mark CUDA as blocked.
- If current laptop GPU is available, use it for bounded benchmark only.
- Prefer correctness over speed.
- Prefer official-equivalent reference backtester over an inaccurate fast one.
- Keep generated artifacts out of the clean repo.

---

## Expected Final Assistant Response

After completing Prompt16, respond with:

1. readiness verdict;
2. repo cleanup summary;
3. method implementation audit summary;
4. current backtester used by each pipeline;
5. whether CUDA acceleration is real, partial, or blocked;
6. whether accelerated results match reference/official semantics;
7. optimisation engine status;
8. five-fold split status;
9. grid-search runtime estimates;
10. package cleanliness status;
11. files changed;
12. tests/checks run;
13. next recommended action.
