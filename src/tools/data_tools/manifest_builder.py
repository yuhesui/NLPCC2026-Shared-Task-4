"""Build lightweight manifests for official and mirrored CSV data."""

from __future__ import annotations

import csv
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


LFS_HEADER = "version https://git-lfs.github.com/spec/v1"
DATE_COLUMNS = ("date", "THEDATE", "PUBLISH_TIME")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_lfs_pointer(path: Path) -> dict[str, Any] | None:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return None
    if not lines or lines[0].strip() != LFS_HEADER:
        return None

    pointer: dict[str, Any] = {"is_lfs_pointer": True}
    for line in lines[1:]:
        if line.startswith("oid sha256:"):
            pointer["lfs_oid_sha256"] = line.split(":", 1)[1].strip()
        elif line.startswith("size "):
            try:
                pointer["lfs_size_bytes"] = int(line.split(" ", 1)[1].strip())
            except ValueError:
                pointer["lfs_size_bytes"] = line.split(" ", 1)[1].strip()
    return pointer


def _normalise_date(value: str) -> str | None:
    value = (value or "").strip()
    if not value:
        return None
    if len(value) >= 8 and value[:8].isdigit():
        return value[:8]
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(value[:19], fmt).strftime("%Y%m%d")
        except ValueError:
            continue
    return None


def inspect_csv(path: Path) -> dict[str, Any]:
    pointer = read_lfs_pointer(path)
    if pointer:
        return {
            "columns": [],
            "row_count": 0,
            "date_min": None,
            "date_max": None,
            "is_lfs_pointer": True,
            **pointer,
            "blocker": "Git LFS pointer is present; actual CSV content is not hydrated.",
        }

    try:
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            columns = list(reader.fieldnames or [])
            date_column = next((col for col in DATE_COLUMNS if col in columns), None)
            row_count = 0
            date_values: list[str] = []
            for row in reader:
                row_count += 1
                if date_column:
                    normalised = _normalise_date(str(row.get(date_column, "")))
                    if normalised:
                        date_values.append(normalised)
    except UnicodeDecodeError:
        return {
            "columns": [],
            "row_count": None,
            "date_min": None,
            "date_max": None,
            "is_lfs_pointer": False,
            "blocker": "Unable to decode CSV as UTF-8.",
        }

    return {
        "columns": columns,
        "row_count": row_count,
        "date_min": min(date_values) if date_values else None,
        "date_max": max(date_values) if date_values else None,
        "is_lfs_pointer": False,
        "blocker": None,
    }


def build_file_record(path: Path, source_root: Path) -> dict[str, Any]:
    record = {
        "path": str(path),
        "relative_path": str(path.relative_to(source_root)),
        "size_bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }
    if path.suffix.lower() == ".csv":
        record.update(inspect_csv(path))
    return record


def build_manifest(source_dir: Path, output_path: Path, dataset_kind: str) -> dict[str, Any]:
    files = sorted(path for path in source_dir.rglob("*") if path.is_file())
    manifest = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_kind": dataset_kind,
        "source_dir": str(source_dir),
        "file_count": len(files),
        "files": [build_file_record(path, source_dir) for path in files],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest


def write_manifest(records: Iterable[dict[str, Any]], output_path: Path, dataset_kind: str) -> dict[str, Any]:
    materialised = list(records)
    manifest = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "dataset_kind": dataset_kind,
        "file_count": len(materialised),
        "files": materialised,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return manifest
