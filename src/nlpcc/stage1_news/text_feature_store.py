"""Filesystem cache for Stage 1 text feature outputs."""

from __future__ import annotations

from dataclasses import asdict
from datetime import date, datetime
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping

from nlpcc.stage1_news.schema import (
    BLView,
    EventTuple,
    NormalizedNewsItem,
    SectorImpact,
    SentimentSignal,
    Stage1Config,
    Stage1Output,
)


class TextFeatureStore:
    """Content-addressed JSONL-compatible cache for Stage 1 outputs.

    The key uses the visible raw-news payload, decision date, and extractor
    config, excluding cache path/mode so the same features can be reused from
    different work directories.
    """

    def __init__(self, root: Path | str) -> None:
        self.root = Path(root)

    def key_for(
        self,
        raw_news: list[dict[str, Any]] | tuple[dict[str, Any], ...] | None,
        *,
        decision_date: int | str | date | datetime | None,
        config: Stage1Config,
    ) -> str:
        payload = {
            "decision_date": _date_key(decision_date),
            "news": _stable_news(raw_news or ()),
            "config": _cache_relevant_config(config),
        }
        text = json.dumps(payload, ensure_ascii=False, sort_keys=True, default=str)
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    def path_for(self, key: str) -> Path:
        return self.root / key[:2] / f"{key}.json"

    def read(self, key: str) -> Stage1Output | None:
        path = self.path_for(key)
        if not path.exists():
            return None
        payload = json.loads(path.read_text(encoding="utf-8"))
        return stage1_output_from_mapping(payload["output"])

    def write(self, key: str, output: Stage1Output, *, metadata: Mapping[str, Any] | None = None) -> Path:
        path = self.path_for(key)
        path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "cache_key": key,
            "metadata": dict(metadata or {}),
            "output": asdict(output),
        }
        path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True, default=str), encoding="utf-8")
        return path


def stage1_output_from_mapping(values: Mapping[str, Any]) -> Stage1Output:
    return Stage1Output(
        items=tuple(_news_item(item) for item in values.get("items", ()) or ()),
        sentiments=tuple(SentimentSignal(**dict(item)) for item in values.get("sentiments", ()) or ()),
        events=tuple(EventTuple(**dict(item)) for item in values.get("events", ()) or ()),
        sector_impacts=tuple(SectorImpact(**dict(item)) for item in values.get("sector_impacts", ()) or ()),
        bl_views=tuple(BLView(**dict(item)) for item in values.get("bl_views", ()) or ()),
        fallback_used=bool(values.get("fallback_used", False)),
        diagnostics=dict(values.get("diagnostics", {}) or {}),
    )


def _news_item(values: Mapping[str, Any]) -> NormalizedNewsItem:
    return NormalizedNewsItem(
        news_id=str(values.get("news_id", "")),
        source=str(values.get("source", "unknown")),
        title=str(values.get("title", "")),
        content=str(values.get("content", "")),
        ranking=_int_or_none(values.get("ranking")),
        publish_time=_datetime_or_none(values.get("publish_time")),
        trade_date=_date_or_none(values.get("trade_date")),
        raw=dict(values.get("raw", {}) or {}),
    )


def _stable_news(raw_news: list[dict[str, Any]] | tuple[dict[str, Any], ...]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in raw_news:
        rows.append(
            {
                "id": row.get("news_id", row.get("CONTENT_ID", row.get("ID"))),
                "date": row.get("THEDATE", row.get("trade_date", row.get("date"))),
                "publish_time": row.get("PUBLISH_TIME", row.get("publish_time")),
                "ranking": row.get("RANKING", row.get("ranking")),
                "source": row.get("SOURCE", row.get("source")),
                "title": row.get("TITLE", row.get("title")),
                "content": row.get("CONTENT", row.get("content")),
            }
        )
    return rows


def _cache_relevant_config(config: Stage1Config) -> dict[str, Any]:
    data = asdict(config)
    for key in ("cache_path", "cache_mode"):
        data.pop(key, None)
    return data


def _date_key(value: int | str | date | datetime | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.strftime("%Y%m%d")
    if isinstance(value, date):
        return value.strftime("%Y%m%d")
    text = str(value)
    digits = "".join(char for char in text if char.isdigit())
    return digits[:8] if len(digits) >= 8 else text


def _datetime_or_none(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if value in (None, ""):
        return None
    text = str(value)
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(text[:19] if "H" in fmt else text[:10], fmt)
        except ValueError:
            continue
    return None


def _date_or_none(value: Any) -> date | None:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    parsed = _datetime_or_none(value)
    return parsed.date() if parsed else None


def _int_or_none(value: Any) -> int | None:
    if value in (None, ""):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None
