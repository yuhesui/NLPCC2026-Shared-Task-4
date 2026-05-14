"""Structured schemas for bounded LLM signals."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


REGIME_LABELS = {
    "risk_on",
    "risk_off",
    "policy_easing",
    "growth_slowdown",
    "inflation_commodity",
    "sector_policy_positive",
    "uncertain",
}
HORIZONS = {"short", "medium", "long"}
REASON_TAGS = {"policy", "macro", "liquidity", "commodity", "sector", "risk", "other"}
EVENT_TYPES = {"policy", "macro", "earnings", "commodity", "regulation", "liquidity", "risk", "other"}


def bounded_float(value: Any, field_name: str, *, low: float = 0.0, high: float = 1.0) -> float:
    """Parse and validate a bounded float."""
    parsed = float(value)
    if not low <= parsed <= high:
        raise ValueError(f"{field_name} must be in [{low}, {high}]")
    return parsed


@dataclass(frozen=True)
class AffectedAssetSignal:
    asset_or_group: str
    direction: int
    confidence: float
    horizon: str

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "AffectedAssetSignal":
        direction = int(data.get("direction"))
        if direction not in {-1, 0, 1}:
            raise ValueError("affected_assets.direction must be -1, 0, or 1")
        horizon = str(data.get("horizon", "short"))
        if horizon not in HORIZONS:
            raise ValueError("affected_assets.horizon is invalid")
        return cls(
            asset_or_group=str(data.get("asset_or_group", "")).strip(),
            direction=direction,
            confidence=bounded_float(data.get("confidence", 0.0), "affected_assets.confidence"),
            horizon=horizon,
        )


@dataclass(frozen=True)
class RegimeSignal:
    regime: str
    confidence: float
    rationale: str
    affected_assets: tuple[AffectedAssetSignal, ...] = ()

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "RegimeSignal":
        regime = str(data.get("regime", "")).strip()
        if regime not in REGIME_LABELS:
            raise ValueError(f"invalid regime: {regime}")
        affected = tuple(AffectedAssetSignal.from_mapping(item) for item in data.get("affected_assets", []) or [])
        return cls(
            regime=regime,
            confidence=bounded_float(data.get("confidence", 0.0), "confidence"),
            rationale=str(data.get("rationale", ""))[:500],
            affected_assets=affected,
        )


@dataclass(frozen=True)
class AlphaScore:
    asset: str
    score: float
    confidence: float
    horizon: str
    reason_tag: str

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "AlphaScore":
        horizon = str(data.get("horizon", "short"))
        if horizon not in HORIZONS:
            raise ValueError("alpha score horizon is invalid")
        reason = str(data.get("reason_tag", "other"))
        if reason not in REASON_TAGS:
            raise ValueError("alpha score reason_tag is invalid")
        score = bounded_float(data.get("score", 0.0), "score", low=-1.0, high=1.0)
        return cls(
            asset=str(data.get("asset", "")).strip(),
            score=score,
            confidence=bounded_float(data.get("confidence", 0.0), "confidence"),
            horizon=horizon,
            reason_tag=reason,
        )


@dataclass(frozen=True)
class AlphaSignal:
    as_of_date: str
    track: str
    scores: tuple[AlphaScore, ...]
    overall_confidence: float

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "AlphaSignal":
        track = str(data.get("track", ""))
        if track not in {"track1", "track2"}:
            raise ValueError("alpha track must be track1 or track2")
        scores = tuple(AlphaScore.from_mapping(item) for item in data.get("scores", []) or [])
        return cls(
            as_of_date=str(data.get("as_of_date", "")),
            track=track,
            scores=scores,
            overall_confidence=bounded_float(data.get("overall_confidence", 0.0), "overall_confidence"),
        )


@dataclass(frozen=True)
class EventSignal:
    event_type: str
    affected_sector: str
    direction: int
    magnitude: float
    confidence: float
    horizon: str
    summary: str

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "EventSignal":
        event_type = str(data.get("event_type", "other"))
        if event_type not in EVENT_TYPES:
            raise ValueError("event_type is invalid")
        direction = int(data.get("direction", 0))
        if direction not in {-1, 0, 1}:
            raise ValueError("event direction must be -1, 0, or 1")
        horizon = str(data.get("horizon", "short"))
        if horizon not in HORIZONS:
            raise ValueError("event horizon is invalid")
        return cls(
            event_type=event_type,
            affected_sector=str(data.get("affected_sector", "")).strip(),
            direction=direction,
            magnitude=bounded_float(data.get("magnitude", 0.0), "magnitude"),
            confidence=bounded_float(data.get("confidence", 0.0), "confidence"),
            horizon=horizon,
            summary=str(data.get("summary", ""))[:500],
        )


@dataclass(frozen=True)
class EventExposureSignal:
    as_of_date: str
    events: tuple[EventSignal, ...] = field(default_factory=tuple)
    overall_confidence: float = 0.0

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> "EventExposureSignal":
        return cls(
            as_of_date=str(data.get("as_of_date", "")),
            events=tuple(EventSignal.from_mapping(item) for item in data.get("events", []) or []),
            overall_confidence=bounded_float(data.get("overall_confidence", 0.0), "overall_confidence"),
        )


@dataclass(frozen=True)
class LlmSignal:
    """Backward-compatible minimal parsed LLM signal contract."""

    label: str
    confidence: float
    rationale: str = ""
