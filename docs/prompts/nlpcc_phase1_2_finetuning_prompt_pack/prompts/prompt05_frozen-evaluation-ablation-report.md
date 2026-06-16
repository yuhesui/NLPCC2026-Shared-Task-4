# prompt05_frozen-evaluation-ablation-report.md

## Model Setting

Use **GPT-5.5 xHigh** in Codex.

## Role

You are GPT-5.5 xHigh acting as:

```text
senior final-validation engineer
official-server parity auditor
financial NLP experiment synthesiser
system-report claim auditor
single implementation-log writer
```

## Objective

Run final frozen evaluation and synthesis for Phase 1–2 experiments.

This prompt evaluates the Phase 1 and Phase 2 variants against A2_real/B2_real and A0/B0 references.

It must not tune on 2025. It must not promote automatically. It must produce a dense `presented/` package that allows monitoring and decision-making.

## Output Folder

```text
outputs/reports/focused_candidate_optimisation/next_phase_finetuning_phase12/prompt05_frozen_eval_ablation_report/
```

Required subfolders:

```text
presented/
presented/run_csv/
reference/
logs/
traces/
server_run/
ablations/
report/
tests/
configs/
```

## Presented Folder Rule

Create exactly:

```text
presented/implementation_log.md
presented/progress_dashboard.md
presented/essential_results.md
presented/blockers_and_decisions.md
presented/run_csv_manifest.csv
presented/run_csv/
```

The `presented/essential_results.md` must merge:

```text
frozen 2025 results
2024-vs-2025 comparison
ablation outcomes
official path status
method ranking
risk register
report claims allowed/not allowed
next decision
```

## Hard Rules

```text
Use rtk, rtk python, rtk git.
No hidden 2026.
No online API.
No model download.
No 2025 tuning.
No parameter changes after frozen configs are selected from 2024.
No broad candidate search.
No proxy/fake result.
No fixed target replay as news.
No remote official submission.
```

## Inputs to Read

```text
Prompt01 split/label audit
Prompt02 Phase 1 configs/results
Prompt03 contrastive BGE configs/results if present
Prompt04 event/aspect/LoRA configs/results if present
Prompt11 official A2/B2 reference results
A0/B0 reference configs/results
```

## Stage 1 — Freeze config manifest

Create a frozen manifest from 2024-selected variants only:

```text
configs/frozen_phase12_candidate_manifest.csv
configs/frozen_phase12_config_hash_manifest.csv
```

Candidate variants:

```text
A0 reference
A2_real original
A2_phase1_best
A2_contrastive_bge if Prompt03 passed
A2_event_aspect_head if Prompt04 passed

B0 reference
B2_real original
B2_phase1_best
B2_contrastive_bge if Prompt03 passed
B2_event_head if Prompt04 passed
```

Every variant must have:

```text
source prompt
selected_by_2024_only
config_hash
model_or_adapter_hash
local_files_only
network_attempted
```

## Stage 2 — Frozen 2025 evaluation

Run full public 2025 evaluation for the frozen variants.

Create:

```text
reference/frozen_2025_phase12_results.csv
reference/frozen_2025_metric_comparison.csv
presented/run_csv/frozen_2025_phase12_results.csv
presented/run_csv/frozen_2025_metric_comparison.csv
traces/frozen_2025_<track>_<candidate_id>_<variant>.csv
logs/frozen_2025_<track>_<candidate_id>_<variant>.log
```

Each row:

```text
track
candidate_id
variant
method_family
selected_by_2024_only
date_start
date_end
return
sharpe
max_drawdown
turnover
mean_abs_overlay
overlay_nonzero_days
delta_vs_original_A2_or_B2
delta_vs_reference_no_news
uses_finetuned_embedding
uses_trained_head
uses_lora
uses_calibration
uses_retrieval
uses_fusion
real_transformer_executed
proxy_mode
heuristic_fallback_used
fixed_target_replay_used
network_attempted
local_files_only
actual_run
official_server_or_platform_run
status
notes
```

## Stage 3 — Robust ablations

For best A2 and best B2 variants, run:

```text
active
zeroed news
date-shuffled news with at least 5 seeds if runtime allows
random labels
retrieval disabled
calibration disabled
trained module disabled
turnover guard disabled
```

Create:

```text
ablations/phase12_final_ablation_results.csv
ablations/phase12_multishuffle_results.csv
presented/run_csv/phase12_final_ablation_results.csv
presented/run_csv/phase12_multishuffle_results.csv
```

Interpretation rule:

```text
If shuffled news beats active, do not claim real news value.
If zeroed equals active, the trained module is not materially used.
If random labels match real labels, labels are too noisy.
```

## Stage 4 — Official local server/platform parity check

Run closest official local path for:

```text
A2 best variant
B2 best variant
A0/B0 references if cheap
```

Prefer strict HTTP path if available.

Create:

```text
server_run/phase12_official_path_manifest.csv
reference/phase12_official_path_results.csv
presented/run_csv/phase12_official_path_results.csv
```

If strict HTTP is not possible, mark why.

## Stage 5 — Decision table

Create:

```text
reference/phase12_method_decision_table.csv
presented/run_csv/phase12_method_decision_table.csv
```

Decision statuses:

```text
recommended_continue
candidate_for_final_pack_after_more_checks
research_only
report_ablation
reject_no_signal
reject_leakage_or_ablation_failure
blocked
```

Do not use:

```text
submission_ready
hidden_ready
top3_ready
```

## Stage 6 — Methodology and report notes

Create:

```text
report/phase12_final_methodology_update.md
report/system_report_update_notes_phase12.md
report/next_phase_recommendation_after_phase12.md
```

Also merge into:

```text
presented/essential_results.md
```

Required report claims:

```text
what improved
what failed
what should not be claimed
whether A2 active-vs-shuffled improved
whether B2 shuffled-news weakness improved
whether fine-tuning was useful
whether only calibration/retrieval should be kept
```

## Stage 7 — Tests

Run:

```bash
rtk python -m pytest tests/test_nlpcc/test_news_overlay -q
rtk python -m pytest tests/test_nlpcc -q
rtk python -m pytest tests -q
```

Create:

```text
tests/test_results_summary_prompt05.csv
presented/run_csv/test_results_summary_prompt05.csv
logs/prompt05_tests.log
```

## Required CSVs in presented/run_csv

```text
frozen_2025_phase12_results.csv
frozen_2025_metric_comparison.csv
phase12_final_ablation_results.csv
phase12_multishuffle_results.csv
phase12_official_path_results.csv
phase12_method_decision_table.csv
test_results_summary_prompt05.csv
```

## Implementation Log Sections

```text
A. Summary
B. Files Read
C. Files Created
D. Commands Run
E. Frozen Config Manifest
F. Frozen 2025 Evaluation
G. Ablations
H. Official Path Check
I. Decision Table
J. Methodology Update
K. Tests
L. Hidden 2026 / Leakage Check
M. Caveats
N. Next Phase
```

## Final Response Format

```text
Prompt05 status:
  <pass/partial/fail/blocked>

Implementation log:
  <path>
  count: <1/other>

Frozen 2025 evaluation:
  status: <complete/partial/fail/blocked>
  rows: <n>
  csv: <path>

Best Phase 1–2 result:
  Track A:
    variant: <name/none>
    decision: <status>
    reason: <short>
  Track B:
    variant: <name/none>
    decision: <status>
    reason: <short>

Ablations:
  status: <complete/partial/fail>
  active beats zeroed:
    Track A: <yes/no/mixed/not_run>
    Track B: <yes/no/mixed/not_run>
  active beats shuffled:
    Track A: <yes/no/mixed/not_run>
    Track B: <yes/no/mixed/not_run>

Official local path:
  status: <complete/partial/blocked/not_run>
  strict HTTP path used: <yes/no>
  csv: <path>

Report update:
  path: <path>

Tests:
  pytest news_overlay: <pass/fail/not_run>
  pytest tests_nlpcc: <pass/fail/not_run>
  pytest full tests: <pass/fail/not_run>

Official submission run?
  no

Hidden 2026 used?
  no

2025 used for tuning?
  no

Main caveats:
  <list>

Best next action:
  <one action>
```
