# NLPCC Next Phase Prompt Pack — Phase 1–2 Fine-Tuning / Retrieval / Calibration Execution

## Purpose

This pack is for a fresh Codex workflow after Prompt11. It executes the first two practical phases of the next fine-tuning research plan for NLPCC 2026 Shared Task 4:

- **Phase 1:** no-training retrieval, clustering, calibration, and shallow fusion baselines;
- **Phase 2:** contrastive embedder fine-tuning and small event/aspect fine-tuning experiments.

The pack assumes the current selected news candidates remain:

```text
Track A: A2_real / G11A, compact production N13/I6/S13 real-transformer news overlay
Track B: B2_real / G15B, compact production N4/I6/S2 real-transformer news overlay
Reference-only controls: A0 / B0
```

The purpose is not to reopen final news-candidate selection. The purpose is to improve and evidence the current A2/B2 news pipeline through leakage-safe labels, retrieval features, calibration, and small fine-tuning.

## Prompt Order

| Prompt | Model Effort | Purpose |
|---|---|---|
| `prompt00_init-session-finetuning-phase.md` | GPT-5.5 High | Fresh Codex session setup, read repo, create phase scaffold, define monitoring rules. |
| `prompt01_data-label-audit-frozen-splits.md` | GPT-5.5 xHigh | Build leakage-safe data/label audit and frozen split manifests. |
| `prompt02_phase1-retrieval-calibration-shallow-fusion.md` | GPT-5.5 High/xHigh | Implement no-training retrieval, clustering, calibration, and shallow fusion baselines. |
| `prompt03_phase2-contrastive-bge-relevance-finetuning.md` | GPT-5.5 xHigh | Run BGE-small contrastive relevance fine-tuning, with local 6 GB safe mode and optional cloud mode. |
| `prompt04_phase2-event-aspect-head-lora-cloud.md` | GPT-5.5 xHigh | Run small event/aspect head training and optional LoRA experiments after label audit passes. |
| `prompt05_frozen-evaluation-ablation-report.md` | GPT-5.5 xHigh | Run frozen 2025 evaluation, ablations, official path checks, and final report synthesis. |

## Presented Folder Rule

Every prompt must write a dense `presented/` folder under its output root. Do not scatter important information across many small Markdown files. The `presented/` folder should allow progress monitoring without opening the entire repo.

Minimum `presented/` contents for each actual execution prompt:

```text
presented/
  implementation_log.md
  progress_dashboard.md
  essential_results.md
  blockers_and_decisions.md
  run_csv/
  run_csv_manifest.csv
```

For long phases, `essential_results.md` should merge summaries, key tables, caveats, commands, result interpretation, and next actions.

## Recommended Codex Skills

See `RECOMMENDED_CODEX_SKILLS.md` and `skills/`.
