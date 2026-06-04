"""Trace schema and JSON writer for News Overlay scaffold runs."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

from nlpcc.news_overlay.base import MethodRunResult, TrackCode


@dataclass(frozen=True)
class NewsOverlayTrace:
    trace_id: str
    track: TrackCode
    n_method: str
    i_method: str
    s_method: str
    results: tuple[MethodRunResult, ...]
    config: dict[str, Any] = field(default_factory=dict)
    runtime_report: dict[str, Any] = field(default_factory=dict)
    cache_report: dict[str, Any] = field(default_factory=dict)
    model_status: dict[str, Any] = field(default_factory=dict)
    summaries: dict[str, Any] = field(default_factory=dict)
    warnings: tuple[str, ...] = ()
    created_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    schema_version: str = "news_overlay_trace_v2"

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["results"] = [result.as_dict() for result in self.results]
        return data


class JsonTraceWriter:
    """Write one trace JSON file."""

    def write_trace(self, trace: dict[str, Any], path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(trace, indent=2, sort_keys=True), encoding="utf-8")
        return target
