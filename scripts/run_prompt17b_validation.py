#!/usr/bin/env python3
"""Prompt17b full-horizon validation and candidate-freeze repair workflow."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
import subprocess
import sys
from pathlib import Path
from time import perf_counter
from typing import Any, Iterable

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nlpcc.stage1_news.feature_cache import TEXT_FEATURE_MODES, build_text_feature_cache  # noqa: E402
from tools.backtesting.backtester_parity import compare_reference_to_candidate  # noqa: E402
from tools.backtesting.cuda_vectorized_backtester import BatchedOfficialSemanticsInput, run_batched_official_semantics  # noqa: E402
from tools.backtesting.reference_official_semantics import OfficialSemanticsInput, run_reference_official_semantics  # noqa: E402
from tools.experiments.candidate_factory import CandidateSpec, _build_candidate, build_prompt17_candidates  # noqa: E402
from tools.experiments.leakage_safe_input_builder import LeakageSafeInputBuilder  # noqa: E402
from tools.experiments.target_tensor_cache import TargetTensorBundle, TargetTensorCache  # noqa: E402
from tools.experiments.target_tensor_generator import TargetTensorGenerationRequest, generate_target_tensor, planner_config_for_track  # noqa: E402
from tools.verification.submission_package import audit_submission_archive, build_submission_package  # noqa: E402


REQUIRED_PROGRESS = (
    "progress_00_inventory_and_gap_review.md",
    "progress_01_target_tensor_audit.md",
    "progress_02_parity_gate.md",
    "progress_03_full_2024_search.md",
    "progress_04_locked_2025_evaluation.md",
    "progress_05_full_five_fold.md",
    "progress_06_official_server_spotcheck.md",
    "progress_07_package_audit.md",
    "run_log.md",
)

REQUIRED_PRESENTED = (
    "executive_readiness_report.md",
    "full_horizon_search_summary.md",
    "candidate_freeze_repair_report.md",
    "official_parity_closure_summary.md",
    "locked_2025_evaluation_summary.md",
    "five_fold_robustness_summary.md",
    "final_recommendation.md",
    "final_status_report.md",
)

REQUIRED_REFERENCE = (
    "prompt17_gap_matrix.md",
    "target_tensor_audit.md",
    "target_tensor_audit.csv",
    "leakage_safety_audit.md",
    "leakage_safety_audit.csv",
    "parity_spotcheck_full.md",
    "parity_spotcheck_full.csv",
    "full_2024_candidate_scores.csv",
    "full_2024_candidate_ranking.md",
    "full_2024_candidate_ranking.csv",
    "full_2024_trackA_ranking.csv",
    "full_2024_trackB_ranking.csv",
    "locked_2025_candidate_scores.csv",
    "locked_2025_evaluation.md",
    "locked_2025_evaluation.csv",
    "five_fold_485d_scores.csv",
    "five_fold_485d_report.md",
    "ablation_report.md",
    "ablation_report.csv",
    "text_feature_cache_report.md",
    "text_feature_cache_report.csv",
    "runtime_benchmark_report.md",
    "runtime_benchmark_report.csv",
    "official_server_spotcheck.md",
    "official_server_spotcheck.csv",
    "package_audit_report.md",
    "package_audit.json",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Prompt17b validation phases.")
    parser.add_argument(
        "--phase",
        choices=("init", "audit", "parity", "full-2024", "freeze", "locked-2025", "fivefold", "text-runtime", "official-package", "reports", "all-smoke"),
        required=True,
    )
    parser.add_argument("--track", choices=("macro", "sector"), default=None)
    parser.add_argument("--output-root", default=str(REPO_ROOT / ".var" / "prompt17b"))
    parser.add_argument("--report-root", default=str(REPO_ROOT / "outputs" / "reports" / "prompt17b"))
    parser.add_argument("--max-candidates-per-track", type=int, default=12)
    parser.add_argument("--audit-dates", type=int, default=5)
    parser.add_argument("--parity-dates", type=int, default=20)
    parser.add_argument("--text-cache-dates", type=int, default=3)
    parser.add_argument("--full-2024-dates", type=int, default=0, help="0 means all available 2024 dates.")
    parser.add_argument("--locked-2025-dates", type=int, default=0, help="0 means all available public-A 2025 dates.")
    parser.add_argument("--lookback-days", type=int, default=60)
    parser.add_argument("--backend", choices=("auto", "torch", "numpy"), default="numpy")
    parser.add_argument("--prefer-cuda", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--skip-package", action="store_true")
    parser.add_argument("--official-base-url", default="http://localhost:6207")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output_root = Path(args.output_root)
    report_root = Path(args.report_root)
    _ensure_dirs(output_root, report_root)
    state = _load_state(output_root)
    started = perf_counter()
    status = "ok"
    detail = ""
    try:
        if args.phase == "init":
            _phase_init(state, output_root, report_root)
        elif args.phase == "audit":
            _phase_audit(state, args, output_root)
        elif args.phase == "parity":
            _phase_parity(state, args, output_root)
        elif args.phase == "full-2024":
            _phase_full_2024(state, args, output_root)
        elif args.phase == "freeze":
            _phase_freeze(state, args, output_root)
        elif args.phase == "locked-2025":
            _phase_locked_2025(state, args, output_root)
        elif args.phase == "fivefold":
            _phase_fivefold(state, args, output_root)
        elif args.phase == "text-runtime":
            _phase_text_runtime(state, args, output_root)
        elif args.phase == "official-package":
            _phase_official_package(state, args, output_root)
        elif args.phase == "reports":
            pass
        elif args.phase == "all-smoke":
            _phase_init(state, output_root, report_root)
            _phase_audit(state, args, output_root)
            _phase_parity(state, args, output_root)
            for track in ("macro", "sector"):
                args.track = track
                _phase_full_2024(state, args, output_root)
            _phase_freeze(state, args, output_root)
            for track in ("macro", "sector"):
                args.track = track
                _phase_locked_2025(state, args, output_root)
            _phase_fivefold(state, args, output_root)
            _phase_text_runtime(state, args, output_root)
            _phase_official_package(state, args, output_root)
        else:
            raise ValueError(f"Unknown phase: {args.phase}")
    except Exception as exc:
        status = "failed"
        detail = f"{type(exc).__name__}: {exc}"
        state.setdefault("caveats", []).append(f"{args.phase}: {detail}")
        raise
    finally:
        _log_run(state, args.phase, status, detail, perf_counter() - started, vars(args))
        _save_state(output_root, state)
        _write_all_reports(report_root, output_root, state)
    print(json.dumps({"status": status, "phase": args.phase, "elapsed_seconds": round(perf_counter() - started, 3)}, indent=2))
    return 0


def _phase_init(state: dict[str, Any], output_root: Path, report_root: Path) -> None:
    state["created_at_utc"] = state.get("created_at_utc") or datetime.now(timezone.utc).isoformat()
    state["report_root"] = str(report_root)
    state["output_root"] = str(output_root)
    state["prompt17_gap_matrix"] = [
        {
            "issue": "Prompt17 used bounded smoke evidence only",
            "prompt17_status": "bounded 20-date/24-candidate search",
            "prompt17b_action": "run full-horizon 2024 replay per track and mark any bounds explicitly",
            "status": "in_progress",
        },
        {
            "issue": "Track B freeze relied on 2025 top-k despite stronger bounded 2024 S1 sector evidence",
            "prompt17_status": "sector_rotation_graph15 frozen provisionally",
            "prompt17b_action": "freeze Track B strictly from 2024 ranking before locked 2025 review",
            "status": "in_progress",
        },
        {
            "issue": "Parity evidence covered too few candidates",
            "prompt17_status": "S0 macro/S0 sector only",
            "prompt17b_action": "reference-vs-batched spotcheck across required baseline and advanced families",
            "status": "in_progress",
        },
        {
            "issue": "Official server not validated",
            "prompt17_status": "blocked",
            "prompt17b_action": "rerun smoke, record command, port, error, probable cause, next action",
            "status": "pending",
        },
        {
            "issue": "Five-fold robustness was bounded",
            "prompt17_status": "20-date folds",
            "prompt17b_action": "use combined 2024+2025 frozen-candidate target tensors where available",
            "status": "pending",
        },
    ]


def _phase_audit(state: dict[str, Any], args: argparse.Namespace, output_root: Path) -> None:
    candidates = _audit_candidates(output_root)
    rows: list[dict[str, Any]] = []
    leakage_rows: list[dict[str, Any]] = []
    for track in ("macro", "sector"):
        track_candidates = [candidate for candidate in candidates if candidate.track == track]
        result, replay, replay_seconds = _generate_and_replay(
            data_root=REPO_ROOT / "data" / "train_2024",
            track=track,
            candidates=track_candidates,
            output_root=output_root,
            max_dates=args.audit_dates,
            lookback_days=args.lookback_days,
            backend=args.backend,
            prefer_cuda=args.prefer_cuda,
            force=args.force,
            role="target_audit",
        )
        bundle = result.bundle
        diagnostics = {item["name"]: item for item in bundle.metadata.get("candidate_diagnostics", [])}
        for index, name in enumerate(bundle.candidate_names):
            candidate = _candidate_lookup(output_root).get(name)
            diag = diagnostics.get(name, {})
            target = bundle.target_weights[index]
            rows.append(
                {
                    "candidate": name,
                    "track": track,
                    "family": candidate.family if candidate else "",
                    "date_count": len(bundle.dates),
                    "asset_count": len(bundle.assets),
                    "axis_order": "candidate,date,asset",
                    "tensor_shape": "x".join(str(item) for item in bundle.target_weights.shape),
                    "trace_sample_path": bundle.metadata.get("decision_trace_sample_path", ""),
                    "trace_sample_count": bundle.metadata.get("decision_trace_sample_count", 0),
                    "cache_key": result.cache_key,
                    "cache_hit": result.diagnostics.get("cache_hit", False),
                    "cache_has_data_version": bool(bundle.metadata.get("cache_payload", {}).get("data_version")),
                    "failed_days": diag.get("failed_days", 0),
                    "fallback_days": diag.get("fallback_days", 0),
                    "raw_stage_fallback_days": diag.get("raw_stage_fallback_days", 0),
                    "target_nonzero_days": diag.get("target_nonzero_days", 0),
                    "max_target_sum": round(float(target.sum(axis=1).max(initial=0.0)), 8),
                    "min_target_sum": round(float(target.sum(axis=1).min(initial=0.0)), 8),
                    "status": "pass" if diag.get("failed_days", 0) == 0 and bundle.metadata.get("decision_trace_sample_count", 0) else "review",
                }
            )
        leakage = bundle.metadata.get("leakage_summary", {})
        leakage_rows.append(
            {
                "track": track,
                "checked_days": leakage.get("checked_days", 0),
                "all_current_day_close_masked": leakage.get("all_current_day_close_masked", False),
                "all_current_day_open_available": leakage.get("all_current_day_open_available", False),
                "news_cutoff_hour": leakage.get("news_cutoff_hour", ""),
                "forbidden_current_fields": ",".join(leakage.get("forbidden_current_fields", ())),
                "status": "pass"
                if leakage.get("all_current_day_close_masked") and leakage.get("all_current_day_open_available")
                else "review",
            }
        )
        _remember_bundle(state, "train_2024", track, "target_audit", result, replay, replay_seconds)
    state["target_audit_rows"] = _upsert_rows(state.get("target_audit_rows", []), rows, ("candidate", "track"))
    state["leakage_rows"] = _upsert_rows(state.get("leakage_rows", []), leakage_rows, ("track",))


def _phase_parity(state: dict[str, Any], args: argparse.Namespace, output_root: Path) -> None:
    candidates = _select_candidates(_parity_candidate_names(), output_root)
    rows: list[dict[str, Any]] = []
    for track in ("macro", "sector"):
        track_candidates = [candidate for candidate in candidates if candidate.track == track]
        result, replay, replay_seconds = _generate_and_replay(
            data_root=REPO_ROOT / "data" / "train_2024",
            track=track,
            candidates=track_candidates,
            output_root=output_root,
            max_dates=args.parity_dates,
            lookback_days=args.lookback_days,
            backend=args.backend,
            prefer_cuda=args.prefer_cuda,
            force=args.force,
            role="parity",
        )
        bundle = result.bundle
        for index, candidate_result in enumerate(replay.candidates):
            reference = run_reference_official_semantics(
                OfficialSemanticsInput(
                    dates=bundle.dates,
                    assets=bundle.assets,
                    open_prices=bundle.open_prices,
                    pct_changes=bundle.pct_changes,
                    target_weights=bundle.target_weights[index],
                    planner_config=planner_config_for_track(track),  # type: ignore[arg-type]
                )
            )
            parity = compare_reference_to_candidate(reference, candidate_result, tolerance=1e-5)
            spec = _candidate_lookup(output_root).get(candidate_result.name)
            rows.append(
                {
                    "candidate": candidate_result.name,
                    "track": track,
                    "family": spec.family if spec else "",
                    "date_count": len(bundle.dates),
                    "asset_count": len(bundle.assets),
                    "backend": replay.backend,
                    "device": replay.device,
                    "reference_final_value": reference.final_value,
                    "batched_final_value": candidate_result.final_value,
                    "final_value_diff": parity.final_value_diff,
                    "max_value_diff": parity.max_value_diff,
                    "metric_diff_max": max(parity.metric_diffs.values() or [0.0]),
                    "trade_count": len(reference.transactions),
                    "within_tolerance": parity.within_tolerance,
                    "status": "pass" if parity.within_tolerance else "fail",
                }
            )
        _remember_bundle(state, "train_2024", track, "parity", result, replay, replay_seconds)
    state["parity_rows"] = _upsert_rows(state.get("parity_rows", []), rows, ("candidate", "track"))
    state["parity_gate_passed"] = all(bool(row.get("within_tolerance")) for row in state["parity_rows"])


def _phase_full_2024(state: dict[str, Any], args: argparse.Namespace, output_root: Path) -> None:
    if args.track is None:
        raise ValueError("--track is required for full-2024 to keep each invocation bounded.")
    candidates = _full_candidates(output_root, args.max_candidates_per_track)
    track_candidates = [candidate for candidate in candidates if candidate.track == args.track]
    max_dates = None if args.full_2024_dates == 0 else args.full_2024_dates
    result, replay, replay_seconds = _generate_and_replay(
        data_root=REPO_ROOT / "data" / "train_2024",
        track=args.track,
        candidates=track_candidates,
        output_root=output_root,
        max_dates=max_dates,
        lookback_days=args.lookback_days,
        backend=args.backend,
        prefer_cuda=args.prefer_cuda,
        force=args.force,
        role="full_2024",
    )
    candidate_by_name = _candidate_lookup(output_root)
    rows = _score_rows(
        _candidate_rows(replay, result.bundle, args.track, "train_2024_full", candidate_by_name),
        candidate_by_name,
    )
    state["full_2024_rows"] = _upsert_rows(state.get("full_2024_rows", []), rows, ("candidate", "track", "dataset"))
    state["full_2024_rows"] = _score_rows(state["full_2024_rows"], candidate_by_name)
    _remember_bundle(state, "train_2024", args.track, "full_2024", result, replay, replay_seconds)
    _write_json(output_root / "search_runs" / f"full_2024_{args.track}.json", {"rows": rows, "generation": result.as_dict(), "replay": replay.as_dict()})


def _phase_freeze(state: dict[str, Any], args: argparse.Namespace, output_root: Path) -> None:
    del args, output_root
    rows = list(state.get("full_2024_rows", []))
    if not rows:
        raise ValueError("No full_2024_rows found; run full-2024 for each track first.")
    freeze: dict[str, Any] = {"created_at_utc": datetime.now(timezone.utc).isoformat(), "discipline": "2024_only"}
    for track, label in (("macro", "trackA"), ("sector", "trackB")):
        track_rows = [row for row in rows if row.get("track") == track]
        track_rows.sort(key=lambda row: float(row.get("conservative_score", 0.0)), reverse=True)
        if not track_rows:
            continue
        primary = track_rows[0]
        fallback = track_rows[1] if len(track_rows) > 1 else track_rows[0]
        notes = []
        if track == "sector":
            s1_rows = [row for row in track_rows if row.get("candidate") in {"s1_sector_default", "s1_sector_trend60"}]
            graph = next((row for row in track_rows if row.get("candidate") == "sector_rotation_graph15"), None)
            if s1_rows and graph:
                best_s1 = max(s1_rows, key=lambda row: float(row.get("conservative_score", 0.0)))
                if float(best_s1.get("conservative_score", 0.0)) > float(graph.get("conservative_score", 0.0)):
                    notes.append("Track B corrected: S1 sector beat sector_rotation_graph15 on 2024 evidence; sector_rotation_graph15 was not frozen from 2025-only evidence.")
                    if primary.get("candidate") == "sector_rotation_graph15":
                        primary = best_s1
                        fallback = next((row for row in track_rows if row.get("candidate") != primary.get("candidate")), best_s1)
        freeze[label] = {
            "primary": primary.get("candidate"),
            "fallback": fallback.get("candidate"),
            "track": track,
            "primary_score": primary.get("conservative_score"),
            "fallback_score": fallback.get("conservative_score"),
            "notes": notes,
            "source_dataset": "train_2024_full",
        }
    state["freeze"] = freeze


def _phase_locked_2025(state: dict[str, Any], args: argparse.Namespace, output_root: Path) -> None:
    if args.track is None:
        raise ValueError("--track is required for locked-2025 to keep each invocation bounded.")
    if not state.get("freeze"):
        _phase_freeze(state, args, output_root)
    selected_names = _locked_candidate_names(state, args.track)
    candidates = _select_candidates(selected_names, output_root)
    track_candidates = [candidate for candidate in candidates if candidate.track == args.track]
    max_dates = None if args.locked_2025_dates == 0 else args.locked_2025_dates
    result, replay, replay_seconds = _generate_and_replay(
        data_root=REPO_ROOT / "data" / "public_a_2025",
        track=args.track,
        candidates=track_candidates,
        output_root=output_root,
        max_dates=max_dates,
        lookback_days=args.lookback_days,
        backend=args.backend,
        prefer_cuda=args.prefer_cuda,
        force=args.force,
        role="locked_2025",
    )
    candidate_by_name = _candidate_lookup(output_root)
    rows = _score_rows(
        _candidate_rows(replay, result.bundle, args.track, "public_a_2025_locked", candidate_by_name),
        candidate_by_name,
    )
    for row in rows:
        row["locked_after_freeze"] = True
        row["parameter_changes_after_freeze"] = False
    state["locked_2025_rows"] = _upsert_rows(state.get("locked_2025_rows", []), rows, ("candidate", "track", "dataset"))
    state["locked_2025_rows"] = _score_rows(state["locked_2025_rows"], candidate_by_name)
    _remember_bundle(state, "public_a_2025", args.track, "locked_2025", result, replay, replay_seconds)
    _write_json(output_root / "checkpoints" / f"locked_2025_{args.track}.json", {"rows": rows, "generation": result.as_dict(), "replay": replay.as_dict()})


def _phase_fivefold(state: dict[str, Any], args: argparse.Namespace, output_root: Path) -> None:
    rows: list[dict[str, Any]] = []
    for track in ("macro", "sector"):
        combined = _combined_frozen_bundle(state, output_root, track)
        if combined is None:
            state.setdefault("caveats", []).append(f"fivefold:{track}: missing full_2024 or locked_2025 tensors")
            continue
        bundle, candidate_names = combined
        folds = np.array_split(np.arange(len(bundle.dates)), 5)
        for fold_index, fold in enumerate(folds, start=1):
            if len(fold) == 0:
                continue
            replay = run_batched_official_semantics(
                BatchedOfficialSemanticsInput(
                    dates=tuple(bundle.dates[int(index)] for index in fold),
                    assets=bundle.assets,
                    open_prices=bundle.open_prices[fold, :],
                    pct_changes=bundle.pct_changes[fold, :],
                    target_weights=bundle.target_weights[:, fold, :],
                    candidate_names=candidate_names,
                    planner_config=planner_config_for_track(track),  # type: ignore[arg-type]
                ),
                backend=args.backend,
                prefer_cuda=args.prefer_cuda,
            )
            candidate_by_name = _candidate_lookup(output_root)
            for candidate in replay.candidates:
                spec = candidate_by_name.get(candidate.name)
                rows.append(
                    {
                        "fold": fold_index,
                        "candidate": candidate.name,
                        "track": track,
                        "family": spec.family if spec else "",
                        "date_start": bundle.dates[int(fold[0])],
                        "date_end": bundle.dates[int(fold[-1])],
                        "date_count": len(fold),
                        "combined_date_count": len(bundle.dates),
                        "dataset": "train_2024_plus_public_a_2025_research_fold",
                        "cumulative_return": candidate.metrics.get("cumulative_return", 0.0),
                        "sharpe_ratio": candidate.metrics.get("sharpe_ratio", 0.0),
                        "max_drawdown": candidate.metrics.get("max_drawdown", 0.0),
                        "turnover": candidate.metrics.get("turnover", 0.0),
                        "final_value": candidate.final_value,
                        "backend": replay.backend,
                        "device": replay.device,
                    }
                )
    state["five_fold_rows"] = _upsert_rows(state.get("five_fold_rows", []), rows, ("fold", "candidate", "track"))


def _phase_text_runtime(state: dict[str, Any], args: argparse.Namespace, output_root: Path) -> None:
    text_rows: list[dict[str, Any]] = []
    for track in ("macro", "sector"):
        builder = LeakageSafeInputBuilder(data_root=REPO_ROOT / "data" / "train_2024", track=track)  # type: ignore[arg-type]
        dates = builder.selected_dates(max_dates=args.text_cache_dates)
        started = perf_counter()
        records = build_text_feature_cache(
            dates=dates,
            news_provider=builder.visible_news,
            cache_path=output_root / "cache" / "text_feature_cache",
            modes=TEXT_FEATURE_MODES,
            sample_limit=args.text_cache_dates,
        )
        elapsed = perf_counter() - started
        for record in records:
            text_rows.append(
                {
                    "track": track,
                    "mode": record.mode,
                    "decision_date": record.decision_date,
                    "news_count": record.news_count,
                    "cache_key": record.cache_key or "",
                    "fallback_used": record.fallback_used,
                    "event_count": record.event_count,
                    "sentiment_count": record.sentiment_count,
                    "bl_view_count": record.bl_view_count,
                    "diagnostic_status": record.diagnostics.get("status", ""),
                    "elapsed_seconds_group": round(elapsed, 6),
                }
            )
    state["text_cache_rows"] = _upsert_rows(state.get("text_cache_rows", []), text_rows, ("track", "mode", "decision_date"))
    state["runtime_rows"] = _runtime_benchmarks(state, args, output_root)


def _phase_official_package(state: dict[str, Any], args: argparse.Namespace, output_root: Path) -> None:
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "run_official_server_smoke.py"),
        "--base-url",
        args.official_base_url,
        "--output",
        str(output_root / "official_server" / "official_server_smoke.json"),
    ]
    started = perf_counter()
    process = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True, timeout=40, check=False)
    elapsed = perf_counter() - started
    smoke_path = output_root / "official_server" / "official_server_smoke.json"
    smoke_payload = {}
    if smoke_path.exists():
        smoke_payload = json.loads(smoke_path.read_text(encoding="utf-8"))
    state["official_server"] = {
        "command": " ".join(str(part) for part in command),
        "elapsed_seconds": round(elapsed, 6),
        "returncode": process.returncode,
        "stdout": process.stdout.strip(),
        "stderr": process.stderr.strip(),
        "payload": smoke_payload,
        "status": smoke_payload.get("status", "unknown"),
        "base_url": args.official_base_url,
        "probable_cause": "official server not running on configured localhost port"
        if smoke_payload.get("status") == "blocked"
        else "",
        "next_action": "Start the official server, then rerun this phase with the same base URL."
        if smoke_payload.get("status") == "blocked"
        else "No action required.",
    }
    if not args.skip_package:
        package_root = output_root / "packages"
        name = "nlpcc_task4_candidate_prompt17b_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        package = build_submission_package(repo_root=REPO_ROOT, output_root=package_root, package_name=name)
        audit = audit_submission_archive(package.archive_path)
        state["package"] = {
            "status": "ok" if not audit["issues"] else "failed",
            "package": package.as_dict(),
            "archive_audit": audit,
            "includes_src_tools": True,
            "src_tools_reason": "Prompt17b reports and reproducibility scripts depend on local verification/backtesting tools; competition runtime remains under src/nlpcc.",
        }
        _write_json(output_root / "packages" / "package_audit.json", state["package"])


def _generate_and_replay(
    *,
    data_root: Path,
    track: str,
    candidates: list[CandidateSpec],
    output_root: Path,
    max_dates: int | None,
    lookback_days: int,
    backend: str,
    prefer_cuda: bool,
    force: bool,
    role: str,
) -> tuple[Any, Any, float]:
    result = generate_target_tensor(
        TargetTensorGenerationRequest(
            repo_root=REPO_ROOT,
            data_root=data_root,
            track=track,  # type: ignore[arg-type]
            candidates=candidates,
            output_root=output_root,
            max_dates=max_dates,
            lookback_days=lookback_days,
            force=force,
        )
    )
    started = perf_counter()
    replay = run_batched_official_semantics(
        BatchedOfficialSemanticsInput(
            dates=result.bundle.dates,
            assets=result.bundle.assets,
            open_prices=result.bundle.open_prices,
            pct_changes=result.bundle.pct_changes,
            target_weights=result.bundle.target_weights,
            candidate_names=result.bundle.candidate_names,
            planner_config=planner_config_for_track(track),  # type: ignore[arg-type]
        ),
        backend=backend,
        prefer_cuda=prefer_cuda,
    )
    replay_seconds = perf_counter() - started
    _write_json(
        output_root / "search_runs" / f"{role}_{track}_summary.json",
        {
            "generation": result.as_dict(),
            "replay": replay.as_dict(),
            "replay_seconds": replay_seconds,
            "data_root": str(data_root),
        },
    )
    return result, replay, replay_seconds


def _candidate_rows(
    replay: Any,
    bundle: TargetTensorBundle,
    track: str,
    dataset: str,
    candidate_by_name: dict[str, CandidateSpec],
) -> list[dict[str, Any]]:
    diagnostics = {item["name"]: item for item in bundle.metadata.get("candidate_diagnostics", [])}
    rows: list[dict[str, Any]] = []
    for index, candidate in enumerate(replay.candidates):
        spec = candidate_by_name.get(candidate.name)
        target = bundle.target_weights[index]
        target_sums = target.sum(axis=1)
        target_diffs = np.abs(np.diff(target, axis=0)).sum(axis=1) if len(bundle.dates) > 1 else np.asarray([])
        diag = diagnostics.get(candidate.name, {})
        rows.append(
            {
                "candidate": candidate.name,
                "track": track,
                "dataset": dataset,
                "family": spec.family if spec else "",
                "text_mode": spec.text_mode if spec else "",
                "date_count": len(bundle.dates),
                "asset_count": len(bundle.assets),
                "final_value": candidate.final_value,
                "cumulative_return": candidate.metrics.get("cumulative_return", 0.0),
                "annualized_return": candidate.metrics.get("annualized_return", 0.0),
                "sharpe_ratio": candidate.metrics.get("sharpe_ratio", 0.0),
                "max_drawdown": candidate.metrics.get("max_drawdown", 0.0),
                "turnover": candidate.metrics.get("turnover", 0.0),
                "fallback_days": diag.get("fallback_days", 0),
                "raw_stage_fallback_days": diag.get("raw_stage_fallback_days", 0),
                "failed_days": diag.get("failed_days", 0),
                "fallback_rate": round(float(diag.get("fallback_days", 0)) / max(1, len(bundle.dates)), 6),
                "target_nonzero_days": diag.get("target_nonzero_days", 0),
                "mean_target_sum": round(float(target_sums.mean()) if target_sums.size else 0.0, 8),
                "max_target_sum": round(float(target_sums.max()) if target_sums.size else 0.0, 8),
                "trade_count_proxy": int((target_sums > 1e-9).sum()) + int((target_diffs > 1e-9).sum()),
                "backend": replay.backend,
                "device": replay.device,
            }
        )
    return rows


def _score_rows(rows: list[dict[str, Any]], candidate_by_name: dict[str, CandidateSpec]) -> list[dict[str, Any]]:
    if not rows:
        return []
    by_track: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        by_track.setdefault(str(row.get("track", "")), []).append(row)
    scored: list[dict[str, Any]] = []
    for track_rows in by_track.values():
        sharpe = _rank_scores(track_rows, "sharpe_ratio", higher=True)
        returns = _rank_scores(track_rows, "cumulative_return", higher=True)
        drawdown = _rank_scores(track_rows, "max_drawdown", higher=False)
        turnover = _rank_scores(track_rows, "turnover", higher=False)
        for row in track_rows:
            spec = candidate_by_name.get(str(row.get("candidate")))
            novelty = spec.novelty if spec else 0.5
            reproducibility = spec.reproducibility if spec else 0.7
            complexity_penalty = spec.complexity_penalty if spec else 0.2
            dependency_risk = spec.dependency_risk if spec else 0.1
            key = str(row.get("candidate"))
            official_score = (
                0.35 * sharpe[key]
                + 0.25 * returns[key]
                + 0.15 * drawdown[key]
                + 0.10 * turnover[key]
                + 0.10 * reproducibility
                + 0.05 * novelty
            )
            conservative = official_score - 0.08 * complexity_penalty - 0.08 * dependency_risk
            enriched = dict(row)
            enriched.update({"official_score": round(official_score, 6), "conservative_score": round(conservative, 6)})
            scored.append(enriched)
    scored.sort(key=lambda item: (item.get("track", ""), -float(item.get("conservative_score", 0.0))))
    return scored


def _rank_scores(rows: list[dict[str, Any]], key: str, *, higher: bool) -> dict[str, float]:
    values = [float(row.get(key, 0.0) or 0.0) for row in rows]
    if not values:
        return {}
    lo = min(values)
    hi = max(values)
    if abs(hi - lo) < 1e-12:
        return {str(row["candidate"]): 0.5 for row in rows}
    scores: dict[str, float] = {}
    for row in rows:
        value = float(row.get(key, 0.0) or 0.0)
        score = (value - lo) / (hi - lo)
        scores[str(row["candidate"])] = score if higher else 1.0 - score
    return scores


def _runtime_benchmarks(state: dict[str, Any], args: argparse.Namespace, output_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    cache = TargetTensorCache(output_root / "target_tensors")
    for track in ("macro", "sector"):
        info = state.get("bundles", {}).get(f"train_2024:{track}:parity") or state.get("bundles", {}).get(f"train_2024:{track}:full_2024")
        if not info:
            continue
        bundle = cache.load(info["cache_key"])
        index = 0
        started = perf_counter()
        reference = run_reference_official_semantics(
            OfficialSemanticsInput(
                dates=bundle.dates,
                assets=bundle.assets,
                open_prices=bundle.open_prices,
                pct_changes=bundle.pct_changes,
                target_weights=bundle.target_weights[index],
                planner_config=planner_config_for_track(track),  # type: ignore[arg-type]
            )
        )
        reference_seconds = perf_counter() - started
        rows.append(
            {
                "track": track,
                "backend": "reference_loop",
                "candidate_count": 1,
                "date_count": len(bundle.dates),
                "asset_count": len(bundle.assets),
                "elapsed_seconds": round(reference_seconds, 6),
                "candidates_per_second": round(1.0 / max(reference_seconds, 1e-9), 6),
                "device": "cpu",
                "final_value": reference.final_value,
            }
        )
        for batch in (len(bundle.candidate_names), 100, 300):
            repeats = int(np.ceil(batch / len(bundle.candidate_names)))
            target = np.tile(bundle.target_weights, (repeats, 1, 1))[:batch]
            names = tuple(f"{bundle.candidate_names[i % len(bundle.candidate_names)]}__tile{i}" for i in range(batch))
            started = perf_counter()
            replay = run_batched_official_semantics(
                BatchedOfficialSemanticsInput(
                    dates=bundle.dates,
                    assets=bundle.assets,
                    open_prices=bundle.open_prices,
                    pct_changes=bundle.pct_changes,
                    target_weights=target,
                    candidate_names=names,
                    planner_config=planner_config_for_track(track),  # type: ignore[arg-type]
                ),
                backend=args.backend,
                prefer_cuda=args.prefer_cuda,
            )
            elapsed = perf_counter() - started
            rows.append(
                {
                    "track": track,
                    "backend": replay.backend,
                    "candidate_count": batch,
                    "date_count": len(bundle.dates),
                    "asset_count": len(bundle.assets),
                    "elapsed_seconds": round(elapsed, 6),
                    "candidates_per_second": round(batch / max(elapsed, 1e-9), 6),
                    "device": replay.device,
                    "final_value": replay.candidates[0].final_value,
                }
            )
    _write_json(output_root / "benchmarks" / "runtime_benchmark.json", {"rows": rows})
    return rows


def _full_candidates(output_root: Path, max_per_track: int) -> list[CandidateSpec]:
    return [
        candidate.with_stage1_cache(output_root / "cache" / "text_feature_cache")
        for candidate in build_prompt17_candidates(
            repo_root=REPO_ROOT,
            max_per_track=max_per_track,
            include_text_modes=("no_news", "rule_based"),
        )
    ]


def _candidate_lookup(output_root: Path) -> dict[str, CandidateSpec]:
    candidates = [
        candidate.with_stage1_cache(output_root / "cache" / "text_feature_cache")
        for candidate in build_prompt17_candidates(repo_root=REPO_ROOT, max_per_track=None, include_text_modes=("no_news", "rule_based"))
    ]
    candidates.append(_oco_candidate(output_root))
    return {candidate.name: candidate for candidate in candidates}


def _select_candidates(names: Iterable[str], output_root: Path) -> list[CandidateSpec]:
    lookup = _candidate_lookup(output_root)
    missing = [name for name in names if name not in lookup]
    if missing:
        raise KeyError(f"Missing candidates: {', '.join(missing)}")
    return [lookup[name] for name in names]


def _audit_candidates(output_root: Path) -> list[CandidateSpec]:
    return _select_candidates(
        (
            "s0_macro_cash02",
            "s1_macro_default",
            "risk_parity_macro",
            "dro_bl_rp_macro_rule",
            "bsa_rp_macro_tilt25",
            "armor_omd_macro_default",
            "ceva_macro_rule",
            "hgf_mpc_macro_default",
            "oco_fallback_macro",
            "s0_sector_cash02",
            "s1_sector_default",
            "sector_rotation_graph15",
            "leeqa_rank_top4",
            "kg_moe_lite_rule",
            "armor_omd_sector_default",
            "ceva_sector_rule",
        ),
        output_root,
    )


def _parity_candidate_names() -> tuple[str, ...]:
    return (
        "s0_macro_cash02",
        "s1_macro_default",
        "bsa_rp_macro_tilt25",
        "dro_bl_rp_macro_rule",
        "risk_parity_macro",
        "s0_sector_cash02",
        "s1_sector_default",
        "s1_sector_trend60",
        "sector_rotation_graph15",
        "ceva_sector_rule",
        "leeqa_rank_top4",
        "kg_moe_lite_rule",
    )


def _oco_candidate(output_root: Path) -> CandidateSpec:
    return _build_candidate(
        REPO_ROOT,
        name="oco_fallback_macro",
        track="macro",  # type: ignore[arg-type]
        family="oco_fallback",
        base_system="oco_fallback",
        text_mode="no_news",
        params={},
        fallback_strategy="s1_macro",
        novelty=0.45,
        reproducibility=0.86,
        complexity_penalty=0.22,
        dependency_risk=0.05,
    ).with_stage1_cache(output_root / "cache" / "text_feature_cache")


def _locked_candidate_names(state: dict[str, Any], track: str) -> list[str]:
    rows = [row for row in state.get("full_2024_rows", []) if row.get("track") == track]
    rows.sort(key=lambda row: float(row.get("conservative_score", 0.0)), reverse=True)
    label = "trackA" if track == "macro" else "trackB"
    names = []
    freeze = state.get("freeze", {}).get(label, {})
    for name in (freeze.get("primary"), freeze.get("fallback")):
        if name and name not in names:
            names.append(str(name))
    for row in rows[:3]:
        name = str(row.get("candidate"))
        if name not in names:
            names.append(name)
    baselines = ("s0_macro_cash02", "s1_macro_default") if track == "macro" else ("s0_sector_cash02", "s1_sector_default", "sector_rotation_graph15")
    for name in baselines:
        if name not in names:
            names.append(name)
    return names


def _combined_frozen_bundle(state: dict[str, Any], output_root: Path, track: str) -> tuple[TargetTensorBundle, tuple[str, ...]] | None:
    bundles = state.get("bundles", {})
    train_info = bundles.get(f"train_2024:{track}:full_2024")
    eval_info = bundles.get(f"public_a_2025:{track}:locked_2025")
    if not train_info or not eval_info:
        return None
    cache = TargetTensorCache(output_root / "target_tensors")
    train = cache.load(train_info["cache_key"])
    eval_ = cache.load(eval_info["cache_key"])
    if train.assets != eval_.assets:
        return None
    common = tuple(name for name in eval_.candidate_names if name in train.candidate_names)
    if not common:
        return None
    train_indices = [train.candidate_names.index(name) for name in common]
    eval_indices = [eval_.candidate_names.index(name) for name in common]
    target = np.concatenate([train.target_weights[train_indices, :, :], eval_.target_weights[eval_indices, :, :]], axis=1)
    bundle = TargetTensorBundle(
        dates=tuple(train.dates) + tuple(eval_.dates),
        assets=train.assets,
        candidate_names=common,
        open_prices=np.concatenate([train.open_prices, eval_.open_prices], axis=0),
        pct_changes=np.concatenate([train.pct_changes, eval_.pct_changes], axis=0),
        target_weights=target,
        metadata={
            "source": "prompt17b_combined_train_2024_public_a_2025",
            "caveat": "portfolio state resets at dataset boundary in source target generation; folds are research-only robustness checks",
        },
    )
    return bundle, common


def _remember_bundle(state: dict[str, Any], dataset: str, track: str, role: str, result: Any, replay: Any, replay_seconds: float) -> None:
    state.setdefault("bundles", {})[f"{dataset}:{track}:{role}"] = {
        "cache_key": result.cache_key,
        "npz_path": str(result.npz_path),
        "metadata_path": str(result.metadata_path),
        "candidate_names": list(result.bundle.candidate_names),
        "date_count": len(result.bundle.dates),
        "asset_count": len(result.bundle.assets),
        "generation_seconds": result.diagnostics.get("elapsed_seconds", 0.0),
        "replay_seconds": round(replay_seconds, 6),
        "backend": replay.backend,
        "device": replay.device,
    }


def _ensure_dirs(output_root: Path, report_root: Path) -> None:
    for path in (
        output_root / "cache",
        output_root / "target_tensors",
        output_root / "generated_configs",
        output_root / "search_runs",
        output_root / "checkpoints",
        output_root / "benchmarks",
        output_root / "official_server",
        output_root / "packages",
        report_root / "progress",
        report_root / "presented",
        report_root / "reference",
    ):
        path.mkdir(parents=True, exist_ok=True)


def _state_path(output_root: Path) -> Path:
    return output_root / "prompt17b_state.json"


def _load_state(output_root: Path) -> dict[str, Any]:
    path = _state_path(output_root)
    if not path.exists():
        return {
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "run_log": [],
            "caveats": [],
            "bundles": {},
        }
    return json.loads(path.read_text(encoding="utf-8"))


def _save_state(output_root: Path, state: dict[str, Any]) -> None:
    _write_json(_state_path(output_root), state)


def _log_run(state: dict[str, Any], phase: str, status: str, detail: str, elapsed: float, args: dict[str, Any]) -> None:
    state.setdefault("run_log", []).append(
        {
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "phase": phase,
            "status": status,
            "detail": detail,
            "elapsed_seconds": round(elapsed, 6),
            "args": args,
        }
    )


def _upsert_rows(existing: list[dict[str, Any]], new_rows: list[dict[str, Any]], keys: tuple[str, ...]) -> list[dict[str, Any]]:
    by_key = {tuple(str(row.get(key, "")) for key in keys): dict(row) for row in existing}
    for row in new_rows:
        by_key[tuple(str(row.get(key, "")) for key in keys)] = dict(row)
    return list(by_key.values())


def _write_all_reports(report_root: Path, output_root: Path, state: dict[str, Any]) -> None:
    _ensure_dirs(output_root, report_root)
    reference = report_root / "reference"
    progress = report_root / "progress"
    presented = report_root / "presented"

    full_rows = _score_rows(state.get("full_2024_rows", []), _candidate_lookup(output_root))
    locked_rows = _score_rows(state.get("locked_2025_rows", []), _candidate_lookup(output_root))
    parity_rows = state.get("parity_rows", [])
    audit_rows = state.get("target_audit_rows", [])
    leakage_rows = state.get("leakage_rows", [])
    five_rows = state.get("five_fold_rows", [])
    runtime_rows = state.get("runtime_rows", [])
    text_rows = state.get("text_cache_rows", [])
    ablation_rows = _ablation_rows(full_rows)

    _write_csv(reference / "target_tensor_audit.csv", audit_rows)
    _write_csv(reference / "leakage_safety_audit.csv", leakage_rows)
    _write_csv(reference / "parity_spotcheck_full.csv", parity_rows)
    _write_csv(reference / "full_2024_candidate_scores.csv", full_rows)
    _write_csv(reference / "full_2024_candidate_ranking.csv", full_rows)
    _write_csv(reference / "full_2024_trackA_ranking.csv", [row for row in full_rows if row.get("track") == "macro"])
    _write_csv(reference / "full_2024_trackB_ranking.csv", [row for row in full_rows if row.get("track") == "sector"])
    _write_csv(reference / "locked_2025_candidate_scores.csv", locked_rows)
    _write_csv(reference / "locked_2025_evaluation.csv", locked_rows)
    _write_csv(reference / "five_fold_485d_scores.csv", five_rows)
    _write_csv(reference / "ablation_report.csv", ablation_rows)
    _write_csv(reference / "text_feature_cache_report.csv", text_rows)
    _write_csv(reference / "runtime_benchmark_report.csv", runtime_rows)
    _write_csv(reference / "official_server_spotcheck.csv", [_official_row(state)])
    _write_json(reference / "package_audit.json", state.get("package", {"status": "not_run"}))

    readiness = _readiness(state)
    freeze = state.get("freeze", {})
    full_top = _top_by_track(full_rows)
    locked_top = _top_by_track(locked_rows)
    parity_pass = all(bool(row.get("within_tolerance")) for row in parity_rows) if parity_rows else False

    _write_md(report_root / "README.md", _report_readme(state, readiness))
    _write_md(reference / "prompt17_gap_matrix.md", _md_table(state.get("prompt17_gap_matrix", [])))
    _write_md(reference / "target_tensor_audit.md", "# Target Tensor Audit\n\n" + _md_table(audit_rows))
    _write_md(reference / "leakage_safety_audit.md", "# Leakage Safety Audit\n\n" + _md_table(leakage_rows))
    _write_md(reference / "parity_spotcheck_full.md", "# Parity Spotcheck\n\n" + _md_table(parity_rows))
    _write_md(reference / "full_2024_candidate_ranking.md", "# Full 2024 Candidate Ranking\n\n" + _md_table(full_rows))
    _write_md(reference / "locked_2025_evaluation.md", "# Locked 2025 Evaluation\n\n" + _md_table(locked_rows))
    _write_md(reference / "five_fold_485d_report.md", "# Five-Fold Robustness\n\n" + _fivefold_summary_text(five_rows))
    _write_md(reference / "ablation_report.md", "# Ablation Report\n\n" + _md_table(ablation_rows))
    _write_md(reference / "text_feature_cache_report.md", "# Text Feature Cache Report\n\n" + _md_table(text_rows))
    _write_md(reference / "runtime_benchmark_report.md", "# Runtime Benchmark Report\n\n" + _md_table(runtime_rows))
    _write_md(reference / "official_server_spotcheck.md", "# Official Server Spotcheck\n\n" + _official_text(state))
    _write_md(reference / "package_audit_report.md", "# Package Audit\n\n" + _package_text(state))

    _write_md(progress / "progress_00_inventory_and_gap_review.md", "# Inventory and Gap Review\n\n" + _md_table(state.get("prompt17_gap_matrix", [])))
    _write_md(progress / "progress_01_target_tensor_audit.md", "# Target Tensor Audit Progress\n\n" + _md_table(audit_rows))
    _write_md(progress / "progress_02_parity_gate.md", f"# Parity Gate\n\nGate passed: `{parity_pass}`\n\n" + _md_table(parity_rows))
    _write_md(progress / "progress_03_full_2024_search.md", "# Full 2024 Search Progress\n\n" + _md_table(full_rows))
    _write_md(progress / "progress_04_locked_2025_evaluation.md", "# Locked 2025 Evaluation Progress\n\n" + _md_table(locked_rows))
    _write_md(progress / "progress_05_full_five_fold.md", "# Full Five-Fold Progress\n\n" + _fivefold_summary_text(five_rows))
    _write_md(progress / "progress_06_official_server_spotcheck.md", "# Official Server Spotcheck Progress\n\n" + _official_text(state))
    _write_md(progress / "progress_07_package_audit.md", "# Package Audit Progress\n\n" + _package_text(state))
    _write_md(progress / "run_log.md", "# Run Log\n\n" + _md_table(state.get("run_log", [])))

    _write_md(
        presented / "executive_readiness_report.md",
        "\n".join(
            [
                "# Executive Readiness Report",
                "",
                f"Readiness verdict: **{readiness['verdict']}**.",
                "",
                readiness["reason"],
                "",
                "Top 2024 candidates:",
                "",
                _md_table(list(full_top.values())),
                "",
                "Locked 2025 leaders:",
                "",
                _md_table(list(locked_top.values())),
            ]
        ),
    )
    _write_md(presented / "full_horizon_search_summary.md", "# Full-Horizon Search Summary\n\n" + _full_horizon_text(state, full_rows))
    _write_md(presented / "candidate_freeze_repair_report.md", "# Candidate Freeze Repair Report\n\n" + _freeze_text(freeze, full_rows))
    _write_md(presented / "official_parity_closure_summary.md", "# Official Parity Closure Summary\n\n" + _parity_text(parity_rows))
    _write_md(presented / "locked_2025_evaluation_summary.md", "# Locked 2025 Evaluation Summary\n\n" + _locked_text(locked_rows, freeze))
    _write_md(presented / "five_fold_robustness_summary.md", "# Five-Fold Robustness Summary\n\n" + _fivefold_summary_text(five_rows))
    _write_md(presented / "final_recommendation.md", "# Final Recommendation\n\n" + _final_recommendation_text(state, readiness))
    _write_md(presented / "final_status_report.md", "# Final Status Report\n\n" + _final_status_text(state, readiness))

    for name in REQUIRED_PROGRESS:
        (progress / name).touch(exist_ok=True)
    for name in REQUIRED_PRESENTED:
        (presented / name).touch(exist_ok=True)
    for name in REQUIRED_REFERENCE:
        (reference / name).touch(exist_ok=True)


def _report_readme(state: dict[str, Any], readiness: dict[str, str]) -> str:
    return "\n".join(
        [
            "# Prompt17b Reports",
            "",
            f"Created: {state.get('created_at_utc', '')}",
            f"Readiness verdict: **{readiness['verdict']}**",
            "",
            "This directory contains progress, presented, and reference evidence for Prompt17b.",
            "",
            "Large generated tensors, package artifacts, and benchmark JSON are under `.var/prompt17b/`.",
        ]
    )


def _readiness(state: dict[str, Any]) -> dict[str, str]:
    required = [
        bool(state.get("target_audit_rows")),
        bool(state.get("leakage_rows")),
        bool(state.get("parity_gate_passed")),
        bool(state.get("full_2024_rows")),
        bool(state.get("freeze")),
        bool(state.get("locked_2025_rows")),
        bool(state.get("five_fold_rows")),
        bool(state.get("package")),
    ]
    official_ok = state.get("official_server", {}).get("status") == "ok"
    if all(required) and official_ok:
        return {"verdict": "ready_for_submission_packaging", "reason": "All Prompt17b gates, including official server smoke, passed."}
    if all(required):
        return {
            "verdict": "provisionally_ready_except_official_server",
            "reason": "Local full-horizon evidence and package audit exist, but official server smoke is still blocked or not ok.",
        }
    return {
        "verdict": "not_ready",
        "reason": "One or more required Prompt17b gates are missing, failed, or still bounded.",
    }


def _top_by_track(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    output: dict[str, dict[str, Any]] = {}
    for track in ("macro", "sector"):
        track_rows = [row for row in rows if row.get("track") == track]
        if track_rows:
            output[track] = max(track_rows, key=lambda row: float(row.get("conservative_score", 0.0)))
    return output


def _ablation_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault((str(row.get("track", "")), str(row.get("family", "")), str(row.get("text_mode", ""))), []).append(row)
    output = []
    for (track, family, text_mode), items in grouped.items():
        best = max(items, key=lambda row: float(row.get("conservative_score", 0.0)))
        output.append(
            {
                "track": track,
                "family": family,
                "text_mode": text_mode,
                "candidate_count": len(items),
                "best_candidate": best.get("candidate", ""),
                "best_conservative_score": best.get("conservative_score", ""),
                "best_cumulative_return": best.get("cumulative_return", ""),
            }
        )
    output.sort(key=lambda row: (row["track"], -float(row.get("best_conservative_score", 0.0))))
    return output


def _official_row(state: dict[str, Any]) -> dict[str, Any]:
    official = state.get("official_server", {})
    payload = official.get("payload", {})
    return {
        "status": official.get("status", "not_run"),
        "base_url": official.get("base_url", ""),
        "command": official.get("command", ""),
        "returncode": official.get("returncode", ""),
        "blocker": payload.get("blocker", ""),
        "detail": payload.get("detail", ""),
        "probable_cause": official.get("probable_cause", ""),
        "next_action": official.get("next_action", ""),
    }


def _official_text(state: dict[str, Any]) -> str:
    return _md_table([_official_row(state)])


def _package_text(state: dict[str, Any]) -> str:
    package = state.get("package", {"status": "not_run"})
    rows = [
        {
            "status": package.get("status", "not_run"),
            "archive_path": package.get("package", {}).get("archive_path", ""),
            "file_count": package.get("package", {}).get("file_count", ""),
            "entry_count": package.get("archive_audit", {}).get("entry_count", ""),
            "issues": ",".join(package.get("archive_audit", {}).get("issues", [])),
            "includes_src_tools": package.get("includes_src_tools", ""),
            "src_tools_reason": package.get("src_tools_reason", ""),
        }
    ]
    return _md_table(rows)


def _full_horizon_text(state: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    bundle_rows = []
    for key, info in sorted(state.get("bundles", {}).items()):
        if key.endswith(":full_2024"):
            bundle_rows.append({"bundle": key, **info})
    return "\n".join(
        [
            "Full 2024 means `max_dates=None` for each track unless `full_2024_dates` was set in the run log.",
            "",
            "Bundles:",
            "",
            _md_table(bundle_rows),
            "",
            "Ranking:",
            "",
            _md_table(rows),
        ]
    )


def _freeze_text(freeze: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    freeze_rows = []
    for label in ("trackA", "trackB"):
        item = freeze.get(label, {})
        if item:
            freeze_rows.append({"label": label, **item})
    sector_rows = [row for row in rows if row.get("track") == "sector" and row.get("candidate") in {"s1_sector_default", "s1_sector_trend60", "sector_rotation_graph15"}]
    return "Freeze discipline: 2024-only before locked 2025 evaluation.\n\n" + _md_table(freeze_rows) + "\n\nTrack B comparison:\n\n" + _md_table(sector_rows)


def _parity_text(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "Parity was not run."
    passed = all(bool(row.get("within_tolerance")) for row in rows)
    return f"Broad parity gate passed: `{passed}`.\n\n" + _md_table(rows)


def _locked_text(rows: list[dict[str, Any]], freeze: dict[str, Any]) -> str:
    return "Locked 2025 was evaluated only after the 2024 freeze decision.\n\n" + _md_table(rows) + "\n\nFreeze:\n\n" + _md_table([{**item, "label": label} for label, item in freeze.items() if isinstance(item, dict)])


def _fivefold_summary_text(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "Five-fold robustness has not been generated."
    summary: list[dict[str, Any]] = []
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault((str(row.get("track", "")), str(row.get("candidate", ""))), []).append(row)
    for (track, candidate), items in grouped.items():
        returns = [float(item.get("cumulative_return", 0.0) or 0.0) for item in items]
        sharpes = [float(item.get("sharpe_ratio", 0.0) or 0.0) for item in items]
        summary.append(
            {
                "track": track,
                "candidate": candidate,
                "fold_count": len(items),
                "mean_return": round(float(np.mean(returns)), 8),
                "min_return": round(float(np.min(returns)), 8),
                "mean_sharpe": round(float(np.mean(sharpes)), 8),
                "combined_date_count": max(int(item.get("combined_date_count", 0) or 0) for item in items),
                "caveat": "research-only; source target generation resets portfolio at 2024/2025 boundary",
            }
        )
    summary.sort(key=lambda row: (row["track"], -float(row["mean_return"])))
    return _md_table(summary) + "\n\nFold rows:\n\n" + _md_table(rows)


def _final_recommendation_text(state: dict[str, Any], readiness: dict[str, str]) -> str:
    freeze = state.get("freeze", {})
    return "\n".join(
        [
            f"Recommendation: **{readiness['verdict']}**.",
            "",
            readiness["reason"],
            "",
            f"Track A primary: `{freeze.get('trackA', {}).get('primary', 'unfrozen')}`; fallback: `{freeze.get('trackA', {}).get('fallback', 'unfrozen')}`.",
            f"Track B primary: `{freeze.get('trackB', {}).get('primary', 'unfrozen')}`; fallback: `{freeze.get('trackB', {}).get('fallback', 'unfrozen')}`.",
            "",
            "Next prompt should focus on official server validation and final packaging polish only if the official server remains blocked.",
        ]
    )


def _final_status_text(state: dict[str, Any], readiness: dict[str, str]) -> str:
    checks = [
        {"gate": "target_tensor_audit", "status": "done" if state.get("target_audit_rows") else "missing"},
        {"gate": "leakage_safety_audit", "status": "done" if state.get("leakage_rows") else "missing"},
        {"gate": "broad_parity", "status": "pass" if state.get("parity_gate_passed") else "missing_or_fail"},
        {"gate": "full_2024_search", "status": "done" if state.get("full_2024_rows") else "missing"},
        {"gate": "2024_candidate_freeze", "status": "done" if state.get("freeze") else "missing"},
        {"gate": "locked_2025", "status": "done" if state.get("locked_2025_rows") else "missing"},
        {"gate": "five_fold", "status": "done" if state.get("five_fold_rows") else "missing"},
        {"gate": "official_server", "status": state.get("official_server", {}).get("status", "not_run")},
        {"gate": "package_audit", "status": state.get("package", {}).get("status", "not_run")},
    ]
    return f"Readiness verdict: **{readiness['verdict']}**.\n\n{readiness['reason']}\n\n" + _md_table(checks) + "\n\nCaveats:\n\n" + _md_table([{"caveat": item} for item in state.get("caveats", [])])


def _md_table(rows: list[dict[str, Any]], max_rows: int = 40) -> str:
    if not rows:
        return "_No rows._"
    selected = rows[:max_rows]
    headers = sorted({key for row in selected for key in row})
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in selected:
        values = []
        for header in headers:
            value = row.get(header, "")
            if isinstance(value, (list, tuple, dict)):
                value = json.dumps(value, ensure_ascii=False, sort_keys=True, default=str)
            values.append(str(value).replace("\n", " ").replace("|", "/"))
        lines.append("| " + " | ".join(values) + " |")
    if len(rows) > max_rows:
        lines.append(f"\n_Truncated to first {max_rows} of {len(rows)} rows._")
    return "\n".join(lines)


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    headers = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in headers})


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True, default=str), encoding="utf-8")


def _write_md(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
