"""Promotion gates for candidate systems."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PromotionGate:
    min_sharpe_delta: float = 0.0
    min_return_delta: float = 0.0
    max_drawdown_worsening: float = 0.02
    max_turnover_multiplier: float = 2.0

    def evaluate(self, candidate: dict[str, float], benchmark: dict[str, float]) -> dict[str, object]:
        sharpe_ok = candidate.get("sharpe_ratio", 0.0) >= benchmark.get("sharpe_ratio", 0.0) + self.min_sharpe_delta
        return_ok = candidate.get("cumulative_return", 0.0) >= benchmark.get("cumulative_return", 0.0) + self.min_return_delta
        drawdown_ok = candidate.get("max_drawdown", 0.0) <= benchmark.get("max_drawdown", 0.0) + self.max_drawdown_worsening
        turnover_limit = max(benchmark.get("turnover", 0.0) * self.max_turnover_multiplier, benchmark.get("turnover", 0.0) + 1e-12)
        turnover_ok = candidate.get("turnover", 0.0) <= turnover_limit
        checks = {
            "sharpe_ok": sharpe_ok,
            "return_ok": return_ok,
            "drawdown_ok": drawdown_ok,
            "turnover_ok": turnover_ok,
        }
        return {"promote": all(checks.values()), "checks": checks}
