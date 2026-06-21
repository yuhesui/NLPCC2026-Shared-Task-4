# Prompt06 — Goal Mode: Larger Alpha-Mining Grid + Transformer Architecture Sweep, 2024-Fit / Frozen-2025 Test

## Role

You are GPT-5.5 xHigh in Codex Goal Mode acting as:

```text
senior quantitative alpha researcher
Chinese financial NLP engineer
transformer-news feature auditor
official-agent integration engineer
backtest reliability auditor
single-log evidence writer
```

This is a **full overnight research + validation goal**. Continue from the current repo fork after Prompt05.

## Goal

Run a larger, stricter alpha-mining and transformer-architecture experiment using more available historical feature data, while preserving the competition split:

```text
FIT / SELECT / OPTIMISE: 2024 only
FROZEN PUBLIC TEST: 2025 only
HIDDEN 2026: never access
```

Do not promote any branch unless it beats the current phase12 path under frozen 2025 and active-vs-zeroed-vs-multi-shuffled ablation.

## Phase Root

Use:

```text
outputs/reports/next_phase_finetuning_phase12/prompt06_large_grid_alpha_transformer_sweep/
```

Required subfolders:

```text
presented/
presented/run_csv/
reference/
logs/
cache/
factors/
transformers/
optimiser/
ablations/
server_run/
repo_cleanup/
tests/
configs/
```

The `presented/` folder must be dense and monitorable:

```text
presented/implementation_log.md
presented/progress_dashboard.md
presented/essential_results.md
presented/blockers_and_decisions.md
presented/final_prompt06_report.md
presented/run_csv_manifest.csv
presented/run_csv/*.csv
```

## Hard Rules

```text
Use rtk, rtk python, rtk git.
No hidden 2026.
No 2025 tuning, threshold selection, epoch selection, model choice, or grid promotion.
No online API/model inference.
No model download unless already locally cached and approved.
No fake/proxy/fixed target replay.
No branch promotion without frozen 2025 and ablation proof.
A0/B0 are reference-only unless report explicitly says policy changed.
Current phase12 remains production baseline unless new branch clears all gates.
```

## Required Inputs to Read

Read before coding:

```text
outputs/reports/next_phase_finetuning_phase12/prompt01_data_label_audit_frozen_splits/
outputs/reports/next_phase_finetuning_phase12/prompt02_phase1_retrieval_calibration_fusion/
outputs/reports/next_phase_finetuning_phase12/prompt03a_goal_bge_contrastive_relevance/
outputs/reports/next_phase_finetuning_phase12/prompt03b_goal_event_aspect_lora/
outputs/reports/next_phase_finetuning_phase12/prompt04_goal_integrate_optimize_official_clean/
outputs/reports/next_phase_finetuning_phase12/prompt05_goal_alpha_mining_lexical_hybrid/
outputs/reports/focused_candidate_optimisation/prompt11_final_news_candidate_cleanup_official_run/
NLPCC_tasks/agent_platform/agents/build_agent.py
NLPCC_tasks/agent_platform/agents/phase12_final_agent.py
NLPCC_tasks/agent_platform/agents/prompt09_real_transformer_agent.py
src/nlpcc/news_overlay/production_tensor.py
NLPCC_tasks/server_platform/app/core/data_loader.py
```

## Stage 0 — Package / Feature Availability Audit

Audit optional packages and use them only if already installed:

```text
qlib
alphalens
vectorbt
sklearn
scipy
statsmodels
pandas-ta or ta
optuna
faiss
transformers
torch
```

If packages are missing, do not install unless local policy allows. Use minimal pandas/numpy/sklearn fallback and record the fallback.

Outputs:

```text
reference/package_availability_audit.csv
reference/input_artifact_manifest.csv
presented/run_csv/package_availability_audit.csv
```

## Stage 1 — Rebuild Larger Factor Panel with More Data

Rebuild the full factor panel rather than relying only on Prompt05 incomplete fields.

Required factor families:

```text
F0 current phase12 baseline features
F1 lexical/entity/BM25 relevance
F2 base BGE asset/sector relevance
F3 fine-tuned BGE asset/sector relevance
F4 lexical + base BGE hybrid
F5 lexical + fine-tuned BGE hybrid
F6 FinBERT tone/confidence/entropy/intensity
F7 FinBERT x relevance interactions
F8 event persistence and event breadth
F9 event novelty and repetition decay
F10 price momentum/reversal/volatility/drawdown
F11 macro regime factors for Track A
F12 sector evidence-count/rank-IC stability for Track B
F13 BGE-vs-FinBERT disagreement factors
F14 cluster support / historical analogue factors
```

Track-specific expectations:

```text
Track A: macro-regime/news persistence/cross-asset risk factors.
Track B: sector relevance/event persistence/evidence breadth/sector graph-like exposure factors.
```

Outputs:

```text
factors/factor_catalog.csv
factors/factor_daily_panel.csv
factors/factor_build_manifest.csv
cache/bge_asset_sector_factor_cache_manifest.csv
cache/finbert_asset_sector_factor_cache_manifest.csv
presented/run_csv/factor_catalog.csv
presented/run_csv/factor_build_manifest.csv
```

If BGE or FinBERT asset/sector fields cannot be materialized, mark branch status `blocked_missing_model_factor_panel`; do not fabricate rows.

## Stage 2 — Transformer Architecture Sweep

Test available transformer architectures/configs as factor families, not just one BGE path.

Minimum architecture variants:

```text
T0 lexical/entity only
T1 base BGE only
T2 fine-tuned BGE only
T3 lexical + base BGE
T4 lexical + fine-tuned BGE
T5 FinBERT tone/confidence only
T6 lexical + FinBERT
T7 BGE + FinBERT
T8 lexical + fine-tuned BGE + FinBERT
T9 event persistence + lexical/BGE
T10 Track-A macro transformer tensor composite
T11 Track-B sector event tensor composite
```

Optional if cached locally:

```text
T12 local cross-encoder/reranker top-k only
T13 local SLM/offline label-audit/rerank output only
```

Outputs:

```text
transformers/transformer_architecture_manifest.csv
transformers/news_model_family_comparison_2024.csv
transformers/finbert_vs_bge_error_analysis.csv
transformers/architecture_ablation_2024.csv
presented/run_csv/transformer_architecture_manifest.csv
presented/run_csv/news_model_family_comparison_2024.csv
```

## Stage 3 — 2024 Alpha Diagnostics

Run factor diagnostics on 2024 only.

Required diagnostics:

```text
rank IC by factor/track/window
quantile spread
hit rate
turnover proxy
factor correlation clustering
active vs zeroed
active vs date-shuffled, 5+ seeds
block-shuffled by week/month
price-only vs news-only vs combined decomposition
```

Outputs:

```text
diagnostics/factor_ic_table_2024.csv
diagnostics/factor_quantile_spread_2024.csv
diagnostics/factor_correlation_cluster_2024.csv
diagnostics/factor_ablation_2024.csv
diagnostics/news_only_vs_price_only_2024.csv
presented/run_csv/factor_ic_table_2024.csv
presented/run_csv/news_only_vs_price_only_2024.csv
```

## Stage 4 — Larger Grid Search on 2024 Only

Run larger bounded grid or Optuna search, separately for Track A and Track B.

Track A search space:

```text
macro_regime_weight
lexical_weight
bge_weight
finbert_weight
event_persistence_weight
price_momentum_weight
risk_off_shrink
confidence_gate
overlay_cap
turnover_cap
drawdown_guard
recency_half_life
```

Track B search space:

```text
sector_relevance_weight
event_persistence_weight
evidence_breadth_weight
lexical_weight
bge_weight
finbert_weight
rank_ic_stability_shrink
sector_concentration_cap
confidence_gate
overlay_cap
turnover_cap
recency_half_life
```

Budget:

```text
minimum: 300 trials per track
preferred overnight: 1000+ trials per track if fast
checkpoint every 100 trials
```

Objective:

```text
score = Sharpe + return_reward - drawdown_penalty - turnover_penalty - instability_penalty - shuffled_similarity_penalty
```

Outputs:

```text
optimiser/large_grid_trials_2024.csv
optimiser/large_grid_best_configs.csv
optimiser/param_importance_2024.csv
configs/A2_prompt06_best.yaml
configs/B2_prompt06_best.yaml
presented/run_csv/large_grid_best_configs.csv
```

## Stage 5 — Frozen 2025 Evaluation

Freeze all selected configs from 2024. Run frozen 2025 only once per selected branch.

Compare:

```text
A0 reference
A2 current phase12
A2 prompt06 best
B0 reference
B2 current phase12
B2 prompt06 best
```

Outputs:

```text
reference/frozen_2025_prompt06_results.csv
reference/frozen_2025_prompt06_metric_comparison.csv
presented/run_csv/frozen_2025_prompt06_results.csv
presented/run_csv/frozen_2025_prompt06_metric_comparison.csv
```

## Stage 6 — Frozen 2025 Ablation and Promotion Gate

For A2_prompt06_best and B2_prompt06_best run:

```text
active
zeroed_news
5+ date_shuffled seeds
block_shuffled_week
block_shuffled_month
lexical_disabled
bge_disabled
finbert_disabled
price_only
news_only
branch_disabled
```

Promotion gate:

```text
active beats current phase12 by Sharpe or materially improves drawdown/turnover
active beats zeroed
active beats mean shuffled
active beats block-shuffled
official/local platform path works or loader plan is exact
no hidden 2026
no 2025 tuning
```

Outputs:

```text
ablations/frozen_2025_prompt06_ablation.csv
reference/prompt06_promotion_decision.csv
presented/run_csv/frozen_2025_prompt06_ablation.csv
presented/run_csv/prompt06_promotion_decision.csv
```

If gates fail, keep branch report-only.

## Stage 7 — Official Path / Agent Port Only If Gates Clear

If and only if a branch clears gates, port it to actual agent path. Otherwise, do not modify production candidate path.

Potential paths:

```text
NLPCC_tasks/agent_platform/agents/phase12_final_agent.py
NLPCC_tasks/agent_platform/agents/phase12_final_candidate_config.json
```

Outputs:

```text
server_run/official_server_or_http_prompt06_results.csv
repo_cleanup/source_config_hash_manifest.csv
repo_cleanup/repo_cleanup_manifest.csv
presented/run_csv/source_config_hash_manifest.csv
```

## Stage 8 — Tests and Package Checks

Run:

```bash
rtk python -m pytest tests/test_nlpcc/test_news_overlay -q
rtk python -m pytest tests/test_nlpcc -q
rtk python -m pytest tests -q
rtk python -m compileall src NLPCC_tasks tests
rtk python -m pip check
```

If compileall/pip check fail from known environment issues, mark `environment_blocked`, not candidate failure.

Outputs:

```text
tests/test_results_summary_prompt06.csv
presented/run_csv/test_results_summary_prompt06.csv
logs/prompt06_tests.log
logs/prompt06_compileall.log
logs/prompt06_pip_check.log
```

## Stage 9 — Final Report

Create:

```text
presented/final_prompt06_report.md
```

Required sections:

```text
1. Executive decision
2. What extra data/features were added
3. Track A architecture and results
4. Track B architecture and results
5. BGE vs FinBERT vs lexical comparison
6. Transformer architecture sweep results
7. 2024 optimization evidence
8. Frozen 2025 results
9. Ablation and shuffled-news proof
10. Promotion decision
11. Repo/package/test status
12. Claims allowed
13. Claims not allowed
14. Best next action
```

## Final Response Format

Use exactly:

```text
Prompt06 status:
  <pass/partial/fail/blocked>

Factor panel:
  rows: <n>
  BGE asset/sector fields: <complete/partial/blocked>
  FinBERT asset/sector fields: <complete/partial/blocked>

Transformer architecture sweep:
  status: <complete/partial/blocked>
  best Track A architecture: <name>
  best Track B architecture: <name>

2024 large grid:
  Track A trials: <n>
  Track B trials: <n>
  best configs: <path>

Frozen 2025:
  status: <complete/partial/blocked>
  A current phase12 Sharpe: <x>
  A prompt06 Sharpe: <x>
  B current phase12 Sharpe: <x>
  B prompt06 Sharpe: <x>

Promotion decision:
  Track A: <promote/report_only/blocked>
  Track B: <promote/report_only/blocked>

Official path:
  status: <unchanged/ported/blocked>
  strict HTTP: <pass/fail/blocked/not_run>

Tests:
  news_overlay: <pass/fail/not_run>
  tests_nlpcc: <pass/fail/not_run>
  full_tests: <pass/fail/not_run>
  compileall: <pass/fail/environment_blocked/not_run>
  pip_check: <pass/fail/environment_blocked/not_run>

Hidden 2026 used?
  no

2025 tuning used?
  no

Best next action:
  <one action>
```
