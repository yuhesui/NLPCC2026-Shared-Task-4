"""Deferred retrieval-index interface for Stage 2.

The MVP stores deterministic tabular text state only. Dense retrieval can be
added later behind this interface without changing pipeline callers.
"""

from __future__ import annotations


def build_retrieval_index_stub() -> dict[str, str]:
    return {
        "status": "deferred",
        "component": "retrieval_index",
        "reason": "Dense retrieval is outside the Stage 2 MVP.",
    }
