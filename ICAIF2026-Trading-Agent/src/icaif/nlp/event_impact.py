"""Event-type priors: half-life, magnitude and overlay-cap multiplier.

Defaults live in ``configs/news/event_priors.yaml`` and are **uncalibrated
priors** (reasoned guesses). They are research parameters to be estimated by
event studies on pre-period data (docs/research/NEWS_OVERLAY_PLAN.md), never
tuned on the evaluation period.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from icaif.core.config import CONFIG_ROOT, load_config
from icaif.nlp.event_extraction import EVENT_TYPES

DEFAULT_PRIORS_PATH = CONFIG_ROOT / "news" / "event_priors.yaml"


@dataclass(frozen=True)
class EventPrior:
    half_life_hours: float
    magnitude: float
    cap_multiplier: float


def load_event_priors(path: Path = DEFAULT_PRIORS_PATH) -> dict[str, EventPrior]:
    data = load_config(path)["event_priors"]
    missing = set(EVENT_TYPES) - set(data)
    if missing:
        raise ValueError(f"event priors missing types: {sorted(missing)}")
    return {k: EventPrior(float(v["half_life_hours"]), float(v["magnitude"]), float(v.get("cap_multiplier", 1.0)))
            for k, v in data.items()}


def priors_as_mapping(priors: Mapping[str, EventPrior]) -> dict[str, dict[str, float]]:
    return {k: {"half_life_hours": p.half_life_hours, "magnitude": p.magnitude, "cap_multiplier": p.cap_multiplier}
            for k, p in priors.items()}
