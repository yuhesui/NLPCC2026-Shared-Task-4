# Prompt1-7 — Transformer Ablation, Dependency, Leakage, and Promotion Audit

    **Recommended model:** GPT-5.5 XHigh

    ## Role

    You are a senior transformer model-risk auditor, quantitative validation lead, dependency/security reviewer, and official-server parity reviewer.

    ## Objective

    Audit transformer/attention News Overlay candidates. Prove whether transformer methods add value over deterministic baselines, or classify them as ablation-only/deferred.

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


    ## Required Ablations

    ```text
    - base allocator only;
    - deterministic lexical baseline;
    - transformer real-news candidate;
    - no-news;
    - zero-news;
    - shuffled-news dates;
    - randomised event labels;
    - random embeddings;
    - lexical relevance versus dense relevance;
    - dense relevance versus cross-encoder reranker;
    - aspect-tone on/off;
    - label-attention on/off;
    - sector-query attention on/off;
    - temporal attention on/off;
    - transformer gate on/off;
    - impact gate on/off;
    - sensitivity gate on/off;
    - confidence gate on/off;
    - overlay strength sweep;
    - turnover cap sweep;
    ```

    ## Dependency Audit

    Verify:

    ```text
    - no silent model downloads;
    - all model paths are explicit;
    - offline mode works;
    - CPU smoke works;
    - GPU optional path works or is marked blocked;
    - official runtime package excludes model binaries by default;
    - dependency manifest records model family, local path, revision/checksum if available;
    - fallback path works if model is missing.
    ```

    ## Required Reports

    ```text
    outputs/reports/news_overlay/prompt1x/presented/transformer_ablation_summary.md
    outputs/reports/news_overlay/prompt1x/presented/transformer_dependency_audit.md
    outputs/reports/news_overlay/prompt1x/presented/promotion_audit.md
    outputs/reports/news_overlay/prompt1x/reference/transformer_ablation_results.csv
    outputs/reports/news_overlay/prompt1x/reference/dependency_audit.csv
    outputs/reports/news_overlay/prompt1x/reference/leakage_audit.md
    outputs/reports/news_overlay/prompt1x/reference/rejected_or_deferred_transformer_methods.md
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
    Transformer ablation status:
      <pass/partial/fail>

    Dependency audit status:
      <pass/partial/fail>

    Transformer methods with evidence:
      <list>

    Transformer methods ablation-only:
      <list>

    Transformer methods rejected/deferred:
      <list>

    Promotion recommendation:
      <no_promotion / research_continue / parity_ready_but_human_review_required>

    Next recommended prompt:
      prompt1_8_verify_fix_transformer_errors.md or prompt1_9_cross_check_transformer_first_external_session.md
    ```
