"""Decision trace records for production safety decisions."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass(frozen=True)
class FallbackEvent:
    trigger: str
    reason: str
    source_agent: str | None = None
    fallback_agent: str | None = None

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DecisionTrace:
    agent: str
    track: str
    decision_date: int | None = None
    created_at_utc: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    fallback_events: tuple[FallbackEvent, ...] = ()
    diagnostics: dict[str, Any] = field(default_factory=dict)

    @property
    def fallback_used(self) -> bool:
        return bool(self.fallback_events)

    def add_event(self, event: FallbackEvent) -> "DecisionTrace":
        return DecisionTrace(
            agent=self.agent,
            track=self.track,
            decision_date=self.decision_date,
            created_at_utc=self.created_at_utc,
            fallback_events=self.fallback_events + (event,),
            diagnostics=self.diagnostics,
        )

    def as_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["fallback_events"] = [event.as_dict() for event in self.fallback_events]
        data["fallback_used"] = self.fallback_used
        return data


def attach_decision_trace(decision: dict[str, Any], trace: DecisionTrace) -> dict[str, Any]:
    metadata = dict(decision.get("metadata", {}) or {})
    metadata["decision_trace"] = trace.as_dict()
    metadata["fallback_used"] = metadata.get("fallback_used", False) or trace.fallback_used
    if trace.fallback_events:
        metadata["fallback_reason"] = ";".join(event.reason for event in trace.fallback_events)
    updated = dict(decision)
    updated["metadata"] = metadata
    return updated
