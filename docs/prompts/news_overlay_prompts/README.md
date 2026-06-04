# News Overlay Prompt 1-x Starter Kit — Transformer-First Revision

This revised kit explicitly requires transformer/attention-style architectures to be implemented as first-class methods. Deterministic rules remain necessary, but only as fallback, baseline, and ablation controls.

## Major Change from Previous Version

Previous kit:

```text
deterministic first, transformer second
```

This revised kit:

```text
transformer/attention architectures must be implemented and tested in Section 1;
deterministic methods are fallback and comparison baselines.
```

## Prompt Order

| Prompt | Thinking Mode | Purpose |
|---|---|---|
| `prompt1_0_setup_docs_and_transformer_stage_plan.md` | GPT-5.5 High | update docs and method/grid tables with transformer-first policy |
| `prompt1_1_section1_transformer_pipeline_scaffold.md` | GPT-5.5 High | scaffold N/I/S registry, transformer cache interfaces, GPU runner |
| `prompt1_2_section1_transformer_news_architectures.md` | GPT-5.5 XHigh | implement N-stage transformer/relevance methods |
| `prompt1_3_section1_transformer_impact_architectures.md` | GPT-5.5 XHigh | implement I-stage transformer/attention impact methods |
| `prompt1_4_section1_sensitivity_overlay_transformer_integration.md` | GPT-5.5 XHigh | implement S-stage sensitivity and transformer-aware overlays |
| `prompt1_5_section1_integration_gpu_cache_trace.md` | GPT-5.5 High | integrate CLI, GPU, cache, trace, configs |
| `prompt1_6_section2_transformer_grid_search_and_tests.md` | GPT-5.5 XHigh | run transformer-first grid and compare to deterministic baselines |
| `prompt1_7_section2_ablation_dependency_promotion_audit.md` | GPT-5.5 XHigh | ablations, dependency audit, leakage audit, promotion gate |
| `prompt1_8_verify_fix_transformer_errors.md` | GPT-5.5 High | fix failed transformer/cache/GPU paths |
| `prompt1_9_cross_check_transformer_first_external_session.md` | GPT-5.5 XHigh | independent cross-check |
| `prompt1_10_restart_context_compression.md` | GPT-5.5 Medium | restart context compression |

## Core Principle

```text
Build transformers for text understanding, relevance, attention, and event extraction;
keep final portfolio actions bounded, interpretable, gated, and fallback-safe.
```

## Main Transformer Architectures Required

```text
N2  BGE-style bi-encoder relevance cache
N3  frozen FinBERT-style aspect-tone classifier
N4  label-attention / Title2Event-inspired event tagger
N5  sector-query attention daily news pooling
N6  cross-encoder sector reranker gate
N7  temporal lagged-news attention encoder
N12 lexical + embedding hybrid
N13 lexical + aspect-tone hybrid
N2345 full transformer-stack
I5  impact-gated attention pooling
I6  transformer aspect-impact aggregator
I7  temporal narrative impact encoder
S6  attention-weighted asset sensitivity pooling
S7  cross-sectional transformer score-to-tilt gate
```

## Context Window Policy

If context compression is anticipated, run `prompt1_10_restart_context_compression.md` and start a fresh session using the generated restart packet.
