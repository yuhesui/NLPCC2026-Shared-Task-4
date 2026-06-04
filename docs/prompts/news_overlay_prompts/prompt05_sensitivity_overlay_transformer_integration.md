# Prompt05 — Implement Sensitivity, Gates, and Transformer-Aware Overlays

    ## Role

    You are a senior quantitative portfolio engineer, event-study researcher, transformer-signal validation specialist, and official-semantics risk-control reviewer.

    ## Instructions

    Implement Substage S methods that estimate ETF/sector sensitivity to news and translate validated news signals into bounded overlays. Transformer outputs may inform decisions but must not become an unconstrained allocator.

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
Substage S answers whether an ETF/sector historically reacts to an event type, whether news ranks sectors better than chance, and how large a bounded overlay may be.

### S1 — CAR/CAAR Event-Study Sensitivity
Use 2024 only to estimate event-class × asset/sector response:
```text
AR[j,t] = R[j,t] - expected_return[j,t]
CAR[j,event] = sum_tau AR[j,tau]
Sens[j,c] = shrink(robust_mean(CAR[j,event_type=c]))
```

### S2 — Rank-IC Gated Sector News Momentum
For Track B, compute Rank-IC between news-score ranks and future sector returns. Estimate thresholds on 2024 only.

### S3 — Volatility-Scaled Macro News Risk Gate
For Track A, scale risky exposure through bounded macro/news risk multipliers. Avoid directional overtrading.

### S4/S5 — Higher-Capacity Overlays
Implement sparse event-sensitivity regression and Black-Litterman news views with strict shrinkage, singularity handling, and fallback.

### S6 — Attention-Weighted Asset Sensitivity Pooling
Combine CAR/CAAR, Rank-IC, dense relevance, aspect impact, and attention weights. Include random-feature and shuffled-news controls.

### S7 — Cross-Sectional Transformer Score-to-Tilt Gate
Research/ablation method only. Map transformer sector scores to bounded tilts; do not implement an unconstrained neural allocator.

### Composite Methods
Implement S12, S13, and S126.

### Required Tests
Test 2024-only sensitivity, Rank-IC gating, bounded Track A risk scaling, S6 transformer ablation sensitivity, composite traces, and final weight constraints.


    ## Examples

    If transformer attention assigns high relevance to semiconductor policy news, the system must still pass event-study sensitivity, Rank-IC validation, confidence gate, turnover limits, and max-tilt limits before adjusting weights.


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
Substage S status: <pass/partial/fail>
Transformer-aware gates implemented: <list>
Track A integration: <pass/partial/fail>
Track B integration: <pass/partial/fail>
Tests run: <commands and pass/fail>
Updated tables: <paths>
Next prompt: prompt06_pipeline_integration_gpu_cache_trace.md
```
