"""N/I/S composition pipeline for the News Overlay scaffold."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from time import perf_counter
from typing import Any

from nlpcc.news_overlay.base import MethodRunContext, MethodRunResult
from nlpcc.news_overlay.config import NewsOverlayConfig
from nlpcc.news_overlay.gpu import resolve_device
from nlpcc.news_overlay.registry import instantiate_method, validate_track_compatibility
from nlpcc.news_overlay.traces import NewsOverlayTrace


@dataclass(frozen=True)
class ScaffoldNewsOverlayPipeline:
    """Minimal transformer-first scaffold pipeline."""

    config: NewsOverlayConfig

    def _context(self) -> MethodRunContext:
        return MethodRunContext(
            track=self.config.track,
            offline=self.config.offline,
            device=resolve_device(self.config.device),
            cache_dir=self.config.cache_dir,
            local_model_paths=dict(self.config.local_model_paths),
            disabled_methods=self.config.disabled_methods,
            preprocessing_version=self.config.preprocessing_version,
            feature_schema_version=self.config.feature_schema_version,
            batch_size=self.config.batch_size,
        )

    def run(self, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        codes = (self.config.n_method, self.config.i_method, self.config.s_method)
        validate_track_compatibility(self.config.track, codes)
        context = self._context()
        working_payload: dict[str, Any] = dict(payload or {})
        method_results: dict[str, dict[str, Any]] = {}
        working_payload["method_results"] = method_results
        working_payload["runtime_config"] = _config_summary(self.config, context)
        results: list[MethodRunResult] = []
        method_runtime: dict[str, float] = {}
        started = perf_counter()
        for code in codes:
            method_started = perf_counter()
            result = instantiate_method(code).run(context, working_payload)
            method_runtime[code] = round(perf_counter() - method_started, 6)
            results.append(result)
            result_dict = result.as_dict()
            method_results[code] = result_dict
            if result.kind == "N":
                working_payload["n_result"] = result_dict
            elif result.kind == "I":
                working_payload["i_result"] = result_dict
            elif result.kind == "S":
                working_payload["s_result"] = result_dict
        elapsed = round(perf_counter() - started, 6)
        runtime_report = _runtime_report(method_runtime, elapsed, context)
        cache_report = _cache_report(results)
        summaries = _trace_summaries(results)
        trace = NewsOverlayTrace(
            trace_id=_trace_id(self.config.track, codes),
            track=self.config.track,
            n_method=self.config.n_method,
            i_method=self.config.i_method,
            s_method=self.config.s_method,
            results=tuple(results),
            config=_config_summary(self.config, context),
            runtime_report=runtime_report,
            cache_report=cache_report,
            model_status=_model_status(results, context),
            summaries=summaries,
            warnings=_warnings(results, summaries),
        )
        return trace.as_dict()


def _trace_id(track: str, codes: tuple[str, str, str]) -> str:
    return sha256(f"{track}:{':'.join(codes)}".encode("utf-8")).hexdigest()[:16]


def _config_summary(config: NewsOverlayConfig, context: MethodRunContext) -> dict[str, Any]:
    return {
        "track": config.track,
        "n_method": config.n_method,
        "i_method": config.i_method,
        "s_method": config.s_method,
        "offline": config.offline,
        "requested_device": config.device,
        "resolved_device": context.device,
        "cache_dir": config.cache_dir,
        "trace_dir": config.trace_dir,
        "batch_size": context.batch_size,
        "preprocessing_version": config.preprocessing_version,
        "feature_schema_version": config.feature_schema_version,
        "disabled_methods": tuple(sorted(config.disabled_methods)),
    }


def _runtime_report(method_runtime: dict[str, float], elapsed: float, context: MethodRunContext) -> dict[str, Any]:
    return {
        "total_runtime_seconds": elapsed,
        "method_runtime_seconds": method_runtime,
        "device": context.device,
        "batch_size": context.batch_size,
        "offline": context.offline,
    }


def _cache_report(results: list[MethodRunResult]) -> dict[str, Any]:
    rows = []
    for result in results:
        diagnostics = result.diagnostics or {}
        rows.append(
            {
                "method_code": result.method_code,
                "cache_key": diagnostics.get("cache_key") or result.outputs.get("cache_key"),
                "cache_hit": bool(diagnostics.get("cache_hit", False)),
                "cache_required": bool(result.outputs.get("cache_key") or diagnostics.get("cache_key")),
            }
        )
    cacheable = [row for row in rows if row["cache_required"]]
    hit_count = sum(1 for row in cacheable if row["cache_hit"])
    return {
        "rows": rows,
        "cacheable_methods": len(cacheable),
        "cache_hits": hit_count,
        "cache_hit_rate": round(hit_count / len(cacheable), 6) if cacheable else 0.0,
    }


def _model_status(results: list[MethodRunResult], context: MethodRunContext) -> dict[str, Any]:
    rows = []
    for result in results:
        availability = (result.diagnostics or {}).get("availability") or {}
        rows.append(
            {
                "method_code": result.method_code,
                "status": result.status.value,
                "fallback_code": result.fallback_code,
                "transformer_used": result.transformer_used,
                "model_identifier": availability.get("model_identifier"),
                "local_model_path": availability.get("local_path"),
                "dependency": availability.get("dependency"),
                "reason": availability.get("reason"),
                "network_attempted": result.network_attempted or bool(availability.get("network_attempted")),
                "device": availability.get("device") or context.device,
            }
        )
    return {
        "rows": rows,
        "network_attempted": any(row["network_attempted"] for row in rows),
        "blocked_methods": tuple(row["method_code"] for row in rows if str(row["status"]).startswith("blocked_")),
    }


def _trace_summaries(results: list[MethodRunResult]) -> dict[str, Any]:
    n_result = next((result for result in results if result.kind == "N"), None)
    i_result = next((result for result in results if result.kind == "I"), None)
    s_result = next((result for result in results if result.kind == "S"), None)
    n_outputs = n_result.outputs if n_result else {}
    i_outputs = i_result.outputs if i_result else {}
    s_outputs = s_result.outputs if s_result else {}
    return {
        "embedding_summary": _embedding_summary(n_outputs),
        "aspect_tone_summary": _aspect_tone_summary(n_outputs),
        "label_attention_labels": _label_attention_summary(n_outputs),
        "sector_query_attention_top_news": _sector_attention_summary(n_outputs),
        "cross_encoder_scores": _cross_encoder_summary(n_outputs),
        "impact_components": _impact_summary(i_outputs),
        "sensitivity_components": _sensitivity_summary(s_outputs),
        "gate_decisions": _gate_decisions(s_outputs),
        "base_weights": _score_dict(s_outputs.get("base_weights") or {}),
        "final_weights": _score_dict(s_outputs.get("adjusted_weights") or {}),
    }


def _embedding_summary(outputs: dict[str, Any]) -> dict[str, Any]:
    rows = list(outputs.get("feature_rows") or ())
    daily = outputs.get("daily_features") or {}
    return {
        "backend": outputs.get("embedding_backend") or "not_applicable_or_component",
        "feature_row_count": len(rows),
        "top_relevance": _top_scores(daily.get("relevance_by_sector") or _merge_row_scores(rows, "relevance_by_sector")),
    }


def _aspect_tone_summary(outputs: dict[str, Any]) -> dict[str, float]:
    rows = list(outputs.get("feature_rows") or ())
    sums: dict[str, float] = {}
    counts: dict[str, int] = {}
    for row in rows:
        for aspect, value in _score_dict(row.get("aspect_tone") or {}).items():
            sums[aspect] = sums.get(aspect, 0.0) + value
            counts[aspect] = counts.get(aspect, 0) + 1
    return {aspect: round(sums[aspect] / max(1, counts[aspect]), 6) for aspect in sorted(sums)}


def _label_attention_summary(outputs: dict[str, Any]) -> dict[str, float]:
    return _top_scores(_merge_row_scores(list(outputs.get("feature_rows") or ()), "label_attention_scores"))


def _sector_attention_summary(outputs: dict[str, Any]) -> dict[str, Any]:
    attention = outputs.get("sector_attention") or {}
    top: dict[str, list[dict[str, Any]]] = {}
    for sector, weights in attention.items():
        if not isinstance(weights, dict):
            continue
        top[sector] = [
            {"news_id": news_id, "attention_weight": round(float(weight), 6)}
            for news_id, weight in sorted(weights.items(), key=lambda item: (-float(item[1]), str(item[0])))[:3]
        ]
    if top:
        return top
    rows = list(outputs.get("feature_rows") or ())
    row_attention: dict[str, dict[str, float]] = {}
    for row in rows:
        news_id = str(row.get("news_id") or "unknown")
        for sector, value in _score_dict(row.get("sector_query_attention_weights") or {}).items():
            row_attention.setdefault(sector, {})[news_id] = value
    return {
        sector: [
            {"news_id": news_id, "attention_weight": round(weight, 6)}
            for news_id, weight in sorted(weights.items(), key=lambda item: (-item[1], item[0]))[:3]
        ]
        for sector, weights in sorted(row_attention.items())
    }


def _cross_encoder_summary(outputs: dict[str, Any]) -> dict[str, Any]:
    rows = list(outputs.get("feature_rows") or ())
    warnings = tuple(sorted({warning for row in rows for warning in row.get("warnings", ()) or ()}))
    return {
        "available": bool(outputs.get("cross_encoder_scores")),
        "scores": outputs.get("cross_encoder_scores") or {},
        "warnings": warnings,
    }


def _impact_summary(outputs: dict[str, Any]) -> dict[str, Any]:
    rows = list(outputs.get("impact_rows") or ())
    return {
        "impact_by_sector": _score_dict(outputs.get("impact_by_sector") or {}),
        "row_count": len(rows),
        "backend": outputs.get("impact_backend"),
        "component_methods": tuple(
            result.get("method_code")
            for result in outputs.get("component_traces", ())
            if isinstance(result, dict)
        ),
    }


def _sensitivity_summary(outputs: dict[str, Any]) -> dict[str, Any]:
    return {
        "overlay_by_asset": _score_dict(outputs.get("overlay_by_asset") or {}),
        "adjusted_weights": _score_dict(outputs.get("adjusted_weights") or {}),
        "backend": outputs.get("overlay_backend"),
        "component_methods": tuple(
            result.get("method_code")
            for result in outputs.get("component_traces", ())
            if isinstance(result, dict)
        ),
    }


def _gate_decisions(outputs: dict[str, Any]) -> dict[str, Any]:
    diagnostics = outputs.get("gate_diagnostics") or {}
    return {
        "rank_ic_pass": diagnostics.get("rank_ic_pass"),
        "risk_multiplier": diagnostics.get("risk_multiplier"),
        "final_weight_constraints": diagnostics.get("final_weight_constraints"),
        "warnings": outputs.get("warnings") or (),
    }


def _warnings(results: list[MethodRunResult], summaries: dict[str, Any]) -> tuple[str, ...]:
    values: set[str] = set()
    for result in results:
        for warning in result.outputs.get("warnings", ()) or ():
            values.add(str(warning))
        if result.fallback_code:
            values.add(f"{result.method_code}_fallback_{result.fallback_code}")
        if result.status.value.startswith("blocked_"):
            values.add(f"{result.method_code}_{result.status.value}")
    for warning in (summaries.get("gate_decisions") or {}).get("warnings", ()) or ():
        values.add(str(warning))
    return tuple(sorted(values))


def _merge_row_scores(rows: list[dict[str, Any]], field: str) -> dict[str, float]:
    scores: dict[str, float] = {}
    for row in rows:
        for key, value in _score_dict(row.get(field) or {}).items():
            scores[key] = scores.get(key, 0.0) + value
    return scores


def _score_dict(value: Any) -> dict[str, float]:
    if not isinstance(value, dict):
        return {}
    return {str(key): round(float(score), 6) for key, score in value.items() if score is not None}


def _top_scores(scores: dict[str, float], limit: int = 8) -> dict[str, float]:
    return {
        key: round(float(value), 6)
        for key, value in sorted(scores.items(), key=lambda item: (-abs(float(item[1])), item[0]))[:limit]
        if abs(float(value)) > 1e-12
    }
