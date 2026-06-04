# Prompt17b — Full-Horizon Official-Semantics Validation, Advanced Parity Closure, and Candidate Freeze Repair

## Role

You are a senior quantitative research engineer, LLM-systems architect, GPU/backtesting engineer, optimiser engineer, shared-task submission strategist, and reliability auditor.

You are continuing the NLPCC 2026 Shared Task 4 repository after Prompt17. Prompt17 successfully added important infrastructure, especially SystemRunner target-tensor generation, Stage 1 text feature caching, and official-semantics NumPy batched replay. However, Prompt17 did **not** complete the intended full overnight validation. It produced bounded smoke evidence only.

Your job in Prompt17b is to **fix the unfinished issues from Prompt17**, not to add new strategy families.

Be conservative. Treat any previous “ready for final packaging/submission polish” claim as provisional unless revalidated by full-horizon evidence, broad parity checks, and honest locked-evaluation discipline.

---

## Current Ground Truth from Prompt16–Prompt17

Treat the following as the current project state unless the repository proves otherwise.

### Prompt16 Ground Truth

Prompt16 added:

```text
- reusable official-semantics reference backtester:
    src/tools/backtesting/reference_official_semantics.py

- NumPy/Torch official-semantics batched replay:
    src/tools/backtesting/cuda_vectorized_backtester.py

- optimiser helpers:
    src/tools/optimiser/

- five-fold 80/20 chronological splitter over combined 2024–2025 dates

- clean package dry-run

- main blocker identified:
    strategy-specific target tensor generation was not yet wired into official-semantics replay
```

Prompt16 also established:

```text
- LocalSmokeBacktester is legacy research-only.
- Prompt15 grid evidence is not final because it used legacy local backtesting.
- NumPy batched replay is preferred until CUDA proves useful at larger scale.
- Official server was unavailable in Prompt16.
- Advanced methods are functional MVPs/prototypes, not fully validated final systems.
```

### Prompt17 Ground Truth

Prompt17 appears to have implemented:

```text
- SystemRunner-based target tensor generation
- leakage-safe input masking:
    current-day open allowed
    current-day close/high/low/change/pct_change masked before strategy execution
- Stage 1 feature cache for:
    no_news
    rule_based
    bge_small_zh
    finbert_tone_chinese
    hybrid_rule_bge_finbert
- official-semantics NumPy batched replay
- bounded 2024 construction search
- bounded 2025 locked evaluation
- bounded five-fold replay
- clean package audit
```

However, Prompt17 left several issues unfinished:

```text
1. The so-called overnight search was bounded:
     24 candidates
     20 construction dates
     10 locked 2025 dates
     NumPy backend
     ~85.56 seconds

2. Backtester parity was too narrow:
     parity report covered only S0 macro and S0 sector
     it did not prove S1 macro, S1 sector, or advanced candidate parity

3. Official server spotcheck was blocked:
     http://localhost:6207 refused connection

4. Track B freeze is questionable:
     sector_rotation_graph15 was frozen even though bounded 2024 ranking placed S1 sector candidates above it.
     This risks using 2025 locked evaluation as a selection filter.

5. Five-fold robustness was bounded:
     it used bounded 2024 tensor horizon, not the full 485-date Prompt16 split.

6. BGE/FinBERT/hybrid Stage 1 modes were cache-smoked but not meaningfully included in target-tensor ranking.

7. The previous final status “Ready for final packaging/submission polish” is too optimistic unless Prompt17b validates it.
```

Prompt17b must fix these issues directly.

---

## Objective

By the end of Prompt17b, the repository must have decision-grade evidence for whether the project is actually ready for Prompt18 packaging/report polish.

The goal is to produce:

```text
1. full-horizon 2024 construction evidence;
2. broad reference-vs-batched replay parity evidence;
3. proper 2024-only candidate freeze discipline;
4. locked 2025 evaluation without selection leakage;
5. full or materially larger five-fold robustness evidence;
6. official server spotcheck if possible;
7. corrected final readiness verdict;
8. clean package audit if and only if candidates remain viable;
9. clear separation of presented reports, progress reports, and reference data artifacts.
```

Do **not** add new strategy families. Fix evidence, parity, scale, and reporting discipline.

---

## Mandatory Files to Read First

Read all available Prompt16 and Prompt17 artifacts before changing code.

### Prompt17 Reports

```text
docs/reports/prompt17/final_status_report.md
docs/reports/prompt17/stage1_2024_grid_report.md
docs/reports/prompt17/overnight_search_results.md
docs/reports/prompt17/official_semantics_grid_search_report.md
docs/reports/prompt17/backtester_parity_spotcheck_report.md
docs/reports/prompt17/top_candidates_2025_locked_evaluation.md
docs/reports/prompt17/stage2_topk_2025_report.md
docs/reports/prompt17/five_fold_robustness_report.md
docs/reports/prompt17/five_fold_evaluation_report.md
docs/reports/prompt17/candidate_ranking_report.md
docs/reports/prompt17/ablation_report.md
docs/reports/prompt17/winner_freeze_report.md
docs/reports/prompt17/package_report.md
docs/reports/prompt17/final_recommendation.md
docs/implementation_logs/20260601_012521_prompt17_overnight_grid_search.md
docs/implementation_logs/20260601_012451_prompt17_official_semantics_target_tensor_search.md
```

If some of these reports were stored under `outputs/reports/prompt17/` instead of `docs/reports/prompt17/`, read the latest available equivalent.

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
scripts/build_text_feature_cache.py
scripts/generate_target_tensors.py
scripts/run_prompt17_overnight_search.py
scripts/run_official_server_smoke.py
tests/
configs/
```

---

## Official Constraints to Preserve

Preserve these constraints:

```text
- Track A / Track 1: Macro-Asset Allocation.
- Track B / Track 2: Sector-Rotation Allocation.
- Agents receive daily Top-20 financial hot news and historical ETF/index price data.
- 2024 data is for training / construction.
- 2025 data is public A-list / locked evaluation.
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

Prompt17b must store reports under:

```text
outputs/reports/prompt17b/
```

Do not mix progress reports, final presented reports, and detailed reference artifacts in the same flat directory.

Use this exact folder structure:

```text
outputs/reports/prompt17b/
  README.md

  progress/
    progress_00_inventory_and_gap_review.md
    progress_01_target_tensor_audit.md
    progress_02_parity_gate.md
    progress_03_full_2024_search.md
    progress_04_locked_2025_evaluation.md
    progress_05_full_five_fold.md
    progress_06_official_server_spotcheck.md
    progress_07_package_audit.md
    run_log.md

  presented/
    executive_readiness_report.md
    full_horizon_search_summary.md
    candidate_freeze_repair_report.md
    official_parity_closure_summary.md
    locked_2025_evaluation_summary.md
    five_fold_robustness_summary.md
    final_recommendation.md
    final_status_report.md

  reference/
    prompt17_gap_matrix.md
    target_tensor_audit.md
    target_tensor_audit.csv
    leakage_safety_audit.md
    leakage_safety_audit.csv
    parity_spotcheck_full.md
    parity_spotcheck_full.csv
    full_2024_candidate_scores.csv
    full_2024_candidate_ranking.md
    full_2024_candidate_ranking.csv
    full_2024_trackA_ranking.csv
    full_2024_trackB_ranking.csv
    locked_2025_candidate_scores.csv
    locked_2025_evaluation.md
    locked_2025_evaluation.csv
    five_fold_485d_scores.csv
    five_fold_485d_report.md
    ablation_report.md
    ablation_report.csv
    text_feature_cache_report.md
    text_feature_cache_report.csv
    runtime_benchmark_report.md
    runtime_benchmark_report.csv
    official_server_spotcheck.md
    official_server_spotcheck.csv
    package_audit_report.md
    package_audit.json
```

### Presented vs Reference Rule

Use:

```text
outputs/reports/prompt17b/presented/
```

for concise, human-readable reports that a reviewer or project lead should read.

Use:

```text
outputs/reports/prompt17b/reference/
```

for full tables, `.csv`, `.json`, machine-readable outputs, long metric dumps, and audit evidence.

Use:

```text
outputs/reports/prompt17b/progress/
```

for intermediate progress checkpoints. These are not final claims.

Detailed runtime artifacts, caches, target tensors, large JSONs, and packages must go under:

```text
.var/prompt17b/
  cache/
  target_tensors/
  generated_configs/
  search_runs/
  checkpoints/
  benchmarks/
  official_server/
  packages/
```

Only small summaries and CSVs should be copied into `outputs/reports/prompt17b/`.

---

## Required Implementation Log

Create:

```text
docs/implementation_logs/<timestamp>_prompt17b_full_horizon_validation_candidate_freeze_repair.md
```

Use exactly:

```md
# Implementation Log: prompt17b - full_horizon_validation_candidate_freeze_repair

## Created

## Summary

## Files Changed

## Prompt17 Gap Review

## Target Tensor Audit

## Leakage Safety Audit

## Parity Gate

## Full 2024 Search

## Candidate Freeze Repair

## Locked 2025 Evaluation

## Full Five-Fold Robustness

## Text Feature Cache

## Runtime / CUDA Benchmark

## Official Server Spotcheck

## Package Audit

## Tests / Checks

## Caveats

## Artifacts

## Next Steps
```

---

# Part A — Prompt17 Gap Review and Execution Inventory

## Objective

Create a precise gap matrix comparing intended Prompt17 requirements against actual Prompt17 execution.

## Tasks

1. Read Prompt17 reports and implementation logs.
2. Summarise what was completed, partial, blocked, or not done.
3. Identify all evidence that is bounded-only.
4. Identify every claim that needs to be downgraded.
5. Identify exact reports and scripts that need repair or rerun.

## Required Report

Write:

```text
outputs/reports/prompt17b/progress/progress_00_inventory_and_gap_review.md
outputs/reports/prompt17b/reference/prompt17_gap_matrix.md
```

Use this table:

| Requirement | Prompt17 Intended Standard | Prompt17 Actual Execution | Status | Prompt17b Fix |
|---|---|---|---|---|

Status values:

```text
pass
partial
fail
blocked
not_applicable
```

Required conclusions:

```text
- Prompt17 target tensor bridge: likely pass, but audit needed.
- Prompt17 search scale: partial/fail; bounded only.
- Prompt17 parity: fail/partial; only S0 macro/sector reported.
- Prompt17 official server parity: blocked.
- Prompt17 Track B freeze: requires repair because 2024-only selection discipline is unclear.
- Prompt17 final readiness verdict: likely over-optimistic.
```

---

# Part B — Target Tensor and Leakage Safety Audit

## Objective

Before running any larger search, audit the target-tensor generator and leakage-safe input builder.

## Required Checks

For each supported strategy family and track, verify:

```text
1. target tensor generated through SystemRunner, not LocalSmokeBacktester;
2. current-day open is available;
3. current-day close/high/low/change/pct_change are masked before decision;
4. same-day news uses official timestamp cutoff;
5. candidate portfolio state advances with official-style value-holding semantics;
6. no direct access to future returns, labels, or post-decision data;
7. target tensor shape is [date, candidate, asset];
8. asset universe is consistent with track;
9. fallback flags are recorded;
10. decision trace samples are written;
11. config hash and candidate metadata are recorded;
12. cache key includes date range, track, text mode, data version, and config hash.
```

## Candidate Families to Audit

At minimum:

```text
S0 macro
S0 sector
S1 macro
S1 sector
DRO-BL-RP
BSA-RP
ARMOR-OMD macro
ARMOR-OMD sector
LEEQA-Rank
KG-MoE-Lite
HGF-MPC
CEVA-KF/CIGA macro
CEVA-KF/CIGA sector
risk parity
sector rotation
OCO fallback
```

## Required Reports

Write:

```text
outputs/reports/prompt17b/progress/progress_01_target_tensor_audit.md
outputs/reports/prompt17b/reference/target_tensor_audit.md
outputs/reports/prompt17b/reference/target_tensor_audit.csv
outputs/reports/prompt17b/reference/leakage_safety_audit.md
outputs/reports/prompt17b/reference/leakage_safety_audit.csv
```

Use this table for target tensor audit:

| Strategy | Track | Config | Dates Tested | Assets | Generated? | Via SystemRunner? | Cache Key OK? | Trace Sample? | Fallback Rate | Status | Notes |
|---|---|---|---:|---:|---|---|---|---|---:|---|---|

Use this table for leakage audit:

| Strategy | Track | Current Open Used? | Current Close Masked? | Current High/Low Masked? | Current Return Masked? | News Cutoff Checked? | Future Label Access? | Status | Notes |
|---|---|---|---|---|---|---|---|---|---|

Status values:

```text
pass
partial
fail
blocked
```

## Hard Gate

Do not run the full 2024 search if any of the following fail:

```text
- S0 macro target tensor generation
- S1 macro target tensor generation
- S1 sector target tensor generation
- at least one advanced macro candidate target tensor generation
- at least one advanced sector candidate target tensor generation
- current-day close/high/low/return masking
```

---

# Part C — Broad Backtester Parity Gate

## Objective

Fix Prompt17’s weak parity coverage.

Prompt17 only showed S0 macro and S0 sector parity. Prompt17b must prove reference-vs-batched replay parity for S0, S1, and representative advanced candidates before full-horizon selection.

## Required Parity Comparisons

Compare:

```text
SystemRunner target tensor generation
→ reference_official_semantics replay
→ batched_official_semantics NumPy replay
→ Torch/CUDA replay only if available and useful
```

For a deterministic short-but-nontrivial window:

```text
at least 20 trading dates
both tracks where applicable
```

Required candidates:

```text
S0 macro
S0 sector
S1 macro
S1 sector
bsa_rp_macro_tilt25
best or default DRO-BL-RP macro
best or default risk_parity_macro
sector_rotation_graph15
s1_sector_default
s1_sector_trend60
ceva_sector_rule
leeqa_rank_top4 or leeqa_rank_rule
kg_moe_lite_rule
```

If a candidate is unavailable, record it as blocked and explain why.

## Pass Criteria

For each candidate:

```text
abs(final_value_reference - final_value_batched) <= 1e-5
metric differences within tolerance
trade/target replay sequence materially equivalent
no NaN/inf weights
weights sum within expected tolerance
cash stays nonnegative or explained by official semantics
```

## Required Reports

Write:

```text
outputs/reports/prompt17b/progress/progress_02_parity_gate.md
outputs/reports/prompt17b/reference/parity_spotcheck_full.md
outputs/reports/prompt17b/reference/parity_spotcheck_full.csv
outputs/reports/prompt17b/presented/official_parity_closure_summary.md
```

Use:

| Candidate | Track | Dates | Reference Final Value | Batched Final Value | Abs Diff | Max Daily Value Diff | Metric Diff | Weight Valid? | Status | Notes |
|---|---|---:|---:|---:|---:|---:|---:|---|---|---|

Status values:

```text
pass
minor_diff
fail
blocked
not_run
```

## Hard Gate

Do not run full-horizon search if these do not pass:

```text
S0 macro
S1 macro
S1 sector
bsa_rp_macro_tilt25 or another advanced macro candidate
sector_rotation_graph15 or another advanced sector candidate
```

If parity fails, stop after writing reports and recommend a repair prompt.

---

# Part D — Full 2024 Construction Search

## Objective

Replace Prompt17’s 20-date bounded 2024 evidence with full-horizon 2024 construction evidence.

## Search Discipline

Use **2024 only** for candidate selection and parameter freeze.

Do not use 2025 for:

```text
- choosing final Track A candidate
- choosing final Track B candidate
- selecting among candidates with similar 2024 results
- tuning parameters
- tuning text modes
- adjusting weights after seeing locked evaluation
```

2025 must remain locked evaluation only.

## Search Stages

### Stage 0 — Reproducibility Smoke

```text
Dates: 20 trading dates
Candidates: same as Prompt17 24-candidate set
Text modes: no_news, rule_based
Backend: NumPy
Purpose: confirm Prompt17b scripts reproduce Prompt17-style outputs
```

### Stage 1 — Full 2024 Baseline Search

```text
Dates: all available 2024 construction dates
Candidates: Prompt17 24-candidate set plus S0/S1/risk parity baselines
Text modes: no_news, rule_based
Backend: NumPy
Purpose: establish full-year baseline ranking
```

### Stage 2 — Full 2024 Medium Search

```text
Dates: all available 2024 construction dates
Candidates: 100–300 first; expand to 500–2000 if runtime is bounded
Candidate families:
  S0
  S1
  risk parity
  DRO-BL-RP
  BSA-RP
  ARMOR-OMD
  LEEQA-Rank
  KG-MoE-Lite
  HGF-MPC
  CEVA-KF/CIGA
  sector rotation
  OCO fallback
Text modes:
  no_news
  rule_based
Backend:
  NumPy default
  CUDA only if benchmark proves useful
Purpose: real 2024 construction ranking
```

### Stage 3 — Optional Text-Model Expansion

Only run if Stage 1–2 complete and runtime remains bounded.

```text
Text modes:
  bge_small_zh
  finbert_tone_chinese
  hybrid_rule_bge_finbert

Requirement:
  use cached features only
  do not silently download models
  do not include local model binaries in package
  compare against no_news/rule_based
```

If local HF modes are too slow, write runtime estimates and skip them.

## Required Metrics

For every candidate compute:

```text
final_value
cumulative_return
annualised_return if applicable
Sharpe
max_drawdown
turnover
trade_count
cash_utilisation
fallback_rate
NaN/invalid weight count
runtime
official_score
research_score
conservative_score
overfit_risk
dependency_risk
parity_risk
implementation_complexity
```

## Scoring

Use an explicit conservative score, e.g.:

```text
competition_score =
  0.30 * sharpe_rank_score
+ 0.20 * cumulative_return_rank_score
+ 0.20 * drawdown_rank_score
+ 0.15 * turnover_rank_score
+ 0.10 * parity_score
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
+ 0.15 * robustness_proxy
- 0.10 * overfit_risk
- 0.08 * dependency_risk
- 0.08 * parity_risk
- 0.05 * implementation_complexity
```

Also report raw metric rankings, because score engineering can hide weak returns.

## Required Reports

Write:

```text
outputs/reports/prompt17b/progress/progress_03_full_2024_search.md
outputs/reports/prompt17b/reference/full_2024_candidate_scores.csv
outputs/reports/prompt17b/reference/full_2024_candidate_ranking.md
outputs/reports/prompt17b/reference/full_2024_candidate_ranking.csv
outputs/reports/prompt17b/reference/full_2024_trackA_ranking.csv
outputs/reports/prompt17b/reference/full_2024_trackB_ranking.csv
outputs/reports/prompt17b/reference/ablation_report.md
outputs/reports/prompt17b/reference/ablation_report.csv
outputs/reports/prompt17b/presented/full_horizon_search_summary.md
```

Ranking table:

| Rank | Candidate | Track | Family | Text Mode | 2024 Return | 2024 Sharpe | Max Drawdown | Turnover | Fallback Rate | Official Score | Conservative Score | Parity Status | Promote? | Notes |
|---:|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---|---|---|

---

# Part E — Candidate Freeze Repair

## Objective

Repair the Prompt17 candidate freeze so it is selected from **2024 construction evidence only**.

## Required Candidate Selection Rule

Freeze candidates only from:

```text
full 2024 construction ranking
parity status
leakage safety status
fallback rate
implementation maturity
dependency risk
```

Do **not** use 2025 results to select candidates.

## Track A Selection

Select:

```text
Track A primary
Track A fallback
Track A ablation-only candidates
Track A rejected/deferred candidates
```

Candidate set must include at least:

```text
S1 macro
BSA-RP
DRO-BL-RP
risk parity
HGF-MPC
CEVA-KF/CIGA macro
S0 macro
```

## Track B Selection

Select:

```text
Track B primary
Track B fallback
Track B ablation-only candidates
Track B rejected/deferred candidates
```

Candidate set must include at least:

```text
S1 sector default
S1 sector trend60
sector_rotation_graph15
CEVA sector
LEEQA-Rank
KG-MoE-Lite
S0 sector
```

## Critical Track B Rule

If `s1_sector_default` or `s1_sector_trend60` beats `sector_rotation_graph15` on full 2024 construction metrics and parity status is comparable, do **not** freeze `sector_rotation_graph15` as primary just because it looked better in bounded 2025.

## Required Reports

Write:

```text
outputs/reports/prompt17b/presented/candidate_freeze_repair_report.md
```

Use exactly:

```md
# Prompt17b Candidate Freeze Repair Report

## 1. Freeze Discipline

State that candidates were selected using 2024 construction evidence only.

## 2. Track A Candidate Decision

- Primary:
- Fallback:
- Ablation only:
- Dropped:
- Evidence:
- Risks:

## 3. Track B Candidate Decision

- Primary:
- Fallback:
- Ablation only:
- Dropped:
- Evidence:
- Risks:

## 4. Comparison Against Prompt17 Freeze

| Track | Prompt17 Freeze | Prompt17b Freeze | Changed? | Reason |
|---|---|---|---|---|

## 5. 2025 Evaluation Eligibility List

List candidates selected before seeing Prompt17b 2025 results.
```

---

# Part F — Locked 2025 Evaluation

## Objective

Evaluate only the pre-frozen 2024-selected candidates on full available 2025 public A data without parameter changes.

## Candidate Set

Evaluate:

```text
Track A primary
Track A fallback
Track B primary
Track B fallback
top 3 Track A ablation candidates
top 3 Track B ablation candidates
S0 macro
S0 sector
S1 macro
S1 sector
```

## Rule

No parameter changes after viewing 2025 results.

If a 2025 result is poor, do not swap candidates unless the report explicitly states that the freeze is reopened and the result is now research-only, not locked evaluation.

## Required Reports

Write:

```text
outputs/reports/prompt17b/progress/progress_04_locked_2025_evaluation.md
outputs/reports/prompt17b/reference/locked_2025_candidate_scores.csv
outputs/reports/prompt17b/reference/locked_2025_evaluation.md
outputs/reports/prompt17b/reference/locked_2025_evaluation.csv
outputs/reports/prompt17b/presented/locked_2025_evaluation_summary.md
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

# Part G — Full Five-Fold Robustness

## Objective

Replace Prompt17’s bounded fold replay with full or materially larger five-fold robustness.

Use the Prompt16 five-fold scheme over 485 combined 2024–2025 dates if available. Label this as:

```text
research-only robustness analysis
```

because it includes 2025.

Do not use this to tune final submission parameters unless explicitly documented as research-only.

## Required Candidates

At minimum:

```text
Track A primary
Track A fallback
Track B primary
Track B fallback
S0 macro
S0 sector
S1 macro
S1 sector
best BSA-RP
best DRO-BL-RP
best CEVA macro
best CEVA sector
best LEEQA-Rank
best KG-MoE-Lite
best sector rotation
```

## Required Reports

Write:

```text
outputs/reports/prompt17b/progress/progress_05_full_five_fold.md
outputs/reports/prompt17b/reference/five_fold_485d_scores.csv
outputs/reports/prompt17b/reference/five_fold_485d_report.md
outputs/reports/prompt17b/presented/five_fold_robustness_summary.md
```

Use:

| Candidate | Track | Fold 1 Return | Fold 1 Sharpe | Fold 2 Return | Fold 2 Sharpe | Fold 3 Return | Fold 3 Sharpe | Fold 4 Return | Fold 4 Sharpe | Fold 5 Return | Fold 5 Sharpe | Mean Return | Mean Sharpe | Std Sharpe | Worst Drawdown | Robustness Verdict |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|

Robustness verdict:

```text
robust
acceptable
fragile
failed
not_run
```

If full 485-date five-fold is too slow, run the largest bounded version feasible, record the exact date coverage, and do not call it full robustness.

---

# Part H — Text Feature Cache and Local Model Evidence

## Objective

Clarify whether optional BGE/FinBERT/hybrid text modes are useful, or merely available.

## Required Checks

For each text mode:

```text
no_news
rule_based
bge_small_zh
finbert_tone_chinese
hybrid_rule_bge_finbert
```

Record:

```text
dates cached
news items
model name
local path / cache source
offline-only status
runtime
cache size
fallback rate
candidate families using it
whether it was included in 2024 ranking
whether it improved over no_news/rule_based
whether it should be package/default/ablation-only
```

## Required Reports

Write:

```text
outputs/reports/prompt17b/reference/text_feature_cache_report.md
outputs/reports/prompt17b/reference/text_feature_cache_report.csv
```

Use:

| Mode | Dates Cached | News Items | Model | Offline Only? | Runtime | Cache Size | Fallback Rate | Used in Ranking? | Improved? | Recommended Use | Notes |
|---|---:|---:|---|---|---:|---:|---:|---|---|---|---|

Recommended use values:

```text
default
candidate
ablation_only
cache_only
drop
```

Default should remain no-model/rule-based unless evidence proves otherwise.

---

# Part I — Runtime and CUDA Benchmark

## Objective

Decide whether CUDA is useful for the larger Prompt17b workload.

## Required Benchmark

Benchmark:

```text
reference loop
NumPy batched official-semantics replay
Torch CPU if available
Torch CUDA if available
```

Use a larger batch than Prompt16/Prompt17, e.g.:

```text
candidate batches: 24, 100, 300, 1000 if feasible
date windows: 20, full 2024 if feasible
```

Do not run a benchmark that risks destabilising the machine.

## Required Reports

Write:

```text
outputs/reports/prompt17b/reference/runtime_benchmark_report.md
outputs/reports/prompt17b/reference/runtime_benchmark_report.csv
```

Use:

| Backend | Device | Candidates | Dates | Runtime Seconds | Speedup vs Reference | Max Metric Diff | Recommended? | Notes |
|---|---|---:|---:|---:|---:|---:|---|---|

Recommendation values:

```text
default
optional
not_recommended
blocked
```

Do not overclaim CUDA if NumPy remains faster.

---

# Part J — Official Server Spotcheck

## Objective

Close the blocked official server parity issue if possible.

## Tasks

1. Check whether the local official server can be started.
2. If startup scripts exist, document the command used.
3. Run official-server spotchecks for selected candidates.
4. Compare official server against local reference replay.
5. If the server remains blocked, write a troubleshooting report.

## Required Candidates

At minimum:

```text
S0 macro
S1 macro
S1 sector
Track A primary
Track B primary
```

## Required Reports

Write:

```text
outputs/reports/prompt17b/progress/progress_06_official_server_spotcheck.md
outputs/reports/prompt17b/reference/official_server_spotcheck.md
outputs/reports/prompt17b/reference/official_server_spotcheck.csv
```

Use:

| Candidate | Track | Window | Official Server Value | Local Reference Value | Abs Diff | Rel Diff | Trade Match | Status | Notes |
|---|---|---|---:|---:|---:|---:|---|---|---|

Status values:

```text
pass
minor_diff
fail
blocked
not_run
```

If blocked, include:

```text
server command attempted
port checked
error message
probable cause
next action
```

Do not claim official parity if the server is unavailable.

---

# Part K — Package Audit

## Objective

Rebuild and audit a package only after the candidate freeze is repaired.

## Package Rules

Include:

```text
NLPCC_tasks/agent_platform/agents/build_agent.py
src/nlpcc/
configs/
requirements.txt or dependency files
README_SUBMISSION.md
frozen final configs
```

Include `src/tools/` only if needed for reproducibility scripts and explicitly documented. Do not silently include research helpers in the competition runtime package unless required.

Exclude:

```text
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
```

## Required Reports

Write:

```text
outputs/reports/prompt17b/progress/progress_07_package_audit.md
outputs/reports/prompt17b/reference/package_audit_report.md
outputs/reports/prompt17b/reference/package_audit.json
```

Use:

| Package Item | Included? | Required? | Status | Notes |
|---|---|---|---|---|

Status values:

```text
pass
partial
fail
excluded
```

---

# Part L — Final Recommendation and Status

## Objective

Produce a corrected readiness verdict.

Do not repeat Prompt17’s optimistic readiness unless the evidence supports it.

## Required Presented Reports

Write:

```text
outputs/reports/prompt17b/presented/executive_readiness_report.md
outputs/reports/prompt17b/presented/final_recommendation.md
outputs/reports/prompt17b/presented/final_status_report.md
outputs/reports/prompt17b/README.md
```

### `final_status_report.md`

Use exactly:

```md
# Prompt17b Final Status Report

## 1. Readiness Verdict

Choose exactly one:

- Ready for Prompt18 final packaging and system-report polish
- Not ready, but full-horizon evidence is now adequate
- Not ready; evidence or parity remains insufficient

## 2. Prompt17 Gaps Fixed

## 3. Target Tensor and Leakage Safety Status

## 4. Broad Parity Gate Status

## 5. Full 2024 Construction Search Summary

## 6. Candidate Freeze Repair

## 7. Locked 2025 Evaluation Summary

## 8. Five-Fold Robustness Summary

## 9. Text Feature Cache / Local Model Decision

## 10. Runtime and CUDA Decision

## 11. Official Server Spotcheck

## 12. Package Audit

## 13. Final Track A Candidate

## 14. Final Track B Candidate

## 15. Remaining Blockers

## 16. Recommended Next Prompt
```

### `final_recommendation.md`

Use:

```md
# Prompt17b Final Recommendation

## 1. Executive Verdict

## 2. Final Track A Recommendation

- Primary:
- Fallback:
- Evidence:
- Risks:
- Required final checks:

## 3. Final Track B Recommendation

- Primary:
- Fallback:
- Evidence:
- Risks:
- Required final checks:

## 4. Candidates for Submission Package

## 5. Candidates for System Report / Ablation Only

## 6. Candidates to Drop

## 7. 2025 Locked Evaluation Interpretation

## 8. Official Parity Interpretation

## 9. Packaging Decision

## 10. Next Prompt
```

---

## Constraints

- Do not add new strategy families.
- Do not use legacy `LocalSmokeBacktester` for final evidence.
- Do not use 2025 public A to choose final candidates or tune parameters.
- Do not claim full 2024 evidence unless all 2024 construction dates are used.
- Do not claim full five-fold robustness unless the intended five-fold date coverage is actually used.
- Do not claim official server parity if the server is unavailable.
- Do not overclaim CUDA if NumPy remains faster.
- Do not overclaim BGE/FinBERT/hybrid if they are only cache-smoked.
- Do not overclaim KG-MoE-Lite as full GNN/MoE.
- Do not overclaim CEVA-KF/CIGA as full causal discovery.
- Do not overclaim ARMOR-OMD as fully proven online learning if it remains an OMD-style MVP.
- Do not modify raw official data.
- Do not include raw official data or model binaries in packages.
- Keep large generated artifacts under `.var/prompt17b/`.
- Keep final human-readable summaries and CSV evidence under `outputs/reports/prompt17b/`.
- If a full search is too slow, write exact partial coverage and do not call it full evidence.
- If a hard gate fails, stop and write a truthful failure report rather than continuing to produce misleading rankings.

---

## Expected Final Assistant Response

After completing Prompt17b, respond with:

1. readiness verdict;
2. whether Prompt17’s unfinished issues were fixed;
3. target tensor and leakage safety status;
4. broad parity gate status;
5. full 2024 search coverage and top candidates;
6. corrected Track A freeze;
7. corrected Track B freeze;
8. locked 2025 evaluation summary;
9. five-fold robustness summary;
10. text feature/local model decision;
11. runtime/CUDA decision;
12. official server spotcheck status;
13. package audit status;
14. exact report folder paths;
15. remaining blockers;
16. next recommended prompt.
