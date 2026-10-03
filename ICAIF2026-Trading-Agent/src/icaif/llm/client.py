"""LLM client abstraction with full call recording.

Every call yields an :class:`LLMCallRecord` (prompt, model id, temperature,
seed, token usage, latency, response hash) appended to a JSONL log so final
materials can disclose exactly what was used. Clients:

* ``NullLLMClient``   — always unavailable (the default; "no LLM" baseline);
* ``ReplayLLMClient`` — answers from a recorded JSONL (reproducible backtests);
* hosted/open-weight clients are not implemented here yet. They must be added
  behind this interface, check ``policy.assert_allowed`` and never be called
  during a backtest for an article published after the model's knowledge
  cutoff without being flagged (look-ahead via model knowledge is a leakage
  channel; see docs/research/FINETUNING_PLAN.md §Leakage).
"""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Protocol

from icaif.core.schemas import content_hash
from icaif.core.time import utc_now
from icaif.llm.policy import assert_allowed


class LLMUnavailable(RuntimeError):
    pass


@dataclass(frozen=True)
class LLMRequest:
    task: str
    prompt: str
    system: str = ""
    temperature: float = 0.0
    seed: int | None = 0
    max_tokens: int = 512
    response_schema: dict[str, Any] | None = None

    @property
    def key(self) -> str:
        return content_hash([self.task, self.system, self.prompt, self.temperature, self.seed])[:24]


@dataclass(frozen=True)
class LLMResponse:
    text: str
    model_id: str
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: float = 0.0


@dataclass(frozen=True)
class LLMCallRecord:
    request_key: str
    task: str
    model_id: str
    temperature: float
    seed: int | None
    prompt: str
    system: str
    response_hash: str
    input_tokens: int
    output_tokens: int
    latency_ms: float
    at: str = field(default_factory=lambda: utc_now().isoformat())


class LLMClient(Protocol):
    model_id: str

    def complete(self, request: LLMRequest) -> LLMResponse: ...


class NullLLMClient:
    model_id = "none"

    def complete(self, request: LLMRequest) -> LLMResponse:
        raise LLMUnavailable("no LLM configured (baseline: no-LLM)")


class ReplayLLMClient:
    """Serve recorded responses keyed by request; unknown requests raise."""

    def __init__(self, path: Path, model_id: str) -> None:
        assert_allowed(model_id)
        self.model_id = model_id
        self._answers: dict[str, str] = {}
        if Path(path).exists():
            for line in Path(path).read_text(encoding="utf-8").splitlines():
                row = json.loads(line)
                if row.get("model_id") == model_id:
                    self._answers[row["request_key"]] = row["text"]

    def complete(self, request: LLMRequest) -> LLMResponse:
        if request.key not in self._answers:
            raise LLMUnavailable(f"no recorded response for {request.task}:{request.key}")
        return LLMResponse(self._answers[request.key], self.model_id)


class RecordingClient:
    """Wraps any client and appends an LLMCallRecord per call."""

    def __init__(self, inner: LLMClient, log_path: Path) -> None:
        self.inner, self.log_path = inner, Path(log_path)
        self.model_id = inner.model_id

    def complete(self, request: LLMRequest) -> LLMResponse:
        start = time.perf_counter()
        resp = self.inner.complete(request)
        latency = resp.latency_ms or (time.perf_counter() - start) * 1000.0
        rec = LLMCallRecord(request.key, request.task, resp.model_id, request.temperature, request.seed, request.prompt,
                            request.system, content_hash(resp.text), resp.input_tokens, resp.output_tokens, latency)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        with self.log_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({**asdict(rec), "text": resp.text}) + "\n")
        return resp
