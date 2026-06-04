# Transformer Architecture Table

## Architecture Requirements

| Architecture | Method codes | Primary purpose | Required interface | Local assets | Cache artifacts | Fallback / blocked behavior | First implementation prompt |
|---|---|---|---|---|---|---|---|
| BGE-style / sentence-transformer bi-encoder | N2, N12, N2345 | Text-to-sector and text-to-asset relevance | `TransformerFeatureProvider.encode_texts`, sector prototype encoder, cache reader/writer | Local embedding model path or pinned local HF cache | text embeddings, sector embeddings, relevance scores, cache manifest | `blocked_missing_local_model`; use N1 BM25/entity relevance | `prompt1_1_section1_transformer_pipeline_scaffold.md`, then `prompt1_2_section1_transformer_news_architectures.md` |
| Frozen FinBERT-style aspect-tone classifier | N3, N13, N2345, I6, I256 | Chinese financial tone and aspect conditioning | batch classifier with stable label schema and unavailable-state report | Local classifier model path and pinned dependency versions | tone/aspect logits, scalar tone, model manifest | `blocked_missing_local_model`; use deterministic tone proxy | `prompt1_2_section1_transformer_news_architectures.md`, then `prompt1_3_section1_transformer_impact_architectures.md` |
| Label-attention / Title2Event-inspired tagger | N4, N2345, G15B | Event type and argument extraction | event label set, argument schema, confidence and validation hooks | Local encoder/classifier where available | event labels, argument spans or normalized slots, confidence | `blocked_missing_local_model`; use deterministic event taxonomy | `prompt1_2_section1_transformer_news_architectures.md` |
| Sector-query attention pooling | N5, N2345, I5, S6, S126, G14B | Daily Top-20 news aggregation per sector/asset | query-key attention over news items and sector prototypes | Encoder cache or local encoder | daily attention weights, pooled sector vectors, sanity summaries | fall back to N1/N12 relevance-weighted pooling | `prompt1_2_section1_transformer_news_architectures.md`, then `prompt1_3` and `prompt1_4` |
| Cross-encoder sector reranker | N6, G13B | High-precision second-stage relevance gate | pairwise text-sector scorer with top-k rerank API | Local cross-encoder model path | rerank scores, accepted/rejected gates | `blocked_missing_local_model`; skip rerank and retain N2/N12 order | `prompt1_2_section1_transformer_news_architectures.md` |
| Temporal lagged-news attention encoder | N7, I7, G22B | Narrative persistence over prior visible news | leakage-safe lag window encoder and decay controls | Local encoder or cached embeddings | lagged state vectors, temporal attention weights | use I4 decay-weighted deterministic persistence | `prompt1_3_section1_transformer_impact_architectures.md` |
| Entity-sector graph attention | N8, G23B | Indirect sector relevance propagation | graph nodes, edges, attention propagation report | Optional local graph/encoder dependency | graph attention scores, propagated relevance | use static entity-sector mapping; mark deferred/blocked if unavailable | `prompt1_4_section1_sensitivity_overlay_transformer_integration.md` |
| Transformer aspect-impact aggregator | I6, I256 | Convert tone/aspect/event outputs into impact scores | aspect-aware impact module with calibration trace | FinBERT/aspect outputs and 2024-only calibration data | aspect impact scores, calibration manifest | fall back to I1/I23 with blocked component notes | `prompt1_3_section1_transformer_impact_architectures.md` |
| Attention-weighted asset sensitivity pooling | S6, S126 | Convert attention/news impact into bounded overlay sensitivities | sensitivity matrix and overlay gate API | N/I attention outputs | sensitivity weights, overlay tilt candidates, risk gate trace | fall back to S12/S13 controls | `prompt1_4_section1_sensitivity_overlay_transformer_integration.md` |
| Cross-sectional transformer score-to-tilt gate | S7 | Learned score-to-overlay ablation | ablation-only tilt gate with strict train/test split | Local model and 2024-only labels | frozen coefficients/model manifest, ablation trace | blocked or disabled by default; never auto-promote | `prompt1_4_section1_sensitivity_overlay_transformer_integration.md` |

## Common Interface Requirements

- All transformer methods must register even when local model files are absent.
- All methods must expose status values, including `available`,
  `blocked_missing_local_model`, `disabled_by_config`, and `fallback_used`.
- Offline mode must be default for tests.
- Cache keys must include method code, model id, local path or revision,
  preprocessing version, decision date, text hash, and asset/sector query where
  applicable.
- Human-readable reports must store scalar summaries only; large embeddings
  belong under cache paths, not Markdown reports.
