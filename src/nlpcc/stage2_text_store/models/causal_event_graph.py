"""Deferred causal-event-graph interface for Stage 2."""

from __future__ import annotations


def build_causal_event_graph_stub() -> dict[str, str]:
    return {
        "status": "deferred",
        "component": "causal_event_graph",
        "reason": "Causal graph construction is deferred until event labels are validated on real data.",
    }
