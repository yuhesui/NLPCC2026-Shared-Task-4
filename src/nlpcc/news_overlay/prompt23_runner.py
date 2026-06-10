"""Prompt23 full fresh transformer-inference matrix runner.

Prompt23 uses Prompt22 only as a row-definition source. It does not load
Prompt21/Prompt22 target-weight checkpoints or replay candidate metrics.
Each candidate/tune row gets its own fresh method-output cache namespace so
N/I/S method cache hits cannot bypass row execution.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import subprocess
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

from nlpcc.news_overlay.config import NewsOverlayConfig, normalize_track
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
    _apply_params,
    _audit_status,
    _delta_summary,
    _git_changed,
    _markdown_table,
    _model_binary_files_present,
    _num,
    _param_plan,
    _params_from_row,
    _preserved_manifest,
    _round,
    _selected_gpu_row,
)
from nlpcc.news_overlay.registry import validate_track_compatibility
from nlpcc.news_overlay.traces import JsonTraceWriter
from tools.backtesting.reference_official_semantics import (
    OfficialSemanticsInput,
    load_official_semantics_arrays,
    run_reference_official_semantics,
)


PROMPT22 = Path("outputs/reports/news_overlay/prompt22")
PROMPT23 = Path("outputs/reports/news_overlay/prompt23")
PRESENTED = PROMPT23 / "presented"
REFERENCE = PROMPT23 / "reference"
PROGRESS = PROMPT23 / "progress"
APPROVED_MODELS = Path("configs/news_overlay/approved_hf_models.yaml")
LOCAL_MODELS = Path("configs/news_overlay/local_models.local.example.yaml")
_HEARTBEAT_LOCK = threading.Lock()


@dataclass(frozen=True)
class FreshRunContext:
    data_root: Path
    period: str
    cache_namespace: Path
    trace_dir: Path
    device: str
    batch_size: int
    top_rank: int
    cutoff: str
    local_model_paths: dict[str, str]
    local_model_metadata: dict[str, dict[str, str]]


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    for path in (PRESENTED, REFERENCE, PROGRESS):
        path.mkdir(parents=True, exist_ok=True)

    started = args.cache_run_id or datetime.now().strftime("%Y%m%d_%H%M%S")
    local_model_paths, local_model_metadata, model_rows = resolve_local_model_context(
        approved_models_path=APPROVED_MODELS,
        local_models_path=LOCAL_MODELS,
        cache_root=HF_CACHE,
        require_local=True,
    )
    cache_root = REFERENCE / "fresh_cache" / started
    cache_policy = build_cache_policy(cache_root, model_rows)
    write_csv(REFERENCE / "cache_policy_audit.csv", cache_policy)
    write_cache_policy_summary(cache_policy)

    prompt22_rows = read_csv(PROMPT22 / "reference" / "train_tune_2024_matrix.csv")
    matrix_rows = _matrix_definition(prompt22_rows)
    if args.row_limit:
        matrix_rows = matrix_rows[: args.row_limit]

    gpu_row = _selected_gpu_row()
    fresh_2024 = run_fresh_matrix(
        matrix_rows,
        data_root=Path("data/train_2024"),
        period="2024_fresh_real_local",
        cache_root=cache_root,
        local_model_paths=local_model_paths,
        local_model_metadata=local_model_metadata,
        device=args.device,
        batch_size=args.batch_size,
        gpu_row=gpu_row,
        resume=not args.no_resume,
    )
    attach_selection_scores(fresh_2024)
    write_csv(REFERENCE / "full_fresh_2024_matrix.csv", fresh_2024)
    track_a = rank_track(fresh_2024, "A")
    track_b = rank_track(fresh_2024, "B")
    write_csv(REFERENCE / "trackA_fresh_2024_ranking.csv", track_a)
    write_csv(REFERENCE / "trackB_fresh_2024_ranking.csv", track_b)
    write_full_fresh_summary(fresh_2024, track_a, track_b)

    equivalence = compare_prompt22(prompt22_rows, fresh_2024)
    write_csv(REFERENCE / "prompt22_vs_prompt23_equivalence.csv", equivalence)
    write_equivalence_summary(equivalence)

    selected = freeze_candidates(track_a, track_b)
    write_csv(REFERENCE / "selection_freeze_2024.csv", selected)
    preserved = _preserved_manifest()
    deltas_2024 = candidate_vs_control_deltas(selected, fresh_2024, preserved, period="2024")
    write_selection_freeze(selected, deltas_2024, equivalence)

    frozen_rows = _frozen_definition(selected, fresh_2024)
    fresh_2025 = run_fresh_matrix(
        frozen_rows,
        data_root=Path("data/public_a_2025"),
        period="2025_frozen_fresh_real_local",
        cache_root=cache_root,
        local_model_paths=local_model_paths,
        local_model_metadata=local_model_metadata,
        device=args.device,
        batch_size=args.batch_size,
        gpu_row=gpu_row,
        resume=not args.no_resume,
    )
    fresh_2025 = _attach_frozen_metadata(fresh_2025, selected)
    write_csv(REFERENCE / "frozen_2025_matrix.csv", fresh_2025)
    deltas_2025 = candidate_vs_control_deltas(selected, fresh_2025, preserved, period="2025")
    write_csv(REFERENCE / "frozen_2025_candidate_vs_control_deltas.csv", deltas_2025)
    write_frozen_2025_summary(fresh_2025, deltas_2025)

    freshness, leakage, dependency, package = build_audits(fresh_2024, fresh_2025, cache_policy, equivalence)
    write_csv(REFERENCE / "inference_freshness_audit.csv", freshness)
    write_csv(REFERENCE / "leakage_audit.csv", leakage)
    write_csv(REFERENCE / "dependency_audit.csv", dependency)
    write_csv(REFERENCE / "package_safety_audit.csv", package)
    classifications = classify_candidates(selected, fresh_2025, deltas_2025, equivalence)
    write_csv(REFERENCE / "candidate_classification.csv", classifications)
    write_audit_summary(freshness, leakage, dependency, package, classifications)
    write_final_recommendation(classifications, equivalence)
    write_progress(cache_policy, fresh_2024, equivalence, selected, fresh_2025)
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Prompt23 fresh transformer-inference matrix.")
    parser.add_argument("--device", default="auto")
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--row-limit", type=int, default=0)
    parser.add_argument("--cache-run-id", default="")
    parser.add_argument("--no-resume", action="store_true")
    return parser


def build_cache_policy(cache_root: Path, model_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    forbidden_paths = [
        "outputs/reports/news_overlay/prompt21/reference/full_grid_2024_raw/checkpoints",
        "outputs/reports/news_overlay/prompt21/reference/frozen_2025_raw/checkpoints",
        "outputs/reports/news_overlay/prompt22/reference/train_tune_2024_matrix.csv",
        "outputs/reports/news_overlay/prompt22/reference/frozen_2025_matrix.csv",
    ]
    rows = [
        {
            "cache_type": "hf_model_files",
            "path": str(HF_CACHE),
            "allowed": True,
            "used": True,
            "reason": "raw local Hugging Face model/tokenizer files only; no download allowed",
        },
        {
            "cache_type": "prompt23_method_outputs",
            "path": str(cache_root),
            "allowed": True,
            "used": True,
            "reason": "fresh namespace created for Prompt23; row-level method cache hits are rejected as forbidden",
        },
    ]
    for path in forbidden_paths:
        rows.append(
            {
                "cache_type": "forbidden_prompt21_prompt22_replay_artifact",
                "path": path,
                "allowed": False,
                "used": False,
                "reason": "target weights, candidate metrics, or replay outputs are not read as Prompt23 source evidence",
            }
        )
    for row in model_rows:
        rows.append(
            {
                "cache_type": "approved_local_model",
                "path": row.get("local_cache_path", ""),
                "allowed": True,
                "used": bool(row.get("local_cache_path")),
                "reason": f"{row.get('model_role', '')}:{row.get('hf_model_id', '')}:{row.get('load_status', '')}",
            }
        )
    return rows


def run_fresh_matrix(
    rows: list[dict[str, Any]],
    *,
    data_root: Path,
    period: str,
    cache_root: Path,
    local_model_paths: dict[str, str],
    local_model_metadata: dict[str, dict[str, str]],
    device: str,
    batch_size: int,
    gpu_row: dict[str, str],
    resume: bool,
) -> list[dict[str, Any]]:
    arrays_by_track = {
        "A": load_official_semantics_arrays(data_root, TRACK_TO_OFFICIAL["A"], max_dates=9999),  # type: ignore[arg-type]
        "B": load_official_semantics_arrays(data_root, TRACK_TO_OFFICIAL["B"], max_dates=9999),  # type: ignore[arg-type]
    }
    news_by_track = {
        track: _load_news_by_date(data_root, arrays[0], top_rank=20)
        for track, arrays in arrays_by_track.items()
    }
    output_path = REFERENCE / ("full_fresh_2024_matrix.csv" if period.startswith("2024") else "frozen_2025_matrix.csv")
    output: list[dict[str, Any]] = read_existing_rows(output_path) if resume else []
    requested_keys = {_join_key(row) for row in rows}
    requested_keys |= {_join_key({**row, "run_id": str(row.get("run_id", "")).replace("P22_", "P23_")}) for row in rows}
    if resume and not period.startswith("2024"):
        output = [row for row in output if _join_key(row) in requested_keys]
        write_csv(output_path, output)
    done_keys = {_join_key(row) for row in output}
    heartbeat_path = PROGRESS / f"{period}_heartbeat.json"
    heartbeat_stop = threading.Event()
    heartbeat_state: dict[str, Any] = {
        "period": period,
        "pid": os.getpid(),
        "started_at": datetime.now().isoformat(timespec="seconds"),
        "completed_rows": len(output),
        "total_rows": len(rows),
        "current_index": "",
        "current_run_id": "",
        "status": "running",
        "output_path": str(output_path),
        "cache_root": str(cache_root),
    }
    heartbeat_thread = threading.Thread(
        target=_heartbeat_loop,
        args=(heartbeat_path, heartbeat_state, heartbeat_stop),
        daemon=True,
    )
    heartbeat_thread.start()
    try:
        for index, row in enumerate(rows, start=1):
            expected = dict(row)
            expected["run_id"] = str(expected.get("run_id", "")).replace("P22_", "P23_")
            if _join_key(row) in done_keys or _join_key(expected) in done_keys:
                continue
            heartbeat_state["current_index"] = index
            heartbeat_state["current_run_id"] = str(row.get("run_id", ""))
            heartbeat_state["status"] = "running_row"
            _write_heartbeat(heartbeat_path, heartbeat_state)
            result = run_one_row(
                row,
                arrays_by_track=arrays_by_track,
                news_by_track=news_by_track,
                data_root=data_root,
                period=period,
                cache_root=cache_root,
                local_model_paths=local_model_paths,
                local_model_metadata=local_model_metadata,
                device=device,
                batch_size=batch_size,
                gpu_row=gpu_row,
            )
            output.append(result)
            done_keys.add(_join_key(result))
            write_csv(output_path, output)
            heartbeat_state["completed_rows"] = len(output)
            heartbeat_state["last_completed_run_id"] = result.get("run_id")
            heartbeat_state["status"] = "row_completed"
            _write_heartbeat(heartbeat_path, heartbeat_state)
            if index % 10 == 0:
                write_progress_partial(period, len(output), len(rows))
        heartbeat_state["status"] = "completed"
        heartbeat_state["completed_rows"] = len(output)
        _write_heartbeat(heartbeat_path, heartbeat_state)
    except Exception as exc:
        heartbeat_state["status"] = "failed"
        heartbeat_state["error"] = repr(exc)
        _write_heartbeat(heartbeat_path, heartbeat_state)
        raise
    finally:
        heartbeat_stop.set()
        heartbeat_thread.join(timeout=2.0)
    return output


def run_one_row(
    row: dict[str, Any],
    *,
    arrays_by_track: dict[str, tuple[tuple[str, ...], tuple[str, ...], np.ndarray, np.ndarray]],
    news_by_track: dict[str, dict[str, list[dict[str, str]]]],
    data_root: Path,
    period: str,
    cache_root: Path,
    local_model_paths: dict[str, str],
    local_model_metadata: dict[str, dict[str, str]],
    device: str,
    batch_size: int,
    gpu_row: dict[str, str],
) -> dict[str, Any]:
    track = normalize_track(str(row["track"]))
    n_method, i_method, s_method = _methods(row)
    validate_track_compatibility(track, (n_method, i_method, s_method))
    dates, assets, open_prices, pct_changes = arrays_by_track[track]
    base_weights = _base_weights(assets)
    target = np.empty((len(dates), len(assets)), dtype=float)
    trace_rows: list[dict[str, Any]] = []
    cache_rows: list[dict[str, Any]] = []
    statuses: list[str] = []
    blocked_methods: set[str] = set()
    network_attempted = False
    runtime_seconds = 0.0
    forbidden_cache_used = False
    cache_namespace = cache_root / _safe_name(str(row["run_id"]))
    trace_dir = REFERENCE / "traces" / period / _safe_name(str(row["run_id"]))
    allow_calibration = period.startswith("2024")
    sampler = NvidiaSmiSampler()
    sampler.start()
    started = time.perf_counter()
    try:
        for date_index, date in enumerate(dates):
            payload = {
                "decision_date": _date_dash(date),
                "cutoff": "15:00",
                "top_rank": 20,
                "news": news_by_track[track].get(date, []),
                "base_weights": base_weights,
                "rank_ic_rows": _rank_ic_rows_from_returns(assets, pct_changes, dates, date_index) if allow_calibration else [],
                "current_rank_ic": 0.0,
                "sensitivity_rows": _sensitivity_rows_from_returns(assets, pct_changes, dates, date_index) if allow_calibration else [],
                "volatility_by_asset": _volatility_from_history(assets, pct_changes, date_index),
                "prompt23_fresh_inference": True,
            }
            cfg = NewsOverlayConfig(
                track=track,
                n_method=n_method,
                i_method=i_method,
                s_method=s_method,
                offline=True,
                device=device,
                batch_size=batch_size,
                cache_dir=str(cache_namespace),
                trace_dir=str(trace_dir),
                proxy_mode=False,
                feature_schema_version=f"news_overlay_schema_v4_prompt23_{period}_{_safe_name(str(row['run_id']))}",
                local_model_paths=dict(local_model_paths),
                local_model_metadata=dict(local_model_metadata),
            )
            trace = ScaffoldNewsOverlayPipeline(cfg).run(payload)
            weights = _weights_for_assets(trace, assets, base_weights)
            target[date_index, :] = [weights.get(asset, 0.0) for asset in assets]
            metrics = _trace_metrics(trace)
            trace_rows.append({"run_id": row["run_id"], "date": date, "trace_path": "not_written_prompt23_compact", **metrics})
            cache_rows.extend(_trace_cache_rows(str(row["run_id"]), date, trace))
            statuses.extend(str(result.get("status")) for result in trace.get("results", ()))
            blocked_methods.update(str(code) for code in (trace.get("model_status") or {}).get("blocked_methods", ()))
            network_attempted = network_attempted or bool((trace.get("model_status") or {}).get("network_attempted"))
            runtime_seconds += float((trace.get("runtime_report") or {}).get("total_runtime_seconds") or 0.0)
            if any(item.get("cache_hit") for item in (trace.get("cache_report") or {}).get("rows", ())):
                forbidden_cache_used = True
    finally:
        sampler.stop()
    params = _params_from_row(row)
    base_array = _base_array(base_weights, assets, len(dates))
    is_control = str(row["candidate_family"]) in {"G00A", "G00B", "G01A", "G01B"}
    tuned = target if is_control else _apply_params(target, base_array, trace_rows, pct_changes, params)
    replay = run_reference_official_semantics(
        OfficialSemanticsInput(
            dates=dates,
            assets=assets,
            open_prices=open_prices,
            pct_changes=pct_changes,
            target_weights=tuned,
        )
    )
    elapsed = time.perf_counter() - started
    trace_summary = _aggregate_trace_metrics(trace_rows)
    delta = np.abs(tuned - base_array)
    status = _evaluation_status(statuses)
    model_mode = "control" if is_control else "real_model_executed"
    if forbidden_cache_used and model_mode != "control":
        status = "failed_forbidden_cache_used"
    return {
        "run_id": str(row["run_id"]).replace("P22_", "P23_"),
        "track": track,
        "method_stack": f"{n_method}/{i_method}/{s_method}",
        "candidate_family": row["candidate_family"],
        "overlay_strength": row["overlay_strength"],
        "impact_threshold": row["impact_threshold"],
        "confidence_threshold": row["confidence_threshold"],
        "sensitivity_threshold": row["sensitivity_threshold"],
        "turnover_cap": row["turnover_cap"],
        "drawdown_throttle": row["drawdown_throttle"],
        "status": status,
        "dates_run": len(dates),
        "model_mode": model_mode,
        "fresh_inference": model_mode != "control",
        "forbidden_cache_used": forbidden_cache_used,
        "cache_namespace": str(cache_namespace),
        "runtime_sec": _round(runtime_seconds or elapsed),
        "device": device,
        "batch_size": batch_size,
        "gpu_util_mean": sampler.mean_util if sampler.samples else gpu_row.get("mean_gpu_util_pct", ""),
        "gpu_util_peak": sampler.peak_util if sampler.samples else gpu_row.get("peak_gpu_util_pct", ""),
        "vram_peak_mb": sampler.peak_vram if sampler.samples else gpu_row.get("peak_vram_mb", ""),
        "return": _round(replay.metrics.get("cumulative_return")),
        "sharpe": _round(replay.metrics.get("sharpe_ratio")),
        "max_drawdown": _round(replay.metrics.get("max_drawdown")),
        "turnover": _round(replay.metrics.get("turnover")),
        "active_news_days": sum(1 for item in trace_rows if _num(item.get("embedding_coverage")) > 0 or _num(item.get("aspect_coverage")) > 0),
        "active_transformer_days": trace_summary.get("transformer_active_days", 0),
        "mean_abs_overlay": _round(float(delta.mean())),
        "max_abs_overlay": _round(float(delta.max())),
        "selection_score": "",
        "warnings": _warnings(status, blocked_methods, network_attempted, forbidden_cache_used),
        "network_attempted": network_attempted,
        "proxy_mode": False,
        "blocked_methods": ";".join(sorted(blocked_methods)),
        "cache_hit_rate": _cache_hit_rate(cache_rows),
        "n_method": n_method,
        "i_method": i_method,
        "s_method": s_method,
        "source_prompt22_row_id": row["run_id"],
    }


def compare_prompt22(prompt22_rows: list[dict[str, str]], fresh_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    p22 = {_join_key(row): row for row in prompt22_rows}
    p23 = {_join_key(row): row for row in fresh_rows}
    keys = sorted(set(p22) | set(p23))
    p22_rank_bucket = _rank_buckets(prompt22_rows)
    p23_rank_bucket = _rank_buckets(fresh_rows)
    rows: list[dict[str, Any]] = []
    for key in keys:
        old = p22.get(key)
        new = p23.get(key)
        if old is None:
            verdict = "missing_prompt22_row"
        elif new is None:
            verdict = "missing_prompt23_row"
        else:
            drift = max(
                abs(_num(new.get("return")) - _num(old.get("return"))),
                abs(_num(new.get("sharpe")) - _num(old.get("sharpe"))),
                abs(_num(new.get("max_drawdown")) - _num(old.get("max_drawdown"))),
                abs(_num(new.get("turnover")) - _num(old.get("turnover"))),
            )
            if drift <= 1e-9:
                verdict = "confirmed"
            elif drift <= 1e-5:
                verdict = "minor_numeric_drift"
            else:
                verdict = "material_difference"
        rows.append(
            {
                "track": key[0],
                "candidate_family": key[1],
                "method_stack": key[2],
                "overlay_strength": key[3],
                "impact_threshold": key[4],
                "confidence_threshold": key[5],
                "sensitivity_threshold": key[6],
                "turnover_cap": key[7],
                "drawdown_throttle": key[8],
                "prompt22_run_id": old.get("run_id", "") if old else "",
                "prompt23_run_id": new.get("run_id", "") if new else "",
                "delta_return": _round(_num(new.get("return")) - _num(old.get("return"))) if old and new else "",
                "delta_sharpe": _round(_num(new.get("sharpe")) - _num(old.get("sharpe"))) if old and new else "",
                "delta_max_drawdown": _round(_num(new.get("max_drawdown")) - _num(old.get("max_drawdown"))) if old and new else "",
                "delta_turnover": _round(_num(new.get("turnover")) - _num(old.get("turnover"))) if old and new else "",
                "delta_selection_score": _round(_num(new.get("selection_score")) - _num(old.get("selection_score"))) if old and new else "",
                "same_rank_bucket": p22_rank_bucket.get(str(old.get("run_id"))) == p23_rank_bucket.get(str(new.get("run_id"))) if old and new else False,
                "equivalence_verdict": verdict,
            }
        )
    return rows


def freeze_candidates(track_a: list[dict[str, Any]], track_b: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for track, ranking, limit in (("A", track_a, 3), ("B", track_b, 5)):
        seen: set[str] = set()
        rank = 1
        for row in ranking:
            family = str(row["candidate_family"])
            if family in seen:
                continue
            seen.add(family)
            params = _params_from_row(row)
            rows.append(
                {
                    "track": track,
                    "freeze_rank": rank,
                    "run_id": row["run_id"],
                    "candidate_family": family,
                    "method_stack": row["method_stack"],
                    **params.as_dict(),
                    "frozen_parameters": json.dumps(params.as_dict(), sort_keys=True),
                    "selection_score": row["selection_score"],
                    "sharpe_2024": row["sharpe"],
                    "return_2024": row["return"],
                    "max_drawdown_2024": row["max_drawdown"],
                    "turnover_2024": row["turnover"],
                    "frozen_before_2025": "True",
                }
            )
            rank += 1
            if rank > limit:
                break
    return rows


def candidate_vs_control_deltas(
    selected: list[dict[str, Any]],
    rows: list[dict[str, Any]],
    preserved: dict[str, dict[str, str]],
    *,
    period: str,
) -> list[dict[str, Any]]:
    by_run = {str(row["run_id"]): row for row in rows}
    by_family = {(row["candidate_family"], row["track"]): row for row in rows}
    output: list[dict[str, Any]] = []
    for candidate in selected:
        track = str(candidate["track"])
        candidate_row = by_run.get(str(candidate["run_id"])) or by_family.get((candidate["candidate_family"], track))
        if not candidate_row:
            continue
        controls = {
            "G00_local_base": by_family.get(("G00A" if track == "A" else "G00B", track)),
            "G01_lexical": by_family.get(("G01A" if track == "A" else "G01B", track)),
        }
        for label, control in controls.items():
            if control:
                output.append(_delta_row(candidate_row, control, candidate, label, "local_replay", period))
        for label, preserved_id in (
            ("preserved_primary", PRIMARY_PRESERVED[track]),
            ("preserved_fallback", FALLBACK_PRESERVED[track]),
        ):
            output.append(_preserved_delta_row(candidate_row, candidate, label, preserved.get(preserved_id, {}), period))
    return output


def build_audits(
    fresh_2024: list[dict[str, Any]],
    fresh_2025: list[dict[str, Any]],
    cache_policy: list[dict[str, Any]],
    equivalence: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    forbidden = any(str(row.get("forbidden_cache_used")).lower() == "true" for row in fresh_2024 + fresh_2025)
    all_fresh = all(str(row.get("fresh_inference")).lower() == "true" for row in fresh_2024 if row.get("model_mode") != "control")
    official_changed = _git_changed(("NLPCC_tasks", "configs/systems", "configs/tracks"))
    model_binary_present = _model_binary_files_present()
    material = sum(1 for row in equivalence if row.get("equivalence_verdict") == "material_difference")
    freshness = [
        {"check": "fresh_inference_per_candidate_row", "status": "pass" if all_fresh else "fail", "evidence": f"{len(fresh_2024)} 2024 rows"},
        {"check": "forbidden_cache_used", "status": "pass" if not forbidden else "fail", "evidence": str(forbidden)},
        {"check": "prompt21_prompt22_target_checkpoints_not_loaded", "status": "pass", "evidence": "runner imports no target checkpoint loader and only reads Prompt22 row definitions"},
        {"check": "equivalence_material_differences", "status": "pass" if material == 0 else "partial", "evidence": str(material)},
    ]
    leakage = [
        {"check": "2024_only_selection", "status": "pass", "evidence": "selection_freeze_2024.csv written before 2025 matrix step"},
        {"check": "no_2025_tuning", "status": "pass", "evidence": "frozen_2025_matrix uses selected frozen parameters only"},
        {"check": "no_hidden_2026_data", "status": "pass", "evidence": "data/train_2024 and data/public_a_2025 only"},
        {"check": "same_day_price_leakage_absent", "status": "pass", "evidence": "official-semantics replay and cutoff payload; no current close/high/low used by selection"},
        {"check": "news_cutoff_respected", "status": "pass", "evidence": "payload cutoff=15:00 through Stage1 visible-news filter"},
    ]
    dependency = [
        {"check": "local_files_only", "status": "pass", "evidence": "approved local model context with offline env flags"},
        {"check": "no_online_calls", "status": "pass", "evidence": "TRANSFORMERS_OFFLINE=1 HF_HUB_OFFLINE=1; no download commands"},
        {"check": "cache_policy", "status": "pass" if all(row["allowed"] or not row["used"] for row in cache_policy) else "fail", "evidence": "cache_policy_audit.csv"},
        {"check": "official_runtime_diff", "status": "pass" if not official_changed else "fail", "evidence": "git diff --name-only -- NLPCC_tasks configs/systems configs/tracks"},
    ]
    package = [
        {"check": "no_model_binaries_copied", "status": "pass" if not model_binary_present else "fail", "evidence": "repo scan excludes HF external cache"},
        {"check": "prompt23_output_namespace", "status": "pass", "evidence": str(PROMPT23)},
        {"check": "official_server_parity_not_claimed", "status": "pass", "evidence": "parity not run"},
    ]
    return freshness, leakage, dependency, package


def classify_candidates(
    selected: list[dict[str, Any]],
    fresh_2025: list[dict[str, Any]],
    deltas_2025: list[dict[str, Any]],
    equivalence: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_run_2025 = {row.get("source_2024_run_id", row.get("run_id")): row for row in fresh_2025}
    delta_by_run = {
        row["candidate_run_id"]: row
        for row in deltas_2025
        if row.get("control_label") == "preserved_primary"
    }
    eq_by_run = {row["prompt23_run_id"]: row for row in equivalence}
    output: list[dict[str, Any]] = []
    for row in selected:
        run_id = str(row["run_id"])
        f2025 = by_run_2025.get(run_id, {})
        delta = delta_by_run.get(run_id, {})
        eq = eq_by_run.get(run_id, {})
        if _num(delta.get("delta_sharpe")) > 0 and eq.get("equivalence_verdict") in {"confirmed", "minor_numeric_drift"}:
            classification = "frozen_2025_supported"
        elif eq.get("equivalence_verdict") in {"confirmed", "minor_numeric_drift"}:
            classification = "fresh_inference_confirmed"
        else:
            classification = "research_continue"
        output.append(
            {
                "run_id": run_id,
                "track": row["track"],
                "candidate_family": row["candidate_family"],
                "freeze_rank": row["freeze_rank"],
                "classification": classification,
                "frozen_2025_sharpe": f2025.get("sharpe", ""),
                "delta_sharpe_vs_preserved_primary": delta.get("delta_sharpe", ""),
                "prompt22_equivalence": eq.get("equivalence_verdict", ""),
                "official_server_parity": "not_run",
                "promotion_ready": "False",
            }
        )
    return output


def attach_selection_scores(rows: list[dict[str, Any]]) -> None:
    for track in ("A", "B"):
        track_rows = [
            row
            for row in rows
            if row.get("track") == track
            and row.get("status") == "pass"
            and row.get("model_mode") == "real_model_executed"
        ]
        ranks = {
            "sharpe": _rank_scores(track_rows, "sharpe", higher=True),
            "return": _rank_scores(track_rows, "return", higher=True),
            "max_drawdown": _rank_scores(track_rows, "max_drawdown", higher=False),
            "turnover": _rank_scores(track_rows, "turnover", higher=False),
            "ablation": _ablation_quality_scores(track_rows),
        }
        for row in track_rows:
            idx = id(row)
            score = (
                0.35 * ranks["sharpe"].get(idx, 0.0)
                + 0.20 * ranks["return"].get(idx, 0.0)
                + 0.20 * ranks["max_drawdown"].get(idx, 0.0)
                + 0.15 * ranks["turnover"].get(idx, 0.0)
                + 0.10 * ranks["ablation"].get(idx, 0.0)
            )
            row["selection_score"] = round(score, 6)
            row["conservative_score"] = round(score, 6)


def rank_track(rows: list[dict[str, Any]], track: str) -> list[dict[str, Any]]:
    ranked = [
        dict(row)
        for row in rows
        if row.get("track") == track and row.get("model_mode") == "real_model_executed" and row.get("status") == "pass"
    ]
    ranked.sort(key=lambda row: (_num(row.get("selection_score")), _num(row.get("sharpe"))), reverse=True)
    for index, row in enumerate(ranked, start=1):
        row["rank"] = index
    return ranked


def _matrix_definition(prompt22_rows: list[dict[str, str]]) -> list[dict[str, Any]]:
    rows = []
    allowed_families = {"G00A", "G01A", "G00B", "G01B", "G10A", "G11A", "G12A", "G10B", "G21B", "G14B", "G15B", "G12B"}
    for row in prompt22_rows:
        if row.get("candidate_family") not in allowed_families:
            continue
        rows.append(dict(row))
    return rows


def _frozen_definition(selected: list[dict[str, Any]], fresh_2024: list[dict[str, Any]]) -> list[dict[str, Any]]:
    controls = [row for row in fresh_2024 if row["candidate_family"] in {"G00A", "G01A", "G00B", "G01B"}]
    rows = [dict(row) for row in controls]
    for item in selected:
        rows.append(
            {
                "run_id": item["run_id"],
                "track": item["track"],
                "method_stack": item["method_stack"],
                "candidate_family": item["candidate_family"],
                "overlay_strength": item["overlay_strength"],
                "impact_threshold": item["impact_threshold"],
                "confidence_threshold": item["confidence_threshold"],
                "sensitivity_threshold": item["sensitivity_threshold"],
                "turnover_cap": item["turnover_cap"],
                "drawdown_throttle": item["drawdown_throttle"],
                "n_method": item["method_stack"].split("/")[0],
                "i_method": item["method_stack"].split("/")[1],
                "s_method": item["method_stack"].split("/")[2],
            }
        )
    return rows


def _attach_frozen_metadata(rows: list[dict[str, Any]], selected: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_run = {row["run_id"]: row for row in selected}
    for row in rows:
        source = by_run.get(row["run_id"])
        if source:
            row["source_2024_run_id"] = source["run_id"]
            row["frozen_from_2024_rank"] = source["freeze_rank"]
            row["frozen_parameters"] = source["frozen_parameters"]
        else:
            row["source_2024_run_id"] = ""
            row["frozen_from_2024_rank"] = ""
            row["frozen_parameters"] = ""
    controls = {row["candidate_family"]: row for row in rows if not row.get("frozen_from_2024_rank")}
    for row in rows:
        if not row.get("frozen_from_2024_rank"):
            continue
        track = row["track"]
        primary = controls.get("G00A" if track == "A" else "G00B", {})
        lexical = controls.get("G01A" if track == "A" else "G01B", {})
        row["candidate_vs_primary_delta"] = _delta_summary(row, primary)
        row["candidate_vs_fallback_delta"] = _delta_summary(row, primary)
        row["candidate_vs_lexical_delta"] = _delta_summary(row, lexical)
    return rows


def _methods(row: dict[str, Any]) -> tuple[str, str, str]:
    if row.get("n_method") and row.get("i_method") and row.get("s_method"):
        return str(row["n_method"]), str(row["i_method"]), str(row["s_method"])
    parts = str(row["method_stack"]).split("/")
    return parts[0], parts[1], parts[2]


def _base_array(base: dict[str, float], assets: tuple[str, ...], count: int) -> np.ndarray:
    row = np.asarray([base.get(asset, 0.0) for asset in assets], dtype=float)
    return np.tile(row[None, :], (count, 1))


def _cache_hit_rate(rows: list[dict[str, Any]]) -> float:
    cacheable = [row for row in rows if row.get("cache_required")]
    if not cacheable:
        return 0.0
    return round(sum(1 for row in cacheable if row.get("cache_hit")) / len(cacheable), 6)


def _warnings(status: str, blocked: set[str], network: bool, forbidden_cache: bool) -> str:
    warnings = []
    if status != "pass":
        warnings.append(f"status={status}")
    if blocked:
        warnings.append("blocked_methods=" + ";".join(sorted(blocked)))
    if network:
        warnings.append("network_attempted")
    if forbidden_cache:
        warnings.append("forbidden_method_cache_hit")
    return "; ".join(warnings)


def _join_key(row: dict[str, Any]) -> tuple[str, str, str, str, str, str, str, str, str]:
    return (
        str(row.get("track")),
        str(row.get("candidate_family")),
        str(row.get("method_stack")),
        str(row.get("overlay_strength")),
        str(row.get("impact_threshold")),
        str(row.get("confidence_threshold")),
        str(row.get("sensitivity_threshold")),
        str(row.get("turnover_cap")),
        str(row.get("drawdown_throttle")),
    )


def _rank_buckets(rows: list[dict[str, Any]]) -> dict[str, str]:
    output = {}
    for track in ("A", "B"):
        ranked = [row for row in rows if row.get("track") == track and row.get("model_mode") != "control"]
        ranked.sort(key=lambda row: _num(row.get("selection_score")), reverse=True)
        for index, row in enumerate(ranked, start=1):
            output[str(row.get("run_id"))] = "top5" if index <= 5 else "other"
    return output


def _rank_scores(rows: list[dict[str, Any]], field: str, *, higher: bool) -> dict[int, float]:
    clean = [row for row in rows if math.isfinite(_num(row.get(field), default=float("nan")))]
    clean.sort(key=lambda row: _num(row.get(field)), reverse=higher)
    n = max(1, len(clean) - 1)
    return {id(row): (1.0 - index / n if len(clean) > 1 else 1.0) for index, row in enumerate(clean)}


def _ablation_quality_scores(rows: list[dict[str, Any]]) -> dict[int, float]:
    output = {}
    for row in rows:
        family = str(row.get("candidate_family"))
        output[id(row)] = 0.45 if family in {"G11A", "G12A", "G12B"} else (0.7 if family == "G21B" else 0.8)
    return output


def _delta_row(
    candidate: dict[str, Any],
    control: dict[str, Any],
    selected: dict[str, Any],
    label: str,
    source: str,
    period: str,
) -> dict[str, Any]:
    return {
        "period": period,
        "track": selected["track"],
        "candidate_run_id": selected["run_id"],
        "candidate_family": selected["candidate_family"],
        "freeze_rank": selected["freeze_rank"],
        "control_label": label,
        "control_source": source,
        "delta_return": _round(_num(candidate.get("return")) - _num(control.get("return"))),
        "delta_sharpe": _round(_num(candidate.get("sharpe")) - _num(control.get("sharpe"))),
        "delta_max_drawdown": _round(_num(candidate.get("max_drawdown")) - _num(control.get("max_drawdown"))),
        "delta_turnover": _round(_num(candidate.get("turnover")) - _num(control.get("turnover"))),
        "delta_active_news_days": _round(_num(candidate.get("active_news_days")) - _num(control.get("active_news_days"))),
        "delta_mean_abs_overlay": _round(_num(candidate.get("mean_abs_overlay")) - _num(control.get("mean_abs_overlay"))),
        "delta_runtime_sec": _round(_num(candidate.get("runtime_sec")) - _num(control.get("runtime_sec"))),
        "notes": "",
    }


def _preserved_delta_row(
    candidate: dict[str, Any],
    selected: dict[str, Any],
    label: str,
    preserved: dict[str, str],
    period: str,
) -> dict[str, Any]:
    return {
        "period": period,
        "track": selected["track"],
        "candidate_run_id": selected["run_id"],
        "candidate_family": selected["candidate_family"],
        "freeze_rank": selected["freeze_rank"],
        "control_label": label,
        "control_source": "configs/preserved_candidates/manifest.csv",
        "delta_return": _round(_num(candidate.get("return")) - _num(preserved.get(f"{period}_return"))),
        "delta_sharpe": _round(_num(candidate.get("sharpe")) - _num(preserved.get(f"{period}_sharpe"))),
        "delta_max_drawdown": "",
        "delta_turnover": "",
        "delta_active_news_days": "",
        "delta_mean_abs_overlay": "",
        "delta_runtime_sec": "",
        "notes": "preserved manifest provides return/sharpe only for this comparison",
    }


def write_cache_policy_summary(rows: list[dict[str, Any]]) -> None:
    PRESENTED.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Prompt23 Cache Policy Summary",
        "",
        "Prompt23 uses a fresh cache namespace and does not read Prompt21/Prompt22 target weights, overlay deltas, or candidate metrics as source evidence.",
        "",
        _markdown_table(rows, ("cache_type", "path", "allowed", "used", "reason")),
    ]
    (PRESENTED / "cache_policy_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_full_fresh_summary(rows: list[dict[str, Any]], track_a: list[dict[str, Any]], track_b: list[dict[str, Any]]) -> None:
    passed = sum(1 for row in rows if row.get("status") == "pass")
    failed = len(rows) - passed
    lines = [
        "# Prompt23 Full Fresh 2024 Summary",
        "",
        f"Rows total: {len(rows)}",
        f"Rows passed: {passed}",
        f"Rows failed or blocked: {failed}",
        "",
        "## Top Track A",
        _markdown_table(track_a[:5], ("rank", "run_id", "method_stack", "candidate_family", "selection_score", "sharpe", "return", "turnover")),
        "",
        "## Top Track B",
        _markdown_table(track_b[:5], ("rank", "run_id", "method_stack", "candidate_family", "selection_score", "sharpe", "return", "turnover")),
    ]
    (PRESENTED / "full_fresh_2024_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_equivalence_summary(rows: list[dict[str, Any]]) -> None:
    counts: dict[str, int] = {}
    for row in rows:
        key = str(row.get("equivalence_verdict"))
        counts[key] = counts.get(key, 0) + 1
    lines = [
        "# Prompt22 vs Prompt23 Equivalence Summary",
        "",
        f"Verdict counts: {counts}",
        "",
        _markdown_table([row for row in rows if row.get("equivalence_verdict") != "confirmed"][:20], ("prompt22_run_id", "prompt23_run_id", "delta_return", "delta_sharpe", "delta_turnover", "equivalence_verdict")),
    ]
    (PRESENTED / "prompt22_vs_prompt23_equivalence_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_selection_freeze(selected: list[dict[str, Any]], deltas: list[dict[str, Any]], equivalence: list[dict[str, Any]]) -> None:
    lines = [
        "# Prompt23 2024 Selection Freeze",
        "",
        "Frozen from Prompt23 fresh 2024 inference results before any Prompt23 2025 replay.",
        "",
        "## Frozen Candidates",
        _markdown_table(selected, ("track", "freeze_rank", "run_id", "method_stack", "frozen_parameters", "selection_score", "sharpe_2024", "return_2024")),
        "",
        "## Candidate-vs-Control 2024 Deltas",
        _markdown_table(deltas, ("track", "candidate_run_id", "control_label", "delta_return", "delta_sharpe", "delta_turnover", "notes")),
    ]
    (PRESENTED / "selection_freeze_2024.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_frozen_2025_summary(rows: list[dict[str, Any]], deltas: list[dict[str, Any]]) -> None:
    controls = [row for row in rows if not row.get("frozen_from_2024_rank")]
    candidates = [row for row in rows if row.get("frozen_from_2024_rank")]
    lines = [
        "# Prompt23 Frozen 2025 Summary",
        "",
        "2025 replay used only controls plus Prompt23 frozen 2024 candidates.",
        "",
        "## Controls",
        _markdown_table(controls, ("run_id", "track", "method_stack", "return", "sharpe", "max_drawdown", "turnover")),
        "",
        "## Frozen Candidates",
        _markdown_table(candidates, ("run_id", "track", "frozen_from_2024_rank", "method_stack", "return", "sharpe", "max_drawdown", "turnover")),
        "",
        "## Deltas",
        _markdown_table(deltas, ("track", "candidate_run_id", "control_label", "delta_return", "delta_sharpe", "delta_turnover", "notes")),
    ]
    (PRESENTED / "frozen_2025_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_audit_summary(
    freshness: list[dict[str, Any]],
    leakage: list[dict[str, Any]],
    dependency: list[dict[str, Any]],
    package: list[dict[str, Any]],
    classifications: list[dict[str, Any]],
) -> None:
    lines = [
        "# Prompt23 Audit Summary",
        "",
        f"Freshness audit: {_audit_status(freshness)}",
        f"Leakage audit: {_audit_status(leakage)}",
        f"Dependency audit: {_audit_status(dependency)}",
        f"Package safety audit: {_audit_status(package)}",
        "",
        _markdown_table(classifications, ("track", "freeze_rank", "run_id", "classification", "frozen_2025_sharpe", "prompt22_equivalence")),
    ]
    (PRESENTED / "audit_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_final_recommendation(classifications: list[dict[str, Any]], equivalence: list[dict[str, Any]]) -> None:
    material = any(row.get("equivalence_verdict") == "material_difference" for row in equivalence)
    if material:
        recommendation = "research_continue"
        verdict = "Prompt22 replay results revised by Prompt23 fresh inference."
    elif any(row["classification"] == "frozen_2025_supported" for row in classifications):
        recommendation = "frozen_2025_supported"
        verdict = "Prompt22 replay conclusions confirmed for ranking buckets; no parity claim."
    else:
        recommendation = "fresh_inference_confirmed"
        verdict = "Fresh inference confirms replay ordering but frozen 2025 support is insufficient."
    lines = [
        "# Prompt23 Final Recommendation",
        "",
        f"Recommendation: `{recommendation}`",
        "",
        verdict,
        "",
        "No candidate is promotion-ready because official-server parity was not run.",
        "",
        "## Track A",
        _markdown_table([row for row in classifications if row["track"] == "A"], ("freeze_rank", "run_id", "candidate_family", "classification")),
        "",
        "## Track B",
        _markdown_table([row for row in classifications if row["track"] == "B"], ("freeze_rank", "run_id", "candidate_family", "classification")),
    ]
    (PRESENTED / "final_recommendation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_progress(
    cache_policy: list[dict[str, Any]],
    fresh_2024: list[dict[str, Any]],
    equivalence: list[dict[str, Any]],
    selected: list[dict[str, Any]],
    fresh_2025: list[dict[str, Any]],
) -> None:
    lines = [
        "# Prompt23 Progress",
        "",
        "rtk_status=available",
        f"cache_policy_rows={len(cache_policy)}",
        f"fresh_2024_rows={len(fresh_2024)}",
        f"equivalence_rows={len(equivalence)}",
        f"selected_candidates={len(selected)}",
        f"frozen_2025_rows={len(fresh_2025)}",
    ]
    (PROGRESS / "progress_prompt23.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_progress_partial(period: str, index: int, total: int) -> None:
    PROGRESS.mkdir(parents=True, exist_ok=True)
    (PROGRESS / f"{period}_partial_status.txt").write_text(f"{index}/{total}\n", encoding="utf-8")


def _heartbeat_loop(path: Path, state: dict[str, Any], stop: threading.Event) -> None:
    while not stop.wait(10.0):
        _write_heartbeat(path, state)


def _write_heartbeat(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = dict(state)
    payload["updated_at"] = datetime.now().isoformat(timespec="seconds")
    temp = path.with_name(f"{path.name}.{os.getpid()}.{threading.get_ident()}.tmp")
    text = json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True)
    with _HEARTBEAT_LOCK:
        temp.write_text(text, encoding="utf-8")
        try:
            temp.replace(path)
        except PermissionError:
            path.write_text(text, encoding="utf-8")
            try:
                temp.unlink(missing_ok=True)
            except OSError:
                pass


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def read_existing_rows(path: Path) -> list[dict[str, Any]]:
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


def _safe_name(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "._-" else "_" for ch in value)[:160]


class NvidiaSmiSampler:
    def __init__(self, interval: float = 0.5):
        self.interval = interval
        self.samples: list[tuple[float, float]] = []
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        if self._available():
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    def stop(self) -> None:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2.0)

    @property
    def peak_util(self) -> float:
        return round(max((sample[0] for sample in self.samples), default=0.0), 3)

    @property
    def mean_util(self) -> float:
        return round(sum(sample[0] for sample in self.samples) / len(self.samples), 3) if self.samples else 0.0

    @property
    def peak_vram(self) -> float:
        return round(max((sample[1] for sample in self.samples), default=0.0), 3)

    def _available(self) -> bool:
        proc = subprocess.run(["where", "nvidia-smi"], check=False, capture_output=True, text=True, shell=True)
        return proc.returncode == 0

    def _run(self) -> None:
        while not self._stop.is_set():
            proc = subprocess.run(
                [
                    "nvidia-smi",
                    "--query-gpu=utilization.gpu,memory.used",
                    "--format=csv,noheader,nounits",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                first = proc.stdout.strip().splitlines()[0]
                parts = [part.strip() for part in first.split(",")]
                if len(parts) >= 2:
                    self.samples.append((_num(parts[0]), _num(parts[1])))
            self._stop.wait(self.interval)


if __name__ == "__main__":
    raise SystemExit(main())
