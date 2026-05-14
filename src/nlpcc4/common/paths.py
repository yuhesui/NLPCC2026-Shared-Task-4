"""Repository path helpers."""

from __future__ import annotations

from pathlib import Path

from nlpcc4.common.constants import OFFICIAL_STARTER_DIR, RUNTIME_DIR


def repo_root() -> Path:
    """Return the repository root inferred from this package location."""
    return Path(__file__).resolve().parents[3]


def runtime_root() -> Path:
    """Return the canonical ignored local runtime directory."""
    return repo_root() / RUNTIME_DIR


def official_starter_root() -> Path:
    """Return the official starter-kit directory."""
    return repo_root() / OFFICIAL_STARTER_DIR


def docs_root() -> Path:
    """Return the documentation root."""
    return repo_root() / "docs"


def configs_root() -> Path:
    """Return the durable configuration root."""
    return repo_root() / "configs"


def run_root() -> Path:
    """Return the root for generated run artifacts."""
    return runtime_root() / "runs"


def run_dir(run_id: str) -> Path:
    """Return the generated artifact directory for a run."""
    return run_root() / run_id


def manual_llm_request_dir(run_id: str) -> Path:
    """Return the manual LLM prompt request directory for a run."""
    return runtime_root() / "manual_llm" / "requests" / run_id


def manual_llm_response_dir(run_id: str) -> Path:
    """Return the manual LLM response directory for a run."""
    return runtime_root() / "manual_llm" / "responses" / run_id


def ensure_runtime_dirs(run_id: str | None = None) -> None:
    """Create canonical runtime directories without writing committed artifacts."""
    for path in [
        runtime_root(),
        run_root(),
        runtime_root() / "manual_llm" / "requests",
        runtime_root() / "manual_llm" / "responses",
        runtime_root() / "logs",
        runtime_root() / "outputs",
        runtime_root() / "cache",
        runtime_root() / "artifacts",
        runtime_root() / "submissions",
    ]:
        path.mkdir(parents=True, exist_ok=True)
    if run_id:
        run_dir(run_id).mkdir(parents=True, exist_ok=True)
        manual_llm_request_dir(run_id).mkdir(parents=True, exist_ok=True)
        manual_llm_response_dir(run_id).mkdir(parents=True, exist_ok=True)
