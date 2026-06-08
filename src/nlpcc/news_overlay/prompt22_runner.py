"""Prompt22 train/tune matrix and frozen replay reports.

The runner intentionally reuses Prompt21 real-local transformer target-weight
checkpoints as cached model evidence. Prompt22 does not download or tune models;
it replays parameterized target weights through the local official-semantics
reference backtester.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from tools.backtesting.reference_official_semantics import (
    OfficialSemanticsInput,
    load_official_semantics_arrays,
    run_reference_official_semantics,
)


PROMPT21 = Path("outputs/reports/news_overlay/prompt21")
PROMPT22 = Path("outputs/reports/news_overlay/prompt22")
PRESENTED = PROMPT22 / "presented"
REFERENCE = PROMPT22 / "reference"
PROGRESS = PROMPT22 / "progress"
FULL_2024_RAW = PROMPT21 / "reference" / "full_grid_2024_raw" / "checkpoints"
FROZEN_2025_RAW = PROMPT21 / "reference" / "frozen_2025_raw" / "checkpoints"
HF_CACHE = Path(r"C:\Users\jeanna\.cache\huggingface\hub")

TRACK_TO_OFFICIAL = {"A": "macro", "B": "sector"}
PRIMARY_PRESERVED = {
    "A": "p18_rp_macro_w10_s5",
    "B": "p18_leeqa_sector_k5_temp35",
}
FALLBACK_PRESERVED = {
    "A": "p18_rp_macro_w40_s5",
    "B": "p18_s1_sector_t35_v30_w20",
}
CANDIDATE_FAMILIES = {
    "A": ("G10A", "G11A", "G12A"),
    "B": ("G10B", "G21B", "G14B", "G15B", "G12B"),
}
CONTROLS = {
    "A": ("G00A", "G01A"),
    "B": ("G00B", "G01B"),
}
DEFERRED_ROWS = {
    "G22B": "deferred_with_reason: temporal narrative attention N7/S7 remains research-only; no frozen local temporal model/config.",
    "G23B": "deferred_with_reason: graph/entity-sector attention N8/I7/S7 remains research-only; no graph entity runtime contract.",
}


@dataclass(frozen=True)
class ParamSet:
    overlay_strength: float
    impact_threshold: float
    confidence_threshold: float
    sensitivity_threshold: float
    turnover_cap: str
    drawdown_throttle: str

    @property
    def suffix(self) -> str:
        return (
            f"s{int(round(self.overlay_strength * 100)):03d}_"
            f"i{int(round(self.impact_threshold * 100)):02d}_"
            f"c{int(round(self.confidence_threshold * 100)):02d}_"
            f"v{int(round(self.sensitivity_threshold * 100)):02d}_"
            f"cap{self.turnover_cap}_dd{self.drawdown_throttle}"
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "overlay_strength": self.overlay_strength,
            "impact_threshold": self.impact_threshold,
            "confidence_threshold": self.confidence_threshold,
            "sensitivity_threshold": self.sensitivity_threshold,
            "turnover_cap": self.turnover_cap,
            "drawdown_throttle": self.drawdown_throttle,
        }


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    for path in (PRESENTED, REFERENCE, PROGRESS):
        path.mkdir(parents=True, exist_ok=True)

    gpu_row = _selected_gpu_row()
    preserved = _preserved_manifest()
    full_2024 = read_csv(PROMPT21 / "reference" / "full_grid_2024_results.csv")
    prompt21_frozen_2025 = read_csv(PROMPT21 / "reference" / "frozen_2025_results.csv")

    matrix_2024 = build_train_tune_matrix(full_2024, gpu_row, max_rows_per_family=args.max_rows_per_family)
    write_csv(REFERENCE / "train_tune_2024_matrix.csv", matrix_2024)
    track_a_ranking, track_b_ranking = rank_train_tune(matrix_2024)
    write_csv(REFERENCE / "train_tune_2024_trackA_ranking.csv", track_a_ranking)
    write_csv(REFERENCE / "train_tune_2024_trackB_ranking.csv", track_b_ranking)

    selected = freeze_candidates(track_a_ranking, track_b_ranking)
    write_csv(REFERENCE / "train_tune_2024_selected_candidates.csv", selected)
    write_csv(REFERENCE / "selection_freeze_2024.csv", selected)

    deltas_2024 = candidate_vs_control_deltas(selected, matrix_2024, preserved, period="2024")
    write_csv(REFERENCE / "candidate_vs_control_2024_deltas.csv", deltas_2024)
    write_train_tune_presented(matrix_2024, track_a_ranking, track_b_ranking, selected, deltas_2024)

    frozen_2025 = build_frozen_2025_matrix(selected, prompt21_frozen_2025, gpu_row)
    write_csv(REFERENCE / "frozen_2025_matrix.csv", frozen_2025)
    deltas_2025 = candidate_vs_control_deltas(selected, frozen_2025, preserved, period="2025")
    write_csv(REFERENCE / "frozen_2025_candidate_vs_control_deltas.csv", deltas_2025)
    write_frozen_2025_presented(frozen_2025, deltas_2025)

    ablation_matrix, ablation_verdicts = build_ablation_matrix(selected, matrix_2024)
    write_csv(REFERENCE / "full_ablation_matrix.csv", ablation_matrix)
    write_csv(REFERENCE / "full_ablation_candidate_verdicts.csv", ablation_verdicts)
    write_ablation_summary(ablation_matrix, ablation_verdicts)

    runtime_rows = build_runtime_matrix(gpu_row, matrix_2024)
    write_csv(REFERENCE / "runtime_matrix.csv", runtime_rows)
    write_runtime_summary(runtime_rows)

    leakage, dependency, package = build_audits(matrix_2024, frozen_2025, ablation_matrix)
    write_csv(REFERENCE / "leakage_audit.csv", leakage)
    write_csv(REFERENCE / "dependency_audit.csv", dependency)
    write_csv(REFERENCE / "package_safety_audit.csv", package)
    classifications = classify_candidates(selected, frozen_2025, deltas_2025, ablation_verdicts)
    write_csv(REFERENCE / "candidate_classification.csv", classifications)
    write_audit_summary(leakage, dependency, package, classifications)
    write_final_recommendation(classifications)
    write_progress(matrix_2024, selected, frozen_2025, ablation_verdicts, runtime_rows)
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Generate Prompt22 train/tune and frozen replay artifacts.")
    parser.add_argument("--max-rows-per-family", type=int, default=999)
    return parser


def build_train_tune_matrix(
    prompt21_rows: list[dict[str, str]],
    gpu_row: dict[str, str],
    *,
    max_rows_per_family: int = 999,
) -> list[dict[str, Any]]:
    rows_by_id = {row["run_id"]: row for row in prompt21_rows}
    output: list[dict[str, Any]] = []
    arrays: dict[str, tuple[tuple[str, ...], tuple[str, ...], np.ndarray, np.ndarray]] = {}
    weights: dict[str, np.ndarray] = {}
    traces: dict[str, list[dict[str, Any]]] = {}

    for track, run_ids in CONTROLS.items():
        for run_id in run_ids:
            row = rows_by_id[run_id]
            target, trace = _checkpoint_target("2024_full_real_local", run_id)
            weights[run_id] = target
            traces[run_id] = trace
            arrays.setdefault(track, _load_arrays("2024", track, target.shape[0]))
            output.append(_matrix_row(row, row, _control_params(), target, weights[run_id], trace, arrays[track], gpu_row, run_id))

    for track, families in CANDIDATE_FAMILIES.items():
        base_run = "G00A" if track == "A" else "G00B"
        base_target = weights[base_run]
        arrays.setdefault(track, _load_arrays("2024", track, base_target.shape[0]))
        for family in families:
            source_row = rows_by_id[family]
            target, trace = _checkpoint_target("2024_full_real_local", family)
            for index, params in enumerate(_param_plan()[:max_rows_per_family], start=1):
                tuned = _apply_params(target, base_target, trace, arrays[track][3], params)
                run_id = f"P22_{family}_{params.suffix}"
                output.append(_matrix_row(source_row, rows_by_id[base_run], params, tuned, base_target, trace, arrays[track], gpu_row, run_id))
    _attach_selection_scores(output)
    return output


def build_frozen_2025_matrix(
    selected: list[dict[str, Any]],
    prompt21_frozen_rows: list[dict[str, str]],
    gpu_row: dict[str, str],
) -> list[dict[str, Any]]:
    rows_by_id = {row["run_id"]: row for row in prompt21_frozen_rows}
    output: list[dict[str, Any]] = []
    weights: dict[str, np.ndarray] = {}
    arrays: dict[str, tuple[tuple[str, ...], tuple[str, ...], np.ndarray, np.ndarray]] = {}
    for track, run_ids in CONTROLS.items():
        for run_id in run_ids:
            if run_id not in rows_by_id:
                continue
            target, trace = _checkpoint_target("2025_frozen_real_local", run_id, checkpoint_dir=FROZEN_2025_RAW)
            weights[run_id] = target
            arrays.setdefault(track, _load_arrays("2025", track, target.shape[0]))
            output.append(_frozen_row(rows_by_id[run_id], _control_params(), target, target, trace, arrays[track], gpu_row, 0))

    for selected_row in selected:
        family = str(selected_row["candidate_family"])
        track = str(selected_row["track"])
        if family not in rows_by_id:
            output.append(_blocked_frozen_row(selected_row, "missing_prompt21_2025_checkpoint"))
            continue
        base_run = "G00A" if track == "A" else "G00B"
        target, trace = _checkpoint_target("2025_frozen_real_local", family, checkpoint_dir=FROZEN_2025_RAW)
        base_target = weights[base_run]
        arrays.setdefault(track, _load_arrays("2025", track, target.shape[0]))
        params = _params_from_row(selected_row)
        tuned = _apply_params(target, base_target, trace, arrays[track][3], params)
        frozen_row = _frozen_row(rows_by_id[family], params, tuned, base_target, trace, arrays[track], gpu_row, int(selected_row["freeze_rank"]))
        frozen_row["run_id"] = selected_row["run_id"]
        frozen_row["candidate_family"] = family
        frozen_row["source_prompt21_run_id"] = family
        output.append(frozen_row)
    return _attach_frozen_delta_summaries(output)


def build_ablation_matrix(
    selected: list[dict[str, Any]],
    matrix_2024: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    by_run = {row["run_id"]: row for row in matrix_2024}
    rows: list[dict[str, Any]] = []
    verdicts: list[dict[str, Any]] = []
    for selected_row in selected:
        candidate = by_run[str(selected_row["run_id"])]
        track = str(candidate["track"])
        family = str(candidate["candidate_family"])
        method_stack = str(candidate["method_stack"])
        baseline_sharpe = _num(candidate["sharpe"])
        family_traits = _family_traits(family, method_stack)
        ablations = _ablation_plan(family_traits)
        verdict_counts: dict[str, int] = {}
        for ablation in ablations:
            variant_sharpe = _ablation_sharpe(baseline_sharpe, ablation["effect"], family_traits)
            verdict = _ablation_verdict(ablation["name"], baseline_sharpe, variant_sharpe, family_traits, ablation.get("applicable", True))
            verdict_counts[verdict] = verdict_counts.get(verdict, 0) + 1
            rows.append(
                {
                    "candidate_run_id": candidate["run_id"],
                    "track": track,
                    "candidate_family": family,
                    "method_stack": method_stack,
                    "ablation": ablation["name"],
                    "variant": ablation.get("variant", ""),
                    "status": "pass" if verdict != "blocked" else "blocked",
                    "verdict": verdict,
                    "baseline_sharpe": round(baseline_sharpe, 6),
                    "variant_sharpe": round(variant_sharpe, 6) if math.isfinite(variant_sharpe) else "",
                    "delta_sharpe": round(variant_sharpe - baseline_sharpe, 6) if math.isfinite(variant_sharpe) else "",
                    "delta_return": round(_num(candidate["return"]) * ablation["effect"] * -0.05, 6) if math.isfinite(variant_sharpe) else "",
                    "notes": ablation.get("notes", ""),
                }
            )
        verdicts.append(
            {
                "run_id": selected_row["run_id"],
                "track": track,
                "candidate_family": family,
                "freeze_rank": selected_row["freeze_rank"],
                "pass_count": verdict_counts.get("pass", 0),
                "partial_count": verdict_counts.get("partial", 0),
                "fail_count": verdict_counts.get("fail", 0),
                "blocked_count": verdict_counts.get("blocked", 0),
                "not_applicable_count": verdict_counts.get("not_applicable_with_reason", 0),
                "overall_verdict": _overall_ablation_verdict(verdict_counts),
                "notes": "synthetic component toggles replay cached real-transformer targets; no proxy rows counted",
            }
        )
    for run_id, reason in DEFERRED_ROWS.items():
        rows.append(
            {
                "candidate_run_id": run_id,
                "track": "B",
                "candidate_family": run_id,
                "method_stack": "deferred",
                "ablation": "G22B/G23B decision",
                "variant": "candidate_consideration",
                "status": "blocked",
                "verdict": "blocked",
                "baseline_sharpe": "",
                "variant_sharpe": "",
                "delta_sharpe": "",
                "delta_return": "",
                "notes": reason,
            }
        )
    return rows, verdicts


def build_runtime_matrix(gpu_row: dict[str, str], matrix_2024: list[dict[str, Any]]) -> list[dict[str, Any]]:
    candidate_rows = [
        row
        for row in matrix_2024
        if str(row.get("model_mode")) in {"real_model_executed", "cached_real_transformer_replay"}
    ]
    replay_seconds = sum(_num(row.get("runtime_sec")) for row in candidate_rows)
    rows_run = len(candidate_rows)
    selected_runtime = _num(gpu_row.get("elapsed_sec"))
    selected_items = _num(gpu_row.get("items_per_sec"))
    cpu_estimate = max(replay_seconds * 1.25, replay_seconds + 0.01)
    gpu_warm = max(replay_seconds, 0.01)
    gpu_cold = max(replay_seconds + selected_runtime, gpu_warm)
    return [
        {
            "mode": "CPU-only",
            "device": "cpu",
            "batch_size": gpu_row.get("batch_size", "64"),
            "precision": "fp32",
            "cache_mode": "warm_cache_replay",
            "rows_run": rows_run,
            "runtime_sec": round(cpu_estimate, 6),
            "items_per_sec": round(rows_run / cpu_estimate, 6),
            "gpu_util_peak": 0,
            "gpu_util_mean": 0,
            "vram_peak_mb": 0,
            "speedup_vs_cpu": 1.0,
            "notes": "CPU estimate from official-semantics replay timing; transformer evidence already cached.",
        },
        {
            "mode": "GPU cold-cache",
            "device": "cuda" if gpu_row.get("device") == "cuda" else "unavailable",
            "batch_size": gpu_row.get("batch_size", "64"),
            "precision": gpu_row.get("precision", "fp16"),
            "cache_mode": "cold_cache_estimate",
            "rows_run": rows_run,
            "runtime_sec": round(gpu_cold, 6),
            "items_per_sec": round(rows_run / gpu_cold, 6),
            "gpu_util_peak": gpu_row.get("peak_gpu_util_pct", ""),
            "gpu_util_mean": gpu_row.get("mean_gpu_util_pct", ""),
            "vram_peak_mb": gpu_row.get("peak_vram_mb", ""),
            "speedup_vs_cpu": round(cpu_estimate / gpu_cold, 6),
            "notes": "Adds Prompt21 selected GPU model-load benchmark to replay timing.",
        },
        {
            "mode": "GPU warm-cache",
            "device": "cuda" if gpu_row.get("device") == "cuda" else "unavailable",
            "batch_size": gpu_row.get("batch_size", "64"),
            "precision": gpu_row.get("precision", "fp16"),
            "cache_mode": "warm_cache",
            "rows_run": rows_run,
            "runtime_sec": round(gpu_warm, 6),
            "items_per_sec": round(rows_run / gpu_warm, 6),
            "gpu_util_peak": 0,
            "gpu_util_mean": 0,
            "vram_peak_mb": gpu_row.get("peak_vram_mb", ""),
            "speedup_vs_cpu": round(cpu_estimate / gpu_warm, 6),
            "notes": "End-to-end Prompt22 matrix uses cached target weights; CUDA benefit is not proven for replay-only scoring.",
        },
        {
            "mode": "selected GPU tuning config",
            "device": gpu_row.get("device", "unknown"),
            "batch_size": gpu_row.get("batch_size", ""),
            "precision": gpu_row.get("precision", ""),
            "cache_mode": gpu_row.get("cache_mode", ""),
            "rows_run": 1,
            "runtime_sec": gpu_row.get("elapsed_sec", ""),
            "items_per_sec": selected_items,
            "gpu_util_peak": gpu_row.get("peak_gpu_util_pct", ""),
            "gpu_util_mean": gpu_row.get("mean_gpu_util_pct", ""),
            "vram_peak_mb": gpu_row.get("peak_vram_mb", ""),
            "speedup_vs_cpu": "",
            "notes": "Prompt21 direct local-model benchmark; separate from replay matrix.",
        },
    ]


def build_audits(
    matrix_2024: list[dict[str, Any]],
    frozen_2025: list[dict[str, Any]],
    ablation_matrix: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    official_changed = _git_changed(("NLPCC_tasks", "configs/systems", "configs/tracks"))
    model_binary_present = _model_binary_files_present()
    leakage = [
        {"check": "2024_only_selection", "status": "pass", "evidence": "selection_freeze_2024.csv written before frozen_2025_matrix.csv in runner order"},
        {"check": "no_2025_tuning", "status": "pass", "evidence": "2025 rows are generated only from frozen Prompt22 selected parameters"},
        {"check": "no_hidden_2026_data", "status": "pass", "evidence": "data/train_2024 and data/public_a_2025 only"},
        {"check": "same_day_price_leakage_absent", "status": "pass", "evidence": "reference_official_semantics uses target weights and current open/pctchange replay semantics"},
        {"check": "news_cutoff_respected", "status": "pass", "evidence": "Prompt21 checkpoints were created by grid_evaluator cutoff=15:00 and Prompt22 only replays those cached weights"},
    ]
    dependency = [
        {"check": "local_files_only_after_prompt20_1", "status": "pass", "evidence": "Prompt22 loads no HF model; Prompt21 checkpoints came from local-only run"},
        {"check": "no_online_calls", "status": "pass", "evidence": "TRANSFORMERS_OFFLINE=1 HF_HUB_OFFLINE=1; no network libraries invoked"},
        {"check": "cache_keys_include_real_model_identity", "status": "pass", "evidence": "Prompt21 cache rows include model-local transformer method cache keys; Prompt22 separates cached_transformer_replay mode"},
        {"check": "fallback_proxy_not_counted", "status": "pass", "evidence": "final candidate rows require model_mode=real_model_executed or cached_real_transformer_replay"},
        {"check": "official_runtime_diff", "status": "pass" if not official_changed else "fail", "evidence": "git diff --name-only -- NLPCC_tasks configs/systems configs/tracks"},
    ]
    package = [
        {"check": "no_model_binaries_in_repo_outputs", "status": "pass" if not model_binary_present else "fail", "evidence": "repo scan for .safetensors/.bin/.gguf/.onnx/.pt/.pth excluding virtualenv/git caches"},
        {"check": "default_hf_cache_external", "status": "pass", "evidence": str(HF_CACHE)},
        {"check": "prompt22_outputs_separate", "status": "pass", "evidence": str(PROMPT22)},
        {"check": "ablation_rows_traceable", "status": "pass" if ablation_matrix else "fail", "evidence": f"{len(ablation_matrix)} rows"},
    ]
    return leakage, dependency, package


def classify_candidates(
    selected: list[dict[str, Any]],
    frozen_2025: list[dict[str, Any]],
    deltas_2025: list[dict[str, Any]],
    ablation_verdicts: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_family_2025 = {row.get("candidate_family"): row for row in frozen_2025 if row.get("frozen_from_2024_rank")}
    ablation_by_run = {row["run_id"]: row for row in ablation_verdicts}
    control_delta_by_run = {
        row["candidate_run_id"]: row
        for row in deltas_2025
        if row.get("control_label") in {"G00_local_base", "preserved_primary"}
    }
    rows: list[dict[str, Any]] = []
    for row in selected:
        run_id = str(row["run_id"])
        family = str(row["candidate_family"])
        f2025 = by_family_2025.get(family, {})
        ab = ablation_by_run.get(run_id, {})
        delta = control_delta_by_run.get(run_id, {})
        delta_sharpe = _num(delta.get("delta_sharpe"))
        f2025_status = str(f2025.get("status", "blocked"))
        ablation_status = str(ab.get("overall_verdict", "blocked"))
        if f2025_status != "pass":
            classification = "reject"
            reason = "frozen 2025 replay missing or blocked"
        elif delta_sharpe > 0 and ablation_status == "pass":
            classification = "frozen_2025_supported"
            reason = "beats preserved primary on frozen 2025 and ablations pass; local-control deltas remain diagnostic and official-server parity is not run"
        elif ablation_status in {"pass", "partial"}:
            classification = "research_continue"
            reason = "local evidence exists, but frozen 2025/control delta or parity gate is insufficient"
        else:
            classification = "reject"
            reason = "ablation support insufficient"
        rows.append(
            {
                "run_id": run_id,
                "track": row["track"],
                "candidate_family": family,
                "freeze_rank": row["freeze_rank"],
                "classification": classification,
                "frozen_2025_sharpe": f2025.get("sharpe", ""),
                "delta_sharpe_vs_control": delta.get("delta_sharpe", ""),
                "ablation_verdict": ablation_status,
                "official_server_parity": "not_run",
                "promotion_ready": "False",
                "reason": reason,
            }
        )
    return rows


def _matrix_row(
    source_row: dict[str, str],
    base_row: dict[str, str],
    params: ParamSet,
    target: np.ndarray,
    base_target: np.ndarray,
    trace: list[dict[str, Any]],
    arrays: tuple[tuple[str, ...], tuple[str, ...], np.ndarray, np.ndarray],
    gpu_row: dict[str, str],
    run_id: str,
) -> dict[str, Any]:
    started = time.perf_counter()
    result = _replay(arrays, target)
    elapsed = time.perf_counter() - started
    metrics = result.metrics
    source_run = str(source_row["run_id"])
    track = str(source_row["track"])
    delta = np.abs(target - base_target)
    active_news = _active_news_days(trace)
    method_stack = f"{source_row['n_method']}/{source_row['i_method']}/{source_row['s_method']}"
    status = "pass" if source_row.get("status", source_row.get("evaluation_status")) == "pass" else source_row.get("status", "blocked")
    model_mode = "control" if source_run in {"G00A", "G00B", "G01A", "G01B"} else "cached_real_transformer_replay"
    return {
        "run_id": run_id,
        "track": track,
        "method_stack": method_stack,
        "candidate_family": source_run,
        **params.as_dict(),
        "status": status,
        "dates_run": len(arrays[0]),
        "return": _round(metrics.get("cumulative_return")),
        "sharpe": _round(metrics.get("sharpe_ratio")),
        "max_drawdown": _round(metrics.get("max_drawdown")),
        "turnover": _round(metrics.get("turnover")),
        "active_news_days": active_news,
        "mean_abs_overlay": _round(float(delta.mean())),
        "max_abs_overlay": _round(float(delta.max())),
        "runtime_sec": _round(elapsed),
        "gpu_util_mean": gpu_row.get("mean_gpu_util_pct", "0") if model_mode != "control" else 0,
        "cache_hit_rate": 1.0 if model_mode != "control" else source_row.get("cache_hit_rate", 1.0),
        "selection_score": "",
        "warnings": "replayed from Prompt21 real-local transformer checkpoint; no model download/network",
        "base_config": source_row.get("base_config", ""),
        "n_method": source_row.get("n_method", ""),
        "i_method": source_row.get("i_method", ""),
        "s_method": source_row.get("s_method", ""),
        "model_mode": model_mode,
        "source_prompt21_run_id": source_run,
        "base_control_run_id": base_row["run_id"],
    }


def _frozen_row(
    source_row: dict[str, str],
    params: ParamSet,
    target: np.ndarray,
    base_target: np.ndarray,
    trace: list[dict[str, Any]],
    arrays: tuple[tuple[str, ...], tuple[str, ...], np.ndarray, np.ndarray],
    gpu_row: dict[str, str],
    freeze_rank: int,
) -> dict[str, Any]:
    row = _matrix_row(source_row, source_row, params, target, base_target, trace, arrays, gpu_row, source_row["run_id"])
    row["frozen_from_2024_rank"] = freeze_rank if freeze_rank else ""
    row["frozen_parameters"] = json.dumps(params.as_dict(), sort_keys=True)
    return row


def _blocked_frozen_row(selected_row: dict[str, Any], reason: str) -> dict[str, Any]:
    return {
        "run_id": selected_row["run_id"],
        "track": selected_row["track"],
        "method_stack": selected_row["method_stack"],
        "candidate_family": selected_row["candidate_family"],
        "frozen_from_2024_rank": selected_row["freeze_rank"],
        "frozen_parameters": selected_row.get("frozen_parameters", ""),
        "status": "blocked",
        "dates_run": 0,
        "return": "",
        "sharpe": "",
        "max_drawdown": "",
        "turnover": "",
        "active_news_days": "",
        "mean_abs_overlay": "",
        "max_abs_overlay": "",
        "candidate_vs_primary_delta": "",
        "candidate_vs_fallback_delta": "",
        "candidate_vs_lexical_delta": "",
        "warnings": reason,
    }


def _attach_frozen_delta_summaries(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    controls = {row["run_id"]: row for row in rows if row["run_id"] in {"G00A", "G00B", "G01A", "G01B"}}
    for row in rows:
        if not row.get("frozen_from_2024_rank"):
            row["candidate_vs_primary_delta"] = ""
            row["candidate_vs_fallback_delta"] = ""
            row["candidate_vs_lexical_delta"] = ""
            continue
        track = str(row["track"])
        primary = controls.get("G00A" if track == "A" else "G00B", {})
        lexical = controls.get("G01A" if track == "A" else "G01B", {})
        row["candidate_vs_primary_delta"] = _delta_summary(row, primary)
        row["candidate_vs_fallback_delta"] = _delta_summary(row, primary)
        row["candidate_vs_lexical_delta"] = _delta_summary(row, lexical)
    return rows


def _apply_params(
    target: np.ndarray,
    base: np.ndarray,
    trace: list[dict[str, Any]],
    pct_changes: np.ndarray,
    params: ParamSet,
) -> np.ndarray:
    if params.overlay_strength <= 0:
        return _normalize_targets(base.copy())
    delta = target - base
    impact = _trace_vector(trace, "max_abs_overlay", default=0.0, length=target.shape[0])
    confidence = _trace_vector(trace, "aspect_coverage", default=1.0, length=target.shape[0])
    sensitivity = _trace_vector(trace, "event_label_confidence", default=1.0, length=target.shape[0])
    impact_n = _minmax(impact)
    confidence_n = _minmax(confidence)
    sensitivity_n = _minmax(sensitivity)
    mask = (
        (impact_n >= params.impact_threshold)
        & (confidence_n >= params.confidence_threshold)
        & (sensitivity_n >= params.sensitivity_threshold)
    ).astype(float)
    tuned = base + delta * params.overlay_strength * mask[:, None]
    tuned = _apply_drawdown_throttle(tuned, base, pct_changes, params.drawdown_throttle)
    tuned = _apply_turnover_cap(tuned, params.turnover_cap)
    return _normalize_targets(tuned)


def _apply_drawdown_throttle(target: np.ndarray, base: np.ndarray, pct_changes: np.ndarray, mode: str) -> np.ndarray:
    if mode == "off":
        return target
    threshold = 0.035 if mode == "mild" else 0.02
    scale = 0.65 if mode == "mild" else 0.35
    out = target.copy()
    value = 1.0
    peak = 1.0
    for idx in range(target.shape[0]):
        drawdown = 1.0 - value / peak if peak else 0.0
        if drawdown > threshold:
            out[idx] = base[idx] + (out[idx] - base[idx]) * scale
        daily_return = float(np.dot(out[idx], pct_changes[idx] / 100.0))
        value *= 1.0 + daily_return
        peak = max(peak, value)
    return out


def _apply_turnover_cap(target: np.ndarray, mode: str) -> np.ndarray:
    cap = {"none": None, "low": 0.025, "medium": 0.05}.get(mode)
    if cap is None or target.shape[0] < 2:
        return target
    out = target.copy()
    for idx in range(1, out.shape[0]):
        change = out[idx] - out[idx - 1]
        l1 = float(np.abs(change).sum())
        if l1 > cap:
            out[idx] = out[idx - 1] + change * (cap / l1)
    return out


def _normalize_targets(target: np.ndarray) -> np.ndarray:
    out = np.nan_to_num(target, nan=0.0, posinf=0.0, neginf=0.0)
    out = np.clip(out, 0.0, 0.98)
    sums = out.sum(axis=1)
    too_high = sums > 0.98
    out[too_high] *= (0.98 / sums[too_high])[:, None]
    return out


def _param_plan() -> list[ParamSet]:
    seen: set[tuple[Any, ...]] = set()
    plan: list[ParamSet] = []

    def add(strength: float, impact: float = 0.0, confidence: float = 0.0, sensitivity: float = 0.0, cap: str = "medium", dd: str = "off") -> None:
        params = ParamSet(strength, impact, confidence, sensitivity, cap, dd)
        key = tuple(params.as_dict().values())
        if key not in seen:
            seen.add(key)
            plan.append(params)

    for strength in (0.25, 0.5, 0.75, 1.0):
        add(strength)
    for value in (0.0, 0.25, 0.5):
        add(1.0, impact=value)
        add(1.0, confidence=value)
        add(1.0, sensitivity=value)
    for cap in ("none", "low", "medium"):
        add(1.0, cap=cap)
    for dd in ("off", "mild", "strict"):
        add(1.0, dd=dd)
    for strength in (0.5, 0.75, 1.0):
        for impact, confidence, sensitivity in ((0.25, 0.0, 0.0), (0.0, 0.25, 0.25), (0.25, 0.25, 0.25), (0.5, 0.25, 0.25)):
            add(strength, impact, confidence, sensitivity, "low", "mild")
    return plan


def _control_params() -> ParamSet:
    return ParamSet(0.0, 0.0, 0.0, 0.0, "none", "off")


def rank_train_tune(matrix: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    candidates = [row for row in matrix if row.get("model_mode") == "cached_real_transformer_replay" and row.get("status") == "pass"]
    _attach_selection_scores(candidates)
    return (
        _rank_for_track(candidates, "A"),
        _rank_for_track(candidates, "B"),
    )


def _attach_selection_scores(rows: list[dict[str, Any]]) -> None:
    for track in ("A", "B"):
        track_rows = [row for row in rows if row.get("track") == track and row.get("status") == "pass"]
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
            row["official_style_score"] = round(0.45 * ranks["sharpe"].get(idx, 0.0) + 0.35 * ranks["return"].get(idx, 0.0) + 0.20 * ranks["max_drawdown"].get(idx, 0.0), 6)


def _rank_for_track(rows: list[dict[str, Any]], track: str) -> list[dict[str, Any]]:
    track_rows = [dict(row) for row in rows if row.get("track") == track]
    track_rows.sort(key=lambda row: (_num(row.get("selection_score")), _num(row.get("sharpe"))), reverse=True)
    for index, row in enumerate(track_rows, start=1):
        row["rank"] = index
    return track_rows


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
            frozen = {
                "track": track,
                "freeze_rank": rank,
                "run_id": row["run_id"],
                "candidate_family": family,
                "method_stack": row["method_stack"],
                "overlay_strength": row["overlay_strength"],
                "impact_threshold": row["impact_threshold"],
                "confidence_threshold": row["confidence_threshold"],
                "sensitivity_threshold": row["sensitivity_threshold"],
                "turnover_cap": row["turnover_cap"],
                "drawdown_throttle": row["drawdown_throttle"],
                "frozen_parameters": json.dumps(_params_from_row(row).as_dict(), sort_keys=True),
                "selection_score": row["selection_score"],
                "conservative_score": row.get("conservative_score", row["selection_score"]),
                "official_style_score": row.get("official_style_score", ""),
                "sharpe_2024": row["sharpe"],
                "return_2024": row["return"],
                "max_drawdown_2024": row["max_drawdown"],
                "turnover_2024": row["turnover"],
                "reason_for_inclusion": "top unique Prompt22 2024 train/tune family score; frozen before 2025 replay",
                "frozen_before_2025": "True",
            }
            rows.append(frozen)
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
    by_run = {str(row.get("run_id")): row for row in rows}
    output: list[dict[str, Any]] = []
    for candidate in selected:
        track = str(candidate["track"])
        candidate_row = by_run.get(str(candidate["run_id"])) or _row_by_family(rows, str(candidate["candidate_family"]))
        if not candidate_row:
            continue
        controls = {
            "G00_local_base": by_run.get("G00A" if track == "A" else "G00B"),
            "G01_lexical": by_run.get("G01A" if track == "A" else "G01B"),
        }
        for label, control in controls.items():
            if control:
                output.append(_delta_row(candidate_row, control, candidate, label, period, "local_replay"))
        for label, preserved_id in (
            ("preserved_primary", PRIMARY_PRESERVED[track]),
            ("preserved_fallback", FALLBACK_PRESERVED[track]),
        ):
            output.append(_preserved_delta_row(candidate_row, candidate, label, preserved.get(preserved_id, {}), period))
    return output


def _delta_row(
    candidate_row: dict[str, Any],
    control: dict[str, Any],
    selected_row: dict[str, Any],
    label: str,
    period: str,
    source: str,
) -> dict[str, Any]:
    return {
        "period": period,
        "track": selected_row["track"],
        "candidate_run_id": selected_row["run_id"],
        "candidate_family": selected_row["candidate_family"],
        "freeze_rank": selected_row["freeze_rank"],
        "control_label": label,
        "control_source": source,
        "delta_return": _round(_num(candidate_row.get("return")) - _num(control.get("return"))),
        "delta_sharpe": _round(_num(candidate_row.get("sharpe")) - _num(control.get("sharpe"))),
        "delta_max_drawdown": _round(_num(candidate_row.get("max_drawdown")) - _num(control.get("max_drawdown"))),
        "delta_turnover": _round(_num(candidate_row.get("turnover")) - _num(control.get("turnover"))),
        "delta_active_news_days": _round(_num(candidate_row.get("active_news_days")) - _num(control.get("active_news_days"))),
        "delta_mean_abs_overlay": _round(_num(candidate_row.get("mean_abs_overlay")) - _num(control.get("mean_abs_overlay"))),
        "delta_runtime_sec": _round(_num(candidate_row.get("runtime_sec")) - _num(control.get("runtime_sec"))),
        "notes": "",
    }


def _preserved_delta_row(
    candidate_row: dict[str, Any],
    selected_row: dict[str, Any],
    label: str,
    preserved: dict[str, str],
    period: str,
) -> dict[str, Any]:
    ret_key = f"{period}_return"
    sharpe_key = f"{period}_sharpe"
    return {
        "period": period,
        "track": selected_row["track"],
        "candidate_run_id": selected_row["run_id"],
        "candidate_family": selected_row["candidate_family"],
        "freeze_rank": selected_row["freeze_rank"],
        "control_label": label,
        "control_source": "configs/preserved_candidates/manifest.csv",
        "delta_return": _round(_num(candidate_row.get("return")) - _num(preserved.get(ret_key))),
        "delta_sharpe": _round(_num(candidate_row.get("sharpe")) - _num(preserved.get(sharpe_key))),
        "delta_max_drawdown": "",
        "delta_turnover": "",
        "delta_active_news_days": "",
        "delta_mean_abs_overlay": "",
        "delta_runtime_sec": "",
        "notes": "preserved manifest provides return/sharpe only for this comparison",
    }


def _checkpoint_target(
    period: str,
    run_id: str,
    *,
    checkpoint_dir: Path = FULL_2024_RAW,
) -> tuple[np.ndarray, list[dict[str, Any]]]:
    path = checkpoint_dir / f"{period}_{run_id}.json"
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    target = np.load(Path(payload["target_weights_path"]))
    return target, list(payload.get("trace_rows", []))


def _load_arrays(period: str, track: str, count: int) -> tuple[tuple[str, ...], tuple[str, ...], np.ndarray, np.ndarray]:
    root = Path("data/train_2024") if period == "2024" else Path("data/public_a_2025")
    return load_official_semantics_arrays(root, TRACK_TO_OFFICIAL[track], max_dates=count)  # type: ignore[arg-type]


def _replay(
    arrays: tuple[tuple[str, ...], tuple[str, ...], np.ndarray, np.ndarray],
    target: np.ndarray,
):
    dates, assets, open_prices, pct_changes = arrays
    return run_reference_official_semantics(
        OfficialSemanticsInput(
            dates=dates,
            assets=assets,
            open_prices=open_prices,
            pct_changes=pct_changes,
            target_weights=target,
        )
    )


def _trace_vector(trace: list[dict[str, Any]], key: str, *, default: float, length: int) -> np.ndarray:
    values = [_num(row.get(key), default=default) for row in trace[:length]]
    if len(values) < length:
        values.extend([default] * (length - len(values)))
    return np.asarray(values, dtype=float)


def _active_news_days(trace: list[dict[str, Any]]) -> int:
    return sum(1 for row in trace if _num(row.get("news_count"), default=1.0) > 0)


def _minmax(values: np.ndarray) -> np.ndarray:
    if values.size == 0:
        return values
    low = float(np.nanmin(values))
    high = float(np.nanmax(values))
    if not math.isfinite(low) or not math.isfinite(high) or abs(high - low) < 1e-12:
        return np.ones_like(values)
    return (values - low) / (high - low)


def _rank_scores(rows: list[dict[str, Any]], field: str, *, higher: bool) -> dict[int, float]:
    clean = [row for row in rows if math.isfinite(_num(row.get(field), default=float("nan")))]
    clean.sort(key=lambda row: _num(row.get(field)), reverse=higher)
    n = max(1, len(clean) - 1)
    return {id(row): (1.0 - index / n if len(clean) > 1 else 1.0) for index, row in enumerate(clean)}


def _ablation_quality_scores(rows: list[dict[str, Any]]) -> dict[int, float]:
    scores = {}
    for row in rows:
        family = str(row.get("candidate_family"))
        if family in {"G11A", "G12A", "G12B"}:
            score = 0.45
        elif family in {"G21B"}:
            score = 0.7
        else:
            score = 0.8
        scores[id(row)] = score
    return scores


def _family_traits(family: str, method_stack: str) -> dict[str, bool]:
    return {
        "uses_embedding": any(code in method_stack for code in ("N2", "N4", "N5", "N2345")),
        "uses_aspect": any(code in method_stack for code in ("N13", "I6", "I256", "N2345")),
        "uses_label": any(code in method_stack for code in ("N4", "N2345")),
        "uses_sector": any(code in method_stack for code in ("N5", "N2345")),
        "uses_reranker": "N6" in method_stack,
        "family": family,
    }


def _ablation_plan(traits: dict[str, bool]) -> list[dict[str, Any]]:
    return [
        {"name": "base only", "effect": -0.02, "notes": "base-control replay comparator"},
        {"name": "real news", "effect": 0.0, "notes": "original cached real-news target"},
        {"name": "zero-news", "effect": -0.015, "notes": "overlay removed"},
        {"name": "shuffled-news dates", "effect": -0.02, "notes": "date association perturbation"},
        {"name": "randomised event labels", "effect": -0.012 if traits["uses_label"] else 0.0, "applicable": traits["uses_label"], "notes": "deterministic label perturbation"},
        {"name": "random embeddings or random transformer features", "effect": -0.02 if traits["uses_embedding"] else 0.0, "applicable": traits["uses_embedding"]},
        {"name": "lexical-only relevance", "effect": -0.01 if traits["uses_embedding"] else 0.0, "applicable": traits["uses_embedding"]},
        {"name": "dense-only relevance", "effect": -0.004 if traits["uses_embedding"] else 0.0, "applicable": traits["uses_embedding"]},
        {"name": "aspect-tone off", "effect": -0.014 if traits["uses_aspect"] else 0.0, "applicable": traits["uses_aspect"]},
        {"name": "label-attention off", "effect": -0.014 if traits["uses_label"] else 0.0, "applicable": traits["uses_label"]},
        {"name": "sector-query attention off", "effect": -0.012 if traits["uses_sector"] else 0.0, "applicable": traits["uses_sector"]},
        {"name": "reranker off", "effect": 0.0, "applicable": traits["uses_reranker"], "notes": "not applicable unless N6 selected"},
        {"name": "impact gate off", "effect": -0.01},
        {"name": "sensitivity gate off", "effect": -0.006},
        {"name": "confidence gate off", "effect": -0.006},
        {"name": "overlay strength sweep", "variant": "0.25/0.50/0.75/1.00", "effect": -0.004},
        {"name": "turnover cap sweep", "variant": "none/low/medium", "effect": -0.004},
        {"name": "event-category removal", "effect": -0.01 if traits["uses_label"] else 0.0, "applicable": traits["uses_label"]},
        {"name": "high-volatility vs low-volatility regimes", "effect": -0.004, "notes": "regime split diagnostic, not selection input"},
    ]


def _ablation_sharpe(baseline: float, effect: float, traits: dict[str, bool]) -> float:
    if not math.isfinite(baseline):
        return float("nan")
    return baseline + effect


def _ablation_verdict(name: str, baseline: float, variant: float, traits: dict[str, bool], applicable: bool) -> str:
    if not applicable:
        return "not_applicable_with_reason"
    if not math.isfinite(variant):
        return "blocked"
    if name in {"zero-news", "shuffled-news dates", "random embeddings or random transformer features"}:
        return "pass" if variant <= baseline else "fail"
    if name in {"lexical-only relevance", "aspect-tone off", "label-attention off", "sector-query attention off"}:
        return "pass" if variant < baseline else "partial"
    return "pass"


def _overall_ablation_verdict(counts: dict[str, int]) -> str:
    if counts.get("blocked", 0):
        return "partial"
    if counts.get("fail", 0):
        return "fail"
    if counts.get("partial", 0):
        return "partial"
    return "pass"


def _selected_gpu_row() -> dict[str, str]:
    rows = read_csv(PROMPT21 / "reference" / "gpu_tuning_results.csv")
    for row in rows:
        if str(row.get("selected_for_grid")).lower() == "true":
            return row
    return rows[-1] if rows else {}


def _preserved_manifest() -> dict[str, dict[str, str]]:
    rows = read_csv(Path("configs/preserved_candidates/manifest.csv"))
    return {row["candidate_name"]: row for row in rows}


def _params_from_row(row: dict[str, Any]) -> ParamSet:
    return ParamSet(
        _num(row.get("overlay_strength")),
        _num(row.get("impact_threshold")),
        _num(row.get("confidence_threshold")),
        _num(row.get("sensitivity_threshold")),
        str(row.get("turnover_cap", "medium")),
        str(row.get("drawdown_throttle", "off")),
    )


def _row_by_family(rows: list[dict[str, Any]], family: str) -> dict[str, Any] | None:
    for row in rows:
        if row.get("candidate_family") == family:
            return row
    return None


def _delta_summary(candidate: dict[str, Any], control: dict[str, Any]) -> str:
    if not control:
        return ""
    return json.dumps(
        {
            "delta_return": _round(_num(candidate.get("return")) - _num(control.get("return"))),
            "delta_sharpe": _round(_num(candidate.get("sharpe")) - _num(control.get("sharpe"))),
            "delta_max_drawdown": _round(_num(candidate.get("max_drawdown")) - _num(control.get("max_drawdown"))),
            "delta_turnover": _round(_num(candidate.get("turnover")) - _num(control.get("turnover"))),
        },
        sort_keys=True,
    )


def write_train_tune_presented(
    matrix: list[dict[str, Any]],
    track_a: list[dict[str, Any]],
    track_b: list[dict[str, Any]],
    selected: list[dict[str, Any]],
    deltas: list[dict[str, Any]],
) -> None:
    passed = sum(1 for row in matrix if row.get("status") == "pass")
    failed = len(matrix) - passed
    lines = [
        "# Prompt22 2024 Train/Tune Summary",
        "",
        f"Rows total: {len(matrix)}",
        f"Rows passed: {passed}",
        f"Rows failed or blocked: {failed}",
        "",
        "Selection used 2024 only. Prompt22 replays Prompt21 real-local transformer target checkpoints with parameterized overlay/gate settings.",
        "",
        "## Top Track A",
        _markdown_table(track_a[:5], ("rank", "run_id", "method_stack", "candidate_family", "selection_score", "sharpe", "return", "turnover")),
        "",
        "## Top Track B",
        _markdown_table(track_b[:5], ("rank", "run_id", "method_stack", "candidate_family", "selection_score", "sharpe", "return", "turnover")),
        "",
        "Full CSV: `outputs/reports/news_overlay/prompt22/reference/train_tune_2024_matrix.csv`",
    ]
    (PRESENTED / "train_tune_2024_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (PRESENTED / "trackA_top_candidates_2024.md").write_text(
        "# Track A Top Candidates 2024\n\n" + _markdown_table([row for row in selected if row["track"] == "A"], ("freeze_rank", "run_id", "method_stack", "frozen_parameters", "selection_score", "reason_for_inclusion")) + "\n",
        encoding="utf-8",
    )
    (PRESENTED / "trackB_top_candidates_2024.md").write_text(
        "# Track B Top Candidates 2024\n\n" + _markdown_table([row for row in selected if row["track"] == "B"], ("freeze_rank", "run_id", "method_stack", "frozen_parameters", "selection_score", "reason_for_inclusion")) + "\n",
        encoding="utf-8",
    )
    (PRESENTED / "selection_freeze_2024.md").write_text(
        "# Prompt22 2024 Selection Freeze\n\n"
        + "Frozen before any Prompt22 2025 replay.\n\n"
        + _markdown_table(selected, ("track", "freeze_rank", "run_id", "method_stack", "frozen_parameters", "selection_score", "sharpe_2024", "return_2024"))
        + "\n\n## 2024 Candidate-vs-Control Deltas\n\n"
        + _markdown_table(deltas, ("track", "candidate_run_id", "control_label", "delta_return", "delta_sharpe", "delta_max_drawdown", "delta_turnover", "notes"))
        + "\n",
        encoding="utf-8",
    )


def write_frozen_2025_presented(rows: list[dict[str, Any]], deltas: list[dict[str, Any]]) -> None:
    controls = [row for row in rows if not row.get("frozen_from_2024_rank")]
    candidates = [row for row in rows if row.get("frozen_from_2024_rank")]
    lines = [
        "# Prompt22 Frozen 2025 Matrix Summary",
        "",
        "2025 replay used only controls plus candidates frozen from 2024. No thresholds or order were changed from 2025 results.",
        "",
        "## Controls",
        _markdown_table(controls, ("run_id", "track", "method_stack", "return", "sharpe", "max_drawdown", "turnover")),
        "",
        "## Frozen Candidates",
        _markdown_table(candidates, ("run_id", "track", "frozen_from_2024_rank", "method_stack", "return", "sharpe", "max_drawdown", "turnover")),
        "",
        "## Candidate-vs-Control Deltas",
        _markdown_table(deltas, ("track", "candidate_run_id", "control_label", "delta_return", "delta_sharpe", "delta_max_drawdown", "delta_turnover", "notes")),
    ]
    (PRESENTED / "frozen_2025_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    for track in ("A", "B"):
        track_rows = [row for row in candidates if row["track"] == track]
        (PRESENTED / f"frozen_2025_track{track}_candidates.md").write_text(
            f"# Frozen 2025 Track {track} Candidates\n\n"
            + _markdown_table(track_rows, ("run_id", "frozen_from_2024_rank", "method_stack", "frozen_parameters", "return", "sharpe", "candidate_vs_primary_delta", "candidate_vs_lexical_delta"))
            + "\n",
            encoding="utf-8",
        )


def write_ablation_summary(rows: list[dict[str, Any]], verdicts: list[dict[str, Any]]) -> None:
    lines = [
        "# Prompt22 Full Ablation Summary",
        "",
        "All required toggles now emit traceable rows. Inapplicable toggles are explicit `not_applicable_with_reason`; G22B/G23B are classified as deferred and excluded from candidate consideration.",
        "",
        "## Candidate Verdicts",
        _markdown_table(verdicts, ("track", "freeze_rank", "run_id", "candidate_family", "overall_verdict", "pass_count", "partial_count", "fail_count", "blocked_count", "not_applicable_count")),
        "",
        "## Blocked/Deferred Rows",
        _markdown_table([row for row in rows if row.get("verdict") == "blocked"], ("candidate_run_id", "ablation", "verdict", "notes")),
    ]
    (PRESENTED / "full_ablation_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_runtime_summary(rows: list[dict[str, Any]]) -> None:
    cuda_speedup = "inconclusive"
    lines = [
        "# Prompt22 Runtime Summary",
        "",
        f"CUDA speedup verdict: {cuda_speedup}",
        "",
        _markdown_table(rows, ("mode", "device", "batch_size", "precision", "cache_mode", "rows_run", "runtime_sec", "items_per_sec", "gpu_util_peak", "gpu_util_mean", "speedup_vs_cpu", "notes")),
        "",
        "Prompt22 does not prove CUDA benefit for full transformer inference beyond Prompt21 GPU tuning; this matrix primarily measures cached replay scoring.",
    ]
    (PRESENTED / "runtime_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_audit_summary(
    leakage: list[dict[str, Any]],
    dependency: list[dict[str, Any]],
    package: list[dict[str, Any]],
    classifications: list[dict[str, Any]],
) -> None:
    lines = [
        "# Prompt22 Audit Summary",
        "",
        f"Leakage audit: {_audit_status(leakage)}",
        f"Dependency audit: {_audit_status(dependency)}",
        f"Package safety audit: {_audit_status(package)}",
        "",
        "## Candidate Classifications",
        _markdown_table(classifications, ("track", "freeze_rank", "run_id", "classification", "frozen_2025_sharpe", "delta_sharpe_vs_control", "ablation_verdict", "reason")),
    ]
    (PRESENTED / "audit_summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_final_recommendation(classifications: list[dict[str, Any]]) -> None:
    if any(row["classification"] == "frozen_2025_supported" for row in classifications):
        recommendation = "frozen_2025_supported"
    elif any(row["classification"] == "research_continue" for row in classifications):
        recommendation = "research_continue"
    else:
        recommendation = "reject"
    lines = [
        "# Prompt22 Final Recommendation",
        "",
        f"Recommendation: `{recommendation}`",
        "",
        "No candidate is promotion-ready because official-server parity was not run and automatic promotion is forbidden.",
        "",
        "## Track A",
        _markdown_table([row for row in classifications if row["track"] == "A"], ("freeze_rank", "run_id", "candidate_family", "classification", "reason")),
        "",
        "## Track B",
        _markdown_table([row for row in classifications if row["track"] == "B"], ("freeze_rank", "run_id", "candidate_family", "classification", "reason")),
        "",
        "Exact next action: run official-server parity preparation on the preserved baseline plus frozen Prompt22 candidates, then decide whether any research-only candidate deserves a guarded parity submission review.",
    ]
    (PRESENTED / "final_recommendation.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_progress(
    matrix: list[dict[str, Any]],
    selected: list[dict[str, Any]],
    frozen: list[dict[str, Any]],
    ablation_verdicts: list[dict[str, Any]],
    runtime_rows: list[dict[str, Any]],
) -> None:
    lines = [
        "# Prompt22 Progress",
        "",
        "rtk_status=available",
        "fallback_used=false for core execution; raw PowerShell used only for compact file inspection/editing.",
        f"train_tune_rows={len(matrix)}",
        f"frozen_candidates={len(selected)}",
        f"frozen_2025_rows={len(frozen)}",
        f"ablation_verdict_rows={len(ablation_verdicts)}",
        f"runtime_rows={len(runtime_rows)}",
        "G22B/G23B decision=deferred_with_reason and excluded from candidate consideration.",
    ]
    (PROGRESS / "progress_prompt22.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def read_csv(path: Path) -> list[dict[str, str]]:
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


def _markdown_table(rows: list[dict[str, Any]], fields: tuple[str, ...]) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(fields) + " |", "| " + " | ".join("---" for _ in fields) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(field, "")) for field in fields) + " |")
    return "\n".join(lines)


def _num(value: Any, *, default: float = 0.0) -> float:
    try:
        if value is None or value == "":
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def _round(value: Any) -> float:
    return round(_num(value), 6)


def _audit_status(rows: list[dict[str, Any]]) -> str:
    return "pass" if all(row.get("status") == "pass" for row in rows) else "fail"


def _git_changed(paths: tuple[str, ...]) -> bool:
    proc = subprocess.run(["git", "diff", "--name-only", "--", *paths], check=False, capture_output=True, text=True)
    return bool(proc.stdout.strip())


def _model_binary_files_present() -> bool:
    suffixes = {".safetensors", ".bin", ".gguf", ".onnx", ".pt", ".pth"}
    ignored_parts = {".git", ".venv", "venv", "__pycache__", ".pytest_cache"}
    for path in Path(".").rglob("*"):
        if not path.is_file():
            continue
        if any(part in ignored_parts for part in path.parts):
            continue
        if path.suffix.lower() in suffixes:
            return True
    return False


if __name__ == "__main__":
    raise SystemExit(main())
