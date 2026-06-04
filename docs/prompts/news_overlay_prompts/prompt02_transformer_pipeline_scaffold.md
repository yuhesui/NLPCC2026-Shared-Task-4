# Prompt02 — Transformer Pipeline Scaffold, Registry, Cache, and Interfaces

    ## Role

    You are a senior Python research engineer, transformer systems engineer, GPU/cache engineer, and official-semantics integration reviewer.

    ## Instructions

    Implement the minimal real scaffold required for transformer-first News Overlay methods. Focus on method registry, base interfaces, model availability, cache, trace schema, CLI, and smoke tests. Avoid full model logic except simple stubs needed for integration.

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

    ### Part A — Method Registry
Implement a registry that lists all N/I/S methods, instantiates methods by code, validates compatibility by track, reports transformer/control/fallback status, and exposes composite methods.

### Part B — Base Interfaces
Define interfaces for:
```text
NewsAnalysisMethod
NewsImpactMethod
NewsSensitivityMethod
NewsOverlayPipeline
TransformerFeatureProvider
ModelAvailabilityReport
CacheManifestWriter
TraceWriter
```

### Part C — Offline Model Availability
Implement statuses:
```text
available
blocked_missing_local_model
blocked_missing_dependency
blocked_offline_policy
disabled_by_config
fallback_used
```
No method may silently download models.

### Part D — Cache Scaffold
Cache keys must include method code, model identifier, local path or revision, preprocessing version, text hash, date, news source hash, and feature schema version.

### Part E — CLI Skeleton
Support command equivalents for:
```text
list-methods
check-models --offline
build-cache --method <N-code>
run --track <A/B> --n-method <...> --i-method <...> --s-method <...>
run-grid --grid <path> --smoke
```

### Part F — Tests
Add bounded tests for registry completeness, composite resolution, missing-model behaviour, offline mode, cache-key stability, invalid method errors, CPU fallback, and trace schema.
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


    ## Examples

    Missing BGE model should produce:
```text
method_code=N2
status=blocked_missing_local_model
fallback=N1
network_attempted=false
```
It should not produce empty embeddings marked as success.


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
Scaffold status: <pass/partial/fail>
Registry status: <pass/partial/fail>
Model availability layer: <pass/partial/fail>
Cache scaffold: <pass/partial/fail>
CLI skeleton: <pass/partial/fail>
Tests run: <commands and pass/fail>
Next prompt: prompt03_transformer_news_architectures.md
```
