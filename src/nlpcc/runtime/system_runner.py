"""Runtime orchestration path for official and local execution."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Mapping

from nlpcc.core.fund_universe import TrackName, get_fund_pool
from nlpcc.execution.official_adapter import build_agent_input, normalize_track
from nlpcc.execution.order_planner import OrderPlannerConfig, OrderPlan, plan_orders_from_target_weights
from nlpcc.runtime.decision_trace import DecisionTrace, FallbackEvent
from nlpcc.stage4_agent.models.conservative_ensemble_agent import ConservativeEnsembleAgent
from nlpcc.stage4_agent.models.kg_moe_lite_agent import KGMoELiteAgent
from nlpcc.stage4_agent.models.oco_ensemble_agent import OCOEnsembleAgent
from nlpcc.stage4_agent.models.risk_parity_agent import RiskParityAgent
from nlpcc.stage4_agent.models.robust_bl_agent import RobustBLAgent
from nlpcc.stage4_agent.models.s0_equal_weight_agent import S0EqualWeightAgent
from nlpcc.stage4_agent.models.s1_quant_core import S1QuantCoreAgent
from nlpcc.stage4_agent.models.sector_rotation_agent import SectorRotationAgent


SYSTEM_ALIASES: dict[str, str] = {
    "s0_equal_weight_macro": "s0_equal_weight",
    "s0_macro": "s0_equal_weight",
    "s0_sector": "s0_equal_weight",
    "s1_quant_core": "s1_macro",
    "s1_track1": "s1_macro",
    "s1_track2": "s1_sector",
    "robust_bl": "robust_bl_track1",
    "sector_rotation": "sector_rotation_track2",
    "oco_fallback_macro": "oco_fallback",
}


@dataclass(frozen=True)
class SystemRunnerConfig:
    track: TrackName = "macro"
    strategy: str = "robust_bl_track1"
    fallback_strategy: str = "s1_macro"
    config_root: Path | None = None
    trace_dir: Path | None = None

    @classmethod
    def for_track(
        cls,
        track: str | None,
        *,
        strategy: str | None = None,
        fallback_strategy: str | None = None,
        config_root: Path | None = None,
        trace_dir: Path | None = None,
    ) -> "SystemRunnerConfig":
        resolved_track = normalize_track(track)
        if resolved_track == "sector":
            return cls(
                track="sector",
                strategy=strategy or "s1_sector",
                fallback_strategy=fallback_strategy or "s1_sector",
                config_root=config_root,
                trace_dir=trace_dir,
            )
        return cls(
            track="macro",
            strategy=strategy or "robust_bl_track1",
            fallback_strategy=fallback_strategy or "s1_macro",
            config_root=config_root,
            trace_dir=trace_dir,
        )


@dataclass(frozen=True)
class SystemDecision:
    target_weights: dict[str, float]
    official_trades: tuple[dict[str, float | str], ...]
    decision_trace: dict[str, Any]
    fallback_status: dict[str, Any]
    stage_outputs_summary: dict[str, Any]
    raw_decision: dict[str, Any]
    order_plan: OrderPlan

    def as_official_decision(self) -> dict[str, Any]:
        decision = dict(self.raw_decision)
        metadata = dict(decision.get("metadata", {}) or {})
        metadata["decision_trace"] = self.decision_trace
        metadata["fallback_status"] = self.fallback_status
        metadata["stage_outputs_summary"] = self.stage_outputs_summary
        metadata["order_plan"] = self.order_plan.diagnostics
        if self.order_plan.rejected_trades:
            metadata["rejected_trades"] = list(self.order_plan.rejected_trades)
        decision["metadata"] = metadata
        decision["target_weights"] = self.target_weights
        decision["trades"] = [dict(trade) for trade in self.official_trades]
        return decision

    def as_dict(self) -> dict[str, Any]:
        return {
            "target_weights": self.target_weights,
            "official_trades": [dict(trade) for trade in self.official_trades],
            "decision_trace": self.decision_trace,
            "fallback_status": self.fallback_status,
            "stage_outputs_summary": self.stage_outputs_summary,
            "raw_decision": self.raw_decision,
            "order_plan": {
                "trades": [dict(trade) for trade in self.order_plan.trades],
                "rejected_trades": list(self.order_plan.rejected_trades),
                "diagnostics": self.order_plan.diagnostics,
            },
        }


@dataclass
class SystemRunner:
    config: SystemRunnerConfig = field(default_factory=SystemRunnerConfig)

    @classmethod
    def for_track(
        cls,
        track: str | None,
        *,
        strategy: str | None = None,
        fallback_strategy: str | None = None,
        config_root: Path | None = None,
        trace_dir: Path | None = None,
    ) -> "SystemRunner":
        return cls(
            SystemRunnerConfig.for_track(
                track,
                strategy=strategy,
                fallback_strategy=fallback_strategy,
                config_root=config_root,
                trace_dir=trace_dir,
            )
        )

    def run_day(
        self,
        *,
        track: str | None = None,
        fund_pool: list[str] | tuple[str, ...] | None = None,
        historical_prices: Mapping[str, list[dict[str, Any]]] | None = None,
        news: list[dict[str, Any]] | None = None,
        current_portfolio: Mapping[str, Any] | None = None,
        date_to_decision: str | int | None = None,
        market_data: Mapping[str, Any] | None = None,
    ) -> SystemDecision:
        del market_data
        resolved_track = normalize_track(track or self.config.track)
        pool = tuple(fund_pool or get_fund_pool(resolved_track))
        agent_input = build_agent_input(
            track=resolved_track,
            fund_pool=pool,
            historical_prices=historical_prices,
            news=news,
            current_portfolio=current_portfolio,
        )
        primary_name = _resolve_system_name(self.config.strategy, resolved_track)
        fallback_name = _resolve_system_name(self.config.fallback_strategy, resolved_track)
        primary_config = load_frozen_system_config(primary_name, config_root=self.config.config_root, track=resolved_track)
        fallback_config = load_frozen_system_config(fallback_name, config_root=self.config.config_root, track=resolved_track)
        trace = DecisionTrace(agent=primary_name, track=resolved_track, decision_date=_date_to_int(date_to_decision))
        fallback_status = {"fallback_used": False, "primary": primary_name, "fallback": fallback_name, "reason": None}

        try:
            primary = _build_agent(primary_config)
            decision = primary.make_decision(**_agent_kwargs(agent_input))
            if not isinstance(decision.get("target_weights"), dict):
                raise ValueError("missing_target_weights")
        except Exception as exc:
            trace = trace.add_event(
                FallbackEvent(
                    trigger="primary_exception",
                    reason=f"{type(exc).__name__}:{exc}",
                    source_agent=primary_name,
                    fallback_agent=fallback_name,
                )
            )
            fallback_status = {
                "fallback_used": True,
                "primary": primary_name,
                "fallback": fallback_name,
                "reason": f"{type(exc).__name__}:{exc}",
            }
            decision = self._run_fallback(fallback_config, agent_input, fallback_status)

        target_weights = {
            str(fund_id): max(0.0, float(weight))
            for fund_id, weight in (decision.get("target_weights", {}) or {}).items()
            if str(fund_id) in pool
        }
        planner_config = _planner_config_from_system_config(primary_config if not fallback_status["fallback_used"] else fallback_config)
        order_plan = plan_orders_from_target_weights(
            target_weights,
            current_portfolio=agent_input["current_portfolio"],
            current_open_by_fund=agent_input["current_open_by_fund"],
            fund_pool=pool,
            config=planner_config,
        )
        stage_summary = _stage_summary(decision, agent_input)
        trace_dict = trace.as_dict()
        trace_dict["order_plan_ok"] = order_plan.ok
        trace_dict["strategy"] = primary_name
        trace_dict["runner"] = "SystemRunner"
        return SystemDecision(
            target_weights=target_weights,
            official_trades=order_plan.trades,
            decision_trace=trace_dict,
            fallback_status=fallback_status,
            stage_outputs_summary=stage_summary,
            raw_decision=dict(decision),
            order_plan=order_plan,
        )

    def _run_fallback(
        self,
        fallback_config: Mapping[str, Any],
        agent_input: Mapping[str, Any],
        fallback_status: Mapping[str, Any],
    ) -> dict[str, Any]:
        try:
            decision = _build_agent(fallback_config).make_decision(**_agent_kwargs(agent_input))
            metadata = dict(decision.get("metadata", {}) or {})
            metadata["fallback_used"] = True
            metadata["fallback_reason"] = fallback_status.get("reason")
            decision["metadata"] = metadata
            return decision
        except Exception as exc:
            return {
                "trades": [],
                "target_weights": {},
                "reasoning": "Fallback failed; hold cash.",
                "metadata": {
                    "agent": "system_runner_cash_hold",
                    "fallback_used": True,
                    "fallback_reason": f"fallback_failure:{type(exc).__name__}:{exc}",
                    "current_day_fields_used": ["open"],
                    "forbidden_current_fields_used": [],
                },
            }


def load_frozen_system_config(
    system_name: str,
    *,
    config_root: Path | None = None,
    track: TrackName = "macro",
) -> dict[str, Any]:
    root = config_root or _repo_root() / "configs"
    resolved = _resolve_system_name(system_name, track)
    path = root / "systems" / f"{resolved}.yaml"
    if not path.exists():
        raise FileNotFoundError(f"Missing system config: {path}")
    system_config = _load_yaml_file(path)
    ref = system_config.get("config") or system_config.get("stage4_config")
    if ref:
        referenced = _load_yaml_file((path.parent / str(ref)).resolve())
        merged = {**referenced, **{key: value for key, value in system_config.items() if key not in {"config", "stage4_config"}}}
    else:
        merged = dict(system_config)
    merged.setdefault("track", track)
    return merged


def _build_agent(config: Mapping[str, Any]) -> Any:
    agent_name = str(config.get("agent") or config.get("name") or "")
    params = _agent_params(config)
    if agent_name == "s0_equal_weight":
        allowed = {key: params[key] for key in ("cash_reserve", "max_weight", "rebalance_threshold") if key in params}
        return S0EqualWeightAgent(**allowed)
    if agent_name == "s1_quant_core":
        return S1QuantCoreAgent.from_config(params)
    if agent_name == "risk_parity":
        return RiskParityAgent.from_config(params)
    if agent_name == "robust_bl":
        return RobustBLAgent.from_config(params)
    if agent_name == "sector_rotation":
        return SectorRotationAgent.from_config(params)
    if agent_name == "kg_moe_lite":
        return KGMoELiteAgent.from_config(params)
    if agent_name == "conservative_ensemble":
        return ConservativeEnsembleAgent.from_config(params)
    if agent_name == "oco_ensemble":
        return OCOEnsembleAgent.from_config(params)
    raise KeyError(f"unsupported_runtime_agent:{agent_name}")


def _agent_params(config: Mapping[str, Any]) -> dict[str, Any]:
    excluded = {
        "name",
        "agent",
        "description",
        "fallback",
        "fallback_role",
        "expected_outputs",
        "uses_news",
        "ablations",
        "stage4_config",
        "config",
    }
    return {key: value for key, value in config.items() if key not in excluded}


def _agent_kwargs(agent_input: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "track": agent_input["track"],
        "fund_pool": agent_input["fund_pool"],
        "historical_prices": agent_input["historical_prices"],
        "news": agent_input["news"],
        "current_portfolio": agent_input["current_portfolio"],
    }


def _planner_config_from_system_config(config: Mapping[str, Any]) -> OrderPlannerConfig:
    constraints = dict(config.get("constraints", {}) or {}) if isinstance(config.get("constraints"), Mapping) else {}
    for key in ("rebalance_threshold", "cash_reserve", "max_weight", "max_turnover"):
        if key in config:
            constraints[key] = config[key]
    return OrderPlannerConfig.from_mapping(constraints)


def _stage_summary(decision: Mapping[str, Any], agent_input: Mapping[str, Any]) -> dict[str, Any]:
    metadata = dict(decision.get("metadata", {}) or {})
    return {
        "stage1": {
            "method": "rule_based_default" if metadata.get("stage1_fallback_used") is not None else "not_used_or_no_news",
            "fallback_used": metadata.get("stage1_fallback_used"),
            "text_view_count": metadata.get("text_view_count"),
        },
        "stage2": {
            "bl_view_count": metadata.get("bl_view_count"),
            "sector_impact_count": metadata.get("sector_impact_count"),
            "diagnostics": metadata.get("stage2_diagnostics"),
        },
        "stage3": {
            "diagnostics": metadata.get("stage3_diagnostics"),
            "current_open_count": len(agent_input.get("current_open_by_fund", {})),
        },
        "stage4": {
            "agent": metadata.get("agent"),
            "track": metadata.get("track"),
            "fallback_used": metadata.get("fallback_used", False),
        },
        "execution": {
            "portfolio_holding_unit": agent_input["current_portfolio"].get("holding_unit"),
            "portfolio_source_fields": agent_input.get("portfolio_adapter", {}).get("source_fields", {}),
        },
    }


def _resolve_system_name(name: str, track: TrackName) -> str:
    resolved = SYSTEM_ALIASES.get(str(name), str(name))
    if resolved == "s1_quant_core":
        return "s1_sector" if track == "sector" else "s1_macro"
    if resolved == "s0_equal_weight" and track == "sector":
        return "s0_equal_weight"
    return resolved


def _date_to_int(value: str | int | None) -> int | None:
    if value is None or value == "":
        return None
    if isinstance(value, int):
        return value
    digits = "".join(char for char in str(value) if char.isdigit())
    return int(digits[:8]) if len(digits) >= 8 else None


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _load_yaml_file(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        loaded = yaml.safe_load(text) or {}
        if not isinstance(loaded, dict):
            raise ValueError(f"Config is not a mapping: {path}")
        return loaded
    except ModuleNotFoundError:
        parsed = _parse_simple_yaml(text)
        if not isinstance(parsed, dict):
            raise ValueError(f"Config is not a mapping: {path}")
        return parsed


def _parse_simple_yaml(text: str) -> Any:
    lines: list[tuple[int, str]] = []
    for raw in text.splitlines():
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        lines.append((indent, raw.strip()))
    if not lines:
        return {}
    value, _ = _parse_yaml_block(lines, 0, lines[0][0])
    return value


def _parse_yaml_block(lines: list[tuple[int, str]], index: int, indent: int) -> tuple[Any, int]:
    if index >= len(lines):
        return {}, index
    if lines[index][1].startswith("- "):
        return _parse_yaml_list(lines, index, indent)
    return _parse_yaml_dict(lines, index, indent)


def _parse_yaml_dict(lines: list[tuple[int, str]], index: int, indent: int) -> tuple[dict[str, Any], int]:
    output: dict[str, Any] = {}
    while index < len(lines):
        current_indent, text = lines[index]
        if current_indent < indent:
            break
        if current_indent > indent or text.startswith("- "):
            break
        key, separator, rest = text.partition(":")
        if not separator:
            output[key.strip()] = None
            index += 1
            continue
        key = key.strip()
        rest = rest.strip()
        if rest:
            output[key] = _parse_scalar(rest)
            index += 1
        else:
            next_index = index + 1
            if next_index < len(lines) and lines[next_index][0] > current_indent:
                child, next_index = _parse_yaml_block(lines, next_index, lines[next_index][0])
                output[key] = child
                index = next_index
            else:
                output[key] = None
                index += 1
    return output, index


def _parse_yaml_list(lines: list[tuple[int, str]], index: int, indent: int) -> tuple[list[Any], int]:
    output: list[Any] = []
    while index < len(lines):
        current_indent, text = lines[index]
        if current_indent < indent or current_indent != indent or not text.startswith("- "):
            break
        rest = text[2:].strip()
        if not rest:
            child, index = _parse_yaml_block(lines, index + 1, lines[index + 1][0])
            output.append(child)
            continue
        if ":" in rest and not rest.startswith(("'", '"')):
            item: dict[str, Any] = {}
            key, _, value = rest.partition(":")
            item[key.strip()] = _parse_scalar(value.strip()) if value.strip() else None
            index += 1
            if index < len(lines) and lines[index][0] > current_indent:
                child, index = _parse_yaml_block(lines, index, lines[index][0])
                if isinstance(child, dict):
                    item.update(child)
                else:
                    item[key.strip()] = child
            output.append(item)
        else:
            output.append(_parse_scalar(rest))
            index += 1
    return output, index


def _parse_scalar(value: str) -> Any:
    lowered = value.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "none", "~"}:
        return None
    if (value.startswith("'") and value.endswith("'")) or (value.startswith('"') and value.endswith('"')):
        return value[1:-1]
    try:
        if any(char in value for char in (".", "e", "E")):
            return float(value)
        return int(value)
    except ValueError:
        return value
