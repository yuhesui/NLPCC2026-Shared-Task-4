"""Deferred knowledge-graph interface for Stage 2."""

from __future__ import annotations


def build_knowledge_graph_stub() -> dict[str, str]:
    return {
        "status": "deferred",
        "component": "knowledge_graph",
        "reason": "Knowledge graph construction is deferred until the tabular text state is stable.",
    }
