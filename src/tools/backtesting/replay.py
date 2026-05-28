"""Replay and summarize saved local backtest artifacts."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def load_backtest(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def replay_summary(result: dict[str, Any]) -> dict[str, Any]:
    portfolio_history = result.get("portfolio_history", [])
    transactions = result.get("transactions", [])
    return {
        "status": result.get("status"),
        "track": result.get("track"),
        "initial_capital": result.get("initial_capital"),
        "final_value": result.get("final_value"),
        "metrics": result.get("metrics", {}),
        "day_count": len(portfolio_history),
        "transaction_count": len(transactions),
        "first_date": portfolio_history[0]["date"] if portfolio_history else None,
        "last_date": portfolio_history[-1]["date"] if portfolio_history else None,
    }


def replay_file(path: Path) -> dict[str, Any]:
    return replay_summary(load_backtest(path))
