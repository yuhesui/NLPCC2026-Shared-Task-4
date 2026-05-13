"""Repository path helpers."""

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
