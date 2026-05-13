"""Repository path helpers.

Custom code should write runtime artifacts only under ignored local directories.
"""

from pathlib import Path


def repo_root() -> Path:
    """Return the repository root inferred from this package location."""
    return Path(__file__).resolve().parents[3]


def runtime_root() -> Path:
    """Return the canonical ignored local runtime directory."""
    return repo_root() / ".var"


def official_starter_root() -> Path:
    """Return the official starter-kit directory."""
    return repo_root() / "NLPCC_tasks"
