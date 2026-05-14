"""YAML config loading and validation for Phase 1a runs."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any, Mapping

import yaml

REQUIRED_TOP_LEVEL_SECTIONS = (
    "strategy",
    "data",
    "signals",
    "portfolio",
    "risk",
    "execution",
    "llm",
    "logging",
)


def deep_merge(base: Mapping[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    """Merge nested mappings without mutating either input."""
    result: dict[str, Any] = deepcopy(dict(base))
    for key, value in override.items():
        if isinstance(value, Mapping) and isinstance(result.get(key), Mapping):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def load_yaml_file(path: str | Path) -> dict[str, Any]:
    """Load a YAML file as a mapping."""
    resolved = Path(path)
    with resolved.open("r", encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    if not isinstance(data, dict):
        raise ValueError(f"YAML config must be a mapping: {resolved}")
    return data


def validate_config(config: Mapping[str, Any], *, path: str | Path | None = None) -> None:
    """Validate the common Phase 1a config shape."""
    missing = [section for section in REQUIRED_TOP_LEVEL_SECTIONS if section not in config]
    if missing:
        location = f" in {path}" if path else ""
        raise ValueError(f"Missing required config sections{location}: {', '.join(missing)}")
    llm_mode = config.get("llm", {}).get("mode", "off")
    if llm_mode not in {"off", "manual", "api"}:
        raise ValueError("llm.mode must be one of: off, manual, api")


def load_config(path: str | Path, overrides: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Load and validate a run config."""
    config = load_yaml_file(path)
    if overrides:
        config = deep_merge(config, overrides)
    validate_config(config, path=path)
    return config


def write_yaml_file(path: str | Path, data: Mapping[str, Any]) -> None:
    """Write a mapping as deterministic YAML."""
    resolved = Path(path)
    resolved.parent.mkdir(parents=True, exist_ok=True)
    with resolved.open("w", encoding="utf-8", newline="\n") as handle:
        yaml.safe_dump(dict(data), handle, sort_keys=False, allow_unicode=True)
