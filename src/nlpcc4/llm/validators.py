"""Validation helpers for bounded LLM signals."""

from __future__ import annotations

from typing import Any, Mapping

from nlpcc4.llm.schemas import AlphaSignal, EventExposureSignal, RegimeSignal


def validate_confidence(confidence: float) -> None:
    """Validate normalized confidence values."""
    if not 0.0 <= confidence <= 1.0:
        raise ValueError("confidence must be in [0, 1]")


def validate_regime_signal(data: Mapping[str, Any]) -> RegimeSignal:
    """Validate regime classifier JSON."""
    return RegimeSignal.from_mapping(data)


def validate_alpha_signal(data: Mapping[str, Any]) -> AlphaSignal:
    """Validate alpha-score JSON."""
    return AlphaSignal.from_mapping(data)


def validate_event_exposure_signal(data: Mapping[str, Any]) -> EventExposureSignal:
    """Validate event-exposure JSON."""
    return EventExposureSignal.from_mapping(data)
