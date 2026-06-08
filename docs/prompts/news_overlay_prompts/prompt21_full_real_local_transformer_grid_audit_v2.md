# Prompt21 — Full Real-Local Transformer Grid Search, CUDA Tuning, and Promotion Audit

## Role

You are a senior quantitative research runner, transformer systems engineer, CUDA/GPU optimisation engineer, Chinese financial NLP engineer, and model-risk auditor.

You are continuing in the same session after Prompt20.1. Local Hugging Face models are now available and validated in local-only mode. Prompt21 merges the old Prompt07 grid-search role and Prompt08 audit role into one full execution prompt.

This is not a design prompt. This is a full real-local model execution, grid-search, ablation, and audit prompt.

---

## Current Starting Point

Use the current repo/session state directly.

Prompt20.1 established, subject to verification from current artifacts:

```text
- N2 uses BAAI/bge-small-zh-v1.5.
- N3 uses yiyanghkust/finbert-tone-chinese.
- N4/N5 use BGE embeddings.
- N6 uses BAAI/bge-reranker-v2-m3 as a true reranker.
- N2345, I256, S126 have real local model evidence where applicable.
- N7, N8, I7, S7 may remain ablation/deferred unless configured.
```

Do not repeat long read-first discovery. Use the existing repo state, current tables, and current outputs.

---

## Goal

Run a **full real-local News Overlay transformer grid** and produce complete grid-search results, candidate rankings, ablation audit, dependency/leakage audit, and promotion recommendation.

This prompt must output:

```text
1. GPU tuning report;
2. full 2024 grid results;
3. full Track A and Track B ranking tables;
4. top 3–5 Track A candidates in presented outputs;
5. top 3–5 Track B candidates in presented outputs;
6. ablation results;
7. dependency and leakage audit;
8. frozen 2025 selected-candidate evaluation if and only if candidates are frozen from 2024;
9. final no-promotion / research-continue / parity-ready recommendation.
```

Never present only a single best candidate for either track. Each track must show **3–5 candidates** unless fewer than 3 valid candidates exist, in which case explain why.

Do not use proxy-mode rows as final evidence.

---

## Output Directory Policy

Store Prompt21 outputs under:

```text
outputs/reports/news_overlay/prompt21/presented/
outputs/reports/news_overlay/prompt21/reference/
outputs/reports/news_overlay/prompt21/progress/
```

Do **not** continue writing Prompt21 results primarily under:

```text
outputs/reports/news_overlay/prompt01_11/
```

You may read legacy `prompt01_11` artifacts, but new Prompt21 deliverables must use the new `prompt21` folder.

Use `reference/` for machine-readable full results and `presented/` for concise human-facing summaries and important result extracts.

Important results must appear in `presented/` even if the full CSV is in `reference/`.

If a CSV is already clear enough, do not generate a redundant long Markdown report. Instead, create a compact presented Markdown file that points to the CSV and summarises only the key results, candidate list, and verdict.

---

## Non-Negotiable Constraints

```text
- Do not change frozen official runtime configs.
- Do not tune on 2025.
- Do not use hidden 2026 data.
- Do not use current-day close/high/low/return before decision time.
- Same-day news must obey official timestamp cutoff.
- Use local-only model loading after Prompt20.1.
- Do not download models in this prompt.
- Do not call online APIs.
- Do not copy model binaries into repo/package outputs.
- Do not promote any candidate automatically.
- If 2025 is run, it must use frozen 2024-selected configs only.
```

---

## Section 1 — GPU / CUDA Tuning Before Full Grid

Before running the full grid, add or run a simple GPU tuning program.

### Target hardware

Assume laptop GPU:

```text
NVIDIA RTX 4050 laptop GPU
```

### Utilisation target

Aim for:

```text
preferred target:
  peak GPU utilisation >80% during embedding/reranker batches

fallback realistic target:
  sustained GPU utilisation >50-60% if small models, CPU bottlenecks, or data I/O prevent >80%
```

Do not fake GPU usage. If >80% is not realistic, report the bottleneck.

### Required tuning dimensions

Sweep a compact set of settings:

```text
batch_size:
  8, 16, 32, 64, 128

max_length:
  128, 256

precision:
  fp32, fp16/autocast if supported

num_cpu_workers:
  0, 2, 4

cache_mode:
  cold_cache, warm_cache

model mix:
  BGE only
  FinBERT only
  BGE + FinBERT
  BGE reranker
```

Avoid OOM. If OOM occurs, record it and back off.

### Required GPU tuning outputs

Create:

```text
outputs/reports/news_overlay/prompt21/reference/gpu_tuning_results.csv
outputs/reports/news_overlay/prompt21/presented/gpu_tuning_summary.md
```

Minimum CSV columns:

```text
setting_id
model_role
batch_size
max_length
precision
num_cpu_workers
device
gpu_name
peak_gpu_util_pct
mean_gpu_util_pct
peak_vram_mb
mean_vram_mb
elapsed_sec
items_per_sec
oom
selected_for_grid
notes
```

Use any available profiler:

```text
- nvidia-smi query loop;
- pynvml if available;
- torch.cuda memory stats;
- existing repo runtime profiler.
```

If `nvidia-smi` or `pynvml` is unavailable, record the missing profiler and still report timing/VRAM via PyTorch.

### Grid execution acceleration policy

After tuning:

```text
- prebuild model caches in large batches;
- keep transformer inference on one GPU process where possible;
- parallelise CPU post-processing / grid scoring separately;
- avoid loading multiple copies of the same model into GPU memory unless tested safe;
- use warm cache for repeated ablation/grid passes;
- use checkpoint/resume so interruption does not lose results.
```

---

## Section 2 — Full Grid Definition

Run the full configured News Overlay grid, not only smoke rows.

At minimum include:

```text
Controls:
  G00A, G00B, G01A, G01B

Track A real-local transformer rows:
  G10A, G11A, G12A

Track B real-local transformer rows:
  G10B, G11B, G12B, G13B, G14B, G15B

Higher-capacity / second-stage rows:
  G20B, G21B

Ablation/deferred rows if configured:
  G22B, G23B

Any additional rows already defined in:
  configs/news_overlay/grids/mandatory_core_grid.csv
  configs/news_overlay/grids/transformer_core_grid.csv
  configs/news_overlay/grids/transformer_ablation_grid.csv
  configs/news_overlay/grids/transformer_asset_smoke_grid.csv
```

Deduplicate by:

```text
track + N method + I method + S method + base config + ablation flag
```

---

## Section 3 — 2024 Full Grid Execution

Run the full grid on 2024 only for construction/selection.

Required:

```text
- local-only models;
- no proxy mode for primary evidence;
- checkpointed runs;
- resume support;
- per-run traces;
- full ranking table;
- failed/blocked row report;
- cache hit/miss report;
- GPU utilisation report attached to run.
```

Metrics required for every row:

```text
run_id
track
base_config
n_method
i_method
s_method
model_mode
status
dates_run
runtime_sec
device
batch_size
gpu_util_mean
gpu_util_peak
vram_peak_mb
cache_hit_rate
return
sharpe
max_drawdown
turnover
active_news_days
active_transformer_days
mean_abs_overlay
max_abs_overlay
gate_activation_count
fallback_rate
warnings
```

Create:

```text
outputs/reports/news_overlay/prompt21/reference/full_grid_2024_results.csv
outputs/reports/news_overlay/prompt21/reference/trackA_2024_ranking.csv
outputs/reports/news_overlay/prompt21/reference/trackB_2024_ranking.csv
outputs/reports/news_overlay/prompt21/presented/full_grid_2024_summary.md
```

The presented summary must include:

```text
- total rows;
- passed rows;
- failed/blocked rows;
- top 3–5 Track A candidates;
- top 3–5 Track B candidates;
- key caveats;
- link/path to full CSVs.
```

---

## Section 4 — 2024 Selection Freeze

Select candidates using 2024 only.

Recommended conservative score:

```text
score =
  0.35 * sharpe_rank
+ 0.20 * cumulative_return_rank
+ 0.20 * max_drawdown_rank
+ 0.15 * turnover_rank
+ 0.10 * ablation_quality_rank
```

If the repo already has a better official-style composite, report both.

Freeze candidate sets, not single candidates:

```text
Track A:
  top 3–5 candidates

Track B:
  top 3–5 candidates
```

The first candidate may be labelled primary, but never report only one candidate.

Create:

```text
outputs/reports/news_overlay/prompt21/reference/selection_freeze_2024.csv
outputs/reports/news_overlay/prompt21/presented/selection_freeze_2024.md
```

The presented freeze file must include both Track A and Track B top 3–5 candidate tables.

Do not look at 2025 before freezing.

---

## Section 5 — Full Ablation Suite

Run ablations for frozen candidate sets and key controls.

Required ablations:

```text
base only
real news
zero-news
shuffled-news dates
randomised event labels
random embeddings or random transformer features
lexical-only relevance
dense-only relevance
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

If any ablation is not implemented, implement it or mark it `not_run_with_reason`.

Create:

```text
outputs/reports/news_overlay/prompt21/reference/ablation_results.csv
outputs/reports/news_overlay/prompt21/presented/ablation_summary.md
```

The presented ablation summary must include:

```text
- Track A top 3–5 candidate ablation verdicts;
- Track B top 3–5 candidate ablation verdicts;
- which ablations passed;
- which ablations failed;
- which are not run with reason.
```

Minimum verdicts:

```text
pass
partial
fail
not_run_with_reason
```

---

## Section 6 — Frozen 2025 Evaluation

Only after 2024 candidate freeze, evaluate frozen selected candidate sets on 2025.

Allowed:

```text
- preserved base controls;
- frozen Track A top 3–5 candidates;
- frozen Track B top 3–5 candidates.
```

Forbidden:

```text
- changing thresholds after seeing 2025;
- selecting a new candidate from 2025;
- changing model/hyperparameters from 2025 results.
```

Create:

```text
outputs/reports/news_overlay/prompt21/reference/frozen_2025_results.csv
outputs/reports/news_overlay/prompt21/presented/frozen_2025_summary.md
```

The presented 2025 summary must include Track A and Track B top 3–5 candidate results, not only the primary.

---

## Section 7 — Dependency / Leakage / Package Audit

Audit:

```text
- no online calls during local-only grid;
- local_files_only=True;
- no model binaries copied into repo/package outputs;
- official runtime configs unchanged;
- no 2025 tuning;
- same-day news cutoff respected;
- current-day price leakage absent;
- cache keys include model id / snapshot / method / preprocessing / text hash;
- fallback/proxy rows not counted as real model evidence;
- GPU settings recorded and reproducible.
```

Create:

```text
outputs/reports/news_overlay/prompt21/reference/dependency_audit.csv
outputs/reports/news_overlay/prompt21/reference/leakage_audit.csv
outputs/reports/news_overlay/prompt21/reference/package_safety_audit.csv
outputs/reports/news_overlay/prompt21/presented/audit_summary.md
```

If the CSVs are clear and complete, keep `audit_summary.md` short.

---

## Section 8 — Promotion Gate

Classify each candidate as one of:

```text
reject
research_continue
ablation_supported
frozen_2025_supported
parity_ready_but_human_review_required
```

Classify all Track A and Track B top 3–5 candidates.

Do not mark `parity_ready_but_human_review_required` unless:

```text
1. selected on 2024 only;
2. frozen 2025 improves over preserved baseline;
3. shuffled-news and zero-news ablations behave correctly;
4. drawdown and turnover are acceptable;
5. dependency footprint is acceptable;
6. local official-semantics replay passes;
7. official-server parity is planned or passed;
8. human approval remains required.
```

If official-server parity is not run, state clearly:

```text
not promotion-ready
```

Create:

```text
outputs/reports/news_overlay/prompt21/reference/candidate_classification.csv
outputs/reports/news_overlay/prompt21/reference/promotion_gate_audit.csv
outputs/reports/news_overlay/prompt21/presented/final_recommendation.md
```

The final recommendation must include:

```text
- top 3–5 Track A candidate classifications;
- top 3–5 Track B candidate classifications;
- no single-candidate-only conclusion;
- exact next action.
```

---

## Required Tests

Before final response, run:

```text
pytest tests/test_nlpcc/test_news_overlay -q
```

Also run targeted tests or smoke commands for:

```text
model availability local-only
cache warm/cold behaviour
grid resume/checkpoint
GPU tuning script
ablation controls
2025 calibration refusal
official runtime diff
```

---

## Required Output Files

Create/update under the new Prompt21 report directory:

```text
outputs/reports/news_overlay/prompt21/progress/progress_full_transformer_grid_audit.md

outputs/reports/news_overlay/prompt21/presented/gpu_tuning_summary.md
outputs/reports/news_overlay/prompt21/presented/full_grid_2024_summary.md
outputs/reports/news_overlay/prompt21/presented/selection_freeze_2024.md
outputs/reports/news_overlay/prompt21/presented/ablation_summary.md
outputs/reports/news_overlay/prompt21/presented/frozen_2025_summary.md
outputs/reports/news_overlay/prompt21/presented/audit_summary.md
outputs/reports/news_overlay/prompt21/presented/final_recommendation.md

outputs/reports/news_overlay/prompt21/reference/gpu_tuning_results.csv
outputs/reports/news_overlay/prompt21/reference/full_grid_2024_results.csv
outputs/reports/news_overlay/prompt21/reference/trackA_2024_ranking.csv
outputs/reports/news_overlay/prompt21/reference/trackB_2024_ranking.csv
outputs/reports/news_overlay/prompt21/reference/selection_freeze_2024.csv
outputs/reports/news_overlay/prompt21/reference/ablation_results.csv
outputs/reports/news_overlay/prompt21/reference/frozen_2025_results.csv
outputs/reports/news_overlay/prompt21/reference/dependency_audit.csv
outputs/reports/news_overlay/prompt21/reference/leakage_audit.csv
outputs/reports/news_overlay/prompt21/reference/package_safety_audit.csv
outputs/reports/news_overlay/prompt21/reference/candidate_classification.csv
outputs/reports/news_overlay/prompt21/reference/promotion_gate_audit.csv

docs/news_overlay/grid_search_table.md
docs/news_overlay/method_table.md
docs/news_overlay/transformer_architecture_table.md
docs/implementation_logs/<timestamp>_prompt21_full_real_local_transformer_grid_audit.md
```

Keep Markdown summaries concise. The full grid must be in CSV. Important candidate tables must also be copied or summarised in `presented/`.

---

## Do Not Do

```text
- Do not use proxy-mode rows as final evidence.
- Do not tune on 2025.
- Do not promote automatically.
- Do not modify frozen official runtime configs.
- Do not download models.
- Do not include model binaries in output packages.
- Do not claim CUDA >80% if the measurement does not show it.
- Do not hide failed/blocked grid rows.
- Do not present only one candidate per track.
```

---

## Final Response Format

```text
Prompt21 status:
  <pass/partial/fail>

GPU tuning:
  selected_config=<...>
  peak_util=<...>
  mean_util=<...>
  vram_peak=<...>
  target_met=<yes/no, reason>

Full 2024 grid:
  rows_total=<n>
  rows_passed=<n>
  rows_failed_or_blocked=<n>
  result_csv=<path>

Top Track A 2024 candidates:
  1. <run_id / method stack / score>
  2. <run_id / method stack / score>
  3. <run_id / method stack / score>
  4. <optional>
  5. <optional>

Top Track B 2024 candidates:
  1. <run_id / method stack / score>
  2. <run_id / method stack / score>
  3. <run_id / method stack / score>
  4. <optional>
  5. <optional>

Frozen 2025 evaluation:
  <run/not_run; summary for top 3–5 candidates per track>

Ablation verdict:
  <pass/partial/fail; summary>

Dependency/leakage audit:
  <pass/partial/fail; summary>

Promotion recommendation:
  <reject/research_continue/ablation_supported/frozen_2025_supported/parity_ready_but_human_review_required>

Official runtime changed?
  <yes/no>

Tests run:
  <commands and pass/fail>

Main artifacts:
  <list key CSV/MD paths>

Next action:
  <specific recommendation>
```
