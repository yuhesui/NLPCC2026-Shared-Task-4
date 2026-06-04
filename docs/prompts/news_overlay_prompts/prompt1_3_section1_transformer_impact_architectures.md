# Prompt1-3 — Section 1I Transformer/Attention News Impact Architectures

    **Recommended model:** GPT-5.5 XHigh

    ## Role

    You are a senior event-driven finance researcher, transformer signal engineer, Chinese financial NLP architect, and leakage-control reviewer.

    ## Objective

    Implement all Substage I methods, with emphasis on transformer/attention impact aggregation rather than pure deterministic event scoring. Deterministic impact remains only as fallback/baseline.

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
    | I0 | zero impact | null control |
    | I1 | deterministic event magnitude | fallback baseline |
    | I2 | PT-NAI | transparent attention index |
    | I3 | event-study calibrated impact | 2024-only impact calibration |
    | I4 | decay-weighted event persistence | novelty and persistence |
    | I5 | impact-gated attention pooling | required transformer/attention aggregation |
    | I6 | transformer aspect-impact aggregator | required FinBERT/aspect-based impact |
    | I7 | temporal narrative impact encoder | recommended temporal transformer/attention |
    | I23 | I2 + I3 | robust non-neural impact core |
    | I256 | I2 + I5 + I6 | required transformer-impact stack |

    ## Required Standard Output

    ```text
    date
    news_id
    event_type
    event_direction
    event_impact
    deterministic_impact
    aspect_impact
    attention_impact
    narrative_impact
    event_novelty
    event_attention
    event_dispersion
    event_persistence_weight
    nai_by_asset
    nai_by_sector
    impact_gate_active
    confidence_gate_active
    method_code
    component_traces
    warnings
    ```

    ## Required Architectures

    I5 impact-gated attention:

    ```text
    attention_input = [dense_relevance, aspect_tone, event_label_prob, lexical_impact]
    alpha_i = softmax(gate_i * score_i)
    impact[t,j] = sum_i alpha_i * value_i[j]
    ```

    I6 transformer aspect-impact:

    ```text
    aspect_impact[i,j] =
      sum_a aspect_weight[a,j] * (P_pos[i,a] - P_neg[i,a]) * relevance[i,j]
    ```

    I7 temporal narrative impact:

    ```text
    narrative_impact[t,j] =
      TemporalAttention(impact_features[t-L:t, j])
    ```

    ## Training and Leakage Rules

    ```text
    - All learned or selected thresholds must be fit on 2024 only.
    - 2025 must not influence model, threshold, component choice, or retry selection.
    - If transformer features are cached over 2025 for evaluation, the cache must contain only text-derived features and no return labels.
    - Do not use post-decision price data in impact construction.
    ```

    ## Required Tests

    ```text
    - I0 zero signal collapses to base.
    - I2 PT-NAI runs on N2/N3/N4/N5 outputs.
    - I5 attention weights are finite and traceable.
    - I6 aspect-impact changes when aspect-tone changes.
    - I7 handles missing lag history.
    - I3 refuses 2025 calibration.
    - I256 composite preserves all component traces.
    - shuffled-news hooks exist.
    - randomised-label hooks exist.
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
    Substage I transformer-impact status:
      <pass/partial/fail>

    Implemented I methods:
      <list>

    Blocked/deferred I methods:
      <list with reasons>

    Leakage checks:
      <pass/partial/fail>

    Tests run:
      <commands and pass/fail>

    Next recommended prompt:
      prompt1_4_section1_sensitivity_overlay_transformer_integration.md
    ```
