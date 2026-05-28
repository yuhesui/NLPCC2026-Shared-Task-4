"""Lightweight causal-shock tags for reporting, not causal claims."""

from __future__ import annotations

from nlpcc.stage1_news.schema import EventTuple


SHOCK_EVENT_TYPES = {"monetary_policy", "fiscal_policy", "geopolitical", "regulation"}


def extract_shock_tags(events: tuple[EventTuple, ...]) -> tuple[str, ...]:
    tags = sorted({event.event_type for event in events if event.event_type in SHOCK_EVENT_TYPES and event.intensity > 0.4})
    return tuple(tags)
