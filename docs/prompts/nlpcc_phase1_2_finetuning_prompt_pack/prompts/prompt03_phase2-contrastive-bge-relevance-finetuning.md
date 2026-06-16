# prompt03_phase2-contrastive-bge-relevance-finetuning.md

## Model Setting

Use **GPT-5.5 xHigh** in Codex.

## Role

You are GPT-5.5 xHigh acting as:

```text
senior embedding fine-tuning engineer
Chinese financial retrieval researcher
small-GPU training optimiser
leakage-safe contrastive learning auditor
single implementation-log writer
```

## Objective

Execute Phase 2A: contrastive fine-tuning of the BGE-style news relevance embedder, starting with a safe local 6 GB RTX 4050 mode and optionally preparing a cloud 24–48 GB mode.

The goal is to improve:

```text
A2_real:
  macro-news relevance and macro aspect matching

B2_real:
  sector-news relevance, event-sector mapping, and shuffled-news robustness
```

This prompt must not run large LLM fine-tuning, RLHF, DPO, TAPT, or DAPT.

## Output Folder

```text
outputs/reports/focused_candidate_optimisation/next_phase_finetuning_phase12/prompt03_phase2_contrastive_bge/
```

Required subfolders:

```text
presented/
presented/run_csv/
reference/
logs/
datasets/
training/
models/
configs/
evaluation/
ablations/
tests/
cloud/
```

## Presented Folder Rule

Create only dense monitoring files in `presented/`:

```text
presented/implementation_log.md
presented/progress_dashboard.md
presented/essential_results.md
presented/blockers_and_decisions.md
presented/run_csv_manifest.csv
presented/run_csv/
```

`presented/essential_results.md` must merge dataset, training, evaluation, ablation, hardware, and next-action summaries.

## Hard Rules

```text
Use rtk, rtk python, rtk git.
No hidden 2026.
No online API.
No model download unless already approved and cached.
No 2025 tuning.
No large LLM SFT.
No QLoRA on generative LLMs.
No DPO/RLHF.
No TAPT/DAPT.
No cross-encoder training unless explicitly scoped as skipped/deferred.
No proxy/fake result.
No fixed target replay as news.
```

## Prerequisite

Read Prompt01 and Prompt02 outputs first.

Proceed only if:

```text
Prompt01 split manifest exists.
news-sector relevance labels exist.
hard-negative manifest exists.
label quality is at least conditional-go.
Prompt02 no-training baselines exist.
```

If prerequisites fail, stop and produce `blocked_missing_labels_or_baselines`.

## Hardware Modes

### Local safe mode: RTX 4050 6 GB

Default first run.

Use:

```text
model: existing local BGE-small-zh snapshot only
local_files_only: true
max_length: 64 or 128
batch_size: 4 to 16
gradient_accumulation: 4 to 16
epochs: 1 to 3
fp16: true if stable
gradient_checkpointing: true if supported
trainable_scope: pooling/projection/head or LoRA-lite only if memory allows
```

### Cloud mode: optional

Prepare but do not require:

```text
24 GB GPU:
  larger batch, more hard negatives, multi-seed

48 GB GPU:
  only if full contrastive run or reranker research is later approved
```

Cloud runs must produce:

```text
cloud/cloud_run_manifest.csv
cloud/environment_manifest.csv
cloud/cost_time_estimate.csv
```

## Stage 1 — Dataset preparation

Create sentence-pair/triplet datasets from Prompt01 labels.

Required files:

```text
datasets/contrastive_train_2024.jsonl
datasets/contrastive_dev_2024.jsonl
datasets/contrastive_hard_negatives_2024.jsonl
datasets/dataset_card.md
datasets/dataset_quality_report.csv
```

Each JSONL row:

```json
{
  "query": "news title or summary",
  "positive": "sector/asset/event prototype",
  "negative": "hard negative prototype",
  "date": "YYYY-MM-DD",
  "track": "A/B",
  "label_source": "...",
  "text_hash": "...",
  "split": "train/dev",
  "leakage_safe": true
}
```

No 2025 rows in training/dev.

## Stage 2 — Training config

Create:

```text
configs/bge_contrastive_local_6gb.yaml
configs/bge_contrastive_cloud_24gb.yaml
configs/bge_contrastive_cloud_48gb_optional.yaml
training/training_command_manifest.csv
```

Recommended loss:

```text
MultipleNegativesRankingLoss if false negatives are controlled
TripletLoss or contrastive loss if explicit negatives are safer
```

If false-negative risk is high, avoid MultipleNegativesRankingLoss and use explicit triplets.

## Stage 3 — Local 6 GB prototype training

Run a bounded prototype:

```text
small subset first
then full 2024 if stable
max runtime cap set in config
checkpoint every epoch
```

Required outputs:

```text
training/local_6gb_training_log.md
training/local_6gb_metrics.csv
models/local_bge_contrastive_adapter_manifest.csv
models/model_card_contrastive_bge.md
```

If OOM occurs:

```text
reduce max_length
reduce batch_size
increase gradient_accumulation
freeze more layers
fall back to projection/head-only
record OOM and final safe config
```

## Stage 4 — Embedding and retrieval evaluation

Evaluate against frozen encoder baseline, on 2024 dev only:

```text
Recall@k
MRR
NDCG@k
hard-negative accuracy
sector confusion
macro relevance confusion
embedding drift
```

Create:

```text
evaluation/retrieval_eval_2024.csv
evaluation/hard_negative_eval_2024.csv
evaluation/embedding_drift_report.csv
presented/run_csv/retrieval_eval_2024.csv
presented/run_csv/hard_negative_eval_2024.csv
```

## Stage 5 — Integrate as candidate feature, not automatic final method

Create a feature-flagged variant:

```text
A2_bge_contrastive_feature
B2_bge_contrastive_feature
```

Do not replace A2/B2 production path unless later evaluation proves it.

Run 2024-only walk-forward with frozen 2024-trained adapter:

```text
reference/contrastive_bge_2024_walkforward_results.csv
presented/run_csv/contrastive_bge_2024_walkforward_results.csv
```

## Stage 6 — Ablations

Run:

```text
frozen BGE baseline
contrastive BGE adapter
random adapter
shuffled labels
soft negatives only
hard negatives included
adapter disabled
```

Create:

```text
ablations/contrastive_bge_ablation_results_2024.csv
presented/run_csv/contrastive_bge_ablation_results_2024.csv
```

## Stage 7 — Tests

Run:

```bash
rtk python -m pytest tests/test_nlpcc/test_news_overlay -q
```

Run targeted training/evaluation smoke tests if created.

Create:

```text
tests/test_results_summary_prompt03.csv
presented/run_csv/test_results_summary_prompt03.csv
logs/prompt03_tests.log
```

## Stop Rules

Stop and mark blocked if:

```text
labels are too sparse
false-negative risk is uncontrolled
local model path missing
network download is attempted
OOM cannot be resolved with safe local settings
contrastive adapter underperforms frozen BGE on dev retrieval
shuffled labels perform similarly to real labels
```

## Final Response Format

```text
Prompt03 status:
  <pass/partial/fail/blocked>

Implementation log:
  <path>
  count: <1/other>

Dataset:
  train rows: <n>
  dev rows: <n>
  hard negatives: <n>
  leakage safe: <yes/no>

Local 6GB training:
  status: <complete/partial/oom/blocked/not_run>
  gpu: <name>
  best safe config: <path>
  model/adaptor manifest: <path>

Retrieval evaluation:
  frozen BGE baseline: <metric summary>
  contrastive adapter: <metric summary>
  csv: <path>

Ablation:
  status: <complete/partial/fail>
  shuffled-label warning: <yes/no>

Candidate integration:
  A2 feature variant: <created/not_created>
  B2 feature variant: <created/not_created>

Cloud mode:
  prepared: <yes/no>
  executed: <yes/no>

Hidden 2026 used?
  no

2025 used for tuning?
  no

Best next action:
  <one action>
```
