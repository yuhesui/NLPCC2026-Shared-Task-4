# Prompt07 — Transformer-First Grid Search and Test Runs

    ## Role

    You are a senior quantitative research runner, transformer experiment engineer, GPU/cache optimiser, official-semantics backtesting engineer, and leakage-control reviewer.

    ## Instructions

    Run the transformer-first grid in a staged, checkpointed, evidence-focused way. Deterministic-only results are controls, not sufficient completion evidence.

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

    ### Stage 0 — Integrity Smoke
Run G00A/G00B and G01A/G01B to confirm base and deterministic controls.

### Stage 1 — Model and Cache Readiness
For N2/N3/N4/N5/N6/N7, check local model availability, offline mode, bounded cache building, and explicit blocked status.

### Stage 2 — Transformer Core Grid on 2024
Run:
```text
G10A, G11A, G12A
G10B, G11B, G12B, G13B, G14B, G15B
```
Use 2024 only for selection. If full 2024 is too slow, run bounded smoke first, estimate runtime, then run the largest feasible broad 2024 evaluation.

### Stage 3 — Higher-Capacity and Ablation Grid
Run G20B/G21B/G22B/G23B if core grid is stable.

### Stage 4 — 2024 Selection Freeze
Select candidates from 2024 only. Record selected candidates, lexical-control comparison, blocked models, fallback rates, dependency risks, and freeze rationale.

### Stage 5 — Frozen 2025 Evaluation
Evaluate only frozen candidates and controls. Do not adjust any parameter after viewing 2025.

### Metrics
Record portfolio metrics and transformer metrics: cache hit rate, embedding coverage, aspect coverage, event-label confidence, attention entropy, reranker coverage, transformer active days, changed-date fraction versus lexical baseline, and shuffled-news degradation.
## Required Transformer-First Grid

| Run ID | Section | Track | N | I | S | Purpose | Transformer Used? | Local Model Required? | Cache Required? |
|---|---|---|---|---|---|---|---|---|---|
| G00A | baseline | A | N0 | I0 | S0 | preserved Track A base | no | no | no |
| G00B | baseline | B | N0 | I0 | S0 | preserved Track B base | no | no | no |
| G01A | lexical_control | A | N1 | I1 | S3 | deterministic Track A control | no | no | no |
| G01B | lexical_control | B | N1 | I1 | S2 | deterministic Track B control | no | no | no |
| G10A | transformer_core | A | N2 | I2 | S3 | embedding relevance + NAI macro gate | yes | yes | yes |
| G11A | transformer_core | A | N13 | I6 | S13 | aspect-tone + transformer impact + macro sensitivity | yes | yes | yes |
| G12A | transformer_core | A | N2345 | I256 | S13 | full transformer news stack + macro gate | yes | yes | yes |
| G10B | transformer_core | B | N2 | I2 | S2 | embedding relevance + Rank-IC sector gate | yes | yes | yes |
| G11B | transformer_core | B | N12 | I23 | S12 | hybrid relevance + event-study sensitivity | yes | yes | yes |
| G12B | transformer_core | B | N2345 | I256 | S126 | full transformer/attention sector stack | yes | yes | yes |
| G13B | transformer_core | B | N6 | I23 | S12 | cross-encoder reranker + impact/sensitivity | yes | yes | yes |
| G14B | transformer_core | B | N5 | I5 | S2 | sector-query attention pooling + Rank-IC | yes | optional | yes |
| G15B | transformer_core | B | N4 | I6 | S2 | label-attention event tagger + aspect impact | yes | optional | yes |
| G20B | higher_capacity | B | N2345 | I256 | S4 | transformer stack + sparse sensitivity | yes | yes | yes |
| G21B | higher_capacity | B | N2345 | I256 | S5 | transformer stack + BL views | yes | yes | yes |
| G22B | ablation | B | N7 | I7 | S6 | temporal narrative attention ablation | yes | optional | yes |
| G23B | ablation | B | N8 | I2 | S6 | graph-attention relevance ablation | yes | optional | yes |

Required comparison rule:

```text
G10A/G11A/G12A must be compared against G01A.
G10B/G11B/G12B/G13B/G14B/G15B must be compared against G01B.
Deterministic-only runs are not sufficient to close Section 1.
```


    ## Examples

    Decision examples:
```text
N2345-I256-S126 improves 2024 but fails shuffled-news -> fragile/research-only.
N12-I23-S12 improves Track B and shuffled-news degrades -> deeper audit candidate.
N2 blocked by missing model path -> blocked_missing_local_model, not failed_alpha.
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
Transformer grid status: <pass/partial/fail>
2024 selection status: <pass/partial/fail>
Frozen 2025 evaluation status: <not_run/pass/partial/fail>
Best transformer Track A candidate: <candidate or none>
Best transformer Track B candidate: <candidate or none>
Lexical baseline comparison: <summary>
Blocked model methods: <list>
Updated grid table: <path>
Next prompt: prompt08_ablation_dependency_promotion_audit.md
```
