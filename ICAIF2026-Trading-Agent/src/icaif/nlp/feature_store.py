"""Article feature cache and point-in-time aggregation into :class:`TextState`.

Two layers:

1. **Article features** (time-independent): relevance per asset, tone,
   events. Content-addressed cache keyed by (record id, content hash, model
   ids, config hash). Each entry records the model ids so a decision can
   assert the model was not trained on later data.
2. **Aggregation at AS_OF** (time-dependent): only articles with
   ``available_at <= as_of`` (via ``PITStore``), recency-decayed with
   event-specific half-lives, novelty-weighted, shrunk toward zero when
   evidence is thin. Component switches implement the ablations in
   ``docs/research/NEWS_OVERLAY_PLAN.md``.

Novelty is computed by greedy near-duplicate clustering in availability
order, which is causal (an article's novelty depends only on earlier ones),
so precomputing it over the full history is point-in-time safe.
"""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

import numpy as np

from icaif.core.config import config_hash
from icaif.core.leakage_guard import assert_model_cutoff
from icaif.core.schemas import Article
from icaif.core.universe import N_ASSETS, SYMBOLS
from icaif.data.point_in_time import PITStore
from icaif.nlp.entity_linking import linked_symbols
from icaif.nlp.event_extraction import RuleEventExtractor
from icaif.nlp.event_impact import EventPrior
from icaif.nlp.preprocessing import clean_article, near_duplicate_clusters, novelty_by_record
from icaif.nlp.recency import age_hours, decay_weight
from icaif.nlp.relevance import RelevanceContext, RelevanceScorer
from icaif.nlp.sentiment import LexiconSentiment
from icaif.nlp.uncertainty import evidence_confidence
from icaif.runtime.state import TextState


@dataclass(frozen=True)
class TextSignalConfig:
    lookback_hours: float = 120.0
    default_half_life_hours: float = 13.0
    clock: str = "wall"  # wall | trading
    min_relevance: float = 0.3
    prior_strength: float = 0.5  # shrinkage pseudo-weight toward 0
    min_weight: float = 0.05  # below this total weight -> NaN (no information)
    direction: str = "sentiment"  # sentiment | event | attention | sentiment_x_event
    relevance_mode: str = "weighted"  # weighted | binary (linked yes/no) | uniform (every asset)
    use_recency: bool = True
    use_novelty: bool = True
    use_confidence: bool = True
    use_event_priors: bool = True
    languages: tuple[str, ...] = ("en", "und")
    evidence_per_asset: int = 3

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any] | None) -> TextSignalConfig:
        data = dict(data or {})
        if "languages" in data:
            data["languages"] = tuple(data["languages"])
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


@dataclass(frozen=True)
class ArticleFeatures:
    record_id: str
    relevance: tuple[float, ...]  # per asset
    relevance_conf: tuple[float, ...]
    tone: float
    tone_conf: float
    event_type: str | None
    event_direction: int
    model_ids: tuple[str, ...]


class ArticleFeatureCache:
    """In-memory cache with optional JSONL persistence (data/cache/text_features/)."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path
        self._rows: dict[str, ArticleFeatures] = {}
        if path is not None and path.exists():
            for line in path.read_text(encoding="utf-8").splitlines():
                row = json.loads(line)
                key = row.pop("cache_key")
                row["relevance"] = tuple(row["relevance"])
                row["relevance_conf"] = tuple(row["relevance_conf"])
                row["model_ids"] = tuple(row["model_ids"])
                self._rows[key] = ArticleFeatures(**row)

    def get(self, key: str) -> ArticleFeatures | None:
        return self._rows.get(key)

    def put(self, key: str, value: ArticleFeatures) -> None:
        self._rows[key] = value
        if self.path is not None:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as stream:
                stream.write(json.dumps({"cache_key": key, **asdict(value)}) + "\n")


@dataclass
class TextStateBuilder:
    """Callable ``as_of -> TextState`` for the backtester and live runner."""

    articles: Sequence[Article]
    relevance: RelevanceScorer
    priors: Mapping[str, EventPrior]
    config: TextSignalConfig = field(default_factory=TextSignalConfig)
    sentiment: Any = field(default_factory=LexiconSentiment)
    cache: ArticleFeatureCache = field(default_factory=ArticleFeatureCache)
    model_trained_through: datetime | None = None
    failed_sources: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        cleaned = [clean_article(a) for a in self.articles]
        cleaned = [a for a in cleaned if a.language in self.config.languages]
        self._store: PITStore[Article] = PITStore(cleaned)
        self._novelty = novelty_by_record(near_duplicate_clusters(list(self._store.all_records)))
        self._events = RuleEventExtractor({k: {"half_life_hours": p.half_life_hours, "magnitude": p.magnitude}
                                           for k, p in self.priors.items()}, LexiconSentiment())
        self._model_ids = (self.relevance.model_id, getattr(self.sentiment, "model_id", "?"), self._events.model_id)
        self._cfg_hash = config_hash(asdict(self.config))

    # -- per-article features -------------------------------------------------
    def features(self, article: Article) -> ArticleFeatures:
        key = f"{article.record_id}:{article.provenance.content_hash[:12]}:{'|'.join(self._model_ids)}:{self._cfg_hash}"
        hit = self.cache.get(key)
        if hit is not None:
            return hit
        ctx = RelevanceContext()
        rel, conf = [], []
        for s in SYMBOLS:
            r = self.relevance.score_relevance(article, s, ctx)
            rel.append(r.relevance)
            conf.append(r.confidence)
        tone = self.sentiment.score(article.text)
        tickers = [s for s in linked_symbols(article.text)]
        events = self._events.extract(article, tickers)
        etype = events[0].event_type if events else None
        edir = events[0].direction if events else 0
        feats = ArticleFeatures(article.record_id, tuple(rel), tuple(conf), tone.score, tone.confidence, etype, edir,
                                self._model_ids)
        self.cache.put(key, feats)
        return feats

    # -- aggregation -----------------------------------------------------------
    def __call__(self, as_of: datetime) -> TextState:
        assert_model_cutoff(self.model_trained_through, as_of, model_id="|".join(self._model_ids))
        cfg = self.config
        start = as_of - timedelta(hours=cfg.lookback_hours)
        visible = self._store.window(as_of, start)
        n = N_ASSETS
        num = np.zeros(n)
        den = np.zeros(n)
        conf_mass = np.zeros(n)
        rel_max = np.zeros(n)
        evm = np.ones(n)
        count = np.zeros(n)
        nov_sum = np.zeros(n)
        evidence: dict[str, list[dict[str, Any]]] = {}
        for article in visible:
            f = self.features(article)
            rel = np.asarray(f.relevance)
            rel = np.where(rel >= cfg.min_relevance, rel, 0.0)
            if cfg.relevance_mode == "binary":
                rel = (rel > 0).astype(float)
            elif cfg.relevance_mode == "uniform":
                rel = np.full(n, 1.0)
            elif cfg.relevance_mode != "weighted":
                raise ValueError(f"unknown relevance_mode {cfg.relevance_mode!r}")
            if not rel.any():
                continue
            prior = self.priors.get(f.event_type) if (cfg.use_event_priors and f.event_type) else None
            half_life = prior.half_life_hours if prior else cfg.default_half_life_hours
            age = age_hours(article.available_at, as_of, clock=cfg.clock)
            w_time = decay_weight(age, half_life) if cfg.use_recency else 1.0
            novelty = self._novelty.get(article.record_id, 1.0) if cfg.use_novelty else 1.0
            conf = f.tone_conf if cfg.use_confidence else 1.0
            direction = self._direction(f, prior)
            w = rel * w_time * novelty
            num += w * direction * (conf if cfg.use_confidence else 1.0)
            den += w
            conf_mass += w * (conf if cfg.use_confidence else 1.0)
            rel_max = np.maximum(rel_max, rel * w_time)
            if prior is not None:
                evm = np.where(rel > 0, np.maximum(evm, prior.cap_multiplier), evm)
            count += rel > 0
            nov_sum += (rel > 0) * novelty
            for j in np.flatnonzero(rel > 0):
                evidence.setdefault(SYMBOLS[j], []).append({
                    "record_id": article.record_id, "title": article.title[:160], "age_hours": round(age, 2),
                    "relevance": round(float(rel[j]), 3), "tone": round(f.tone, 3), "event_type": f.event_type,
                    "weight": round(float(w[j]), 4)})
        with np.errstate(invalid="ignore", divide="ignore"):
            score = num / (den + cfg.prior_strength)
            novelty_mean = np.where(count > 0, nov_sum / np.maximum(count, 1), 0.0)
        score = np.where(den >= cfg.min_weight, score, np.nan)
        confidence = np.array([evidence_confidence([m], [1.0]) for m in conf_mass])
        for s in evidence:
            evidence[s] = sorted(evidence[s], key=lambda e: -e["weight"])[: cfg.evidence_per_asset]
        return TextState(score=score, confidence=confidence, relevance=rel_max, event_multiplier=evm,
                         article_count=count, novelty=novelty_mean, evidence=evidence,
                         sources_failed=self.failed_sources, model_ids=self._model_ids)

    def _direction(self, f: ArticleFeatures, prior: EventPrior | None) -> float:
        mode = self.config.direction
        if mode == "sentiment":
            return f.tone
        if mode == "event":
            return float(f.event_direction) * (prior.magnitude if prior else 0.5)
        if mode == "attention":
            return 1.0
        if mode == "sentiment_x_event":
            return f.tone * (prior.magnitude if prior else 0.5)
        raise ValueError(f"unknown direction mode {mode!r}")
