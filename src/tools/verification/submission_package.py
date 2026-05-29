"""Submission packaging helpers for reproducible release artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import zipfile
from typing import Iterable


DEFAULT_INCLUDE_PATHS = (
    Path("src/nlpcc"),
    Path("configs"),
    Path("scripts/create_implementation_log.py"),
    Path("scripts/run_local_smoke.py"),
    Path("scripts/run_official_server_smoke.py"),
    Path("scripts/run_experiment.py"),
    Path("scripts/generate_report.py"),
    Path("scripts/run_verification.py"),
    Path("scripts/package_submission.py"),
    Path("NLPCC_tasks/agent_platform/agents/build_agent.py"),
    Path("README.md"),
    Path("AGENTS.md"),
    Path("METHODOLOGY.md"),
    Path("WORKFLOW.md"),
    Path("pyproject.toml"),
    Path("requirements.txt"),
    Path("requirements-dev.txt"),
    Path("docs/REPO_STRUCTURE.md"),
    Path("docs/architecture/OFFICIAL_COMPATIBILITY.md"),
    Path("docs/architecture/FOUR_STAGE_SYSTEM.md"),
    Path("docs/strategy/METHODOLOGY.md"),
)

RAW_DATA_MARKERS = (
    Path("data"),
    Path("data/raw_official"),
    Path("NLPCC_tasks/dataset"),
)

EXCLUDED_PARTS = {
    ".git",
    ".pytest_cache",
    "__pycache__",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "outputs",
}

EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".tmp", ".log"}


@dataclass(frozen=True)
class SubmissionPackageResult:
    package_dir: Path
    archive_path: Path
    manifest_path: Path
    file_count: int
    raw_data_issues: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return {
            "package_dir": str(self.package_dir),
            "archive_path": str(self.archive_path),
            "manifest_path": str(self.manifest_path),
            "file_count": self.file_count,
            "raw_data_issues": list(self.raw_data_issues),
        }


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_excluded(path: Path) -> bool:
    return any(part in EXCLUDED_PARTS for part in path.parts) or path.suffix.lower() in EXCLUDED_SUFFIXES


def is_raw_data_path(path: Path) -> bool:
    normalized = path.as_posix()
    return any(normalized == marker.as_posix() or normalized.startswith(marker.as_posix() + "/") for marker in RAW_DATA_MARKERS)


def collect_submission_files(repo_root: Path, include_paths: Iterable[Path] = DEFAULT_INCLUDE_PATHS) -> list[Path]:
    files: set[Path] = set()
    for include_path in include_paths:
        absolute = repo_root / include_path
        if not absolute.exists():
            continue
        if absolute.is_file():
            relative = absolute.relative_to(repo_root)
            if not is_excluded(relative):
                files.add(relative)
            continue
        for candidate in absolute.rglob("*"):
            if not candidate.is_file():
                continue
            relative = candidate.relative_to(repo_root)
            if is_excluded(relative):
                continue
            files.add(relative)
    return sorted(files, key=lambda item: item.as_posix())


def validate_no_raw_data(files: Iterable[Path]) -> tuple[str, ...]:
    return tuple(path.as_posix() for path in files if is_raw_data_path(path))


def build_submission_package(
    *,
    repo_root: Path,
    output_root: Path = Path("outputs/submissions"),
    package_name: str | None = None,
    include_paths: Iterable[Path] = DEFAULT_INCLUDE_PATHS,
) -> SubmissionPackageResult:
    repo_root = repo_root.resolve()
    output_root = output_root if output_root.is_absolute() else repo_root / output_root
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    name = package_name or f"nlpcc_task4_candidate_{timestamp}"
    package_dir = output_root / name
    archive_path = output_root / f"{name}.zip"
    if package_dir.exists() or archive_path.exists():
        raise FileExistsError(f"Submission package already exists: {package_dir} or {archive_path}")

    files = collect_submission_files(repo_root, include_paths)
    raw_data_issues = validate_no_raw_data(files)
    if raw_data_issues:
        raise ValueError(f"Refusing to package raw data paths: {', '.join(raw_data_issues)}")

    package_dir.mkdir(parents=True, exist_ok=False)
    copied: list[dict[str, str]] = []
    for relative in files:
        source = repo_root / relative
        destination = package_dir / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        copied.append(
            {
                "path": relative.as_posix(),
                "sha256": sha256_file(source),
                "bytes": str(source.stat().st_size),
            }
        )

    manifest = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "package_name": name,
        "file_count": len(copied),
        "raw_data_excluded": True,
        "raw_data_policy": "No files under data/ or NLPCC_tasks/dataset/ are included.",
        "files": copied,
    }
    manifest_path = package_dir / "SUBMISSION_MANIFEST.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    (package_dir / "README_SUBMISSION.md").write_text(_submission_readme(name), encoding="utf-8")

    with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for candidate in sorted(package_dir.rglob("*")):
            if candidate.is_file():
                archive.write(candidate, candidate.relative_to(package_dir).as_posix())

    return SubmissionPackageResult(
        package_dir=package_dir,
        archive_path=archive_path,
        manifest_path=manifest_path,
        file_count=len(copied),
        raw_data_issues=raw_data_issues,
    )


def audit_submission_archive(archive_path: Path) -> dict[str, object]:
    issues: list[str] = []
    with zipfile.ZipFile(archive_path, "r") as archive:
        names = archive.namelist()
    for name in names:
        if is_raw_data_path(Path(name)):
            issues.append(name)
        if "__pycache__" in Path(name).parts or name.endswith(".pyc"):
            issues.append(name)
    return {"archive_path": str(archive_path), "entry_count": len(names), "issues": issues}


def _submission_readme(package_name: str) -> str:
    return "\n".join(
        [
            f"# {package_name}",
            "",
            "Candidate NLPCC Task 4 submission package.",
            "",
            "Included contents:",
            "",
            "- `src/nlpcc/` competition implementation",
            "- `configs/` system and experiment configuration",
            "- reproducibility and run scripts under `scripts/`",
            "- top-level repository guidance and selected architecture docs",
            "",
            "Raw official datasets are intentionally excluded. Recreate local data roots from the official starter kit before running backtests.",
            "",
        ]
    )
