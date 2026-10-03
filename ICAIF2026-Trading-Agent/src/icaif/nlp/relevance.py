"""Asset-conditioned relevance: ``score_relevance(article, asset, context) -> RelevanceResult``.

Implementations (compare them; do not assume one wins):
  lexical_entity     entity-linking evidence only (deterministic baseline)
  dense              cosine(article, asset profile) with any Encoder
  cross_encoder      local cross-encoder reranker (optional dependency)
  hybrid             max/weighted blend of entity + dense evidence
  llm_judge          structured LLM judgement (icaif.llm; policy-gated)
"""

from __future__ import annotations

import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Protocol

import numpy as np

from icaif.core.schemas import Article
from icaif.core.time import utc_now
from icaif.core.universe import SECTOR_OF, SYMBOLS
from icaif.nlp.embeddings import Encoder, EncoderSpec, ModelUnavailable, cosine
from icaif.nlp.entity_linking import ALIASES, link_entities

# Short business profiles used as bi-encoder "queries" (hand-written, editable).
ASSET_PROFILES: dict[str, str] = {
    "AAPL": "Apple consumer electronics iPhone Mac services App Store",
    "MSFT": "Microsoft software cloud Azure Windows Office AI",
    "NVDA": "Nvidia GPUs semiconductors AI data center chips",
    "INTC": "Intel semiconductors CPUs foundry chip manufacturing",
    "CRM": "Salesforce enterprise software CRM cloud subscriptions",
    "JPM": "JPMorgan Chase bank lending investment banking trading",
    "BAC": "Bank of America consumer banking loans deposits interest rates",
    "GS": "Goldman Sachs investment banking trading asset management",
    "V": "Visa payments card network transaction volumes",
    "PYPL": "PayPal digital payments Venmo checkout fintech",
    "LLY": "Eli Lilly pharmaceuticals diabetes obesity drugs clinical trials",
    "JNJ": "Johnson & Johnson pharmaceuticals medical devices litigation",
    "UNH": "UnitedHealth health insurance Medicare Optum",
    "PFE": "Pfizer pharmaceuticals vaccines drug pipeline",
    "TMO": "Thermo Fisher life sciences laboratory instruments diagnostics",
    "AMZN": "Amazon e-commerce retail AWS cloud logistics advertising",
    "TSLA": "Tesla electric vehicles batteries autonomous driving energy",
    "WMT": "Walmart retail grocery consumer spending stores",
    "NKE": "Nike footwear apparel sportswear consumer brand",
    "KO": "Coca-Cola beverages soft drinks consumer staples",
    "CAT": "Caterpillar construction mining machinery equipment",
    "GE": "GE Aerospace jet engines aviation defense",
    "BA": "Boeing aircraft manufacturing airlines defense",
    "XOM": "Exxon Mobil oil gas production refining energy",
    "CVX": "Chevron oil gas production refining energy",
    "GOOGL": "Alphabet Google search advertising YouTube cloud AI",
    "META": "Meta Platforms Facebook Instagram social media advertising",
    "DIS": "Disney media entertainment streaming parks",
    "T": "AT&T telecommunications wireless broadband",
    "NEE": "NextEra Energy electric utility renewables power generation",
}


@dataclass(frozen=True)
class RelevanceResult:
    asset: str
    relevance: float  # [0,1]
    confidence: float  # [0,1]
    evidence: tuple[str, ...]
    model_id: str
    inferred_at: datetime = field(default_factory=utc_now)
    status: str = "ok"  # ok | blocked_missing_local_model | policy_blocked


@dataclass(frozen=True)
class RelevanceContext:
    decision_time: datetime | None = None
    live: bool = False
    extra: Mapping[str, Any] = field(default_factory=dict)


class RelevanceScorer(Protocol):
    model_id: str

    def score_relevance(self, article: Article, asset: str, context: RelevanceContext) -> RelevanceResult: ...


class LexicalEntityRelevance:
    """Relevance from entity mentions: title mentions weigh more than body."""

    model_id = "lexical_entity_v1"

    def score_relevance(self, article: Article, asset: str, context: RelevanceContext) -> RelevanceResult:
        title_m = [m for m in link_entities(article.title) if m.symbol == asset]
        body_m = [m for m in link_entities(article.body) if m.symbol == asset]
        explicit = asset in article.tickers
        if not (title_m or body_m or explicit):
            return RelevanceResult(asset, 0.0, 0.6, (), self.model_id)
        conf = max([m.confidence for m in title_m + body_m] + ([0.9] if explicit else []))
        rel = min(1.0, (0.7 if title_m else 0.0) + 0.1 * min(3, len(body_m)) + (0.3 if explicit else 0.0))
        rel = max(rel, 0.4)
        evidence = tuple(dict.fromkeys(m.text for m in title_m + body_m))[:5]
        return RelevanceResult(asset, rel, conf, evidence, self.model_id)


class DenseRelevance:
    """Cosine similarity between the article and an asset profile, calibrated
    to [0,1] by a per-article softmax over the 30 assets (relative relevance)."""

    def __init__(self, encoder: Encoder, *, temperature: float = 0.05, profiles: Mapping[str, str] | None = None) -> None:
        self.encoder = encoder
        self.model_id = f"dense:{encoder.model_id}"
        self.temperature = temperature
        self.profiles = dict(profiles or ASSET_PROFILES)
        self._asset_vecs = encoder.encode([self.profiles[s] for s in SYMBOLS])
        self._cache: dict[str, np.ndarray] = {}

    def _probs(self, article: Article) -> np.ndarray:
        key = article.record_id
        if key not in self._cache:
            sims = cosine(self.encoder.encode([article.text]), self._asset_vecs)[0]
            z = sims / self.temperature
            p = np.exp(z - z.max())
            self._cache[key] = p / p.sum()
        return self._cache[key]

    def score_relevance(self, article: Article, asset: str, context: RelevanceContext) -> RelevanceResult:
        p = self._probs(article)
        j = SYMBOLS.index(asset)
        rel = float(min(1.0, p[j] * len(SYMBOLS) / 4.0))  # 4x uniform share -> relevance 1
        conf = float(np.clip(p.max() * len(SYMBOLS) / 10.0, 0.0, 1.0))
        return RelevanceResult(asset, rel, conf, (f"p={p[j]:.3f}",), self.model_id)


class LocalCrossEncoderRelevance:
    """Local cross-encoder reranker (e.g. an MS-MARCO MiniLM cross-encoder). Optional."""

    def __init__(self, spec: EncoderSpec) -> None:
        self.model_id = f"cross:{spec.model_id}"
        if not spec.local_path or not Path(os.path.expanduser(spec.local_path)).exists():
            raise ModelUnavailable(f"{spec.model_id}: local cross-encoder not found")
        os.environ.setdefault("HF_HUB_OFFLINE", "1")
        try:
            from sentence_transformers import CrossEncoder  # type: ignore[import-not-found]
        except ImportError as error:
            raise ModelUnavailable("sentence-transformers not installed") from error
        self._model = CrossEncoder(os.path.expanduser(spec.local_path), local_files_only=True)

    def score_relevance(self, article: Article, asset: str, context: RelevanceContext) -> RelevanceResult:
        logit = float(self._model.predict([(ASSET_PROFILES[asset], article.text)])[0])
        rel = float(1.0 / (1.0 + np.exp(-logit)))
        return RelevanceResult(asset, rel, abs(2 * rel - 1), (f"logit={logit:.2f}",), self.model_id)


class HybridRelevance:
    """Entity evidence dominates; dense similarity adds indirect exposure
    (e.g. sector/commodity news) at a discount."""

    def __init__(self, lexical: RelevanceScorer, dense: RelevanceScorer, *, dense_weight: float = 0.5,
                 sector_spillover: float = 0.0) -> None:
        self.lexical, self.dense = lexical, dense
        self.dense_weight, self.sector_spillover = dense_weight, sector_spillover
        self.model_id = f"hybrid({lexical.model_id},{dense.model_id},w={dense_weight},s={sector_spillover})"

    def score_relevance(self, article: Article, asset: str, context: RelevanceContext) -> RelevanceResult:
        lex = self.lexical.score_relevance(article, asset, context)
        den = self.dense.score_relevance(article, asset, context)
        rel = max(lex.relevance, self.dense_weight * den.relevance)
        if self.sector_spillover > 0 and lex.relevance == 0:
            peers = [s for s in SYMBOLS if SECTOR_OF[s] == SECTOR_OF[asset] and s != asset]
            if any(self.lexical.score_relevance(article, p, context).relevance > 0 for p in peers):
                rel = max(rel, self.sector_spillover)
        conf = max(lex.confidence if lex.relevance > 0 else 0.0, den.confidence * self.dense_weight)
        return RelevanceResult(asset, float(rel), float(conf), lex.evidence + den.evidence, self.model_id)


def relevance_matrix(scorer: RelevanceScorer, articles: Sequence[Article], context: RelevanceContext,
                     assets: Sequence[str] = SYMBOLS) -> tuple[np.ndarray, np.ndarray]:
    rel = np.zeros((len(articles), len(assets)))
    conf = np.zeros_like(rel)
    for i, a in enumerate(articles):
        for j, s in enumerate(assets):
            r = scorer.score_relevance(a, s, context)
            rel[i, j], conf[i, j] = r.relevance, r.confidence
    return rel, conf


__all__ = ["ALIASES", "ASSET_PROFILES", "DenseRelevance", "HybridRelevance", "LexicalEntityRelevance",
           "LocalCrossEncoderRelevance", "RelevanceContext", "RelevanceResult", "RelevanceScorer", "relevance_matrix"]
