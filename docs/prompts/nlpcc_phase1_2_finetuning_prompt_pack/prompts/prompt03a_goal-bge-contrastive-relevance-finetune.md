/goal Finish the BGE contrastive relevance branch for NLPCC Phase 1-2 from the current fork, producing a real frozen fine-tuned relevance artifact or an honest blocked report.

You are GPT-5.5 xHigh in Codex Goal mode. Act as senior Chinese-financial-NLP engineer, leakage auditor, small-GPU finetuning operator, and evidence writer.

Root output folder:
`outputs/reports/next_phase_finetuning_phase12/prompt03a_goal_bge_contrastive_relevance/`

Dense monitor folder:
`presented/` with only essential, information-dense files:
`implementation_log.md`, `progress_dashboard.md`, `essential_results.md`, `blockers_and_decisions.md`, `run_csv_manifest.csv`, `run_csv/`.

Context to read first:
- AGENTS.md, README.md, RTK instructions.
- `outputs/reports/next_phase_finetuning_phase12/prompt00_init_session/`
- `outputs/reports/next_phase_finetuning_phase12/prompt01_data_label_audit_frozen_splits/`
- `outputs/reports/next_phase_finetuning_phase12/prompt02_phase1_retrieval_calibration_fusion/`
- Prompt11 A2/B2 configs and official result traces if still under old folder.

Hard rules:
Use `rtk`, `rtk python`, `rtk git`. Verify RTK Python/env before training. No hidden 2026. No 2025 tuning. No online API. No model download. Local HF only. A2_real and B2_real remain selected news candidates. A0/B0 are reference-only. If local BGE missing, stop as `blocked_missing_local_bge`.

Main goal:
Materialize full 2024 BGE vector cache, build safe hard negatives, train or skip contrastive BGE relevance model, freeze best 2024 config, optimize overlay only on 2024, and prepare artifact for Prompt04.

Required stages:
1. Cache gate: materialize full 2024 BGE embeddings/top-k index for news-to-asset and news-to-sector. Record model path, snapshot/hash, local_files_only, network_attempted=false, device, dtype, row count, embedding dim, cache key.
2. Retrieval baseline: compare lexical/entity, previous R1/R3/R4/R5, fresh BGE top-k, and hybrid lexical+BGE. If fresh BGE is unusable or worse without explanation, do not train; write blocked report.
3. Dataset build: create contrastive train/dev from 2024 only using Prompt01 relevance labels, hard negatives, same-date wrong sector, high-overlap wrong sector, and date-shuffled negatives. Flag false-negative risk.
4. Train: run small-GPU-safe contrastive BGE finetuning if feasible: small batches, grad accumulation, fp16 if stable, short max_len, early stop on 2024 dev retrieval metric. No 2025 checkpoint choice.
5. Optimize: freeze best 2024 checkpoint/config; run bounded overlay optimization on 2024 only for A2_real and B2_real using tuned relevance features. Compare against Prompt02 shallow-fusion and original A2/B2.
6. Ablate: active, zeroed, shuffled-date, retrieval-disabled, base-BGE-vs-finetuned-BGE.
7. Tests: run news overlay tests and any targeted cache/retrieval tests.

Required outputs:
- `cache/bge_vector_cache_manifest.csv`
- `retrieval/fresh_retrieval_metric_comparison.csv`
- `training/contrastive_dataset_manifest.csv`
- `training/training_run_manifest.csv`
- `training/checkpoint_selection_2024_only.csv`
- `optimiser/bge_branch_best_configs.csv`
- `ablations/bge_branch_ablation_results.csv`
- `tests/test_results_summary_prompt03a.csv`
- copy key CSVs to `presented/run_csv/`.

Completion criteria:
Pass if either: (a) fine-tuned BGE improves 2024 dev retrieval or portfolio ablation over base BGE and writes frozen config; or (b) training is blocked/skipped with evidence and safe fallback config. Final answer must give status, selected artifact, 2025 tuning=no, hidden 2026=no, and best next action.
