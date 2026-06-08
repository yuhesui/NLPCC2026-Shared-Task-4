"""Explicit Hugging Face download-once and local-only model helpers."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any


DEFAULT_HF_HUB_CACHE = Path(r"C:\Users\jeanna\.cache\huggingface\hub")
PROMPT20_REFERENCE_DIR = Path("outputs/reports/news_overlay/prompt01_11/reference")
DETECTED_ENV_VARS = (
    "HF_HOME",
    "HF_HUB_CACHE",
    "TRANSFORMERS_CACHE",
    "SENTENCE_TRANSFORMERS_HOME",
    "NEWS_OVERLAY_LOCAL_MODELS",
    "BGE_MODEL_PATH",
    "FINBERT_MODEL_PATH",
    "RERANKER_MODEL_PATH",
)


ROLE_ENV_PATHS = {
    "embedding_encoder": "BGE_MODEL_PATH",
    "aspect_tone_encoder": "FINBERT_MODEL_PATH",
    "reranker": "RERANKER_MODEL_PATH",
}


DEFAULT_METHOD_CODES_BY_ROLE = {
    "embedding_encoder": (
        "N2",
        "N3",
        "N4",
        "N5",
        "N7",
        "N8",
        "N12",
        "N13",
        "N2345",
        "I5",
        "I6",
        "I7",
        "I256",
        "S6",
        "S7",
        "S126",
    ),
    "aspect_tone_encoder": ("N3", "N13", "I6"),
    "reranker": ("N6",),
}


@dataclass(frozen=True)
class ApprovedHFModel:
    role: str
    hf_model_id: str
    revision: str
    enabled: bool
    purpose: str
    license: str = "unknown"
    expected_size: str = "unknown"
    dependency_requirements: str = "torch; transformers; huggingface_hub"
    download_approved: bool = False
    method_codes: tuple[str, ...] = ()
    notes: str = ""

    @classmethod
    def from_mapping(cls, role: str, values: dict[str, Any]) -> "ApprovedHFModel":
        if not isinstance(values, dict):
            raise ValueError(f"Approved model entry for {role!r} must be a mapping.")
        hf_model_id = str(values.get("hf_model_id") or "").strip()
        revision = str(values.get("revision") or "").strip()
        if not hf_model_id:
            raise ValueError(f"Approved model entry {role!r} is missing hf_model_id.")
        if not revision:
            raise ValueError(f"Approved model entry {role!r} is missing pinned revision.")
        method_codes = tuple(str(item).upper() for item in (values.get("method_codes") or DEFAULT_METHOD_CODES_BY_ROLE.get(role, ())))
        return cls(
            role=role,
            hf_model_id=hf_model_id,
            revision=revision,
            enabled=_truthy(values.get("enabled", False)),
            purpose=str(values.get("purpose") or ""),
            license=str(values.get("license") or "unknown"),
            expected_size=str(values.get("expected_size") or "unknown"),
            dependency_requirements=str(values.get("dependency_requirements") or "torch; transformers; huggingface_hub"),
            download_approved=_truthy(values.get("download_approved", False)),
            method_codes=method_codes,
            notes=str(values.get("notes") or ""),
        )

    def as_manifest_row(self, *, local_cache_path: str | None = None, download_status: str = "not_attempted", load_status: str = "not_checked", device_used: str = "unknown") -> dict[str, Any]:
        return {
            "model_role": self.role,
            "hf_model_id": self.hf_model_id,
            "revision_or_commit": self.revision,
            "license": self.license,
            "expected_size": self.expected_size,
            "local_cache_path": local_cache_path or "",
            "dependency_requirements": self.dependency_requirements,
            "download_status": download_status,
            "load_status": load_status,
            "device_used": device_used,
            "notes": self.notes,
        }


def detect_hf_environment() -> dict[str, str]:
    """Return requested Hugging Face environment variables if present."""

    return {name: os.environ[name] for name in DETECTED_ENV_VARS if os.environ.get(name)}


def expected_hf_cache_path(cache_root: str | Path | None = None) -> Path:
    """Resolve the expected Hugging Face hub cache path without creating it."""

    if cache_root:
        return Path(cache_root).expanduser()
    if os.environ.get("HF_HUB_CACHE"):
        return Path(os.environ["HF_HUB_CACHE"]).expanduser()
    if os.environ.get("HF_HOME"):
        return Path(os.environ["HF_HOME"]).expanduser() / "hub"
    return DEFAULT_HF_HUB_CACHE


def load_approved_models(path: str | Path) -> dict[str, ApprovedHFModel]:
    """Load approved Hugging Face model metadata from explicit YAML config."""

    config_path = Path(path)
    if not config_path.exists():
        raise FileNotFoundError(f"Approved model config not found: {config_path}")
    data = _load_yaml(config_path)
    models = data.get("models") if isinstance(data, dict) else None
    if not isinstance(models, dict) or not models:
        raise ValueError(f"Approved model config must contain a non-empty 'models' mapping: {config_path}")
    return {str(role): ApprovedHFModel.from_mapping(str(role), values) for role, values in models.items()}


def resolve_local_model_context(
    *,
    approved_models_path: str | Path | None = None,
    local_models_path: str | Path | None = None,
    cache_root: str | Path | None = None,
    require_local: bool = False,
) -> tuple[dict[str, str], dict[str, dict[str, str]], list[dict[str, Any]]]:
    """Resolve local model paths and metadata for News Overlay method contexts.

    The function never downloads. It maps enabled approved models, environment
    overrides, and optional local YAML overrides into method-code paths.
    """

    local_paths: dict[str, str] = {}
    metadata: dict[str, dict[str, str]] = {}
    rows: list[dict[str, Any]] = []
    cache = expected_hf_cache_path(cache_root)

    if local_models_path:
        loaded = _load_yaml(Path(local_models_path))
        for key, value in ((loaded or {}).get("local_model_paths") or {}).items():
            if value:
                local_paths[str(key)] = _expand_path(str(value), cache)

    if approved_models_path:
        for model in load_approved_models(approved_models_path).values():
            env_path = os.environ.get(ROLE_ENV_PATHS.get(model.role, ""))
            snapshot = Path(env_path).expanduser() if env_path else resolve_cached_snapshot(model, cache)
            load_status = "local_path_found" if snapshot and snapshot.exists() else "blocked_missing_model"
            local_cache_path = str(snapshot) if snapshot else str(model_cache_dir(model.hf_model_id, cache))
            rows.append(
                model.as_manifest_row(
                    local_cache_path=local_cache_path,
                    download_status="cached" if load_status == "local_path_found" else "not_downloaded",
                    load_status=load_status,
                )
            )
            if not model.enabled or not snapshot or not snapshot.exists():
                continue
            for method_code in model.method_codes:
                local_paths[method_code] = str(snapshot)
                metadata[method_code] = {
                    "role": model.role,
                    "hf_model_id": model.hf_model_id,
                    "revision_or_commit": model.revision,
                    "local_cache_path": str(snapshot),
                    "license": model.license,
                    "expected_size": model.expected_size,
                }
            sanitized = model.hf_model_id.replace("/", "--")
            metadata[sanitized] = {
                "role": model.role,
                "hf_model_id": model.hf_model_id,
                "revision_or_commit": model.revision,
                "local_cache_path": str(snapshot),
                "license": model.license,
                "expected_size": model.expected_size,
            }

    if require_local and not local_paths:
        raise FileNotFoundError("No local News Overlay model paths resolved. Run explicit download-models first or set local overrides.")
    return local_paths, metadata, rows


def download_approved_models(
    *,
    approved_models_path: str | Path,
    cache_root: str | Path | None = None,
    report_dir: str | Path = PROMPT20_REFERENCE_DIR,
    model_id: str | None = None,
    include_disabled: bool = False,
    download_user_approved: bool = False,
    device: str = "auto",
) -> dict[str, Path]:
    """Download enabled approved models once and write compact manifests."""

    if not download_user_approved:
        raise PermissionError("download-models requires --download-user-approved for non-silent network access.")
    approved = load_approved_models(approved_models_path)
    allowed_ids = {model.hf_model_id for model in approved.values()}
    if model_id and model_id not in allowed_ids:
        raise ValueError(f"Unapproved model id rejected: {model_id}")

    try:
        from huggingface_hub import HfApi, snapshot_download  # type: ignore
    except Exception as exc:  # pragma: no cover - dependency-specific
        raise RuntimeError("huggingface_hub is required for explicit download-models mode.") from exc

    cache = expected_hf_cache_path(cache_root)
    report_path = Path(report_dir)
    report_path.mkdir(parents=True, exist_ok=True)
    api = HfApi()
    download_rows: list[dict[str, Any]] = []
    file_rows: list[dict[str, Any]] = []
    availability_rows: list[dict[str, Any]] = []

    for model in approved.values():
        should_download = model.enabled or include_disabled
        if model_id and model.hf_model_id != model_id:
            should_download = False
        if not should_download:
            row = model.as_manifest_row(download_status="disabled_not_downloaded", load_status="not_checked", device_used=device)
            row.update(
                {
                    "network_attempted": False,
                    "download_user_approved": download_user_approved,
                    "download_time": "",
                    "file_count": 0,
                    "size_estimate_bytes": 0,
                    "local_files_only": True,
                }
            )
            download_rows.append(row)
            continue
        if not model.download_approved:
            raise PermissionError(f"Approved config entry {model.role!r} must set download_approved: true before download.")
        info = api.model_info(model.hf_model_id, revision=model.revision, files_metadata=True)
        resolved_revision = str(getattr(info, "sha", model.revision) or model.revision)
        try:
            snapshot_path = Path(
                snapshot_download(
                    repo_id=model.hf_model_id,
                    revision=model.revision,
                    cache_dir=str(cache),
                    local_files_only=False,
                )
            )
        except OSError as exc:
            if getattr(exc, "winerror", None) != 1314:
                raise
            snapshot_path = _download_without_symlinks(snapshot_download, model, cache)
        files = _manifest_files(snapshot_path)
        total_size = sum(int(row["size_bytes"]) for row in files)
        download_time = datetime.now(timezone.utc).isoformat()
        row = model.as_manifest_row(
            local_cache_path=str(snapshot_path),
            download_status="downloaded",
            load_status="cached_not_loaded",
            device_used=device,
        )
        row.update(
            {
                "revision_or_commit": resolved_revision,
                "network_attempted": True,
                "download_user_approved": download_user_approved,
                "download_time": download_time,
                "file_count": len(files),
                "size_estimate_bytes": total_size,
                "local_files_only": False,
            }
        )
        download_rows.append(row)
        for file_row in files:
            file_rows.append(
                {
                    "model_role": model.role,
                    "hf_model_id": model.hf_model_id,
                    "revision_or_commit": resolved_revision,
                    "local_cache_path": str(snapshot_path),
                    **file_row,
                }
            )
        availability_rows.append(
            {
                "model_role": model.role,
                "hf_model_id": model.hf_model_id,
                "revision_or_commit": resolved_revision,
                "local_cache_path": str(snapshot_path),
                "download_status": "downloaded",
                "load_status": "cached_not_loaded",
                "network_attempted": True,
                "local_files_only": False,
            }
        )

    paths = {
        "download_manifest_csv": write_csv(download_rows, report_path / "hf_model_download_manifest.csv"),
        "download_manifest_md": write_download_markdown(download_rows, report_path / "hf_model_download_manifest.md"),
        "model_file_manifest_csv": write_csv(file_rows, report_path / "model_file_manifest.csv"),
        "model_availability_report_csv": write_csv(availability_rows, report_path / "model_availability_report.csv"),
    }
    return paths


def model_cache_dir(hf_model_id: str, cache_root: str | Path | None = None) -> Path:
    cache = expected_hf_cache_path(cache_root)
    return cache / f"models--{hf_model_id.replace('/', '--')}"


def resolve_cached_snapshot(model: ApprovedHFModel, cache_root: str | Path | None = None) -> Path | None:
    root = model_cache_dir(model.hf_model_id, cache_root)
    pinned = root / "snapshots" / model.revision
    if (pinned / "config.json").exists():
        return pinned
    local_pinned = _local_snapshot_dir(model, expected_hf_cache_path(cache_root))
    if (local_pinned / "config.json").exists():
        return local_pinned
    snapshots = root / "snapshots"
    if not snapshots.exists():
        return None
    candidates = [path for path in snapshots.iterdir() if path.is_dir() and (path / "config.json").exists()]
    if not candidates:
        return None
    return sorted(candidates, key=lambda path: path.name, reverse=True)[0]


def write_csv(rows: list[dict[str, Any]], path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = sorted({key for row in rows for key in row}) if rows else ["status"]
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)
    return target


def write_download_markdown(rows: list[dict[str, Any]], path: str | Path) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Prompt20 Hugging Face Download Manifest",
        "",
        "Downloads are allowed only through explicit `download-models` mode. Later inference must use `local_files_only=True`.",
        "",
        "| role | model | revision_or_commit | status | local_cache_path | size_bytes | network_attempted |",
        "|---|---|---|---|---|---:|---|",
    ]
    for row in rows:
        lines.append(
            "| {role} | {model} | {revision} | {status} | {path} | {size} | {network} |".format(
                role=row.get("model_role", ""),
                model=row.get("hf_model_id", ""),
                revision=row.get("revision_or_commit", ""),
                status=row.get("download_status", ""),
                path=row.get("local_cache_path", ""),
                size=row.get("size_estimate_bytes", ""),
                network=row.get("network_attempted", ""),
            )
        )
    target.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return target


def _load_yaml(path: Path) -> dict[str, Any]:
    import yaml  # type: ignore

    loaded = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"YAML root must be a mapping: {path}")
    return loaded


def _expand_path(value: str, cache: Path) -> str:
    text = value.replace("${HF_HUB_CACHE}", str(cache)).replace("${DEFAULT_HF_HUB_CACHE}", str(DEFAULT_HF_HUB_CACHE))
    return os.path.expandvars(text)


def _manifest_files(snapshot_path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in sorted(item for item in snapshot_path.rglob("*") if item.is_file()):
        try:
            size = path.stat().st_size
        except OSError:
            size = 0
        rows.append({"relative_path": path.relative_to(snapshot_path).as_posix(), "size_bytes": size})
    return rows


def _download_without_symlinks(snapshot_download: Any, model: ApprovedHFModel, cache: Path) -> Path:
    local_dir = _local_snapshot_dir(model, cache)
    local_dir.mkdir(parents=True, exist_ok=True)
    return Path(
        snapshot_download(
            repo_id=model.hf_model_id,
            revision=model.revision,
            local_dir=str(local_dir),
            local_files_only=False,
            max_workers=1,
        )
    )


def _local_snapshot_dir(model: ApprovedHFModel, cache: Path) -> Path:
    return cache / "local_snapshots" / model.hf_model_id.replace("/", "--") / model.revision


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}
