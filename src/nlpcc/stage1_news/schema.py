"""Stage 1 news-processing schemas."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import date, datetime
from typing import Any, Literal


SentimentLabel = Literal["positive", "negative", "neutral"]
Direction = Literal["positive", "negative", "neutral"]


@dataclass(frozen=True)
class Stage1Config:
    top_rank: int = 20
    min_relevance: float = 0.05
    fallback_confidence: float = 0.25
    use_llm: bool = False

    @classmethod
    def from_mapping(cls, values: dict[str, Any] | None) -> "Stage1Config":
        if not values:
            return cls()
        return cls(**{key: value for key, value in values.items() if key in cls.__dataclass_fields__})


@dataclass(frozen=True)
class NormalizedNewsItem:
    news_id: str
    source: str
    title: str
    content: str
    ranking: int | None
    publish_time: datetime | None
    trade_date: date | None = None
    raw: dict[str, Any] = field(default_factory=dict)

    @property
    def text(self) -> str:
        return " ".join(part for part in (self.title, self.content) if part).strip()


@dataclass(frozen=True)
class SentimentSignal:
    news_id: str
    label: SentimentLabel
    score: float
    confidence: float
    evidence: tuple[str, ...] = ()


@dataclass(frozen=True)
class EventTuple:
    news_id: str
    event_type: str
    entities: tuple[str, ...]
    sectors: tuple[str, ...]
    direction: Direction
    intensity: float
    confidence: float
    evidence: str


@dataclass(frozen=True)
class SectorImpact:
    sector: str
    direction: Direction
    intensity: float
    confidence: float
    evidence_count: int


@dataclass(frozen=True)
class BLView:
    asset_group: str
    direction: Direction
    expected_return_bps: float
    confidence: float
    rationale: str


@dataclass(frozen=True)
class Stage1Output:
    items: tuple[NormalizedNewsItem, ...]
    sentiments: tuple[SentimentSignal, ...]
    events: tuple[EventTuple, ...]
    sector_impacts: tuple[SectorImpact, ...]
    bl_views: tuple[BLView, ...]
    fallback_used: bool = False
    diagnostics: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)
