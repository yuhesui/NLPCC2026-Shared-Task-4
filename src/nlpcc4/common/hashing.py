"""Small hashing helpers for run metadata and config fingerprints."""

from __future__ import annotations

import json
from hashlib import sha256
from typing import Any, Mapping


def stable_text_hash(text: str) -> str:
    """Return a deterministic SHA-256 hash for text."""
    return sha256(text.encode("utf-8")).hexdigest()


def stable_json_hash(value: Mapping[str, Any]) -> str:
    """Return a deterministic hash for JSON-serializable mappings."""
    text = json.dumps(value, sort_keys=True, ensure_ascii=True, default=str)
    return stable_text_hash(text)


def short_hash(text_or_mapping: str | Mapping[str, Any], length: int = 8) -> str:
    """Return a short deterministic hash."""
    if isinstance(text_or_mapping, str):
        digest = stable_text_hash(text_or_mapping)
    else:
        digest = stable_json_hash(text_or_mapping)
    return digest[:length]


def deterministic_run_id(
    *,
    track: str,
    strategy: str,
    start_date: str,
    end_date: str,
    llm_mode: str,
    config: Mapping[str, Any],
) -> str:
    """Build a stable run id for repeatable local runs."""
    digest = short_hash(
        {
            "track": track,
            "strategy": strategy,
            "start_date": start_date,
            "end_date": end_date,
            "llm_mode": llm_mode,
            "config": config,
        },
        length=8,
    )
    start = start_date.replace("-", "")
    end = end_date.replace("-", "")
    return f"{track}_{strategy}_{start}_{end}_{llm_mode}_{digest}"
