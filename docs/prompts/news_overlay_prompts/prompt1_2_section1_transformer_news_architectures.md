# Prompt1-2 — Section 1N Transformer News Architectures: Embedding, Relevance, Event Tagging, and Attention

    **Recommended model:** GPT-5.5 XHigh

    ## Role

    You are a senior Chinese financial NLP engineer, transformer retrieval engineer, attention-model architect, GPU/cache engineer, and model-risk reviewer.

    ## Objective

    Implement all Substage N methods, with transformer/attention architectures as first-class targets. Deterministic N1 is only fallback/baseline; the main deliverable is the transformer-style news understanding layer.

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
    | N0 | no-news/base-only | control path |
    | N1 | deterministic taxonomy + entity/BM25 relevance | fallback and lexical baseline |
    | N2 | BGE-style bi-encoder relevance cache | required; local model path; CPU/GPU batch encoding; no silent download |
    | N3 | frozen FinBERT-style aspect-tone classifier | required; aspect/tone probabilities; cache; fallback |
    | N4 | label-attention / Title2Event-inspired event tagger | required; event label descriptions; label-attention scoring; rule fallback |
    | N5 | sector-query attention daily news pooling | required; sector query over daily news keys/values |
    | N6 | cross-encoder sector reranker gate | implement if local reranker available; otherwise blocked status + interface |
    | N7 | temporal lagged-news attention encoder | implement small/frozen attention over lagged news features |
    | N8 | entity-sector graph-attention propagation | implement lightweight static graph attention or mark deferred with schema |
    | N12 | N1 + N2 hybrid | required |
    | N13 | N1 + N3 hybrid | required |
    | N2345 | N2 + N3 + N4 + N5 transformer-stack | required composite |

    ## Required Output Schema

    Each N-method must output:

    ```text
    date
    news_id
    timestamp
    cutoff_safe
    raw_text_hash
    duplicate_cluster_id
    event_type
    event_type_probabilities
    event_direction
    event_confidence
    entities
    sectors
    assets
    lexical_relevance_by_asset
    dense_relevance_by_asset
    cross_encoder_relevance_by_asset
    attention_relevance_by_asset
    final_relevance_by_asset
    aspect_tone
    label_attention_scores
    sector_query_attention_weights
    embedding_cache_key
    model_status
    device
    method_code
    warnings
    ```

    ## Required Architecture Details

    N2 bi-encoder:

    ```text
    Rel_dense(news_i, sector_j) = cosine(Encoder(news_i), Encoder(sector_proto_j))
    ```

    N3 aspect-tone:

    ```text
    tone_score = P(positive|aspect) - P(negative|aspect)
    aspects = policy, regulation, demand, liquidity, earnings, geopolitics, risk
    ```

    N4 label-attention:

    ```text
    p(event_label | news) = softmax(Enc(news)^T Enc(label_description))
    ```

    N5 sector-query attention:

    ```text
    alpha[i,j] = softmax(q_sector_j^T k_news_i / sqrt(d))
    pooled_news[j] = sum_i alpha[i,j] * v_news_i
    ```

    N6 reranker:

    ```text
    score(news_i, sector_j) = CrossEncoder([news_i, sector_proto_j])
    ```

    N7 temporal encoder:

    ```text
    z[t,j] = AttentionEncoder(features[t-L:t, j])
    ```

    ## Required Tests

    ```text
    - N2 local model missing -> blocked_missing_local_model, no crash.
    - N2 local model available -> cache write/read smoke.
    - N3 aspect-tone output has expected fields.
    - N4 label-attention assigns at least one label or reports low confidence.
    - N5 attention weights sum correctly over daily news items.
    - N6 reranker does not run without explicit local model.
    - N7 handles short history with padding.
    - N12/N13/N2345 composites preserve component traceability.
    - No method attempts network access.
    - CPU mode works.
    - device=auto works.
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
    Substage N transformer implementation status:
      <pass/partial/fail>

    Implemented transformer N methods:
      <list>

    Blocked/deferred N methods:
      <list with reasons>

    Local model/cache status:
      <pass/partial/fail>

    Tests run:
      <commands and pass/fail>

    Updated method table:
      <path>

    Next recommended prompt:
      prompt1_3_section1_transformer_impact_architectures.md
    ```
