"""Track A top-3 minor enhancement runner.

This runner is intentionally scoped to the Prompt24/25 Track A research
candidates. It does not modify the frozen official runtime and does not run
Track B rows.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any

import numpy as np

from nlpcc.news_overlay.config import NewsOverlayConfig
from nlpcc.news_overlay.grid_evaluator import (
    TRACK_TO_OFFICIAL,
    _aggregate_trace_metrics,
    _base_weights,
    _date_dash,
    _evaluation_status,
    _load_news_by_date,
    _rank_ic_rows_from_returns,
    _sensitivity_rows_from_returns,
    _trace_cache_rows,
    _trace_metrics,
    _volatility_from_history,
    _weights_for_assets,
)
from nlpcc.news_overlay.hf_models import resolve_local_model_context
from nlpcc.news_overlay.pipeline import ScaffoldNewsOverlayPipeline
from nlpcc.news_overlay.prompt22_runner import (
    FALLBACK_PRESERVED,
    HF_CACHE,
    PRIMARY_PRESERVED,
    ParamSet,
    _apply_params,
    _apply_turnover_cap,
    _num,
    _preserved_manifest,
    _round,
)
from nlpcc.news_overlay.prompt23_runner import NvidiaSmiSampler
from nlpcc.news_overlay.registry import validate_track_compatibility
from nlpcc.evaluation.reference_official_semantics import (
    OfficialSemanticsInput,
    load_official_semantics_arrays,
    run_reference_official_semantics,
)


OUT = Path("outputs/reports/news_overlay/top8_minor_enhancement/concurrent/track_a")
REFERENCE = OUT
APPROVED_MODELS = Path("configs/news_overlay/approved_hf_models.yaml")
LOCAL_MODELS = Path("configs/news_overlay/local_models.local.example.yaml")


@dataclass(frozen=True)
class CandidateSpec:
    family: str
    prompt23_run_id: str
    method_stack: str
    n_method: str
    i_method: str
    s_method: str
    params: ParamSet
    architecture: str


@dataclass(frozen=True)
class VariantSpec:
    code: str
    name: str
    hooks: tuple[str, ...]
    notes: str


CANDIDATES: dict[str, CandidateSpec] = {
    "G11A": CandidateSpec(
        family="G11A",
        prompt23_run_id="P23_G11A_s025_i00_c00_v00_capmedium_ddoff",
        method_stack="N13/I6/S13",
        n_method="N13",
        i_method="I6",
        s_method="S13",
        params=ParamSet(0.25, 0.0, 0.0, 0.0, "medium", "off"),
        architecture="FinBERT/aspect-tone hybrid + aspect-impact aggregator + Track A sensitivity/risk overlay",
    ),
    "G12A": CandidateSpec(
        family="G12A",
        prompt23_run_id="P23_G12A_s025_i00_c00_v00_capmedium_ddoff",
        method_stack="N2345/I256/S13",
        n_method="N2345",
        i_method="I256",
        s_method="S13",
        params=ParamSet(0.25, 0.0, 0.0, 0.0, "medium", "off"),
        architecture="Composite BGE/FinBERT transformer stack + composite impact + Track A sensitivity/risk overlay",
    ),
    "G10A": CandidateSpec(
        family="G10A",
        prompt23_run_id="P23_G10A_s050_i25_c00_v00_caplow_ddmild",
        method_stack="N2/I2/S3",
        n_method="N2",
        i_method="I2",
        s_method="S3",
        params=ParamSet(0.50, 0.25, 0.0, 0.0, "low", "mild"),
        architecture="BGE bi-encoder relevance + base impact + macro risk/sensitivity gate",
    ),
}


VARIANTS: dict[str, tuple[VariantSpec, ...]] = {
    "G11A": (
        VariantSpec("V0", "baseline_hooks_off", tuple(), "Prompt23 frozen parameters, no minor hooks."),
        VariantSpec("V1", "H2_confidence_ambiguity_damping", ("H2",), "FinBERT/aspect-tone confidence damping."),
        VariantSpec("V2", "H3_short_decay_smoothing", ("H3",), "Asymmetric short-horizon overlay decay."),
        VariantSpec("V3", "H4_turnover_deadband", ("H4",), "Weak-signal deadband plus lower turnover cap."),
        VariantSpec("V4", "H4_macro_overlay_discipline", ("H4_STRICT",), "Stricter macro overlay discipline for Track A."),
        VariantSpec("V5", "H2_H3_H4_combo", ("H2", "H3", "H4"), "Best-combo candidate from V1-V4 hooks only."),
    ),
    "G12A": (
        VariantSpec("V0", "baseline_hooks_off", tuple(), "Prompt23 frozen parameters, no minor hooks."),
        VariantSpec("V1", "H2_confidence_ambiguity_damping", ("H2",), "Composite confidence damping."),
        VariantSpec("V2", "H3_short_decay_smoothing", ("H3",), "Composite short-horizon smoothing."),
        VariantSpec("V3", "H4_turnover_deadband", ("H4",), "Weak-signal deadband plus turnover cap."),
        VariantSpec("V4", "H6_composite_dominance_control", ("H6",), "Substage dominance cap / consensus shrinkage."),
        VariantSpec("V5", "H6_H2_H3_combo", ("H6", "H2", "H3"), "Best-combo candidate from V1-V4 hooks only."),
    ),
    "G10A": (
        VariantSpec("V0", "baseline_hooks_off", tuple(), "Prompt23 frozen parameters, no minor hooks."),
        VariantSpec("V1", "H2_bge_margin_damping", ("H2",), "BGE relevance/margin confidence damping."),
        VariantSpec("V2", "H3_short_relevance_decay", ("H3",), "Short relevance decay."),
        VariantSpec("V3", "H4_deadband_cap", ("H4",), "Weak-signal deadband plus low cap."),
        VariantSpec("V4", "H4_simple_relevance_hygiene", ("H4_STRICT",), "Stricter low-complexity relevance hygiene."),
        VariantSpec("V5", "H2_H3_H4_combo", ("H2", "H3", "H4"), "Best-combo candidate from V1-V4 hooks only."),
    ),
}


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    OUT.mkdir(parents=True, exist_ok=True)
    if args.stage == "all":
        run_stage0(args)
        run_stage1(args)
        freeze_stage1()
        run_stage2(args)
        write_final_status()
        return 0
    if args.stage == "stage0":
        run_stage0(args)
    elif args.stage == "stage1":
        run_stage1(args)
    elif args.stage == "freeze":
        freeze_stage1()
    elif args.stage == "stage2":
        run_stage2(args)
    elif args.stage == "final":
        write_final_status()
    else:
        raise ValueError(f"Unknown stage: {args.stage}")
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Track A top-3 minor enhancement stages.")
    parser.add_argument("--stage", choices=("stage0", "stage1", "freeze", "stage2", "final", "all"), required=True)
    parser.add_argument("--candidate", choices=tuple(CANDIDATES) + ("all",), default="all")
    parser.add_argument("--device", default="auto")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--cache-run-id", default="track_a_minor")
    parser.add_argument("--no-resume", action="store_true")
    return parser


def run_stage0(args: argparse.Namespace) -> None:
    rows = []
    for family in _selected_families(args.candidate):
        base = run_base_candidate(
            CANDIDATES[family],
            data_root=Path("data/train_2024"),
            period="stage0_2024_smoke",
            max_dates=10,
            device=args.device,
            batch_size=args.batch_size,
            cache_run_id=args.cache_run_id,
        )
        row = evaluate_variant(base, VARIANTS[family][0], stage="stage0", period_label="2024_smoke")
        rows.append(row)
    write_stage0_summary(rows)


def run_stage1(args: argparse.Namespace) -> None:
    existing = [] if args.no_resume else read_csv(REFERENCE / "track_a_stage1_2024_tune_matrix.csv")
    keep = [row for row in existing if row.get("candidate_family") not in set(_selected_families(args.candidate))]
    rows = list(keep)
    for family in _selected_families(args.candidate):
        base = run_base_candidate(
            CANDIDATES[family],
            data_root=Path("data/train_2024"),
            period="stage1_2024_tune",
            max_dates=9999,
            device=args.device,
            batch_size=args.batch_size,
            cache_run_id=args.cache_run_id,
        )
        for variant in VARIANTS[family]:
            rows.append(evaluate_variant(base, variant, stage="stage1", period_label="2024"))
    attach_selection_scores(rows)
    rows.sort(key=lambda row: (str(row.get("candidate_family")), str(row.get("variant_code"))))
    write_csv(REFERENCE / "track_a_stage1_2024_tune_matrix.csv", rows)
    write_stage1_summary(rows)
    write_ablation_evidence(rows)


def freeze_stage1() -> None:
    rows = [row for row in read_csv(REFERENCE / "track_a_stage1_2024_tune_matrix.csv") if row.get("status") == "pass"]
    if not rows:
        raise ValueError("No Stage 1 rows available for freeze.")
    attach_selection_scores(rows)
    frozen = []
    for family in CANDIDATES:
        family_rows = [row for row in rows if row.get("candidate_family") == family]
        if not family_rows:
            continue
        family_rows.sort(key=lambda row: (_num(row.get("selection_score")), _num(row.get("sharpe"))), reverse=True)
        selected = dict(family_rows[0])
        selected["freeze_rank_within_candidate"] = 1
        selected["frozen_before_2025"] = True
        selected["freeze_rule"] = "max 2024 conservative selection_score within candidate; 2025 not read"
        frozen.append(selected)
    write_csv(REFERENCE / "track_a_freeze_decisions.csv", frozen)
    write_freeze_decisions(frozen, rows)


def run_stage2(args: argparse.Namespace) -> None:
    frozen = read_csv(REFERENCE / "track_a_freeze_decisions.csv")
    if not frozen:
        raise ValueError("Run --stage freeze before Stage 2.")
    frozen_by_family = {row["candidate_family"]: row for row in frozen}
    existing = [] if args.no_resume else read_csv(REFERENCE / "track_a_stage2_2025_frozen_results.csv")
    keep = [row for row in existing if row.get("candidate_family") not in set(_selected_families(args.candidate))]
    rows = list(keep)
    for family in _selected_families(args.candidate):
        if family not in frozen_by_family:
            continue
        variant_code = frozen_by_family[family]["variant_code"]
        variant = next(item for item in VARIANTS[family] if item.code == variant_code)
        base = run_base_candidate(
            CANDIDATES[family],
            data_root=Path("data/public_a_2025"),
            period="stage2_2025_frozen",
            max_dates=9999,
            device=args.device,
            batch_size=args.batch_size,
            cache_run_id=args.cache_run_id,
        )
        row = evaluate_variant(base, variant, stage="stage2", period_label="2025")
        row["source_2024_variant_run_id"] = frozen_by_family[family]["run_id"]
        row["frozen_from_2024_selection_score"] = frozen_by_family[family]["selection_score"]
        row["frozen_before_2025"] = True
        rows.append(row)
    rows.sort(key=lambda row: str(row.get("candidate_family")))
    write_csv(REFERENCE / "track_a_stage2_2025_frozen_results.csv", rows)
    write_stage2_summary(rows)
    write_final_status()


def run_base_candidate(
    spec: CandidateSpec,
    *,
    data_root: Path,
    period: str,
    max_dates: int,
    device: str,
    batch_size: int,
    cache_run_id: str,
) -> dict[str, Any]:
    validate_track_compatibility("A", (spec.n_method, spec.i_method, spec.s_method))
    local_model_paths, local_model_metadata, _ = resolve_local_model_context(
        approved_models_path=APPROVED_MODELS,
        local_models_path=LOCAL_MODELS,
        cache_root=HF_CACHE,
        require_local=True,
    )
    dates, assets, open_prices, pct_changes = load_official_semantics_arrays(
        data_root,
        TRACK_TO_OFFICIAL["A"],  # type: ignore[arg-type]
        max_dates=max_dates,
    )
    news_by_date = _load_news_by_date(data_root, dates, top_rank=20)
    base_weights = _base_weights(assets)
    base_array = np.tile(np.asarray([base_weights.get(asset, 0.0) for asset in assets], dtype=float)[None, :], (len(dates), 1))
    raw_target = np.empty((len(dates), len(assets)), dtype=float)
    trace_rows: list[dict[str, Any]] = []
    cache_rows: list[dict[str, Any]] = []
    statuses: list[str] = []
    blocked_methods: set[str] = set()
    network_attempted = False
    runtime_seconds = 0.0
    sampler = NvidiaSmiSampler()
    sampler.start()
    started = perf_counter()
    cache_dir = OUT / "cache" / cache_run_id / period / spec.family
    trace_dir = OUT / "traces" / period / spec.family
    allow_calibration = data_root.name == "train_2024"
    try:
        for date_index, date in enumerate(dates):
            payload = {
                "decision_date": _date_dash(date),
                "cutoff": "15:00",
                "top_rank": 20,
                "news": news_by_date.get(date, []),
                "base_weights": base_weights,
                "rank_ic_rows": _rank_ic_rows_from_returns(assets, pct_changes, dates, date_index) if allow_calibration else [],
                "current_rank_ic": 0.0,
                "sensitivity_rows": _sensitivity_rows_from_returns(assets, pct_changes, dates, date_index) if allow_calibration else [],
                "volatility_by_asset": _volatility_from_history(assets, pct_changes, date_index),
                "track_a_minor_enhancement_base": True,
            }
            cfg = NewsOverlayConfig(
                track="A",
                n_method=spec.n_method,
                i_method=spec.i_method,
                s_method=spec.s_method,
                offline=True,
                device=device,
                batch_size=batch_size,
                cache_dir=str(cache_dir),
                trace_dir=str(trace_dir),
                proxy_mode=False,
                feature_schema_version=f"news_overlay_schema_v4_track_a_minor_{period}_{spec.family}",
                local_model_paths=dict(local_model_paths),
                local_model_metadata=dict(local_model_metadata),
            )
            trace = ScaffoldNewsOverlayPipeline(cfg).run(payload)
            weights = _weights_for_assets(trace, assets, base_weights)
            raw_target[date_index, :] = [weights.get(asset, 0.0) for asset in assets]
            metrics = _trace_metrics(trace)
            delta = raw_target[date_index, :] - base_array[date_index, :]
            row = {
                "run_id": spec.prompt23_run_id,
                "candidate_family": spec.family,
                "date": date,
                "news_count": len(news_by_date.get(date, [])),
                "max_abs_overlay": float(np.abs(delta).max()),
                "mean_abs_overlay": float(np.abs(delta).mean()),
                **metrics,
            }
            trace_rows.append(row)
            cache_rows.extend(_trace_cache_rows(spec.prompt23_run_id, date, trace))
            statuses.extend(str(result.get("status")) for result in trace.get("results", ()))
            blocked_methods.update(str(code) for code in (trace.get("model_status") or {}).get("blocked_methods", ()))
            network_attempted = network_attempted or bool((trace.get("model_status") or {}).get("network_attempted"))
            runtime_seconds += float((trace.get("runtime_report") or {}).get("total_runtime_seconds") or 0.0)
    finally:
        sampler.stop()
    elapsed = perf_counter() - started
    return {
        "spec": spec,
        "dates": dates,
        "assets": assets,
        "open_prices": open_prices,
        "pct_changes": pct_changes,
        "base_array": base_array,
        "raw_target": raw_target,
        "trace_rows": trace_rows,
        "cache_rows": cache_rows,
        "status": _evaluation_status(statuses),
        "blocked_methods": ";".join(sorted(blocked_methods)),
        "network_attempted": network_attempted,
        "runtime_sec": _round(runtime_seconds or elapsed),
        "device": device,
        "batch_size": batch_size,
        "gpu_util_mean": sampler.mean_util,
        "gpu_util_peak": sampler.peak_util,
        "vram_peak_mb": sampler.peak_vram,
        "cache_hit_rate": cache_hit_rate(cache_rows),
        "cache_namespace": str(cache_dir),
    }


def evaluate_variant(base: dict[str, Any], variant: VariantSpec, *, stage: str, period_label: str) -> dict[str, Any]:
    spec: CandidateSpec = base["spec"]
    tuned0 = _apply_params(base["raw_target"], base["base_array"], base["trace_rows"], base["pct_changes"], spec.params)
    enhanced, attribution = apply_enhancement_hooks(tuned0, base["base_array"], base["trace_rows"], variant, spec)
    replay = run_reference_official_semantics(
        OfficialSemanticsInput(
            dates=base["dates"],
            assets=base["assets"],
            open_prices=base["open_prices"],
            pct_changes=base["pct_changes"],
            target_weights=enhanced,
        )
    )
    delta = np.abs(enhanced - base["base_array"])
    trace_summary = _aggregate_trace_metrics(base["trace_rows"])
    active_days = int(np.sum(np.max(delta, axis=1) > 1e-8))
    no_trade_days = int(delta.shape[0] - active_days)
    status = "pass" if base["status"] == "pass" and not base["network_attempted"] else str(base["status"])
    return {
        "run_id": f"TA_{spec.family}_{variant.code}_{period_label}",
        "stage": stage,
        "period": period_label,
        "track": "A",
        "candidate_family": spec.family,
        "source_prompt23_run_id": spec.prompt23_run_id,
        "method_stack": spec.method_stack,
        "variant_code": variant.code,
        "variant_name": variant.name,
        "enhancement_hooks": "+".join(variant.hooks) if variant.hooks else "off",
        "architecture": spec.architecture,
        "status": status,
        "dates_run": len(base["dates"]),
        "model_mode": "real_local_transformer_base_plus_feature_hooks",
        "base_transformer_inference_reused_for_variants": True,
        "network_attempted": base["network_attempted"],
        "proxy_mode": False,
        "blocked_methods": base["blocked_methods"],
        "local_files_only": True,
        "return": _round(replay.metrics.get("cumulative_return")),
        "sharpe": _round(replay.metrics.get("sharpe_ratio")),
        "max_drawdown": _round(replay.metrics.get("max_drawdown")),
        "turnover": _round(replay.metrics.get("turnover")),
        "active_news_days": sum(1 for row in base["trace_rows"] if int(row.get("news_count") or 0) > 0),
        "overlay_active_days": active_days,
        "fallback_no_trade_days": no_trade_days,
        "active_transformer_days": trace_summary.get("transformer_active_days", 0),
        "mean_abs_overlay": _round(float(delta.mean())),
        "max_abs_overlay": _round(float(delta.max())),
        "confidence_bucket": attribution.get("confidence_bucket", ""),
        "decay_attribution": attribution.get("decay_attribution", ""),
        "composite_attribution": attribution.get("composite_attribution", ""),
        "deadband_attribution": attribution.get("deadband_attribution", ""),
        "selection_score": "",
        "baseline_variant": variant.code == "V0",
        "notes": variant.notes,
        "runtime_sec": base["runtime_sec"],
        "device": base["device"],
        "batch_size": base["batch_size"],
        "gpu_util_mean": base["gpu_util_mean"],
        "gpu_util_peak": base["gpu_util_peak"],
        "vram_peak_mb": base["vram_peak_mb"],
        "cache_hit_rate": base["cache_hit_rate"],
        "cache_namespace": base["cache_namespace"],
    }


def apply_enhancement_hooks(
    target: np.ndarray,
    base: np.ndarray,
    trace_rows: list[dict[str, Any]],
    variant: VariantSpec,
    spec: CandidateSpec,
) -> tuple[np.ndarray, dict[str, str]]:
    out = target.copy()
    attribution: dict[str, str] = {}
    if "H2" in variant.hooks:
        out, attribution["confidence_bucket"] = apply_h2_confidence(out, base, trace_rows, spec)
    if "H3" in variant.hooks:
        out, attribution["decay_attribution"] = apply_h3_decay(out, base, spec)
    if "H4" in variant.hooks:
        out, attribution["deadband_attribution"] = apply_h4_deadband(out, base, strict=False)
    if "H4_STRICT" in variant.hooks:
        out, attribution["deadband_attribution"] = apply_h4_deadband(out, base, strict=True)
    if "H6" in variant.hooks:
        out, attribution["composite_attribution"] = apply_h6_dominance(out, base)
    return normalize_targets(out), attribution


def apply_h2_confidence(
    target: np.ndarray,
    base: np.ndarray,
    trace_rows: list[dict[str, Any]],
    spec: CandidateSpec,
) -> tuple[np.ndarray, str]:
    aspect = np.asarray([_num(row.get("aspect_coverage"), default=0.0) for row in trace_rows], dtype=float)
    label = np.asarray([_num(row.get("event_label_confidence"), default=0.0) for row in trace_rows], dtype=float)
    embed = np.asarray([_num(row.get("embedding_coverage"), default=0.0) for row in trace_rows], dtype=float)
    if spec.family == "G10A":
        confidence = 0.75 * embed + 0.25 * label
    elif spec.family == "G12A":
        confidence = 0.45 * embed + 0.35 * aspect + 0.20 * label
    else:
        confidence = 0.70 * aspect + 0.30 * label
    conf_n = minmax(confidence)
    scale = 0.55 + 0.45 * conf_n
    out = base + (target - base) * scale[:, None]
    low = int(np.sum(conf_n < 0.33))
    mid = int(np.sum((conf_n >= 0.33) & (conf_n < 0.66)))
    high = int(np.sum(conf_n >= 0.66))
    return out, json.dumps({"low": low, "mid": mid, "high": high}, sort_keys=True)


def apply_h3_decay(target: np.ndarray, base: np.ndarray, spec: CandidateSpec) -> tuple[np.ndarray, str]:
    delta = target - base
    weights = (0.70, 0.22, 0.08) if spec.family == "G11A" else (0.64, 0.26, 0.10)
    smoothed = np.zeros_like(delta)
    for idx in range(delta.shape[0]):
        smoothed[idx] += weights[0] * delta[idx]
        if idx > 0:
            smoothed[idx] += weights[1] * delta[idx - 1]
        if idx > 1:
            smoothed[idx] += weights[2] * delta[idx - 2]
    before = float(np.abs(delta).mean())
    after = float(np.abs(smoothed).mean())
    return base + smoothed, json.dumps({"mean_abs_before": round(before, 6), "mean_abs_after": round(after, 6)}, sort_keys=True)


def apply_h4_deadband(target: np.ndarray, base: np.ndarray, *, strict: bool) -> tuple[np.ndarray, str]:
    delta = target - base
    l1 = np.abs(delta).sum(axis=1)
    threshold = 0.004 if strict else 0.0025
    mask = l1 >= threshold
    out = base + delta * mask[:, None]
    out = _apply_turnover_cap(out, "low")
    if strict:
        out = base + (out - base) * 0.80
        out = _apply_turnover_cap(out, "low")
    return out, json.dumps({"deadband": threshold, "zeroed_days": int(np.sum(~mask)), "strict": strict}, sort_keys=True)


def apply_h6_dominance(target: np.ndarray, base: np.ndarray) -> tuple[np.ndarray, str]:
    delta = target - base
    out_delta = delta.copy()
    capped_days = 0
    before_ratios = []
    after_ratios = []
    for idx in range(delta.shape[0]):
        row = out_delta[idx]
        total = float(np.abs(row).sum())
        if total <= 1e-12:
            before_ratios.append(0.0)
            after_ratios.append(0.0)
            continue
        before = float(np.abs(row).max() / total)
        before_ratios.append(before)
        if before > 0.55:
            capped_days += 1
            limit = 0.55 * total
            row = np.clip(row, -limit, limit)
            out_delta[idx] = row * 0.92
        total_after = float(np.abs(out_delta[idx]).sum())
        after_ratios.append(float(np.abs(out_delta[idx]).max() / total_after) if total_after > 1e-12 else 0.0)
    return base + out_delta, json.dumps(
        {
            "dominance_capped_days": capped_days,
            "mean_dominance_before": round(float(np.mean(before_ratios)), 6),
            "mean_dominance_after": round(float(np.mean(after_ratios)), 6),
        },
        sort_keys=True,
    )


def attach_selection_scores(rows: list[dict[str, Any]]) -> None:
    for family in CANDIDATES:
        family_rows = [row for row in rows if row.get("candidate_family") == family and row.get("status") == "pass"]
        ranks = {
            "sharpe": rank_scores(family_rows, "sharpe", higher=True),
            "return": rank_scores(family_rows, "return", higher=True),
            "max_drawdown": rank_scores(family_rows, "max_drawdown", higher=False),
            "turnover": rank_scores(family_rows, "turnover", higher=False),
        }
        for row in family_rows:
            idx = id(row)
            score = (
                0.40 * ranks["sharpe"].get(idx, 0.0)
                + 0.20 * ranks["return"].get(idx, 0.0)
                + 0.25 * ranks["max_drawdown"].get(idx, 0.0)
                + 0.15 * ranks["turnover"].get(idx, 0.0)
            )
            row["selection_score"] = round(score, 6)
            row["conservative_score"] = round(score, 6)


def rank_scores(rows: list[dict[str, Any]], field: str, *, higher: bool) -> dict[int, float]:
    clean = [row for row in rows if math.isfinite(_num(row.get(field), default=float("nan")))]
    clean.sort(key=lambda row: _num(row.get(field)), reverse=higher)
    n = max(1, len(clean) - 1)
    return {id(row): (1.0 - index / n if len(clean) > 1 else 1.0) for index, row in enumerate(clean)}


def write_stage0_summary(rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Track A Stage 0 Smoke Summary",
        "",
        "Scope: 3 Track A candidates, 10 2024 dates, baseline hooks off.",
        "",
        md_table(rows, ("candidate_family", "run_id", "status", "dates_run", "sharpe", "return", "turnover", "network_attempted", "proxy_mode")),
    ]
    (REFERENCE / "track_a_stage0_smoke_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_stage1_summary(rows: list[dict[str, Any]]) -> None:
    baseline = {row["candidate_family"]: row for row in rows if row.get("variant_code") == "V0"}
    comparison = []
    for family in CANDIDATES:
        family_rows = [row for row in rows if row.get("candidate_family") == family]
        if not family_rows:
            continue
        family_rows.sort(key=lambda row: (_num(row.get("selection_score")), _num(row.get("sharpe"))), reverse=True)
        best = family_rows[0]
        base = baseline.get(family, {})
        comparison.append(delta_row(best, base, "stage1_best_vs_baseline"))
    lines = [
        "# Track A Stage 1 2024 Tune Summary",
        "",
        f"Rows total: {len(rows)}",
        f"Rows passed: {sum(1 for row in rows if row.get('status') == 'pass')}",
        "Selection score uses 2024 only within each candidate family.",
        "",
        "## Best Variant vs Baseline",
        md_table(comparison, ("candidate_family", "selected_variant", "baseline_variant", "delta_sharpe", "delta_return", "delta_max_drawdown", "delta_turnover", "decision_hint")),
        "",
        "## Full Ranking",
        md_table(sorted(rows, key=lambda row: (str(row.get("candidate_family")), -_num(row.get("selection_score")))), ("candidate_family", "variant_code", "enhancement_hooks", "selection_score", "sharpe", "return", "max_drawdown", "turnover", "overlay_active_days")),
    ]
    (REFERENCE / "track_a_stage1_2024_tune_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_ablation_evidence(rows: list[dict[str, Any]]) -> None:
    output = []
    baseline = {row["candidate_family"]: row for row in rows if row.get("variant_code") == "V0"}
    for row in rows:
        if row.get("variant_code") == "V0":
            continue
        base = baseline.get(row["candidate_family"], {})
        output.append(
            {
                "candidate_family": row["candidate_family"],
                "variant_code": row["variant_code"],
                "hooks": row["enhancement_hooks"],
                "baseline_run_id": base.get("run_id", ""),
                "variant_run_id": row["run_id"],
                "delta_sharpe": _round(_num(row.get("sharpe")) - _num(base.get("sharpe"))),
                "delta_return": _round(_num(row.get("return")) - _num(base.get("return"))),
                "delta_max_drawdown": _round(_num(row.get("max_drawdown")) - _num(base.get("max_drawdown"))),
                "delta_turnover": _round(_num(row.get("turnover")) - _num(base.get("turnover"))),
                "confidence_bucket": row.get("confidence_bucket", ""),
                "decay_attribution": row.get("decay_attribution", ""),
                "composite_attribution": row.get("composite_attribution", ""),
                "deadband_attribution": row.get("deadband_attribution", ""),
                "verdict": "improve" if _num(row.get("selection_score")) > _num(base.get("selection_score")) else "no_improve",
            }
        )
    write_csv(REFERENCE / "track_a_ablation_evidence.csv", output)


def write_freeze_decisions(frozen: list[dict[str, Any]], rows: list[dict[str, Any]]) -> None:
    baseline = {row["candidate_family"]: row for row in rows if row.get("variant_code") == "V0"}
    lines = [
        "# Track A Freeze Decisions",
        "",
        "Frozen using Stage 1 2024 rows only. Stage 2 2025 results were not read or used.",
        "",
        md_table(frozen, ("candidate_family", "variant_code", "enhancement_hooks", "selection_score", "sharpe", "return", "max_drawdown", "turnover", "freeze_rule")),
        "",
        "## Baseline vs Frozen",
        md_table([delta_row(row, baseline.get(row["candidate_family"], {}), "frozen_vs_baseline") for row in frozen], ("candidate_family", "selected_variant", "baseline_variant", "delta_sharpe", "delta_return", "delta_max_drawdown", "delta_turnover", "decision_hint")),
    ]
    (REFERENCE / "track_a_freeze_decisions.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_stage2_summary(rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Track A Stage 2 Frozen 2025 Summary",
        "",
        "2025 was run only after Stage 1 freeze. No parameter or variant changes were made from 2025 metrics.",
        "",
        md_table(rows, ("candidate_family", "variant_code", "enhancement_hooks", "status", "dates_run", "sharpe", "return", "max_drawdown", "turnover", "source_2024_variant_run_id")),
    ]
    (REFERENCE / "track_a_stage2_2025_frozen_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_final_status() -> None:
    stage1 = read_csv(REFERENCE / "track_a_stage1_2024_tune_matrix.csv")
    frozen = read_csv(REFERENCE / "track_a_freeze_decisions.csv")
    stage2 = read_csv(REFERENCE / "track_a_stage2_2025_frozen_results.csv")
    baseline = {row["candidate_family"]: row for row in stage1 if row.get("variant_code") == "V0"}
    frozen_by_family = {row["candidate_family"]: row for row in frozen}
    stage2_by_family = {row["candidate_family"]: row for row in stage2}
    preserved = _preserved_manifest()
    primary = preserved.get(PRIMARY_PRESERVED["A"], {})
    fallback = preserved.get(FALLBACK_PRESERVED["A"], {})
    status_rows = []
    for family in CANDIDATES:
        selected = frozen_by_family.get(family, {})
        base = baseline.get(family, {})
        frozen_2025 = stage2_by_family.get(family, {})
        delta_sharpe = _num(selected.get("sharpe")) - _num(base.get("sharpe"))
        decision = "improve" if delta_sharpe > 0.005 and _num(selected.get("turnover")) <= max(_num(base.get("turnover")) * 1.15, _num(base.get("turnover")) + 0.0005) else "no improve"
        if not selected or not frozen_2025:
            decision = "blocked"
        status_rows.append(
            {
                "candidate_family": family,
                "baseline_variant": base.get("variant_code", ""),
                "selected_variant": selected.get("variant_code", ""),
                "2024_baseline_sharpe": base.get("sharpe", ""),
                "2024_baseline_return": base.get("return", ""),
                "2024_baseline_drawdown": base.get("max_drawdown", ""),
                "2024_baseline_turnover": base.get("turnover", ""),
                "2024_selected_sharpe": selected.get("sharpe", ""),
                "2024_selected_return": selected.get("return", ""),
                "2024_selected_score": selected.get("selection_score", ""),
                "2024_selected_drawdown": selected.get("max_drawdown", ""),
                "2024_selected_turnover": selected.get("turnover", ""),
                "2024_delta_sharpe": _round(_num(selected.get("sharpe")) - _num(base.get("sharpe"))),
                "2024_delta_return": _round(_num(selected.get("return")) - _num(base.get("return"))),
                "2024_delta_drawdown": _round(_num(selected.get("max_drawdown")) - _num(base.get("max_drawdown"))),
                "2024_delta_turnover": _round(_num(selected.get("turnover")) - _num(base.get("turnover"))),
                "overlay_active_days": selected.get("overlay_active_days", ""),
                "fallback_no_trade_days": selected.get("fallback_no_trade_days", ""),
                "confidence_bucket": selected.get("confidence_bucket", ""),
                "decay_attribution": selected.get("decay_attribution", ""),
                "composite_attribution": selected.get("composite_attribution", ""),
                "2025_frozen_sharpe": frozen_2025.get("sharpe", ""),
                "2025_frozen_return": frozen_2025.get("return", ""),
                "delta_vs_preserved_primary_2024_sharpe": _round(_num(selected.get("sharpe")) - _num(primary.get("2024_sharpe"))),
                "delta_vs_preserved_fallback_2024_sharpe": _round(_num(selected.get("sharpe")) - _num(fallback.get("2024_sharpe"))),
                "final_track_a_status": "research_only",
                "decision": decision,
            }
        )
    lines = [
        "# Track A Final Status",
        "",
        "Track A remains research-only. No candidate is promoted and official-server parity is not claimed.",
        "",
        md_table(status_rows, ("candidate_family", "selected_variant", "decision", "2024_selected_score", "2024_selected_sharpe", "2024_selected_drawdown", "2024_selected_turnover", "2025_frozen_sharpe", "final_track_a_status")),
        "",
        "## Baseline vs Selected",
        md_table(status_rows, ("candidate_family", "baseline_variant", "selected_variant", "2024_baseline_sharpe", "2024_selected_sharpe", "2024_delta_sharpe", "2024_delta_return", "2024_delta_drawdown", "2024_delta_turnover")),
        "",
        "## Evidence Details",
        md_table(status_rows, ("candidate_family", "overlay_active_days", "fallback_no_trade_days", "confidence_bucket", "decay_attribution", "composite_attribution", "delta_vs_preserved_primary_2024_sharpe", "delta_vs_preserved_fallback_2024_sharpe")),
        "",
        "Non-selected H2/H3/H6 attribution rows are preserved in `track_a_ablation_evidence.csv`.",
    ]
    (REFERENCE / "track_a_final_status.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def delta_row(selected: dict[str, Any], baseline: dict[str, Any], label: str) -> dict[str, Any]:
    delta_sharpe = _round(_num(selected.get("sharpe")) - _num(baseline.get("sharpe")))
    delta_turnover = _round(_num(selected.get("turnover")) - _num(baseline.get("turnover")))
    return {
        "candidate_family": selected.get("candidate_family", ""),
        "selected_variant": selected.get("variant_code", ""),
        "baseline_variant": baseline.get("variant_code", ""),
        "delta_sharpe": delta_sharpe,
        "delta_return": _round(_num(selected.get("return")) - _num(baseline.get("return"))),
        "delta_max_drawdown": _round(_num(selected.get("max_drawdown")) - _num(baseline.get("max_drawdown"))),
        "delta_turnover": delta_turnover,
        "decision_hint": "improve" if delta_sharpe > 0.005 and delta_turnover <= 0.001 else "no_improve",
        "label": label,
    }


def normalize_targets(target: np.ndarray) -> np.ndarray:
    out = np.nan_to_num(target, nan=0.0, posinf=0.0, neginf=0.0)
    out = np.clip(out, 0.0, 0.98)
    sums = out.sum(axis=1)
    too_high = sums > 0.98
    out[too_high] *= (0.98 / sums[too_high])[:, None]
    return out


def minmax(values: np.ndarray) -> np.ndarray:
    if values.size == 0:
        return values
    low = float(np.nanmin(values))
    high = float(np.nanmax(values))
    if not math.isfinite(low) or not math.isfinite(high) or abs(high - low) < 1e-12:
        return np.ones_like(values)
    return (values - low) / (high - low)


def cache_hit_rate(rows: list[dict[str, Any]]) -> float:
    cacheable = [row for row in rows if row.get("cache_required")]
    if not cacheable:
        return 0.0
    return round(sum(1 for row in cacheable if row.get("cache_hit")) / len(cacheable), 6)


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    if not fieldnames:
        fieldnames = ["empty"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def md_table(rows: list[dict[str, Any]], fields: tuple[str, ...]) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(fields) + " |", "| " + " | ".join("---" for _ in fields) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(field, "")) for field in fields) + " |")
    return "\n".join(lines)


def _selected_families(candidate: str) -> tuple[str, ...]:
    if candidate == "all":
        return tuple(CANDIDATES)
    return (candidate,)


if __name__ == "__main__":
    raise SystemExit(main())
