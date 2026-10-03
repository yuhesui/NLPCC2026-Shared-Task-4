"""YAML configuration loading with ``extends`` inheritance and stable hashing.

A config file may contain ``extends: <relative path or list of paths>``;
parents are merged first (deep-merge for mappings, replacement otherwise).
The resolved mapping's SHA-256 (:func:`config_hash`) is the identity used by
the experiment registry, so two configs that resolve identically share a hash
regardless of file layout.
"""

from __future__ import annotations

import copy
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import yaml

from icaif.core.schemas import content_hash

REPO_ROOT = Path(__file__).resolve().parents[3]
CONFIG_ROOT = REPO_ROOT / "configs"


class ConfigError(ValueError):
    pass


def deep_merge(base: Mapping[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = copy.deepcopy(dict(base))
    for key, value in override.items():
        if isinstance(value, Mapping) and isinstance(merged.get(key), Mapping):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


def load_config(path: str | Path, *, _seen: tuple[Path, ...] = ()) -> dict[str, Any]:
    source = Path(path)
    if not source.is_absolute():
        source = (REPO_ROOT / source) if not source.exists() else source.resolve()
    source = source.resolve()
    if source in _seen:
        raise ConfigError(f"circular extends: {' -> '.join(str(p) for p in (*_seen, source))}")
    if not source.exists():
        raise ConfigError(f"config not found: {source}")
    data = yaml.safe_load(source.read_text(encoding="utf-8")) or {}
    if not isinstance(data, dict):
        raise ConfigError(f"config root must be a mapping: {source}")
    parents = data.pop("extends", None)
    if parents is None:
        return data
    resolved: dict[str, Any] = {}
    for parent in [parents] if isinstance(parents, str) else list(parents):
        parent_path = (source.parent / parent).resolve()
        resolved = deep_merge(resolved, load_config(parent_path, _seen=(*_seen, source)))
    return deep_merge(resolved, data)


def config_hash(config: Mapping[str, Any]) -> str:
    return content_hash(dict(config))[:16]
