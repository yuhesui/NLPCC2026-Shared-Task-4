"""Configuration helpers for the News Overlay scaffold."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from nlpcc.news_overlay.base import TrackCode


def normalize_track(track: str) -> TrackCode:
    text = str(track).strip().lower()
    if text in {"a", "track_a", "track1", "track_1", "macro"}:
        return "A"
    if text in {"b", "track_b", "track2", "track_2", "sector"}:
        return "B"
    raise ValueError(f"Unknown track: {track!r}")


@dataclass(frozen=True)
class NewsOverlayConfig:
    """Runtime config for scaffold CLI and tests."""

    track: TrackCode = "A"
    n_method: str = "N1"
    i_method: str = "I1"
    s_method: str = "S3"
    offline: bool = True
    device: str = "auto"
    cache_dir: str = ".var/news_overlay_prompt01_11/cache"
    trace_dir: str = ".var/news_overlay_prompt01_11/logs"
    preprocessing_version: str = "news_overlay_v1"
    feature_schema_version: str = "news_overlay_schema_v4"
    batch_size: int = 16
    proxy_mode: bool = False
    local_model_paths: dict[str, str] = field(default_factory=dict)
    local_model_metadata: dict[str, dict[str, str]] = field(default_factory=dict)
    disabled_methods: frozenset[str] = field(default_factory=frozenset)

    @classmethod
    def from_mapping(cls, values: dict[str, Any] | None) -> "NewsOverlayConfig":
        if not values:
            return cls()
        data = dict(values)
        if "track" in data:
            data["track"] = normalize_track(str(data["track"]))
        if "disabled_methods" in data and not isinstance(data["disabled_methods"], frozenset):
            data["disabled_methods"] = frozenset(str(item) for item in data["disabled_methods"])
        if "batch_size" in data:
            data["batch_size"] = max(1, int(data["batch_size"]))
        if "proxy_mode" in data:
            data["proxy_mode"] = _truthy(data["proxy_mode"])
        accepted = {key: value for key, value in data.items() if key in cls.__dataclass_fields__}
        return cls(**accepted)

    @property
    def cache_path(self) -> Path:
        return Path(self.cache_dir)

    @property
    def trace_path(self) -> Path:
        return Path(self.trace_dir)


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}
