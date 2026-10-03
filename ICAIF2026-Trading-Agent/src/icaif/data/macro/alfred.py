"""Vintage-aware macro observations (FRED/ALFRED style).

ALFRED ``series/observations`` with ``realtime_start``/``realtime_end`` gives
every vintage of every reference period. We convert each row into a
:class:`MacroObservation` with ``available_at = realtime_start`` at the
series' release time-of-day (configurable; default 08:30 ET, the usual BLS/BEA
release time). Revisions therefore appear as later records and
``MacroStore.latest`` returns only what had been released by the decision time.

Network fetching requires a free FRED API key and is not wired by default.
"""

from __future__ import annotations

from collections.abc import Mapping
from datetime import date, datetime
from typing import Any

from icaif.core.schemas import MacroObservation, Provenance, content_hash
from icaif.core.time import et_datetime


def parse_alfred_observations(
    payload: Mapping[str, Any], *, series_id: str, release_time_et: str = "08:30", retrieved_at: datetime | None = None
) -> list[MacroObservation]:
    out: list[MacroObservation] = []
    for row in payload.get("observations", []) or []:
        value = row.get("value")
        if value in (None, "", "."):
            continue  # ALFRED uses "." for missing values: skipped, not imputed
        period = et_datetime(date.fromisoformat(row["date"]), "00:00")
        vintage = str(row["realtime_start"])
        available = et_datetime(date.fromisoformat(vintage), release_time_et)
        out.append(
            MacroObservation(
                series_id=series_id,
                event_time=period,
                value=float(value),
                available_at=available,
                vintage=vintage,
                provenance=Provenance("fred_alfred", f"{series_id}:{row['date']}:{vintage}",
                                      content_hash(dict(row)), retrieved_at=retrieved_at,
                                      access_method="api.stlouisfed.org/fred/series/observations (realtime)"),
            )
        )
    return out
