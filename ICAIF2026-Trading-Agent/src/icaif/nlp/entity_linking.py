"""Ticker / company entity linking for the 30-name universe.

Rules:
* company names and distinctive aliases match case-insensitively on word
  boundaries ("Apple", "Microsoft", "JPMorgan", ...);
* ambiguous short tickers (T, V, GE, BA, KO, ...) and common-word names only
  match as cashtags (``$T``), exchange tags (``NYSE: T``) or parenthesised
  tickers ``(T)`` — never as bare words;
* alias lists are data (``ALIASES``) so research can extend them; each mention
  records its evidence span for traces.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from icaif.core.universe import SYMBOLS

ALIASES: dict[str, tuple[str, ...]] = {
    "AAPL": ("Apple Inc", "Apple", "iPhone"),
    "MSFT": ("Microsoft", "Azure"),
    "NVDA": ("Nvidia", "NVIDIA"),
    "INTC": ("Intel",),
    "CRM": ("Salesforce",),
    "JPM": ("JPMorgan", "JP Morgan", "J.P. Morgan", "JPMorgan Chase"),
    "BAC": ("Bank of America", "BofA"),
    "GS": ("Goldman Sachs", "Goldman"),
    "V": ("Visa Inc",),
    "PYPL": ("PayPal", "Venmo"),
    "LLY": ("Eli Lilly",),
    "JNJ": ("Johnson & Johnson", "Johnson and Johnson", "J&J"),
    "UNH": ("UnitedHealth", "United Health Group", "Optum"),
    "PFE": ("Pfizer",),
    "TMO": ("Thermo Fisher",),
    "AMZN": ("Amazon", "AWS"),
    "TSLA": ("Tesla",),
    "WMT": ("Walmart",),
    "NKE": ("Nike",),
    "KO": ("Coca-Cola", "Coca Cola"),
    "CAT": ("Caterpillar",),
    "GE": ("GE Aerospace", "General Electric"),
    "BA": ("Boeing",),
    "XOM": ("Exxon Mobil", "ExxonMobil", "Exxon"),
    "CVX": ("Chevron",),
    "GOOGL": ("Alphabet", "Google", "YouTube"),
    "META": ("Meta Platforms", "Facebook", "Instagram", "WhatsApp"),
    "DIS": ("Disney", "Walt Disney"),
    "T": ("AT&T",),
    "NEE": ("NextEra Energy", "NextEra", "Florida Power & Light"),
}
# Aliases that are also ordinary words: matched only with corporate context.
_CONTEXT_REQUIRED = {"Apple": r"Apple(?!\s+(?:pie|juice|orchard|tree|cider)s?\b)",
                     "Visa Inc": r"Visa Inc", "Meta Platforms": r"Meta Platforms"}

AMBIGUOUS_TICKERS = frozenset({"T", "V", "GE", "BA", "KO", "CAT", "DIS", "GS", "NEE", "CRM", "META"})


@dataclass(frozen=True)
class EntityMention:
    symbol: str
    kind: str  # cashtag | exchange_tag | paren_ticker | name | bare_ticker
    span: tuple[int, int]
    text: str
    confidence: float


def _patterns() -> list[tuple[str, str, re.Pattern[str], float]]:
    pats: list[tuple[str, str, re.Pattern[str], float]] = []
    for symbol in SYMBOLS:
        esc = re.escape(symbol)
        pats.append((symbol, "cashtag", re.compile(rf"(?<![A-Za-z0-9])\${esc}(?![A-Za-z0-9])"), 0.95))
        pats.append((symbol, "exchange_tag", re.compile(rf"\b(?:NYSE|NASDAQ|Nasdaq)\s*:\s*{esc}\b"), 0.95))
        pats.append((symbol, "paren_ticker", re.compile(rf"\(\s*{esc}\s*\)"), 0.9))
        if symbol not in AMBIGUOUS_TICKERS and len(symbol) >= 3:
            pats.append((symbol, "bare_ticker", re.compile(rf"(?<![A-Za-z0-9$]){esc}(?![A-Za-z0-9])"), 0.7))
        for alias in ALIASES.get(symbol, ()):
            body = _CONTEXT_REQUIRED.get(alias, re.escape(alias))
            flags = 0 if alias in _CONTEXT_REQUIRED else re.IGNORECASE
            pats.append((symbol, "name", re.compile(rf"(?<![A-Za-z0-9]){body}(?![A-Za-z0-9])", flags), 0.85))
    return pats


_PATTERNS = _patterns()


def link_entities(text: str) -> list[EntityMention]:
    mentions: list[EntityMention] = []
    for symbol, kind, pattern, conf in _PATTERNS:
        for m in pattern.finditer(text):
            mentions.append(EntityMention(symbol, kind, m.span(), m.group(0), conf))
    mentions.sort(key=lambda x: (x.span[0], -x.confidence))
    return mentions


def linked_symbols(text: str, *, min_confidence: float = 0.7) -> dict[str, float]:
    """symbol -> max mention confidence (boosted slightly for repeated mentions)."""

    out: dict[str, float] = {}
    counts: dict[str, int] = {}
    for m in link_entities(text):
        if m.confidence >= min_confidence:
            out[m.symbol] = max(out.get(m.symbol, 0.0), m.confidence)
            counts[m.symbol] = counts.get(m.symbol, 0) + 1
    return {s: min(1.0, c + 0.02 * (counts[s] - 1)) for s, c in out.items()}
