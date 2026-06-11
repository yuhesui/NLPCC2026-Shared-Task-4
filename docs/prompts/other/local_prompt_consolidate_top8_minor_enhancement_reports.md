# Local Prompt — Consolidate Top-8 Minor-Enhancement Reports

## Role

You are a local repo-analysis agent, CSV consolidation engineer, and research-output auditor.

You are working inside the repository. Do not use the internet. Do not call online APIs. Do not rerun model inference or backtests.

Your task is to analyse the existing reports under:

```text
outputs/reports/news_overlay/top8_minor_enhancement
```

and create a clean `presented/` folder containing the most useful consolidated CSV outputs for human review.

This is **analysis and report consolidation only**.

---

## Goal

Create:

```text
outputs/reports/news_overlay/top8_minor_enhancement/presented/
```

and place there the most useful merged / cleaned / ranked CSV files.

Markdown is optional. CSV is preferred. Do not create long extra `.md` reports unless a very short `README.md` is necessary to explain files.

---

## What to Read

Recursively scan:

```text
outputs/reports/news_overlay/top8_minor_enhancement/
```

Especially inspect likely subfolders:

```text
concurrent/track_a/
concurrent/track_b_parity/
concurrent/track_b_research/
```

Read all `.csv` and concise `.md` status files.

Do not assume exact filenames. Discover files programmatically.

---

## Required Behaviour

### 1. Inventory all files

Create:

```text
presented/file_inventory.csv
```

Columns:

```text
path
relative_path
file_type
size_bytes
rows
columns
mtime
category
notes
```

Categories should include:

```text
track_a
track_b_parity
track_b_research
shared
implementation_log
unknown
```

---

### 2. Merge Stage 1 tune matrices

Find and merge all Stage 1 2024 tune matrix CSVs.

Create:

```text
presented/merged_stage1_2024_tune_matrix.csv
```

Expected source patterns may include:

```text
*stage1*2024*tune*matrix*.csv
```

Add columns if missing:

```text
source_file
branch
track_group
candidate_family
candidate_run_id
variant
method_stack
```

Do not drop rows. If schemas differ, union columns and fill missing values.

---

### 3. Merge Stage 2 frozen 2025 results

Find and merge all Stage 2 frozen 2025 result CSVs.

Create:

```text
presented/merged_stage2_2025_frozen_results.csv
```

Expected source patterns may include:

```text
*stage2*2025*frozen*results*.csv
```

Again, union columns and preserve source file.

---

### 4. Merge ablation evidence

Find and merge all ablation evidence CSVs.

Create:

```text
presented/merged_ablation_evidence.csv
```

Expected source patterns:

```text
*ablation*evidence*.csv
```

Add source/branch columns.

---

### 5. Merge freeze decisions

Find and merge freeze-decision files.

Create:

```text
presented/merged_freeze_decisions.csv
```

Sources may be CSV or Markdown.

If Markdown freeze files are easier to parse manually, create a row-level extraction with best effort and include:

```text
source_file
track
candidate
variant
method_stack
status
reason
raw_line
```

---

### 6. Create top candidate summary

Create:

```text
presented/top_candidate_summary.csv
```

This should contain the most important selected/frozen candidates across all branches.

Try to include:

```text
track
group
candidate
variant
method_stack
enhancement
status
2024_return
2024_sharpe
2024_selection_score
2025_return
2025_sharpe
2025_max_drawdown
2025_turnover
delta_vs_g00
delta_vs_g01
promotion_status
recommended_next_use
source_files
```

Expected groups:

```text
track_a_research
track_b_parity
track_b_research_blocked
```

If a metric is unavailable, leave blank rather than inventing.

---

### 7. Create candidate ranking views

Create:

```text
presented/ranking_by_2024_selection_score.csv
presented/ranking_by_2025_sharpe.csv
presented/ranking_by_2025_return.csv
presented/ranking_by_status_priority.csv
```

Sort descending for performance metrics.

For `ranking_by_status_priority.csv`, use this priority order:

```text
1. primary_parity_review_candidate
2. parity_review_backup
3. parity_review_candidate
4. frozen_2025_supported
5. research_only
6. research_continue
7. blocked
8. rejected
9. unknown
```

---

### 8. Create control comparison table

If available from deltas or control-check files, create:

```text
presented/control_comparison_summary.csv
```

Include:

```text
candidate
track
variant
comparison_control
delta_return
delta_sharpe
delta_max_drawdown
delta_turnover
verdict
source_file
```

Read files such as:

```text
*delta*check*.csv
*control*delta*.csv
*candidate_vs_control*.csv
```

---

### 9. Create blocker / risk table

Create:

```text
presented/blocker_risk_summary.csv
```

Extract from final status Markdown and audit CSVs where possible.

Columns:

```text
candidate
track
branch
blocker
severity
evidence
next_fix
source_file
```

Make sure to include:

```text
- official-server parity not run;
- Track A research-only;
- G21B/G12B material differences unresolved;
- preserved-control delta failures;
- missing Stage 0 artifacts if applicable;
- missing tuner capability audit if applicable;
- no final package dry-run if applicable.
```

Do not invent blockers not supported by available files.

---

### 10. Optional short README

Create only a concise file:

```text
presented/README.md
```

Limit to:

```text
- what was scanned;
- list of generated CSVs;
- any missing inputs;
- main caution: these are report-consolidation outputs, not new backtest results.
```

No long narrative report is needed.

---

## Validation Checks

After writing outputs:

1. Confirm `presented/` exists.
2. Confirm every generated CSV is readable by pandas.
3. Confirm merged CSV row counts equal the sum of source rows where applicable.
4. Confirm no source files were modified.
5. Confirm no model inference or backtests were run.
6. Confirm official runtime folders were not modified.

Write validation results to:

```text
presented/consolidation_validation.csv
```

Columns:

```text
check
result
details
```

---

## Do Not Do

```text
- Do not run model inference.
- Do not run backtests.
- Do not tune anything.
- Do not change candidate statuses unless files support it.
- Do not modify official runtime.
- Do not delete source reports.
- Do not create long Markdown reports.
- Do not invent missing metrics.
```

---

## Final Response Format

```text
Consolidation status:
  <pass/partial/fail>

Scanned folder:
  outputs/reports/news_overlay/top8_minor_enhancement

Presented folder:
  outputs/reports/news_overlay/top8_minor_enhancement/presented

Generated CSVs:
  <list>

Rows merged:
  stage1_2024=<n>
  stage2_2025=<n>
  ablation=<n>
  freeze_decisions=<n>

Top candidates extracted:
  <n>

Main missing inputs:
  <list or none>

Validation:
  <pass/partial/fail>

Next useful action:
  <one sentence>
```
