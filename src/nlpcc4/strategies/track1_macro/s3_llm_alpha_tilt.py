"""S3 Track 1 risk-budgeted LLM alpha-tilt optimizer."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

from nlpcc4.common.types import DecisionContext, StrategyOutput
from nlpcc4.execution.constraints import project_long_only
from nlpcc4.llm.client import LLMRequest, LLMUnavailable, request_llm_json
from nlpcc4.llm.manual_io import ManualResponseInvalid, ManualResponseMissing
from nlpcc4.llm.schemas import AlphaSignal
from nlpcc4.llm.validators import validate_alpha_signal
from nlpcc4.strategies.shared.risk_budget import allocate_risk_budget
from nlpcc4.strategies.track1_macro.s1_quant_core import Track1S1QuantCore
from nlpcc4.strategies.track1_macro.s2_llm_regime import _news_block
from nlpcc4.strategies.track1_macro.universe import TRACK1_UNIVERSE


def _alpha_prompt_path() -> Path:
    return Path(__file__).resolve().parents[2] / "llm" / "prompts" / "alpha_score.md"


def _apply_alpha_tilt(
    base_weights: Mapping[str, float],
    alpha_signal: AlphaSignal,
    fund_pool: Sequence[str],
    *,
    historical_prices: Mapping[str, Sequence[Mapping]],
    max_deviation: float,
    max_weight: float,
    cash_buffer: float,
    volatility_window: int,
) -> dict[str, float]:
    score_map = {asset: 0.0 for asset in fund_pool}
    for item in alpha_signal.scores:
        if item.asset in score_map:
            score_map[item.asset] += item.score * item.confidence * alpha_signal.overall_confidence
    positive_scores = {asset: max(0.0, 1.0 + score_map.get(asset, 0.0)) for asset in fund_pool}
    tilted = allocate_risk_budget(
        positive_scores,
        historical_prices,
        volatility_window=volatility_window,
        cash_buffer=cash_buffer,
        max_weight=max_weight,
        universe=fund_pool,
    )
    bounded = {}
    for asset in fund_pool:
        base = float(base_weights.get(asset, 0.0))
        delta = max(-max_deviation, min(max_deviation, tilted.get(asset, 0.0) - base))
        bounded[asset] = max(0.0, base + delta)
    return project_long_only(bounded, universe=fund_pool, max_weight=max_weight, cash_buffer=cash_buffer)


@dataclass
class Track1S3LLMAlphaTilt:
    config: Mapping[str, Any]
    name: str = "s3_llm_alpha_tilt"

    def compute_target_weights(self, context: DecisionContext) -> StrategyOutput:
        base = Track1S1QuantCore(self.config).compute_target_weights(context)
        fund_pool = tuple(context.fund_pool or TRACK1_UNIVERSE)
        llm_cfg = self.config.get("llm", {})
        portfolio = self.config.get("portfolio", {})
        risk = self.config.get("risk", {})
        mode = context.llm_mode or llm_cfg.get("mode", "off")
        diagnostics: dict[str, Any] = {"strategy": self.name, "fallback_strategy": "s1_quant_core"}
        if mode == "off":
            diagnostics["fallback_reason"] = "llm_mode_off"
            return StrategyOutput(base.target_weights, diagnostics)
        prompt = (
            _alpha_prompt_path()
            .read_text(encoding="utf-8")
            .replace("{decision_date}", context.decision_date)
            .replace("{track}", context.track)
            .replace("{fund_pool}", ", ".join(fund_pool))
            .replace("{base_weights}", str(dict(base.target_weights)))
            .replace("{quant_context}", str({"base_diagnostics": base.diagnostics}))
            .replace("{news_block}", _news_block(context.news))
        )
        request = LLMRequest(mode=mode, prompt=prompt, run_id=context.run_id, stem=f"{context.decision_date.replace('-', '')}_{context.track}_{self.name}_alpha")
        try:
            signal, llm_diag = request_llm_json(request, validate_alpha_signal)
        except (ManualResponseMissing, ManualResponseInvalid):
            raise
        except (LLMUnavailable, Exception) as exc:
            diagnostics["fallback_reason"] = f"llm_invalid_or_unavailable: {exc}"
            return StrategyOutput(base.target_weights, diagnostics)
        assert isinstance(signal, AlphaSignal)
        diagnostics.update(llm_diag)
        diagnostics["overall_confidence"] = signal.overall_confidence
        if signal.overall_confidence < float(llm_cfg.get("confidence_threshold", 0.50)) or not signal.scores:
            diagnostics["fallback_reason"] = "weak_or_empty_alpha_signal"
            return StrategyOutput(base.target_weights, diagnostics)
        final_weights = _apply_alpha_tilt(
            base.target_weights,
            signal,
            fund_pool,
            historical_prices=context.historical_prices,
            max_deviation=float(llm_cfg.get("max_weight_deviation_from_base", 0.08)),
            max_weight=float(portfolio.get("max_single_weight", 0.30)),
            cash_buffer=float(portfolio.get("cash_buffer", 0.01)),
            volatility_window=int(risk.get("volatility_window", self.config.get("signals", {}).get("volatility_window", 20))),
        )
        diagnostics["alpha_scores"] = [
            {"asset": score.asset, "score": score.score, "confidence": score.confidence, "reason_tag": score.reason_tag}
            for score in signal.scores
        ]
        return StrategyOutput(final_weights, diagnostics)


def build_strategy(config: Mapping[str, Any] | None = None) -> Track1S3LLMAlphaTilt:
    return Track1S3LLMAlphaTilt(config or {})
