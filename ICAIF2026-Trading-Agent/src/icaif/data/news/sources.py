"""News source interface, a local JSONL source, GDELT parsing and a
failure-tolerant aggregator.

Policy (docs/llm_and_external_data.md of the official kit): only freely and
publicly accessible information available at or before the submission
deadline; no paid/private feeds; document sources and access methods.

``available_at`` rules:
* historical/backfilled items: ``published_at + source_latency`` (config) —
  never the retrieval time of a later backfill;
* live items: ``max(published_at, retrieved_at)``.
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Protocol

from icaif.core.schemas import Article, Provenance, content_hash
from icaif.core.time import parse_timestamp, utc_now
from icaif.data.market.loaders import SourceUnavailable


class NewsSource(Protocol):
    name: str

    def fetch(self, start: datetime, end: datetime) -> list[Article]: ...


def availability_time(published_at: datetime, *, retrieved_at: datetime | None, latency: timedelta, live: bool) -> datetime:
    if live:
        if retrieved_at is None:
            raise ValueError("live items need retrieved_at")
        return max(published_at, retrieved_at)
    return published_at + latency


@dataclass
class JsonlNewsSource:
    """Local JSONL file(s): one article per line with at least
    ``id,title,published_at`` and optional ``body,url,source,available_at``."""

    name: str
    paths: Sequence[Path]
    latency: timedelta = timedelta(minutes=5)

    def fetch(self, start: datetime, end: datetime) -> list[Article]:
        out: list[Article] = []
        for path in self.paths:
            if not Path(path).exists():
                raise SourceUnavailable(f"{self.name}: missing file {path}")
            for line_no, line in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), start=1):
                if not line.strip():
                    continue
                row = json.loads(line)
                article = parse_article_row(row, default_source=self.name, latency=self.latency, where=f"{path}:{line_no}")
                if start <= article.published_at < end:
                    out.append(article)
        return out


class MalformedArticle(ValueError):
    pass


def parse_article_row(row: Mapping[str, Any], *, default_source: str, latency: timedelta, where: str = "") -> Article:
    try:
        published = parse_timestamp(str(row["published_at"]), "published_at")
    except (KeyError, ValueError, TypeError) as error:
        raise MalformedArticle(f"{where}: bad or missing published_at ({error})") from error
    title = str(row.get("title") or "").strip()
    if not title:
        raise MalformedArticle(f"{where}: empty title")
    body = str(row.get("body") or "")
    retrieved = parse_timestamp(str(row["retrieved_at"])) if row.get("retrieved_at") else None
    if row.get("available_at"):
        available = parse_timestamp(str(row["available_at"]), "available_at")
    else:
        available = availability_time(published, retrieved_at=retrieved, latency=latency, live=False)
    source = str(row.get("source") or default_source)
    article_id = str(row.get("id") or content_hash(title + published.isoformat())[:16])
    return Article(
        article_id=article_id,
        title=title,
        body=body,
        source=source,
        published_at=published,
        available_at=available,
        url=str(row.get("url") or ""),
        provenance=Provenance(source, article_id, content_hash(title + "\n" + body), retrieved_at=retrieved,
                              access_method=str(row.get("access_method") or "local_jsonl")),
    )


def parse_gdelt_doc_response(payload: Mapping[str, Any], *, retrieved_at: datetime, live: bool,
                             latency: timedelta = timedelta(minutes=15)) -> list[Article]:
    """Parse a GDELT DOC 2.0 ``mode=artlist&format=json`` response.

    GDELT gives ``seendate`` (UTC, ``YYYYMMDDTHHMMSSZ``) = when GDELT saw the
    URL, which we treat as ``published_at``. Article bodies are not included;
    titles only. Fetching is done by scripts/data/fetch_gdelt.py (opt-in).
    """

    out: list[Article] = []
    for row in payload.get("articles", []) or []:
        seen = str(row.get("seendate", ""))
        try:
            published = datetime.strptime(seen, "%Y%m%dT%H%M%SZ").replace(tzinfo=utc_now().tzinfo)
        except ValueError:
            continue  # counted by caller via len(payload) - len(out); malformed rows are not guessed
        url = str(row.get("url", ""))
        title = str(row.get("title", "")).strip()
        if not url or not title:
            continue
        aid = content_hash(url)[:20]
        out.append(
            Article(
                article_id=aid,
                title=title,
                body="",
                source="gdelt:" + str(row.get("domain", "unknown")),
                published_at=published,
                available_at=availability_time(published, retrieved_at=retrieved_at, latency=latency, live=live),
                url=url,
                language=str(row.get("language", "und")).lower()[:12],
                provenance=Provenance("gdelt_doc_api", aid, content_hash(title + url), retrieved_at=retrieved_at,
                                      access_method="https://api.gdeltproject.org/api/v2/doc/doc"),
            )
        )
    return out


@dataclass
class SourceFailure:
    source: str
    error: str
    at: str


@dataclass
class AggregatedNews:
    articles: list[Article]
    failures: list[SourceFailure] = field(default_factory=list)

    @property
    def degraded(self) -> bool:
        return bool(self.failures)


def fetch_all(sources: Iterable[NewsSource], start: datetime, end: datetime) -> AggregatedNews:
    """Fetch from every source; a failing source is recorded, never fatal.

    Only :class:`SourceUnavailable` and network-ish ``OSError`` are tolerated;
    programming errors (TypeError etc.) propagate so bugs are not masked.
    """

    articles: list[Article] = []
    failures: list[SourceFailure] = []
    for source in sources:
        try:
            articles.extend(source.fetch(start, end))
        except (SourceUnavailable, OSError, MalformedArticle) as error:
            failures.append(SourceFailure(source.name, f"{type(error).__name__}: {error}", utc_now().isoformat()))
    return AggregatedNews(articles, failures)
