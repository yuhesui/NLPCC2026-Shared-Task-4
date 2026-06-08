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

## Prompt03 Substage N Status

| Method family | Status after Prompt03 | Local model behavior | Fallback behavior |
|---|---|---|---|
| BGE-style / sentence-transformer bi-encoder | N2 interface and local-only encoder path implemented; N12/N2345 composition implemented | Explicit local path required; `AutoTokenizer`/`AutoModel` load with `local_files_only=True` | `blocked_missing_local_model` or `blocked_missing_dependency`; N1 feature rows remain populated |
| Frozen FinBERT-style aspect-tone | N3 aspect schema and local transformer aspect-similarity path implemented; N13/N2345 composition implemented | Explicit local path required | Complete aspect-tone schema with deterministic tone fallback |
| Label-attention / Title2Event-inspired tagger | N4 label-description scoring and event-argument schema implemented | Explicit local path enables transformer label-similarity scoring | Lexical label probabilities and entity/event arguments |
| Sector-query attention pooling | N5 daily sector-query attention weights implemented | Explicit local path enables transformer query/key scoring | Lexical relevance softmax attention |
| Cross-encoder sector reranker | N6 interface and blocked-state handling implemented | Local reranker path required in a later prompt | Reports blocked and falls back to N2 |
| Temporal lagged-news attention | N7 lightweight lagged-news attention implemented | Local temporal encoder still pending | Short-history warnings plus deterministic temporal overlap attention |
| Entity-sector graph attention | N8 static propagation scaffold implemented | Optional graph-attention model pending | Static entity-sector propagation for ablation |

## Prompt04 Substage I Status

| Method family | Status after Prompt04 | Local model behavior | Fallback / leakage behavior |
|---|---|---|---|
| Zero/deterministic impact controls | I0 and I1 implemented | No local model required | I0 emits zero signal; I1 remains deterministic baseline/fallback only |
| PT-NAI | I2 implemented | No local model required; consumes N feature rows | Includes tone, relevance, label confidence, attention, dispersion, duplicate adjustment, shuffled-news hook, and random-label hook |
| Event-study calibrated impact | I3 implemented | No local model required | Calibration rows are accepted only for 2024; 2025 calibration rows raise refusal; default prior table is traceable |
| Decay-weighted persistence | I4 implemented | No local model required | Monotone decay weights, novelty, repeated-event dampening, and policy-theme persistence are traceable |
| Impact-gated attention pooling | I5 implemented | Explicit local impact model path still optional/missing | Missing local assets produce `blocked_missing_local_model` with deterministic attention fallback rows |
| Transformer aspect-impact aggregation | I6 implemented | Consumes N3/N2345 aspect-tone outputs; optional local impact model path still missing | Missing local assets produce `blocked_missing_local_model`; fallback output uses N-derived aspect tone and sector aspect weights |
| Temporal narrative impact encoder | I7 lightweight path implemented | Optional local temporal model path still missing | Missing local assets produce `blocked_missing_local_model`; short-history diagnostics are explicit |
| Composite impact stacks | I23 and I256 implemented | I256 remains blocked when local I5/I6 assets are unavailable | Component traces remain visible; no candidate is promoted |

## Prompt05 Substage S Status

| Method family | Status after Prompt05 | Local model behavior | Fallback / leakage behavior |
|---|---|---|---|
| Overlay controls and event sensitivity | S0 and S1 implemented | No local model required | S1 accepts only 2024 sensitivity calibration rows; otherwise uses traceable shrunk priors. |
| Rank-IC and macro gates | S2 and S3 implemented | No local model required | S2 uses 2024-only Rank-IC threshold rows; S3 applies bounded Track A risk multipliers without directional overtrading. |
| Higher-capacity overlays | S4 and S5 implemented as bounded proxies | No local model required | S4 uses 2024-only sparse/ridge-style coefficients with S1 fallback if rows are missing; S5 uses a shrunk BL-style diagonal-volatility proxy. |
| Transformer-aware sensitivity pooling | S6 implemented | Explicit local S6 asset path is still optional/missing | Missing local assets produce `blocked_missing_local_model` with bounded fallback output; random-feature and shuffled-news controls are traceable. |
| Cross-sectional score-to-tilt gate | S7 implemented as ablation-only | Explicit local S7 asset path is still optional/missing | Missing local assets produce `blocked_missing_local_model`; output is bounded and cannot act as an unconstrained allocator. |
| Composite sensitivity stacks | S12, S13, and S126 implemented | S126 remains blocked when local S6 assets are unavailable | Component traces remain visible; final adjusted-weight previews enforce long-only, max-weight, turnover, and max-tilt guards. |

## Prompt06 Pipeline Integration Status

| Integration surface | Status after Prompt06 | Output artifacts | Notes |
|---|---|---|---|
| Pipeline composition | N/I/S stacks integrated for required Track A and Track B combinations | v2 trace JSON per run | Supports N2-I2-S3, N13-I6-S13, N2345-I256-S13, N2-I2-S2, N12-I23-S12, and N2345-I256-S126. |
| Trace schema | Implemented | `results`, `runtime_report`, `cache_report`, `model_status`, `summaries`, `warnings` | Summaries include embeddings, aspect tone, label attention, sector-query attention, impact components, sensitivity components, gate decisions, and base/final weights. |
| CPU/GPU routing | Implemented | trace config and runtime report | `device=auto` resolves to CUDA when available, otherwise CPU; `batch_size` is carried in config and context. |
| Cache reporting | Implemented | cache manifest CSV and cache-hit report JSON | CLI run and grid commands emit cache keys, hit flags, hit rate, and runtime summaries. |
| Grid readiness | Implemented | grid status CSV under the run output directory | Full mandatory grid runs without crashing; transformer rows remain explicit `blocked_missing_local_model` when local assets are absent. |

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

## Prompt20 Download-Once / Local-Only Status

Prompt20 selected and recorded approved Hugging Face models in
`configs/news_overlay/approved_hf_models.yaml`. The enabled model is
`BAAI/bge-small-zh-v1.5` pinned to
`e534609e6b53ac54bd42d8e87995d21a73b90bad`, downloaded once to
`C:\Users\jeanna\.cache\huggingface\hub`, and loaded afterward with
`local_files_only=True`.

The BGE snapshot is used as the shared real encoder for BGE-style relevance,
aspect-label similarity, event-label attention, sector-query attention, and the
downstream transformer-aware I/S stacks. The optional
`yiyanghkust/finbert-tone-chinese` classifier and `BAAI/bge-reranker-base`
cross-encoder are recorded as disabled approved candidates; they were not
downloaded by Prompt20. Therefore `N3` is real-encoder aspect evidence rather
than true classifier logits, and `N6` remains blocked.

## Prompt20.1 Local-Only Architecture Status

Prompt20.1 revalidated the architecture against pre-downloaded Hugging Face
snapshots without any download command:

- BGE bi-encoder: `BAAI/bge-small-zh-v1.5` snapshot
  `e534609e6b53ac54bd42d8e87995d21a73b90bad`.
- FinBERT-style classifier: `yiyanghkust/finbert-tone-chinese` snapshot
  `e91b1a3af10e1e8c9c03429d3cd7d5e9a1c8000d`.
- General sentiment fallback: `IDEA-CCNL/Erlangshen-Roberta-110M-Sentiment`
  snapshot `7c257c5cde3225d0789acfa8d67eb043289b0295`, recorded but not used
  while FinBERT is available.
- Cross-encoder reranker: `BAAI/bge-reranker-v2-m3` snapshot
  `953dc6f6f85a1b2dbfca4c34a2796e7dde08d41e`.

`N3` now uses local `AutoModelForSequenceClassification` logits when a
sentiment/FinBERT model is configured. `N6` now uses a local pairwise
sequence-classification scorer when the reranker snapshot loads. Both paths
load with `local_files_only=True`.

## Prompt21 Full-Grid Architecture Status

Prompt21 executed the full configured News Overlay grid with local-only
snapshots and checkpoint/resume support.

- GPU tuning selected `gpu010`: BGE + FinBERT, batch 64, max length 256,
  fp16/autocast, CUDA. The selected mixed-model row reached 73.0% peak GPU
  utilization and 62.167% mean utilization; reranker-specific tuning rows
  reached above 90% peak, but the mixed-grid setting did not meet the preferred
  >80% peak target.
- The process-local model cache keeps loaded tokenizer/model objects resident
  while every `from_pretrained` call remains `local_files_only=True`.
- Full 2024 candidate evidence used `real_model_executed` rows only; blocked
  `N7`/`N8` ablation rows were retained as blocked evidence, not promoted.
- Frozen 2025 replay used only the 2024-selected candidate set plus preserved
  controls. It was not used for tuning or reselection.

## Prompt22 Matrix Architecture Status

Prompt22 adds a replay architecture for train/tune matrices that consumes
Prompt21 checkpointed real-local transformer target weights and applies bounded
overlay/gate transformations before official-semantics replay.

- Local HF model loading is not repeated in Prompt22; offline variables are set
  and the runner performs no download or API operation.
- Matrix cache identity is separated from proxy mode by
  `model_mode=cached_real_transformer_replay` and source Prompt21 run ids.
- The 2024 train/tune matrix sweeps overlay strength, impact threshold,
  confidence threshold, sensitivity threshold, turnover cap, and drawdown
  throttle on 2024 only.
- The frozen 2025 matrix accepts only the frozen 2024-selected parameters and
  control rows.
- Runtime evidence is split between Prompt21 direct local-model GPU tuning and
  Prompt22 cached replay scoring; CUDA benefit is not claimed for full
  end-to-end execution from Prompt22 alone.
