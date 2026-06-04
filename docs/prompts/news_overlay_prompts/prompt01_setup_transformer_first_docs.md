# Prompt01 — Setup Transformer-First News Overlay Documentation

    ## Role

    You are a senior research-engineering lead, Chinese financial NLP systems architect, transformer pipeline planner, and reproducibility reviewer.

    ## Instructions

    Set up repository documentation and status tables for a transformer-first News Overlay stage. This is a documentation and planning prompt, not an implementation prompt. Later agents must not be able to reduce the work to deterministic keyword rules.

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

    ### Part A — Repository Discovery
1. Identify current docs, configs, Stage 1 news code, Stage 2 text storage, execution paths, and backtester paths.
2. Identify whether `docs/news_overlay/` exists.
3. Identify whether existing local model features include BGE, FinBERT, or hybrid modes.
4. Record missing paths and nearest equivalents.

### Part B — Documentation Setup
Create or update:
```text
docs/news_overlay/README.md
docs/news_overlay/transformer_first_policy.md
docs/news_overlay/method_table.md
docs/news_overlay/transformer_architecture_table.md
docs/news_overlay/grid_search_table.md
docs/news_overlay/dependency_policy.md
docs/news_overlay/gpu_cache_policy.md
docs/news_overlay/ablation_policy.md
docs/news_overlay/promotion_gate.md
docs/news_overlay/restart_context.md
```

### Part C — Status Tables
Create method and grid tables. Method rows must cover every N/I/S method. Grid rows must include transformer candidates and lexical controls.
## Transformer-First Method Inventory

### Substage N — News Analysis / Embedding / Relevance

| Code | Method | Required Status |
|---|---|---|
| N0 | no-news/base-only control | control |
| N1 | deterministic taxonomy + entity/BM25 relevance | fallback/baseline |
| N2 | BGE-style or sentence-transformer bi-encoder relevance cache | required |
| N3 | frozen FinBERT-style aspect-tone classifier | required |
| N4 | label-attention / Title2Event-inspired event tagger | required |
| N5 | sector-query attention daily news pooling | required |
| N6 | cross-encoder sector reranker gate | required if local reranker exists; otherwise blocked with interface |
| N7 | temporal lagged-news attention encoder | required lightweight version |
| N8 | entity-sector graph-attention propagation | ablation/defer with scaffold |
| N12 | N1 + N2 lexical/embedding hybrid | required |
| N13 | N1 + N3 lexical/aspect-tone hybrid | required |
| N2345 | N2 + N3 + N4 + N5 transformer-stack | required primary stack |

### Substage I — News Impact Estimation

| Code | Method | Required Status |
|---|---|---|
| I0 | zero-impact control | control |
| I1 | deterministic event magnitude score | fallback/baseline |
| I2 | Permutation-Tested News Attention Index, PT-NAI | required |
| I3 | event-study calibrated impact score | required |
| I4 | decay-weighted event persistence | required |
| I5 | impact-gated attention pooling | required |
| I6 | transformer aspect-impact aggregator | required |
| I7 | temporal narrative impact encoder | required lightweight version |
| I23 | I2 + I3 NAI plus event-study impact | required |
| I256 | I2 + I5 + I6 transformer-impact stack | required primary stack |

### Substage S — ETF / Sector Sensitivity and Overlay Use

| Code | Method | Required Status |
|---|---|---|
| S0 | no-sensitivity / uniform control | control |
| S1 | CAR/CAAR event-study sensitivity matrix | required |
| S2 | Rank-IC Gated Sector News Momentum | required |
| S3 | Volatility-Scaled Macro News Risk Gate | required |
| S4 | Sparse Event-Sensitivity Regression Overlay | required |
| S5 | Black-Litterman News View Overlay | recommended |
| S6 | attention-weighted asset sensitivity pooling | required |
| S7 | cross-sectional transformer score-to-tilt gate | ablation/research |
| S12 | S1 + S2 event-study sensitivity + Rank-IC | required |
| S13 | S1 + S3 event-study sensitivity + macro risk | required |
| S126 | S1 + S2 + S6 transformer-aware sector gate | required primary Track B stack |

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

    Example method row:
```text
N2 | BGE-style bi-encoder relevance | required | blocked_missing_local_model if no model path exists, not silently omitted
```
Example grid logic:
```text
G12B = N2345-I256-S126. If it cannot run, report which component blocked it.
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
Documentation setup status: <pass/partial/fail>
Transformer-first policy status: <pass/partial/fail>
Method table path: <path>
Grid table path: <path>
Files created/updated: <list>
Missing or substituted files: <list>
Next prompt: prompt02_transformer_pipeline_scaffold.md
```
