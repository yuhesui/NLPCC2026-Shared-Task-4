"""Expand ``configs/experiments/initial_matrix.yaml`` into concrete experiment configs."""

from __future__ import annotations

import itertools
from collections.abc import Iterator, Mapping
from typing import Any

from icaif.core.config import deep_merge


def _set_dotted(target: dict[str, Any], dotted: str, value: Any) -> dict[str, Any]:
    keys = dotted.split(".")
    node: dict[str, Any] = {}
    out = node
    for k in keys[:-1]:
        node[k] = {}
        node = node[k]
    node[keys[-1]] = value
    return deep_merge(target, out)


def _slug(value: Any) -> str:
    text = "-".join(str(v) for v in value) if isinstance(value, list) else str(value)
    return (text or "none").replace(":", "").replace(".", "p").replace(" ", "")


def expand_matrix(matrix: Mapping[str, Any], *, families: set[str] | None = None,
                  runnable_only: bool = True) -> Iterator[tuple[str, dict[str, Any]]]:
    defaults = dict(matrix.get("defaults", {}))
    for family, spec in matrix["families"].items():
        if families and family not in families:
            continue
        if runnable_only and spec.get("status") != "runnable_synthetic":
            continue
        base = deep_merge(defaults, spec.get("base", {}))
        if "experiments" in spec:
            for item in spec["experiments"]:
                yield family, deep_merge(base, {**item, "family": family})
        if "variants" in spec:
            for name, override in spec["variants"].items():
                yield family, deep_merge(deep_merge(base, override), {"family": family, "name": name})
        if "grid" in spec:
            keys = list(spec["grid"])
            for combo in itertools.product(*(spec["grid"][k] for k in keys)):
                exp = dict(base)
                for k, v in zip(keys, combo, strict=True):
                    exp = _set_dotted(exp, k, v)
                name = "__".join(f"{k.split('.')[-1]}={_slug(v)}" for k, v in zip(keys, combo, strict=True))
                yield family, deep_merge(exp, {"family": family, "name": name})
