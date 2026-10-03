"""Structured event schema and extractors.

Sentiment is one task among several: events carry type, direction,
magnitude, novelty, expected horizon and evidence so overlays can use
event-specific caps and decay. Extractors:

  RuleEventExtractor          keyword patterns per event type (baseline)
  LabelAttentionEventMatcher  encoder similarity to label descriptions
  LLM extraction              icaif.llm.tasks.extract_event (policy-gated)
"""

from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime

import numpy as np

from icaif.core.schemas import Article
from icaif.nlp.embeddings import Encoder, cosine
from icaif.nlp.sentiment import LexiconSentiment

EVENT_TYPES: tuple[str, ...] = (
    "earnings", "guidance", "product", "regulatory", "litigation", "m_and_a", "management",
    "capital_allocation", "analyst_action", "credit", "supply", "demand", "commodity", "rates",
    "fx", "macro", "geopolitical", "sector", "market_wide",
)

LABEL_DESCRIPTIONS: dict[str, str] = {
    "earnings": "quarterly earnings results revenue EPS beat or miss",
    "guidance": "company raises or cuts its outlook forecast guidance",
    "product": "product launch release recall or new technology",
    "regulatory": "regulators approval investigation antitrust FDA SEC rules",
    "litigation": "lawsuit court ruling settlement legal liability",
    "m_and_a": "merger acquisition takeover deal divestiture",
    "management": "CEO CFO executive appointment resignation leadership change",
    "capital_allocation": "share buyback dividend increase debt issuance capital return",
    "analyst_action": "analyst upgrade downgrade price target rating change",
    "credit": "credit rating downgrade bond default borrowing costs",
    "supply": "supply chain disruption shortages production capacity",
    "demand": "customer demand orders sales volumes consumer spending",
    "commodity": "oil gas metals commodity prices",
    "rates": "interest rates Federal Reserve rate decision Treasury yields",
    "fx": "dollar currency exchange rates",
    "macro": "inflation jobs report GDP economic data",
    "geopolitical": "war sanctions tariffs trade tensions elections",
    "sector": "industry wide sector trend peers competitors",
    "market_wide": "stock market broad selloff rally indexes investors",
}

_RULES: dict[str, tuple[str, ...]] = {
    "earnings": (r"\bearnings\b", r"\bEPS\b", r"\bquarterly results\b", r"\brevenue\b", r"\bprofit\b"),
    "guidance": (r"\bguidance\b", r"\boutlook\b", r"\bforecast\b"),
    "product": (r"\blaunch(es|ed)?\b", r"\brecall(s|ed)?\b", r"\bunveil(s|ed)?\b"),
    "regulatory": (r"\bregulator(s|y)?\b", r"\bFDA\b", r"\bantitrust\b", r"\binvestigation\b", r"\bapproval\b"),
    "litigation": (r"\blawsuit\b", r"\bsue[sd]?\b", r"\bsettlement\b", r"\bcourt\b", r"\bjury\b"),
    "m_and_a": (r"\bacquir(e|es|ed|ing)\b", r"\bacquisition\b", r"\bmerger\b", r"\btakeover\b"),
    "management": (r"\bCEO\b", r"\bCFO\b", r"\bresign(s|ed)?\b", r"\bappoint(s|ed)?\b", r"\bsteps down\b"),
    "capital_allocation": (r"\bbuyback\b", r"\brepurchase\b", r"\bdividend\b"),
    "analyst_action": (r"\bupgrade[sd]?\b", r"\bdowngrade[sd]?\b", r"\bprice target\b", r"\banalysts?\b"),
    "credit": (r"\bcredit rating\b", r"\bMoody'?s\b", r"\bS&P Global Ratings\b", r"\bdefault\b"),
    "supply": (r"\bsupply chain\b", r"\bshortage\b", r"\bproduction\b"),
    "demand": (r"\bdemand\b", r"\borders\b", r"\bsales\b"),
    "commodity": (r"\boil prices?\b", r"\bcrude\b", r"\bnatural gas\b", r"\bcopper\b"),
    "rates": (r"\bFed\b", r"\bFederal Reserve\b", r"\binterest rates?\b", r"\byields?\b", r"\bcentral bank\b"),
    "fx": (r"\bdollar\b", r"\bcurrency\b", r"\bexchange rate\b"),
    "macro": (r"\binflation\b", r"\bCPI\b", r"\bpayrolls\b", r"\bGDP\b", r"\beconomic data\b", r"\bjobs report\b"),
    "geopolitical": (r"\btariffs?\b", r"\bsanctions?\b", r"\bwar\b", r"\belection\b"),
    "sector": (r"\bindustry\b", r"\bsector\b", r"\bpeers\b"),
    "market_wide": (r"\bmarkets?\b", r"\bstocks\b", r"\bWall Street\b", r"\bS&P 500\b", r"\bindex(es)?\b"),
}
_COMPILED = {k: [re.compile(p, re.IGNORECASE) for p in v] for k, v in _RULES.items()}


@dataclass(frozen=True)
class Event:
    ticker: str | None  # None for market-wide / macro events
    event_type: str
    direction: int  # -1, 0, +1
    magnitude: float  # [0,1]
    confidence: float  # [0,1]
    novelty: float  # [0,1]
    expected_horizon_hours: float
    source_quality: float  # [0,1]
    published_at: datetime
    available_at: datetime
    evidence: tuple[str, ...]
    extractor: str

    def __post_init__(self) -> None:
        if self.event_type not in EVENT_TYPES:
            raise ValueError(f"unknown event type {self.event_type!r}")
        if self.direction not in (-1, 0, 1):
            raise ValueError("direction must be -1, 0 or +1")


def classify_event_types(text: str) -> dict[str, float]:
    """Rule hits per event type, normalised to [0,1] confidence."""

    out: dict[str, float] = {}
    for etype, pats in _COMPILED.items():
        hits = sum(1 for p in pats if p.search(text))
        if hits:
            out[etype] = min(1.0, 0.4 + 0.2 * hits)
    return out


class RuleEventExtractor:
    model_id = "rule_events_v1"

    def __init__(self, priors: Mapping[str, Mapping[str, float]], sentiment: LexiconSentiment | None = None) -> None:
        self.priors = priors
        self.sentiment = sentiment or LexiconSentiment()

    def extract(self, article: Article, tickers: Sequence[str], *, novelty: float = 1.0,
                source_quality: float = 0.5) -> list[Event]:
        types = classify_event_types(article.text)
        if not types:
            return []
        tone = self.sentiment.score(article.text)
        direction = int(np.sign(tone.score)) if tone.confidence > 0 else 0
        # Most specific type wins; market-wide only if nothing else matched.
        ranked = sorted(types.items(), key=lambda kv: (kv[0] == "market_wide", -kv[1]))
        etype, tconf = ranked[0]
        prior = self.priors.get(etype, {})
        horizon = float(prior.get("half_life_hours", 13.0))
        magnitude = float(prior.get("magnitude", 0.5)) * (abs(tone.score) if direction else 0.5)
        events = []
        targets: list[str | None] = list(tickers) or [None]
        for t in targets:
            events.append(Event(t, etype, direction, magnitude, float(tconf * max(tone.confidence, 0.2)), novelty, horizon,
                                source_quality, article.published_at, article.available_at,
                                tuple(sorted(types)), self.model_id))
        return events


class LabelAttentionEventMatcher:
    """Event-type distribution via softmax attention between the article and
    label descriptions under any :class:`Encoder` (transformer or lexical)."""

    def __init__(self, encoder: Encoder, *, temperature: float = 0.05) -> None:
        self.encoder = encoder
        self.temperature = temperature
        self.model_id = f"label_attention:{encoder.model_id}"
        self._labels = list(EVENT_TYPES)
        self._label_vecs = encoder.encode([LABEL_DESCRIPTIONS[k] for k in self._labels])

    def distribution(self, text: str) -> dict[str, float]:
        sims = cosine(self.encoder.encode([text]), self._label_vecs)[0].astype(np.float64) / self.temperature
        p = np.exp(sims - sims.max())
        p /= p.sum()
        return dict(zip(self._labels, (float(x) for x in p), strict=True))
