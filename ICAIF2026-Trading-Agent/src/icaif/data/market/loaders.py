"""Market data loaders and source interface.

Only a *file* loader is implemented: a CSV of completed bars with explicit
availability timestamps. Live/historical vendors plug in behind
:class:`MarketDataSource`; none is wired by default because the competition
requires free, public, terms-compliant sources and the choice (e.g. Yahoo
Finance chart data, exchange-published data) needs a terms review first
(docs/data/DATA_PROVENANCE.md). There is deliberately no hidden network call.

CSV columns (header required):
``symbol,start,end,open,high,low,close,volume,available_at,source,source_id``
Timestamps are ISO-8601 with offsets. ``available_at`` must be the time the
completed bar was (or would have been) readable, never earlier than ``end``.
"""

from __future__ import annotations

import csv
from collections.abc import Iterable
from datetime import datetime
from pathlib import Path
from typing import Protocol

from icaif.core.schemas import MarketBar, Provenance, content_hash
from icaif.core.time import parse_timestamp
from icaif.data.market.panel import MarketPanel

REQUIRED_COLUMNS = ("symbol", "start", "end", "open", "high", "low", "close", "volume", "available_at", "source")


class SourceUnavailable(RuntimeError):
    """A data source could not be reached or is not configured. Callers degrade explicitly."""


class MarketDataSource(Protocol):
    name: str

    def fetch_bars(self, start: datetime, end: datetime) -> list[MarketBar]: ...


def read_bars_csv(path: Path) -> list[MarketBar]:
    bars: list[MarketBar] = []
    with Path(path).open(newline="", encoding="utf-8") as stream:
        reader = csv.DictReader(stream)
        missing = [c for c in REQUIRED_COLUMNS if c not in (reader.fieldnames or ())]
        if missing:
            raise ValueError(f"{path}: missing columns {missing}")
        for line, row in enumerate(reader, start=2):
            try:
                bars.append(
                    MarketBar(
                        symbol=row["symbol"].strip(),
                        start=parse_timestamp(row["start"]),
                        end=parse_timestamp(row["end"]),
                        open=float(row["open"]),
                        high=float(row["high"]),
                        low=float(row["low"]),
                        close=float(row["close"]),
                        volume=float(row["volume"]),
                        available_at=parse_timestamp(row["available_at"]),
                        provenance=Provenance(
                            source=row["source"],
                            source_id=row.get("source_id") or f"{row['symbol']}:{row['start']}",
                            content_hash=content_hash(row),
                        ),
                    )
                )
            except (ValueError, TypeError) as error:
                raise ValueError(f"{path}:{line}: {error}") from error
    return bars


def load_panel_csv(paths: Iterable[Path], *, bar_minutes: int) -> MarketPanel:
    bars: list[MarketBar] = []
    for path in paths:
        bars.extend(read_bars_csv(path))
    return MarketPanel.from_bars(bars, bar_minutes=bar_minutes, synthetic=False)


class UnconfiguredVendorSource:
    """Placeholder that fails loudly. Replace after a terms review (see TODO)."""

    def __init__(self, name: str) -> None:
        self.name = name

    def fetch_bars(self, start: datetime, end: datetime) -> list[MarketBar]:
        # TODO(data): implement a terms-reviewed public intraday source and record
        # its access method + terms in docs/data/DATA_PROVENANCE.md.
        raise SourceUnavailable(f"market source {self.name!r} is not configured")
