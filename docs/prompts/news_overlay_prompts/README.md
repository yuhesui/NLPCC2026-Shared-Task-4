# News Overlay Prompt Package — Transformer-First Structured Edition

This package contains only the prompt files for the News Overlay stage.

Repository target path:

```text
docs/prompts/news_overlay_prompts/
```

## AI Mode Recommendations

The mode recommendations are intentionally listed only in this README. Individual prompt files do not contain separate mode labels.

| Prompt | Recommended AI Mode | Purpose |
|---|---|---|
| `prompt01_setup_transformer_first_docs.md` | GPT-5.5 High | setup documentation, method tables, grid tables, and transformer-first policy |
| `prompt02_transformer_pipeline_scaffold.md` | GPT-5.5 High | create registry, interfaces, cache/model-availability layer, CLI skeleton |
| `prompt03_transformer_news_architectures.md` | GPT-5.5 XHigh | implement N-stage transformer news analysis, embeddings, event tagging, relevance, attention |
| `prompt04_transformer_impact_architectures.md` | GPT-5.5 XHigh | implement I-stage PT-NAI, attention impact, aspect impact, temporal impact |
| `prompt05_sensitivity_overlay_transformer_integration.md` | GPT-5.5 XHigh | implement S-stage sensitivity, Rank-IC, macro gate, transformer-aware overlay |
| `prompt06_pipeline_integration_gpu_cache_trace.md` | GPT-5.5 High | integrate pipeline, cache, GPU/CPU routing, CLI, trace schema |
| `prompt07_transformer_grid_search_and_test_runs.md` | GPT-5.5 XHigh | run transformer-first grid and frozen tests |
| `prompt08_ablation_dependency_promotion_audit.md` | GPT-5.5 XHigh | run ablations, dependency audit, leakage audit, promotion gate |
| `prompt09_verify_fix_transformer_errors.md` | GPT-5.5 High | verify and fix cache/model/GPU/grid errors |
| `prompt10_external_cross_check.md` | GPT-5.5 XHigh | independent cross-check in another session |
| `prompt11_restart_context_compression.md` | GPT-5.5 Medium | compact context for starting a new session |

## Intended Execution Order

```text
Section 1 — Implementation:
  prompt01
  prompt02
  prompt03
  prompt04
  prompt05
  prompt06

Section 2 — Testing, Ablation, Verification:
  prompt07
  prompt08
  prompt09
  prompt10

Context Management:
  prompt020 whenever the context window is becoming too compressed.
```

## Core Policy

This is a transformer-first prompt package. Deterministic methods must exist, but only as fallback, sanity control, lexical baseline, ablation comparator, and official-runtime safety guard.

The main implementation target is:

```text
N2345 + I256 + S126
```

where:

```text
N2345 = embedding relevance + aspect-tone + label-attention event tagging + sector-query attention pooling
I256  = PT-NAI + impact-gated attention pooling + transformer aspect-impact aggregation
S126  = event-study sensitivity + Rank-IC sector gate + attention-weighted asset sensitivity
```
