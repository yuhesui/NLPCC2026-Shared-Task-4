"""The fixed 30-stock ICAIF universe (official ``universe.json``, schema_version 1).

Sector labels organise the list only; the rules impose no sector quotas.
Symbol order here is the official file order and is the canonical vector order
used everywhere in this package (``SYMBOLS[i]`` <-> ``weights[i]``).
"""

from __future__ import annotations

from collections.abc import Mapping
from types import MappingProxyType
from typing import Final

SECTORS: Final[Mapping[str, tuple[str, ...]]] = MappingProxyType(
    {
        "Technology": ("AAPL", "MSFT", "NVDA", "INTC", "CRM"),
        "Finance": ("JPM", "BAC", "GS", "V", "PYPL"),
        "Healthcare": ("LLY", "JNJ", "UNH", "PFE", "TMO"),
        "Consumer": ("AMZN", "TSLA", "WMT", "NKE", "KO"),
        "Industrial & Energy": ("CAT", "GE", "BA", "XOM", "CVX"),
        "Communication & Utilities": ("GOOGL", "META", "DIS", "T", "NEE"),
    }
)

SYMBOLS: Final[tuple[str, ...]] = tuple(symbol for group in SECTORS.values() for symbol in group)
SYMBOL_INDEX: Final[Mapping[str, int]] = MappingProxyType({s: i for i, s in enumerate(SYMBOLS)})
SECTOR_OF: Final[Mapping[str, str]] = MappingProxyType(
    {symbol: sector for sector, group in SECTORS.items() for symbol in group}
)
N_ASSETS: Final = len(SYMBOLS)

if N_ASSETS != 30 or len(set(SYMBOLS)) != 30:  # pragma: no cover - import-time invariant
    raise RuntimeError("ICAIF universe must contain exactly 30 unique symbols")


def sector_members(symbol: str) -> tuple[str, ...]:
    """Other symbols sharing ``symbol``'s sector label (used for hard negatives)."""

    sector = SECTOR_OF[symbol]
    return tuple(s for s in SECTORS[sector] if s != symbol)


def validate_symbol_set(symbols: object) -> None:
    """Raise ``ValueError`` unless ``symbols`` is exactly the official universe."""

    provided = set(symbols)  # type: ignore[arg-type]
    expected = set(SYMBOLS)
    missing = sorted(expected - provided)
    unknown = sorted(provided - expected)
    if missing or unknown:
        raise ValueError(f"symbol set mismatch: missing={missing} unknown={unknown}")
