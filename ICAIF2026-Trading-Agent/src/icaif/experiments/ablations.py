"""Text ablations as transforms of the text provider (never of raw data stores).

Each ablation answers "does the NLP layer add genuine incremental value?":
  none / no_news           overlay disabled (quant core only)
  zeroed                   finite zero scores (overlay machinery runs, no tilt)
  shuffled                 asset labels permuted per round (keeps distribution)
  wrong_asset              signals rotated to other assets (structured confusion)
  random                   seeded Gaussian scores on the same information mask
  stale:<hours>            text state from AS_OF - offset (date-offset test)
  sign_flip                negated scores (should hurt if signal is real)
Component ablations (relevance-only, sentiment-only, event-only, no-recency,
no-novelty, no-confidence, cap=0, source removal) are TextSignalConfig /
overlay-config variants — see ``component_variants``.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import replace
from datetime import datetime, timedelta
from typing import Any

import numpy as np

from icaif.core.schemas import content_hash
from icaif.runtime.state import TextState

TextProvider = Callable[[datetime], TextState]


def _rng_for(as_of: datetime, seed: int) -> np.random.Generator:
    return np.random.default_rng(int(content_hash([as_of.isoformat(), seed])[:12], 16))


def ablate(provider: TextProvider, kind: str, *, seed: int = 0) -> TextProvider | None:
    if kind in ("none", "full"):
        return provider
    if kind == "no_news":
        return None
    if kind.startswith("stale:"):
        offset = timedelta(hours=float(kind.split(":", 1)[1]))
        return lambda as_of: provider(as_of - offset)

    def wrapped(as_of: datetime) -> TextState:
        ts = provider(as_of)
        info = np.isfinite(ts.score)
        if kind == "zeroed":
            return replace(ts, score=np.where(info, 0.0, np.nan))
        if kind == "sign_flip":
            return replace(ts, score=-ts.score)
        if kind == "random":
            rng = _rng_for(as_of, seed)
            return replace(ts, score=np.where(info, rng.normal(0, np.nanstd(ts.score) or 1.0, ts.score.size), np.nan))
        if kind in ("shuffled", "wrong_asset"):
            if kind == "shuffled":
                perm = _rng_for(as_of, seed).permutation(ts.score.size)
            else:
                perm = np.roll(np.arange(ts.score.size), 5)  # 5 = one sector block -> different sector
            return replace(ts, score=ts.score[perm], confidence=ts.confidence[perm], relevance=ts.relevance[perm],
                           event_multiplier=ts.event_multiplier[perm], article_count=ts.article_count[perm],
                           novelty=ts.novelty[perm], evidence={})
        raise ValueError(f"unknown ablation {kind!r}")

    return wrapped


ABLATIONS = ("no_news", "zeroed", "shuffled", "wrong_asset", "random", "stale:24", "stale:120", "sign_flip", "full")


def component_variants() -> dict[str, dict[str, Any]]:
    """TextSignalConfig overrides for component ablations."""

    return {
        "relevance_only": {"direction": "attention"},
        "sentiment_only": {"relevance_mode": "binary", "direction": "sentiment"},
        "market_sentiment": {"relevance_mode": "uniform", "direction": "sentiment"},
        "event_only": {"relevance_mode": "binary", "direction": "event"},
        "relevance_sentiment": {"direction": "sentiment", "use_event_priors": False},
        "relevance_event": {"direction": "event"},
        "full": {"direction": "sentiment_x_event"},
        "no_recency": {"use_recency": False},
        "no_novelty": {"use_novelty": False},
        "no_confidence": {"use_confidence": False},
    }
