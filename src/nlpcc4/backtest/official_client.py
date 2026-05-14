"""Minimal official-server health helpers."""

from __future__ import annotations

import json
import urllib.error
import urllib.request


def check_official_server(base_url: str = "http://localhost:6207") -> dict[str, object]:
    """Return server availability diagnostics without requiring credentials."""
    try:
        with urllib.request.urlopen(base_url.rstrip("/") + "/docs", timeout=3) as response:
            return {"available": True, "status": response.status}
    except (urllib.error.URLError, TimeoutError) as exc:
        return {"available": False, "error": str(exc)}


def pretty_json(data: object) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)
