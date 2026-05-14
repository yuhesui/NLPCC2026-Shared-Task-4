"""Manual-copy LLM request/response file workflow."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Mapping, TypeVar

from nlpcc4.common.paths import manual_llm_request_dir, manual_llm_response_dir
from nlpcc4.llm.parsers import parse_json_object

T = TypeVar("T")


class ManualResponseMissing(FileNotFoundError):
    """Raised when a required manual LLM response file is absent."""


class ManualResponseInvalid(ValueError):
    """Raised when a manual LLM response file is invalid."""


@dataclass(frozen=True)
class ManualLLMRequest:
    run_id: str
    stem: str
    prompt_text: str

    @property
    def request_path(self) -> Path:
        return manual_llm_request_dir(self.run_id) / f"{self.stem}.md"

    @property
    def response_path(self) -> Path:
        return manual_llm_response_dir(self.run_id) / f"{self.stem}.json"


def decision_stem(decision_date: str, track: str, strategy: str, decision_id: str) -> str:
    """Build the required manual LLM filename stem."""
    return f"{decision_date.replace('-', '')}_{track}_{strategy}_{decision_id}"


def write_manual_prompt(request: ManualLLMRequest) -> Path:
    """Write a manual prompt file and create the matching response directory."""
    request.request_path.parent.mkdir(parents=True, exist_ok=True)
    request.response_path.parent.mkdir(parents=True, exist_ok=True)
    body = (
        f"{request.prompt_text.rstrip()}\n\n"
        "Paste the JSON-only model response here:\n\n"
        f"{request.response_path}\n"
    )
    request.request_path.write_text(body, encoding="utf-8", newline="\n")
    return request.request_path


def read_manual_response(
    request: ManualLLMRequest,
    validator: Callable[[Mapping[str, Any]], T],
) -> T:
    """Read and validate the matching manual response JSON file."""
    if not request.response_path.exists():
        raise ManualResponseMissing(
            f"Missing manual LLM response for {request.stem}. Paste JSON into {request.response_path}"
        )
    try:
        payload = parse_json_object(request.response_path.read_text(encoding="utf-8"))
        return validator(payload)
    except Exception as exc:
        raise ManualResponseInvalid(f"Invalid manual LLM response at {request.response_path}: {exc}") from exc
