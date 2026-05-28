"""Deterministic decayed event memory."""

from __future__ import annotations

from collections import defaultdict
from math import pow

from nlpcc.stage2_text_store.schema import DecayedEventMemory, EventTableRow


def decay_weight(age_days: float, half_life_days: float) -> float:
    """Return exponential half-life decay weight."""

    if half_life_days <= 0:
        raise ValueError("half_life_days must be positive")
    if age_days < 0:
        raise ValueError("age_days must be non-negative")
    return pow(0.5, age_days / half_life_days)


def build_decayed_event_memory(
    event_table: tuple[EventTableRow, ...],
    *,
    as_of_date_int: int | None = None,
    half_life_days: float = 5.0,
    age_days_by_event_id: dict[str, float] | None = None,
) -> DecayedEventMemory:
    """Aggregate event signals with deterministic exponential decay."""

    ages = age_days_by_event_id or {}
    features: dict[str, float] = defaultdict(float)
    for event in event_table:
        age_days = float(ages.get(event.event_id, 0.0))
        weight = decay_weight(age_days, half_life_days)
        contribution = event.signed_intensity * event.confidence * weight * event.duplicate_count
        features[f"memory.sector.{event.sector}.signal"] += contribution
        features[f"memory.event_type.{event.event_type}.signal"] += contribution

    rounded = {key: round(value, 8) for key, value in sorted(features.items())}
    return DecayedEventMemory(
        as_of_date_int=as_of_date_int,
        features=rounded,
        decay_half_life_days=half_life_days,
        event_count=len(event_table),
    )
