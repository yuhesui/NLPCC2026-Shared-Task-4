"""Deterministic retrieval analogue index for Stage 2."""

from __future__ import annotations

import hashlib
import math
from typing import Any

from nlpcc.stage2_text_store.schema import EventTableRow


def build_retrieval_index_stub() -> dict[str, str]:
    return {
        "status": "available_mvp",
        "component": "retrieval_index",
        "reason": "Use build_retrieval_analogue_index for deterministic event-similarity analogues.",
    }


def build_retrieval_analogue_index(
    event_table: tuple[EventTableRow, ...],
    *,
    embedding_dim: int = 16,
    k: int = 5,
    max_events: int = 128,
) -> dict[str, Any]:
    """Build a small cosine-similarity index over event rows.

    The MVP deliberately uses deterministic hashed embeddings unless Stage 1
    supplies local model references. It stores no future returns at runtime.
    """

    rows: list[dict[str, Any]] = []
    selected_events = tuple(
        sorted(event_table, key=lambda item: abs(item.signed_intensity) * item.confidence, reverse=True)[:max_events]
    )
    for event in selected_events:
        vector = _event_embedding(event, dims=embedding_dim)
        rows.append(
            {
                "event_id": event.event_id,
                "news_id": event.news_id,
                "event_type": event.event_type,
                "sector": event.sector,
                "direction": event.direction,
                "signed_intensity": event.signed_intensity,
                "confidence": event.confidence,
                "embedding": vector,
            }
        )
    neighbours: dict[str, list[dict[str, float | str]]] = {}
    for row in rows:
        scored: list[tuple[float, str]] = []
        for other in rows:
            if row["event_id"] == other["event_id"]:
                continue
            scored.append((_cosine(row["embedding"], other["embedding"]), str(other["event_id"])))
        scored.sort(reverse=True)
        neighbours[str(row["event_id"])] = [
            {"event_id": event_id, "cosine": round(score, 6)} for score, event_id in scored[: max(0, k)]
        ]
    return {
        "status": "available_mvp",
        "component": "retrieval_analogue_index",
        "embedding_dim": embedding_dim,
        "event_count": len(rows),
        "source_event_count": len(event_table),
        "max_events": max_events,
        "rows": rows,
        "nearest": neighbours,
    }


def analogue_score_by_sector(index: dict[str, Any]) -> dict[str, float]:
    scores: dict[str, float] = {}
    weights: dict[str, float] = {}
    for row in index.get("rows", []):
        sector = str(row.get("sector") or "unknown")
        signed = float(row.get("signed_intensity", 0.0) or 0.0)
        confidence = float(row.get("confidence", 0.0) or 0.0)
        scores[sector] = scores.get(sector, 0.0) + signed * confidence
        weights[sector] = weights.get(sector, 0.0) + confidence
    return {sector: round(scores[sector] / max(weights.get(sector, 0.0), 1e-9), 8) for sector in scores}


def _event_embedding(event: EventTableRow, *, dims: int) -> tuple[float, ...]:
    text = f"{event.event_type}|{event.sector}|{event.direction}|{event.evidence}"
    digest = hashlib.sha256(text.encode("utf-8", errors="ignore")).digest()
    values = [((digest[idx % len(digest)] / 127.5) - 1.0) for idx in range(max(1, dims))]
    norm = math.sqrt(sum(value * value for value in values)) or 1.0
    return tuple(round(value / norm, 6) for value in values)


def _cosine(left: tuple[float, ...], right: tuple[float, ...]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    numerator = sum(a * b for a, b in zip(left, right))
    left_norm = math.sqrt(sum(a * a for a in left)) or 1.0
    right_norm = math.sqrt(sum(b * b for b in right)) or 1.0
    return numerator / (left_norm * right_norm)
