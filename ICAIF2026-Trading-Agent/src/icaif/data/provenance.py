"""Dataset manifests: file hashes, row counts, time coverage and source notes.

Every experiment records the manifest hash of the data it used
(``icaif.experiments.registry``). Manifests are JSON files under
``data/manifests/`` (git-ignored) and copied into experiment records.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable, Mapping
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

from icaif.core.schemas import content_hash
from icaif.core.time import utc_now


def file_sha256(path: Path, chunk: int = 1 << 20) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        while block := stream.read(chunk):
            digest.update(block)
    return digest.hexdigest()


@dataclass(frozen=True)
class ManifestEntry:
    path: str
    sha256: str
    bytes: int
    rows: int | None = None
    start: str | None = None
    end: str | None = None


@dataclass(frozen=True)
class DatasetManifest:
    name: str
    kind: str  # market_bars | news | filings | macro | features | training
    entries: tuple[ManifestEntry, ...]
    sources: tuple[str, ...]
    synthetic: bool
    created_at: str = field(default_factory=lambda: utc_now().isoformat())
    notes: str = ""
    extra: Mapping[str, Any] = field(default_factory=dict)

    @property
    def manifest_hash(self) -> str:
        """Identity excludes ``created_at`` so rebuilding identical data is stable."""

        body = asdict(self)
        body.pop("created_at")
        return content_hash(body)[:16]

    def as_dict(self) -> dict[str, Any]:
        body = asdict(self)
        body["manifest_hash"] = self.manifest_hash
        return body

    def write(self, path: Path) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.as_dict(), indent=2, sort_keys=True), encoding="utf-8")
        return path


def build_file_manifest(
    name: str, kind: str, files: Iterable[Path], *, sources: Iterable[str], synthetic: bool, notes: str = ""
) -> DatasetManifest:
    entries = []
    for path in sorted(Path(p) for p in files):
        entries.append(ManifestEntry(path=str(path), sha256=file_sha256(path), bytes=path.stat().st_size))
    return DatasetManifest(name, kind, tuple(entries), tuple(sources), synthetic, notes=notes)


def in_memory_manifest(
    name: str, kind: str, payload: Any, *, sources: Iterable[str], synthetic: bool, rows: int, start: str, end: str
) -> DatasetManifest:
    """Manifest for data generated in memory (e.g. seeded synthetic fixtures)."""

    entry = ManifestEntry(path=f"memory:{name}", sha256=content_hash(payload), bytes=0, rows=rows, start=start, end=end)
    return DatasetManifest(name, kind, (entry,), tuple(sources), synthetic)
