"""Simple macro-regime classifier from Stage 1 views."""

from __future__ import annotations

from nlpcc.stage1_news.schema import BLView


def classify_macro_regime(views: tuple[BLView, ...]) -> dict[str, float | str]:
    score = sum(view.expected_return_bps * view.confidence for view in views)
    if score > 5:
        regime = "risk_on"
    elif score < -5:
        regime = "risk_off"
    else:
        regime = "neutral"
    confidence = min(1.0, abs(score) / 50.0)
    return {"regime": regime, "score": score, "confidence": confidence}
