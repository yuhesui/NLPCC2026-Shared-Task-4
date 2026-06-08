# News Overlay Method Implementation Table

## Status Legend

| Status | Meaning |
|---|---|
| `documented` | Method policy is documented but code is not implemented by this prompt. |
| `scaffold_registered` | Method has a registry entry, interface stub, availability status handling, and smoke-test coverage. |
| `implemented_cache_backed` | Method has concrete feature-row or impact-row logic, JSON result cache support, traceable status, and tests. |
| `implemented_local_transformer_optional` | Method has local-only transformer encoder integration when configured, plus deterministic unavailable fallback. |
| `interface_scaffold_blocked` | Method interface is present and reports blocked/fallback state until a later prompt adds the full architecture. |
| `fallback_available` | Deterministic or no-news behavior exists elsewhere and remains usable as fallback/control. |
| `planned_transformer` | Must be implemented as a first-class method in Prompt1-x. |
| `blocked_missing_local_model` | Valid future status when local model assets are unavailable. Rows must remain visible. |

## Substage N: News Analysis, Embedding, and Relevance

| Code | Method | Priority | Role | Transformer used? | Local model required? | Cache required? | Current status | Fallback / unavailable handling |
|---|---|---|---|---|---|---|---|---|
| N0 | no-news / base-only input | control | base/null | no | no | no | implemented_cache_backed | Returns empty feature rows so the frozen base allocator can run unchanged. |
| N1 | deterministic taxonomy + entity/BM25 relevance | fallback | lexical baseline only | no | no | optional | implemented_cache_backed | Chinese keyword/entity extraction, taxonomy labels, lexical relevance, duplicate clusters, and fallback rows. |
| N2 | BGE-style bi-encoder text-to-sector relevance cache | required | main transformer relevance method | yes | yes | yes | implemented_local_transformer_optional | Uses local-only transformer embeddings for news and sector prototypes when configured; otherwise `blocked_missing_local_model` with N1 fallback. |
| N3 | frozen FinBERT-style aspect-tone classifier | required | contextual tone/aspect feature | yes | yes | yes | implemented_local_transformer_optional | Uses local transformer aspect-similarity scaling when configured; otherwise complete aspect schema with deterministic tone fallback. |
| N4 | label-attention / Title2Event-inspired event tagger | required | transformer event typing and argument extraction | yes | yes | yes | implemented_local_transformer_optional | Uses local transformer label-description attention when configured; otherwise lexical label probabilities and event arguments. |
| N5 | sector-query attention daily news pooling | required | attention aggregation over daily Top-20 news | yes | depends_on_N2_or_local_encoder | yes | implemented_local_transformer_optional | Uses local transformer sector query/key attention when configured; otherwise lexical softmax attention. |
| N6 | cross-encoder sector reranker gate | recommended | high-precision second-stage relevance | yes | yes | yes | interface_scaffold_blocked | Interface and status handling are present; without a local reranker it reports blocked and falls back to N2. |
| N7 | temporal lagged-news attention encoder | recommended | narrative persistence over lagged news | yes | depends_on_local_encoder | yes | implemented_cache_backed | Lightweight lagged-news attention over short histories with explicit short-history warnings and N1 fallback status. |
| N8 | entity-sector graph-attention propagation | ablation/defer | indirect sector relevance | yes | optional | yes | implemented_cache_backed | Static entity-sector propagation scaffold for ablation; reports missing model assets when transformer graph attention is unavailable. |
| N12 | N1 + N2 lexical/embedding hybrid | required | robust hybrid relevance | yes | yes_for_N2 | yes | implemented_cache_backed | Composite merges component rows and traces N1/N2 statuses. |
| N13 | N1 + N3 lexical/aspect-tone hybrid | required | robust hybrid tone | yes | yes_for_N3 | yes | implemented_cache_backed | Composite merges component rows and traces N1/N3 statuses. |
| N2345 | N2 + N3 + N4 + N5 transformer-stack | required | primary transformer-first stack | yes | yes | yes | implemented_cache_backed | Primary N stack resolves component traces and remains blocked, not omitted, when local assets are unavailable. |

## Substage I: News Impact Estimation

| Code | Method | Priority | Role | Transformer used? | Local model required? | Cache required? | Current status | Fallback / unavailable handling |
|---|---|---|---|---|---|---|---|---|
| I0 | zero impact | control | null | no | no | no | implemented_cache_backed | Emits zero impact rows and no sector impact. |
| I1 | deterministic event magnitude | fallback | baseline only | no | no | optional | implemented_cache_backed | Deterministic event-magnitude fallback from event priors, relevance, tone, confidence, duplicates, and novelty. |
| I2 | Permutation-Tested News Attention Index, PT-NAI | required | transparent index | attention_statistical | no | yes | implemented_cache_backed | Computes NAI from N relevance/tone/label attention/news attention with shuffled-news and random-label hooks. |
| I3 | event-study calibrated impact | required | CAR/CAAR impact calibration | no | no | yes | implemented_cache_backed | Builds 2024-only event-study lookup tables or default priors; refuses calibration rows outside 2024. |
| I4 | decay-weighted event persistence | required | persistence and novelty control | no | no | yes | implemented_cache_backed | Implements novelty, repeated-event dampening, monotone decay weights, and policy-theme persistence. |
| I5 | impact-gated attention pooling | required | attention impact aggregation | yes | depends_on_N_attention | yes | implemented_cache_backed | Computes confidence/novelty/relevance-gated attention; if local impact model missing, reports blocked with deterministic fallback output. |
| I6 | transformer aspect-impact aggregator | required | FinBERT/aspect-aware impact score | yes | yes_for_N3 | yes | implemented_cache_backed | Consumes N3/N2345 aspect-tone rows with sector aspect weights; missing local model reports blocked with fallback output. |
| I7 | temporal narrative impact encoder | recommended | lagged narrative impact | yes | depends_on_N7 | yes | implemented_cache_backed | Consumes lagged NAI/impact history and emits narrative persistence diagnostics; short history is explicit. |
| I23 | I2 + I3 NAI plus event-study impact | required | robust impact core | mixed | no | yes | implemented_cache_backed | Merges I2/I3 component traces and impact summaries. |
| I256 | I2 + I5 + I6 attention/aspect impact stack | required | transformer-impact stack | yes | yes_for_aspect_or_attention | yes | implemented_cache_backed | Merges I2/I5/I6 traces and stays blocked, not omitted, when local impact assets are unavailable. |

## Substage S: ETF / Sector News Sensitivity and Overlay Use

| Code | Method | Priority | Role | Transformer used? | Local model required? | Cache required? | Current status | Fallback / unavailable handling |
|---|---|---|---|---|---|---|---|---|
| S0 | no sensitivity / uniform sensitivity | control | null | no | no | no | implemented_cache_backed | Overlay-disabled control returns base weights unchanged. |
| S1 | CAR/CAAR event-study sensitivity matrix | required | event-class sensitivity | no | no | yes | implemented_cache_backed | Builds 2024-only CAR/CAAR sensitivity rows or default shrunk priors and emits bounded overlays. |
| S2 | Rank-IC Gated Sector News Momentum | required | Track B signal validation | no | no | yes | implemented_cache_backed | Track B Rank-IC gate uses 2024-only threshold rows and bounded sector tilts. |
| S3 | Volatility-Scaled Macro News Risk Gate | required | Track A risk gate | no | no | yes | implemented_cache_backed | Track A macro risk multiplier is bounded and redistributes between risky and defensive assets. |
| S4 | Sparse Event-Sensitivity Regression Overlay | required | data-driven sensitivity | no | no | yes | implemented_cache_backed | Uses 2024-only univariate ridge-style sparse coefficients with S1 fallback when rows are missing. |
| S5 | Black-Litterman News View Overlay | recommended | Bayesian view overlay | no | no | yes | implemented_cache_backed | Shrunk BL-style news-view proxy uses diagonal volatility and singularity-safe bounded overlays. |
| S6 | attention-weighted asset sensitivity pooling | required | transformer/attention sensitivity | yes | depends_on_N_attention | yes | implemented_cache_backed | Consumes attention/relevance/confidence impact rows; missing local S assets report `blocked_missing_local_model` with S1 fallback output. |
| S7 | cross-sectional transformer score-to-tilt gate | ablation | learned score-to-overlay | yes | yes | yes | implemented_cache_backed | Ablation-only bounded score-to-tilt gate; never an unconstrained allocator. |
| S12 | S1 + S2 event-study sensitivity + Rank-IC | required | Track B first robust gate | no | no | yes | implemented_cache_backed | Composite merges S1/S2 bounded overlays and component traces. |
| S13 | S1 + S3 event-study sensitivity + macro risk | required | Track A first robust gate | no | no | yes | implemented_cache_backed | Composite merges S1/S3 bounded overlays and component traces. |
| S126 | S1 + S2 + S6 sensitivity stack | required | transformer-aware Track B gate | yes | depends_on_S6 | yes | implemented_cache_backed | Composite remains visible and blocked when S6 local assets are unavailable; S12 fallback is explicit. |

## Prompt09 Verification Note

Prompt09 corrected the reference status table so `N3` is explicitly recorded as
component-level proxy evidence through `N13` and `N2345` component traces. This
does not promote `N3`: real local FinBERT/aspect-tone assets are still missing,
and the method remains `blocked_missing_local_model` outside proxy mode.

## Prompt20 Local Transformer Revalidation Note

Prompt20 added explicit Hugging Face download-once mode and downloaded the
approved pinned `BAAI/bge-small-zh-v1.5` snapshot to the user's Hugging Face
cache. Local-only, no-proxy smokes now report `real_model_executed` for `N2`,
`N3` real-encoder aspect similarity, `N4`, `N5`, `N12`, `N13`, `N2345`, `I5`,
`I6`, `I256`, `S6`, and `S126`, with `network_attempted=false` and
`local_files_only=True` after download. `N6` remains
`blocked_missing_local_model` because no true cross-encoder implementation or
enabled reranker snapshot is present. The optional FinBERT-style classifier is
recorded as approved metadata but remains disabled; `N3` should be described as
real BGE encoder evidence, not true FinBERT classifier execution.
