"""Hidden-state containers shared by HGF/MPC-style prototypes."""

from __future__ import annotations

from typing import Any


def build_hidden_state_store(
    kalman_state: dict[str, Any] | None = None,
    hmm_state: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "status": "available_mvp",
        "component": "hidden_state_store",
        "kalman_state": kalman_state or {},
        "hmm_state": hmm_state or {},
    }
