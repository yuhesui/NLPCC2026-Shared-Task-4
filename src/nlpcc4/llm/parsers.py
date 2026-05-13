"""Parsers for structured LLM JSON outputs."""

import json
from typing import Any


def parse_json_object(text: str) -> dict[str, Any]:
    """Parse an LLM response that must be a JSON object."""
    value = json.loads(text)
    if not isinstance(value, dict):
        raise ValueError("LLM output must be a JSON object")
    return value
