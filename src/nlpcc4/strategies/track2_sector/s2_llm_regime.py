"""S2 Track 2 structured LLM regime-to-rules allocator."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from nlpcc4.common.types import DecisionContext, StrategyOutput
from nlpcc4.execution.constraints import blend_weights, project_long_only
from nlpcc4.llm.client import LLMRequest, LLMUnavailable, request_llm_json
from nlpcc4.llm.manual_io import ManualResponseInvalid, ManualResponseMissing
from nlpcc4.llm.validators import validate_regime_signal
from nlpcc4.strategies.track1_macro.s2_llm_regime import _news_block, _prompt_path
from nlpcc4.strategies.track2_sector.sector_groups import SECTOR_GROUPS
from nlpcc4.strategies.track2_sector.s1_quant_core import Track2S1QuantCore
from nlpcc4.strategies.track2_sector.universe import TRACK2_UNIVERSE


def _track2_regime_weights(regime: str, fund_pool: tuple[str, ...]) -> dict[str, float]:
    raw = {asset: 1.0 for asset in fund_pool}
    if regime in {"risk_on", "policy_easing", "sector_policy_positive"}:
        for asset in SECTOR_GROUPS["technology"] + SECTOR_GROUPS["financials"]:
            if asset in raw:
                raw[asset] += 2.0
    elif regime in {"risk_off", "growth_slowdown"}:
        for asset in SECTOR_GROUPS["consumption"] + SECTOR_GROUPS["healthcare"]:
            if asset in raw:
                raw[asset] += 2.0
    elif regime == "inflation_commodity":
        for asset in SECTOR_GROUPS["materials_energy"]:
            if asset in raw:
                raw[asset] += 3.0
    return raw


@dataclass
class Track2S2LLMRegime:
    config: Mapping[str, Any]
    name: str = "s2_llm_regime"

    def compute_target_weights(self, context: DecisionContext) -> StrategyOutput:
        s1 = Track2S1QuantCore(self.config)
        base = s1.compute_target_weights(context)
        fund_pool = tuple(context.fund_pool or TRACK2_UNIVERSE)
        llm_cfg = self.config.get("llm", {})
        portfolio = self.config.get("portfolio", {})
        mode = context.llm_mode or llm_cfg.get("mode", "off")
        diagnostics: dict[str, Any] = {"strategy": self.name, "fallback_strategy": "s1_quant_core"}
        if mode == "off":
            diagnostics["fallback_reason"] = "llm_mode_off"
            return StrategyOutput(base.target_weights, diagnostics)
        prompt = (
            _prompt_path()
            .read_text(encoding="utf-8")
            .replace("{decision_date}", context.decision_date)
            .replace("{track}", context.track)
            .replace("{fund_pool}", ", ".join(fund_pool))
            .replace("{quant_context}", str({"base_weights": dict(base.target_weights)}))
            .replace("{news_block}", _news_block(context.news))
        )
        request = LLMRequest(mode=mode, prompt=prompt, run_id=context.run_id, stem=f"{context.decision_date.replace('-', '')}_{context.track}_{self.name}_regime")
        try:
            signal, llm_diag = request_llm_json(request, validate_regime_signal)
        except (ManualResponseMissing, ManualResponseInvalid):
            raise
        except (LLMUnavailable, Exception) as exc:
            diagnostics["fallback_reason"] = f"llm_invalid_or_unavailable: {exc}"
            return StrategyOutput(base.target_weights, diagnostics)
        diagnostics.update(llm_diag)
        diagnostics["regime_signal"] = {"regime": signal.regime, "confidence": signal.confidence}
        if signal.confidence < float(llm_cfg.get("confidence_threshold", 0.55)) or signal.regime == "uncertain":
            diagnostics["fallback_reason"] = "low_confidence_or_uncertain"
            return StrategyOutput(base.target_weights, diagnostics)
        regime_target = project_long_only(
            _track2_regime_weights(signal.regime, fund_pool),
            universe=fund_pool,
            max_weight=portfolio.get("max_single_weight", 0.22),
            cash_buffer=float(portfolio.get("cash_buffer", 0.01)),
        )
        alpha = min(float(llm_cfg.get("max_blend", 0.25)), signal.confidence * 0.25)
        final = project_long_only(
            blend_weights(base.target_weights, regime_target, alpha, universe=fund_pool),
            universe=fund_pool,
            max_weight=portfolio.get("max_single_weight", 0.22),
            cash_buffer=float(portfolio.get("cash_buffer", 0.01)),
        )
        diagnostics.update({"blend_alpha": alpha, "regime_target": regime_target})
        return StrategyOutput(final, diagnostics)


def build_strategy(config: Mapping[str, Any] | None = None) -> Track2S2LLMRegime:
    return Track2S2LLMRegime(config or {})
