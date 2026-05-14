"""Simple deterministic news features for baselines and LLM prompts."""

from __future__ import annotations

from typing import Mapping, Sequence


POSITIVE_TERMS = (
    "easing",
    "support",
    "stimulus",
    "recovery",
    "positive",
    "growth",
    "liquidity",
    "policy",
)
NEGATIVE_TERMS = (
    "risk",
    "slowdown",
    "default",
    "tightening",
    "decline",
    "pressure",
    "regulation",
    "volatility",
)


def _text(item: Mapping) -> str:
    return f"{item.get('TITLE', item.get('title', ''))} {item.get('CONTENT', item.get('content', ''))}".lower()


def news_sentiment_score(news: Sequence[Mapping]) -> float:
    """Return a bounded deterministic sentiment score in [-1, 1]."""
    if not news:
        return 0.0
    score = 0.0
    total_weight = 0.0
    for item in news:
        text = _text(item)
        ranking = item.get("RANKING", item.get("ranking", 10)) or 10
        weight = 1.0 / max(float(ranking), 1.0)
        local = sum(term in text for term in POSITIVE_TERMS) - sum(term in text for term in NEGATIVE_TERMS)
        score += weight * local
        total_weight += weight * max(abs(local), 1)
    if total_weight <= 0:
        return 0.0
    return max(-1.0, min(1.0, score / total_weight))


def keyword_exposure_scores(news: Sequence[Mapping], keyword_map: Mapping[str, Sequence[str]]) -> dict[str, float]:
    """Map news keywords to bounded exposure scores by asset/group."""
    scores = {asset: 0.0 for asset in keyword_map}
    if not news:
        return scores
    for item in news:
        text = _text(item)
        ranking = item.get("RANKING", item.get("ranking", 10)) or 10
        weight = 1.0 / max(float(ranking), 1.0)
        for asset, keywords in keyword_map.items():
            hits = sum(1 for keyword in keywords if keyword.lower() in text)
            if hits:
                scores[asset] += weight * hits
    max_abs = max((abs(value) for value in scores.values()), default=0.0)
    if max_abs <= 0:
        return scores
    return {asset: max(-1.0, min(1.0, value / max_abs)) for asset, value in scores.items()}
