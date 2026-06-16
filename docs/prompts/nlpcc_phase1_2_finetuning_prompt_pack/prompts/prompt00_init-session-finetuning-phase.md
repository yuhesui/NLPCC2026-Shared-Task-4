# prompt00_init-session-finetuning-phase.md

## Model Setting

Use **GPT-5.5 High** in Codex.

## Role

You are GPT-5.5 High in a fresh Codex session acting as:

```text
senior research-code initialisation engineer
NLPCC repo-state auditor
Chinese financial NLP workflow planner
fine-tuning experiment safety engineer
single implementation-log writer
```

## Objective

Initialise the next fine-tuning/retrieval/calibration phase for the NLPCC 2026 Shared Task 4 project without changing modelling code.

This is a setup and evidence-intake prompt, not an experiment prompt.

You must prepare the workspace for:

```text
Phase 1:
  no-training retrieval, clustering, calibration, and shallow fusion baselines

Phase 2:
  contrastive BGE relevance fine-tuning and small event/aspect head fine-tuning
```

## Current Candidate Policy

Do not reopen candidate selection.

```text
Track A selected news candidate:
  A2_real / G11A / compact N13/I6/S13 real-transformer news overlay

Track B selected news candidate:
  B2_real / G15B / compact N4/I6/S2 real-transformer news overlay

Reference-only controls:
  A0 / B0 no-news baselines
```

A0/B0 are benchmarks and fallback references only. They are not final selected news candidates in this phase.

## Required Read Order

Read these before doing anything:

```text
AGENTS.md
README.md
docs/REPO_STRUCTURE.md if present
docs/workflow/PROMPT_EXECUTION_PLAN.md if present
docs/news_overlay/**
docs/context/**
docs/architecture/**
docs/strategy/**
NLPCC_tasks/**
src/**
tests/**
outputs/reports/focused_candidate_optimisation/prompt09_real_transformer_news_overlay/**
outputs/reports/focused_candidate_optimisation/prompt10_final_candidate_methodology_audit/**
outputs/reports/focused_candidate_optimisation/prompt10a_final_candidate_evidence_repair/**
outputs/reports/focused_candidate_optimisation/prompt11_final_news_candidate_cleanup_official_run/**
outputs/reports/focused_candidate_optimisation/prompt11_final_news_candidate_cleanup_official_run/fine_tuning_plan/**
```

If some files/folders are missing, record the missing evidence. Do not guess.

## Phase Root

Use:

```text
outputs/reports/focused_candidate_optimisation/next_phase_finetuning_phase12/prompt00_init_session/
```

Create:

```text
presented/
presented/run_csv/
reference/
logs/
repo_audit/
config/
tests/
```

## Presented Folder Rule

The `presented/` folder must be dense and monitorable.

Create exactly:

```text
presented/implementation_log.md
presented/progress_dashboard.md
presented/essential_results.md
presented/blockers_and_decisions.md
presented/run_csv_manifest.csv
presented/run_csv/
```

Avoid small fragmented Markdown files inside `presented/`.

## Hard Rules

```text
Use rtk, rtk python, rtk git.
No hidden 2026.
No online inference/API.
No model download.
No training.
No retuning.
No broad candidate search.
No proxy/fake news runs.
No heuristic fallback in production candidate path.
No fixed target replay as news.
No stale summary reuse.
```

## Work Items

### 1. Repo and phase inventory

Create:

```text
repo_audit/repo_phase_intake_manifest.csv
repo_audit/current_candidate_file_map.csv
repo_audit/current_model_asset_expectation.csv
reference/phase12_scaffold_manifest.csv
```

The manifest must identify:

```text
A2_real source/config path
B2_real source/config path
A0/B0 reference path
real transformer tensor provider path
official agent adapter path
BGE model config/path if present
FinBERT model config/path if present
reranker config/path if present
prior Prompt11 official result CSVs
prior fine_tuning_plan files
```

### 2. Create phase scaffold

Prepare empty directories for Prompt01–05:

```text
prompt01_data_label_audit_frozen_splits/
prompt02_phase1_retrieval_calibration_fusion/
prompt03_phase2_contrastive_bge/
prompt04_phase2_event_aspect_lora/
prompt05_frozen_eval_ablation_report/
```

Each should contain a placeholder `presented/README.placeholder.md` explaining that actual prompts will populate it.

### 3. Environment smoke only

Run:

```bash
rtk --version
rtk python -c "import sys, torch; print(sys.executable); print(torch.__version__); print(torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu')"
rtk git status --short
```

Do not run training.

Create:

```text
reference/environment_smoke.csv
logs/environment_smoke.log
```

### 4. Phase governance

Create:

```text
config/phase12_governance.yaml
config/phase12_allowed_methods.csv
config/phase12_stop_rules.csv
```

Allowed methods:

```text
calibration-only
frozen encoder + shallow heads
retrieval/clustering feature augmentation
shallow fusion
BGE-small contrastive fine-tuning
weak event/aspect head training
LoRA only after label audit passes
```

Disallowed unless later human-approved:

```text
full RLHF
RLAIF
large generative SFT
QLoRA on large LLMs
TAPT/DAPT with unclear corpus provenance
online RAG
hidden 2026 use
2025 tuning
unbounded overlay amplification
```

## Required Output Files

```text
presented/implementation_log.md
presented/progress_dashboard.md
presented/essential_results.md
presented/blockers_and_decisions.md
presented/run_csv_manifest.csv

repo_audit/repo_phase_intake_manifest.csv
repo_audit/current_candidate_file_map.csv
repo_audit/current_model_asset_expectation.csv
reference/phase12_scaffold_manifest.csv
reference/environment_smoke.csv
config/phase12_governance.yaml
config/phase12_allowed_methods.csv
config/phase12_stop_rules.csv
logs/environment_smoke.log
```

## Implementation Log Sections

```text
A. Summary
B. Files Read
C. Files Created
D. Commands Run
E. Candidate Policy Confirmed
F. Environment Smoke
G. Phase Scaffold
H. Missing Evidence
I. Hidden 2026 / Leakage Check
J. Caveats
K. Next Prompt
```

## Final Response Format

```text
Prompt00 status:
  <pass/partial/fail/blocked>

Phase root:
  <path>

Implementation log:
  <path>
  count: <1/other>

Candidate policy:
  Track A selected news candidate: A2_real / G11A
  Track B selected news candidate: B2_real / G15B
  A0/B0 role: reference_only

Environment:
  rtk python: <path>
  cuda available: <yes/no>
  gpu: <name/cpu>
  local hardware class: <6GB_4050 / other / unknown>

Phase scaffold:
  status: <complete/partial/fail>
  next prompt: prompt01_data-label-audit-frozen-splits.md

Missing evidence:
  <list>

Hidden 2026 used?
  no

Best next action:
  Run prompt01_data-label-audit-frozen-splits.md
```
