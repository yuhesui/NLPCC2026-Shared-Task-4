/goal Finish the event/aspect fine-tuning branch for NLPCC Phase 1-2 from the current fork, producing frozen-head and optional LoRA artifacts or an honest blocked report.

You are GPT-5.5 xHigh in Codex Goal mode. Act as weak-label auditor, FinBERT/event-head engineer, PEFT/LoRA operator, portfolio overlay engineer, and evidence writer.

Root output folder:
`outputs/reports/next_phase_finetuning_phase12/prompt03b_goal_event_aspect_lora/`

Dense monitor folder:
`presented/` with `implementation_log.md`, `progress_dashboard.md`, `essential_results.md`, `blockers_and_decisions.md`, `run_csv_manifest.csv`, `run_csv/`.

Context to read first:
- AGENTS.md, README.md, RTK instructions.
- Prompt00/01/02 outputs under `outputs/reports/next_phase_finetuning_phase12/`.
- Prompt01 event/aspect labels, quality tables, class balance, noise-risk tables.
- Prompt02 calibration/fusion artifacts and ablations.
- Prompt11 selected A2/B2 configs/source maps.

Hard rules:
Use `rtk`, `rtk python`, `rtk git`. Verify RTK Python/env and CUDA. No hidden 2026. No 2025 tuning. No online API. No model download. Local model only. A2_real/B2_real selected; A0/B0 reference-only. Do not train LoRA until label-noise gate passes.

Main goal:
Audit weak event/aspect labels, train frozen heads first, optionally train LoRA only if justified, freeze 2024-selected configs, optimize bounded overlays, and prepare artifact for Prompt04.

Required stages:
1. Label gate: audit event/aspect weak labels for coverage, class balance, noise risk, false positives, false negatives, and dev stability. Decision must be one of `go_lora`, `go_frozen_head_only`, `blocked_label_noise_too_high`, `blocked_class_coverage_too_sparse`.
2. Cache/logits: rebuild or verify 2024 FinBERT/event model probability/logit cache. Record model path, snapshot/hash, local_files_only, network_attempted=false, device, dtype, row count.
3. Frozen heads: train shallow/frozen encoder classifiers or regressors for A2 macro aspect/tone and B2 event/sector impact using 2024 train only; select using 2024 dev only.
4. Optional LoRA: only if label gate allows. Use PEFT/LoRA on small local encoder/classifier; small batches, grad accumulation, early stop. If 6GB laptop cannot handle it, emit `blocked_local_vram` and write cloud-ready config, not fake results.
5. Optimize: freeze best 2024 config; bounded overlay optimization on 2024 only for A2_real and B2_real. Compare frozen-head, LoRA-if-any, Prompt02 shallow-fusion, and original A2/B2.
6. Ablate: active, zeroed, shuffled labels, label-head-disabled, confidence-gate-disabled, LoRA-vs-frozen-head if LoRA ran.
7. Tests: run news overlay tests and targeted no-proxy/no-fixed-replay tests if present.

Required outputs:
- `label_audit/event_aspect_label_gate.csv`
- `features/finbert_event_logit_cache_manifest.csv`
- `training/frozen_head_training_manifest.csv`
- `training/lora_training_manifest.csv`
- `training/checkpoint_selection_2024_only.csv`
- `optimiser/event_aspect_branch_best_configs.csv`
- `ablations/event_aspect_branch_ablation_results.csv`
- `tests/test_results_summary_prompt03b.csv`
- copy key CSVs to `presented/run_csv/`.

Completion criteria:
Pass if frozen-head or LoRA branch produces a valid 2024-frozen config with ablations, or if LoRA is blocked and frozen-head/no-training fallback is evidenced. Final answer must state LoRA allowed yes/no, final artifact, 2025 tuning=no, hidden 2026=no, and best next action.
