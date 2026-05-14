"""S2 Track 1 structured LLM regime-to-rules allocator."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from nlpcc4.common.types import DecisionContext, StrategyOutput
from nlpcc4.execution.constraints import blend_weights, project_long_only
from nlpcc4.execution.turnover import apply_turnover_cap
from nlpcc4.llm.client import LLMRequest, LLMUnavailable, request_llm_json
from nlpcc4.llm.manual_io import ManualResponseInvalid, ManualResponseMissing
from nlpcc4.llm.schemas import RegimeSignal
from nlpcc4.llm.validators import validate_regime_signal
from nlpcc4.strategies.track1_macro.regimes import REGIME_GROUP_WEIGHTS
from nlpcc4.strategies.track1_macro.s1_quant_core import Track1S1QuantCore
from nlpcc4.strategies.track1_macro.universe import (
    TRACK1_COMMODITY_ASSETS,
    TRACK1_DEFENSIVE_ASSETS,
    TRACK1_GROWTH_ASSETS,
    TRACK1_UNIVERSE,
)


def _news_block(news: Sequence[Mapping]) -> str:
    lines = []
    for item in news[:20]:
        title = item.get("TITLE", item.get("title", ""))
        content = item.get("CONTENT", item.get("content", ""))
        lines.append(f"- {title}: {str(content)[:240]}")
    return "\n".join(lines) if lines else "- No news available"


def _prompt_path() -> Path:
    return Path(__file__).resolve().parents[2] / "llm" / "prompts" / "regime_classifier.md"


def regime_rule_weights(regime: str, fund_pool: Sequence[str]) -> dict[str, float]:
    """Map a bounded regime label to deterministic Track 1 weights."""
    group_weights = REGIME_GROUP_WEIGHTS.get(regime, REGIME_GROUP_WEIGHTS["uncertain"])
    defensive = tuple(asset for asset in TRACK1_DEFENSIVE_ASSETS if asset in fund_pool)
    growth = tuple(asset for asset in TRACK1_GROWTH_ASSETS if asset in fund_pool)
    commodity = tuple(asset for asset in TRACK1_COMMODITY_ASSETS if asset in fund_pool)
    used = set(defensive) | set(growth) | set(commodity)
    equity = tuple(asset for asset in fund_pool if asset not in used)
    raw = {asset: 0.0 for asset in fund_pool}
    for group_name, assets in (
        ("defensive", defensive),
        ("growth", growth),
        ("commodity", commodity),
        ("equity", equity),
    ):
        if assets:
            each = group_weights.get(group_name, 0.0) / len(assets)
            for asset in assets:
                raw[asset] += each
    return raw


@dataclass
class Track1S2LLMRegime:
    """S1 base plus confidence-gated deterministic regime mapping."""

    config: Mapping[str, Any]
    name: str = "s2_llm_regime"

    def compute_target_weights(self, context: DecisionContext) -> StrategyOutput:
        s1 = Track1S1QuantCore(self.config)
        base = s1.compute_target_weights(context)
        fund_pool = tuple(context.fund_pool or TRACK1_UNIVERSE)
        llm_cfg = self.config.get("llm", {})
        portfolio = self.config.get("portfolio", {})
        execution = self.config.get("execution", {})
        mode = context.llm_mode or llm_cfg.get("mode", "off")
        diagnostics: dict[str, Any] = {"strategy": self.name, "fallback_strategy": "s1_quant_core"}
        if mode == "off":
            diagnostics.update({"fallback_reason": "llm_mode_off", "base_diagnostics": base.diagnostics})
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
        request = LLMRequest(
            mode=mode,
            prompt=prompt,
            run_id=context.run_id,
            stem=f"{context.decision_date.replace('-', '')}_{context.track}_{self.name}_regime",
            model=str(llm_cfg.get("model", "gpt-5")),
            api_base=llm_cfg.get("api_base"),
            temperature=float(llm_cfg.get("temperature", 0.0)),
        )
        try:
            signal, llm_diag = request_llm_json(request, validate_regime_signal)
        except (ManualResponseMissing, ManualResponseInvalid):
            raise
        except (LLMUnavailable, Exception) as exc:
            diagnostics.update({"fallback_reason": f"llm_invalid_or_unavailable: {exc}"})
            return StrategyOutput(base.target_weights, diagnostics)
        assert isinstance(signal, RegimeSignal)
        diagnostics.update(llm_diag)
        diagnostics["regime_signal"] = {
            "regime": signal.regime,
            "confidence": signal.confidence,
            "rationale": signal.rationale,
        }
        threshold = float(llm_cfg.get("confidence_threshold", 0.55))
        if signal.confidence < threshold or signal.regime == "uncertain":
            diagnostics["fallback_reason"] = "low_confidence_or_uncertain"
            return StrategyOutput(base.target_weights, diagnostics)
        regime_target = project_long_only(
            regime_rule_weights(signal.regime, fund_pool),
            universe=fund_pool,
            max_weight=portfolio.get("max_single_weight", 0.30),
            cash_buffer=float(portfolio.get("cash_buffer", 0.01)),
        )
        alpha = min(float(llm_cfg.get("max_blend", 0.35)), signal.confidence * float(llm_cfg.get("blend_scale", 0.35)))
        blended = blend_weights(base.target_weights, regime_target, alpha, universe=fund_pool)
        capped = apply_turnover_cap(
            context.previous_weights,
            blended,
            execution.get("max_daily_turnover", portfolio.get("max_daily_turnover", 0.20)),
            universe=fund_pool,
        )
        final_weights = project_long_only(
            capped,
            universe=fund_pool,
            max_weight=portfolio.get("max_single_weight", 0.30),
            cash_buffer=float(portfolio.get("cash_buffer", 0.01)),
        )
        diagnostics.update({"blend_alpha": alpha, "regime_target": regime_target})
        return StrategyOutput(final_weights, diagnostics)


def build_strategy(config: Mapping[str, Any] | None = None) -> Track1S2LLMRegime:
    """Build the Track 1 S2 strategy."""
    return Track1S2LLMRegime(config or {})
