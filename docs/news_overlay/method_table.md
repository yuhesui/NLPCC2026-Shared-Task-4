# News Overlay Method Implementation Table

## Status Legend

| Status | Meaning |
|---|---|
| `documented` | Method policy is documented but code is not implemented by this prompt. |
| `fallback_available` | Deterministic or no-news behavior exists elsewhere and remains usable as fallback/control. |
| `planned_transformer` | Must be implemented as a first-class method in Prompt1-x. |
| `blocked_missing_local_model` | Valid future status when local model assets are unavailable. Rows must remain visible. |

## Substage N: News Analysis, Embedding, and Relevance

| Code | Method | Priority | Role | Transformer used? | Local model required? | Cache required? | Current status | Fallback / unavailable handling |
|---|---|---|---|---|---|---|---|---|
| N0 | no-news / base-only input | control | base/null | no | no | no | fallback_available | Preserve frozen base config with overlay disabled. |
| N1 | deterministic taxonomy + entity/BM25 relevance | fallback | lexical baseline only | no | no | optional | fallback_available | Must remain as safety fallback and lexical comparator. |
| N2 | BGE-style bi-encoder text-to-sector relevance cache | required | main transformer relevance method | yes | yes | yes | planned_transformer | If model missing, mark `blocked_missing_local_model` and fall back to N1. |
| N3 | frozen FinBERT-style aspect-tone classifier | required | contextual tone/aspect feature | yes | yes | yes | planned_transformer | If model missing, mark `blocked_missing_local_model` and fall back to N1 tone proxy. |
| N4 | label-attention / Title2Event-inspired event tagger | required | transformer event typing and argument extraction | yes | yes | yes | planned_transformer | If model missing, preserve schema and use deterministic event taxonomy. |
| N5 | sector-query attention daily news pooling | required | attention aggregation over daily Top-20 news | yes | depends_on_N2_or_local_encoder | yes | planned_transformer | If encoder/cache missing, use N1 relevance-weighted pooling. |
| N6 | cross-encoder sector reranker gate | recommended | high-precision second-stage relevance | yes | yes | yes | planned_transformer | If model missing, skip rerank gate and record blocked status. |
| N7 | temporal lagged-news attention encoder | recommended | narrative persistence over lagged news | yes | depends_on_local_encoder | yes | planned_transformer | If unavailable, use decay-weighted deterministic lag features. |
| N8 | entity-sector graph-attention propagation | ablation/defer | indirect sector relevance | yes | optional | yes | planned_transformer | If unavailable, use static entity-sector mapping only. |
| N12 | N1 + N2 lexical/embedding hybrid | required | robust hybrid relevance | yes | yes_for_N2 | yes | planned_transformer | If N2 missing, degrade visibly to N1 with blocked note. |
| N13 | N1 + N3 lexical/aspect-tone hybrid | required | robust hybrid tone | yes | yes_for_N3 | yes | planned_transformer | If N3 missing, degrade visibly to N1 tone proxy with blocked note. |
| N2345 | N2 + N3 + N4 + N5 transformer-stack | required | primary transformer-first stack | yes | yes | yes | planned_transformer | If any component missing, report component status and use explicit hybrid fallback. |

## Substage I: News Impact Estimation

| Code | Method | Priority | Role | Transformer used? | Local model required? | Cache required? | Current status | Fallback / unavailable handling |
|---|---|---|---|---|---|---|---|---|
| I0 | zero impact | control | null | no | no | no | fallback_available | Preserve as no-news/null impact control. |
| I1 | deterministic event magnitude | fallback | baseline only | no | no | optional | fallback_available | Required lexical impact baseline and fallback. |
| I2 | Permutation-Tested News Attention Index, PT-NAI | required | transparent index | attention_statistical | no | yes | documented | If attention features unavailable, compute deterministic PT-NAI from N1/N12 scalars. |
| I3 | event-study calibrated impact | required | CAR/CAAR impact calibration | no | no | yes | documented | Fit calibration on 2024 only; 2025 frozen evaluation only. |
| I4 | decay-weighted event persistence | required | persistence and novelty control | no | no | yes | documented | Use lagged leakage-safe news only. |
| I5 | impact-gated attention pooling | required | attention impact aggregation | yes | depends_on_N_attention | yes | planned_transformer | If attention unavailable, use deterministic event-magnitude pooling. |
| I6 | transformer aspect-impact aggregator | required | FinBERT/aspect-aware impact score | yes | yes_for_N3 | yes | planned_transformer | If aspect model missing, mark blocked and use deterministic magnitude. |
| I7 | temporal narrative impact encoder | recommended | lagged narrative impact | yes | depends_on_N7 | yes | planned_transformer | If unavailable, use I4 decay persistence. |
| I23 | I2 + I3 NAI plus event-study impact | required | robust impact core | mixed | no | yes | documented | Must separate 2024 calibration from 2025 frozen test. |
| I256 | I2 + I5 + I6 attention/aspect impact stack | required | transformer-impact stack | yes | yes_for_aspect_or_attention | yes | planned_transformer | If transformer components missing, report blocked components and fall back to I23 or I1. |

## Substage S: ETF / Sector News Sensitivity and Overlay Use

| Code | Method | Priority | Role | Transformer used? | Local model required? | Cache required? | Current status | Fallback / unavailable handling |
|---|---|---|---|---|---|---|---|---|
| S0 | no sensitivity / uniform sensitivity | control | null | no | no | no | fallback_available | Preserve as overlay-disabled control. |
| S1 | CAR/CAAR event-study sensitivity matrix | required | event-class sensitivity | no | no | yes | documented | Estimate on 2024 only; freeze before 2025. |
| S2 | Rank-IC Gated Sector News Momentum | required | Track B signal validation | no | no | yes | documented | Compare to Track B lexical control and S1 sector fallback. |
| S3 | Volatility-Scaled Macro News Risk Gate | required | Track A risk gate | no | no | yes | documented | Compare to Track A base risk-parity controls. |
| S4 | Sparse Event-Sensitivity Regression Overlay | required | data-driven sensitivity | no | no | yes | documented | Fit sparse coefficients on 2024 only. |
| S5 | Black-Litterman News View Overlay | recommended | Bayesian view overlay | no | no | yes | documented | Must remain bounded by confidence and turnover gates. |
| S6 | attention-weighted asset sensitivity pooling | required | transformer/attention sensitivity | yes | depends_on_N_attention | yes | planned_transformer | If attention unavailable, fall back to S1/S2 sensitivity. |
| S7 | cross-sectional transformer score-to-tilt gate | ablation | learned score-to-overlay | yes | yes | yes | planned_transformer | Ablation only; cannot promote without strict controls. |
| S12 | S1 + S2 event-study sensitivity + Rank-IC | required | Track B first robust gate | no | no | yes | documented | Required Track B robust comparator. |
| S13 | S1 + S3 event-study sensitivity + macro risk | required | Track A first robust gate | no | no | yes | documented | Required Track A robust comparator. |
| S126 | S1 + S2 + S6 sensitivity stack | required | transformer-aware Track B gate | yes | depends_on_S6 | yes | planned_transformer | If S6 unavailable, report blocked and compare S12 only. |
