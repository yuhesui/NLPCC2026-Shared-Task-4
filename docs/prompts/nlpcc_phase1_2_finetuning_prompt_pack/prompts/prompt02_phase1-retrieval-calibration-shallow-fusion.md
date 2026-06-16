# prompt02_phase1-retrieval-calibration-shallow-fusion.md

## Model Setting

Use **GPT-5.5 High**. Use **GPT-5.5 xHigh** if Prompt01 found messy labels or source-path ambiguity.

## Role

You are GPT-5.5 acting as:

```text
senior retrieval-feature engineer
financial NLP calibration engineer
portfolio overlay fusion engineer
official-run validation engineer
single implementation-log writer
```

## Objective

Execute Phase 1: no-training retrieval, clustering, calibration, and shallow fusion baselines for A2_real and B2_real.

This prompt must establish strong baselines before true fine-tuning.

## Output Folder

```text
outputs/reports/focused_candidate_optimisation/next_phase_finetuning_phase12/prompt02_phase1_retrieval_calibration_fusion/
```

Required subfolders:

```text
presented/
presented/run_csv/
reference/
logs/
features/
retrieval/
clustering/
calibration/
fusion/
configs/
ablations/
tests/
```

## Presented Folder Rule

The `presented/` folder must be monitorable and dense.

Create:

```text
presented/implementation_log.md
presented/progress_dashboard.md
presented/essential_results.md
presented/blockers_and_decisions.md
presented/run_csv_manifest.csv
presented/run_csv/
```

Do not create many small Markdown summaries under `presented/`; merge into `essential_results.md`.

## Hard Rules

```text
Use rtk, rtk python, rtk git.
No hidden 2026.
No online API.
No model download.
No training of transformer weights.
No LoRA.
No DAPT/TAPT.
No DPO/RLHF.
No 2025 tuning.
No broad candidate search.
No proxy/fake news in production candidate path.
No fixed target replay as news.
```

## Candidate Scope

```text
A2_real / G11A
B2_real / G15B
A0 / B0 reference-only controls
```

Do not add new families.

## Stage 1 — Feature and cache rebuild

Using local-only model assets already present, rebuild or verify:

```text
BGE embeddings
FinBERT logits/probabilities
event label scores
asset/sector relevance scores
A2/B2 news tensors
```

Create:

```text
features/phase1_feature_cache_manifest.csv
features/phase1_daily_feature_stats.csv
features/phase1_tensor_sample_rows.csv
features/phase1_model_provenance.csv
```

Every row must include:

```text
local_files_only
network_attempted
model_path
model_snapshot_or_hash
cache_key
date
track
candidate_id
feature_shape
```

## Stage 2 — Retrieval and clustering baselines

Implement feature-construction only:

```text
R1_bm25_entity_baseline
R2_bge_vector_topk_similarity
R3_news_cluster_support
R4_nearest_historical_news_analogue
R5_event_cluster_confirmation
```

The retrieval system must be local feature construction, not online generative RAG.

Create:

```text
retrieval/vector_index_manifest.csv
retrieval/daily_topk_retrieval_features.csv
retrieval/historical_analogue_features.csv
clustering/news_cluster_assignments.csv
clustering/cluster_support_features.csv
```

Leakage rule:

```text
For date t, retrieval index may include only historical news strictly before t unless the feature is same-day visible news aggregation under official cutoff.
Do not retrieve from future dates.
```

## Stage 3 — Calibration baselines

Implement no-training or shallow calibration:

```text
C1_temperature_scaling_if_logits_exist
C2_Platt_logistic_calibration
C3_isotonic_calibration
C4_confidence_margin_damping
C5_entropy_uncertainty_shrinkage
```

Train/calibrate on 2024 only. Freeze parameters.

Create:

```text
calibration/calibration_fit_manifest.csv
calibration/calibration_parameters_2024.csv
calibration/calibration_diagnostics_2024.csv
calibration/frozen_calibration_config.yaml
```

Do not choose calibration based on 2025 performance.

## Stage 4 — Shallow fusion baselines

Implement shallow models only:

```text
F1_linear_shrinkage_fusion
F2_ridge_or_logistic_head
F3_rank_fusion
F4_gated_fusion_by_confidence_and_regime
F5_risk_controlled_overlay_shrinkage
```

Use 2024 only for fitting.

A2 focus:

```text
macro relevance
tone confidence
risk-regime confidence
turnover-aware overlay shrinkage
```

B2 focus:

```text
sector relevance
event-label confidence
Rank-IC stability
turnover/drawdown-aware overlay shrinkage
```

Create:

```text
fusion/fusion_model_manifest.csv
fusion/fusion_parameters_2024.csv
fusion/fusion_feature_importance.csv
fusion/frozen_fusion_configs.csv
```

## Stage 5 — 2024 walk-forward validation

Run 2024-only validation for:

```text
A2_real baseline
A2_calibrated
A2_retrieval_features
A2_shallow_fusion

B2_real baseline
B2_calibrated
B2_retrieval_features
B2_shallow_fusion

A0/B0 references
```

Create:

```text
reference/phase1_2024_walkforward_results.csv
reference/phase1_2024_metric_comparison.csv
presented/run_csv/phase1_2024_walkforward_results.csv
presented/run_csv/phase1_2024_metric_comparison.csv
```

Do not run frozen 2025 selection here unless needed only as a smoke marked `report_only_not_selection`.

## Stage 6 — Ablations

Run on 2024:

```text
active news
zeroed news
date-shuffled news
retrieval disabled
calibration disabled
fusion disabled
confidence gate disabled
turnover guard disabled
```

Create:

```text
ablations/phase1_ablation_results_2024.csv
presented/run_csv/phase1_ablation_results_2024.csv
```

## Stage 7 — Tests

Run:

```bash
rtk python -m pytest tests/test_nlpcc/test_news_overlay -q
rtk python -m pytest tests/test_nlpcc -q
```

Do not run pip check or compileall unless cheap and previously expected.

Create:

```text
tests/test_results_summary_prompt02.csv
presented/run_csv/test_results_summary_prompt02.csv
logs/prompt02_tests.log
```

## Required Dense Presented Files

`presented/essential_results.md` must include:

```text
method table
feature/cache status
retrieval status
calibration status
fusion status
2024 walk-forward table
ablation table
go/no-go for Prompt03 and Prompt04
caveats
```

## Final Response Format

```text
Prompt02 status:
  <pass/partial/fail/blocked>

Implementation log:
  <path>
  count: <1/other>

Phase 1 methods:
  retrieval: <complete/partial/blocked>
  clustering: <complete/partial/blocked>
  calibration: <complete/partial/blocked>
  shallow fusion: <complete/partial/blocked>

2024 walk-forward:
  rows: <n>
  best A2 variant: <name/none>
  best B2 variant: <name/none>
  csv: <path>

Ablations:
  status: <complete/partial/fail>
  active beats zeroed:
    Track A: <yes/no/mixed>
    Track B: <yes/no/mixed>
  active beats shuffled:
    Track A: <yes/no/mixed>
    Track B: <yes/no/mixed>

Go/no-go:
  Prompt03 contrastive BGE: <go/no_go/conditional>
  Prompt04 LoRA/event head: <go/no_go/conditional>

Hidden 2026 used?
  no

2025 used for tuning?
  no

Best next action:
  <one action>
```
