# Skill: small-gpu-finetuning-runner

## Purpose
Apply safe fine-tuning defaults for a 6 GB RTX 4050 laptop.

## Defaults
```text
max_length: 64 or 128
batch_size: 4 to 8
gradient_accumulation: 8 to 16
epochs: 1 to 3
fp16: true if stable
gradient_checkpointing: true if supported
freeze_base_model: true by default
trainable_scope: classifier head / projection / tiny LoRA
```

## OOM response
1. reduce max_length
2. reduce batch_size
3. increase gradient accumulation
4. freeze more layers
5. switch to head-only
6. stop and record blocked if still unstable
