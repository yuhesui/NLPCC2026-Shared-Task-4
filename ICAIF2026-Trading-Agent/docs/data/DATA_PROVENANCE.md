# Data provenance

Competition rule: external market, company and news data must be **freely and publicly accessible**
and available at or before the corresponding submission deadline; no private/paid/proprietary feeds;
sources and access methods must be documented in final materials. The kit ships synthetic prices only.

## Record contract (`core/schemas.py`)

| Field | Meaning |
|---|---|
| `event_time` | when the fact happened / reference period (bar end, macro period, filing period) |
| `published_at` | first publication by the source |
| `available_at` | earliest time *this agent* could use it — the only field the leakage guard compares |
| `retrieved_at` | when we fetched it |
| `source`, `source_id`, `content_hash` | provenance (`Provenance`), plus `access_method`, `terms_note` |

Rules: historical/backfilled items use `available_at = published_at + source latency` (never the
backfill time); live items use `max(published_at, retrieved_at)`. Bars: `available_at ≥ bar end`.
Macro: one record per vintage, `available_at` = release time. Filings: EDGAR `acceptanceDateTime`;
amendments are separate records.

## Source register

| Source | Use | Status | Access / availability | Terms note |
|---|---|---|---|---|
| Synthetic world (`data/market/synthetic.py`) | tests, plumbing | implemented | in-memory, seeded | not data; never evidence |
| Local bars CSV (`data/market/loaders.py`) | historical / live bars | loader implemented, **no data yet** | `data/raw/market/*.csv` | provider must be public & terms-reviewed |
| Intraday market data vendor | live bars | **TODO: choose** (`UnconfiguredVendorSource` fails loudly) | — | Yahoo Finance chart data is the organizer-suggested public reference; review Yahoo's terms before automated use |
| SEC EDGAR submissions API | filings, 8-K events, business descriptions | parser implemented; fetch opt-in | `data.sec.gov/submissions/CIK##########.json`, `acceptanceDateTime` | SEC fair-access: descriptive User-Agent, ≤10 req/s |
| GDELT DOC 2.0 | news discovery (titles + URLs) | parser implemented; fetch not wired | `api.gdeltproject.org/api/v2/doc/doc`, `seendate` + 15 min | free/open; confirm with organizers (Q6) |
| Yahoo Finance news | news | interface only | — | organizer-recommended; terms review required |
| Company IR pages / press-release RSS | first-party news | interface only | feed timestamps | per-site terms |
| FRED / ALFRED | macro with vintages | parser implemented | `realtime_start` @ release time | free API key |
| Federal Reserve, BLS, BEA, Treasury release calendars | macro event timing | planned | official calendars | public domain (US government) |
| Paid / private feeds | — | **rejected** | — | prohibited |

## Failure handling

`data/news/sources.fetch_all` records `SourceUnavailable`/`OSError`/malformed-row failures per source
and continues; programming errors propagate. Failed sources are listed in `TextState.sources_failed`
and in every decision trace. Market-data staleness beyond `max_staleness_hours` → HOLD.

## Manifests

`data/provenance.py` builds manifests (file sha256, bytes, rows, time range, sources, synthetic flag);
the manifest hash is part of every experiment id. Raw data lives in `data/raw/` (git-ignored, never
edited in place); derived data in `data/interim|processed/`; caches in `data/cache/`.
