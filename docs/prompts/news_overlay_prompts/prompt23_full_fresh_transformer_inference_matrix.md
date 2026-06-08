# Prompt23 — Full Fresh Transformer-Inference Matrix Replay

## Role

You are a senior quantitative research runner, transformer systems engineer, CUDA/GPU execution engineer, Chinese financial NLP engineer, and model-risk auditor.

You are continuing after Prompt22. Prompt22 produced a 2024 train/tune matrix, frozen 2025 matrix, ablation matrix, and candidate classifications, but it replayed Prompt21 real-local transformer target checkpoints rather than rerunning full transformer inference for every tune row.

Prompt23 is intentionally simple: rerun the full Prompt22 candidate/tuning matrix with **fresh real-local transformer inference per row** to verify that the cached/checkpoint replay conclusions are valid.

---

## Goal

Run the complete Prompt22 2024 train/tune matrix again, but this time with fresh local transformer inference for every tune row.

The goal is complete only if it produces:

```text
1. full 2024 matrix with fresh transformer inference per row;
2. side-by-side comparison against Prompt22 cached/checkpoint replay results;
3. 3–5 frozen candidates per track selected from fresh 2024 results only;
4. frozen 2025 matrix for those candidates;
5. candidate-vs-control deltas;
6. cache/inference audit proving no target-weight replay was used;
7. clear verdict on whether Prompt22 replay results are confirmed, revised, or invalidated.
```

---

## Key Rule

Do **not** reuse Prompt21/Prompt22 cached target weights or completed candidate outputs as the source of truth.

Allowed caches:

```text
- Hugging Face model files;
- tokenizer files;
- raw model weights;
- raw immutable input files;
- optional tokenization cache if it is independent of method/tune output;
- low-level embedding cache only if it is keyed by:
    model id,
    snapshot/revision,
    date,
    news text hash,
    preprocessing version,
    method code,
    and is regenerated/validated within Prompt23.
```

Forbidden caches:

```text
- Prompt21 target-weight checkpoints;
- Prompt22 train/tune candidate result replay;
- precomputed final overlay deltas;
- precomputed final target weights;
- precomputed candidate metrics;
- any cache that bypasses N/I/S method execution for the tune row.
```

If any cache is reused, document exactly why it is safe. If unsure, invalidate and regenerate.

---

## Scope

Run all Prompt22 candidate families and tune rows.

Minimum candidate families:

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

Use the same Prompt22 tune dimensions unless the repo has an exact Prompt22 matrix config:

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
```

If Prompt22 already saved the exact matrix rows, use the same row list.

---

## Output Directory

Store all outputs under:

```text
outputs/reports/news_overlay/prompt23/presented/
outputs/reports/news_overlay/prompt23/reference/
outputs/reports/news_overlay/prompt23/progress/
```

Do not write Prompt23 primary outputs into `prompt21`, `prompt22`, or `prompt01_11`.

---

## Non-Negotiable Constraints

```text
- Do not modify frozen official runtime configs.
- Use 2024 only for train/tune/selection.
- Use 2025 only after 2024 candidates are frozen.
- Do not use hidden 2026 data.
- Do not use current-day close/high/low/return before decision time.
- Same-day news must obey official timestamp cutoff.
- Use local-only Hugging Face model loading.
- Do not download models.
- Do not call online APIs.
- Do not copy model binaries into repo/package outputs.
- Do not promote automatically.
- Do not report only one candidate per track.
```

---

## Section 1 — Preflight and Cache Invalidation

Before running the matrix:

```text
1. verify local-only model availability;
2. verify BGE / FinBERT / reranker local loading;
3. verify official runtime diff is clean;
4. identify Prompt21/Prompt22 target-weight or candidate-output caches;
5. disable or invalidate forbidden caches;
6. create Prompt23 cache namespace;
7. write cache policy report.
```

Required output:

```text
outputs/reports/news_overlay/prompt23/reference/cache_policy_audit.csv
outputs/reports/news_overlay/prompt23/presented/cache_policy_summary.md
```

---

## Section 2 — Full Fresh 2024 Transformer Matrix

Run the full 2024 matrix with fresh N/I/S execution for every row.

Each row must execute:

```text
N-stage:
  actual local model feature extraction / relevance / attention / label logic

I-stage:
  impact / aspect-impact / attention-impact logic

S-stage:
  sensitivity / overlay / bounded target-weight generation

Backtest:
  official-semantics or existing validated local replay
```

Every row must record:

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
model_mode
fresh_inference=true/false
forbidden_cache_used=true/false
cache_namespace
runtime_sec
device
batch_size
gpu_util_mean
gpu_util_peak
vram_peak_mb
return
sharpe
max_drawdown
turnover
active_news_days
active_transformer_days
mean_abs_overlay
max_abs_overlay
selection_score
warnings
```

Required output:

```text
outputs/reports/news_overlay/prompt23/reference/full_fresh_2024_matrix.csv
outputs/reports/news_overlay/prompt23/reference/trackA_fresh_2024_ranking.csv
outputs/reports/news_overlay/prompt23/reference/trackB_fresh_2024_ranking.csv
outputs/reports/news_overlay/prompt23/presented/full_fresh_2024_summary.md
```

The presented summary must include top 3–5 candidates per track.

---

## Section 3 — Prompt22 Replay Equivalence Check

Compare Prompt23 fresh-inference results with Prompt22 cached/replay results.

Join by:

```text
track
candidate_family
method_stack
overlay_strength
impact_threshold
confidence_threshold
sensitivity_threshold
turnover_cap
drawdown_throttle
```

Compute:

```text
delta_return
delta_sharpe
delta_max_drawdown
delta_turnover
delta_selection_score
same_rank_bucket
equivalence_verdict
```

Verdicts:

```text
confirmed
minor_numeric_drift
material_difference
missing_prompt22_row
missing_prompt23_row
```

Required output:

```text
outputs/reports/news_overlay/prompt23/reference/prompt22_vs_prompt23_equivalence.csv
outputs/reports/news_overlay/prompt23/presented/prompt22_vs_prompt23_equivalence_summary.md
```

If material differences appear, use Prompt23 fresh-inference results as the source of truth.

---

## Section 4 — 2024 Candidate Freeze

Freeze 3–5 candidates per track using Prompt23 fresh 2024 results only.

Required output:

```text
outputs/reports/news_overlay/prompt23/reference/selection_freeze_2024.csv
outputs/reports/news_overlay/prompt23/presented/selection_freeze_2024.md
```

Presented freeze must include:

```text
- top 3–5 Track A candidates;
- top 3–5 Track B candidates;
- exact frozen parameters;
- candidate-vs-control 2024 deltas;
- whether each candidate confirms or changes Prompt22 ranking.
```

Do not inspect Prompt23 2025 results before writing the freeze.

---

## Section 5 — Frozen 2025 Matrix

After the Prompt23 2024 freeze file is written, run frozen 2025 evaluation.

Allowed rows:

```text
- preserved controls;
- lexical controls;
- frozen top 3–5 Track A candidates;
- frozen top 3–5 Track B candidates.
```

Forbidden:

```text
- tuning thresholds on 2025;
- selecting new candidates from 2025;
- changing candidate order based on 2025 except in a labelled diagnostic table.
```

Required output:

```text
outputs/reports/news_overlay/prompt23/reference/frozen_2025_matrix.csv
outputs/reports/news_overlay/prompt23/reference/frozen_2025_candidate_vs_control_deltas.csv
outputs/reports/news_overlay/prompt23/presented/frozen_2025_summary.md
```

The presented summary must show controls and 3–5 candidates per track.

---

## Section 6 — Audit

Audit and report:

```text
- no forbidden cache use;
- full fresh inference per tune row;
- no 2025 tuning;
- no official runtime change;
- no hidden 2026 use;
- no same-day price leakage;
- news cutoff respected;
- local_files_only=True;
- no online calls;
- no model binaries copied;
- cache keys include model id/snapshot/method/preprocess/text hash;
- official-server parity not claimed unless actually run.
```

Required output:

```text
outputs/reports/news_overlay/prompt23/reference/inference_freshness_audit.csv
outputs/reports/news_overlay/prompt23/reference/leakage_audit.csv
outputs/reports/news_overlay/prompt23/reference/dependency_audit.csv
outputs/reports/news_overlay/prompt23/reference/package_safety_audit.csv
outputs/reports/news_overlay/prompt23/reference/candidate_classification.csv
outputs/reports/news_overlay/prompt23/presented/audit_summary.md
outputs/reports/news_overlay/prompt23/presented/final_recommendation.md
```

Candidate classifications:

```text
reject
research_continue
fresh_inference_confirmed
frozen_2025_supported
parity_ready_but_human_review_required
```

Do not classify as `parity_ready_but_human_review_required` unless official-server parity preparation is actually satisfactory.

---

## Section 7 — Tests and Checks

Use RTK if available:

```bash
rtk --version
rtk python -m pytest tests/test_nlpcc/test_news_overlay -q
rtk git diff
rtk git status
```

If RTK is unavailable, use standard commands and record the fallback.

Also run targeted checks for:

```text
fresh inference flag
forbidden cache blocking
2024-only selection
2025 calibration refusal
local-only model loading
official runtime diff
Prompt22-vs-Prompt23 equivalence
```

---

## Required Output Files

Create/update:

```text
outputs/reports/news_overlay/prompt23/progress/progress_prompt23.md

outputs/reports/news_overlay/prompt23/presented/cache_policy_summary.md
outputs/reports/news_overlay/prompt23/presented/full_fresh_2024_summary.md
outputs/reports/news_overlay/prompt23/presented/prompt22_vs_prompt23_equivalence_summary.md
outputs/reports/news_overlay/prompt23/presented/selection_freeze_2024.md
outputs/reports/news_overlay/prompt23/presented/frozen_2025_summary.md
outputs/reports/news_overlay/prompt23/presented/audit_summary.md
outputs/reports/news_overlay/prompt23/presented/final_recommendation.md

outputs/reports/news_overlay/prompt23/reference/cache_policy_audit.csv
outputs/reports/news_overlay/prompt23/reference/full_fresh_2024_matrix.csv
outputs/reports/news_overlay/prompt23/reference/trackA_fresh_2024_ranking.csv
outputs/reports/news_overlay/prompt23/reference/trackB_fresh_2024_ranking.csv
outputs/reports/news_overlay/prompt23/reference/prompt22_vs_prompt23_equivalence.csv
outputs/reports/news_overlay/prompt23/reference/selection_freeze_2024.csv
outputs/reports/news_overlay/prompt23/reference/frozen_2025_matrix.csv
outputs/reports/news_overlay/prompt23/reference/frozen_2025_candidate_vs_control_deltas.csv
outputs/reports/news_overlay/prompt23/reference/inference_freshness_audit.csv
outputs/reports/news_overlay/prompt23/reference/leakage_audit.csv
outputs/reports/news_overlay/prompt23/reference/dependency_audit.csv
outputs/reports/news_overlay/prompt23/reference/package_safety_audit.csv
outputs/reports/news_overlay/prompt23/reference/candidate_classification.csv

docs/implementation_logs/<timestamp>_prompt23_full_fresh_transformer_inference_matrix.md
```

Keep Markdown concise. Full matrices must be CSV.

---

## Do Not Do

```text
- Do not use Prompt21/Prompt22 target-weight checkpoints as final evidence.
- Do not tune on 2025.
- Do not use proxy rows as final evidence.
- Do not promote automatically.
- Do not modify frozen official runtime configs.
- Do not download models.
- Do not include model binaries in output packages.
- Do not report only one candidate per track.
- Do not hide failed/blocked rows.
- Do not claim official parity unless actually run.
```

---

## Final Response Format

```text
Prompt23 status:
  <pass/partial/fail>

Fresh inference:
  rows_total=<n>
  rows_passed=<n>
  forbidden_cache_used=<yes/no>
  matrix_csv=<path>

Prompt22 vs Prompt23 equivalence:
  <confirmed/minor_numeric_drift/material_difference; summary>

Top Track A frozen candidates:
  1. <run_id / method stack / frozen params / score>
  2. <run_id / method stack / frozen params / score>
  3. <run_id / method stack / frozen params / score>
  4. <optional>
  5. <optional>

Top Track B frozen candidates:
  1. <run_id / method stack / frozen params / score>
  2. <run_id / method stack / frozen params / score>
  3. <run_id / method stack / frozen params / score>
  4. <optional>
  5. <optional>

Frozen 2025 matrix:
  rows_total=<n>
  summary=<short summary>
  matrix_csv=<path>

Audit:
  freshness=<pass/partial/fail>
  leakage=<pass/partial/fail>
  dependency=<pass/partial/fail>
  package_safety=<pass/partial/fail>

Promotion recommendation:
  <reject/research_continue/fresh_inference_confirmed/frozen_2025_supported/parity_ready_but_human_review_required>

Official runtime changed?
  <yes/no>

Tests/checks run:
  <commands and pass/fail>

Main artifacts:
  <key paths>

Next action:
  <specific recommendation>
```
