# Prompt 17 — Overnight Official-Semantics Grid Search, Target-Tensor Wiring, Cached Text Features, and Candidate Freeze

## Role

You are a senior quantitative research engineer, GPU/backtesting systems engineer, optimisation engineer, and shared-task submission lead.

You are working on the NLPCC 2026 Shared Task 4 repository after Prompt16 cleaned the repo, audited strategy implementations, added an official-semantics reference backtester, added NumPy/Torch batched replay, and built the optimisation/five-fold helper layer.

This prompt is intended to support an **overnight run**.

Long-running searches are allowed in this prompt, but they must be staged, logged, resumable, and checkpointed. Do not launch one uncontrolled monolithic run without intermediate outputs.

The main goal is to finally connect the strategy layer to the official-semantics accelerated replay layer and run a meaningful overnight search.

---

## 0. Mandatory Context to Read First

Read the latest Prompt13–Prompt16 artifacts before changing code:

```text
docs/reports/prompt16/final_status_report.md
docs/reports/prompt16/repo_cleanup_report.md
docs/reports/prompt16/method_implementation_audit.md
docs/reports/prompt16/backtester_semantics_audit.md
docs/reports/prompt16/cuda_backtester_report.md
docs/reports/prompt16/official_equivalence_report.md
docs/reports/prompt16/optimisation_engine_report.md
docs/reports/prompt16/five_fold_split_plan.md
docs/reports/prompt16/grid_search_runtime_estimate.md
docs/reports/prompt16/package_cleanliness_report.md
docs/implementation_logs/20260531_144835_prompt16_repo_cleanup_backtester_optimisation.md

outputs/reports/prompt15/final_recommendation.md
outputs/reports/prompt15/top5_candidate_pipelines.md
outputs/reports/prompt15/wrapper_parity_validation.md
outputs/reports/prompt15/final_system_evidence_pack.md
outputs/reports/prompt15/stage1_local_model_integration_report.md
outputs/reports/prompt15/model_implementation_status.md

outputs/reports/prompt14/final_recommendation.md
outputs/reports/prompt14/official_local_parity_rerun_report.md
outputs/reports/prompt14/package_rebuild_report.md
```

If some outputs have been moved during cleanup, read their preserved copies under `docs/reports/` or the latest available equivalent.

Also inspect the relevant code:

```text
NLPCC_tasks/agent_platform/agents/build_agent.py
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
src/tools/optimiser/
src/tools/experiments/
src/tools/reporting/
configs/
scripts/
tests/
```

---

## 1. Current Ground Truth from Prompt16

Treat the following as ground truth unless the repo proves otherwise:

```text
1. LocalSmokeBacktester is legacy research-only and should not be used for final grid evidence.
2. The correct local reference is:
     src/tools/backtesting/reference_official_semantics.py
3. The accelerated replay layer is:
     src/tools/backtesting/cuda_vectorized_backtester.py
   with NumPy fallback and optional Torch CUDA.
4. NumPy batched replay is currently preferred for quick/medium searches.
5. CUDA is real but was slower on tiny batches; retest only at larger batch sizes.
6. Prompt15 grid still used the legacy backtester and is not final evidence.
7. The missing bridge is:
     strategy-specific target-tensor generation
   so that strategies can be evaluated through official-semantics batched replay.
8. The optimiser/five-fold framework exists but is not fully wired into target generation for all strategies.
9. Advanced strategies are functional MVPs but not yet fully validated.
10. Stage 1 local Hugging Face models are integrated but disabled by default unless configs enable them.
```

Your first task is to close the missing bridge.

---

## 2. Official Constraints to Preserve

Preserve these constraints:

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
- Default final runtime must retain deterministic no-model / no-API fallback.
- Do not tune final submission parameters based on 2025 public A. Use 2025 only for locked evaluation unless clearly labelled as research-only robustness analysis.

---

## 3. Main Objective

By the end of Prompt17, the repository should have:

```text
strategy config
→ leakage-safe SystemRunner target-weight generation
→ target-weight tensor cache
→ official-semantics reference replay
→ NumPy/Torch batched replay
→ overnight grid/halving/five-fold search
→ 2024 construction ranking
→ locked 2025 evaluation for selected candidates
→ official/server parity spot checks if server available
→ final candidate freeze recommendation
```

The goal is to produce **decision-grade evidence**, not just plumbing evidence.

---

## 4. Overnight Run Policy

This prompt is allowed to run long jobs, but only under the following controls:

1. Use checkpointed stages.
2. Write progress files after each stage.
3. Avoid monolithic all-or-nothing scripts.
4. Resume from caches if interrupted.
5. Keep raw data untouched.
6. Keep generated artifacts under:

```text
.var/prompt17/
```

7. Copy only small final summaries to:

```text
docs/reports/prompt17/
```

8. Log all major commands and runtimes.
9. If CUDA is used, log device name, memory, batch size, and whether CUDA is actually faster than NumPy.
10. If Hugging Face local text models are used, cache their outputs once and reuse cached features.

---

## 5. Required Deliverables

Create:

```text
docs/implementation_logs/<timestamp>_prompt17_overnight_grid_search.md

docs/reports/prompt17/target_tensor_generation_report.md
docs/reports/prompt17/text_feature_cache_report.md
docs/reports/prompt17/backtester_parity_spotcheck_report.md
docs/reports/prompt17/overnight_search_plan.md
docs/reports/prompt17/overnight_search_results.md
docs/reports/prompt17/top_candidates_2024_construction.md
docs/reports/prompt17/top_candidates_2025_locked_evaluation.md
docs/reports/prompt17/five_fold_robustness_report.md
docs/reports/prompt17/official_server_spotcheck_report.md
docs/reports/prompt17/final_candidate_freeze_report.md
docs/reports/prompt17/package_update_report.md
docs/reports/prompt17/final_status_report.md
```

Use `.var/prompt17/` for detailed runtime outputs:

```text
.var/prompt17/cache/
.var/prompt17/target_tensors/
.var/prompt17/search_runs/
.var/prompt17/checkpoints/
.var/prompt17/benchmarks/
.var/prompt17/packages/
```

---

# Part A — Wire Strategy-Specific Target-Tensor Generation

## Objective

Build the missing bridge from strategy configs / SystemRunner decisions to target-weight tensors that can be replayed by the official-semantics batched backtester.

## Required Behavior

For each strategy configuration and date range, generate:

```text
target_weights[t, candidate, asset]
candidate_metadata[candidate]
date_index[t]
asset_index[asset]
track
config_hash
stage_outputs_summary
fallback_flags
decision_trace_sample
```

The target tensor generation must:

1. call the same strategy logic used by the official wrapper/SystemRunner;
2. use leakage-safe daily inputs;
3. respect current-day field restrictions;
4. use only available same-day news before cutoff;
5. avoid using current-day close/high/low/return before decision time;
6. support macro and sector tracks;
7. support no-news, rule-based text, BGE-small, FinBERT, and hybrid text modes;
8. cache target tensors by config hash, date range, track, data version, and text feature version;
9. support resume if interrupted.

## Required Strategies

Target generation must support at least:

```text
S0 equal weight
S1 macro
S1 sector
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
```

## Suggested Files

Use current conventions, likely:

```text
src/tools/experiments/target_tensor_generator.py
src/tools/experiments/candidate_factory.py
src/tools/experiments/strategy_config_expander.py
src/tools/experiments/target_tensor_cache.py
src/tools/experiments/leakage_safe_input_builder.py
scripts/generate_target_tensors.py
tests/test_tools/test_experiments/test_prompt17_target_tensors.py
```

## Required Report

Write:

```text
docs/reports/prompt17/target_tensor_generation_report.md
```

Use:

| Strategy Family | Track | Configs Generated | Target Tensor Generated? | Cache Path | Dates | Assets | Fallback Rate | Status | Notes |
|---|---|---:|---|---|---:|---:|---:|---|---|

Status:

```text
pass
partial
fail
blocked
```

---

# Part B — Cache Stage 1 Text Features

## Objective

Avoid repeated expensive local Hugging Face inference during grid search.

## Required Feature Modes

Cache features for:

```text
no_news
rule_based
bge_small_zh
finbert_tone_chinese
hybrid_rule_bge_finbert
```

## Required Behavior

The cache must include:

```text
date
news source/file
news hash
stage1 mode
model name
model revision/local path
feature version
event count
sentiment summary
embedding reference or compressed vector
sector impact summary
BL view summary
fallback flag
```

Do not put full large embeddings in human-readable reports unless tiny previews are needed.

## Required Files

Likely:

```text
src/nlpcc/stage1_news/feature_cache.py
src/nlpcc/stage1_news/text_feature_store.py
scripts/build_text_feature_cache.py
tests/test_nlpcc/test_stage1_news/test_prompt17_text_feature_cache.py
```

## Required Report

Write:

```text
docs/reports/prompt17/text_feature_cache_report.md
```

Use:

| Mode | Dates Cached | News Items | Model | Cache Path | Runtime | Cache Size | Fallback Rate | Status | Notes |
|---|---:|---:|---|---|---:|---:|---:|---|---|

## Runtime Policy

If HF inference is too slow, cache only:

```text
1. rule_based full 2024;
2. rule_based full 2025;
3. bge/finbert/hybrid for a bounded sample;
```

Then estimate full cache time.

---

# Part C — Backtester Parity Spot Checks

## Objective

Before launching the overnight search, prove that target tensor replay matches the reference single-run path.

## Required Checks

For a bounded date window, compare:

```text
SystemRunner single-candidate loop
→ reference_official_semantics.py replay
→ NumPy batched replay
→ Torch CUDA replay if useful
```

For at least:

```text
S0 macro
S1 macro
S1 sector
DRO-BL-RP
BSA-RP
ARMOR-OMD
LEEQA-Rank
KG-MoE-Lite
HGF-MPC
CEVA-KF/CIGA
```

## Required Report

Write:

```text
docs/reports/prompt17/backtester_parity_spotcheck_report.md
```

Use:

| Strategy | Track | Dates | SystemRunner Value | Reference Replay Value | Batched Replay Value | CUDA Value | Max Diff | Status | Notes |
|---|---|---:|---:|---:|---:|---:|---:|---|---|

Status:

```text
pass
minor_diff
fail
blocked
not_run
```

## Rule

Do not launch overnight search if S0/S1 and at least one advanced macro and one advanced sector candidate fail local parity between SystemRunner and replay.

---

# Part D — Define the Overnight Search Plan

## Objective

Create a staged search plan that starts conservative and expands.

## Required Report

Write before running the overnight search:

```text
docs/reports/prompt17/overnight_search_plan.md
```

Use:

| Stage | Candidate Families | Text Mode | Date Range | Folds | Backend | Candidate Count | Estimated Runtime | Run? | Notes |
|---|---|---|---|---:|---|---:|---:|---|---|

## Required Stages

### Stage 0 — Smoke

```text
<= 20 candidates
<= 30 dates
rule_based / no_news only
reference + NumPy batched
```

### Stage 1 — Quick 2024 Construction Search

```text
100–300 candidates
full 2024
rule_based / no_news
NumPy batched
reference spot checks
```

### Stage 2 — Medium 2024 Construction Search

```text
500–2000 candidates
full 2024
rule_based + cached text features if available
NumPy batched
successive halving if needed
```

### Stage 3 — Five-Fold Research CV

```text
top candidate families only
five-fold 80/20 over 2024–2025
research-only robustness
do not call this final tuning
```

### Stage 4 — Locked 2025 Evaluation

```text
top 5–10 candidates selected from 2024 only
full 2025
no parameter changes
```

### Stage 5 — Official Server Spot Check

```text
best final candidates
short deterministic window
official server if reachable
```

---

# Part E — Run Overnight Search

## Objective

Run the staged search plan.

## Required Candidate Families

Include at least:

```text
S0
S1
DRO-BL-RP
BSA-RP
ARMOR-OMD
LEEQA-Rank
KG-MoE-Lite
HGF-MPC
CEVA-KF/CIGA
risk parity
sector rotation
OCO fallback
```

## Required Search Parameters

Include meaningful parameter variation for:

```text
DRO-BL-RP:
  tau, confidence_scale, rp_anchor_weight, turnover_cap, max_weight

BSA-RP:
  regime_decay, risk_budget_floor, belief_smoothing, drawdown_throttle

ARMOR-OMD:
  eta, expert_floor, regret_decay, transaction_penalty

LEEQA-Rank:
  feature weights, top_k, softmax_temperature, turnover_cap

KG-MoE-Lite:
  graph_decay, router_temperature, expert_weights, sector_cap

HGF-MPC:
  kalman_process_var, kalman_obs_var, horizon, turnover_penalty

CEVA-KF/CIGA:
  stability_threshold, causal_confidence_scale, impact_decay, overlay_weight

Text modes:
  no_news, rule_based, bge_small_zh, finbert_tone_chinese, hybrid_rule_bge_finbert
```

## Scoring

Use a conservative score:

```text
competition_score =
  0.30 * sharpe_rank_score
+ 0.20 * cumulative_return_rank_score
+ 0.20 * drawdown_rank_score
+ 0.15 * turnover_rank_score
+ 0.10 * wrapper_or_replay_parity_score
+ 0.05 * simplicity_score

research_score =
  0.25 * novelty
+ 0.20 * interpretability
+ 0.20 * ablation_cleanliness
+ 0.15 * visualisability
+ 0.10 * reproducibility
+ 0.10 * report_signal

conservative_score =
  0.55 * competition_score
+ 0.30 * research_score
+ 0.15 * robustness_score
- 0.10 * overfit_risk
- 0.08 * dependency_risk
- 0.08 * parity_risk
- 0.05 * implementation_complexity
```

Also report raw metrics:

```text
final value
cumulative return
Sharpe
max drawdown
turnover
trade count
cash utilisation
fallback rate
runtime
```

## Required Outputs

Write detailed run artifacts to:

```text
.var/prompt17/search_runs/
```

Write compact reports to:

```text
docs/reports/prompt17/overnight_search_results.md
docs/reports/prompt17/top_candidates_2024_construction.md
```

Use:

| Rank | Candidate | Track | Family | Text Mode | Params Hash | 2024 Return | 2024 Sharpe | Drawdown | Turnover | Fallback Rate | Competition Score | Research Score | Conservative Score | Runtime | Status | Notes |
|---:|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|---|

---

# Part F — Locked 2025 Evaluation for Selected Candidates

## Objective

Evaluate selected candidates on 2025 without tuning.

## Selection Rule

Select candidates from 2024 construction results only:

```text
top 5 Track A
top 5 Track B
top 5 overall
plus S0/S1 baselines
```

Do not change parameters after viewing 2025.

## Required Report

Write:

```text
docs/reports/prompt17/top_candidates_2025_locked_evaluation.md
```

Use:

| Candidate | Track | 2024 Rank | 2025 Return | 2025 Sharpe | 2025 Drawdown | 2025 Turnover | Generalisation | Promote? | Notes |
|---|---|---:|---:|---:|---:|---:|---|---|---|

Generalisation:

```text
strong
acceptable
weak
failed
not_run
```

---

# Part G — Five-Fold Robustness Report

## Objective

Run five-fold research CV for top candidate families if time permits.

This is **research-only robustness**, not final 2025 tuning.

## Required Candidates

At least:

```text
S1 macro
S1 sector
best DRO-BL-RP
best BSA-RP
best ARMOR-OMD
best LEEQA-Rank
best KG-MoE-Lite
best HGF-MPC
best CEVA-KF/CIGA
```

## Required Report

Write:

```text
docs/reports/prompt17/five_fold_robustness_report.md
```

Use:

| Candidate | Track | Fold 1 Sharpe | Fold 2 Sharpe | Fold 3 Sharpe | Fold 4 Sharpe | Fold 5 Sharpe | Mean Sharpe | Std Sharpe | Worst Drawdown | Robustness Verdict |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|

Robustness verdict:

```text
robust
acceptable
fragile
failed
not_run
```

---

# Part H — Official Server Spot Check

## Objective

If official server is reachable, run short official-server spot checks for final candidates.

## Required Candidates

At least:

```text
S0 macro
S1 macro
S1 sector
best Track A candidate
best Track B candidate
```

## Required Report

Write:

```text
docs/reports/prompt17/official_server_spotcheck_report.md
```

Use:

| Candidate | Track | Window | Official Value | Local Reference Value | Diff | Trade Match | Status | Notes |
|---|---|---|---:|---:|---:|---|---|---|

If server is unavailable, mark blocked and preserve local evidence.

---

# Part I — Final Candidate Freeze

## Objective

Freeze final candidates for the next packaging/submission phase.

## Required Report

Write:

```text
docs/reports/prompt17/final_candidate_freeze_report.md
```

Use:

```md
# Prompt17 Final Candidate Freeze Report

## 1. Final Track A Recommendation

- Candidate:
- Fallback:
- Evidence:
- Risks:
- Required final checks:

## 2. Final Track B Recommendation

- Candidate:
- Fallback:
- Evidence:
- Risks:
- Required final checks:

## 3. Top 5 Overall Candidates

| Rank | Candidate | Track | Family | Evidence | Action |
|---:|---|---|---|---|---|

## 4. Candidates to Package

## 5. Candidates for Report/Ablation Only

## 6. Candidates to Drop

## 7. Final Configs to Freeze

## 8. Remaining Submission Blockers
```

---

# Part J — Package Update

## Objective

Rebuild a clean package containing the frozen final candidate configs.

## Package Rules

Include:

```text
NLPCC_tasks/agent_platform/agents/build_agent.py
src/nlpcc/
configs/
requirements.txt or lock file
README_SUBMISSION.md
frozen final system configs
```

Exclude:

```text
raw official data
NLPCC_tasks/dataset/
outputs/
.var/
models/
outputs/models/
__pycache__
.pyc
large HF model files
large logs
```

If final configs require local HF models, include only a manifest and clear download/cache instructions, not model binaries.

## Required Report

Write:

```text
docs/reports/prompt17/package_update_report.md
```

Use:

| Package Item | Included? | Status | Notes |
|---|---|---|---|

---

# Part K — Final Status Report

Create:

```text
docs/reports/prompt17/final_status_report.md
```

Use exactly:

```md
# Prompt17 Final Status Report

## 1. Readiness Verdict

Choose one:

- Ready for final packaging/submission polish
- Not ready, but search evidence is complete
- Not ready

## 2. Target Tensor Wiring Status

## 3. Text Feature Cache Status

## 4. Backtester / Replay Status

## 5. Overnight Search Summary

## 6. 2024 Construction Top Candidates

## 7. 2025 Locked Evaluation Summary

## 8. Five-Fold Robustness Summary

## 9. Official Server Spot Check

## 10. Final Track A Candidate

## 11. Final Track B Candidate

## 12. Package Status

## 13. Remaining Blockers

## 14. Recommended Next Step
```

---

## Required Implementation Log

Create:

```text
docs/implementation_logs/<timestamp>_prompt17_overnight_grid_search.md
```

Use:

```md
# Implementation Log: prompt17 - overnight_grid_search

## Created

<timestamp>

## Summary

## Files Changed

## Target Tensor Generation

## Text Feature Cache

## Backtester Parity

## Overnight Search

## 2025 Locked Evaluation

## Five-Fold Robustness

## Official Server Spot Check

## Final Candidate Freeze

## Package

## Tests / Checks

## Caveats

## Artifacts

## Next Steps
```

---

## Constraints

- Do not use legacy `LocalSmokeBacktester` for final selection evidence.
- Use `reference_official_semantics.py` and/or official-semantics batched replay for final search evidence.
- Do not tune based on 2025 public A.
- Do not use current-day close/high/low/return before decision time.
- Do not modify raw official data.
- Do not include raw official data in packages.
- Do not include Hugging Face model binaries in packages unless explicitly required and documented.
- Do not silently download models.
- Do not overclaim CUDA if NumPy remains faster.
- Do not overclaim official parity if official server is unavailable.
- Do not overclaim causal discovery, full GNN/MoE, or full online learning if the implementations are MVPs.
- Keep detailed outputs under `.var/prompt17/`; keep only compact reports under `docs/reports/prompt17/`.
- Checkpoint long runs.
- If interrupted, preserve partial results and write an incomplete-status report.

---

## Expected Final Assistant Response

After completing Prompt17, respond with:

1. readiness verdict;
2. target-tensor wiring status;
3. text feature cache status;
4. backtester/replay status;
5. overnight search summary;
6. 2024 top candidates;
7. 2025 locked evaluation summary;
8. five-fold robustness summary;
9. official server spot-check status;
10. final Track A candidate;
11. final Track B candidate;
12. package status;
13. remaining blockers;
14. next recommended step.
