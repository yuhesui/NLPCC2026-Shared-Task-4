"""Narrow Prompt02 search spaces and deterministic fallback sampler."""

from __future__ import annotations

from collections.abc import Mapping
import hashlib
import random
from typing import Any


COMMON_SPACE: dict[str, tuple[float, float]] = {
    "overlay_scale": (0.35, 1.05),
    "gate_threshold": (0.0, 0.08),
    "deadband": (0.0, 0.012),
    "confidence_cap": (0.006, 0.03),
    "turnover_penalty_weight": (0.05, 0.35),
    "fallback_threshold": (0.0, 0.25),
    "max_abs_overlay": (0.004, 0.025),
}


SPECIFIC_SPACE: dict[str, dict[str, tuple[float, float]]] = {
    "B1": {
        "n4_relevance_floor": (0.0, 0.15),
        "n4_label_smoothing": (0.0, 0.20),
        "i6_aspect_weight": (0.60, 1.30),
        "s2_sector_shrink": (0.45, 1.00),
        "h1_hook_strength": (0.0, 0.0),
        "h5_hook_strength": (0.0, 0.0),
    },
    "B2": {
        "n4_relevance_floor": (0.0, 0.15),
        "n4_label_smoothing": (0.0, 0.20),
        "i6_aspect_weight": (0.60, 1.30),
        "s2_sector_shrink": (0.45, 1.00),
        "h1_hook_strength": (0.20, 0.85),
        "h5_hook_strength": (0.20, 0.85),
    },
    "B3": {
        "consensus_shrink": (0.35, 0.85),
        "dominance_cap": (0.20, 0.55),
        "bl_confidence_cap": (0.008, 0.025),
        "event_count_floor": (1.0, 4.0),
        "weak_signal_deadband": (0.001, 0.015),
        "safe_fallback_weight": (0.0, 0.60),
    },
    "A1": {
        "macro_overlay_scale": (0.30, 1.00),
        "h4_strength": (0.25, 0.95),
        "composite_shrink": (0.40, 1.00),
        "aspect_tone_weight": (0.60, 1.30),
        "signal_deadband": (0.0, 0.015),
    },
    "A2": {
        "macro_overlay_scale": (0.30, 1.00),
        "h4_strength": (0.0, 0.40),
        "composite_shrink": (0.50, 1.00),
        "aspect_tone_weight": (0.60, 1.30),
        "signal_deadband": (0.0, 0.015),
    },
}


def candidate_search_space(candidate_id: str) -> dict[str, tuple[float, float]]:
    """Return a bounded search space for one candidate id."""

    if candidate_id not in SPECIFIC_SPACE:
        return {}
    return {**COMMON_SPACE, **SPECIFIC_SPACE[candidate_id]}


def deterministic_trials(candidate_id: str, *, count: int, seed: int = 202602) -> list[dict[str, float]]:
    """Sample bounded trial params with deterministic random search fallback."""

    space = candidate_search_space(candidate_id)
    rng = random.Random(seed + int(hashlib.sha256(candidate_id.encode("utf-8")).hexdigest()[:8], 16))
    rows: list[dict[str, float]] = [midpoint(space)]
    while len(rows) < count:
        rows.append({name: round(rng.uniform(low, high), 6) for name, (low, high) in space.items()})
    return rows[:count]


def midpoint(space: Mapping[str, tuple[float, float]]) -> dict[str, float]:
    return {name: round((low + high) / 2.0, 6) for name, (low, high) in space.items()}


def params_hash(params: Mapping[str, Any]) -> str:
    payload = "|".join(f"{key}={params[key]}" for key in sorted(params))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:16]
