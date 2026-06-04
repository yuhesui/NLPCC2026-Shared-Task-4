# Prompt1-1 — Section 1 Transformer Pipeline Scaffold, Registry, Cache, and Interfaces

    **Recommended model:** GPT-5.5 High

    ## Role

    You are a senior Python research engineer, transformer systems engineer, GPU/cache pipeline engineer, and official-semantics integration reviewer.

    ## Objective

    Build the Section 1 scaffold so transformer/attention methods can be implemented and tested cleanly. This prompt must support local transformer caches, model availability checks, GPU/CPU routing, and N/I/S method composition.

    ## Fixed Project Context

Project:

```text
NLPCC 2026 Shared Task 4:
LLM-based Investment Advisor Agents for Asset Allocation in the Chinese Market
```

Tracks:

```text
Track A / Track 1:
  Macro-Asset Allocation

Track B / Track 2:
  Sector-Rotation Allocation
```

Frozen official runtime to preserve:

```text
Track A primary:
  p18_rp_macro_w10_s5

Track A fallback:
  p18_rp_macro_w40_s5

Track B primary:
  p18_leeqa_sector_k5_temp35

Track B fallback:
  p18_s1_sector_t35_v30_w20
```

This News Overlay stage is an implementation/research extension. It must not silently replace the frozen official runtime.


    ## Transformer-First Implementation Requirement

This revised Prompt1-x kit explicitly prioritises transformer/attention architectures over overly simplistic deterministic methods.

Deterministic rules are still required, but only as:

```text
1. safety fallback;
2. lexical baseline;
3. sanity-control path;
4. ablation comparator;
5. official-runtime compatibility guard.
```

They are **not sufficient** as the main Section 1 implementation.

Section 1 must implement and test transformer-style architectures as first-class methods:

```text
- BGE-style / sentence-transformer bi-encoder relevance cache;
- cross-encoder sector reranker gate where feasible;
- frozen FinBERT-style aspect-tone classifier;
- label-attention / Title2Event-inspired event tagger;
- sector-query attention daily news pooling;
- temporal lagged-news transformer or attention encoder;
- optional entity-sector graph-attention propagation;
- hybrid lexical + transformer fallback path.
```

If local model assets are not available, the agent must still implement:

```text
- method interfaces;
- config flags;
- cache manifests;
- unavailable-state handling;
- deterministic fallback;
- tests proving no silent download;
- status-table rows marked `blocked_missing_local_model`, not simply omitted.
```


    ## Mandatory Read-First Files

Read these if present. If exact paths differ, locate the latest equivalent.

```text
AGENTS.md
README.md
docs/README.md
docs/news_overlay/
docs/prompts/news_overlay_prompts/
docs/new_overlay_research/
outputs/reports/news_overlay/prompt0b/
outputs/reports/prompt20/presented/current_repo_status_report.md
outputs/reports/prompt20/presented/current_repo_status_table.md
outputs/reports/prompt20/presented/preserved_candidate_summary.md
outputs/reports/prompt20/presented/next_stage_news_text_overlay_workflow.md
configs/preserved_candidates/manifest.json
src/nlpcc/stage1_news/
src/nlpcc/stage2_text_store/
src/nlpcc/stage3_trade/
src/nlpcc/stage4_agent/
src/nlpcc/execution/
src/tools/backtesting/
src/tools/experiments/
src/tools/create_implementation_log.py
```

Also inspect prior prompt style if available:

```text
prompt17_overnight_official_semantics_grid_search.md
prompt17b_full_horizon_validation_candidate_freeze_repair.md
prompt18_official_server_big_grid_final_packaging.md
prompt19_tuner_news_cleanup_report_handoff.md
prompt20_wrapup_cleanup_status_next_workflow.md
```


    ## Method Codes — Transformer-First Three-Substage Architecture

### Substage N — News Analysis / Embedding / Relevance

| Code | Method | Priority | Role |
|---|---|---|---|
| N0 | no-news / base-only input | control | base/null |
| N1 | deterministic taxonomy + entity/BM25 relevance | fallback | lexical baseline only |
| N2 | BGE-style bi-encoder text-to-sector relevance cache | required | main transformer relevance method |
| N3 | frozen FinBERT-style aspect-tone classifier | required | contextual tone/aspect feature |
| N4 | label-attention / Title2Event-inspired event tagger | required | transformer event typing and argument extraction |
| N5 | sector-query attention daily news pooling | required | attention aggregation over daily Top-20 news |
| N6 | cross-encoder sector reranker gate | recommended | high-precision second-stage relevance |
| N7 | temporal lagged-news attention encoder | recommended | narrative persistence over lagged news |
| N8 | entity-sector graph-attention propagation | ablation/defer | indirect sector relevance |
| N12 | N1 + N2 lexical/embedding hybrid | required | robust hybrid relevance |
| N13 | N1 + N3 lexical/aspect-tone hybrid | required | robust hybrid tone |
| N2345 | N2 + N3 + N4 + N5 transformer-stack | required | primary transformer-first stack |

### Substage I — News Impact Estimation

| Code | Method | Priority | Role |
|---|---|---|---|
| I0 | zero impact | control | null |
| I1 | deterministic event magnitude | fallback | baseline only |
| I2 | Permutation-Tested News Attention Index, PT-NAI | required | transparent index |
| I3 | event-study calibrated impact | required | CAR/CAAR impact calibration |
| I4 | decay-weighted event persistence | required | persistence and novelty control |
| I5 | impact-gated attention pooling | required | attention impact aggregation |
| I6 | transformer aspect-impact aggregator | required | FinBERT/aspect-aware impact score |
| I7 | temporal narrative impact encoder | recommended | lagged narrative impact |
| I23 | I2 + I3 NAI plus event-study impact | required | robust impact core |
| I256 | I2 + I5 + I6 attention/aspect impact stack | required | transformer-impact stack |

### Substage S — ETF / Sector News Sensitivity and Overlay Use

| Code | Method | Priority | Role |
|---|---|---|---|
| S0 | no sensitivity / uniform sensitivity | control | null |
| S1 | CAR/CAAR event-study sensitivity matrix | required | event-class sensitivity |
| S2 | Rank-IC Gated Sector News Momentum | required | Track B signal validation |
| S3 | Volatility-Scaled Macro News Risk Gate | required | Track A risk gate |
| S4 | Sparse Event-Sensitivity Regression Overlay | required | data-driven sensitivity |
| S5 | Black-Litterman News View Overlay | recommended | Bayesian view overlay |
| S6 | attention-weighted asset sensitivity pooling | required | transformer/attention sensitivity |
| S7 | cross-sectional transformer score-to-tilt gate | ablation | learned score-to-overlay |
| S12 | S1 + S2 event-study sensitivity + Rank-IC | required | Track B first robust gate |
| S13 | S1 + S3 event-study sensitivity + macro risk | required | Track A first robust gate |
| S126 | S1 + S2 + S6 sensitivity stack | required | transformer-aware Track B gate |


    ## Required Scaffold

    Create or update equivalent files:

    ```text
    src/nlpcc/news_overlay/
      __init__.py
      base.py
      registry.py
      config.py
      pipeline.py
      traces.py
      cache.py
      gpu.py
      model_availability.py
      transformer_features.py
      cli.py

    src/nlpcc/news_overlay/n_methods/
    src/nlpcc/news_overlay/i_methods/
    src/nlpcc/news_overlay/s_methods/

    configs/news_overlay/
      methods/
      grids/
      local_models.example.yaml

    tests/test_news_overlay/
    ```

    If existing repo conventions differ, adapt and document the mapping.

    ## Required Interfaces

    ```text
    TransformerFeatureProvider:
      checks local model availability
      forbids silent downloads
      encodes text in batches
      writes deterministic cache records

    NewsAnalysisMethod:
      emits event/relevance/tone/attention records

    NewsImpactMethod:
      emits impact/NAI/attention impact records

    NewsSensitivityMethod:
      emits sensitivity/gate/overlay records

    NewsOverlayPipeline:
      composes N + I + S methods and writes traces

    ModelAvailabilityReport:
      local path, dependency status, device status, missing-model reason
    ```

    ## Required Tests

    ```text
    - registry lists all N/I/S method codes;
    - transformer methods can be registered without local model files;
    - missing model gives blocked_missing_local_model, not crash;
    - no method attempts network access in offline mode;
    - CPU fallback path works;
    - cache key includes model/preprocessing/text/date/method;
    - N2345/I256/S126 composite configs can be built;
    - deterministic N1 remains available as fallback only.
    ```

    ## GPU / Acceleration / Cache Requirements

Transformer-first implementation requires efficient local inference and caching.

Required:

```text
- Auto-detect `cpu` / `cuda`.
- Provide CLI flags: `--device auto|cpu|cuda`, `--batch-size`, `--num-workers`, `--cache-dir`, `--offline`, `--local-model-path`.
- Use GPU for embedding, classifier, reranker, and attention batches if available.
- CPU fallback must work for smoke tests.
- No method may silently download model files.
- If local model is missing, mark method status as `blocked_missing_local_model` and fall back to N1.
- Cache every expensive text output by deterministic hash.
- Cache key must include model id, local path/revision, preprocessing version, method code, text hash, and date.
- Write cache manifests and runtime reports.
- Compare CPU/GPU outputs for shape, NaN, and deterministic scalar consistency.
```

Recommended:

```text
- Batch daily news embedding across dates where leakage-safe.
- Precompute sector prototype embeddings.
- Store large vectors in binary/cache files, not human-readable reports.
- Store scalar summaries in CSV/MD reports.
```


    ## Transformer-First Grid Search Table

Every implementation and testing prompt must update this table.

| Run ID | Section | Track | N Method | I Method | S Method | Base Config | Transformer Used? | Local Model Required? | Cache Required? | Purpose | Implementation Status | Test Status | 2024 Tune Status | 2025 Frozen Status | GPU Used | Runtime | Sharpe | CumRet | MaxDD | Turnover | Zero-News Pass | Shuffled-News Pass | Lexical Baseline Beat? | Decision | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---:|---:|---:|---:|---:|---:|---|---|---|---|---|

### Mandatory Core Grid

| Run ID | Section | Track | N | I | S | Purpose |
|---|---|---|---|---|---|---|
| G00A | baseline | A | N0 | I0 | S0 | Track A preserved base |
| G00B | baseline | B | N0 | I0 | S0 | Track B preserved base |
| G01A | lexical_control | A | N1 | I1 | S3 | deterministic-only Track A control |
| G01B | lexical_control | B | N1 | I1 | S2 | deterministic-only Track B control |
| G10A | transformer_core | A | N2 | I2 | S3 | BGE relevance + NAI + macro gate |
| G11A | transformer_core | A | N13 | I6 | S13 | aspect-tone + transformer impact + macro sensitivity |
| G12A | transformer_core | A | N2345 | I256 | S13 | full transformer news stack + macro gate |
| G10B | transformer_core | B | N2 | I2 | S2 | BGE relevance + NAI + Rank-IC |
| G11B | transformer_core | B | N12 | I23 | S12 | hybrid relevance + NAI/ESC + CAR/Rank-IC |
| G12B | transformer_core | B | N2345 | I256 | S126 | full transformer/attention Track B stack |
| G13B | transformer_core | B | N6 | I23 | S12 | cross-encoder reranker + impact/sensitivity |
| G14B | transformer_core | B | N5 | I5 | S2 | sector-query attention pooling + Rank-IC |
| G15B | transformer_core | B | N4 | I6 | S2 | label-attention event tagger + aspect impact |
| G20B | higher_capacity | B | N2345 | I256 | S4 | transformer stack + sparse sensitivity |
| G21B | higher_capacity | B | N2345 | I256 | S5 | transformer stack + Black-Litterman views |
| G22B | ablation | B | N7 | I7 | S6 | temporal narrative attention ablation |
| G23B | ablation | B | N8 | I2 | S6 | graph-attention relevance ablation |

### Required Comparison Rule

A transformer/attention candidate must be compared against its lexical-control counterpart:

```text
G10A/G11A/G12A must beat or explain failure relative to G01A.
G10B/G11B/G12B/G13B/G14B/G15B must beat or explain failure relative to G01B.
```

Deterministic-only candidates may remain as fallback, but cannot be declared the Section 1 success condition unless all transformer methods are blocked by unavailable local assets or fail ablation tests.


    ## Common Deliverables

Each prompt must update relevant artifacts under:

```text
outputs/reports/news_overlay/prompt1x/
  progress/
  presented/
  reference/
```

Required common files:

```text
outputs/reports/news_overlay/prompt1x/reference/method_implementation_table.csv
outputs/reports/news_overlay/prompt1x/reference/transformer_method_status.csv
outputs/reports/news_overlay/prompt1x/reference/grid_search_status_table.csv
outputs/reports/news_overlay/prompt1x/reference/cache_manifest.csv
outputs/reports/news_overlay/prompt1x/reference/dependency_manifest.md
outputs/reports/news_overlay/prompt1x/reference/error_log.md
docs/news_overlay/method_table.md
docs/news_overlay/grid_search_table.md
docs/news_overlay/transformer_architecture_table.md
docs/news_overlay/restart_context.md
docs/implementation_logs/<timestamp>_news_overlay_prompt1x_<short_name>.md
```


    ## Non-Negotiable Constraints

```text
- Do not change frozen official runtime configs.
- Do not promote any News Overlay candidate automatically.
- 2024 is the only construction/tuning/parameter-selection period.
- 2025 is frozen test/generalisation evaluation only.
- Do not use hidden 2026.
- Do not use current-day close/high/low/return before decision time.
- Same-day news must obey official timestamp cutoff.
- No online API dependency.
- No silent model downloads.
- No unpinned transformer/model dependency.
- No model binaries in official runtime package unless explicitly approved in a later prompt.
- All transformer/attention methods must have deterministic fallback or unavailable-state handling.
- Official-server parity is required before any promotion recommendation.
- Do not overclaim transformer benefit unless lexical/rule baselines and ablations prove it.
```


    ## Final Answer Requirements

    End with:

    ```text
    Scaffold status:
      <pass/partial/fail>

    Transformer registry status:
      <pass/partial/fail>

    Cache/model-availability status:
      <pass/partial/fail>

    Tests run:
      <commands and pass/fail>

    Next recommended prompt:
      prompt1_2_section1_transformer_news_architectures.md
    ```
