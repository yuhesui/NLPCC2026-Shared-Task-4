# Prompt1-8 — Verify and Fix Transformer/Cache/GPU Errors

    **Recommended model:** GPT-5.5 High

    ## Role

    You are a senior debugging engineer, transformer dependency specialist, GPU/cache engineer, and reproducibility auditor.

    ## Objective

    Fix implementation, cache, device, dependency, trace, and grid errors discovered in transformer-first News Overlay implementation/testing. Do not add new architectures unless needed to complete already specified methods.

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


    ## Required Checks

    ```text
    - model availability reporting is correct;
    - no method attempts network access;
    - missing local model is handled gracefully;
    - cache keys are deterministic;
    - CPU path works;
    - GPU path works or is blocked honestly;
    - N2345/I256/S126 composite runs or is blocked with specific reason;
    - transformer traces include model/cache/attention fields;
    - lexical baseline comparison is recorded;
    - method/grid tables are updated;
    ```

    ## Required Reports

    ```text
    outputs/reports/news_overlay/prompt1x/presented/transformer_fix_summary.md
    outputs/reports/news_overlay/prompt1x/reference/error_log.md
    outputs/reports/news_overlay/prompt1x/reference/fix_manifest.csv
    outputs/reports/news_overlay/prompt1x/reference/post_fix_test_results.md
    docs/implementation_logs/<timestamp>_news_overlay_prompt1_8_verify_fix_transformer_errors.md
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
    Fix status:
      <pass/partial/fail>

    Transformer/cache errors fixed:
      <list>

    Remaining blockers:
      <list>

    Tests rerun:
      <commands and pass/fail>

    Next recommended prompt:
      prompt1_9_cross_check_transformer_first_external_session.md
    ```
