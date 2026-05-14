"""OpenAI-compatible JSON client and mode dispatcher."""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Callable, Mapping, TypeVar

from nlpcc4.llm.manual_io import ManualLLMRequest, read_manual_response, write_manual_prompt
from nlpcc4.llm.parsers import parse_json_object

T = TypeVar("T")


class LLMUnavailable(RuntimeError):
    """Raised when API mode cannot be used safely."""


@dataclass(frozen=True)
class LLMRequest:
    mode: str
    prompt: str
    run_id: str
    stem: str
    model: str = "gpt-5"
    api_base: str | None = None
    temperature: float = 0.0


def _call_openai_compatible(request: LLMRequest) -> dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    api_base = request.api_base or os.getenv("OPENAI_API_BASE", "https://api.openai.com/v1")
    model = os.getenv("OPENAI_MODEL", request.model)
    if not api_key:
        raise LLMUnavailable("OPENAI_API_KEY is not set for llm-mode=api")
    url = api_base.rstrip("/") + "/chat/completions"
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": request.prompt}],
        "temperature": request.temperature,
        "response_format": {"type": "json_object"},
    }
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        raise LLMUnavailable(f"OpenAI-compatible request failed: {exc}") from exc
    content = data["choices"][0]["message"]["content"]
    return parse_json_object(content)


def request_llm_json(
    request: LLMRequest,
    validator: Callable[[Mapping[str, Any]], T],
    *,
    off_value: T | None = None,
) -> tuple[T | None, dict[str, Any]]:
    """Execute off/manual/api mode and return a validated signal plus diagnostics."""
    if request.mode == "off":
        return off_value, {"llm_mode": "off", "used_llm": False}
    manual_request = ManualLLMRequest(request.run_id, request.stem, request.prompt)
    if request.mode == "manual":
        prompt_path = write_manual_prompt(manual_request)
        value = read_manual_response(manual_request, validator)
        return value, {
            "llm_mode": "manual",
            "used_llm": True,
            "manual_prompt_path": str(prompt_path),
            "manual_response_path": str(manual_request.response_path),
        }
    if request.mode == "api":
        payload = _call_openai_compatible(request)
        return validator(payload), {"llm_mode": "api", "used_llm": True}
    raise ValueError("llm mode must be off, manual, or api")
