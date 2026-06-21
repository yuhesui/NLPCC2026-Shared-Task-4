"""Track fund universes used by smoke tests and future adapters."""

from __future__ import annotations

from typing import Literal


TrackName = Literal["macro", "sector"]


MACRO_FUND_POOL: tuple[str, ...] = (
    "000300.SH",
    "000905.SH",
    "399006.SZ",
    "000688.SH",
    "000932.SH",
    "000941.SH",
    "399971.SZ",
    "000819.SH",
    "000928.SH",
    "000012.SH",
    "518880.SH",
)


SECTOR_FUND_POOL: tuple[str, ...] = (
    "512880.SH",
    "512800.SH",
    "512070.SH",
    "159995.SZ",
    "159819.SZ",
    "515880.SH",
    "159852.SZ",
    "512010.SH",
    "512170.SH",
    "159992.SZ",
    "515170.SH",
    "512690.SH",
    "512400.SH",
    "515220.SH",
    "159870.SZ",
    "512200.SH",
)


def get_fund_pool(track: TrackName) -> tuple[str, ...]:
    """Return the official public fund pool for a supported track."""

    if track == "macro":
        return MACRO_FUND_POOL
    if track == "sector":
        return SECTOR_FUND_POOL
    raise ValueError(f"Unsupported track: {track!r}")
