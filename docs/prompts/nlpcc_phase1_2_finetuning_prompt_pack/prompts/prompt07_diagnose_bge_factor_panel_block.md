# Prompt07 — Diagnose BGE Asset/Sector Factor Panel Block

## Role

You are GPT-5.5 xHigh in Codex acting as a strict research-code auditor, feature-pipeline debugger, local-model cache auditor, and no-leakage factor-panel repair engineer.

This is a **diagnosis-first** prompt. Do not run another large grid. Do not tune portfolio overlays. Do not use 2025 for selection. Do not access hidden 2026. Do not download models or call online APIs.

## Objective

Find exactly why Prompt05/Prompt06 reported:

```text
BGE asset/sector fields = blocked_missing_model_factor_panel
```

Then produce a minimal repair plan and, only if safe and quick, a tiny proof-of-build sample for real BGE factors.

The goal is not to improve Sharpe in this prompt. The goal is to prove whether BGE can be materialized as a real daily asset/sector factor panel.

## Output Folder

Use:

```text
outputs/reports/next_phase_finetuning_phase12/prompt07_diagnose_bge_factor_panel_block/
```

Required subfolders:

```text
presented/
presented/run_csv/
audit/
cache/
samples/
logs/
tests/
```

The `presented/` folder must be dense and self-contained:

```text
presented/implementation_log.md
presented/essential_results.md
presented/blockers_and_decisions.md
presented/progress_dashboard.md
presented/run_csv_manifest.csv
```

## Required Inputs to Read

Read these first:

```text
outputs/reports/next_phase_finetuning_phase12/prompt03a_goal_bge_contrastive_relevance/
outputs/reports/next_phase_finetuning_phase12/prompt05_goal_alpha_mining_lexical_hybrid/
outputs/reports/next_phase_finetuning_phase12/prompt06_large_grid_alpha_transformer_sweep/
outputs/reports/next_phase_finetuning_phase12/prompt02_phase1_retrieval_calibration_fusion/retrieval/daily_topk_retrieval_features.csv
outputs/reports/next_phase_finetuning_phase12/prompt02_phase1_retrieval_calibration_fusion/features/phase1_tensor_sample_rows.csv
NLPCC_tasks/agent_platform/agents/phase12_final_agent.py
NLPCC_tasks/agent_platform/agents/prompt09_real_transformer_agent.py
src/nlpcc/news_overlay/production_tensor.py
configs/news_overlay/
```

## Stage 1 — Trace Existing BGE Evidence

Create:

```text
audit/bge_existing_artifact_trace.csv
audit/bge_expected_vs_available_columns.csv
presented/run_csv/bge_existing_artifact_trace.csv
```

Trace:

- Prompt03a BGE model path.
- Prompt03a BGE vector cache manifest.
- Prompt03a fine-tuned checkpoint.
- Prompt02 retrieval features.
- Prompt05/06 factor panel columns.
- Any expected columns such as `base_bge_relevance_score`, `fine_tuned_bge_relevance_score`, `asset_bge_score`, `sector_bge_score`.

For every artifact, record:

```text
path
exists
row_count
date_range
track_coverage
asset_or_sector_coverage
has_base_bge
has_finetuned_bge
cache_key_or_hash
why_relevant
```

## Stage 2 — Identify the Exact Block Reason

Create:

```text
audit/bge_block_reason_table.csv
presented/run_csv/bge_block_reason_table.csv
```

Classify each possible blocker as `true`, `false`, or `unknown`:

```text
model_path_missing
model_load_failed
fine_tuned_checkpoint_missing
news_embedding_cache_only_not_asset_panel
asset_sector_query_embeddings_missing
date_asset_join_missing
track_a_asset_mapping_missing
track_b_sector_mapping_missing
column_name_mismatch
cache_path_moved_or_not_found
factor_builder_did_not_load_prompt03a_cache
local_models_config_missing
runtime_budget_skipped
non_null_threshold_failed
all_values_nan_after_join
official_loader_cannot_access_factor
```

For each blocker include:

```text
evidence_file
evidence_snippet_or_column
fix_needed
safe_to_fix_now
```

## Stage 3 — Minimal BGE Factor Panel Proof

If model/cache paths exist, build a tiny proof sample only:

```text
samples/bge_factor_panel_sample_2024.csv
samples/bge_factor_panel_sample_manifest.csv
presented/run_csv/bge_factor_panel_sample_manifest.csv
```

Use a small sample:

```text
dates: first 5 valid 2024 dates + last 5 valid 2024 dates
Track A: all official Track A assets if cheap, otherwise first 5 assets
Track B: all official sectors if cheap, otherwise first 5 sectors
models: base BGE and fine-tuned BGE if both exist
```

For each date × asset/sector produce:

```text
date
track
asset_or_sector
news_count
base_bge_relevance_score
finetuned_bge_relevance_score
score_delta
embedding_source
query_source
local_files_only
network_attempted
status
blocked_reason
```

If this cannot be built, do not fake it. Emit `blocked_sample_not_buildable`.

## Stage 4 — Decide Repair Path

Create:

```text
audit/bge_repair_decision.csv
presented/run_csv/bge_repair_decision.csv
presented/blockers_and_decisions.md
```

Allowed decisions:

```text
repair_simple_column_mapping
repair_cache_loader
repair_query_embedding_builder
repair_date_asset_join
requires_new_factor_builder
blocked_missing_model
blocked_missing_mapping
blocked_runtime_or_memory
```

For each decision include:

```text
expected_effort
risk
files_to_modify
tests_needed
whether_prompt06_should_be_rerun
```

## Stage 5 — Tests

Run only cheap tests:

```bash
rtk python -m pytest tests/test_nlpcc/test_news_overlay -q
```

If you created a small sample builder, add/run a tiny artifact validation script.

Do not run a large grid, compileall, or pip check.

## Final Response Format

Use exactly:

```text
Prompt07 status:
  <pass/partial/fail/blocked>

BGE block diagnosis:
  primary reason:
    <one sentence>
  secondary reasons:
    <list>

Existing BGE artifacts:
  base model path found: <yes/no>
  fine-tuned checkpoint found: <yes/no>
  vector cache found: <yes/no>
  asset/sector factor panel found: <yes/no>

Minimal sample:
  status: <built/partial/blocked>
  rows: <n>
  csv: <path>

Repair decision:
  <repair_simple_column_mapping / repair_cache_loader / repair_query_embedding_builder / repair_date_asset_join / requires_new_factor_builder / blocked>

Should rerun Prompt06 after repair?
  <yes/no>
  reason: <short>

Tests:
  news_overlay pytest: <pass/fail/not_run>

Hidden 2026 used?
  no

2025 tuning used?
  no

Best next action:
  <one action>
```
