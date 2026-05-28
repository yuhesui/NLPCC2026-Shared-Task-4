"""Stage 2 quantified text-store schemas."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Literal


DuplicatePolicy = Literal["merge"]


@dataclass(frozen=True)
class Stage2Config:
    """Runtime settings for deterministic Stage 2 aggregation."""

    decay_half_life_days: float = 5.0
    min_confidence: float = 0.0
    max_confidence: float = 1.0
    duplicate_policy: DuplicatePolicy = "merge"

    @classmethod
    def from_mapping(cls, values: dict[str, Any] | None) -> "Stage2Config":
        if not values:
            return cls()
        accepted = {key: value for key, value in values.items() if key in cls.__dataclass_fields__}
        return cls(**accepted)


@dataclass(frozen=True)
class FlatFeatureRow:
    feature_name: str
    value: float
    confidence: float
    source_count: int = 0
    date_int: int | None = None


@dataclass(frozen=True)
class EventTableRow:
    event_id: str
    news_id: str
    event_type: str
    sector: str
    direction: str
    signed_intensity: float
    confidence: float
    evidence: str
    duplicate_count: int = 1


@dataclass(frozen=True)
class BLViewRecord:
    view_id: str
    asset_group: str
    direction: str
    expected_return_bps: float
    confidence: float
    rationale: str
    source_count: int = 1


@dataclass(frozen=True)
class ConfidenceMatrix:
    labels: tuple[str, ...]
    values: tuple[tuple[float, ...], ...]

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DecayedEventMemory:
    as_of_date_int: int | None
    features: dict[str, float]
    decay_half_life_days: float
    event_count: int

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Stage2TextState:
    flat_features: tuple[FlatFeatureRow, ...]
    event_table: tuple[EventTableRow, ...]
    bl_views: tuple[BLViewRecord, ...]
    confidence_matrix: ConfidenceMatrix
    decayed_memory: DecayedEventMemory
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
