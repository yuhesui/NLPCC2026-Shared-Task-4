# Prompt07b — Repair BGE Factor Cache Loader and Build Full Asset/Sector Panel

## Role

You are GPT-5.5 Extended Thinking acting as a senior research-code auditor, retrieval engineer, quant factor engineer, and repo-safety reviewer.

This is a **repair-and-validate prompt**, not a new alpha-mining or optimization prompt.

## Objective

Repair the Prompt05/Prompt06 BGE factor-panel blocker by materializing the existing Prompt03a BGE cached embeddings into a full daily `date × track × asset_or_sector` factor panel.

Do **not** run a large grid.  
Do **not** promote any production agent.  
Do **not** modify `phase12_final` production behavior.  
Do **not** fabricate BGE rows.  
Do **not** use hidden 2026.  
Do **not** use 2025 for tuning.

## Source of Truth

Read recent project artifacts first:

```text
outputs/reports/next_phase_finetuning_phase12/prompt03a_goal_bge_contrastive_relevance/
outputs/reports/next_phase_finetuning_phase12/prompt05_goal_alpha_mining_lexical_hybrid/
outputs/reports/next_phase_finetuning_phase12/prompt06_large_grid_alpha_transformer_sweep/
outputs/reports/next_phase_finetuning_phase12/prompt07_diagnose_bge_factor_panel_block/
outputs/reports/next_phase_finetuning_phase12/prompt04_goal_integrate_optimize_official_clean/
```

Also read:

```text
AGENTS.md
README.md
rtk-optimized.md
configs/news_overlay/approved_hf_models.yaml
NLPCC_tasks/agent_platform/agents/phase12_final_agent.py
NLPCC_tasks/agent_platform/agents/prompt09_real_transformer_agent.py
src/nlpcc/news_overlay/production_tensor.py
```

Use `rtk python` and `rtk git`.

## Known Diagnosis From Prompt07

Prompt07 found:

```text
Base BGE model exists.
Fine-tuned BGE checkpoint exists.
Prompt03a BGE vector cache exists.
Asset/sector query embeddings exist.
Track A asset mapping exists.
Track B sector mapping exists.
Prompt05/06 failed because they did not load/materialize Prompt03a cached BGE vectors into daily factor-panel columns.
A tiny 270-row sample was built successfully from real cached embeddings.
```

Therefore, the expected repair is:

```text
load Prompt03a base/fine-tuned .npz caches
compute or load news-query similarity scores
aggregate visible news by decision date and asset/sector query
write standard BGE factor columns
join into factor panel by date, track, asset_or_sector
validate non-null coverage
```

## Output Root

Write all outputs under:

```text
outputs/reports/next_phase_finetuning_phase12/prompt07b_repair_bge_factor_cache_loader/
```

Required subfolders:

```text
audit/
cache/
factors/
diagnostics/
samples/
tests/
presented/
presented/run_csv/
logs/
```

## Required Work

### 1. Intake and artifact trace

Create:

```text
audit/input_artifact_manifest.csv
audit/bge_cache_trace.csv
audit/bge_query_key_trace.csv
audit/expected_panel_schema.csv
```

For each artifact, record:

```text
path
exists
rows_or_shape
columns_or_keys
hash_if_file
status
notes
```

### 2. Build full BGE factor panel

Build a full 2024 panel with these required columns:

```text
date
track
asset_or_sector
base_bge_relevance_score
fine_tuned_bge_relevance_score
bge_delta_score
base_bge_top_news_count
fine_tuned_bge_top_news_count
bge_visible_news_count
source_cache
hidden_2026_used
uses_2025_for_tuning
proxy_or_fake_rows_used
```

Track A should cover all available macro assets from Prompt03a query keys.
Track B should cover all available sector queries from Prompt03a query keys.

Use only visible 2024 news and Prompt03a cached vectors. If a date has no visible news, write explicit zero/NaN policy in manifest. Do not silently drop dates.

### 3. Coverage validation

Create:

```text
diagnostics/bge_factor_coverage_by_track.csv
diagnostics/bge_factor_non_null_summary.csv
diagnostics/bge_factor_date_gap_report.csv
diagnostics/bge_factor_asset_sector_gap_report.csv
```

Required checks:

```text
Track A non-null base BGE rows >= 95% of expected rows
Track A non-null fine-tuned BGE rows >= 95% of expected rows
Track B non-null base BGE rows >= 95% of expected rows
Track B non-null fine-tuned BGE rows >= 95% of expected rows
no hidden 2026
no 2025 tuning
no fake/proxy rows
```

If any check fails, stop and write blockers. Do not run IC/grid.

### 4. Small sanity diagnostics only

If coverage passes, run small diagnostics only:

```text
diagnostics/bge_factor_ic_sanity_2024.csv
diagnostics/bge_factor_shuffle_sanity_2024.csv
diagnostics/base_vs_finetuned_bge_panel_comparison.csv
diagnostics/bge_vs_prompt03a_retrieval_consistency.csv
```

Do not optimize portfolio overlays. Do not select final candidates.

The sanity diagnostics should answer:

```text
Is base BGE non-null?
Is fine-tuned BGE non-null?
Are base and fine-tuned BGE meaningfully different?
Does fine-tuned BGE improve over base BGE in panel-level IC or rank consistency?
Does active BGE beat date-shuffled BGE in a simple diagnostic?
Does the panel match Prompt03a retrieval evidence directionally?
```

### 5. Tests

Run:

```text
rtk python -m pytest tests/test_nlpcc/test_news_overlay -q
```

Also write a targeted artifact validation script that checks output schema, non-null thresholds, leakage flags, and row counts.

Create:

```text
tests/test_results_summary_prompt07b.csv
tests/prompt07b_artifact_validation.csv
```

### 6. Dense presented monitor

Create:

```text
presented/progress_dashboard.md
presented/essential_results.md
presented/implementation_log.md
presented/blockers_and_decisions.md
presented/run_csv_manifest.csv
```

Keep `presented/` concise but complete.

## Stop Conditions

Stop immediately and report blockers if:

```text
Prompt03a .npz cache cannot be loaded
query keys are missing or malformed
expected Track A/B mappings cannot be reconstructed
full factor panel has <95% non-null coverage
any hidden 2026 data is touched
2025 is used for tuning
fake/proxy rows would be needed
```

## Final Response Format

End with exactly:

```text
Prompt07b status: pass / partial / blocked / fail
BGE full panel built: yes/no
Rows written:
Track A coverage:
Track B coverage:
Base vs fine-tuned difference:
Sanity IC verdict:
Shuffle sanity verdict:
Tests:
Should Prompt06 be rerun now: yes/no
Reason:
Next best action:
```

## Promotion Rule

Prompt07b cannot promote anything. Even if the panel looks good, the only allowed next step is a rerun of Prompt06 diagnostics/grid using the repaired panel.
