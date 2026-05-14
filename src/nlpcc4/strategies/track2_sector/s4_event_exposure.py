"""S4 Track 2 event-to-exposure sector mapper."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from nlpcc4.common.types import DecisionContext, StrategyOutput
from nlpcc4.data.features import momentum_return
from nlpcc4.execution.constraints import blend_weights, project_long_only
from nlpcc4.llm.client import LLMRequest, LLMUnavailable, request_llm_json
from nlpcc4.llm.manual_io import ManualResponseInvalid, ManualResponseMissing
from nlpcc4.llm.validators import validate_event_exposure_signal
from nlpcc4.strategies.track1_macro.s2_llm_regime import _news_block
from nlpcc4.strategies.track2_sector.event_taxonomy import SECTOR_EXPOSURE_MAP
from nlpcc4.strategies.track2_sector.s1_quant_core import Track2S1QuantCore
from nlpcc4.strategies.track2_sector.sector_groups import SECTOR_GROUPS
from nlpcc4.strategies.track2_sector.universe import TRACK2_UNIVERSE


def _event_prompt_path() -> Path:
    return Path(__file__).resolve().parents[2] / "llm" / "prompts" / "event_exposure.md"


def _map_sector_to_assets(sector: str, fund_pool: tuple[str, ...]) -> tuple[str, ...]:
    text = sector.lower().replace("-", "_").replace(" ", "_")
    for key, assets in SECTOR_EXPOSURE_MAP.items():
        if key in text:
            return tuple(asset for asset in assets if asset in fund_pool)
    for group, assets in SECTOR_GROUPS.items():
        if group in text:
            return tuple(asset for asset in assets if asset in fund_pool)
    return ()


@dataclass
class Track2S4EventExposure:
    config: Mapping[str, Any]
    name: str = "s4_event_exposure"

    def compute_target_weights(self, context: DecisionContext) -> StrategyOutput:
        base = Track2S1QuantCore(self.config).compute_target_weights(context)
        fund_pool = tuple(context.fund_pool or TRACK2_UNIVERSE)
        llm_cfg = self.config.get("llm", {})
        portfolio = self.config.get("portfolio", {})
        signals = self.config.get("signals", {})
        mode = context.llm_mode or llm_cfg.get("mode", "off")
        diagnostics: dict[str, Any] = {"strategy": self.name, "fallback_strategy": "s1_quant_core"}
        if mode == "off":
            diagnostics["fallback_reason"] = "llm_mode_off"
            return StrategyOutput(base.target_weights, diagnostics)
        trend_context = {
            asset: momentum_return(context.historical_prices.get(asset, ()), int(signals.get("trend_confirmation_window", 20)))
            for asset in fund_pool
        }
        prompt = (
            _event_prompt_path()
            .read_text(encoding="utf-8")
            .replace("{decision_date}", context.decision_date)
            .replace("{track}", context.track)
            .replace("{sector_groups}", str(SECTOR_GROUPS))
            .replace("{quant_context}", str(trend_context))
            .replace("{news_block}", _news_block(context.news))
        )
        request = LLMRequest(mode=mode, prompt=prompt, run_id=context.run_id, stem=f"{context.decision_date.replace('-', '')}_{context.track}_{self.name}_events")
        try:
            signal, llm_diag = request_llm_json(request, validate_event_exposure_signal)
        except (ManualResponseMissing, ManualResponseInvalid):
            raise
        except (LLMUnavailable, Exception) as exc:
            diagnostics["fallback_reason"] = f"llm_invalid_or_unavailable: {exc}"
            return StrategyOutput(base.target_weights, diagnostics)
        diagnostics.update(llm_diag)
        diagnostics["overall_confidence"] = signal.overall_confidence
        if signal.overall_confidence < float(llm_cfg.get("confidence_threshold", 0.50)) or not signal.events:
            diagnostics["fallback_reason"] = "weak_or_empty_event_signal"
            return StrategyOutput(base.target_weights, diagnostics)
        exposure = {asset: 0.0 for asset in fund_pool}
        threshold = float(signals.get("event_confidence_threshold", 0.45))
        for event in signal.events:
            if event.confidence < threshold:
                continue
            assets = _map_sector_to_assets(event.affected_sector, fund_pool)
            if not assets:
                continue
            for asset in assets:
                trend = trend_context.get(asset, 0.0)
                if event.direction > 0 and trend < float(signals.get("negative_trend_block", -0.05)):
                    continue
                exposure[asset] += event.direction * event.magnitude * event.confidence
        if max((abs(value) for value in exposure.values()), default=0.0) <= 1e-12:
            diagnostics["fallback_reason"] = "no_confirmed_event_exposure"
            return StrategyOutput(base.target_weights, diagnostics)
        shifted = {
            asset: max(0.0, base.target_weights.get(asset, 0.0) + float(signals.get("event_weight_scale", 0.12)) * exposure[asset])
            for asset in fund_pool
        }
        event_target = project_long_only(
            shifted,
            universe=fund_pool,
            max_weight=portfolio.get("max_single_weight", 0.22),
            cash_buffer=float(portfolio.get("cash_buffer", 0.01)),
        )
        alpha = min(float(llm_cfg.get("max_blend", 0.30)), signal.overall_confidence * 0.30)
        final = project_long_only(
            blend_weights(base.target_weights, event_target, alpha, universe=fund_pool),
            universe=fund_pool,
            max_weight=portfolio.get("max_single_weight", 0.22),
            cash_buffer=float(portfolio.get("cash_buffer", 0.01)),
        )
        diagnostics.update({"blend_alpha": alpha, "event_exposure": exposure})
        return StrategyOutput(final, diagnostics)


def build_strategy(config: Mapping[str, Any] | None = None) -> Track2S4EventExposure:
    return Track2S4EventExposure(config or {})
