# Prompt1-9 — Independent Transformer-First Cross-Check in Separate Session

    **Recommended model:** GPT-5.5 XHigh

    ## Role

    You are an independent transformer systems auditor, quantitative research reviewer, leakage-control specialist, and skeptical model-risk reviewer.

    ## Objective

    Cross-check whether the implementation truly built transformer/attention architectures rather than only deterministic placeholders. Verify code, configs, caches, tests, traces, ablations, and claims.

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


    ## Read-First Files

    ```text
    docs/news_overlay/README.md
    docs/news_overlay/method_table.md
    docs/news_overlay/transformer_architecture_table.md
    docs/news_overlay/grid_search_table.md
    outputs/reports/news_overlay/prompt1x/presented/
    outputs/reports/news_overlay/prompt1x/reference/
    src/nlpcc/news_overlay/
    configs/news_overlay/
    tests/test_news_overlay/
    ```

    ## Cross-Check Questions

    ```text
    1. Are N2/N3/N4/N5/N6/N7/N8 actually registered?
    2. Do transformer methods have code paths, not only documentation?
    3. Does missing local model produce blocked status rather than silent success?
    4. Does offline mode prevent downloads?
    5. Are embeddings/aspect/attention traces written?
    6. Are transformer candidates compared against N1 lexical controls?
    7. Are zero-news and shuffled-news ablations present?
    8. Is 2025 excluded from tuning?
    9. Is deterministic path preserved as fallback?
    10. Are claims about transformer value supported by results?
    ```

    ## Required Reports

    ```text
    outputs/reports/news_overlay/prompt1x_crosscheck/presented/transformer_cross_check_summary.md
    outputs/reports/news_overlay/prompt1x_crosscheck/reference/cross_check_findings.csv
    outputs/reports/news_overlay/prompt1x_crosscheck/reference/required_fixes.md
    outputs/reports/news_overlay/prompt1x_crosscheck/reference/transformer_method_reality_check.md
    docs/implementation_logs/<timestamp>_news_overlay_prompt1_9_transformer_crosscheck.md
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
    Cross-check verdict:
      <pass/partial/fail>

    Transformer implementation reality:
      <implemented/mostly_placeholders/blocked/misrepresented>

    Critical issues:
      <list or none>

    Required next action:
      <prompt1_8_fix / further_tests / ready_for_human_review>
    ```
