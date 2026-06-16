# Execution Order and Model Assignment

## Hardware assumptions

```text
Local:
  RTX 4050 Laptop GPU, 6 GB VRAM.
  Use for: cache rebuild, calibration, shallow heads, small BGE contrastive prototype.

Cloud optional:
  24 GB GPU:
    Use for full BGE-small contrastive training, multi-seed runs, LoRA on small encoders.
  48 GB GPU:
    Use only for reranker/LoRA/TAPT/DAPT research after Phase 1 proves value.
```

## Execution order

```text
prompt00 -> prompt01 -> prompt02 -> prompt03 -> prompt04 -> prompt05
```

Do not run Prompt03/04 until Prompt01 creates valid labels and Prompt02 establishes no-training controls.

## Model effort

| Prompt | Recommended model setting |
|---|---|
| prompt00 | GPT-5.5 High |
| prompt01 | GPT-5.5 xHigh |
| prompt02 | GPT-5.5 High, use xHigh if repo state is messy |
| prompt03 | GPT-5.5 xHigh |
| prompt04 | GPT-5.5 xHigh |
| prompt05 | GPT-5.5 xHigh |
