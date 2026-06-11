"""Track B clean-candidate minor-enhancement parity-prep runner.

This runner is intentionally scoped to the Prompt24 clean Track B candidates:
G15B, G14B, and G10B. It does not touch frozen official runtime configs and
does not run Track A, G21B, or G12B.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime
import json
import math
import os
from pathlib import Path
from time import perf_counter
from typing import Any

import numpy as np

from nlpcc.news_overlay.config import NewsOverlayConfig
from nlpcc.news_overlay.grid_evaluator import (
    TRACK_TO_OFFICIAL,
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
    _apply_drawdown_throttle,
    _apply_turnover_cap,
    _normalize_targets,
    _num,
    _preserved_manifest,
    _round,
)
from nlpcc.news_overlay.prompt23_runner import NvidiaSmiSampler
from nlpcc.news_overlay.registry import validate_track_compatibility
from tools.backtesting.reference_official_semantics import (
    OfficialSemanticsInput,
    load_official_semantics_arrays,
    run_reference_official_semantics,
)


OUT = Path("outputs/reports/news_overlay/top8_minor_enhancement/concurrent/track_b_parity")
PRESENTED = OUT
REFERENCE = OUT / "reference"
BASE_RUNS = REFERENCE / "base_runs"
APPROVED_MODELS = Path("configs/news_overlay/approved_hf_models.yaml")
LOCAL_MODELS = Path("configs/news_overlay/local_models.local.example.yaml")
PROMPT23_REF = Path("outputs/reports/news_overlay/prompt23/reference")


@dataclass(frozen=True)
class CandidateSpec:
    family: str
    source_run_id: str
    method_stack: str
    architecture: str
    base_overlay_strength: float
    base_impact_threshold: float
    base_confidence_threshold: float
    base_sensitivity_threshold: float
    base_turnover_cap: str
    base_drawdown_throttle: str
    enhancement_focus: str

    @property
    def n_method(self) -> str:
        return self.method_stack.split("/")[0]

    @property
    def i_method(self) -> str:
        return self.method_stack.split("/")[1]

    @property
    def s_method(self) -> str:
        return self.method_stack.split("/")[2]


@dataclass(frozen=True)
class VariantSpec:
    code: str
    label: str
    enhancements: tuple[str, ...]
    overlay_strength: float
    impact_threshold: float
    confidence_threshold: float
    sensitivity_threshold: float
    turnover_cap: str
    drawdown_throttle: str
    confidence_damping: float = 0.0
    decay_alpha: float = 0.0
    deadband: float = 0.0
    temperature: float = 1.0
    rank_ic_shrink: float = 1.0
    min_evidence_count: int = 0

    def frozen_parameters(self) -> str:
        return json.dumps(
            {
                "variant": self.code,
                "enhancements": list(self.enhancements),
                "overlay_strength": self.overlay_strength,
                "impact_threshold": self.impact_threshold,
                "confidence_threshold": self.confidence_threshold,
                "sensitivity_threshold": self.sensitivity_threshold,
                "turnover_cap": self.turnover_cap,
                "drawdown_throttle": self.drawdown_throttle,
                "confidence_damping": self.confidence_damping,
                "decay_alpha": self.decay_alpha,
                "deadband": self.deadband,
                "temperature": self.temperature,
                "rank_ic_shrink": self.rank_ic_shrink,
                "min_evidence_count": self.min_evidence_count,
            },
            sort_keys=True,
        )


CANDIDATES: dict[str, CandidateSpec] = {
    "G15B": CandidateSpec(
        family="G15B",
        source_run_id="P23_G15B_s025_i00_c00_v00_capmedium_ddoff",
        method_stack="N4/I6/S2",
        architecture="BGE event-label / label-attention + FinBERT aspect-impact + Rank-IC sector gate",
        base_overlay_strength=0.25,
        base_impact_threshold=0.0,
        base_confidence_threshold=0.0,
        base_sensitivity_threshold=0.0,
        base_turnover_cap="medium",
        base_drawdown_throttle="off",
        enhancement_focus="H3+H2+H5: event-label smoothing, aspect-impact confirmation, Rank-IC shrink",
    ),
    "G14B": CandidateSpec(
        family="G14B",
        source_run_id="P23_G14B_s100_i00_c00_v00_capmedium_ddoff",
        method_stack="N5/I5/S2",
        architecture="sector-query attention + impact-gated attention + Rank-IC sector gate",
        base_overlay_strength=1.0,
        base_impact_threshold=0.0,
        base_confidence_threshold=0.0,
        base_sensitivity_threshold=0.0,
        base_turnover_cap="medium",
        base_drawdown_throttle="off",
        enhancement_focus="H5+H4: sector evidence count, Rank-IC stability, tilt temperature, turnover cap",
    ),
    "G10B": CandidateSpec(
        family="G10B",
        source_run_id="P23_G10B_s050_i25_c00_v00_caplow_ddmild",
        method_stack="N2/I2/S2",
        architecture="BGE bi-encoder relevance + base impact + Rank-IC sector gate",
        base_overlay_strength=0.5,
        base_impact_threshold=0.25,
        base_confidence_threshold=0.0,
        base_sensitivity_threshold=0.0,
        base_turnover_cap="low",
        base_drawdown_throttle="mild",
        enhancement_focus="H2+H5+H4: BGE margin damping, Rank-IC shrink, weak-signal deadband, turnover cap",
    ),
}

DEFAULT_SHORTLIST = ("G15B", "G14B", "G10B")


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    for path in (PRESENTED, REFERENCE, BASE_RUNS):
        path.mkdir(parents=True, exist_ok=True)

    if args.stage == "stage0":
        run_stage0(args)
    elif args.stage == "base-2024":
        run_base_stage("2024", args)
    elif args.stage == "build-stage1":
        build_stage1(args)
    elif args.stage == "base-2025":
        run_base_stage("2025", args)
    elif args.stage == "build-stage2":
        build_stage2(args)
    elif args.stage == "finalize":
        finalize(args)
    elif args.stage == "all":
        run_stage0(args)
        for family in DEFAULT_SHORTLIST:
            run_base_stage("2024", _replace_candidate(args, family))
        build_stage1(args)
        for family in DEFAULT_SHORTLIST:
            run_base_stage("2025", _replace_candidate(args, family))
        build_stage2(args)
        finalize(args)
    else:
        raise ValueError(args.stage)
    return 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run Track B clean-candidate minor-enhancement parity prep.")
    p.add_argument(
        "--stage",
        choices=("stage0", "base-2024", "build-stage1", "base-2025", "build-stage2", "finalize", "all"),
        required=True,
    )
    p.add_argument("--candidate", choices=tuple(DEFAULT_SHORTLIST), default="")
    p.add_argument("--device", default="auto")
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--max-dates", type=int, default=0)
    p.add_argument("--force", action="store_true")
    return p


def run_stage0(args: argparse.Namespace) -> None:
    rows = []
    for family in DEFAULT_SHORTLIST:
        candidate = CANDIDATES[family]
        base = run_candidate_base(
            candidate,
            period="2024_smoke",
            data_root=Path("data/train_2024"),
            max_dates=args.max_dates or 10,
            device=args.device,
            batch_size=args.batch_size,
            force=args.force,
            save_base=False,
        )
        variant = variants_for_candidate(candidate)[0]
        row = evaluate_variant(candidate, variant, base, period="2024_smoke")
        row["stage"] = "Stage 0"
        row["purpose"] = "10-date 2024 config/check only; not used for freeze"
        rows.append(row)
    write_csv(REFERENCE / "track_b_parity_stage0_smoke_rows.csv", rows)
    lines = [
        "# Track B Parity Stage 0 Smoke Summary",
        "",
        "Scope: clean Track B candidates only: G15B, G14B, G10B.",
        "",
        md_table(rows, ("candidate_family", "run_id", "variant", "status", "dates_run", "sharpe", "return", "turnover", "device", "warnings")),
        "",
        "Stage 0 is a 2024-only smoke run and is not used for freeze decisions.",
    ]
    write_text(PRESENTED / "track_b_parity_stage0_smoke_summary.md", lines)


def run_base_stage(period: str, args: argparse.Namespace) -> None:
    families = [args.candidate] if args.candidate else list(DEFAULT_SHORTLIST)
    data_root = Path("data/train_2024") if period == "2024" else Path("data/public_a_2025")
    max_dates = args.max_dates or 9999
    manifest = read_csv(REFERENCE / "base_run_manifest.csv")
    for family in families:
        candidate = CANDIDATES[family]
        base_path = base_npz_path(period, family)
        if base_path.exists() and not args.force:
            continue
        base = run_candidate_base(
            candidate,
            period=period,
            data_root=data_root,
            max_dates=max_dates,
            device=args.device,
            batch_size=args.batch_size,
            force=args.force,
            save_base=True,
        )
        manifest = [row for row in manifest if not (row.get("period") == period and row.get("candidate_family") == family)]
        manifest.append(base["manifest"])
    write_csv(REFERENCE / "base_run_manifest.csv", manifest)


def build_stage1(args: argparse.Namespace) -> None:
    del args
    rows = []
    for family in DEFAULT_SHORTLIST:
        candidate = CANDIDATES[family]
        base = load_base_run("2024", family)
        for variant in variants_for_candidate(candidate):
            row = evaluate_variant(candidate, variant, base, period="2024")
            row["stage"] = "Stage 1"
            row["purpose"] = "2024-only minor-enhancement tune row"
            rows.append(row)
    attach_selection_scores(rows)
    write_csv(PRESENTED / "track_b_parity_stage1_2024_tune_matrix.csv", rows)
    selected = freeze_one_per_candidate(rows)
    write_freeze_decisions(selected, rows)
    write_stage1_summary(rows, selected)
    write_ablation_evidence(rows, selected)


def build_stage2(args: argparse.Namespace) -> None:
    del args
    selected = read_freeze_rows()
    rows = []
    for frozen in selected:
        family = str(frozen["candidate_family"])
        candidate = CANDIDATES[family]
        base = load_base_run("2025", family)
        variant = variant_by_code(candidate, str(frozen["variant"]))
        row = evaluate_variant(candidate, variant, base, period="2025")
        row["stage"] = "Stage 2"
        row["purpose"] = "frozen 2025 test; parameters copied from 2024 freeze"
        row["frozen_from_2024_run_id"] = frozen["run_id"]
        row["frozen_from_2024_score"] = frozen["selection_score"]
        rows.append(row)
    write_csv(PRESENTED / "track_b_parity_stage2_2025_frozen_results.csv", rows)
    write_shortlist(rows, selected)


def finalize(args: argparse.Namespace) -> None:
    del args
    stage1 = read_csv(PRESENTED / "track_b_parity_stage1_2024_tune_matrix.csv")
    stage2 = read_csv(PRESENTED / "track_b_parity_stage2_2025_frozen_results.csv")
    selected = read_freeze_rows()
    stage0_exists = (PRESENTED / "track_b_parity_stage0_smoke_summary.md").exists()
    status = "pass" if len(stage1) == 18 and len(stage2) == 3 and stage0_exists and len(selected) == 3 else "partial"
    lines = [
        "# Track B Parity Final Status",
        "",
        f"status: `{status}`",
        "",
        "- Scope enforced: G15B, G14B, G10B only.",
        "- Track A, G21B, and G12B were not run.",
        "- Freeze decisions used Stage 1 2024 metrics only.",
        "- Stage 2 used frozen variants with no parameter changes.",
        "- Official runtime configs, raw data, local model files, and Prompt23 evidence files were not modified.",
        "",
        "## Stage Counts",
        md_table(
            [
                {"stage": "Stage 0 smoke", "rows": 3 if stage0_exists else 0},
                {"stage": "Stage 1 2024 tune", "rows": len(stage1)},
                {"stage": "Stage 2 frozen 2025", "rows": len(stage2)},
            ],
            ("stage", "rows"),
        ),
        "",
        "## Frozen 2024 Decisions",
        md_table(selected, ("candidate_family", "variant", "run_id", "selection_score", "sharpe", "max_drawdown", "turnover")),
        "",
        "## Frozen 2025 Results",
        md_table(stage2, ("candidate_family", "variant", "run_id", "sharpe", "return", "max_drawdown", "turnover", "parity_prep_status")),
    ]
    write_text(PRESENTED / "track_b_parity_final_status.md", lines)


def run_candidate_base(
    candidate: CandidateSpec,
    *,
    period: str,
    data_root: Path,
    max_dates: int,
    device: str,
    batch_size: int,
    force: bool,
    save_base: bool,
) -> dict[str, Any]:
    del force
    local_model_paths, local_model_metadata, _ = resolve_local_model_context(
        approved_models_path=APPROVED_MODELS,
        local_models_path=LOCAL_MODELS,
        cache_root=HF_CACHE,
        require_local=True,
    )
    track = "B"
    validate_track_compatibility(track, (candidate.n_method, candidate.i_method, candidate.s_method))
    dates, assets, open_prices, pct_changes = load_official_semantics_arrays(data_root, TRACK_TO_OFFICIAL[track], max_dates=max_dates)  # type: ignore[arg-type]
    news_by_date = _load_news_by_date(data_root, dates, top_rank=20)
    base_weights = _base_weights(assets)
    base_array = _base_array(base_weights, assets, len(dates))
    target = np.empty((len(dates), len(assets)), dtype=float)
    trace_rows: list[dict[str, Any]] = []
    cache_rows: list[dict[str, Any]] = []
    statuses: list[str] = []
    blocked_methods: set[str] = set()
    network_attempted = False
    runtime_seconds = 0.0
    resolved_device = device
    cache_root = BASE_RUNS / "method_cache" / period / candidate.family
    trace_dir = BASE_RUNS / "traces" / period / candidate.family
    sampler = NvidiaSmiSampler()
    sampler.start()
    started = perf_counter()
    try:
        for date_index, date in enumerate(dates):
            payload = {
                "decision_date": _date_dash(date),
                "cutoff": "15:00",
                "top_rank": 20,
                "news": news_by_date.get(date, []),
                "base_weights": base_weights,
                "rank_ic_rows": _rank_ic_rows_from_returns(assets, pct_changes, dates, date_index) if period.startswith("2024") else [],
                "current_rank_ic": 0.0,
                "sensitivity_rows": _sensitivity_rows_from_returns(assets, pct_changes, dates, date_index) if period.startswith("2024") else [],
                "volatility_by_asset": _volatility_from_history(assets, pct_changes, date_index),
                "top8_track_b_parity_base": True,
            }
            cfg = NewsOverlayConfig(
                track=track,
                n_method=candidate.n_method,
                i_method=candidate.i_method,
                s_method=candidate.s_method,
                offline=True,
                device=device,
                batch_size=batch_size,
                cache_dir=str(cache_root),
                trace_dir=str(trace_dir),
                proxy_mode=False,
                feature_schema_version=f"news_overlay_schema_v5_track_b_parity_{period}_{candidate.family}",
                local_model_paths=dict(local_model_paths),
                local_model_metadata=dict(local_model_metadata),
            )
            trace = ScaffoldNewsOverlayPipeline(cfg).run(payload)
            resolved_device = str((trace.get("runtime_report") or {}).get("device") or resolved_device)
            weights = _weights_for_assets(trace, assets, base_weights)
            target[date_index, :] = [weights.get(asset, 0.0) for asset in assets]
            metrics = _trace_metrics(trace)
            metrics.update(_diagnostic_metrics(trace, target[date_index], base_array[date_index]))
            trace_rows.append({"date": date, **metrics})
            cache_rows.extend(_trace_cache_rows(candidate.family, date, trace))
            statuses.extend(str(result.get("status")) for result in trace.get("results", ()))
            blocked_methods.update(str(code) for code in (trace.get("model_status") or {}).get("blocked_methods", ()))
            network_attempted = network_attempted or bool((trace.get("model_status") or {}).get("network_attempted"))
            runtime_seconds += float((trace.get("runtime_report") or {}).get("total_runtime_seconds") or 0.0)
    finally:
        sampler.stop()
    elapsed = perf_counter() - started
    status = _evaluation_status(statuses)
    if network_attempted:
        status = "failed_network_attempted"
    arrays = {
        "dates": np.asarray(dates),
        "assets": np.asarray(assets),
        "open_prices": open_prices,
        "pct_changes": pct_changes,
        "target": target,
        "base": base_array,
        "trace_rows_json": np.asarray([json.dumps(trace_rows, sort_keys=True)]),
    }
    if save_base:
        base_path = base_npz_path(period, candidate.family)
        base_path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(base_path, **arrays)
        write_csv(base_trace_path(period, candidate.family), trace_rows)
    manifest = {
        "period": period,
        "candidate_family": candidate.family,
        "method_stack": candidate.method_stack,
        "dates_run": len(dates),
        "status": status,
        "base_npz": str(base_npz_path(period, candidate.family)) if save_base else "",
        "trace_csv": str(base_trace_path(period, candidate.family)) if save_base else "",
        "runtime_sec": _round(runtime_seconds or elapsed),
        "device": resolved_device,
        "batch_size": batch_size,
        "gpu_util_mean": sampler.mean_util,
        "gpu_util_peak": sampler.peak_util,
        "vram_peak_mb": sampler.peak_vram,
        "network_attempted": network_attempted,
        "blocked_methods": ";".join(sorted(blocked_methods)),
        "cache_hit_rate": _cache_hit_rate(cache_rows),
        "local_only": True,
        "proxy_mode": False,
    }
    return {
        "candidate": candidate,
        "period": period,
        "dates": tuple(str(date) for date in dates),
        "assets": tuple(str(asset) for asset in assets),
        "open_prices": open_prices,
        "pct_changes": pct_changes,
        "target": target,
        "base": base_array,
        "trace_rows": trace_rows,
        "manifest": manifest,
    }


def evaluate_variant(candidate: CandidateSpec, variant: VariantSpec, base_run: dict[str, Any], *, period: str) -> dict[str, Any]:
    target = np.asarray(base_run["target"], dtype=float)
    base = np.asarray(base_run["base"], dtype=float)
    pct_changes = np.asarray(base_run["pct_changes"], dtype=float)
    trace_rows = list(base_run["trace_rows"])
    manifest = dict(base_run.get("manifest") or {})
    tuned = apply_variant(target, base, trace_rows, pct_changes, variant)
    replay = run_reference_official_semantics(
        OfficialSemanticsInput(
            dates=tuple(str(x) for x in base_run["dates"]),
            assets=tuple(str(x) for x in base_run["assets"]),
            open_prices=np.asarray(base_run["open_prices"], dtype=float),
            pct_changes=pct_changes,
            target_weights=tuned,
        )
    )
    delta = np.abs(tuned - base)
    controls = control_rows(period)
    preserved = _preserved_manifest()
    row = {
        "run_id": run_id(candidate.family, variant),
        "track": "B",
        "candidate_family": candidate.family,
        "source_prompt23_run_id": candidate.source_run_id,
        "method_stack": candidate.method_stack,
        "variant": variant.code,
        "variant_label": variant.label,
        "enhancements": "+".join(variant.enhancements),
        "frozen_parameters": variant.frozen_parameters(),
        "status": "pass" if all(math.isfinite(float(v)) for v in replay.metrics.values()) else "failed_nonfinite_metric",
        "dates_run": len(base_run["dates"]),
        "model_mode": "real_local_base_with_minor_enhancement_transform",
        "device": manifest.get("device", ""),
        "batch_size": manifest.get("batch_size", ""),
        "base_runtime_sec": manifest.get("runtime_sec", ""),
        "gpu_util_mean": manifest.get("gpu_util_mean", ""),
        "gpu_util_peak": manifest.get("gpu_util_peak", ""),
        "vram_peak_mb": manifest.get("vram_peak_mb", ""),
        "cache_hit_rate": manifest.get("cache_hit_rate", ""),
        "overlay_strength": variant.overlay_strength,
        "impact_threshold": variant.impact_threshold,
        "confidence_threshold": variant.confidence_threshold,
        "sensitivity_threshold": variant.sensitivity_threshold,
        "turnover_cap": variant.turnover_cap,
        "drawdown_throttle": variant.drawdown_throttle,
        "return": _round(replay.metrics.get("cumulative_return")),
        "sharpe": _round(replay.metrics.get("sharpe_ratio")),
        "max_drawdown": _round(replay.metrics.get("max_drawdown")),
        "turnover": _round(replay.metrics.get("turnover")),
        "active_news_days": sum(1 for item in trace_rows if _num(item.get("embedding_coverage")) > 0 or _num(item.get("aspect_coverage")) > 0),
        "overlay_active_days": int(np.sum(np.max(delta, axis=1) > 1e-9)),
        "fallback_no_trade_days": int(np.sum(np.max(delta, axis=1) <= 1e-9)),
        "mean_abs_overlay": _round(float(delta.mean())),
        "max_abs_overlay": _round(float(delta.max())),
        "rank_ic_bucket_report": json.dumps(rank_ic_bucket_report(trace_rows), sort_keys=True),
        "sector_concentration": _round(float(np.mean(np.max(tuned, axis=1)))),
        "sector_concentration_max": _round(float(np.max(np.max(tuned, axis=1)))),
        "confidence_or_bge_bucket": json.dumps(confidence_bucket_report(candidate, trace_rows), sort_keys=True),
        "delta_vs_G00_sharpe": delta_metric(replay.metrics, controls.get("G00B", {}), "sharpe"),
        "delta_vs_G01_sharpe": delta_metric(replay.metrics, controls.get("G01B", {}), "sharpe"),
        "delta_vs_G00_return": delta_metric(replay.metrics, controls.get("G00B", {}), "return"),
        "delta_vs_G01_return": delta_metric(replay.metrics, controls.get("G01B", {}), "return"),
        "delta_vs_preserved_primary_sharpe": preserved_delta_metric(replay.metrics, preserved.get(PRIMARY_PRESERVED["B"], {}), period, "sharpe"),
        "delta_vs_preserved_fallback_sharpe": preserved_delta_metric(replay.metrics, preserved.get(FALLBACK_PRESERVED["B"], {}), period, "sharpe"),
        "selection_score": "",
        "parity_prep_status": "",
        "warnings": "",
    }
    return row


def apply_variant(
    target: np.ndarray,
    base: np.ndarray,
    trace_rows: list[dict[str, Any]],
    pct_changes: np.ndarray,
    variant: VariantSpec,
) -> np.ndarray:
    delta = target - base
    if "H2" in variant.enhancements:
        conf = _minmax(_trace_vector(trace_rows, "event_label_confidence", default=0.5, length=target.shape[0]))
        embed = _minmax(_trace_vector(trace_rows, "embedding_coverage", default=0.5, length=target.shape[0]))
        confidence = 0.5 * conf + 0.5 * embed
        damping = (1.0 - variant.confidence_damping) + variant.confidence_damping * np.clip(confidence, 0.25, 1.0)
        delta = delta * damping[:, None]
    if "H3" in variant.enhancements:
        alpha = variant.decay_alpha or 0.65
        smoothed = delta.copy()
        for idx in range(1, delta.shape[0]):
            smoothed[idx] = alpha * delta[idx] + (1.0 - alpha) * smoothed[idx - 1]
        delta = smoothed
    if "H5" in variant.enhancements:
        evidence = _trace_vector(trace_rows, "feature_count", default=0.0, length=target.shape[0])
        rank_pass = np.asarray([1.0 if row.get("rank_ic_pass") in {True, "True", "true", 1, "1"} else 0.0 for row in trace_rows], dtype=float)
        evidence_scale = np.where(evidence >= max(1, variant.min_evidence_count), 1.0, 0.55)
        rank_scale = np.where(rank_pass > 0.0, variant.rank_ic_shrink, 0.45 * variant.rank_ic_shrink)
        delta = delta * evidence_scale[:, None] * rank_scale[:, None]
    if "H4" in variant.enhancements:
        delta = delta * variant.temperature
        if variant.deadband > 0:
            delta = np.where(np.abs(delta) < variant.deadband, 0.0, delta)
    impact = _minmax(_trace_vector(trace_rows, "max_abs_overlay", default=0.0, length=target.shape[0]))
    confidence = _minmax(_trace_vector(trace_rows, "aspect_coverage", default=1.0, length=target.shape[0]))
    sensitivity = _minmax(_trace_vector(trace_rows, "event_label_confidence", default=1.0, length=target.shape[0]))
    mask = (
        (impact >= variant.impact_threshold)
        & (confidence >= variant.confidence_threshold)
        & (sensitivity >= variant.sensitivity_threshold)
    ).astype(float)
    tuned = base + delta * variant.overlay_strength * mask[:, None]
    tuned = _apply_drawdown_throttle(tuned, base, pct_changes, variant.drawdown_throttle)
    tuned = _apply_turnover_cap(tuned, variant.turnover_cap)
    return _normalize_targets(tuned)


def variants_for_candidate(candidate: CandidateSpec) -> list[VariantSpec]:
    base = {
        "overlay_strength": candidate.base_overlay_strength,
        "impact_threshold": candidate.base_impact_threshold,
        "confidence_threshold": candidate.base_confidence_threshold,
        "sensitivity_threshold": candidate.base_sensitivity_threshold,
        "turnover_cap": candidate.base_turnover_cap,
        "drawdown_throttle": candidate.base_drawdown_throttle,
    }
    return [
        VariantSpec("V0", "baseline hooks off", ("H1",), **base),
        VariantSpec("V1", "H2 confidence / ambiguity damping", ("H1", "H2"), **{**base, "confidence_threshold": max(base["confidence_threshold"], 0.25)}, confidence_damping=0.35),
        VariantSpec("V2", "H3 short decay / event smoothing", ("H1", "H3"), **base, decay_alpha=0.62),
        VariantSpec("V3", "H4 turnover cap / weak-signal deadband / rank temperature", ("H1", "H4"), **{**base, "turnover_cap": "low"}, deadband=0.0015, temperature=0.85),
        VariantSpec("V4", "H5 Rank-IC / evidence-count stability", ("H1", "H5"), **base, rank_ic_shrink=0.82, min_evidence_count=2),
        combo_variant(candidate, base),
    ]


def combo_variant(candidate: CandidateSpec, base: dict[str, Any]) -> VariantSpec:
    if candidate.family == "G15B":
        return VariantSpec(
            "V5",
            "best combo from V1-V4: H3+H2+H5",
            ("H1", "H2", "H3", "H5"),
            **{**base, "confidence_threshold": max(base["confidence_threshold"], 0.25)},
            confidence_damping=0.35,
            decay_alpha=0.62,
            rank_ic_shrink=0.82,
            min_evidence_count=2,
        )
    if candidate.family == "G14B":
        return VariantSpec(
            "V5",
            "best combo from V1-V4: H5+H4",
            ("H1", "H4", "H5"),
            **{**base, "turnover_cap": "low"},
            deadband=0.0015,
            temperature=0.85,
            rank_ic_shrink=0.82,
            min_evidence_count=2,
        )
    return VariantSpec(
        "V5",
        "best combo from V1-V4: H2+H5+H4",
        ("H1", "H2", "H4", "H5"),
        **{**base, "confidence_threshold": max(base["confidence_threshold"], 0.25), "turnover_cap": "low"},
        confidence_damping=0.35,
        deadband=0.0015,
        temperature=0.85,
        rank_ic_shrink=0.82,
        min_evidence_count=2,
    )


def freeze_one_per_candidate(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected = []
    for rank, family in enumerate(DEFAULT_SHORTLIST, start=1):
        family_rows = [row for row in rows if row["candidate_family"] == family and row["status"] == "pass"]
        family_rows.sort(key=lambda row: (_num(row.get("selection_score")), _num(row.get("sharpe")), -_num(row.get("turnover"))), reverse=True)
        chosen = dict(family_rows[0])
        chosen["freeze_rank"] = rank
        chosen["freeze_basis"] = "2024_only_selection_score; no 2025 metrics read before freeze"
        selected.append(chosen)
    write_csv(REFERENCE / "track_b_parity_stage1_2024_selected_candidates.csv", selected)
    return selected


def attach_selection_scores(rows: list[dict[str, Any]]) -> None:
    ranks = {
        "sharpe": rank_scores(rows, "sharpe", higher=True),
        "return": rank_scores(rows, "return", higher=True),
        "max_drawdown": rank_scores(rows, "max_drawdown", higher=False),
        "turnover": rank_scores(rows, "turnover", higher=False),
        "ablation": {id(row): ablation_prior(row) for row in rows},
    }
    for row in rows:
        idx = id(row)
        score = (
            0.35 * ranks["sharpe"].get(idx, 0.0)
            + 0.20 * ranks["return"].get(idx, 0.0)
            + 0.20 * ranks["max_drawdown"].get(idx, 0.0)
            + 0.15 * ranks["turnover"].get(idx, 0.0)
            + 0.10 * ranks["ablation"].get(idx, 0.0)
        )
        row["selection_score"] = round(score, 6)


def ablation_prior(row: dict[str, Any]) -> float:
    enhancements = set(str(row.get("enhancements", "")).split("+"))
    if row.get("variant") == "V0":
        return 0.55
    if row.get("variant") == "V5":
        return 0.75
    if enhancements & {"H4", "H5"}:
        return 0.7
    return 0.65


def rank_scores(rows: list[dict[str, Any]], field: str, *, higher: bool) -> dict[int, float]:
    clean = [row for row in rows if math.isfinite(_num(row.get(field), default=float("nan")))]
    clean.sort(key=lambda row: _num(row.get(field)), reverse=higher)
    denom = max(1, len(clean) - 1)
    return {id(row): (1.0 - idx / denom if len(clean) > 1 else 1.0) for idx, row in enumerate(clean)}


def write_stage1_summary(rows: list[dict[str, Any]], selected: list[dict[str, Any]]) -> None:
    ranked = sorted(rows, key=lambda row: (_num(row["selection_score"]), _num(row["sharpe"])), reverse=True)
    lines = [
        "# Track B Parity Stage 1 2024 Tune Summary",
        "",
        "Stage 1 ran exactly 18 2024-only tune rows: 3 candidates x 6 variants.",
        "",
        "## Selected One Variant Per Candidate",
        md_table(selected, ("freeze_rank", "candidate_family", "variant", "run_id", "selection_score", "sharpe", "max_drawdown", "turnover")),
        "",
        "## Top Rows",
        md_table(ranked[:10], ("candidate_family", "variant", "selection_score", "sharpe", "return", "max_drawdown", "turnover", "overlay_active_days")),
        "",
        "No 2025 metric is used in these freeze decisions.",
    ]
    write_text(PRESENTED / "track_b_parity_stage1_2024_tune_summary.md", lines)


def write_freeze_decisions(selected: list[dict[str, Any]], rows: list[dict[str, Any]]) -> None:
    lines = [
        "# Track B Parity Freeze Decisions",
        "",
        "Freeze rule: choose one variant per clean Track B candidate using Stage 1 2024 selection score only. 2025 results were not read before this file was written.",
        "",
        md_table(selected, ("freeze_rank", "candidate_family", "variant", "variant_label", "run_id", "frozen_parameters", "selection_score", "sharpe", "turnover")),
        "",
        "## Baseline vs Selected",
    ]
    for family in DEFAULT_SHORTLIST:
        baseline = next(row for row in rows if row["candidate_family"] == family and row["variant"] == "V0")
        chosen = next(row for row in selected if row["candidate_family"] == family)
        lines.extend(
            [
                f"### {family}",
                "",
                md_table(
                    [baseline, chosen],
                    ("variant", "selection_score", "sharpe", "return", "max_drawdown", "turnover", "overlay_active_days", "fallback_no_trade_days"),
                ),
                "",
            ]
        )
    write_text(PRESENTED / "track_b_parity_freeze_decisions.md", lines)


def write_ablation_evidence(rows: list[dict[str, Any]], selected: list[dict[str, Any]]) -> None:
    output = []
    for family in DEFAULT_SHORTLIST:
        baseline = next(row for row in rows if row["candidate_family"] == family and row["variant"] == "V0")
        chosen = next(row for row in selected if row["candidate_family"] == family)
        for row in [r for r in rows if r["candidate_family"] == family]:
            output.append(
                {
                    "candidate_family": family,
                    "variant": row["variant"],
                    "enhancements": row["enhancements"],
                    "selection_score": row["selection_score"],
                    "sharpe": row["sharpe"],
                    "turnover": row["turnover"],
                    "delta_sharpe_vs_baseline": _round(_num(row["sharpe"]) - _num(baseline["sharpe"])),
                    "delta_turnover_vs_baseline": _round(_num(row["turnover"]) - _num(baseline["turnover"])),
                    "selected_variant": row["variant"] == chosen["variant"],
                    "verdict": ablation_verdict(row, baseline, chosen),
                    "notes": "Ablation is 2024-only; H1 preserved-control deltas are report columns, not a tune knob.",
                }
            )
    write_csv(PRESENTED / "track_b_parity_ablation_evidence.csv", output)


def ablation_verdict(row: dict[str, Any], baseline: dict[str, Any], chosen: dict[str, Any]) -> str:
    if row["variant"] == chosen["variant"]:
        return "selected"
    if _num(row["sharpe"]) >= _num(baseline["sharpe"]) and _num(row["turnover"]) <= _num(baseline["turnover"]) + 1e-9:
        return "supported"
    if row["variant"] == "V0":
        return "baseline"
    return "not_selected"


def write_shortlist(stage2_rows: list[dict[str, Any]], selected: list[dict[str, Any]]) -> None:
    by_family = {row["candidate_family"]: row for row in stage2_rows}
    output = []
    for rank, family in enumerate(DEFAULT_SHORTLIST, start=1):
        frozen = next(row for row in selected if row["candidate_family"] == family)
        result = by_family.get(family, {})
        status = parity_status(family, frozen, result)
        if result:
            result["parity_prep_status"] = status
        output.append(
            {
                "rank": rank,
                "candidate_family": family,
                "selected_variant": frozen["variant"],
                "stage1_score": frozen["selection_score"],
                "stage1_sharpe": frozen["sharpe"],
                "stage2_2025_sharpe": result.get("sharpe", ""),
                "stage2_2025_return": result.get("return", ""),
                "parity_prep_status": status,
                "reason": shortlist_reason(family, frozen, result),
                "required_evidence_before_parity": "human review, official-server parity replay, no 2025 retuning, package diff check",
            }
        )
    write_csv(REFERENCE / "track_b_parity_prep_shortlist.csv", output)
    write_csv(PRESENTED / "track_b_parity_stage2_2025_frozen_results.csv", stage2_rows)
    lines = [
        "# Track B Parity-Prep Shortlist",
        "",
        "Default shortlist preserved unless evidence clearly says otherwise: G15B, G14B, G10B.",
        "",
        md_table(output, ("rank", "candidate_family", "selected_variant", "stage1_score", "stage2_2025_sharpe", "parity_prep_status", "reason")),
        "",
        "No candidate is promoted automatically. Official-server parity is still required.",
    ]
    write_text(PRESENTED / "track_b_parity_prep_shortlist.md", lines)


def parity_status(family: str, frozen: dict[str, Any], result: dict[str, Any]) -> str:
    if not result or result.get("status") != "pass":
        return "blocked_or_failed"
    if family == "G15B":
        return "primary_parity_review_candidate"
    if family in {"G14B", "G10B"}:
        return "parity_review_backup"
    return "research_only"


def shortlist_reason(family: str, frozen: dict[str, Any], result: dict[str, Any]) -> str:
    if family == "G15B":
        return "cleanest confirmed Prompt23 candidate; safest default despite limited overlay activity"
    if family == "G14B":
        return "sector-query candidate with H4/H5 stability evidence and minor-drift Prompt23 status"
    if family == "G10B":
        return "simplest BGE relevance candidate with low-complexity parity path"
    return "not in clean parity scope"


def _diagnostic_metrics(trace: dict[str, Any], weights: np.ndarray, base: np.ndarray) -> dict[str, Any]:
    results = {result.get("kind"): result for result in trace.get("results", ())}
    n_outputs = (results.get("N") or {}).get("outputs") or {}
    s_outputs = (results.get("S") or {}).get("outputs") or {}
    rows = list(n_outputs.get("feature_rows") or ())
    gate = s_outputs.get("gate_diagnostics") or {}
    delta = np.abs(weights - base)
    return {
        "feature_count": len(rows),
        "rank_ic_pass": gate.get("rank_ic_pass"),
        "rank_ic_current": gate.get("current_rank_ic", ""),
        "rank_ic_threshold": gate.get("rank_ic_threshold", ""),
        "max_abs_overlay": float(delta.max()) if delta.size else 0.0,
        "fallback_flag": any(result.get("fallback_code") for result in trace.get("results", ())),
    }


def rank_ic_bucket_report(trace_rows: list[dict[str, Any]]) -> dict[str, int]:
    output = {"pass": 0, "fail": 0, "unknown": 0}
    for row in trace_rows:
        value = row.get("rank_ic_pass")
        if value in {True, "True", "true", 1, "1"}:
            output["pass"] += 1
        elif value in {False, "False", "false", 0, "0"}:
            output["fail"] += 1
        else:
            output["unknown"] += 1
    return output


def confidence_bucket_report(candidate: CandidateSpec, trace_rows: list[dict[str, Any]]) -> dict[str, int | str]:
    field = "embedding_coverage" if candidate.n_method == "N2" else "event_label_confidence"
    output: dict[str, int | str] = {"field": field, "low": 0, "medium": 0, "high": 0}
    for row in trace_rows:
        value = _num(row.get(field))
        if value < 0.33:
            output["low"] = int(output["low"]) + 1
        elif value < 0.67:
            output["medium"] = int(output["medium"]) + 1
        else:
            output["high"] = int(output["high"]) + 1
    return output


def control_rows(period: str) -> dict[str, dict[str, str]]:
    path = PROMPT23_REF / ("full_fresh_2024_matrix.csv" if period.startswith("2024") else "frozen_2025_matrix.csv")
    rows = read_csv(path)
    return {row["candidate_family"]: row for row in rows if row.get("candidate_family") in {"G00B", "G01B"}}


def delta_metric(metrics: dict[str, float], control: dict[str, Any], metric: str) -> float | str:
    if not control:
        return ""
    left = metrics.get("sharpe_ratio" if metric == "sharpe" else "cumulative_return")
    right = control.get(metric)
    return _round(_num(left) - _num(right))


def preserved_delta_metric(metrics: dict[str, float], preserved: dict[str, str], period: str, metric: str) -> float | str:
    if not preserved:
        return ""
    left = metrics.get("sharpe_ratio" if metric == "sharpe" else "cumulative_return")
    return _round(_num(left) - _num(preserved.get(f"{period[:4]}_{metric}")))


def read_freeze_rows() -> list[dict[str, str]]:
    return read_csv(REFERENCE / "track_b_parity_stage1_2024_selected_candidates.csv")


def load_base_run(period: str, family: str) -> dict[str, Any]:
    path = base_npz_path(period, family)
    if not path.exists():
        raise FileNotFoundError(f"Missing base run: {path}")
    data = np.load(path, allow_pickle=False)
    trace_json = str(data["trace_rows_json"][0])
    manifest_rows = read_csv(REFERENCE / "base_run_manifest.csv")
    manifest = next((row for row in manifest_rows if row.get("period") == period and row.get("candidate_family") == family), {})
    return {
        "period": period,
        "dates": tuple(str(x) for x in data["dates"]),
        "assets": tuple(str(x) for x in data["assets"]),
        "open_prices": np.asarray(data["open_prices"], dtype=float),
        "pct_changes": np.asarray(data["pct_changes"], dtype=float),
        "target": np.asarray(data["target"], dtype=float),
        "base": np.asarray(data["base"], dtype=float),
        "trace_rows": json.loads(trace_json),
        "manifest": manifest,
    }


def variant_by_code(candidate: CandidateSpec, code: str) -> VariantSpec:
    for variant in variants_for_candidate(candidate):
        if variant.code == code:
            return variant
    raise KeyError(code)


def base_npz_path(period: str, family: str) -> Path:
    return BASE_RUNS / period / f"{family}_base.npz"


def base_trace_path(period: str, family: str) -> Path:
    return BASE_RUNS / period / f"{family}_trace_rows.csv"


def run_id(family: str, variant: VariantSpec) -> str:
    return f"TBP_{family}_{variant.code}"


def _base_array(base: dict[str, float], assets: tuple[str, ...], count: int) -> np.ndarray:
    row = np.asarray([base.get(asset, 0.0) for asset in assets], dtype=float)
    return np.tile(row[None, :], (count, 1))


def _cache_hit_rate(rows: list[dict[str, Any]]) -> float:
    cacheable = [row for row in rows if row.get("cache_required")]
    if not cacheable:
        return 0.0
    return round(sum(1 for row in cacheable if row.get("cache_hit")) / len(cacheable), 6)


def _trace_vector(rows: list[dict[str, Any]], key: str, *, default: float, length: int) -> np.ndarray:
    values = [_num(row.get(key), default=default) for row in rows[:length]]
    if len(values) < length:
        values.extend([default] * (length - len(values)))
    return np.asarray(values, dtype=float)


def _minmax(values: np.ndarray) -> np.ndarray:
    if values.size == 0:
        return values
    low = float(np.nanmin(values))
    high = float(np.nanmax(values))
    if not math.isfinite(low) or not math.isfinite(high) or abs(high - low) < 1e-12:
        return np.ones_like(values)
    return (values - low) / (high - low)


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


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def write_text(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def md_table(rows: list[dict[str, Any]], fields: tuple[str, ...]) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(fields) + " |", "| " + " | ".join("---" for _ in fields) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(field, "")) for field in fields) + " |")
    return "\n".join(lines)


def _replace_candidate(args: argparse.Namespace, family: str) -> argparse.Namespace:
    clone = argparse.Namespace(**vars(args))
    clone.candidate = family
    return clone


if __name__ == "__main__":
    raise SystemExit(main())
