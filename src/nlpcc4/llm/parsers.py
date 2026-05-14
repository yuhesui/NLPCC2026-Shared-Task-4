"""Parsers for structured LLM JSON outputs."""

from __future__ import annotations

import json
import re
from typing import Any


def extract_json_object(text: str) -> str:
    """Extract the first JSON object from raw text or markdown fences."""
    stripped = text.strip()
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", stripped, flags=re.DOTALL | re.IGNORECASE)
    if fence:
        return fence.group(1)
    start = stripped.find("{")
    end = stripped.rfind("}")
    if start == -1 or end == -1 or end <= start:
        raise ValueError("LLM output does not contain a JSON object")
    return stripped[start : end + 1]


def parse_json_object(text: str) -> dict[str, Any]:
    """Parse an LLM response that must contain a JSON object."""
    value = json.loads(extract_json_object(text))
    if not isinstance(value, dict):
        raise ValueError("LLM output must be a JSON object")
    return value
