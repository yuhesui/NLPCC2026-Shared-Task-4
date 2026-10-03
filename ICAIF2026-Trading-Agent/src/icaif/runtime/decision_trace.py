"""Per-round decision traces (JSON), secret-free by construction.

Ported from AlphaAllocator ``runtime/decision_trace.py`` (immutable trace +
fallback events) and extended to answer, for every round:

  what information was available | what the quant core said | what the NLP
  layer said and which events mattered | previous portfolio | unconstrained
  proposal | which constraints changed it | expected turnover and fee |
  what was submitted (or why nothing was).

:func:`redact` removes credential-like keys and values before writing; tests
assert no token can appear in a trace file.
"""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from icaif.core.time import utc_now
from icaif.core.universe import SYMBOLS

_SECRET_KEY = re.compile(r"(token|secret|password|api[_-]?key|authorization|credential|bearer)", re.IGNORECASE)
_SECRET_VALUE = re.compile(r"(sk-[A-Za-z0-9_-]{8,}|Bearer\s+\S+|[A-Za-z0-9_-]{32,})")


@dataclass(frozen=True)
class FallbackEvent:
    trigger: str
    reason: str
    source: str
    fallback: str

    def as_dict(self) -> dict[str, str]:
        return asdict(self)


def _jsonable(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        if value.shape == (len(SYMBOLS),):
            return {s: (None if not np.isfinite(x) else round(float(x), 10)) for s, x in zip(SYMBOLS, value, strict=True)}
        return value.tolist()
    if isinstance(value, np.floating | float):
        return None if not np.isfinite(value) else float(value)
    if isinstance(value, np.integer):
        return int(value)
    if isinstance(value, Mapping):
        return {str(k): _jsonable(v) for k, v in value.items()}
    if isinstance(value, list | tuple):
        return [_jsonable(v) for v in value]
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def redact(value: Any, secrets: tuple[str, ...] = ()) -> Any:
    if isinstance(value, Mapping):
        return {k: ("[REDACTED]" if _SECRET_KEY.search(str(k)) else redact(v, secrets)) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v, secrets) for v in value]
    if isinstance(value, str):
        text = value
        for secret in secrets:
            if secret:
                text = text.replace(secret, "[REDACTED]")
        return _SECRET_VALUE.sub("[REDACTED]", text) if len(text) >= 32 and " " not in text else text
    return value


@dataclass
class DecisionTrace:
    phase: str
    round_id: str
    decision_time: str
    deadline: str
    execution_time: str
    agent: str
    created_at: str = field(default_factory=lambda: utc_now().isoformat())
    information: dict[str, Any] = field(default_factory=dict)
    quant: dict[str, Any] = field(default_factory=dict)
    nlp: dict[str, Any] = field(default_factory=dict)
    portfolio: dict[str, Any] = field(default_factory=dict)
    constraints: dict[str, Any] = field(default_factory=dict)
    costs: dict[str, Any] = field(default_factory=dict)
    action: str = "PENDING"
    submitted_weights: dict[str, float] | None = None
    fallback_events: list[FallbackEvent] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def add_fallback(self, event: FallbackEvent) -> None:
        self.fallback_events.append(event)

    def as_dict(self, secrets: tuple[str, ...] = ()) -> dict[str, Any]:
        body = asdict(self)
        body["fallback_events"] = [e.as_dict() for e in self.fallback_events]
        body["fallback_used"] = bool(self.fallback_events)
        return redact(_jsonable(body), secrets)

    def write(self, directory: Path, secrets: tuple[str, ...] = ()) -> Path:
        directory.mkdir(parents=True, exist_ok=True)
        path = directory / f"{self.round_id}.trace.json"
        path.write_text(json.dumps(self.as_dict(secrets), indent=2, sort_keys=True), encoding="utf-8")
        return path
