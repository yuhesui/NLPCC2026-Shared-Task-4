"""Config-driven portfolio pipeline: alpha -> base -> exposure -> overlay ->
turnover -> finalise.

Every stage's output is recorded in :class:`PipelineResult` so the decision
trace can answer "what did the quant core say / what did NLP change / which
constraint moved the target" (docs/architecture/SYSTEM_ARCHITECTURE.md).

Base methods (``config["base"]["method"]``):
  cash, equal, inverse_vol, erc, score_tilt, topk_equal, topk_softmax, optimizer
Rebalance policy (``config["rebalance"]``):
  {"mode": "every_round"} | {"mode": "rounds", "rounds": [1, 4]} | {"mode": "once"}
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

import numpy as np

from icaif.core.constants import FEE_RATE
from icaif.features.covariance import estimate_covariance
from icaif.features.cross_sectional import nan_to_neutral, zscore
from icaif.features.regime import regime_state
from icaif.features.returns import HORIZON_HOURS
from icaif.features.volatility import annualise_per_bar, realized_vol
from icaif.models.alpha.selection import topk_equal, topk_softmax
from icaif.models.alpha.signals import alpha_scores, grinold_alpha
from icaif.portfolio.constraints import Constraints, scale_to_capped_simplex
from icaif.portfolio.exposure import decide_gross
from icaif.portfolio.fusion import apply_overlay, overlay_budget
from icaif.portfolio.inverse_vol import inverse_vol_weights
from icaif.portfolio.optimizer import optimize
from icaif.portfolio.risk_parity import solve_erc
from icaif.portfolio.target_weights import finalize_target
from icaif.portfolio.turnover import TurnoverConfig, TurnoverController, expected_fee, l1_turnover
from icaif.runtime.state import AgentState, DecisionContext


class InsufficientHistory(RuntimeError):
    """Not enough visible bars for the configured lookbacks (explicit, not silent)."""


@dataclass
class PipelineResult:
    action: str  # "SUBMIT" | "HOLD"
    target: np.ndarray
    stages: dict[str, np.ndarray] = field(default_factory=dict)
    diagnostics: dict[str, Any] = field(default_factory=dict)

    @property
    def expected_turnover(self) -> float:
        return float(self.diagnostics.get("expected_turnover", 0.0))


class PortfolioPipeline:
    def __init__(self, config: Mapping[str, Any]) -> None:
        self.config = dict(config)
        self.cons = Constraints(**self.config.get("constraints", {}))
        self.turnover = TurnoverController(TurnoverConfig.from_mapping(self.config.get("turnover")))
        self.min_history_hours = float(self.config.get("min_history_hours", 13.0))
        self.fee_rate = float(self.config.get("fee_rate", FEE_RATE))

    # -- helpers ---------------------------------------------------------
    def _needs_covariance(self) -> bool:
        base = self.config["base"]
        return (base["method"] in ("erc", "optimizer")
                or (base["method"] == "score_tilt" and base.get("anchor") == "erc")
                or "vol_target" in self.config.get("exposure", {}))

    @staticmethod
    def _require(cov: np.ndarray | None, method: str) -> np.ndarray:
        if cov is None:
            raise RuntimeError(f"base method {method!r} needs a covariance estimate (pipeline wiring bug)")
        return cov

    def _should_rebalance(self, ctx: DecisionContext, state: AgentState) -> bool:
        policy = self.config.get("rebalance", {"mode": "every_round"})
        mode = policy.get("mode", "every_round")
        if mode == "every_round":
            return True
        if mode == "rounds":
            return ctx.round_number in set(policy["rounds"])
        if mode == "once":
            return state.rounds_rebalanced == 0
        raise ValueError(f"unknown rebalance mode {mode!r}")

    def run(self, ctx: DecisionContext, state: AgentState) -> PipelineResult:
        cfg = self.config
        view = ctx.market_state
        current = np.asarray(ctx.current_weights, dtype=float)
        diag: dict[str, Any] = {"strategy": cfg.get("name", "unnamed")}
        stages: dict[str, np.ndarray] = {"current": current}
        if not self._should_rebalance(ctx, state):
            diag["hold_reason"] = "rebalance_policy"
            return PipelineResult("HOLD", current.copy(), stages, diag)
        if view.n_bars < view.bars(self.min_history_hours):
            raise InsufficientHistory(f"{view.n_bars} bars visible; need {view.bars(self.min_history_hours)}")

        # 1) alpha
        alpha_cfg = cfg.get("alpha", {"method": "none"})
        score, alpha_diag = alpha_scores(view, alpha_cfg)
        diag["alpha"] = alpha_diag
        stages["alpha_score"] = score

        # 2) risk inputs (lazy)
        risk_cfg = cfg.get("risk", {})
        vol_bars = view.bars(float(risk_cfg.get("vol_lookback_hours", 65.0)))
        vol = realized_vol(view, vol_bars)
        cov = None
        if self._needs_covariance():
            cov, cov_diag = estimate_covariance(
                view,
                lookback_bars=view.bars(float(risk_cfg.get("cov_lookback_hours", 130.0))),
                method=risk_cfg.get("cov_method", "ledoit_wolf"),
                alpha=float(risk_cfg.get("fixed_alpha", 0.2)),
            )
            diag["covariance"] = cov_diag

        # 3) unit-gross base portfolio (shape only; exposure applied below)
        base_unit = self._base_weights(cfg["base"], score, vol, cov, current, state, diag, view)
        stages["base_unit"] = base_unit

        # 4) gross exposure
        exp_cfg = cfg.get("exposure", {"base": 1.0})
        predicted_vol = None
        if "vol_target" in exp_cfg and cov is not None and base_unit.sum() > 0:
            w_norm = base_unit / base_unit.sum()
            predicted_vol = float(annualise_per_bar(np.sqrt(w_norm @ cov @ w_norm), view.panel.bars_per_day))
        regime = regime_state(view) if "regime" in exp_cfg else None
        nav_dd = state.nav_drawdown(ctx.nav_estimate)
        exposure = decide_gross(exp_cfg, predicted_vol_ann=predicted_vol, regime=regime, nav_drawdown=nav_dd)
        diag["exposure"] = {"gross": exposure.gross, "components": exposure.components,
                            "predicted_vol_ann": predicted_vol, "nav_drawdown": nav_dd,
                            "regime": regime.as_dict() if regime else None}
        if cfg["base"]["method"] == "optimizer":
            base = base_unit  # optimizer already solved at the exposure-free gross; rescale below
            scale = exposure.gross / base.sum() if base.sum() > exposure.gross > 0 else 1.0
            base = base * min(1.0, scale)
        else:
            unit_sum = base_unit.sum()
            base = base_unit * (exposure.gross / unit_sum) if unit_sum > 0 else base_unit
            base = scale_to_capped_simplex(base, self.cons.max_weight, base.sum(), on_zero="cash")
        stages["base"] = base

        # 5) bounded text overlay
        pre_overlay = base
        ov_cfg = cfg.get("overlay", {"enabled": False})
        if ov_cfg.get("enabled") and ctx.text_state is not None:
            ts = ctx.text_state
            conf = float(np.nanmean(np.where(np.isfinite(ts.score), ts.confidence, np.nan))) if np.isfinite(ts.score).any() else 0.0
            ev = float(np.nanmax(ts.event_multiplier[np.isfinite(ts.score)])) if np.isfinite(ts.score).any() else 1.0
            eta, eta_parts = overlay_budget(ov_cfg, confidence=conf, event_multiplier=ev)
            signal = np.where(ts.confidence >= float(ov_cfg.get("min_confidence", 0.0)), ts.score, np.nan)
            ov = apply_overlay(base, signal, eta=eta, transform=ov_cfg.get("transform", "zscore"), cons=self.cons,
                               per_asset_cap=ov_cfg.get("per_asset_cap"), deadband=float(ov_cfg.get("deadband", 0.0)),
                               temperature=float(ov_cfg.get("temperature", 1.0)), k=int(ov_cfg.get("k", 5)))
            stages["overlay_delta"] = ov.realised_delta
            diag["overlay"] = {"eta": eta, "eta_parts": eta_parts, **ov.diagnostics, "text": ts.summary()}
            pre_overlay, base = base, ov.weights
        stages["pre_turnover"] = base

        # 6) turnover control against actual drifted holdings
        outcome = self.turnover.apply(base, current, ctx.trading_day)
        diag["turnover_steps"] = outcome.steps
        if outcome.hold:
            diag["hold_reason"] = "below_min_change"
            return PipelineResult("HOLD", current.copy(), stages, diag)

        # 7) finalise (fee buffer + feasibility)
        final = finalize_target(outcome.weights, current, self.cons, fee_rate=self.fee_rate)
        stages["final"] = final.weights
        diag["expected_turnover"] = final.expected_turnover
        diag["expected_fee"] = expected_fee(final.weights, current, ctx.nav_estimate, self.fee_rate)
        diag["gross"] = final.gross
        diag["news_driven_turnover"] = l1_turnover(base, pre_overlay) if "overlay_delta" in stages else 0.0
        return PipelineResult("SUBMIT", final.weights, stages, diag)

    def commit(self, ctx: DecisionContext, state: AgentState, result: PipelineResult) -> None:
        """Update persistent state after the decision was actually emitted."""

        if result.action == "SUBMIT":
            self.turnover.commit(ctx.trading_day, result.expected_turnover)
            state.rounds_rebalanced += 1
            state.held = [bool(x > 1e-9) for x in result.target]
        state.rounds_decided += 1
        state.last_round_id = ctx.round_id
        state.last_target = [float(x) for x in result.target]
        if self.turnover.budget is not None:
            b = self.turnover.budget.as_dict()
            state.budget_day, state.budget_used = b["day"], b["used"]

    def restore(self, state: AgentState) -> None:
        if self.turnover.budget is not None and state.budget_day:
            from datetime import date

            self.turnover.budget.day = date.fromisoformat(state.budget_day)
            self.turnover.budget.used = state.budget_used

    # -- base methods ---------------------------------------------------------
    def _base_weights(self, base_cfg: Mapping[str, Any], score: np.ndarray, vol: np.ndarray, cov: np.ndarray | None,
                      current: np.ndarray, state: AgentState, diag: dict[str, Any], view: Any) -> np.ndarray:
        method = base_cfg["method"]
        cap = self.cons.max_weight
        n = current.size
        if method == "cash":
            return np.zeros(n)
        if method == "equal":
            return np.full(n, 1.0 / n)
        if method == "inverse_vol":
            return inverse_vol_weights(vol, 1.0, self.cons)
        if method == "erc":
            res = solve_erc(self._require(cov, method), 1.0, self.cons)
            diag["erc"] = {"iterations": res.iterations, "max_rc_error": res.max_rc_error, "converged": res.converged}
            return res.weights
        if method == "score_tilt":
            # risk-based anchor tilted multiplicatively by the alpha z-score
            anchor_kind = base_cfg.get("anchor", "inverse_vol")
            if anchor_kind == "erc":
                anchor = solve_erc(self._require(cov, method), 1.0, self.cons).weights
            else:
                anchor = inverse_vol_weights(vol, 1.0, self.cons)
            kappa = float(base_cfg.get("kappa", 0.5))
            tilt = np.maximum(0.0, 1.0 + kappa * nan_to_neutral(zscore(score)))
            return scale_to_capped_simplex(anchor * tilt, cap, 1.0, on_zero="cash")
        if method == "topk_equal":
            return topk_equal(score, int(base_cfg.get("k", 5)), 1.0, cap, positive_only=bool(base_cfg.get("positive_only", True)))
        if method == "topk_softmax":
            held = np.array(state.held, dtype=bool) if len(state.held) == n else None
            return topk_softmax(score, int(base_cfg.get("k", 5)), float(base_cfg.get("temperature", 0.35)), 1.0, cap,
                                held=held, exit_rank=base_cfg.get("exit_rank"),
                                positive_only=bool(base_cfg.get("positive_only", False)))
        if method == "optimizer":
            cov = self._require(cov, method)
            horizon = str(base_cfg.get("alpha_horizon", "1d"))
            h_bars = view.bars(HORIZON_HOURS[horizon])
            alpha = grinold_alpha(score, vol, float(base_cfg.get("ic", 0.03)), h_bars)
            cov_h = cov * h_bars
            gamma = float(base_cfg.get("gamma", self.fee_rate))
            res = optimize(alpha, cov_h, current, lam=float(base_cfg.get("risk_aversion", 5.0)), gamma=gamma,
                           gross=float(base_cfg.get("max_gross", 1.0)), cons=self.cons)
            diag["optimizer"] = {"iterations": res.iterations, "converged": res.converged, "objective": res.objective}
            return res.weights
        raise ValueError(f"unknown base method {method!r}")
