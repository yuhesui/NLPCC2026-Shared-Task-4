"""Substage S sensitivity, gates, and bounded overlay implementations."""

from __future__ import annotations

from collections import defaultdict
from hashlib import sha256
import json
import math
from pathlib import Path
from typing import Any

from nlpcc.core.fund_universe import MACRO_FUND_POOL, SECTOR_FUND_POOL
from nlpcc.news_overlay.base import (
    AvailabilityStatus,
    MethodRunContext,
    MethodRunResult,
    MethodSpec,
    NewsSensitivityMethod,
)
from nlpcc.news_overlay.cache import build_cache_key
from nlpcc.news_overlay.model_availability import (
    check_model_availability,
    composite_asset_status,
    is_proxy_report,
    model_ref_for_cache,
)


MAX_ABS_TILT = 0.05
MAX_WEIGHT = 0.35
MAX_TURNOVER = 0.25
CASH_RESERVE = 0.03
REGRESSION_SHRINKAGE = 0.50
BL_VIEW_SHRINKAGE = 0.35

SECTOR_TO_ASSETS: dict[str, tuple[str, ...]] = {
    "bank": ("512800.SH", "000300.SH"),
    "brokerage": ("512880.SH", "000300.SH"),
    "insurance": ("512070.SH", "000300.SH"),
    "semiconductor": ("159995.SZ", "000688.SH", "399006.SZ"),
    "ai": ("159819.SZ", "399006.SZ", "000688.SH"),
    "communication": ("515880.SH", "399006.SZ"),
    "software": ("159852.SZ", "399006.SZ", "000688.SH"),
    "pharma": ("512010.SH",),
    "healthcare": ("512170.SH",),
    "innovative_drug": ("159992.SZ",),
    "food_beverage": ("515170.SH", "000932.SH"),
    "liquor": ("512690.SH", "000932.SH"),
    "nonferrous": ("512400.SH", "000819.SH"),
    "coal": ("515220.SH", "000928.SH"),
    "chemicals": ("159870.SZ", "000819.SH"),
    "real_estate": ("512200.SH", "000300.SH"),
    "consumer": ("000932.SH", "515170.SH", "512690.SH"),
    "new_energy": ("000941.SH",),
    "media": ("399971.SZ",),
    "energy": ("000928.SH", "515220.SH"),
    "materials": ("000819.SH", "512400.SH", "159870.SZ"),
    "broad_market": ("000300.SH", "000905.SH", "399006.SZ", "000688.SH"),
    "bond": ("000012.SH",),
    "gold": ("518880.SH",),
}

TRACK_A_RISKY_ASSETS = tuple(asset for asset in MACRO_FUND_POOL if asset not in {"000012.SH", "518880.SH"})
TRACK_A_DEFENSIVE_ASSETS = ("000012.SH", "518880.SH")


class RealNewsSensitivityMethod(NewsSensitivityMethod):
    """Concrete Substage S implementation with cache and bounded overlays."""

    def run(self, context: MethodRunContext, payload: dict[str, Any] | None = None) -> MethodRunResult:
        if context.track not in self.spec.supported_tracks:
            raise ValueError(f"{self.spec.code} is not compatible with Track {context.track}")

        data = payload or {}
        i_outputs = _extract_i_outputs(data)
        cache_key = _method_cache_key(self.spec, context, data, i_outputs)
        cached = _read_cache(context, self.spec.code, cache_key)
        if cached is not None:
            cached["diagnostics"]["cache_hit"] = True
            return MethodRunResult(
                method_code=self.spec.code,
                kind="S",
                status=AvailabilityStatus(cached["status"]),
                fallback_code=cached.get("fallback_code"),
                transformer_used=bool(cached.get("transformer_used")),
                network_attempted=False,
                outputs=cached["outputs"],
                diagnostics=cached["diagnostics"],
            )

        if self.spec.code == "S12":
            result = _run_composite(self.spec, context, data, i_outputs, cache_key, ("S1", "S2"))
        elif self.spec.code == "S13":
            result = _run_composite(self.spec, context, data, i_outputs, cache_key, ("S1", "S3"))
        elif self.spec.code == "S126":
            result = _run_composite(self.spec, context, data, i_outputs, cache_key, ("S1", "S2", "S6"))
        else:
            runners = {
                "S0": _run_s0,
                "S1": _run_s1,
                "S2": _run_s2,
                "S3": _run_s3,
                "S4": _run_s4,
                "S5": _run_s5,
                "S6": _run_s6,
                "S7": _run_s7,
            }
            result = runners[self.spec.code](self.spec, context, data, i_outputs, cache_key)
        _write_cache(context, self.spec.code, cache_key, result)
        return result


def _run_s0(
    spec: MethodSpec,
    context: MethodRunContext,
    data: dict[str, Any],
    i_outputs: dict[str, Any],
    cache_key: str,
) -> MethodRunResult:
    del i_outputs
    base_weights = _base_weights(context, data)
    return _result(
        spec,
        AvailabilityStatus.AVAILABLE,
        context,
        cache_key,
        data,
        sensitivity_rows=[],
        sensitivity_matrix={},
        overlay_by_asset={},
        adjusted_weights=base_weights,
        gate_diagnostics={"control": "no_sensitivity_uniform"},
        extra_outputs={"overlay_backend": "no_sensitivity_control"},
    )


def _run_s1(
    spec: MethodSpec,
    context: MethodRunContext,
    data: dict[str, Any],
    i_outputs: dict[str, Any],
    cache_key: str,
) -> MethodRunResult:
    impact_rows = _impact_rows(i_outputs)
    calibration_rows = _sensitivity_calibration_rows(data)
    sensitivity_matrix, provenance = _event_sensitivity_matrix(calibration_rows, impact_rows, context)
    overlay = _overlay_from_sensitivity(impact_rows, sensitivity_matrix, context, data)
    adjusted, constraints = _adjusted_weights(context, data, overlay)
    return _result(
        spec,
        AvailabilityStatus.AVAILABLE,
        context,
        cache_key,
        data,
        sensitivity_rows=_matrix_rows(spec.code, sensitivity_matrix, provenance),
        sensitivity_matrix=sensitivity_matrix,
        overlay_by_asset=overlay,
        adjusted_weights=adjusted,
        gate_diagnostics={"event_study_provenance": provenance, "final_weight_constraints": constraints},
        extra_outputs={"overlay_backend": "event_study_sensitivity"},
    )


def _run_s2(
    spec: MethodSpec,
    context: MethodRunContext,
    data: dict[str, Any],
    i_outputs: dict[str, Any],
    cache_key: str,
) -> MethodRunResult:
    rank_rows = _rank_ic_rows(data)
    rank_ics = [_rank_ic(row.get("news_scores") or row.get("scores") or {}, row.get("future_returns") or row.get("returns") or {}) for row in rank_rows]
    rank_ics = [value for value in rank_ics if value is not None]
    threshold = float(data.get("rank_ic_threshold", _rank_ic_threshold(rank_ics)))
    current_rank_ic = data.get("current_rank_ic")
    if current_rank_ic is None:
        current_rank_ic = rank_ics[-1] if rank_ics else _score_dispersion(_impact_by_sector(i_outputs))
    rank_ic_pass = float(current_rank_ic) >= threshold
    sector_scores = _impact_by_sector(i_outputs) if rank_ic_pass else {}
    overlay = _sector_scores_to_overlay(sector_scores, context, data, max_abs_tilt=_max_tilt(data, default=0.04), demean=True)
    adjusted, constraints = _adjusted_weights(context, data, overlay)
    diagnostics = {
        "rank_ic_values": [round(value, 6) for value in rank_ics],
        "rank_ic_threshold": round(threshold, 6),
        "current_rank_ic": round(float(current_rank_ic), 6),
        "rank_ic_pass": rank_ic_pass,
        "construction_period": "2024_only",
        "final_weight_constraints": constraints,
    }
    return _result(
        spec,
        AvailabilityStatus.AVAILABLE,
        context,
        cache_key,
        data,
        sensitivity_rows=[{"method_code": spec.code, "rank_ic": value} for value in diagnostics["rank_ic_values"]],
        sensitivity_matrix={},
        overlay_by_asset=overlay,
        adjusted_weights=adjusted,
        gate_diagnostics=diagnostics,
        extra_outputs={"overlay_backend": "rank_ic_gated_sector_momentum"},
    )


def _run_s3(
    spec: MethodSpec,
    context: MethodRunContext,
    data: dict[str, Any],
    i_outputs: dict[str, Any],
    cache_key: str,
) -> MethodRunResult:
    impact = _impact_by_sector(i_outputs)
    risk_multiplier = _macro_risk_multiplier(impact, data)
    overlay = _macro_risk_overlay(context, data, risk_multiplier)
    adjusted, constraints = _adjusted_weights(context, data, overlay)
    diagnostics = {
        "risk_multiplier": risk_multiplier,
        "risky_assets": TRACK_A_RISKY_ASSETS,
        "defensive_assets": TRACK_A_DEFENSIVE_ASSETS,
        "bounded": 0.70 <= risk_multiplier <= 1.05,
        "directional_overtrade_guard": True,
        "final_weight_constraints": constraints,
    }
    return _result(
        spec,
        AvailabilityStatus.AVAILABLE,
        context,
        cache_key,
        data,
        sensitivity_rows=[{"method_code": spec.code, "asset": asset, "risk_multiplier": risk_multiplier} for asset in TRACK_A_RISKY_ASSETS],
        sensitivity_matrix={},
        overlay_by_asset=overlay,
        adjusted_weights=adjusted,
        gate_diagnostics=diagnostics,
        extra_outputs={"overlay_backend": "volatility_scaled_macro_risk_gate"},
    )


def _run_s4(
    spec: MethodSpec,
    context: MethodRunContext,
    data: dict[str, Any],
    i_outputs: dict[str, Any],
    cache_key: str,
) -> MethodRunResult:
    regression_rows = _regression_rows(data)
    if not regression_rows:
        fallback = _run_s1(spec, context, data, i_outputs, cache_key)
        outputs = dict(fallback.outputs)
        outputs["overlay_backend"] = "sparse_regression_fallback_to_s1"
        outputs["warnings"] = tuple(sorted(set(outputs.get("warnings", ())) | {"missing_regression_rows"}))
        return MethodRunResult(
            method_code=spec.code,
            kind="S",
            status=AvailabilityStatus.AVAILABLE,
            fallback_code=None,
            transformer_used=spec.transformer_used,
            network_attempted=False,
            outputs=outputs,
            diagnostics={**fallback.diagnostics, "cache_key": cache_key, "regression_row_count": 0},
        )
    coefficients = _sparse_regression_coefficients(regression_rows)
    raw_scores = _regression_asset_scores(coefficients, _impact_by_sector(i_outputs), context)
    overlay = _scores_to_bounded_overlay(raw_scores, context, data, max_abs_tilt=_max_tilt(data), demean=context.track == "B")
    adjusted, constraints = _adjusted_weights(context, data, overlay)
    return _result(
        spec,
        AvailabilityStatus.AVAILABLE,
        context,
        cache_key,
        data,
        sensitivity_rows=_coefficient_rows(spec.code, coefficients),
        sensitivity_matrix={"coefficients": coefficients},
        overlay_by_asset=overlay,
        adjusted_weights=adjusted,
        gate_diagnostics={
            "regression_row_count": len(regression_rows),
            "shrinkage": REGRESSION_SHRINKAGE,
            "singularity_handling": "univariate_ridge_pinv_safe",
            "final_weight_constraints": constraints,
        },
        extra_outputs={"overlay_backend": "sparse_event_sensitivity_regression"},
    )


def _run_s5(
    spec: MethodSpec,
    context: MethodRunContext,
    data: dict[str, Any],
    i_outputs: dict[str, Any],
    cache_key: str,
) -> MethodRunResult:
    view_scores = _asset_scores_from_sector_scores(_impact_by_sector(i_outputs), context)
    volatility = _volatility_by_asset(context, data)
    posterior_scores = {
        asset: (score / max(0.05, volatility.get(asset, 0.20))) * BL_VIEW_SHRINKAGE
        for asset, score in view_scores.items()
    }
    overlay = _scores_to_bounded_overlay(posterior_scores, context, data, max_abs_tilt=_max_tilt(data), demean=context.track == "B")
    adjusted, constraints = _adjusted_weights(context, data, overlay)
    return _result(
        spec,
        AvailabilityStatus.AVAILABLE,
        context,
        cache_key,
        data,
        sensitivity_rows=[
            {"method_code": spec.code, "asset": asset, "posterior_score": value}
            for asset, value in sorted(posterior_scores.items())
        ],
        sensitivity_matrix={"black_litterman_proxy_scores": _top_scores(posterior_scores)},
        overlay_by_asset=overlay,
        adjusted_weights=adjusted,
        gate_diagnostics={
            "view_shrinkage": BL_VIEW_SHRINKAGE,
            "singularity_handling": "diagonal_volatility_proxy_no_matrix_inverse",
            "view_count": len(view_scores),
            "final_weight_constraints": constraints,
        },
        extra_outputs={"overlay_backend": "black_litterman_news_view_proxy"},
    )


def _run_s6(
    spec: MethodSpec,
    context: MethodRunContext,
    data: dict[str, Any],
    i_outputs: dict[str, Any],
    cache_key: str,
) -> MethodRunResult:
    report = check_model_availability(spec, context)
    calibration_rows = _sensitivity_calibration_rows(data)
    sensitivity_matrix, provenance = _event_sensitivity_matrix(calibration_rows, _impact_rows(i_outputs), context)
    raw_scores = _attention_weighted_scores(_impact_rows(i_outputs), sensitivity_matrix, context, data)
    overlay = _scores_to_bounded_overlay(raw_scores, context, data, max_abs_tilt=_max_tilt(data), demean=context.track == "B")
    adjusted, constraints = _adjusted_weights(context, data, overlay)
    controls = _attention_controls(raw_scores, data)
    return _result(
        spec,
        report.status,
        context,
        cache_key,
        data,
        sensitivity_rows=[
            {"method_code": spec.code, "asset": asset, "attention_sensitivity_score": score}
            for asset, score in sorted(raw_scores.items())
        ],
        sensitivity_matrix={"event_sensitivity": sensitivity_matrix, "attention_weighted_scores": _top_scores(raw_scores)},
        overlay_by_asset=overlay,
        adjusted_weights=adjusted,
        fallback_code="S1" if report.status != AvailabilityStatus.AVAILABLE else None,
        availability=report.as_dict(),
        gate_diagnostics={
            "event_study_provenance": provenance,
            "random_feature_control": controls["random_feature_control"],
            "shuffled_news_control": controls["shuffled_news_control"],
            "final_weight_constraints": constraints,
        },
        extra_outputs={
            "overlay_backend": "proxy_attention_weighted_sensitivity_pooling"
            if is_proxy_report(report)
            else (
                "attention_weighted_sensitivity_pooling"
                if report.status == AvailabilityStatus.AVAILABLE
                else "fallback_attention_weighted_sensitivity_pooling"
            ),
            "transformer_controls": controls,
        },
    )


def _run_s7(
    spec: MethodSpec,
    context: MethodRunContext,
    data: dict[str, Any],
    i_outputs: dict[str, Any],
    cache_key: str,
) -> MethodRunResult:
    report = check_model_availability(spec, context)
    sector_scores = data.get("transformer_scores") or data.get("sector_scores") or _impact_by_sector(i_outputs)
    asset_scores = _asset_scores_from_sector_scores(_score_dict(sector_scores), context)
    overlay = _scores_to_bounded_overlay(asset_scores, context, data, max_abs_tilt=min(_max_tilt(data), 0.03), demean=context.track == "B")
    adjusted, constraints = _adjusted_weights(context, data, overlay)
    return _result(
        spec,
        report.status,
        context,
        cache_key,
        data,
        sensitivity_rows=[{"method_code": spec.code, "asset": asset, "score_to_tilt": score} for asset, score in sorted(asset_scores.items())],
        sensitivity_matrix={"score_to_tilt_inputs": _top_scores(asset_scores)},
        overlay_by_asset=overlay,
        adjusted_weights=adjusted,
        fallback_code="S1" if report.status != AvailabilityStatus.AVAILABLE else None,
        availability=report.as_dict(),
        gate_diagnostics={
            "ablation_only": True,
            "unconstrained_allocator": False,
            "max_abs_tilt": min(_max_tilt(data), 0.03),
            "final_weight_constraints": constraints,
        },
        extra_outputs={
            "overlay_backend": "proxy_cross_sectional_score_to_tilt"
            if is_proxy_report(report)
            else ("cross_sectional_transformer_score_to_tilt" if report.status == AvailabilityStatus.AVAILABLE else "fallback_score_to_tilt_proxy")
        },
    )


def _run_composite(
    spec: MethodSpec,
    context: MethodRunContext,
    data: dict[str, Any],
    i_outputs: dict[str, Any],
    cache_key: str,
    components: tuple[str, ...],
) -> MethodRunResult:
    from nlpcc.news_overlay.registry import get_method_spec

    del i_outputs
    component_results = [RealNewsSensitivityMethod(get_method_spec(code)).run(context, data) for code in components]
    merged_overlay = _merge_component_overlays(component_results, context, data)
    adjusted, constraints = _adjusted_weights(context, data, merged_overlay)
    status = AvailabilityStatus.AVAILABLE
    for result in component_results:
        if result.status != AvailabilityStatus.AVAILABLE:
            status = result.status
            break
    availability = _composite_availability(spec, context, status, component_results)
    sensitivity_rows = [
        {"method_code": spec.code, "asset": asset, "overlay": value, "trace": {"source": "composite", "components": components}}
        for asset, value in sorted(merged_overlay.items())
    ]
    return _result(
        spec,
        status,
        context,
        cache_key,
        data,
        sensitivity_rows=sensitivity_rows,
        sensitivity_matrix={"components": {result.method_code: result.outputs.get("sensitivity_matrix", {}) for result in component_results}},
        overlay_by_asset=merged_overlay,
        adjusted_weights=adjusted,
        fallback_code=spec.fallback_code if status != AvailabilityStatus.AVAILABLE else None,
        availability=availability,
        gate_diagnostics={"components": components, "final_weight_constraints": constraints},
        extra_outputs={"component_traces": [result.as_dict() for result in component_results], "overlay_backend": "composite"},
    )


def _extract_i_outputs(data: dict[str, Any]) -> dict[str, Any]:
    if "impact_rows" in data or "impact_by_sector" in data:
        return {"impact_rows": data.get("impact_rows") or (), "impact_by_sector": data.get("impact_by_sector") or {}}
    i_result = data.get("i_result")
    if isinstance(i_result, MethodRunResult):
        return dict(i_result.outputs)
    if isinstance(i_result, dict):
        outputs = i_result.get("outputs") if "outputs" in i_result else i_result
        return dict(outputs or {})
    method_results = data.get("method_results")
    if isinstance(method_results, dict):
        for result in method_results.values():
            if isinstance(result, dict) and result.get("kind") == "I":
                return dict(result.get("outputs") or {})
    return {"impact_rows": (), "impact_by_sector": {}}


def _method_cache_key(spec: MethodSpec, context: MethodRunContext, data: dict[str, Any], i_outputs: dict[str, Any]) -> str:
    date = str(data.get("decision_date") or context.decision_date or "unknown")
    payload = json.dumps(
        {
            "i_outputs": i_outputs,
            "base_weights": data.get("base_weights") or {},
            "sensitivity_rows": data.get("sensitivity_rows") or data.get("sensitivity_calibration_rows") or (),
            "rank_ic_rows": data.get("rank_ic_rows") or (),
            "regression_rows": data.get("regression_rows") or data.get("sensitivity_regression_rows") or (),
            "volatility_by_asset": data.get("volatility_by_asset") or {},
            "max_abs_tilt": data.get("max_abs_tilt"),
            "shuffle_news": bool(data.get("shuffle_news") or data.get("shuffled_news")),
            "random_feature_seed": data.get("random_feature_seed"),
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    return build_cache_key(
        method_code=spec.code,
        model_identifier=spec.model_identifier,
        local_path_or_revision=model_ref_for_cache(spec, context),
        preprocessing_version=context.preprocessing_version,
        texts=payload,
        date=date,
        sources="substage_s",
        feature_schema_version=context.feature_schema_version,
    ).digest()


def _cache_path(context: MethodRunContext, method_code: str, cache_key: str) -> Path:
    return Path(context.cache_dir) / "s_methods" / method_code / f"{cache_key}.json"


def _read_cache(context: MethodRunContext, method_code: str, cache_key: str) -> dict[str, Any] | None:
    path = _cache_path(context, method_code, cache_key)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def _write_cache(context: MethodRunContext, method_code: str, cache_key: str, result: MethodRunResult) -> None:
    path = _cache_path(context, method_code, cache_key)
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "method_code": result.method_code,
        "status": result.status.value,
        "fallback_code": result.fallback_code,
        "transformer_used": result.transformer_used,
        "outputs": result.outputs,
        "diagnostics": {**result.diagnostics, "cache_hit": False},
    }
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def _result(
    spec: MethodSpec,
    status: AvailabilityStatus,
    context: MethodRunContext,
    cache_key: str,
    data: dict[str, Any],
    *,
    sensitivity_rows: list[dict[str, Any]],
    sensitivity_matrix: dict[str, Any],
    overlay_by_asset: dict[str, float],
    adjusted_weights: dict[str, float],
    gate_diagnostics: dict[str, Any],
    fallback_code: str | None = None,
    availability: dict[str, Any] | None = None,
    extra_outputs: dict[str, Any] | None = None,
) -> MethodRunResult:
    availability_data = availability or {"method_code": spec.code, "status": status.value, "network_attempted": False}
    asset_status = str(availability_data.get("asset_status") or availability_data.get("status") or status.value)
    proxy_flag = bool(availability_data.get("proxy") or asset_status in {"available_proxy_only", "available_via_shared_encoder"})
    warnings = tuple(sorted(_warnings_from_rows(sensitivity_rows) | set(data.get("warnings", ()) or ())))
    outputs = {
        "sensitivity_rows": sensitivity_rows,
        "sensitivity_matrix": sensitivity_matrix,
        "base_weights": _base_weights(context, data),
        "overlay_by_asset": _top_scores(overlay_by_asset, limit=64),
        "adjusted_weights": _top_scores(adjusted_weights, limit=64),
        "gate_diagnostics": gate_diagnostics,
        "required_schema_fields": (
            "method_code",
            "sensitivity_rows",
            "sensitivity_matrix",
            "overlay_by_asset",
            "adjusted_weights",
            "gate_diagnostics",
            "cache_key",
            "model_status",
            "asset_status",
            "fallback_flag",
            "proxy_flag",
            "warnings",
        ),
        "cache_key": cache_key,
        "model_status": status.value,
        "asset_status": asset_status,
        "proxy_flag": proxy_flag,
        "fallback_flag": bool(fallback_code),
        "warnings": warnings,
    }
    if extra_outputs:
        outputs.update(extra_outputs)
    diagnostics = {
        "cache_key": cache_key,
        "cache_hit": False,
        "availability": availability_data,
        "leakage_checks": {
            "calibration_period": "2024_only_or_precomputed",
            "uses_current_day_market_return": False,
            "uses_hidden_2026": False,
            "network_attempted": False,
            "official_runtime_modified": False,
        },
    }
    return MethodRunResult(
        method_code=spec.code,
        kind="S",
        status=status,
        fallback_code=fallback_code,
        transformer_used=spec.transformer_used,
        network_attempted=False,
        outputs=outputs,
        diagnostics=diagnostics,
    )


def _sensitivity_calibration_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [dict(row) for row in (data.get("sensitivity_rows") or data.get("sensitivity_calibration_rows") or ())]
    _validate_2024_rows(rows, "S1 sensitivity calibration")
    return rows


def _composite_availability(
    spec: MethodSpec,
    context: MethodRunContext,
    status: AvailabilityStatus,
    component_results: list[MethodRunResult],
) -> dict[str, Any]:
    asset_status = composite_asset_status(component_results)
    metadata = context.local_model_metadata.get(spec.code) or context.local_model_metadata.get(spec.model_identifier or "") or {}
    return {
        "method_code": spec.code,
        "status": status.value,
        "asset_status": asset_status,
        "model_identifier": spec.model_identifier,
        "hf_model_id": metadata.get("hf_model_id"),
        "local_path": model_ref_for_cache(spec, context),
        "revision": metadata.get("revision_or_commit") or metadata.get("revision"),
        "fallback_code": spec.fallback_code,
        "network_attempted": False,
        "local_files_only": True,
        "reason": "composite_component_status",
        "device": context.device,
        "proxy": asset_status in {"available_proxy_only", "available_via_shared_encoder"},
        "transformer_execution": bool(spec.transformer_used and asset_status == "available"),
        "component_asset_status": {
            result.method_code: (result.diagnostics.get("availability") or {}).get("asset_status")
            or (result.diagnostics.get("availability") or {}).get("status")
            for result in component_results
        },
    }


def _rank_ic_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [dict(row) for row in (data.get("rank_ic_rows") or ())]
    _validate_2024_rows(rows, "S2 Rank-IC calibration")
    return rows


def _regression_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [dict(row) for row in (data.get("regression_rows") or data.get("sensitivity_regression_rows") or ())]
    _validate_2024_rows(rows, "S4 regression calibration")
    return rows


def _validate_2024_rows(rows: list[dict[str, Any]], label: str) -> None:
    for row in rows:
        row_date = str(row.get("date") or row.get("decision_date") or row.get("trade_date") or "")
        if row_date and not row_date.startswith("2024"):
            raise ValueError(f"{label} requires 2024-only rows, got {row_date}")


def _impact_rows(i_outputs: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [dict(row) for row in (i_outputs.get("impact_rows") or ())]
    if rows:
        return rows
    return [
        {"method_code": "I_aggregate", "sector": sector, "event_type": "none", "impact_score": value, "relevance": 1.0, "confidence": 0.5}
        for sector, value in _score_dict(i_outputs.get("impact_by_sector") or {}).items()
    ]


def _impact_by_sector(i_outputs: dict[str, Any]) -> dict[str, float]:
    direct = _score_dict(i_outputs.get("impact_by_sector") or i_outputs.get("nai_by_sector") or {})
    if direct:
        return direct
    aggregate: dict[str, float] = {}
    for row in _impact_rows(i_outputs):
        sector = str(row.get("sector") or "broad_market")
        aggregate[sector] = aggregate.get(sector, 0.0) + float(row.get("impact_score") or 0.0)
    return _top_scores(aggregate)


def _event_sensitivity_matrix(
    calibration_rows: list[dict[str, Any]],
    impact_rows: list[dict[str, Any]],
    context: MethodRunContext,
) -> tuple[dict[str, dict[str, float]], dict[str, Any]]:
    grouped: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in calibration_rows:
        event_type = str(row.get("event_type") or "none")
        value = _abnormal_return(row)
        if value is None:
            continue
        assets = _row_assets(row, context)
        for asset in assets:
            grouped[(event_type, asset)].append(value)
    if not grouped:
        return _default_sensitivity_matrix(impact_rows, context), {
            "source": "default_shrunk_event_sensitivity_prior",
            "construction_period": "2024_only",
            "row_count": 0,
            "leakage_checked": True,
        }
    matrix: dict[str, dict[str, float]] = {}
    for (event_type, asset), values in grouped.items():
        shrink = len(values) / (len(values) + 3.0)
        matrix.setdefault(event_type, {})[asset] = round(_bounded(_robust_mean(values) * shrink, low=-0.25, high=0.25), 6)
    return matrix, {
        "source": "payload_sensitivity_rows",
        "construction_period": "2024_only",
        "row_count": len(calibration_rows),
        "leakage_checked": True,
    }


def _default_sensitivity_matrix(impact_rows: list[dict[str, Any]], context: MethodRunContext) -> dict[str, dict[str, float]]:
    matrix: dict[str, dict[str, float]] = {}
    rows = impact_rows or [{"event_type": "none", "sector": "broad_market", "impact_score": 0.0}]
    for row in rows:
        event_type = str(row.get("event_type") or "none")
        sector = str(row.get("sector") or "broad_market")
        assets = _assets_for_sector(sector, context)
        for asset in assets:
            matrix.setdefault(event_type, {})[asset] = max(abs(matrix.get(event_type, {}).get(asset, 0.0)), 0.35)
    return matrix


def _overlay_from_sensitivity(
    impact_rows: list[dict[str, Any]],
    sensitivity_matrix: dict[str, dict[str, float]],
    context: MethodRunContext,
    data: dict[str, Any],
) -> dict[str, float]:
    raw: dict[str, float] = {}
    for row in impact_rows:
        event_type = str(row.get("event_type") or "none")
        sector = str(row.get("sector") or "broad_market")
        impact = float(row.get("impact_score") or 0.0)
        event_matrix = sensitivity_matrix.get(event_type) or sensitivity_matrix.get("none") or {}
        candidate_assets = tuple(asset for asset in _assets_for_sector(sector, context) if asset in event_matrix) or tuple(event_matrix)
        for asset in candidate_assets:
            raw[asset] = raw.get(asset, 0.0) + impact * float(event_matrix.get(asset, 0.0))
    return _scores_to_bounded_overlay(raw, context, data, max_abs_tilt=_max_tilt(data), demean=context.track == "B")


def _sparse_regression_coefficients(regression_rows: list[dict[str, Any]]) -> dict[str, dict[str, float]]:
    grouped: dict[tuple[str, str], list[tuple[float, float]]] = defaultdict(list)
    for row in regression_rows:
        target_asset = str(row.get("asset") or row.get("sector") or "broad_market")
        target_assets = (target_asset,) if "." in target_asset else tuple(SECTOR_TO_ASSETS.get(target_asset, (target_asset,)))
        target = row.get("target_return", row.get("future_return", row.get("return")))
        if target is None:
            continue
        features = _score_dict(row.get("features") or row.get("event_scores") or row.get("news_scores") or {})
        for asset in target_assets:
            for feature, value in features.items():
                grouped[(asset, feature)].append((float(value), float(target)))
    coefficients: dict[str, dict[str, float]] = {}
    for (asset, feature), pairs in grouped.items():
        numerator = sum(x * y for x, y in pairs)
        denominator = sum(x * x for x, _ in pairs) + 1.0
        coef = _bounded((numerator / denominator) * REGRESSION_SHRINKAGE, low=-0.25, high=0.25)
        if abs(coef) >= 1e-8:
            coefficients.setdefault(asset, {})[feature] = round(coef, 6)
    return coefficients


def _regression_asset_scores(coefficients: dict[str, dict[str, float]], sector_scores: dict[str, float], context: MethodRunContext) -> dict[str, float]:
    pool = set(_track_assets(context))
    scores: dict[str, float] = {}
    for asset, feature_coefs in coefficients.items():
        if asset not in pool:
            continue
        score = sum(float(sector_scores.get(feature, 0.0)) * coef for feature, coef in feature_coefs.items())
        if abs(score) > 1e-12:
            scores[asset] = score
    return scores


def _attention_weighted_scores(
    impact_rows: list[dict[str, Any]],
    sensitivity_matrix: dict[str, dict[str, float]],
    context: MethodRunContext,
    data: dict[str, Any],
) -> dict[str, float]:
    del data
    scores: dict[str, float] = {}
    for row in impact_rows:
        event_type = str(row.get("event_type") or "none")
        sector = str(row.get("sector") or "broad_market")
        impact = float(row.get("impact_score") or 0.0)
        relevance = float(row.get("relevance") or 1.0)
        confidence = float(row.get("confidence") or 0.5)
        attention = float(row.get("attention_weight") or row.get("sector_attention_weight") or 1.0)
        aspect = abs(float(row.get("aspect_weighted_tone") or row.get("direction") or 1.0))
        event_matrix = sensitivity_matrix.get(event_type) or sensitivity_matrix.get("none") or {}
        assets = tuple(asset for asset in _assets_for_sector(sector, context) if asset in event_matrix) or _assets_for_sector(sector, context)
        for asset in assets:
            sensitivity = float(event_matrix.get(asset, 0.35))
            scores[asset] = scores.get(asset, 0.0) + impact * sensitivity * (0.35 + 0.25 * relevance + 0.25 * confidence + 0.15 * attention) * aspect
    return scores


def _attention_controls(raw_scores: dict[str, float], data: dict[str, Any]) -> dict[str, Any]:
    random_control = {"enabled": data.get("random_feature_seed") is not None, "scores": {}}
    if data.get("random_feature_seed") is not None:
        seed = str(data.get("random_feature_seed"))
        random_control["scores"] = {
            asset: round(value * _hash_unit(f"{seed}:{asset}"), 6)
            for asset, value in sorted(raw_scores.items())
        }
    shuffled = {"enabled": bool(data.get("shuffle_news") or data.get("shuffled_news")), "order_sensitive": False}
    return {"random_feature_control": random_control, "shuffled_news_control": shuffled}


def _rank_ic(news_scores: Any, future_returns: Any) -> float | None:
    scores = _score_dict(news_scores)
    returns = _score_dict(future_returns)
    keys = sorted(set(scores) & set(returns))
    if len(keys) < 2:
        return None
    score_ranks = _ranks([scores[key] for key in keys])
    return_ranks = _ranks([returns[key] for key in keys])
    return _pearson(score_ranks, return_ranks)


def _rank_ic_threshold(rank_ics: list[float]) -> float:
    if not rank_ics:
        return 0.0
    positives = [value for value in rank_ics if value > 0]
    if not positives:
        return 0.0
    return max(0.0, _robust_mean(positives) * 0.5)


def _macro_risk_multiplier(impact: dict[str, float], data: dict[str, Any]) -> float:
    volatility = _score_dict(data.get("volatility_by_asset") or {})
    avg_vol = sum(volatility.values()) / len(volatility) if volatility else 0.20
    macro_positive = (
        impact.get("broad_market", 0.0)
        + 0.6 * impact.get("bank", 0.0)
        + 0.6 * impact.get("brokerage", 0.0)
        + 0.4 * impact.get("consumer", 0.0)
    )
    defensive_pressure = impact.get("gold", 0.0) + impact.get("bond", 0.0)
    risk_pressure = max(0.0, -macro_positive) + max(0.0, defensive_pressure)
    multiplier = 1.0 + 0.25 * macro_positive - 0.35 * risk_pressure - 0.10 * max(0.0, avg_vol - 0.20)
    return round(_bounded(multiplier, low=0.70, high=1.05), 6)


def _macro_risk_overlay(context: MethodRunContext, data: dict[str, Any], multiplier: float) -> dict[str, float]:
    base = _base_weights(context, data)
    raw: dict[str, float] = {}
    for asset in TRACK_A_RISKY_ASSETS:
        raw[asset] = base.get(asset, 0.0) * (multiplier - 1.0)
    risky_delta = sum(raw.values())
    defensive_assets = tuple(asset for asset in TRACK_A_DEFENSIVE_ASSETS if asset in base)
    if defensive_assets:
        for asset in defensive_assets:
            raw[asset] = raw.get(asset, 0.0) - risky_delta / len(defensive_assets)
    return _clip_overlay(raw, _max_tilt(data))


def _sector_scores_to_overlay(
    sector_scores: dict[str, float],
    context: MethodRunContext,
    data: dict[str, Any],
    *,
    max_abs_tilt: float,
    demean: bool,
) -> dict[str, float]:
    return _scores_to_bounded_overlay(_asset_scores_from_sector_scores(sector_scores, context), context, data, max_abs_tilt=max_abs_tilt, demean=demean)


def _asset_scores_from_sector_scores(sector_scores: dict[str, float], context: MethodRunContext) -> dict[str, float]:
    scores: dict[str, float] = {}
    pool = set(_track_assets(context))
    for sector, score in sector_scores.items():
        assets = [asset for asset in _assets_for_sector(sector, context) if asset in pool]
        if not assets:
            continue
        for asset in assets:
            scores[asset] = scores.get(asset, 0.0) + float(score) / len(assets)
    return scores


def _scores_to_bounded_overlay(
    scores: dict[str, float],
    context: MethodRunContext,
    data: dict[str, Any],
    *,
    max_abs_tilt: float,
    demean: bool,
) -> dict[str, float]:
    pool = set(_track_assets(context))
    filtered = {asset: float(value) for asset, value in scores.items() if asset in pool and abs(float(value)) > 1e-12}
    if not filtered:
        return {}
    if demean and len(filtered) > 1:
        mean = sum(filtered.values()) / len(filtered)
        filtered = {asset: value - mean for asset, value in filtered.items()}
    peak = max(abs(value) for value in filtered.values()) or 1.0
    scaled = {asset: (value / peak) * max_abs_tilt for asset, value in filtered.items()}
    return _clip_overlay(scaled, _max_tilt(data, default=max_abs_tilt))


def _merge_component_overlays(component_results: list[MethodRunResult], context: MethodRunContext, data: dict[str, Any]) -> dict[str, float]:
    sums: dict[str, float] = {}
    counts: dict[str, int] = {}
    for result in component_results:
        for asset, value in (result.outputs.get("overlay_by_asset") or {}).items():
            sums[asset] = sums.get(asset, 0.0) + float(value)
            counts[asset] = counts.get(asset, 0) + 1
    averaged = {asset: sums[asset] / max(1, counts[asset]) for asset in sums}
    return _clip_overlay(averaged, _max_tilt(data))


def _adjusted_weights(
    context: MethodRunContext,
    data: dict[str, Any],
    overlay: dict[str, float],
) -> tuple[dict[str, float], dict[str, Any]]:
    base = _base_weights(context, data)
    max_weight = float(data.get("max_weight", MAX_WEIGHT))
    invested = 1.0 - float(data.get("cash_reserve", CASH_RESERVE))
    raw = {asset: max(0.0, base.get(asset, 0.0) + overlay.get(asset, 0.0)) for asset in _track_assets(context)}
    capped = {asset: min(max_weight, value) for asset, value in raw.items()}
    total = sum(capped.values())
    if total > invested and total > 0:
        capped = {asset: value * invested / total for asset, value in capped.items()}
    adjusted = {asset: round(value, 6) for asset, value in capped.items() if value > 1e-12}
    turnover = 0.5 * sum(abs(adjusted.get(asset, 0.0) - base.get(asset, 0.0)) for asset in set(adjusted) | set(base))
    issues = []
    if any(value < -1e-10 for value in adjusted.values()):
        issues.append("negative_weight")
    if any(value > max_weight + 1e-8 for value in adjusted.values()):
        issues.append("max_weight")
    if sum(adjusted.values()) > invested + 1e-8:
        issues.append("cash_reserve")
    if turnover > float(data.get("max_turnover", MAX_TURNOVER)) + 1e-8:
        issues.append("turnover")
    return adjusted, {
        "sum_weight": round(sum(adjusted.values()), 6),
        "max_weight": round(max(adjusted.values()) if adjusted else 0.0, 6),
        "turnover_estimate": round(turnover, 6),
        "max_abs_overlay": round(max((abs(value) for value in overlay.values()), default=0.0), 6),
        "issues": tuple(issues),
        "long_only_pass": "negative_weight" not in issues,
        "max_weight_pass": "max_weight" not in issues,
        "turnover_pass": "turnover" not in issues,
    }


def _base_weights(context: MethodRunContext, data: dict[str, Any]) -> dict[str, float]:
    supplied = _score_dict(data.get("base_weights") or {})
    assets = _track_assets(context)
    if supplied:
        filtered = {asset: max(0.0, float(supplied.get(asset, 0.0))) for asset in assets}
    else:
        filtered = {asset: 1.0 for asset in assets}
    invested = 1.0 - float(data.get("cash_reserve", CASH_RESERVE))
    total = sum(filtered.values()) or 1.0
    return {asset: round(value * invested / total, 6) for asset, value in filtered.items() if value > 0}


def _track_assets(context: MethodRunContext) -> tuple[str, ...]:
    return MACRO_FUND_POOL if context.track == "A" else SECTOR_FUND_POOL


def _assets_for_sector(sector: str, context: MethodRunContext) -> tuple[str, ...]:
    pool = set(_track_assets(context))
    mapped = tuple(asset for asset in SECTOR_TO_ASSETS.get(sector, ()) if asset in pool)
    if mapped:
        return mapped
    if sector in pool:
        return (sector,)
    if context.track == "A":
        return tuple(asset for asset in SECTOR_TO_ASSETS["broad_market"] if asset in pool)
    return ()


def _row_assets(row: dict[str, Any], context: MethodRunContext) -> tuple[str, ...]:
    asset = row.get("asset") or row.get("asset_code")
    if asset:
        asset_text = str(asset)
        return (asset_text,) if asset_text in set(_track_assets(context)) else ()
    sector = str(row.get("sector") or row.get("asset_group") or "broad_market")
    return _assets_for_sector(sector, context)


def _abnormal_return(row: dict[str, Any]) -> float | None:
    for key in ("abnormal_return", "car", "caar"):
        if row.get(key) is not None:
            return float(row[key])
    if row.get("return") is not None and row.get("expected_return") is not None:
        return float(row["return"]) - float(row["expected_return"])
    if row.get("future_return") is not None and row.get("expected_return") is not None:
        return float(row["future_return"]) - float(row["expected_return"])
    return None


def _volatility_by_asset(context: MethodRunContext, data: dict[str, Any]) -> dict[str, float]:
    supplied = _score_dict(data.get("volatility_by_asset") or {})
    return {asset: max(0.01, float(supplied.get(asset, 0.20))) for asset in _track_assets(context)}


def _max_tilt(data: dict[str, Any], default: float = MAX_ABS_TILT) -> float:
    return min(MAX_ABS_TILT, max(0.0, float(data.get("max_abs_tilt", default))))


def _clip_overlay(overlay: dict[str, float], max_abs_tilt: float) -> dict[str, float]:
    return {
        asset: round(_bounded(value, low=-max_abs_tilt, high=max_abs_tilt), 6)
        for asset, value in sorted(overlay.items())
        if abs(value) > 1e-12
    }


def _matrix_rows(method_code: str, matrix: dict[str, dict[str, float]], provenance: dict[str, Any]) -> list[dict[str, Any]]:
    return [
        {
            "method_code": method_code,
            "event_type": event_type,
            "asset": asset,
            "sensitivity": value,
            "trace": {"source": provenance["source"], "construction_period": provenance["construction_period"]},
        }
        for event_type, row in sorted(matrix.items())
        for asset, value in sorted(row.items())
    ]


def _coefficient_rows(method_code: str, coefficients: dict[str, dict[str, float]]) -> list[dict[str, Any]]:
    return [
        {"method_code": method_code, "asset": asset, "feature": feature, "coefficient": coefficient}
        for asset, row in sorted(coefficients.items())
        for feature, coefficient in sorted(row.items())
    ]


def _score_dispersion(scores: dict[str, float]) -> float:
    if len(scores) < 2:
        return 0.0
    values = list(scores.values())
    return round((max(values) - min(values)) / (sum(abs(value) for value in values) + 1e-12), 6)


def _ranks(values: list[float]) -> list[float]:
    ordered = sorted((value, index) for index, value in enumerate(values))
    ranks = [0.0] * len(values)
    index = 0
    while index < len(ordered):
        end = index + 1
        while end < len(ordered) and ordered[end][0] == ordered[index][0]:
            end += 1
        rank = (index + end - 1) / 2.0 + 1.0
        for _, original_index in ordered[index:end]:
            ranks[original_index] = rank
        index = end
    return ranks


def _pearson(first: list[float], second: list[float]) -> float:
    if len(first) != len(second) or len(first) < 2:
        return 0.0
    mean_first = sum(first) / len(first)
    mean_second = sum(second) / len(second)
    numerator = sum((a - mean_first) * (b - mean_second) for a, b in zip(first, second))
    denom_first = math.sqrt(sum((a - mean_first) ** 2 for a in first))
    denom_second = math.sqrt(sum((b - mean_second) ** 2 for b in second))
    denominator = denom_first * denom_second
    if denominator <= 1e-12:
        return 0.0
    return round(numerator / denominator, 6)


def _robust_mean(values: list[float]) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(float(value) for value in values)
    trim = 1 if len(sorted_values) >= 5 else 0
    trimmed = sorted_values[trim : len(sorted_values) - trim] if trim else sorted_values
    return sum(trimmed) / len(trimmed)


def _score_dict(value: Any) -> dict[str, float]:
    if not isinstance(value, dict):
        return {}
    return {str(key): float(score) for key, score in value.items() if score is not None}


def _top_scores(scores: dict[str, float], limit: int = 32) -> dict[str, float]:
    return {
        key: round(float(value), 6)
        for key, value in sorted(scores.items(), key=lambda item: (-abs(item[1]), item[0]))[:limit]
        if abs(float(value)) > 1e-12
    }


def _bounded(value: float, *, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def _hash_unit(text: str) -> float:
    digest = sha256(text.encode("utf-8")).digest()
    return (int.from_bytes(digest[:4], "little") / 2**32) * 2.0 - 1.0


def _warnings_from_rows(rows: list[dict[str, Any]]) -> set[str]:
    warnings: set[str] = set()
    for row in rows:
        for warning in row.get("warnings", ()) or ():
            warnings.add(str(warning))
        trace = row.get("trace") or {}
        if isinstance(trace, dict):
            for warning in trace.get("warnings", ()) or ():
                warnings.add(str(warning))
    return warnings
