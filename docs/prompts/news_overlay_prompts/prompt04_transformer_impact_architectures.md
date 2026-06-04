# Prompt04 — Implement Transformer Impact Architectures

    ## Role

    You are a senior event-driven finance researcher, transformer signal engineer, Chinese financial NLP architect, and leakage-control reviewer.

    ## Instructions

    Implement Substage I methods. Deterministic magnitude is only fallback; the primary target is to convert transformer-derived relevance, aspect tone, label attention, and news attention into impact signals.

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


    ## Read-First Discovery Protocol

Do not blindly assume fixed file paths. First discover the repository structure, then read the latest equivalent files.

Prioritise these categories:

```text
1. current official runtime configs and preserved candidate configs;
2. Prompt20 current-state dossier and preserved-candidate summary;
3. Prompt0B / Prompt01–Prompt11 News Overlay design notes if present;
4. existing Stage 1 news-processing code;
5. existing Stage 2 text-store code;
6. existing Stage 3/4 trading and execution code;
7. existing official-semantics backtester and target-tensor tools;
8. existing scripts, tests, config conventions, and implementation-log utility.
```

Minimum items or equivalents to locate:

```text
AGENTS.md
README.md
docs/
docs/news_overlay/ if present
outputs/reports/prompt20/presented/current_repo_status_report.md
outputs/reports/prompt20/presented/preserved_candidate_summary.md
outputs/reports/prompt20/presented/next_stage_news_text_overlay_workflow.md
configs/preserved_candidates/
configs/prompt18_final_candidates.json
src/nlpcc/
src/tools/backtesting/
src/tools/experiments/
tests/
```

If a file is missing, use the nearest current equivalent and record the substitution in the progress report.




    ## Tasks

    ### Architecture Target
Substage I answers how important, directional, novel, persistent, and reliable each news event is. It emits impact features and gates, not final portfolio weights.

### I0/I1 Controls
Implement zero-impact and deterministic event magnitude as controls/fallback.

### I2 — PT-NAI
Compute a permutation-testable News Attention Index:
```text
NAI[t,j] = sum_i Impact_i * Relevance[i,j] * Direction[i,j] * Confidence[i,j]
```
Include tone, attention, dispersion, relevance, duplicate adjustment, shuffled-news hooks, and random-label hooks.

### I3 — Event-Study Calibrated Impact
Estimate event-class impact using 2024 only. Compute AR/CAR/CAAR or robust equivalents and write provenance for lookup tables.

### I4 — Decay-Weighted Event Persistence
Implement novelty windows, repeated-event dampening, and policy-theme persistence.

### I5 — Impact-Gated Attention Pooling
Compute attention over news items, gated by confidence/novelty/relevance. Output per-news attention weights and impact contribution.

### I6 — Transformer Aspect-Impact Aggregator
Consume N3 aspect-tone outputs:
```text
aspect_impact[i,j] = sum_a aspect_weight[a,j] * (P_positive[i,a] - P_negative[i,a]) * relevance[i,j]
```

### I7 — Temporal Narrative Impact Encoder
Consume lagged NAI/aspect/attention signals and output narrative impact and persistence diagnostics.

### Composite Methods
Implement I23 and I256 with component-level traceability.

### Required Tests
Test zero signal, synthetic NAI, shuffled-news hooks, 2025 calibration refusal, monotone decay, attention weights, aspect-impact sensitivity, short-history handling, and composite traces.


    ## Examples

    Input:
```text
event_type = monetary_easing
relevance(bank_sector) = high
aspect_tone(policy_support) = positive
novelty = high
```
Expected output:
```text
positive impact for bank/brokerage/broad market;
trace records whether the score came from aspect tone, attention, or event-study calibration.
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
Substage I status: <pass/partial/fail>
Transformer-impact methods implemented: <list>
Blocked or deferred methods: <list with reason>
Leakage checks: <pass/partial/fail>
Tests run: <commands and pass/fail>
Updated tables: <paths>
Next prompt: prompt05_sensitivity_overlay_transformer_integration.md
```
