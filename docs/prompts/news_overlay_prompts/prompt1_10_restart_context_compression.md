# Prompt1-10 — Restart Context Compression for Transformer-First News Overlay

    **Recommended model:** GPT-5.5 Medium

    ## Role

    You are a concise technical context compressor and project handoff writer.

    ## Objective

    Create a compact restart packet for the transformer-first News Overlay stage.

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


    ## Required Output Structure

    Write:

    ```text
    docs/news_overlay/restart_context.md
    outputs/reports/news_overlay/prompt1x/reference/current_method_status.csv
    outputs/reports/news_overlay/prompt1x/reference/current_transformer_status.csv
    outputs/reports/news_overlay/prompt1x/reference/current_grid_status.csv
    outputs/reports/news_overlay/prompt1x/reference/open_errors.md
    outputs/reports/news_overlay/prompt1x/reference/next_prompt_recommendation.md
    ```

    Structure:

    ```md
    # News Overlay Restart Context — Transformer-First Stage

    ## 1. Current State

    ## 2. Frozen Constraints

    ## 3. Implemented Transformer Methods

    ## 4. Blocked Transformer Methods

    ## 5. Deterministic Fallback Status

    ## 6. Cache / GPU / Dependency Status

    ## 7. Grid Runs Completed

    ## 8. Best Current Candidates

    ## 9. Open Errors

    ## 10. Files to Read First in New Session

    ## 11. Exact Next Prompt to Run

    ## 12. One-Paragraph Executive Summary
    ```

    ## Final Answer Requirements

    End with:

    ```text
    Restart packet status:
      <pass/partial/fail>

    Restart context path:
      <path>

    Next prompt:
      <specific prompt filename>
    ```
