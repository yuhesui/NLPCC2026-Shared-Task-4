# Prompt10 — External Cross-Check of Transformer-First News Overlay

    ## Role

    You are an independent transformer systems auditor, quantitative research reviewer, leakage-control specialist, and skeptical model-risk reviewer.

    ## Instructions

    Run this prompt in a separate session. Do not trust previous claims. Verify whether transformer/attention architectures are real and whether evidence supports conclusions.

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

    ### Part A — Discover Current Artifacts
Find News Overlay docs, method tables, transformer architecture table, implementation logs, source code, configs, cache/model reports, grid results, ablation reports, dependency/leakage reports, and tests.

### Part B — Method Reality Check
For N2/N3/N4/N5/N6/N7/N8/N2345/I5/I6/I7/I256/S6/S7/S126, classify each as implemented, scaffold_only, blocked_missing_local_model, deferred_with_reason, incorrectly_claimed, or missing.

### Part C — Evidence Check
Verify registry/documentation alignment, config existence, transformer trace fields, offline-safe local model handling, cache manifests, lexical-baseline comparisons, ablations, 2025 isolation, and official runtime preservation.

### Part D — Failure-Mode Search
Identify at least 10 possible failure modes, including empty embeddings marked as success, cache key missing model revision, attention weights not normalised, 2025 leakage, transformer features not affecting weights, composite ignoring components, and shuffled-news ablation missing.

### Part E — Reports
Write cross-check summary, method reality table, findings table, required fixes, and implementation log.


    ## Examples

    Example verdict:
```text
Cross-check verdict = partial
Reason = N2/N3 are real and cached; N4/N5 are scaffold-only; G12B claims pass but trace lacks label-attention fields.
```


    ## Artifact and Reporting Policy

Use this report tree unless the repository already has a compatible News Overlay report structure:

```text
outputs/reports/news_overlay/prompt01_11/
  README.md
  progress/
  presented/
  reference/
```

Required core artifacts:

```text
outputs/reports/news_overlay/prompt01_11/reference/method_implementation_table.csv
outputs/reports/news_overlay/prompt01_11/reference/transformer_method_status.csv
outputs/reports/news_overlay/prompt01_11/reference/grid_search_status_table.csv
outputs/reports/news_overlay/prompt01_11/reference/cache_manifest.csv
outputs/reports/news_overlay/prompt01_11/reference/model_availability_report.csv
outputs/reports/news_overlay/prompt01_11/reference/dependency_manifest.md
outputs/reports/news_overlay/prompt01_11/reference/leakage_audit.md
outputs/reports/news_overlay/prompt01_11/reference/error_log.md
```

Keep large generated files under:

```text
.var/news_overlay_prompt01_11/
  cache/
  target_tensors/
  grid_runs/
  checkpoints/
  benchmarks/
  logs/
```

Create an implementation log for every prompt:

```text
docs/implementation_logs/<timestamp>_news_overlay_prompt01_11_<short_name>.md
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
Cross-check verdict: <pass/partial/fail>
Transformer implementation reality: <implemented/partial/scaffold_only/blocked/misrepresented>
Critical issues: <list or none>
Medium issues: <list or none>
Required next action: <prompt09_fix / further_tests / ready_for_human_review>
```
