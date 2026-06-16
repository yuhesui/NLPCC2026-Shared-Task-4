# Shared Artifact Schema

All prompts should use this phase root unless the repo has a stricter active convention:

```text
outputs/reports/focused_candidate_optimisation/next_phase_finetuning_phase12/
```

Each prompt should use a subfolder:

```text
prompt00_init_session/
prompt01_data_label_audit_frozen_splits/
prompt02_phase1_retrieval_calibration_fusion/
prompt03_phase2_contrastive_bge/
prompt04_phase2_event_aspect_lora/
prompt05_frozen_eval_ablation_report/
```

## Dense presented folder

Each subfolder must contain:

```text
presented/
  implementation_log.md
  progress_dashboard.md
  essential_results.md
  blockers_and_decisions.md
  run_csv/
  run_csv_manifest.csv
```

Do not create many tiny Markdown files in `presented/`. Merge content into `essential_results.md` unless it is a CSV or log.

## Common CSV columns

All run-result CSVs should include:

```text
phase
prompt_id
track
candidate_id
variant
method_family
date_start
date_end
train_window
eval_window
uses_hidden_2026
uses_2025_for_tuning
local_files_only
network_attempted
real_transformer_executed
proxy_mode
heuristic_fallback_used
fixed_target_replay_used
actual_run
status
notes
```
