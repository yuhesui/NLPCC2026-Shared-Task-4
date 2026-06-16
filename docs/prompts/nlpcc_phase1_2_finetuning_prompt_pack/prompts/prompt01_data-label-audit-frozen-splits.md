# prompt01_data-label-audit-frozen-splits.md

## Model Setting

Use **GPT-5.5 xHigh** in Codex.

## Role

You are GPT-5.5 xHigh acting as:

```text
senior leakage-safe data engineer
Chinese financial NLP label designer
quant validation engineer
model-provenance auditor
single implementation-log writer
```

## Objective

Build the leakage-safe data and label foundation for Phase 1–2 experiments.

This prompt must not train models. It must create auditable datasets, split manifests, label-source manifests, and label-quality diagnostics for:

```text
A2_real / G11A:
  macro news relevance
  macro aspect/tone labels
  risk-regime confidence labels
  overlay calibration labels

B2_real / G15B:
  sector-news relevance labels
  event-label weak supervision labels
  sector impact / Rank-IC labels
  pairwise news-sector ranking labels
```

## Output Folder

```text
outputs/reports/focused_candidate_optimisation/next_phase_finetuning_phase12/prompt01_data_label_audit_frozen_splits/
```

Required subfolders:

```text
presented/
presented/run_csv/
reference/
logs/
labels/
splits/
audits/
quality/
tests/
```

## Presented Folder Rule

Create exactly these dense monitoring files:

```text
presented/implementation_log.md
presented/progress_dashboard.md
presented/essential_results.md
presented/blockers_and_decisions.md
presented/run_csv_manifest.csv
presented/run_csv/
```

`presented/essential_results.md` must merge:

```text
split summary
label summary
label quality summary
leakage audit
blockers
go/no-go decision for Prompt02/03/04
```

## Hard Rules

```text
Use rtk, rtk python, rtk git.
No hidden 2026.
No online API.
No model download.
No training.
No retuning.
No use of 2025 for threshold/parameter selection.
No hidden label construction from 2026.
No post-cutoff same-day price or close/high/low in decision-time features.
No stale summary reuse.
```

## Required Inputs to Read

```text
Prompt11 outputs and fine_tuning_plan
A2/B2 configs and source maps
news data loaders
price data loaders
official DataLoader semantics
tests related to news overlay and leakage
local model cache manifests if present
```

## Stage 1 — Split Manifest

Create strict split files:

```text
splits/frozen_split_manifest.csv
splits/date_cutoff_policy.md
splits/train_dev_eval_protocol.yaml
```

Required split policy:

```text
2024:
  training/development only
  may use walk-forward folds

2025:
  frozen public evaluation only
  cannot be used for parameter selection

2026 hidden:
  never accessed
```

If the repo contains earlier Type-B/C/D splits, record compatibility but do not silently inherit them unless they are leakage-safe.

## Stage 2 — News/price feature availability audit

Create:

```text
audits/news_price_availability_audit.csv
audits/cutoff_semantics_audit.csv
audits/candidate_feature_dependency_audit.csv
```

Must check:

```text
daily Top-20 news loaded before cutoff
title/body/summary fields
same-day close/high/low hidden before decision
model features generated from visible data only
A2/B2 tensor features align by date
no post-2024 model/label corpus accidentally used for training
```

## Stage 3 — Label datasets

Create these label files where possible:

```text
labels/news_to_asset_relevance_2024.csv
labels/news_to_sector_relevance_2024.csv
labels/event_label_weak_supervision_2024.csv
labels/macro_aspect_labels_2024.csv
labels/forward_return_bucket_labels_2024.csv
labels/risk_adjusted_return_labels_2024.csv
labels/pairwise_news_sector_preferences_2024.csv
labels/calibration_targets_2024.csv
labels/cluster_pseudo_labels_2024.csv
```

Each label row must include:

```text
label_id
date
news_id
track
candidate_scope
asset_or_sector
text_hash
label_type
label_value
label_source
label_confidence
uses_forward_return
forward_window
feature_cutoff_safe
target_available_after_decision
leakage_risk
split
notes
```

Allowed label sources:

```text
deterministic event taxonomy
entity/sector mapping
2024-only forward returns as training labels
2024-only Rank-IC and hit-rate labels
2024-only cluster labels
manual/static pre-2025 taxonomy files if already in repo
```

Do not create labels using:

```text
2025 tuning
hidden 2026
future news beyond date
post-cutoff same-day close/high/low as features
online LLM judgments
```

## Stage 4 — Positive/negative and hard-negative construction

Create:

```text
labels/positive_negative_construction_manifest.csv
labels/hard_negative_manifest_2024.csv
```

Hard negatives for contrastive BGE:

```text
same-date wrong sector
same-event-family wrong sector
high lexical overlap but wrong sector
date-shuffled sector
sector with opposite forward response in 2024
```

Flag possible false negatives.

## Stage 5 — Label quality diagnostics

Create:

```text
quality/label_quality_summary.csv
quality/label_coverage_by_track.csv
quality/label_coverage_by_event_class.csv
quality/label_noise_risk_table.csv
quality/class_balance_table.csv
quality/go_no_go_table.csv
```

Go/no-go decisions:

```text
Prompt02 can proceed if:
  split manifest exists
  feature availability audit passes or caveats are explicit

Prompt03 can proceed if:
  news-sector relevance labels have enough positives and negatives
  hard-negative set exists
  false-negative risk is documented

Prompt04 can proceed if:
  event/aspect labels have enough coverage and noise is acceptable
```

## Stage 6 — Tests and smoke checks

Run cheap checks:

```bash
rtk python -m pytest tests/test_nlpcc/test_news_overlay -q
```

If there are label validation tests, run them. If not, create lightweight validation scripts under `src/tools/` or `scripts/` only if repo conventions allow.

Create:

```text
tests/test_results_summary_prompt01.csv
presented/run_csv/test_results_summary_prompt01.csv
logs/prompt01_tests.log
```

## Required CSVs copied to presented/run_csv

```text
frozen_split_manifest.csv
label_quality_summary.csv
label_coverage_by_track.csv
go_no_go_table.csv
test_results_summary_prompt01.csv
```

## Implementation Log Sections

```text
A. Summary
B. Files Read
C. Files Created
D. Commands Run
E. Split Protocol
F. News/Price Cutoff Audit
G. Label Dataset Construction
H. Positive/Negative Construction
I. Label Quality Diagnostics
J. Go/No-Go Decisions
K. Tests
L. Hidden 2026 / Leakage Check
M. Caveats
N. Next Prompt
```

## Final Response Format

```text
Prompt01 status:
  <pass/partial/fail/blocked>

Implementation log:
  <path>
  count: <1/other>

Split manifest:
  <path>

Label datasets:
  created: <n>
  key files:
    <list>

Leakage audit:
  status: <pass/partial/fail>
  hidden 2026 used: no
  2025 used for tuning: no

Go/no-go:
  Prompt02: <go/no_go/conditional>
  Prompt03: <go/no_go/conditional>
  Prompt04: <go/no_go/conditional>

Presented monitor:
  <path>

Main blockers:
  <list>

Best next action:
  <one action>
```
