# News Overlay Transformer-First Control Document

## Purpose

This folder controls the Prompt1-x News Overlay phase for NLPCC 2026 Shared
Task 4. The phase is a research extension for stronger news/text processing
and gated overlay tests. It must not silently replace the frozen official
runtime.

## Frozen Official Runtime

| Track | Role | Preserved config |
|---|---|---|
| Track A / macro | primary | `p18_rp_macro_w10_s5` |
| Track A / macro | fallback | `p18_rp_macro_w40_s5` |
| Track B / sector | primary | `p18_leeqa_sector_k5_temp35` |
| Track B / sector | fallback | `p18_s1_sector_t35_v30_w20` |

Any News Overlay candidate is experimental until it passes 2024-only
construction, frozen 2025 evaluation, ablation tests, leakage checks,
dependency checks, and official-server parity. Promotion also requires a
separate human decision.

## Transformer-First Rule

Prompt1-x prioritizes transformer and attention architectures. Deterministic
rules are still mandatory, but only as:

1. safety fallback;
2. lexical baseline;
3. sanity-control path;
4. ablation comparator;
5. official-runtime compatibility guard.

Deterministic-only news processing is not a sufficient Section 1 success
condition unless all transformer methods are honestly blocked by missing local
model assets or fail ablation tests.

## Required Architecture Families

Section 1 implementation prompts must build interfaces, configs, tests, and
status reporting for:

- BGE-style or sentence-transformer bi-encoder relevance cache;
- cross-encoder sector reranker gate where feasible;
- frozen FinBERT-style aspect-tone classifier;
- label-attention or Title2Event-inspired event tagger;
- sector-query attention daily news pooling;
- temporal lagged-news transformer or attention encoder;
- optional entity-sector graph-attention propagation;
- hybrid lexical plus transformer fallback path.

The final portfolio action must remain bounded, gated, traceable, and
ablation-tested. Transformer outputs may create relevance, tone, event,
attention, impact, and sensitivity features; they must not become an
unconstrained direct allocator.

## Local Model, Cache, and Dependency Policy

- No online API dependency is allowed for News Overlay runtime tests.
- No silent model downloads are allowed.
- No unpinned transformer or model dependency may be added.
- No model binary may enter the official runtime package unless explicitly
  approved in a later prompt.
- Local model paths must be explicit in config or environment-controlled
  discovery.
- Missing model assets must produce `blocked_missing_local_model`, deterministic
  fallback, and status-table rows.
- Expensive transformer outputs must use deterministic cache keys including
  method code, model id, local path or revision, preprocessing version, date,
  and text hash.
- Cache manifests must be written even when the cache is unavailable or empty.

## Evaluation Discipline

- 2024 is the only construction, tuning, and parameter-selection period.
- 2025 is frozen test and generalization evaluation only.
- Hidden 2026 data must not be used.
- Same-day news must obey the official timestamp cutoff.
- Current-day close, high, low, return, and derived current-day return fields
  must not be used before the decision timestamp.
- Transformer candidates must be compared against lexical controls before any
  success claim.
- Zero-news and shuffled-news tests are required for overlay candidates.

## Required Tables

- Method table: [method_table.md](method_table.md)
- Transformer architecture table:
  [transformer_architecture_table.md](transformer_architecture_table.md)
- Grid table: [grid_search_table.md](grid_search_table.md)
- Restart context: [restart_context.md](restart_context.md)
