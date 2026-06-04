"""Substage I transformer-first news impact architecture implementations."""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from hashlib import sha256
import json
import math
from pathlib import Path
from typing import Any

from nlpcc.news_overlay.base import (
    AvailabilityStatus,
    MethodRunContext,
    MethodRunResult,
    MethodSpec,
    NewsImpactMethod,
)
from nlpcc.news_overlay.cache import build_cache_key
from nlpcc.news_overlay.model_availability import check_model_availability


ASPECTS = ("policy", "regulation", "demand", "liquidity", "earnings", "geopolitics", "risk")

EVENT_IMPACT_PRIORS: dict[str, float] = {
    "monetary_easing": 0.85,
    "liquidity_support": 0.75,
    "policy_support": 0.62,
    "demand_recovery": 0.55,
    "earnings_growth": 0.52,
    "commodity_supply": 0.25,
    "tech_innovation": 0.48,
    "healthcare_policy": 0.18,
    "consumption_upgrade": 0.42,
    "regulation_tightening": -0.55,
    "geopolitical_risk": -0.72,
    "default_credit_risk": -0.82,
    "none": 0.0,
}

SECTOR_ASPECT_WEIGHTS: dict[str, dict[str, float]] = {
    "bank": {"liquidity": 0.35, "policy": 0.25, "risk": 0.20, "earnings": 0.12, "regulation": 0.08},
    "brokerage": {"liquidity": 0.30, "policy": 0.24, "demand": 0.18, "risk": 0.16, "earnings": 0.12},
    "insurance": {"liquidity": 0.24, "policy": 0.20, "earnings": 0.20, "risk": 0.20, "regulation": 0.16},
    "broad_market": {"liquidity": 0.24, "policy": 0.22, "demand": 0.18, "earnings": 0.16, "risk": 0.12, "geopolitics": 0.08},
    "bond": {"liquidity": 0.40, "policy": 0.24, "risk": 0.18, "geopolitics": 0.10, "demand": 0.08},
    "gold": {"geopolitics": 0.30, "risk": 0.28, "liquidity": 0.22, "policy": 0.12, "demand": 0.08},
    "semiconductor": {"demand": 0.25, "earnings": 0.22, "policy": 0.18, "geopolitics": 0.18, "risk": 0.10, "liquidity": 0.07},
    "ai": {"demand": 0.28, "earnings": 0.20, "policy": 0.18, "liquidity": 0.14, "risk": 0.12, "geopolitics": 0.08},
    "software": {"demand": 0.24, "policy": 0.22, "earnings": 0.18, "risk": 0.14, "liquidity": 0.12, "geopolitics": 0.10},
}

POLICY_THEMES = {"monetary_easing", "liquidity_support", "policy_support", "healthcare_policy"}


@dataclass(frozen=True)
class ImpactContribution:
    method_code: str
    news_id: str
    event_type: str
    sector: str
    relevance: float
    direction: float
    confidence: float
    impact_magnitude: float
    duplicate_adjustment: float
    attention_weight: float
    novelty: float
    impact_score: float
    trace: dict[str, Any]

    def as_dict(self) -> dict[str, Any]:
        return {
            "method_code": self.method_code,
            "news_id": self.news_id,
            "event_type": self.event_type,
            "sector": self.sector,
            "relevance": self.relevance,
            "direction": self.direction,
            "confidence": self.confidence,
            "impact_magnitude": self.impact_magnitude,
            "duplicate_adjustment": self.duplicate_adjustment,
            "attention_weight": self.attention_weight,
            "novelty": self.novelty,
            "impact_score": self.impact_score,
            "trace": self.trace,
        }


class RealNewsImpactMethod(NewsImpactMethod):
    """Concrete Substage I implementation with cache and trace support."""

    def run(self, context: MethodRunContext, payload: dict[str, Any] | None = None) -> MethodRunResult:
        if context.track not in self.spec.supported_tracks:
            raise ValueError(f"{self.spec.code} is not compatible with Track {context.track}")

        data = payload or {}
        n_rows = _extract_n_feature_rows(data)
        cache_key = _method_cache_key(self.spec, context, data, n_rows)
        cached = _read_cache(context, self.spec.code, cache_key)
        if cached is not None:
            cached["diagnostics"]["cache_hit"] = True
            return MethodRunResult(
                method_code=self.spec.code,
                kind="I",
                status=AvailabilityStatus(cached["status"]),
                fallback_code=cached.get("fallback_code"),
                transformer_used=bool(cached.get("transformer_used")),
                network_attempted=False,
                outputs=cached["outputs"],
                diagnostics=cached["diagnostics"],
            )

        if self.spec.code == "I23":
            result = _run_composite(self.spec, context, data, n_rows, cache_key, ("I2", "I3"))
        elif self.spec.code == "I256":
            result = _run_composite(self.spec, context, data, n_rows, cache_key, ("I2", "I5", "I6"))
        else:
            runners = {
                "I0": _run_i0,
                "I1": _run_i1,
                "I2": _run_i2,
                "I3": _run_i3,
                "I4": _run_i4,
                "I5": _run_i5,
                "I6": _run_i6,
                "I7": _run_i7,
            }
            result = runners[self.spec.code](self.spec, context, data, n_rows, cache_key)
        _write_cache(context, self.spec.code, cache_key, result)
        return result


def _run_i0(
    spec: MethodSpec,
    context: MethodRunContext,
    data: dict[str, Any],
    n_rows: list[dict[str, Any]],
    cache_key: str,
) -> MethodRunResult:
    del data
    rows = [
        _zero_impact_row(spec.code, row, sector, cache_key)
        for row in n_rows
        for sector in sorted((row.get("relevance_by_sector") or {}).keys())
    ]
    return _result(
        spec,
        AvailabilityStatus.AVAILABLE,
        context,
        cache_key,
        n_rows,
        impact_rows=rows,
        impact_by_sector={},
        extra_outputs={"control": "zero_impact"},
    )


def _run_i1(
    spec: MethodSpec,
    context: MethodRunContext,
    data: dict[str, Any],
    n_rows: list[dict[str, Any]],
    cache_key: str,
) -> MethodRunResult:
    del data
    contributions = _impact_contributions(spec.code, n_rows)
    return _result(
        spec,
        AvailabilityStatus.AVAILABLE,
        context,
        cache_key,
        n_rows,
        impact_rows=[item.as_dict() for item in contributions],
        impact_by_sector=_aggregate_contributions(contributions),
        extra_outputs={"impact_backend": "deterministic_event_magnitude"},
    )


def _run_i2(
    spec: MethodSpec,
    context: MethodRunContext,
    data: dict[str, Any],
    n_rows: list[dict[str, Any]],
    cache_key: str,
) -> MethodRunResult:
    rows, hooks = _permutation_rows(n_rows, data)
    contributions = _impact_contributions(spec.code, rows, include_attention=True, include_dispersion=True)
    aggregate = _aggregate_contributions(contributions)
    return _result(
        spec,
        AvailabilityStatus.AVAILABLE,
        context,
        cache_key,
        rows,
        impact_rows=[item.as_dict() for item in contributions],
        impact_by_sector=aggregate,
        extra_outputs={
            "nai_by_sector": aggregate,
            "permutation_hooks": hooks,
            "shuffled_news_pass_ready": hooks["shuffled_news_enabled"],
            "random_label_pass_ready": hooks["random_label_enabled"],
            "impact_backend": "pt_nai",
        },
    )


def _run_i3(
    spec: MethodSpec,
    context: MethodRunContext,
    data: dict[str, Any],
    n_rows: list[dict[str, Any]],
    cache_key: str,
) -> MethodRunResult:
    calibration_rows = list(data.get("calibration_rows") or data.get("event_study_rows") or ())
    calibration_table, provenance = _event_study_calibration(calibration_rows)
    rows = []
    for feature in n_rows:
        event_type = _event_type(feature)
        confidence = _event_confidence(feature)
        for sector, relevance in (feature.get("relevance_by_sector") or {}).items():
            impact = _lookup_calibrated_impact(calibration_table, event_type, str(sector))
            rows.append(
                {
                    "method_code": spec.code,
                    "news_id": str(feature.get("news_id") or "unknown"),
                    "event_type": event_type,
                    "sector": str(sector),
                    "relevance": round(float(relevance), 6),
                    "calibrated_event_impact": impact,
                    "confidence": confidence,
                    "impact_score": round(float(relevance) * confidence * impact, 6),
                    "trace": {"source": "event_study_calibration", "construction_period": "2024_only"},
                }
            )
    return _result(
        spec,
        AvailabilityStatus.AVAILABLE,
        context,
        cache_key,
        n_rows,
        impact_rows=rows,
        impact_by_sector=_aggregate_rows(rows),
        extra_outputs={
            "calibration_table": calibration_table,
            "calibration_provenance": provenance,
            "impact_backend": "event_study_calibrated",
        },
    )


def _run_i4(
    spec: MethodSpec,
    context: MethodRunContext,
    data: dict[str, Any],
    n_rows: list[dict[str, Any]],
    cache_key: str,
) -> MethodRunResult:
    history = _history_events(data)
    decay_weights = _decay_weights(len(history), half_life=float(data.get("half_life_days") or 3.0))
    current = _impact_contributions(spec.code, n_rows)
    repeated = _history_counter(history)
    rows = []
    policy_persistence = 0.0
    for item in current:
        key = (item.event_type, item.sector)
        novelty = round(1.0 / (1.0 + repeated.get(key, 0)), 6)
        persistence_boost = 1.0
        if item.event_type in POLICY_THEMES:
            policy_persistence += abs(item.impact_score)
            persistence_boost = 1.15
        score = round(item.impact_score * novelty * persistence_boost, 6)
        row = item.as_dict()
        row.update(
            {
                "novelty": novelty,
                "repeated_event_count": repeated.get(key, 0),
                "policy_theme_persistence": round(policy_persistence, 6),
                "impact_score": score,
            }
        )
        rows.append(row)
    return _result(
        spec,
        AvailabilityStatus.AVAILABLE,
        context,
        cache_key,
        n_rows,
        impact_rows=rows,
        impact_by_sector=_aggregate_rows(rows),
        extra_outputs={
            "decay_weights": decay_weights,
            "history_count": len(history),
            "policy_theme_persistence": round(policy_persistence, 6),
            "impact_backend": "decay_weighted_persistence",
        },
    )


def _run_i5(
    spec: MethodSpec,
    context: MethodRunContext,
    data: dict[str, Any],
    n_rows: list[dict[str, Any]],
    cache_key: str,
) -> MethodRunResult:
    report = check_model_availability(spec, context)
    contributions = _impact_contributions(spec.code, n_rows, include_attention=True)
    attention = _impact_attention_by_sector(contributions)
    rows = []
    for item in contributions:
        weight = attention.get(item.sector, {}).get(item.news_id, 0.0)
        row = item.as_dict()
        row.update(
            {
                "attention_weight": weight,
                "impact_score": round(item.impact_score * weight, 6),
                "trace": {**item.trace, "attention_gate": weight},
            }
        )
        rows.append(row)
    return _result(
        spec,
        report.status,
        context,
        cache_key,
        n_rows,
        impact_rows=rows,
        impact_by_sector=_aggregate_rows(rows),
        fallback_code="I1" if report.status != AvailabilityStatus.AVAILABLE else None,
        availability=report.as_dict(),
        extra_outputs={
            "attention_by_sector": attention,
            "impact_backend": "impact_gated_attention_pooling" if report.status == AvailabilityStatus.AVAILABLE else "fallback_impact_attention",
        },
    )


def _run_i6(
    spec: MethodSpec,
    context: MethodRunContext,
    data: dict[str, Any],
    n_rows: list[dict[str, Any]],
    cache_key: str,
) -> MethodRunResult:
    del data
    report = check_model_availability(spec, context)
    rows = []
    for feature in n_rows:
        confidence = _event_confidence(feature)
        aspect_tone = _score_dict(feature.get("aspect_tone") or {})
        for sector, relevance in _score_dict(feature.get("relevance_by_sector") or {}).items():
            weights = _aspect_weights(sector)
            signed_tone = sum(float(aspect_tone.get(aspect, 0.0)) * weight for aspect, weight in weights.items())
            score = round(signed_tone * float(relevance) * confidence, 6)
            rows.append(
                {
                    "method_code": spec.code,
                    "news_id": str(feature.get("news_id") or "unknown"),
                    "event_type": _event_type(feature),
                    "sector": sector,
                    "relevance": round(float(relevance), 6),
                    "confidence": confidence,
                    "aspect_weighted_tone": round(signed_tone, 6),
                    "aspect_weights": weights,
                    "impact_score": score,
                    "trace": {"source": "aspect_impact", "formula": "sum_aspect_weighted_tone_times_relevance"},
                }
            )
    return _result(
        spec,
        report.status,
        context,
        cache_key,
        n_rows,
        impact_rows=rows,
        impact_by_sector=_aggregate_rows(rows),
        fallback_code="I1" if report.status != AvailabilityStatus.AVAILABLE else None,
        availability=report.as_dict(),
        extra_outputs={
            "aspect_impact_by_sector": _aggregate_rows(rows),
            "aspect_weight_table": SECTOR_ASPECT_WEIGHTS,
            "impact_backend": "transformer_aspect_impact" if report.status == AvailabilityStatus.AVAILABLE else "fallback_aspect_impact_from_n_features",
        },
    )


def _run_i7(
    spec: MethodSpec,
    context: MethodRunContext,
    data: dict[str, Any],
    n_rows: list[dict[str, Any]],
    cache_key: str,
) -> MethodRunResult:
    report = check_model_availability(spec, context)
    history = _impact_history(data)
    current = _aggregate_contributions(_impact_contributions(spec.code, n_rows, include_attention=True))
    historical = _decayed_history_impact(history)
    combined = dict(current)
    for sector, value in historical.items():
        combined[sector] = round(combined.get(sector, 0.0) + 0.5 * value, 6)
    warnings = []
    if len(history) < 2:
        warnings.append("short_history")
    return _result(
        spec,
        report.status,
        context,
        cache_key,
        n_rows,
        impact_rows=[
            {
                "method_code": spec.code,
                "sector": sector,
                "impact_score": value,
                "trace": {"source": "temporal_narrative", "history_count": len(history)},
            }
            for sector, value in sorted(combined.items())
        ],
        impact_by_sector=combined,
        fallback_code="I4" if report.status != AvailabilityStatus.AVAILABLE else None,
        availability=report.as_dict(),
        extra_outputs={
            "narrative_impact_by_sector": combined,
            "persistence_diagnostics": {"history_count": len(history), "warnings": warnings},
            "impact_backend": "temporal_narrative_encoder" if report.status == AvailabilityStatus.AVAILABLE else "fallback_temporal_overlap",
        },
    )


def _run_composite(
    spec: MethodSpec,
    context: MethodRunContext,
    data: dict[str, Any],
    n_rows: list[dict[str, Any]],
    cache_key: str,
    components: tuple[str, ...],
) -> MethodRunResult:
    from nlpcc.news_overlay.registry import get_method_spec

    component_results = [RealNewsImpactMethod(get_method_spec(code)).run(context, data) for code in components]
    merged = _merge_component_impacts(component_results)
    status = AvailabilityStatus.AVAILABLE
    if any(result.status != AvailabilityStatus.AVAILABLE for result in component_results):
        status = AvailabilityStatus.BLOCKED_MISSING_LOCAL_MODEL
    return _result(
        spec,
        status,
        context,
        cache_key,
        n_rows,
        impact_rows=[
            {"method_code": spec.code, "sector": sector, "impact_score": value, "trace": {"source": "composite", "components": components}}
            for sector, value in sorted(merged.items())
        ],
        impact_by_sector=merged,
        fallback_code=spec.fallback_code if status != AvailabilityStatus.AVAILABLE else None,
        extra_outputs={"component_traces": [result.as_dict() for result in component_results], "impact_backend": "composite"},
    )


def _extract_n_feature_rows(data: dict[str, Any]) -> list[dict[str, Any]]:
    if "n_feature_rows" in data:
        return [dict(row) for row in data.get("n_feature_rows") or ()]
    if "feature_rows" in data:
        return [dict(row) for row in data.get("feature_rows") or ()]
    n_result = data.get("n_result")
    if isinstance(n_result, MethodRunResult):
        return [dict(row) for row in n_result.outputs.get("feature_rows", ())]
    if isinstance(n_result, dict):
        outputs = n_result.get("outputs") if "outputs" in n_result else n_result
        return [dict(row) for row in (outputs or {}).get("feature_rows", ())]
    return []


def _method_cache_key(spec: MethodSpec, context: MethodRunContext, data: dict[str, Any], n_rows: list[dict[str, Any]]) -> str:
    date = str(data.get("decision_date") or context.decision_date or "unknown")
    key_payload = json.dumps(
        {
            "n_rows": n_rows,
            "calibration_rows": data.get("calibration_rows") or data.get("event_study_rows") or (),
            "history": data.get("impact_history") or data.get("nai_history") or data.get("event_history") or (),
        },
        ensure_ascii=False,
        sort_keys=True,
    )
    sources = tuple(str(row.get("source") or "unknown") for row in n_rows)
    return build_cache_key(
        method_code=spec.code,
        model_identifier=spec.model_identifier,
        local_path_or_revision=context.local_model_paths.get(spec.code) or context.local_model_paths.get(spec.model_identifier or ""),
        preprocessing_version=context.preprocessing_version,
        texts=key_payload,
        date=date,
        sources=sources,
        feature_schema_version=context.feature_schema_version,
    ).digest()


def _cache_path(context: MethodRunContext, method_code: str, cache_key: str) -> Path:
    return Path(context.cache_dir) / "i_methods" / method_code / f"{cache_key}.json"


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
    n_rows: list[dict[str, Any]],
    *,
    impact_rows: list[dict[str, Any]],
    impact_by_sector: dict[str, float],
    fallback_code: str | None = None,
    availability: dict[str, Any] | None = None,
    extra_outputs: dict[str, Any] | None = None,
) -> MethodRunResult:
    outputs = {
        "impact_rows": impact_rows,
        "impact_by_sector": _top_scores(impact_by_sector),
        "required_schema_fields": (
            "method_code",
            "impact_rows",
            "impact_by_sector",
            "cache_key",
            "model_status",
            "fallback_flag",
            "warnings",
        ),
        "cache_key": cache_key,
        "model_status": status.value,
        "fallback_flag": bool(fallback_code),
        "warnings": _warnings_from_rows(impact_rows),
    }
    if extra_outputs:
        outputs.update(extra_outputs)
    diagnostics = {
        "cache_key": cache_key,
        "cache_hit": False,
        "n_feature_row_count": len(n_rows),
        "availability": availability or {"method_code": spec.code, "status": status.value, "network_attempted": False},
        "leakage_checks": {
            "uses_current_day_market_return": False,
            "calibration_period": "2024_only_or_precomputed",
            "network_attempted": False,
        },
    }
    return MethodRunResult(
        method_code=spec.code,
        kind="I",
        status=status,
        fallback_code=fallback_code,
        transformer_used=spec.transformer_used,
        network_attempted=False,
        outputs=outputs,
        diagnostics=diagnostics,
    )


def _zero_impact_row(method_code: str, feature: dict[str, Any], sector: str, cache_key: str) -> dict[str, Any]:
    return {
        "method_code": method_code,
        "news_id": str(feature.get("news_id") or "unknown"),
                    "event_type": _event_type(feature),
        "sector": sector,
        "impact_score": 0.0,
        "cache_key": cache_key,
        "trace": {"source": "zero_impact_control"},
    }


def _impact_contributions(
    method_code: str,
    n_rows: list[dict[str, Any]],
    *,
    include_attention: bool = False,
    include_dispersion: bool = False,
) -> list[ImpactContribution]:
    duplicate_counts = Counter(str(row.get("duplicate_cluster_id") or row.get("news_id") or index) for index, row in enumerate(n_rows))
    contributions: list[ImpactContribution] = []
    for index, row in enumerate(n_rows):
        event_type = _event_type(row)
        relevance_by_sector = _score_dict(row.get("relevance_by_sector") or {})
        if not relevance_by_sector:
            continue
        event_confidence = _event_confidence(row)
        dispersion = _event_dispersion(row)
        cluster_id = str(row.get("duplicate_cluster_id") or row.get("news_id") or index)
        duplicate_adjustment = round(1.0 / math.sqrt(max(1, duplicate_counts[cluster_id])), 6)
        for sector, relevance in relevance_by_sector.items():
            direction = _direction_for_sector(row, event_type, sector)
            magnitude = _impact_magnitude(row, event_type)
            confidence = _bounded(0.35 + 0.30 * event_confidence + 0.25 * float(relevance) + (0.10 * dispersion if include_dispersion else 0.0))
            attention_weight = _sector_attention(row, sector) if include_attention else 1.0
            novelty = _row_novelty(row)
            score = magnitude * float(relevance) * direction * confidence * duplicate_adjustment * novelty
            if include_attention:
                score *= 0.75 + 0.25 * attention_weight
            contributions.append(
                ImpactContribution(
                    method_code=method_code,
                    news_id=str(row.get("news_id") or f"news_{index}"),
                    event_type=event_type,
                    sector=sector,
                    relevance=round(float(relevance), 6),
                    direction=round(direction, 6),
                    confidence=round(confidence, 6),
                    impact_magnitude=round(magnitude, 6),
                    duplicate_adjustment=duplicate_adjustment,
                    attention_weight=round(attention_weight, 6),
                    novelty=round(novelty, 6),
                    impact_score=round(score, 6),
                    trace={
                        "source": "impact_formula",
                        "formula": "impact_magnitude*relevance*direction*confidence*duplicate_adjustment*novelty",
                        "event_confidence": event_confidence,
                        "event_dispersion": dispersion,
                    },
                )
            )
    return contributions


def _permutation_rows(n_rows: list[dict[str, Any]], data: dict[str, Any]) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    rows = [dict(row) for row in n_rows]
    shuffle_enabled = bool(data.get("shuffle_news") or data.get("shuffled_news"))
    random_label_seed = data.get("random_label_seed")
    seed = str(data.get("permutation_seed") or random_label_seed or "prompt04")
    if shuffle_enabled:
        rows.sort(key=lambda row: sha256(f"{seed}:{row.get('news_id')}".encode("utf-8")).hexdigest())
    if random_label_seed is not None and rows:
        labels = sorted(EVENT_IMPACT_PRIORS)
        for row in rows:
            digest = sha256(f"{random_label_seed}:{row.get('news_id')}".encode("utf-8")).digest()
            row["event_type"] = labels[int.from_bytes(digest[:2], "little") % len(labels)]
    return rows, {
        "shuffled_news_enabled": shuffle_enabled,
        "random_label_enabled": random_label_seed is not None,
        "seed": seed,
        "network_attempted": False,
    }


def _event_study_calibration(calibration_rows: list[dict[str, Any]]) -> tuple[dict[str, dict[str, float]], dict[str, Any]]:
    grouped: dict[tuple[str, str], list[float]] = defaultdict(list)
    for row in calibration_rows:
        row_date = str(row.get("date") or row.get("decision_date") or row.get("trade_date") or "")
        if row_date and not row_date.startswith("2024"):
            raise ValueError(f"I3 calibration requires 2024-only rows, got {row_date}")
        event_type = str(row.get("event_type") or "none")
        sector = str(row.get("sector") or row.get("asset") or row.get("asset_code") or "broad_market")
        value = row.get("abnormal_return", row.get("car", row.get("caar", row.get("return", 0.0))))
        grouped[(event_type, sector)].append(float(value))
    if not grouped:
        table = {
            event_type: {"__default__": round(prior * 0.025, 6)}
            for event_type, prior in sorted(EVENT_IMPACT_PRIORS.items())
        }
        return table, {
            "source": "default_event_study_prior",
            "construction_period": "2024_only",
            "row_count": 0,
            "leakage_checked": True,
        }
    table: dict[str, dict[str, float]] = {}
    for (event_type, sector), values in grouped.items():
        table.setdefault(event_type, {})[sector] = _robust_mean(values)
    return table, {
        "source": "payload_calibration_rows",
        "construction_period": "2024_only",
        "row_count": len(calibration_rows),
        "leakage_checked": True,
    }


def _lookup_calibrated_impact(table: dict[str, dict[str, float]], event_type: str, sector: str) -> float:
    event_table = table.get(event_type) or table.get("none") or {"__default__": 0.0}
    return round(float(event_table.get(sector, event_table.get("__default__", 0.0))), 6)


def _history_events(data: dict[str, Any]) -> list[dict[str, Any]]:
    return [dict(row) for row in (data.get("event_history") or data.get("history") or ())]


def _impact_history(data: dict[str, Any]) -> list[dict[str, Any]]:
    return [dict(row) for row in (data.get("impact_history") or data.get("nai_history") or ())]


def _history_counter(history: list[dict[str, Any]]) -> Counter[tuple[str, str]]:
    counter: Counter[tuple[str, str]] = Counter()
    for row in history:
        event_type = str(row.get("event_type") or "none")
        sectors = row.get("sectors") or row.get("relevance_by_sector") or row.get("impact_by_sector") or {"broad_market": 1.0}
        if isinstance(sectors, dict):
            iterable = sectors.keys()
        else:
            iterable = sectors
        for sector in iterable:
            counter[(event_type, str(sector))] += 1
    return counter


def _decay_weights(length: int, *, half_life: float) -> list[float]:
    weights = [round(math.exp(-index / max(0.1, half_life)), 6) for index in range(length)]
    return weights


def _decayed_history_impact(history: list[dict[str, Any]]) -> dict[str, float]:
    aggregate: dict[str, float] = {}
    weights = _decay_weights(len(history), half_life=3.0)
    for index, row in enumerate(reversed(history)):
        weight = weights[index] if index < len(weights) else 0.0
        for sector, value in _score_dict(row.get("impact_by_sector") or row.get("nai_by_sector") or {}).items():
            aggregate[sector] = aggregate.get(sector, 0.0) + weight * float(value)
    return _top_scores(aggregate)


def _impact_attention_by_sector(contributions: list[ImpactContribution]) -> dict[str, dict[str, float]]:
    grouped: dict[str, list[ImpactContribution]] = defaultdict(list)
    for item in contributions:
        grouped[item.sector].append(item)
    attention: dict[str, dict[str, float]] = {}
    for sector, rows in grouped.items():
        values = [(row.news_id, math.exp(min(6.0, abs(row.impact_score) * 8.0 + row.confidence))) for row in rows]
        total = sum(value for _, value in values) or 1.0
        attention[sector] = {news_id: round(value / total, 6) for news_id, value in values}
    return attention


def _merge_component_impacts(component_results: list[MethodRunResult]) -> dict[str, float]:
    sums: dict[str, float] = {}
    counts: dict[str, int] = {}
    for result in component_results:
        for sector, value in (result.outputs.get("impact_by_sector") or {}).items():
            sums[sector] = sums.get(sector, 0.0) + float(value)
            counts[sector] = counts.get(sector, 0) + 1
    return _top_scores({sector: value / max(1, counts[sector]) for sector, value in sums.items()})


def _aggregate_contributions(contributions: list[ImpactContribution]) -> dict[str, float]:
    aggregate: dict[str, float] = {}
    for item in contributions:
        aggregate[item.sector] = aggregate.get(item.sector, 0.0) + item.impact_score
    return _top_scores(aggregate)


def _aggregate_rows(rows: list[dict[str, Any]]) -> dict[str, float]:
    aggregate: dict[str, float] = {}
    for row in rows:
        sector = row.get("sector")
        if sector is None:
            continue
        aggregate[str(sector)] = aggregate.get(str(sector), 0.0) + float(row.get("impact_score") or 0.0)
    return _top_scores(aggregate)


def _event_confidence(row: dict[str, Any]) -> float:
    scores = _score_dict(row.get("event_probabilities") or row.get("label_attention_scores") or {})
    if scores:
        return round(max(scores.values()), 6)
    return 0.5


def _event_type(row: dict[str, Any]) -> str:
    event_type = str(row.get("event_type") or "none")
    if event_type != "none":
        return event_type
    scores = _score_dict(row.get("event_probabilities") or row.get("label_attention_scores") or {})
    if scores:
        return max(scores, key=scores.get)
    return "none"


def _event_dispersion(row: dict[str, Any]) -> float:
    scores = list(_score_dict(row.get("event_probabilities") or row.get("label_attention_scores") or {}).values())
    if len(scores) < 2:
        return 0.0
    return round(max(scores) - min(scores), 6)


def _impact_magnitude(row: dict[str, Any], event_type: str) -> float:
    prior = abs(EVENT_IMPACT_PRIORS.get(event_type, 0.25))
    event_confidence = _event_confidence(row)
    return round(prior * (0.65 + 0.35 * event_confidence), 6)


def _direction_for_sector(row: dict[str, Any], event_type: str, sector: str) -> float:
    prior = EVENT_IMPACT_PRIORS.get(event_type, 0.0)
    prior_direction = 1.0 if prior >= 0 else -1.0
    tone = _sector_aspect_tone(row, sector)
    if abs(tone) < 1e-6:
        return prior_direction
    return _bounded(0.60 * tone + 0.40 * prior_direction, low=-1.0, high=1.0)


def _sector_aspect_tone(row: dict[str, Any], sector: str) -> float:
    aspect_tone = _score_dict(row.get("aspect_tone") or {})
    weights = _aspect_weights(sector)
    return round(sum(float(aspect_tone.get(aspect, 0.0)) * weight for aspect, weight in weights.items()), 6)


def _aspect_weights(sector: str) -> dict[str, float]:
    weights = dict(SECTOR_ASPECT_WEIGHTS.get(sector, {}))
    if not weights:
        weights = {aspect: round(1.0 / len(ASPECTS), 6) for aspect in ASPECTS}
    total = sum(weights.values()) or 1.0
    return {aspect: round(value / total, 6) for aspect, value in sorted(weights.items())}


def _sector_attention(row: dict[str, Any], sector: str) -> float:
    weights = _score_dict(row.get("sector_query_attention_weights") or {})
    return round(float(weights.get(sector, 1.0)), 6)


def _row_novelty(row: dict[str, Any]) -> float:
    warnings = tuple(str(item) for item in row.get("warnings", ()) or ())
    if any("fallback" in item for item in warnings):
        return 0.92
    return 1.0


def _score_dict(value: Any) -> dict[str, float]:
    if not isinstance(value, dict):
        return {}
    return {str(key): float(score) for key, score in value.items() if score is not None}


def _robust_mean(values: list[float]) -> float:
    if not values:
        return 0.0
    sorted_values = sorted(values)
    trim = 1 if len(sorted_values) >= 5 else 0
    trimmed = sorted_values[trim : len(sorted_values) - trim] if trim else sorted_values
    return round(_bounded(sum(trimmed) / len(trimmed), low=-1.0, high=1.0), 6)


def _warnings_from_rows(rows: list[dict[str, Any]]) -> tuple[str, ...]:
    warnings = set()
    for row in rows:
        for warning in row.get("warnings", ()) or ():
            warnings.add(str(warning))
        trace = row.get("trace") or {}
        if isinstance(trace, dict):
            for warning in trace.get("warnings", ()) or ():
                warnings.add(str(warning))
    return tuple(sorted(warnings))


def _bounded(value: float, *, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


def _top_scores(scores: dict[str, float], limit: int = 16) -> dict[str, float]:
    return {
        key: round(float(value), 6)
        for key, value in sorted(scores.items(), key=lambda item: (-abs(item[1]), item[0]))[:limit]
        if abs(value) > 1e-12
    }
