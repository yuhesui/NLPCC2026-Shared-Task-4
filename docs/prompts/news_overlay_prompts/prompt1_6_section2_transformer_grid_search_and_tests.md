# Prompt1-6 — Section 2 Transformer-First Grid Search and Test Runs

    **Recommended model:** GPT-5.5 XHigh

    ## Role

    You are a senior quantitative research runner, transformer experiment engineer, GPU/cache optimiser, and leakage-control reviewer.

    ## Objective

    Run the transformer-first grid. Deterministic-only methods are controls; they are not sufficient to close the stage unless all transformer methods are blocked or fail honestly.

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


    ## Required Execution Order

    1. Run baseline/null controls:

    ```text
    G00A, G00B
    ```

    2. Run deterministic lexical controls:

    ```text
    G01A, G01B
    ```

    3. Build/verify local transformer caches:

    ```text
    N2, N3, N4, N5
    ```

    4. Run transformer core grid:

    ```text
    G10A, G11A, G12A
    G10B, G11B, G12B, G13B, G14B, G15B
    ```

    5. Run higher-capacity transformer-aware grid:

    ```text
    G20B, G21B
    ```

    6. Run attention/graph ablations if feasible:

    ```text
    G22B, G23B
    ```

    ## Required Metrics

    In addition to portfolio metrics, record transformer metrics:

    ```text
    model availability
    cache hit rate
    embedding coverage
    aspect-tone coverage
    event-label confidence
    attention entropy
    fallback rate
    transformer active days
    lexical baseline beat?
    transformer incremental Sharpe/return/drawdown/turnover
    ```

    ## Selection Rules

    ```text
    - 2024 only for selection/tuning.
    - 2025 frozen evaluation only after selection.
    - Transformer candidate must beat or provide useful orthogonal ablation against lexical control.
    - If transformer candidate fails because local model is missing, mark blocked_missing_local_model, not failed_alpha.
    - If transformer candidate underperforms, keep as ablation evidence and do not promote.
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
    Transformer grid status:
      <pass/partial/fail>

    Local model/cache status:
      <pass/partial/fail>

    Best transformer Track A candidate:
      <candidate or none>

    Best transformer Track B candidate:
      <candidate or none>

    Lexical baseline comparison:
      <summary>

    2025 frozen status:
      <not_run/pass/partial/fail>

    Updated grid table:
      <path>

    Next recommended prompt:
      prompt1_7_section2_ablation_dependency_promotion_audit.md
    ```
