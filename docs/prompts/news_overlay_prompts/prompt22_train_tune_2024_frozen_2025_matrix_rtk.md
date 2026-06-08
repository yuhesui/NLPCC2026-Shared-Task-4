# Prompt22 — Fix Remaining News Overlay Behaviours, 2024 Train/Tune Matrix, Frozen 2025 Matrix, and RTK-Optimised Execution

## Role

You are a senior quantitative research runner, transformer systems engineer, CUDA/GPU optimisation engineer, Chinese financial NLP engineer, backtesting auditor, and model-risk reviewer.

You are continuing after Prompt21 in the same News Overlay workflow. Prompt21 produced a real-local transformer grid, candidate freeze, frozen 2025 replay, GPU tuning, and audit outputs, but several important behaviours remain incomplete.

This prompt is a **repair + train/tune + matrix-generation prompt**.

---

## Goal

Fix all remaining Prompt21 behavioural gaps, then run a disciplined **2024-only train/tune matrix** and a **frozen 2025 evaluation matrix**.

The prompt is complete only if it produces:

```text
1. full missing-ablation implementation/fix report;
2. complete 2024 train/tune matrix;
3. frozen 2025 evaluation matrix using only 2024-selected configs;
4. candidate-vs-control delta tables;
5. 3–5 candidates per track, never only one;
6. updated candidate classifications;
7. RTK-optimised command usage for large/high-verbosity repo operations;
8. clear statement of what is promotion-ready, research-only, or blocked.
```

---

## Current Starting Point

Use the current repo/session state after Prompt21.

Prompt21 status to treat as current baseline:

```text
- Real-local transformer rows exist.
- 2024 full grid was run.
- 2024 candidate freeze was produced.
- Frozen 2025 selected-candidate replay was produced.
- GPU tuning was run but did not reach >80% target.
- Official runtime was not promoted.
- Official-server parity was not run.
- Full ablation suite was incomplete.
```

The most important remaining Prompt21 gaps are:

```text
1. many ablations are not_run_with_reason;
2. frozen 2025 presented summary should include preserved-base controls and candidate-vs-control deltas;
3. full train/tune matrix over overlay/gate parameters is still insufficient;
4. official-server parity is not yet evidenced;
5. GPU speed benefit is not proven end-to-end;
6. G22B/G23B remain partial/deferred unless intentionally removed.
```

---

## RTK Usage Requirement

RTK is installed or documented in the repo. Use RTK for high-verbosity commands to reduce token output.

Use RTK wrappers where applicable:

```bash
rtk git status
rtk git diff
rtk git log

rtk find "*.md" .
rtk grep "pattern"
rtk ls .
rtk read <large_file>

rtk python pytest
```

For Python tests, prefer:

```bash
rtk python pytest tests/test_nlpcc/test_news_overlay -q
```

instead of raw high-verbosity `pytest`, unless RTK is unavailable.

Before using RTK, verify:

```bash
rtk --version
```

If RTK is unavailable, fall back to standard commands but keep outputs compact and record:

```text
rtk_status=unavailable
fallback_used=true
```

Do not let RTK hide required evidence. If a command result is material, write the full structured evidence to CSV/MD artifacts and use RTK only to keep console output compact.

---

## Output Directory Policy

Store all Prompt22 outputs under:

```text
outputs/reports/news_overlay/prompt22/presented/
outputs/reports/news_overlay/prompt22/reference/
outputs/reports/news_overlay/prompt22/progress/
```

Do not continue writing Prompt22 results primarily under `prompt01_11` or `prompt21`.

Use:

```text
reference/
  full CSVs, matrices, raw verdict tables, run manifests

presented/
  concise human-facing summaries, top candidate tables, key deltas, verdicts

progress/
  execution log, blockers, staged status
```

If a CSV is clear enough, do not duplicate it in a long Markdown file. But the most important 3–5 candidates per track, deltas, and final verdicts must appear in `presented/`.

---

## Non-Negotiable Constraints

```text
- Do not modify frozen official runtime configs.
- Use 2024 only for train/tune/threshold/model/candidate selection.
- Use 2025 only for frozen evaluation after 2024 decisions are locked.
- Do not use hidden 2026 data.
- Do not use current-day close/high/low/return before decision time.
- Same-day news must obey official timestamp cutoff.
- Use local-only Hugging Face model loading.
- Do not download models in this prompt.
- Do not call online APIs.
- Do not copy model binaries into repo/package outputs.
- Do not promote automatically.
- Do not report only one candidate per track.
```

---

## Section 1 — Fix Remaining Behavioural Gaps

First fix the remaining Prompt21 issues before running new matrices.

### 1.1 Complete missing ablation toggles

Implement or repair dedicated toggles for:

```text
random embeddings / random transformer features
aspect-tone off
label-attention off
sector-query attention off
reranker off
impact gate off
sensitivity gate off
confidence gate off
overlay strength sweep
turnover cap sweep
event-category removal
high-volatility vs low-volatility regimes
```

Each toggle must produce a traceable row in the ablation matrix.

Allowed verdicts:

```text
pass
partial
fail
blocked
not_applicable_with_reason
```

Do not leave avoidable `not_run_with_reason` rows if the behaviour can be implemented in this prompt.

### 1.2 Candidate-vs-control deltas

For every top 3–5 candidate per track, compute deltas versus:

```text
Track A:
  preserved Track A primary
  preserved Track A fallback
  G00A base control
  G01A lexical control

Track B:
  preserved Track B primary
  preserved Track B fallback
  G00B base control
  G01B lexical control
```

Metrics:

```text
delta_return
delta_sharpe
delta_max_drawdown
delta_turnover
delta_active_news_days
delta_mean_abs_overlay
delta_runtime_sec
```

### 1.3 2025 presented controls

Ensure frozen 2025 presented outputs include:

```text
- preserved-base controls;
- lexical controls;
- frozen candidate set;
- candidate-vs-control deltas;
- 3–5 candidates per track.
```

### 1.4 G22B/G23B decision

For deferred/partial rows:

```text
G22B temporal narrative attention
G23B graph/entity-sector attention
```

Either:

```text
- implement and run them as ablation rows; or
- explicitly remove them from candidate consideration and classify as deferred_with_reason.
```

Do not leave ambiguous partial-blocked statuses.

---

## Section 2 — 2024 Train/Tune Matrix

Run a 2024-only train/tune matrix. This is where tuning is allowed.

### 2.1 Candidate families

Include at least the Prompt21 top candidate families:

```text
Track A:
  G10A N2/I2/S3
  G11A N13/I6/S13
  G12A N2345/I256/S13

Track B:
  G10B N2/I2/S2
  G21B N2345/I256/S5
  G14B N5/I5/S2
  G15B N4/I6/S2
  G12B N2345/I256/S126
```

Include controls:

```text
G00A, G01A
G00B, G01B
```

### 2.2 Tune dimensions

Tune only on 2024.

Use a compact but meaningful grid:

```text
overlay_strength:
  0.25, 0.50, 0.75, 1.00

impact_threshold:
  0.00, 0.25, 0.50

confidence_threshold:
  0.00, 0.25, 0.50

sensitivity_threshold:
  0.00, 0.25, 0.50

turnover_cap:
  none, low, medium

drawdown_throttle:
  off, mild, strict

cache_mode:
  warm_cache preferred after first pass
```

If this is too large, use a staged matrix:

```text
Stage A:
  coarse sweep over all candidates

Stage B:
  refined sweep over top 3 per track

Stage C:
  final 3–5 frozen candidates per track
```

Do not use 2025 during any tuning or refinement.

### 2.3 Matrix outputs

Create:

```text
outputs/reports/news_overlay/prompt22/reference/train_tune_2024_matrix.csv
outputs/reports/news_overlay/prompt22/reference/train_tune_2024_trackA_ranking.csv
outputs/reports/news_overlay/prompt22/reference/train_tune_2024_trackB_ranking.csv
outputs/reports/news_overlay/prompt22/reference/train_tune_2024_selected_candidates.csv

outputs/reports/news_overlay/prompt22/presented/train_tune_2024_summary.md
outputs/reports/news_overlay/prompt22/presented/trackA_top_candidates_2024.md
outputs/reports/news_overlay/prompt22/presented/trackB_top_candidates_2024.md
```

Every matrix row must include:

```text
run_id
track
method_stack
candidate_family
overlay_strength
impact_threshold
confidence_threshold
sensitivity_threshold
turnover_cap
drawdown_throttle
status
dates_run
return
sharpe
max_drawdown
turnover
active_news_days
mean_abs_overlay
max_abs_overlay
runtime_sec
gpu_util_mean
cache_hit_rate
selection_score
warnings
```

---

## Section 3 — 2024 Selection Freeze

Freeze 3–5 candidates per track using 2024 only.

Selection score:

```text
score =
  0.35 * sharpe_rank
+ 0.20 * cumulative_return_rank
+ 0.20 * max_drawdown_rank
+ 0.15 * turnover_rank
+ 0.10 * ablation_quality_rank
```

If the repo has an official-style score, report both:

```text
conservative_score
official_style_score
```

Create:

```text
outputs/reports/news_overlay/prompt22/reference/selection_freeze_2024.csv
outputs/reports/news_overlay/prompt22/presented/selection_freeze_2024.md
```

The presented freeze must include:

```text
- top 3–5 Track A candidates;
- top 3–5 Track B candidates;
- exact frozen parameter values;
- reason for inclusion;
- candidate-vs-control 2024 deltas.
```

Do not look at 2025 before writing this freeze file.

---

## Section 4 — Frozen 2025 Matrix

After the 2024 freeze file is written, run 2025 only for frozen candidates and controls.

Allowed 2025 rows:

```text
- preserved controls;
- lexical controls;
- frozen top 3–5 Track A candidates;
- frozen top 3–5 Track B candidates.
```

Forbidden:

```text
- changing thresholds after seeing 2025;
- selecting new candidates from 2025;
- changing candidate order based on 2025 except in a clearly labelled diagnostic table.
```

Create:

```text
outputs/reports/news_overlay/prompt22/reference/frozen_2025_matrix.csv
outputs/reports/news_overlay/prompt22/reference/frozen_2025_candidate_vs_control_deltas.csv

outputs/reports/news_overlay/prompt22/presented/frozen_2025_summary.md
outputs/reports/news_overlay/prompt22/presented/frozen_2025_trackA_candidates.md
outputs/reports/news_overlay/prompt22/presented/frozen_2025_trackB_candidates.md
```

Every 2025 row must include:

```text
run_id
track
method_stack
frozen_from_2024_rank
frozen_parameters
status
dates_run
return
sharpe
max_drawdown
turnover
active_news_days
mean_abs_overlay
max_abs_overlay
candidate_vs_primary_delta
candidate_vs_fallback_delta
candidate_vs_lexical_delta
warnings
```

---

## Section 5 — Full Ablation Matrix After Tuning

Run ablations on the frozen candidate sets.

Create:

```text
outputs/reports/news_overlay/prompt22/reference/full_ablation_matrix.csv
outputs/reports/news_overlay/prompt22/reference/full_ablation_candidate_verdicts.csv

outputs/reports/news_overlay/prompt22/presented/full_ablation_summary.md
```

Presented summary must include:

```text
- Track A top 3–5 candidate ablation verdicts;
- Track B top 3–5 candidate ablation verdicts;
- missing/blocked ablations, if any;
- whether shuffled/zero/random controls behave correctly;
- whether transformer components matter beyond lexical controls.
```

---

## Section 6 — GPU / Runtime Matrix

Use Prompt21 GPU tuning result as baseline, then measure end-to-end speed.

Compare:

```text
CPU-only
GPU cold-cache
GPU warm-cache
selected GPU tuning config
```

Create:

```text
outputs/reports/news_overlay/prompt22/reference/runtime_matrix.csv
outputs/reports/news_overlay/prompt22/presented/runtime_summary.md
```

Metrics:

```text
mode
device
batch_size
precision
cache_mode
rows_run
runtime_sec
items_per_sec
gpu_util_peak
gpu_util_mean
vram_peak_mb
speedup_vs_cpu
notes
```

Do not claim CUDA is useful unless end-to-end runtime improves.

---

## Section 7 — Audit and Classification

Audit:

```text
- no 2025 tuning;
- no official runtime change;
- no hidden 2026 use;
- no same-day price leakage;
- news cutoff respected;
- local_files_only=True;
- no online calls;
- no model binaries copied;
- cache keys include model id/snapshot/method/preprocess/text hash;
- candidate selection came only from 2024;
- ablation behaviour is sufficient or insufficient.
```

Create:

```text
outputs/reports/news_overlay/prompt22/reference/leakage_audit.csv
outputs/reports/news_overlay/prompt22/reference/dependency_audit.csv
outputs/reports/news_overlay/prompt22/reference/package_safety_audit.csv
outputs/reports/news_overlay/prompt22/reference/candidate_classification.csv

outputs/reports/news_overlay/prompt22/presented/audit_summary.md
outputs/reports/news_overlay/prompt22/presented/final_recommendation.md
```

Classification values:

```text
reject
research_continue
ablation_supported
frozen_2025_supported
parity_ready_but_human_review_required
```

Do not classify as `parity_ready_but_human_review_required` unless local official-semantics replay and parity preparation are satisfactory. If official-server parity is still not run, state it clearly.

---

## Section 8 — Tests and Checks

Use RTK for verbose checks where possible:

```bash
rtk python pytest tests/test_nlpcc/test_news_overlay -q
rtk git diff
rtk git status
```

Also run targeted checks for:

```text
ablation toggles
2024 tuning only
2025 calibration refusal
candidate freeze before 2025
runtime matrix
cache warm/cold behaviour
local-only model loading
official runtime diff
```

If RTK is unavailable, fall back to standard commands and record this.

---

## Required Output Files

Create/update:

```text
outputs/reports/news_overlay/prompt22/progress/progress_prompt22.md

outputs/reports/news_overlay/prompt22/presented/train_tune_2024_summary.md
outputs/reports/news_overlay/prompt22/presented/trackA_top_candidates_2024.md
outputs/reports/news_overlay/prompt22/presented/trackB_top_candidates_2024.md
outputs/reports/news_overlay/prompt22/presented/selection_freeze_2024.md
outputs/reports/news_overlay/prompt22/presented/frozen_2025_summary.md
outputs/reports/news_overlay/prompt22/presented/frozen_2025_trackA_candidates.md
outputs/reports/news_overlay/prompt22/presented/frozen_2025_trackB_candidates.md
outputs/reports/news_overlay/prompt22/presented/full_ablation_summary.md
outputs/reports/news_overlay/prompt22/presented/runtime_summary.md
outputs/reports/news_overlay/prompt22/presented/audit_summary.md
outputs/reports/news_overlay/prompt22/presented/final_recommendation.md

outputs/reports/news_overlay/prompt22/reference/train_tune_2024_matrix.csv
outputs/reports/news_overlay/prompt22/reference/train_tune_2024_trackA_ranking.csv
outputs/reports/news_overlay/prompt22/reference/train_tune_2024_trackB_ranking.csv
outputs/reports/news_overlay/prompt22/reference/train_tune_2024_selected_candidates.csv
outputs/reports/news_overlay/prompt22/reference/selection_freeze_2024.csv
outputs/reports/news_overlay/prompt22/reference/frozen_2025_matrix.csv
outputs/reports/news_overlay/prompt22/reference/frozen_2025_candidate_vs_control_deltas.csv
outputs/reports/news_overlay/prompt22/reference/full_ablation_matrix.csv
outputs/reports/news_overlay/prompt22/reference/full_ablation_candidate_verdicts.csv
outputs/reports/news_overlay/prompt22/reference/runtime_matrix.csv
outputs/reports/news_overlay/prompt22/reference/leakage_audit.csv
outputs/reports/news_overlay/prompt22/reference/dependency_audit.csv
outputs/reports/news_overlay/prompt22/reference/package_safety_audit.csv
outputs/reports/news_overlay/prompt22/reference/candidate_classification.csv

docs/news_overlay/grid_search_table.md
docs/news_overlay/method_table.md
docs/news_overlay/transformer_architecture_table.md
docs/implementation_logs/<timestamp>_prompt22_train_tune_2024_frozen_2025_matrix.md
```

Keep Markdown concise. The full matrices must be CSV.

---

## Do Not Do

```text
- Do not tune on 2025.
- Do not use proxy rows as final evidence.
- Do not promote automatically.
- Do not modify frozen official runtime configs.
- Do not download models.
- Do not include model binaries in output packages.
- Do not report only one candidate per track.
- Do not hide failed/blocked tuning rows.
- Do not claim CUDA benefit unless runtime_matrix shows speedup.
```

---

## Final Response Format

```text
Prompt22 status:
  <pass/partial/fail>

RTK status:
  <available/unavailable; commands used>

Behaviour fixes:
  <summary>

2024 train/tune matrix:
  rows_total=<n>
  rows_passed=<n>
  rows_failed_or_blocked=<n>
  matrix_csv=<path>

Top Track A 2024 frozen candidates:
  1. <run_id / method stack / frozen params / score>
  2. <run_id / method stack / frozen params / score>
  3. <run_id / method stack / frozen params / score>
  4. <optional>
  5. <optional>

Top Track B 2024 frozen candidates:
  1. <run_id / method stack / frozen params / score>
  2. <run_id / method stack / frozen params / score>
  3. <run_id / method stack / frozen params / score>
  4. <optional>
  5. <optional>

Frozen 2025 matrix:
  rows_total=<n>
  summary=<short summary>
  matrix_csv=<path>

Full ablation matrix:
  verdict=<pass/partial/fail>
  matrix_csv=<path>

Runtime matrix:
  cuda_speedup=<yes/no/inconclusive>
  best_mode=<...>
  runtime_csv=<path>

Audit:
  leakage=<pass/partial/fail>
  dependency=<pass/partial/fail>
  package_safety=<pass/partial/fail>

Promotion recommendation:
  <reject/research_continue/ablation_supported/frozen_2025_supported/parity_ready_but_human_review_required>

Official runtime changed?
  <yes/no>

Tests/checks run:
  <commands and pass/fail>

Main artifacts:
  <key paths>

Next action:
  <specific recommendation>
```
