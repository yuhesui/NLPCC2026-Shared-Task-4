# Prompt1-4 — Section 1S Sensitivity, Overlay, and Transformer-Aware Integration

    **Recommended model:** GPT-5.5 XHigh

    ## Role

    You are a senior quantitative portfolio engineer, event-study researcher, transformer-signal validation specialist, and risk-control reviewer.

    ## Objective

    Implement Substage S methods that validate ETF/sector sensitivity to transformer-derived news signals and convert them into bounded overlays. Transformer outputs may inform relevance/impact/sensitivity, but portfolio changes must remain gated and auditable.

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


    ## Methods to Implement

    | Code | Method | Required Implementation |
    |---|---|---|
    | S0 | no sensitivity/uniform | control |
    | S1 | CAR/CAAR event-study sensitivity matrix | required |
    | S2 | Rank-IC Gated Sector News Momentum | required Track B gate |
    | S3 | Volatility-Scaled Macro News Risk Gate | required Track A gate |
    | S4 | Sparse Event-Sensitivity Regression Overlay | required higher-capacity sensitivity |
    | S5 | Black-Litterman News View Overlay | recommended |
    | S6 | attention-weighted asset sensitivity pooling | required transformer-aware sensitivity |
    | S7 | cross-sectional transformer score-to-tilt gate | ablation/research |
    | S12 | S1 + S2 | required Track B robust gate |
    | S13 | S1 + S3 | required Track A robust gate |
    | S126 | S1 + S2 + S6 | required transformer-aware Track B gate |

    ## Required Standard Output

    ```text
    date
    track
    base_config
    asset
    sensitivity_score
    car_caar_sensitivity
    rank_ic_score
    attention_sensitivity
    transformer_score
    macro_risk_score
    overlay_signal
    max_tilt
    turnover_budget
    drawdown_gate_active
    sensitivity_gate_active
    transformer_gate_active
    final_delta_weight
    final_target_weight
    method_code
    warnings
    ```

    ## Transformer-Aware Requirements

    S6 must evaluate whether transformer features are actually useful:

    ```text
    sensitivity[j,c] = f(CAR[j,c], RankIC[j,c], attention_relevance[j,c], aspect_impact[j,c])
    ```

    It must support ablations:

    ```text
    - lexical-only sensitivity;
    - embedding-only sensitivity;
    - aspect-tone-only sensitivity;
    - attention-pooling sensitivity;
    - full transformer stack;
    - random transformer features;
    - shuffled-news transformer features.
    ```

    ## Required Tests

    ```text
    - S1 builds CAR/CAAR from 2024 only.
    - S2 Rank-IC uses 2024 only.
    - S3 only scales Track A risk through bounded multiplier.
    - S6 produces different sensitivity under transformer vs lexical features.
    - S126 combines S1/S2/S6 with traceability.
    - S4/S5 handle small synthetic data without singularity/crash.
    - final weights obey sum/limit/turnover constraints.
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
    Substage S transformer-aware integration status:
      <pass/partial/fail>

    Implemented S methods:
      <list>

    Transformer-sensitive gates implemented:
      <list>

    Tests run:
      <commands and pass/fail>

    Next recommended prompt:
      prompt1_5_section1_integration_gpu_cache_trace.md
    ```
