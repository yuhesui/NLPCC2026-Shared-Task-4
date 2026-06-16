# prompt04_phase2-event-aspect-head-lora-cloud.md

## Model Setting

Use **GPT-5.5 xHigh** in Codex.

## Role

You are GPT-5.5 xHigh acting as:

```text
senior transformer classifier fine-tuning engineer
Chinese financial event extraction engineer
LoRA/PEFT training operator
model-risk and leakage auditor
single implementation-log writer
```

## Objective

Execute Phase 2B: small event/aspect head training and optional LoRA experiments for A2_real and B2_real.

This prompt is conditional. It should run only if Prompt01 label quality is sufficient and Prompt02/03 show that trained text modules are worth testing.

Primary targets:

```text
A2_real:
  macro aspect/tone head
  risk-policy-liquidity-property labels
  confidence calibration for overlay shrinkage

B2_real:
  N4 event-label head
  sector-event relevance head
  event confidence and Rank-IC stability features
```

## Output Folder

```text
outputs/reports/focused_candidate_optimisation/next_phase_finetuning_phase12/prompt04_phase2_event_aspect_lora/
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

Use dense monitor files only:

```text
presented/implementation_log.md
presented/progress_dashboard.md
presented/essential_results.md
presented/blockers_and_decisions.md
presented/run_csv_manifest.csv
presented/run_csv/
```

## Hard Rules

```text
Use rtk, rtk python, rtk git.
No hidden 2026.
No online API.
No model download unless local approved snapshot already exists.
No 2025 tuning.
No full LLM fine-tuning.
No QLoRA on large generative LLMs.
No RLHF/RLAIF/DPO in this prompt.
No TAPT/DAPT in this prompt.
No broad candidate search.
No proxy/fake result.
No fixed target replay as news.
```

## Run Gate

Before training, read:

```text
Prompt01 go_no_go_table.csv
Prompt02 phase1_2024_walkforward_results.csv
Prompt03 retrieval_eval_2024.csv if present
```

Proceed only if:

```text
event/aspect labels have enough coverage
class balance is not catastrophic
label noise is documented
baseline no-training controls exist
```

If not, stop and write `blocked_label_quality_insufficient`.

## Hardware Modes

### Local 6 GB safe mode

Use for:

```text
frozen encoder + classifier head
calibration head
very small LoRA if memory permits
```

Defaults:

```text
max_length: 64 or 128
batch_size: 4 to 8
gradient_accumulation: 8 to 16
epochs: 1 to 3
trainable_scope: classifier head first
LoRA rank: 4 or 8 only if safe
```

### Cloud 24–48 GB optional

Use only after local head baseline works.

24 GB:

```text
LoRA on small encoder/classifier
multi-seed
larger batch
```

48 GB:

```text
only if running larger reranker or extensive multi-seed PEFT
```

## Stage 1 — Dataset construction

Create:

```text
datasets/event_head_train_2024.jsonl
datasets/event_head_dev_2024.jsonl
datasets/aspect_head_train_2024.jsonl
datasets/aspect_head_dev_2024.jsonl
datasets/class_label_schema.yaml
datasets/dataset_quality_report.csv
```

Labels:

```text
B2 event labels:
  policy
  liquidity
  technology
  healthcare
  property
  consumer
  export/geopolitics
  regulation
  broad risk
  non-event/irrelevant

A2 macro aspect labels:
  monetary easing/tightening
  fiscal support
  liquidity stress
  property stress
  risk-on/risk-off
  neutral
```

## Stage 2 — Frozen encoder + shallow heads

Train first:

```text
H1_frozen_encoder_event_head
H2_frozen_encoder_aspect_head
H3_frozen_encoder_calibration_head
```

Create:

```text
training/frozen_head_training_metrics.csv
models/frozen_head_model_manifest.csv
evaluation/frozen_head_eval_2024.csv
presented/run_csv/frozen_head_eval_2024.csv
```

## Stage 3 — Optional LoRA/PEFT

Only run if frozen head baseline is stable.

Train:

```text
L1_lora_event_head_B2
L2_lora_macro_aspect_A2
```

Create:

```text
configs/lora_event_head_local_6gb.yaml
configs/lora_event_head_cloud_24gb.yaml
training/lora_training_metrics.csv
models/lora_adapter_manifest.csv
evaluation/lora_eval_2024.csv
presented/run_csv/lora_eval_2024.csv
```

LoRA must be parameter-efficient and adapter-based. Do not overwrite base model weights.

## Stage 4 — Calibration and confusion diagnostics

Create:

```text
evaluation/event_confusion_matrix.csv
evaluation/aspect_confusion_matrix.csv
evaluation/calibration_curve_table.csv
evaluation/error_slice_table.csv
evaluation/label_noise_failure_cases.csv
```

## Stage 5 — Candidate feature integration

Create feature-flagged variants:

```text
A2_aspect_head_feature
A2_lora_aspect_feature if LoRA passed

B2_event_head_feature
B2_lora_event_feature if LoRA passed
```

Run 2024-only walk-forward:

```text
reference/event_aspect_head_2024_walkforward_results.csv
presented/run_csv/event_aspect_head_2024_walkforward_results.csv
```

## Stage 6 — Ablations

Run:

```text
frozen encoder baseline
shallow head
LoRA adapter
random labels
shuffled news
event labels disabled
aspect labels disabled
calibration disabled
```

Create:

```text
ablations/event_aspect_ablation_results_2024.csv
presented/run_csv/event_aspect_ablation_results_2024.csv
```

## Stage 7 — Tests

Run:

```bash
rtk python -m pytest tests/test_nlpcc/test_news_overlay -q
```

Create:

```text
tests/test_results_summary_prompt04.csv
presented/run_csv/test_results_summary_prompt04.csv
logs/prompt04_tests.log
```

## Stop Rules

Stop or downgrade to research-only if:

```text
random/shuffled labels perform similarly to real labels
LoRA gives no improvement over frozen head
class balance is too poor
B2 shuffled-news weakness worsens
A2 active-vs-shuffled margin worsens
training attempts network download
local model provenance cannot be recorded
```

## Final Response Format

```text
Prompt04 status:
  <pass/partial/fail/blocked>

Implementation log:
  <path>
  count: <1/other>

Run gate:
  label quality: <pass/conditional/fail>
  reason: <short>

Frozen-head training:
  status: <complete/partial/fail/blocked>
  A2 aspect head: <summary>
  B2 event head: <summary>

LoRA:
  status: <complete/partial/skipped/blocked>
  reason: <short>
  adapter manifest: <path/none>

2024 walk-forward:
  rows: <n>
  csv: <path>

Ablation:
  status: <complete/partial/fail>
  random/shuffled warning: <yes/no>

Candidate variants:
  <list>

Hidden 2026 used?
  no

2025 used for tuning?
  no

Best next action:
  <one action>
```
