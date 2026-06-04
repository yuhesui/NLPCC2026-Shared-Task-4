# Prompt020 — Restart Context Compression for Transformer-First News Overlay

## Role

You are a concise technical context compressor and project handoff writer.

## Instructions

Use this prompt when the current session is becoming too long or context compression is expected. Do not implement methods or run tests. Produce a compact restart packet that lets a new session continue safely.

## Context

You are working on the next-stage **News Overlay** phase for the NLPCC 2026 Shared Task 4 repository.

Project:

```text
NLPCC 2026 Shared Task 4:
LLM-based Investment Advisor Agents for Asset Allocation in the Chinese Market
```

Tracks:

```text
Track A / Track 1: Macro-Asset Allocation
Track B / Track 2: Sector-Rotation Allocation
```

Frozen official runtime must remain unchanged unless a later human-approved promotion prompt explicitly reopens it:

```text
Track A primary:   p18_rp_macro_w10_s5
Track A fallback:  p18_rp_macro_w40_s5
Track B primary:   p18_leeqa_sector_k5_temp35
Track B fallback:  p18_s1_sector_t35_v30_w20
```

This prompt set has two sections:

```text
Section 1: implement methods and integrate them into the pipeline.
Section 2: test methods, run grid pipelines, run ablations, verify/fix, and cross-check.
```

This stage is **transformer-first**. Deterministic methods remain required, but only as fallback, baseline, sanity-control, and ablation methods.


## Tasks

### Part A — Locate Latest State
Find the latest method table, transformer status table, grid status table, presented reports, reference reports, error logs, and implementation logs. Use equivalents if exact paths differ.

### Part B — Write Restart Files
Write:

```text
docs/news_overlay/restart_context.md
outputs/reports/news_overlay/prompt01_11/reference/current_method_status.csv
outputs/reports/news_overlay/prompt01_11/reference/current_transformer_status.csv
outputs/reports/news_overlay/prompt01_11/reference/current_grid_status.csv
outputs/reports/news_overlay/prompt01_11/reference/open_errors.md
outputs/reports/news_overlay/prompt01_11/reference/next_prompt_recommendation.md
```

### Part C — Required Restart Context Structure
Use exactly:

```md
# News Overlay Restart Context — Transformer-First Stage

## 1. Current State
## 2. Frozen Constraints
## 3. Implemented Transformer Methods
## 4. Scaffold-Only / Blocked Transformer Methods
## 5. Deterministic Fallback Status
## 6. Cache / GPU / Dependency Status
## 7. Grid Runs Completed
## 8. Best Current Candidates
## 9. Ablation and Leakage Status
## 10. Open Errors
## 11. Files to Read First in New Session
## 12. Exact Next Prompt to Run
## 13. One-Paragraph Executive Summary
```

## Examples

```text
N2 and N3 are implemented with offline cache and CPU fallback.
N4 is scaffold-only and requires label-description implementation.
G12B has not been run because N5 attention pooling is failing trace validation.
The next prompt should be prompt09_verify_fix_transformer_errors.md.
```

## Non-Negotiable Constraints

```text
- Do not change the frozen official runtime.
- Do not automatically promote a News Overlay candidate.
- Use 2024 only for construction, training, parameter selection, and threshold selection.
- Use 2025 only for frozen evaluation after 2024 selection is complete.
- Do not use hidden 2026 data.
- Do not use current-day close/high/low/return before decision time.
- Same-day news must respect the official timestamp cutoff.
- Do not use online APIs.
- Do not silently download models.
- Do not include Hugging Face or other model binaries in the official runtime package.
- Keep a deterministic no-model fallback for every transformer method.
- Do not overclaim transformer value unless ablations prove it.
- Do not use legacy or non-official-semantics backtesters for final selection evidence.
- Do not modify raw official data.
```


## Expected Output

End with:

```text
Restart packet status: <pass/partial/fail>
Restart context path: <path>
Current next prompt: <specific prompt filename>
Main blockers: <list or none>
```
