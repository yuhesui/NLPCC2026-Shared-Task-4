"""Deterministic cache-key and manifest scaffold for News Overlay features."""

from __future__ import annotations

import csv
from dataclasses import asdict, dataclass
from hashlib import sha256
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class NewsOverlayCacheKey:
    method_code: str
    model_identifier: str
    local_path_or_revision: str
    preprocessing_version: str
    text_hash: str
    date: str
    news_source_hash: str
    feature_schema_version: str

    def digest(self) -> str:
        payload = "|".join(
            (
                self.method_code,
                self.model_identifier,
                self.local_path_or_revision,
                self.preprocessing_version,
                self.text_hash,
                self.date,
                self.news_source_hash,
                self.feature_schema_version,
            )
        )
        return sha256(payload.encode("utf-8")).hexdigest()

    def as_dict(self) -> dict[str, str]:
        data = asdict(self)
        data["cache_key"] = self.digest()
        return data


def stable_text_hash(texts: tuple[str, ...] | list[str] | str) -> str:
    if isinstance(texts, str):
        parts = (texts,)
    else:
        parts = tuple(str(item) for item in texts)
    return sha256("\n".join(parts).encode("utf-8")).hexdigest()


def news_source_hash(sources: tuple[str, ...] | list[str] | str | None) -> str:
    if sources is None:
        parts: tuple[str, ...] = ()
    elif isinstance(sources, str):
        parts = (sources,)
    else:
        parts = tuple(str(item) for item in sources)
    return sha256("|".join(sorted(parts)).encode("utf-8")).hexdigest()


def build_cache_key(
    *,
    method_code: str,
    model_identifier: str | None,
    local_path_or_revision: str | None,
    preprocessing_version: str,
    texts: tuple[str, ...] | list[str] | str,
    date: str,
    sources: tuple[str, ...] | list[str] | str | None,
    feature_schema_version: str,
) -> NewsOverlayCacheKey:
    return NewsOverlayCacheKey(
        method_code=method_code,
        model_identifier=model_identifier or "none",
        local_path_or_revision=local_path_or_revision or "none",
        preprocessing_version=preprocessing_version,
        text_hash=stable_text_hash(texts),
        date=str(date),
        news_source_hash=news_source_hash(sources),
        feature_schema_version=feature_schema_version,
    )


class CsvCacheManifestWriter:
    """Write small human-readable cache manifest rows."""

    def write_manifest(self, rows: list[dict[str, Any]], path: str | Path) -> Path:
        target = Path(path)
        target.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = sorted({key for row in rows for key in row.keys()}) if rows else ["status"]
        with target.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fieldnames)
            writer.writeheader()
            for row in rows:
                writer.writerow(row)
        return target
