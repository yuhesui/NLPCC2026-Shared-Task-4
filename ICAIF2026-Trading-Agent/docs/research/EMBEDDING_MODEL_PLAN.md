# Embedding / relevance model plan

Question: which representation gives the most *downstream, fee-adjusted, point-in-time* value for
asset-conditioned relevance (and label-attention event typing) — not which gets the best retrieval score.

## 1. Policy status (configs/embeddings/registry.yaml)

The organizer list restricts **generative LLMs** to named families. **Team ruling (2026-10-03,
Q1 resolved): non-LLM encoders are permitted; a publicly available model run locally on the team's own
machine is acceptable.** Paid or third-party hosted embedding APIs remain excluded. The
`requires_rule_confirmation` flag and `nlp.embeddings.check_policy` stay in place for any future ambiguous entry.

| Category | Models |
|---|---|
| Permitted and ready (needs a local snapshot) | lexical/entity baseline; feature-hashing encoder; all-MiniLM-L6-v2, bge-small/base-en-v1.5, e5-base-v2, gte-base-en-v1.5, nomic-embed-text-v1.5 (generic); ms-marco MiniLM cross-encoder, bge-reranker-base (rerankers); ProsusAI/finbert, finbert-tone (tone); FinLang finance-embeddings; Qwen3-Embedding-0.6B, Qwen3-Reranker-0.6B, EmbeddingGemma-300m; Qwen3-0.6B mean-pooled (disclosed as LLM use) |
| Unsuitable | bge-small-zh, finbert-tone-chinese (language; NLPCC legacy); voyage-finance-2, OpenAI text-embedding-3 (paid hosted, not local) |
| Deferred | Qwen3-Embedding-4B/8B (cost), LLM2Vec-style conversions |

Model files are **never downloaded by code in this repository**. A human downloads a pinned revision
once, records it (model id, revision, licence, sha256 of weights, date) and sets `local_path`.
The runtime sets `HF_HUB_OFFLINE=1` and `local_files_only=True`.

## 2. Interface

`nlp.relevance.score_relevance(article, asset, context) -> RelevanceResult(relevance, confidence,
evidence, model_id, inferred_at, status)` with implementations: `LexicalEntityRelevance`,
`DenseRelevance(encoder)`, `LocalCrossEncoderRelevance`, `HybridRelevance`, and the LLM judge
(`llm.tasks.classify_relevance`). Asset queries are the hand-written `ASSET_PROFILES`; a variant
uses 10-K business descriptions (EDGAR, available before the period).

## 3. Experiments

**E0 baselines**: lexical/entity; hashing encoder (dense_hash); hybrid_hash. *(runnable now)*
**E1 frozen generic encoders**: MiniLM, bge-small/base-en, e5-base, gte-base, nomic — cosine vs profile, softmax over 30 assets.
**E2 finance-domain**: FinLang embeddings; FinBERT [CLS]/mean-pool (tone model as encoder, expected weak).
**E3 allowed-family LLM encoders**: Qwen3-0.6B mean-pool, Qwen3-Embedding-0.6B (if confirmed), EmbeddingGemma.
**E4 fine-tuned bi-encoders** (FINETUNING_PLAN Stage B): best of E1–E3 + MNRL / triplet / contrastive.
**E5 rerankers**: cross-encoder over top-5 assets from E1/E4.
**E6 hybrids**: entity ∨ dense with sector spill-over, weight grid.
**E7 LLM relevance judge** (allowed hosted model) on a sampled subset for labelling and as a ceiling.

Negatives for every learned/evaluated model: random company, same-sector hard, most-correlated company
(covariance estimated before the article), market-wide article, temporally adjacent unrelated article,
same-company stale repeat (`models/text/pairs.py` builds all six).

## 4. Metrics

Retrieval (on a temporally held-out labelled set): Recall@1/3/5, MRR, NDCG@5, calibration (ECE of
relevance as probability), same-sector confusion rate, direct-entity precision (articles naming the
company). **Downstream** (required for promotion): rank-IC of the per-asset text score with next
1h/1d/5d idiosyncratic return; portfolio CR, Sharpe, MDD, turnover, fees and rank-objective delta versus
(a) the same system with `overlay.enabled: false` and (b) the lexical baseline, across walk-forward windows.

## 5. Promotion rule

An encoder is promoted only if, on locked validation windows: downstream rank-objective improves over both
no-news and lexical controls in a majority of windows; the improvement survives the shuffled /
wrong-asset / sign-flip ablations (which must degrade it); turnover-adjusted CR does not fall; its
registry status is `ready`. Better Recall@K alone never promotes a model.

## 6. Status

Interfaces, policy gate, registry and E0 are implemented and tested. E1–E3, E5, E6 are now policy-cleared
and **blocked only on local model files** (manual pinned download); E4 also needs labelled real data; E7
needs an LLM client.
