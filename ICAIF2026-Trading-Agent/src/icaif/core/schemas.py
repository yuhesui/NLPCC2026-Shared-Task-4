"""Point-in-time record contracts.

Every observation that can influence a decision carries explicit time and
provenance fields:

``event_time``    when the underlying fact happened / period it describes
``published_at``  when the source first published it (if known)
``available_at``  earliest time *this agent* could have used it
``retrieved_at``  when we actually fetched it (live) / built the cache (research)
``source``, ``source_id``, ``content_hash``  provenance

The single rule enforced by :mod:`icaif.core.leakage_guard` is
``available_at <= decision_time``. ``available_at`` must never precede
``published_at`` or ``event_time``-derived completion (e.g. a bar's end).
"""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from icaif.core.time import ensure_aware


def content_hash(payload: Any) -> str:
    """Stable SHA-256 of a JSON-serialisable payload (sorted keys, UTF-8)."""

    if isinstance(payload, bytes):
        raw = payload
    elif isinstance(payload, str):
        raw = payload.encode("utf-8")
    else:
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


@dataclass(frozen=True)
class Provenance:
    source: str
    source_id: str
    content_hash: str
    retrieved_at: datetime | None = None
    access_method: str = ""
    terms_note: str = ""

    def __post_init__(self) -> None:
        if not self.source or not self.source_id:
            raise ValueError("provenance requires source and source_id")
        if self.retrieved_at is not None:
            object.__setattr__(self, "retrieved_at", ensure_aware(self.retrieved_at, "retrieved_at"))

    def as_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "source_id": self.source_id,
            "content_hash": self.content_hash,
            "retrieved_at": self.retrieved_at.isoformat() if self.retrieved_at else None,
            "access_method": self.access_method,
            "terms_note": self.terms_note,
        }


def _check_times(event_time: datetime | None, published_at: datetime | None, available_at: datetime) -> None:
    if published_at is not None and available_at < published_at:
        raise ValueError("available_at must not precede published_at")


@dataclass(frozen=True)
class MarketBar:
    """One completed OHLCV bar covering ``[start, end)``.

    ``available_at`` is when the completed bar could be read (>= ``end``).
    A bar is never visible before it completes, so intraday leakage through a
    partially formed bar is structurally impossible.
    """

    symbol: str
    start: datetime
    end: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    available_at: datetime
    provenance: Provenance

    def __post_init__(self) -> None:
        for name in ("start", "end", "available_at"):
            object.__setattr__(self, name, ensure_aware(getattr(self, name), name))
        if not self.start < self.end:
            raise ValueError(f"bar start must precede end ({self.symbol} {self.start})")
        if self.available_at < self.end:
            raise ValueError(f"bar available_at precedes bar end ({self.symbol} {self.end})")
        for name in ("open", "high", "low", "close"):
            value = getattr(self, name)
            if isinstance(value, bool) or not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be a positive finite price ({self.symbol} {self.end})")
        if not math.isfinite(self.volume) or self.volume < 0:
            raise ValueError("volume must be finite and non-negative")
        if self.high < max(self.open, self.close) - 1e-9 or self.low > min(self.open, self.close) + 1e-9:
            raise ValueError(f"inconsistent OHLC ({self.symbol} {self.end})")

    @property
    def event_time(self) -> datetime:
        return self.end

    @property
    def published_at(self) -> datetime:
        return self.end

    @property
    def record_id(self) -> str:
        return f"bar:{self.symbol}:{self.start.isoformat()}"


@dataclass(frozen=True)
class Article:
    """A news item / press release / filing text, normalised."""

    article_id: str
    title: str
    body: str
    source: str
    published_at: datetime
    available_at: datetime
    provenance: Provenance
    url: str = ""
    language: str = "und"
    tickers: tuple[str, ...] = ()
    event_time: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "published_at", ensure_aware(self.published_at, "published_at"))
        object.__setattr__(self, "available_at", ensure_aware(self.available_at, "available_at"))
        if self.event_time is not None:
            object.__setattr__(self, "event_time", ensure_aware(self.event_time, "event_time"))
        _check_times(self.event_time, self.published_at, self.available_at)

    @property
    def text(self) -> str:
        return f"{self.title}\n{self.body}".strip()

    @property
    def record_id(self) -> str:
        return f"article:{self.source}:{self.article_id}"


@dataclass(frozen=True)
class MacroObservation:
    """One vintage of a macro series value (ALFRED-style real-time period).

    ``event_time`` is the reference period; ``available_at`` the vintage's
    release time. Revisions are new records with a later ``available_at``.
    """

    series_id: str
    event_time: datetime
    value: float
    available_at: datetime
    provenance: Provenance
    vintage: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "event_time", ensure_aware(self.event_time, "event_time"))
        object.__setattr__(self, "available_at", ensure_aware(self.available_at, "available_at"))
        if not math.isfinite(self.value):
            raise ValueError("macro value must be finite")

    @property
    def published_at(self) -> datetime:
        return self.available_at

    @property
    def record_id(self) -> str:
        return f"macro:{self.series_id}:{self.event_time.date()}:{self.vintage or self.available_at.isoformat()}"


@dataclass(frozen=True)
class Filing:
    """An SEC filing index entry. ``available_at`` = EDGAR acceptance time.

    Amendments (``form`` ending in ``/A``) are separate filings with their own
    acceptance time; they never rewrite what was visible before they existed.
    """

    cik: str
    ticker: str
    form: str
    accession: str
    accepted_at: datetime
    provenance: Provenance
    period_of_report: datetime | None = None
    primary_document: str = ""

    def __post_init__(self) -> None:
        object.__setattr__(self, "accepted_at", ensure_aware(self.accepted_at, "accepted_at"))
        if self.period_of_report is not None:
            object.__setattr__(self, "period_of_report", ensure_aware(self.period_of_report, "period_of_report"))

    @property
    def is_amendment(self) -> bool:
        return self.form.upper().endswith("/A")

    @property
    def available_at(self) -> datetime:
        return self.accepted_at

    @property
    def published_at(self) -> datetime:
        return self.accepted_at

    @property
    def event_time(self) -> datetime | None:
        return self.period_of_report

    @property
    def record_id(self) -> str:
        return f"filing:{self.accession}"
