"""SEC EDGAR submissions-API parsing (https://www.sec.gov/edgar/sec-api-documentation).

``https://data.sec.gov/submissions/CIK##########.json`` lists recent filings
with ``acceptanceDateTime`` — the moment EDGAR accepted the filing, which we
use as ``available_at``. Amendments (``10-K/A`` etc.) are distinct filings
with their own acceptance time.

Network access is opt-in (``fetch_submissions``) and needs a descriptive
``SEC_USER_AGENT`` (SEC fair-access policy; <= 10 requests/second).
"""

from __future__ import annotations

import json
import os
import urllib.request
from collections.abc import Mapping
from datetime import datetime
from typing import Any

from icaif.core.schemas import Filing, Provenance, content_hash
from icaif.core.time import ET, parse_timestamp, utc_now
from icaif.data.market.loaders import SourceUnavailable

# CIKs for the 30 symbols (SEC company_tickers.json). Verify with
# scripts/data/check_sec_ciks.py before relying on them live.
CIKS: dict[str, str] = {
    "AAPL": "0000320193", "MSFT": "0000789019", "NVDA": "0001045810", "INTC": "0000050863",
    "CRM": "0001108524", "JPM": "0000019617", "BAC": "0000070858", "GS": "0000886982",
    "V": "0001403161", "PYPL": "0001633917", "LLY": "0000059478", "JNJ": "0000200406",
    "UNH": "0000731766", "PFE": "0000078003", "TMO": "0000097745", "AMZN": "0001018724",
    "TSLA": "0001318605", "WMT": "0000104169", "NKE": "0000320187", "KO": "0000021344",
    "CAT": "0000018230", "GE": "0000040545", "BA": "0000012927", "XOM": "0000034088",
    "CVX": "0000093410", "GOOGL": "0001652044", "META": "0001326801", "DIS": "0001744489",
    "T": "0000732717", "NEE": "0000753308",
}


def _acceptance(value: str) -> datetime:
    """EDGAR ``acceptanceDateTime`` (e.g. ``2024-11-01T16:30:12.000Z``)."""

    return parse_timestamp(value, "acceptanceDateTime")


def parse_submissions(payload: Mapping[str, Any], *, ticker: str, retrieved_at: datetime | None = None) -> list[Filing]:
    recent = payload.get("filings", {}).get("recent", {})
    forms = recent.get("form", [])
    cik = str(payload.get("cik", "")).zfill(10)
    out: list[Filing] = []
    for i, form in enumerate(forms):
        try:
            accepted = _acceptance(recent["acceptanceDateTime"][i])
        except (KeyError, IndexError, ValueError):
            continue
        accession = recent["accessionNumber"][i]
        report = recent.get("reportDate", [""] * len(forms))[i]
        period = None
        if report:
            period = datetime.fromisoformat(report).replace(tzinfo=ET)
        out.append(
            Filing(
                cik=cik,
                ticker=ticker,
                form=str(form),
                accession=str(accession),
                accepted_at=accepted,
                period_of_report=period,
                primary_document=str(recent.get("primaryDocument", [""] * len(forms))[i]),
                provenance=Provenance("sec_edgar", str(accession), content_hash([form, accession, str(accepted)]),
                                      retrieved_at=retrieved_at, access_method="data.sec.gov/submissions"),
            )
        )
    return out


def fetch_submissions(ticker: str, *, timeout: float = 20.0) -> list[Filing]:  # pragma: no cover - network
    agent = os.environ.get("SEC_USER_AGENT", "").strip()
    if not agent or "@" not in agent:
        raise SourceUnavailable("set SEC_USER_AGENT='Name contact@example.org' to query EDGAR")
    url = f"https://data.sec.gov/submissions/CIK{CIKS[ticker]}.json"
    request = urllib.request.Request(url, headers={"User-Agent": agent, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read())
    except OSError as error:
        raise SourceUnavailable(f"EDGAR request failed for {ticker}: {error}") from error
    return parse_submissions(payload, ticker=ticker, retrieved_at=utc_now())
