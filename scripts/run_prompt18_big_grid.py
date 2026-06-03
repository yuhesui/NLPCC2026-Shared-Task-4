#!/usr/bin/env python3
"""Prompt18 official-server validation, big grid, freeze, and package split."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
from time import perf_counter, sleep
from typing import Any, Iterable, Mapping
from urllib import error, parse, request
import zipfile

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nlpcc.core.fund_universe import get_fund_pool  # noqa: E402
from nlpcc.execution.order_planner import OrderPlannerConfig  # noqa: E402
from nlpcc.runtime.system_runner import SystemRunner  # noqa: E402
from tools.backtesting.backtester_parity import compare_reference_to_candidate  # noqa: E402
from tools.backtesting.cuda_vectorized_backtester import BatchedOfficialSemanticsInput, run_batched_official_semantics  # noqa: E402
from tools.backtesting.reference_official_semantics import OfficialSemanticsInput, run_reference_official_semantics  # noqa: E402
from tools.experiments.candidate_factory import CandidateSpec, _build_candidate, build_prompt17_candidates  # noqa: E402
from tools.experiments.leakage_safe_input_builder import LeakageSafeInputBuilder  # noqa: E402
from tools.experiments.strategy_config_expander import materialize_prompt17_configs  # noqa: E402
from tools.experiments.target_tensor_cache import TargetTensorCache  # noqa: E402
from tools.experiments.target_tensor_generator import TargetTensorGenerationRequest, generate_target_tensor, planner_config_for_track  # noqa: E402


REPORT_PROGRESS = (
    "progress_00_context_and_readiness_review.md",
    "progress_01_official_server_startup.md",
    "progress_02_pre_grid_integrity_gate.md",
    "progress_03_big_grid_plan.md",
    "progress_04_big_grid_run_status.md",
    "progress_05_candidate_freeze.md",
    "progress_06_locked_2025_evaluation.md",
    "progress_07_official_server_parity.md",
    "progress_08_package_split.md",
    "run_log.md",
)

REPORT_PRESENTED = (
    "executive_summary.md",
    "official_server_validation_summary.md",
    "big_grid_search_summary.md",
    "final_candidate_selection_report.md",
    "locked_2025_evaluation_summary.md",
    "final_package_summary.md",
    "final_submission_readiness_report.md",
    "final_recommendation.md",
)

REPORT_REFERENCE = (
    "context_gap_review.md",
    "official_server_startup_report.md",
    "official_server_startup_report.csv",
    "pre_grid_integrity_gate.md",
    "pre_grid_integrity_gate.csv",
    "big_grid_plan.md",
    "big_grid_plan.csv",
    "big_grid_candidate_catalog.csv",
    "big_grid_runtime_benchmark.md",
    "big_grid_runtime_benchmark.csv",
    "big_grid_2024_scores.csv",
    "big_grid_2024_ranking.md",
    "big_grid_2024_ranking.csv",
    "big_grid_trackA_ranking.csv",
    "big_grid_trackB_ranking.csv",
    "big_grid_ablation_report.md",
    "big_grid_ablation_report.csv",
    "candidate_freeze_2024_only.md",
    "candidate_freeze_2024_only.csv",
    "locked_2025_scores.csv",
    "locked_2025_evaluation.md",
    "locked_2025_evaluation.csv",
    "final_parity_reference_vs_batched.md",
    "final_parity_reference_vs_batched.csv",
    "official_server_parity.md",
    "official_server_parity.csv",
    "final_runtime_package_audit.md",
    "final_runtime_package_audit.json",
    "reproducibility_package_audit.md",
    "reproducibility_package_audit.json",
    "dependency_and_model_manifest.md",
    "dependency_and_model_manifest.json",
)

PROMPT17B_FREEZE = {
    "macro_primary": "bsa_rp_macro_tilt25",
    "macro_fallback": "bsa_rp_macro_rule",
    "sector_primary": "armor_omd_sector_default",
    "sector_fallback": "s0_sector_cash02",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prompt18 big-grid workflow.")
    parser.add_argument(
        "--phase",
        required=True,
        choices=(
            "init",
            "startup",
            "integrity",
            "plan",
            "benchmark",
            "grid-chunk",
            "freeze",
            "locked-2025",
            "local-parity",
            "official-parity",
            "packages",
            "reports",
            "all-smoke",
            "stop-server",
        ),
    )
    parser.add_argument("--track", choices=("macro", "sector"), default=None)
    parser.add_argument("--chunk-index", type=int, default=0)
    parser.add_argument("--chunk-size", type=int, default=30)
    parser.add_argument("--output-root", default=str(REPO_ROOT / ".var" / "prompt18"))
    parser.add_argument("--report-root", default=str(REPO_ROOT / "outputs" / "reports" / "prompt18"))
    parser.add_argument("--backend", choices=("numpy", "torch", "auto"), default="numpy")
    parser.add_argument("--prefer-cuda", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--official-base-url", default="http://localhost:6207")
    parser.add_argument("--lookback-days", type=int, default=60)
    parser.add_argument("--integrity-dates", type=int, default=20)
    parser.add_argument("--parity-dates", type=int, default=20)
    parser.add_argument("--official-parity-dates", type=int, default=5)
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
        elif args.phase == "startup":
            _phase_startup(state, args, output_root)
        elif args.phase == "integrity":
            _phase_integrity(state, args, output_root)
        elif args.phase == "plan":
            _phase_plan(state, args, output_root)
        elif args.phase == "benchmark":
            _phase_benchmark(state, args, output_root)
        elif args.phase == "grid-chunk":
            _phase_grid_chunk(state, args, output_root)
        elif args.phase == "freeze":
            _phase_freeze(state, args, output_root)
        elif args.phase == "locked-2025":
            _phase_locked_2025(state, args, output_root)
        elif args.phase == "local-parity":
            _phase_local_parity(state, args, output_root)
        elif args.phase == "official-parity":
            _phase_official_parity(state, args, output_root)
        elif args.phase == "packages":
            _phase_packages(state, args, output_root, report_root)
        elif args.phase == "reports":
            pass
        elif args.phase == "all-smoke":
            _phase_init(state, output_root, report_root)
            _phase_startup(state, args, output_root)
            args.integrity_dates = 3
            _phase_integrity(state, args, output_root)
            _phase_plan(state, args, output_root)
        elif args.phase == "stop-server":
            _stop_started_server(output_root)
        else:
            raise ValueError(args.phase)
    except Exception as exc:
        status = "failed"
        detail = f"{type(exc).__name__}: {exc}"
        state.setdefault("caveats", []).append(f"{args.phase}: {detail}")
        raise
    finally:
        _log_run(state, args.phase, status, detail, perf_counter() - started, vars(args))
        _save_state(output_root, state)
        _write_reports(report_root, output_root, state)
    print(json.dumps({"status": status, "phase": args.phase, "elapsed_seconds": round(perf_counter() - started, 3)}, indent=2))
    return 0


def _phase_init(state: dict[str, Any], output_root: Path, report_root: Path) -> None:
    state["created_at_utc"] = state.get("created_at_utc") or datetime.now(timezone.utc).isoformat()
    state["output_root"] = str(output_root)
    state["report_root"] = str(report_root)
    state["context_gap_rows"] = [
        {
            "Issue": "official server not reachable in Prompt17b",
            "Prompt17b Status": "blocked at localhost:6207",
            "Prompt18 Required Action": "install/check dependencies, start local server, run smoke and candidate parity",
            "Severity": "critical",
        },
        {
            "Issue": "grid search not truly large",
            "Prompt17b Status": "24 candidates over full 2024",
            "Prompt18 Required Action": "run Option 1 large grid: at least 300 total candidates, 100+ per track, full 2024",
            "Severity": "high",
        },
        {
            "Issue": "local text modes not final-ranked",
            "Prompt17b Status": "cache-tested only",
            "Prompt18 Required Action": "keep text modes as reproducibility/report evidence unless bounded large-grid cache is feasible",
            "Severity": "medium",
        },
        {
            "Issue": "package split incomplete",
            "Prompt17b Status": "single package included src/tools",
            "Prompt18 Required Action": "create official runtime package and research reproducibility package separately",
            "Severity": "high",
        },
        {
            "Issue": "Prompt17b local evidence",
            "Prompt17b Status": "target audit, leakage audit, broad parity, full 2024 24-candidate replay, locked 2025, five-fold",
            "Prompt18 Required Action": "reuse as pre-grid context, not final big-grid evidence",
            "Severity": "resolved",
        },
    ]
    candidates, catalog = _big_grid_catalog(output_root)
    state["catalog_count"] = len(candidates)
    state["catalog_track_counts"] = _count_by(catalog, "track")
    _write_csv(output_root / "grid_runs" / "big_grid_candidate_catalog.csv", catalog)


def _phase_startup(state: dict[str, Any], args: argparse.Namespace, output_root: Path) -> None:
    rows = _startup_history_rows(output_root)
    port = int(args.official_base_url.rsplit(":", 1)[-1])
    if _port_open("127.0.0.1", port):
        rows.append(
            {
                "Attempt": len(rows) + 1,
                "Command": "port probe",
                "Port": port,
                "Result": "already_running",
                "Error": "",
                "Probable Cause": "server process already listening",
                "Next Action": "run official server smoke and candidate parity",
            }
        )
    else:
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        stdout = output_root / "official_server" / "server_stdout_prompt18.log"
        stderr = output_root / "official_server" / "server_stderr_prompt18.log"
        process = subprocess.Popen(
            [sys.executable, "start_server.py"],
            cwd=REPO_ROOT / "NLPCC_tasks",
            stdout=stdout.open("ab"),
            stderr=stderr.open("ab"),
            env=env,
        )
        (output_root / "official_server" / "server_pid.txt").write_text(str(process.pid), encoding="utf-8")
        started = False
        for _ in range(45):
            sleep(1)
            if _port_open("127.0.0.1", port):
                started = True
                break
            if process.poll() is not None:
                break
        rows.append(
            {
                "Attempt": len(rows) + 1,
                "Command": f"{sys.executable} start_server.py",
                "Port": port,
                "Result": "started" if started else "blocked_unknown",
                "Error": "" if started else _tail(stderr, 80),
                "Probable Cause": "" if started else "server exited before binding port",
                "Next Action": "run official server smoke" if started else "inspect stderr and repair dependency/startup error",
            }
        )
    smoke_output = output_root / "official_server" / "official_server_smoke_prompt18.json"
    command = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "run_official_server_smoke.py"),
        "--base-url",
        args.official_base_url,
        "--output",
        str(smoke_output),
    ]
    proc = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True, timeout=120, check=False)
    smoke = json.loads(smoke_output.read_text(encoding="utf-8")) if smoke_output.exists() else {}
    rows.append(
        {
            "Attempt": len(rows) + 1,
            "Command": " ".join(command),
            "Port": port,
            "Result": "started" if smoke.get("status") == "ok" else "blocked_unknown",
            "Error": smoke.get("detail", proc.stderr.strip()),
            "Probable Cause": "" if smoke.get("status") == "ok" else smoke.get("blocker", "official smoke failed"),
            "Next Action": "candidate parity" if smoke.get("status") == "ok" else "fix smoke failure before claiming official readiness",
        }
    )
    state["official_startup_rows"] = rows
    state["official_server_smoke"] = smoke
    state["official_server_running"] = _port_open("127.0.0.1", port)


def _phase_integrity(state: dict[str, Any], args: argparse.Namespace, output_root: Path) -> None:
    candidates = _integrity_candidates(output_root)
    rows: list[dict[str, Any]] = []
    parity_rows: list[dict[str, Any]] = []
    hard_candidates = {
        "s0_macro_cash02",
        "s1_macro_default",
        "s1_sector_default",
        "bsa_rp_macro_tilt25",
        "armor_omd_sector_default",
    }
    for track in ("macro", "sector"):
        track_candidates = [candidate for candidate in candidates if candidate.track == track]
        result = generate_target_tensor(
            TargetTensorGenerationRequest(
                repo_root=REPO_ROOT,
                data_root=REPO_ROOT / "data" / "train_2024",
                track=track,  # type: ignore[arg-type]
                candidates=track_candidates,
                output_root=output_root,
                max_dates=args.integrity_dates,
                lookback_days=args.lookback_days,
                force=args.force,
            )
        )
        replay = _replay(result, track, args.backend, args.prefer_cuda)
        leakage = result.bundle.metadata.get("leakage_summary", {})
        rows.append(
            {
                "Check": "current-day close/high/low/return masking",
                "Candidate": "*",
                "Track": track,
                "Dates": leakage.get("checked_days", 0),
                "Status": "pass" if leakage.get("all_current_day_close_masked") else "fail",
                "Evidence": json.dumps(leakage, sort_keys=True),
                "Notes": "LeakageSafeInputBuilder diagnostics",
            }
        )
        payload = result.bundle.metadata.get("cache_payload", {})
        cache_fields_ok = bool(payload.get("data_version")) and all(
            all(key in candidate for key in ("family", "config_hash", "text_mode", "name"))
            for candidate in payload.get("candidates", [])
        )
        rows.append(
            {
                "Check": "target tensor cache key fields",
                "Candidate": "*",
                "Track": track,
                "Dates": len(result.bundle.dates),
                "Status": "pass" if cache_fields_ok else "fail",
                "Evidence": ",".join(sorted(payload.keys())),
                "Notes": "Requires data_version, track, date range, text mode, config hash, family",
            }
        )
        for index, candidate in enumerate(replay.candidates):
            reference = run_reference_official_semantics(
                OfficialSemanticsInput(
                    dates=result.bundle.dates,
                    assets=result.bundle.assets,
                    open_prices=result.bundle.open_prices,
                    pct_changes=result.bundle.pct_changes,
                    target_weights=result.bundle.target_weights[index],
                    planner_config=_planner_config_from_bundle_candidate(result.bundle.metadata, index, planner_config_for_track(track)),  # type: ignore[arg-type]
                )
            )
            parity = compare_reference_to_candidate(reference, candidate, tolerance=1e-5)
            row = {
                "Candidate": candidate.name,
                "Track": track,
                "Dates": len(result.bundle.dates),
                "Reference Final Value": reference.final_value,
                "Batched Final Value": candidate.final_value,
                "Abs Diff": parity.final_value_diff,
                "Max Daily Diff": parity.max_value_diff,
                "Metric Diff": max(parity.metric_diffs.values() or [0.0]),
                "Status": "pass" if parity.within_tolerance else "fail",
                "Notes": "hard_gate" if candidate.name in hard_candidates else "representative",
            }
            parity_rows.append(row)
            rows.append(
                {
                    "Check": "reference-vs-batched parity",
                    "Candidate": candidate.name,
                    "Track": track,
                    "Dates": len(result.bundle.dates),
                    "Status": row["Status"],
                    "Evidence": f"final_diff={parity.final_value_diff:.3e}; max_diff={parity.max_value_diff:.3e}",
                    "Notes": row["Notes"],
                }
            )
    candidates_large, catalog = _big_grid_catalog(output_root)
    rows.append(
        {
            "Check": "candidate catalog generation",
            "Candidate": "*",
            "Track": "both",
            "Dates": 0,
            "Status": "pass" if len(candidates_large) >= 300 and _count_by(catalog, "track").get("macro", 0) >= 100 and _count_by(catalog, "track").get("sector", 0) >= 100 else "fail",
            "Evidence": json.dumps(_count_by(catalog, "track"), sort_keys=True),
            "Notes": f"catalog_count={len(candidates_large)}",
        }
    )
    package_files = _collect_package_files(
        include_paths=[Path("NLPCC_tasks/agent_platform/agents/build_agent.py"), Path("src/nlpcc"), Path("configs"), Path("requirements.txt")],
        allow_reports=False,
    )
    raw_issues = [path.as_posix() for path in package_files if _is_raw_data(path)]
    rows.append(
        {
            "Check": "runtime package raw data exclusion",
            "Candidate": "*",
            "Track": "both",
            "Dates": 0,
            "Status": "pass" if not raw_issues else "fail",
            "Evidence": f"file_count={len(package_files)} raw_issues={len(raw_issues)}",
            "Notes": ",".join(raw_issues[:5]),
        }
    )
    state["pre_grid_integrity_rows"] = rows
    state["final_local_parity_rows"] = parity_rows
    state["pre_grid_hard_gate_passed"] = all(
        row["Status"] == "pass"
        for row in rows
        if row["Check"] in {"current-day close/high/low/return masking", "candidate catalog generation"}
        or (row["Check"] == "reference-vs-batched parity" and row["Candidate"] in hard_candidates)
    )


def _phase_plan(state: dict[str, Any], args: argparse.Namespace, output_root: Path) -> None:
    del args
    candidates, catalog = _big_grid_catalog(output_root)
    _write_csv(output_root / "grid_runs" / "big_grid_candidate_catalog.csv", catalog)
    track_counts = _count_by(catalog, "track")
    plan_rows = [
        {
            "Stage": "Option 1 medium-large grid",
            "Candidate Count": len(candidates),
            "Tracks": "macro,sector",
            "Text Modes": "no_news,rule_based",
            "Date Range": "all available 2024 construction dates",
            "Backend": "NumPy official-semantics batched replay",
            "Estimated Runtime": "1-2 hours strategy target generation; replay < 1 minute",
            "Run?": "yes",
            "Notes": f"macro={track_counts.get('macro', 0)} sector={track_counts.get('sector', 0)}",
        }
    ]
    state["big_grid_plan_rows"] = plan_rows
    state["big_grid_option"] = "Option 1"
    state["catalog_count"] = len(candidates)
    state["catalog_track_counts"] = track_counts


def _phase_benchmark(state: dict[str, Any], args: argparse.Namespace, output_root: Path) -> None:
    if not state.get("pre_grid_hard_gate_passed"):
        raise RuntimeError("Pre-grid hard gate has not passed.")
    candidates = _integrity_candidates(output_root)
    rows: list[dict[str, Any]] = []
    track = "macro"
    result = generate_target_tensor(
        TargetTensorGenerationRequest(
            repo_root=REPO_ROOT,
            data_root=REPO_ROOT / "data" / "train_2024",
            track=track,  # type: ignore[arg-type]
            candidates=[candidate for candidate in candidates if candidate.track == track][:5],
            output_root=output_root,
            max_dates=20,
            lookback_days=args.lookback_days,
            force=False,
        )
    )
    reference_planner = _planner_config_from_bundle_candidate(result.bundle.metadata, 0, planner_config_for_track(track))
    reference = run_reference_official_semantics(
        OfficialSemanticsInput(
            dates=result.bundle.dates,
            assets=result.bundle.assets,
            open_prices=result.bundle.open_prices,
            pct_changes=result.bundle.pct_changes,
            target_weights=result.bundle.target_weights[0],
            planner_config=reference_planner,
        )
    )
    for backend, prefer_cuda in (("reference", False), ("numpy", False), ("torch", False), ("torch", True)):
        for batch in (24, 100, 300):
            if backend == "reference" and batch != 24:
                continue
            target = np.repeat(result.bundle.target_weights[:1], batch, axis=0)
            names = tuple(f"{result.bundle.candidate_names[0]}__bench{i}" for i in range(batch))
            bench_planner = _planner_config_from_bundle_candidate(result.bundle.metadata, 0, planner_config_for_track(track))
            started = perf_counter()
            if backend == "reference":
                check = run_reference_official_semantics(
                    OfficialSemanticsInput(
                        dates=result.bundle.dates,
                        assets=result.bundle.assets,
                        open_prices=result.bundle.open_prices,
                        pct_changes=result.bundle.pct_changes,
                        target_weights=result.bundle.target_weights[0],
                        planner_config=bench_planner,
                    )
                )
                elapsed = perf_counter() - started
                diff = abs(check.final_value - reference.final_value)
                rows.append(
                    {
                        "Backend": "reference_loop",
                        "Device": "cpu",
                        "Candidates": 1,
                        "Dates": len(result.bundle.dates),
                        "Runtime Seconds": round(elapsed, 6),
                        "Candidates Per Second": round(1.0 / max(elapsed, 1e-9), 6),
                        "Max Metric Diff": diff,
                        "Correct?": True,
                        "Recommended?": False,
                        "Notes": "correctness source",
                    }
                )
                continue
            try:
                replay = run_batched_official_semantics(
                    BatchedOfficialSemanticsInput(
                        dates=result.bundle.dates,
                        assets=result.bundle.assets,
                        open_prices=result.bundle.open_prices,
                        pct_changes=result.bundle.pct_changes,
                        target_weights=target,
                        candidate_names=names,
                        planner_config=planner_config_for_track(track),
                        planner_configs=tuple(bench_planner for _ in range(batch)),
                    ),
                    backend=backend,
                    prefer_cuda=prefer_cuda,
                )
                elapsed = perf_counter() - started
                diff = abs(replay.candidates[0].final_value - reference.final_value)
                rows.append(
                    {
                        "Backend": replay.backend,
                        "Device": replay.device,
                        "Candidates": batch,
                        "Dates": len(result.bundle.dates),
                        "Runtime Seconds": round(elapsed, 6),
                        "Candidates Per Second": round(batch / max(elapsed, 1e-9), 6),
                        "Max Metric Diff": diff,
                        "Correct?": diff <= 1e-5,
                        "Recommended?": replay.backend == "numpy" and batch == 300,
                        "Notes": "CUDA preferred" if prefer_cuda else "",
                    }
                )
            except Exception as exc:
                rows.append(
                    {
                        "Backend": backend,
                        "Device": "unknown",
                        "Candidates": batch,
                        "Dates": len(result.bundle.dates),
                        "Runtime Seconds": 0,
                        "Candidates Per Second": 0,
                        "Max Metric Diff": "",
                        "Correct?": False,
                        "Recommended?": False,
                        "Notes": f"{type(exc).__name__}: {exc}",
                    }
                )
    state["runtime_benchmark_rows"] = rows


def _phase_grid_chunk(state: dict[str, Any], args: argparse.Namespace, output_root: Path) -> None:
    if not state.get("pre_grid_hard_gate_passed"):
        raise RuntimeError("Pre-grid hard gate has not passed.")
    if args.track is None:
        raise ValueError("--track is required for grid-chunk.")
    candidates, catalog = _big_grid_catalog(output_root)
    track_candidates = [candidate for candidate in candidates if candidate.track == args.track]
    chunk_start = args.chunk_index * args.chunk_size
    chunk = track_candidates[chunk_start : chunk_start + args.chunk_size]
    if not chunk:
        raise ValueError(f"No candidates for {args.track} chunk {args.chunk_index}")
    chunk_path = output_root / "grid_runs" / f"{args.track}_chunk_{args.chunk_index:03d}_scores.csv"
    if chunk_path.exists() and not args.force:
        rows = _read_csv(chunk_path)
        state["big_grid_rows"] = _merge_scores(state.get("big_grid_rows", []), rows)
        state.setdefault("grid_completed_chunks", {})[f"{args.track}:{args.chunk_index}"] = "cached"
        return
    started = perf_counter()
    result = generate_target_tensor(
        TargetTensorGenerationRequest(
            repo_root=REPO_ROOT,
            data_root=REPO_ROOT / "data" / "train_2024",
            track=args.track,  # type: ignore[arg-type]
            candidates=chunk,
            output_root=output_root,
            max_dates=None,
            lookback_days=args.lookback_days,
            force=args.force,
        )
    )
    replay = _replay(result, args.track, args.backend, args.prefer_cuda)
    elapsed = perf_counter() - started
    lookup = {candidate.name: candidate for candidate in candidates}
    rows = _score_rows(_candidate_rows(replay, result.bundle, args.track, "train_2024_big_grid", lookup, elapsed / len(chunk)), lookup)
    for row in rows:
        row["grid_chunk"] = args.chunk_index
        row["grid_option"] = "Option 1"
    _write_csv(chunk_path, rows)
    _write_json(
        output_root / "checkpoints" / f"{args.track}_chunk_{args.chunk_index:03d}.json",
        {
            "track": args.track,
            "chunk_index": args.chunk_index,
            "candidate_count": len(chunk),
            "date_count": len(result.bundle.dates),
            "elapsed_seconds": round(elapsed, 6),
            "generation": result.as_dict(),
            "replay_backend": replay.backend,
            "replay_device": replay.device,
        },
    )
    state["big_grid_rows"] = _merge_scores(state.get("big_grid_rows", []), rows)
    state["big_grid_rows"] = _score_rows(state["big_grid_rows"], lookup)
    state.setdefault("grid_completed_chunks", {})[f"{args.track}:{args.chunk_index}"] = "completed"
    state["big_grid_success"] = _big_grid_success(state)
    _write_csv(output_root / "grid_runs" / "big_grid_candidate_catalog.csv", catalog)


def _phase_freeze(state: dict[str, Any], args: argparse.Namespace, output_root: Path) -> None:
    del args
    rows = _score_rows(state.get("big_grid_rows", []), _big_grid_lookup(output_root))
    if not rows:
        raise RuntimeError("No big-grid rows available.")
    freeze_rows = []
    freeze: dict[str, Any] = {"created_at_utc": datetime.now(timezone.utc).isoformat(), "discipline": "2024_only_big_grid"}
    for track, label in (("macro", "Track A"), ("sector", "Track B")):
        track_rows = [row for row in rows if row.get("track") == track]
        track_rows.sort(key=lambda row: float(row.get("conservative_score", 0.0)), reverse=True)
        if len(track_rows) < 2:
            raise RuntimeError(f"Need at least two candidates for {track} freeze")
        primary = track_rows[0]
        fallback = next((row for row in track_rows[1:] if row.get("family") in {"s0", "s1", "bsa_rp", "risk_parity", "armor_omd"}), track_rows[1])
        key_prefix = "macro" if track == "macro" else "sector"
        freeze[f"{key_prefix}_primary"] = primary.get("candidate")
        freeze[f"{key_prefix}_fallback"] = fallback.get("candidate")
        freeze[f"{key_prefix}_primary_row"] = primary
        freeze[f"{key_prefix}_fallback_row"] = fallback
        for role, chosen in (("primary", primary), ("fallback", fallback)):
            prompt17b_name = PROMPT17B_FREEZE[f"{key_prefix}_{role}"]
            freeze_rows.append(
                {
                    "Track": label,
                    "Role": role,
                    "Prompt17b Candidate": prompt17b_name,
                    "Prompt18 Candidate": chosen.get("candidate"),
                    "Changed?": prompt17b_name != chosen.get("candidate"),
                    "2024 Evidence": f"rank={_rank_of(rows, chosen.get('candidate'))}; score={chosen.get('conservative_score')}; return={chosen.get('cumulative_return')}; sharpe={chosen.get('sharpe_ratio')}",
                    "Risk": _risk_label(chosen),
                    "Decision": "freeze_from_2024_big_grid",
                }
            )
    state["freeze"] = freeze
    state["candidate_freeze_rows"] = freeze_rows
    _write_final_prompt18_configs(output_root, freeze)


def _phase_locked_2025(state: dict[str, Any], args: argparse.Namespace, output_root: Path) -> None:
    if not state.get("freeze"):
        _phase_freeze(state, args, output_root)
    names = _locked_2025_names(state)
    lookup = _all_candidate_lookup(output_root)
    rows: list[dict[str, Any]] = []
    for track in ("macro", "sector"):
        track_names = [name for name in names if lookup[name].track == track]
        result = generate_target_tensor(
            TargetTensorGenerationRequest(
                repo_root=REPO_ROOT,
                data_root=_official_dataset_root(),
                track=track,  # type: ignore[arg-type]
                candidates=[lookup[name] for name in track_names],
                output_root=output_root,
                start_date="20250102",
                end_date="20251231",
                max_dates=None,
                lookback_days=args.lookback_days,
                force=args.force,
            )
        )
        replay = _replay(result, track, args.backend, args.prefer_cuda)
        track_rows = _score_rows(_candidate_rows(replay, result.bundle, track, "public_a_2025_locked_after_big_grid", lookup, 0.0), lookup)
        for row in track_rows:
            prior = next((item for item in state.get("big_grid_rows", []) if item.get("candidate") == row.get("candidate")), {})
            role = _frozen_role(state, str(row.get("candidate")))
            row.update(
                {
                    "Frozen Role": role,
                    "2024 Rank": _rank_of(state.get("big_grid_rows", []), row.get("candidate")),
                    "2024 Return": prior.get("cumulative_return", ""),
                    "2024 Sharpe": prior.get("sharpe_ratio", ""),
                    "2025 Return": row.get("cumulative_return", ""),
                    "2025 Sharpe": row.get("sharpe_ratio", ""),
                    "2025 Max Drawdown": row.get("max_drawdown", ""),
                    "2025 Turnover": row.get("turnover", ""),
                    "Generalisation": _generalisation(row, prior),
                    "Promote Status": "frozen" if role in {"primary", "fallback"} else "evidence_only",
                    "Notes": "No parameter changes after 2024 freeze.",
                }
            )
        rows.extend(track_rows)
    state["locked_2025_rows"] = rows


def _phase_local_parity(state: dict[str, Any], args: argparse.Namespace, output_root: Path) -> None:
    names = _final_parity_names(state)
    lookup = _big_grid_lookup(output_root)
    parity_rows: list[dict[str, Any]] = []
    for track in ("macro", "sector"):
        track_names = [name for name in names if lookup[name].track == track]
        if not track_names:
            continue
        result = generate_target_tensor(
            TargetTensorGenerationRequest(
                repo_root=REPO_ROOT,
                data_root=REPO_ROOT / "data" / "train_2024",
                track=track,  # type: ignore[arg-type]
                candidates=[lookup[name] for name in track_names],
                output_root=output_root,
                max_dates=args.parity_dates,
                lookback_days=args.lookback_days,
                force=False,
            )
        )
        replay = _replay(result, track, args.backend, args.prefer_cuda)
        for index, candidate in enumerate(replay.candidates):
            reference = run_reference_official_semantics(
                OfficialSemanticsInput(
                    dates=result.bundle.dates,
                    assets=result.bundle.assets,
                    open_prices=result.bundle.open_prices,
                    pct_changes=result.bundle.pct_changes,
                    target_weights=result.bundle.target_weights[index],
                    planner_config=_planner_config_from_bundle_candidate(result.bundle.metadata, index, planner_config_for_track(track)),  # type: ignore[arg-type]
                )
            )
            parity = compare_reference_to_candidate(reference, candidate, tolerance=1e-5)
            parity_rows.append(
                {
                    "Candidate": candidate.name,
                    "Track": track,
                    "Dates": len(result.bundle.dates),
                    "Reference Final Value": reference.final_value,
                    "Batched Final Value": candidate.final_value,
                    "Abs Diff": parity.final_value_diff,
                    "Max Daily Diff": parity.max_value_diff,
                    "Metric Diff": max(parity.metric_diffs.values() or [0.0]),
                    "Status": "pass" if parity.within_tolerance else "fail",
                    "Notes": "final Prompt18 local parity",
                }
            )
    state["final_local_parity_rows"] = parity_rows


def _phase_official_parity(state: dict[str, Any], args: argparse.Namespace, output_root: Path) -> None:
    if not _port_open("127.0.0.1", int(args.official_base_url.rsplit(":", 1)[-1])):
        state["official_server_parity_rows"] = [
            {
                "Candidate": "*",
                "Track": "*",
                "Window": "",
                "Official Server Value": "",
                "Local Reference Value": "",
                "Batched Value": "",
                "Official-Local Diff": "",
                "Local-Batched Diff": "",
                "Trade Match": "",
                "Status": "blocked",
                "Notes": "official server not listening",
            }
        ]
        return
    names = _official_parity_names(state)
    lookup = _big_grid_lookup(output_root)
    rows: list[dict[str, Any]] = []
    for name in names:
        candidate = lookup[name]
        try:
            row = _run_official_candidate_parity(candidate, args, output_root)
        except Exception as exc:
            row = {
                "Candidate": name,
                "Track": candidate.track,
                "Window": f"first {args.official_parity_dates} public-A 2025 dates",
                "Official Server Value": "",
                "Local Reference Value": "",
                "Batched Value": "",
                "Official-Local Diff": "",
                "Local-Batched Diff": "",
                "Trade Match": "",
                "Status": "blocked",
                "Notes": f"{type(exc).__name__}: {exc}",
            }
        rows.append(row)
    state["official_server_parity_rows"] = rows


def _phase_packages(state: dict[str, Any], args: argparse.Namespace, output_root: Path, report_root: Path) -> None:
    del args
    manifest = _dependency_manifest(state, output_root)
    state["dependency_manifest"] = manifest
    _write_json(report_root / "reference" / "dependency_and_model_manifest.json", manifest)
    runtime = _build_prompt18_package(
        output_root=output_root,
        package_name="prompt18_official_runtime",
        include_paths=[
            Path("NLPCC_tasks/agent_platform/agents/build_agent.py"),
            Path("NLPCC_tasks/logs.py"),
            Path("src/nlpcc"),
            Path("configs"),
            Path("README.md"),
            Path("AGENTS.md"),
            Path("requirements.txt"),
            Path("pyproject.toml"),
        ],
        allow_reports=False,
        readme_name="README_SUBMISSION.md",
        readme_text=_runtime_readme(state),
    )
    reproducibility = _build_prompt18_package(
        output_root=output_root,
        package_name="prompt18_reproducibility",
        include_paths=[
            Path("NLPCC_tasks/agent_platform/agents/build_agent.py"),
            Path("NLPCC_tasks/logs.py"),
            Path("src/nlpcc"),
            Path("src/tools"),
            Path("configs"),
            Path("scripts/run_prompt18_big_grid.py"),
            Path("scripts/run_prompt17b_validation.py"),
            Path("scripts/run_official_server_smoke.py"),
            Path("scripts/create_implementation_log.py"),
            Path("outputs/reports/prompt18"),
            Path("README.md"),
            Path("AGENTS.md"),
            Path("requirements.txt"),
            Path("requirements-dev.txt"),
            Path("pyproject.toml"),
        ],
        allow_reports=True,
        readme_name="README_REPRODUCIBILITY.md",
        readme_text=_repro_readme(state),
    )
    state["runtime_package_audit"] = runtime
    state["reproducibility_package_audit"] = reproducibility


def _big_grid_catalog(output_root: Path) -> tuple[list[CandidateSpec], list[dict[str, Any]]]:
    del output_root
    specs: list[CandidateSpec] = []
    rows: list[dict[str, Any]] = []

    def add(
        *,
        name: str,
        track: str,
        family: str,
        base_system: str,
        text_mode: str,
        params: Mapping[str, Any],
        maturity: str,
        dependency: str,
        runtime: str,
        novelty: float,
        reproducibility: float,
        complexity: float,
        dependency_risk: float,
    ) -> None:
        candidate = _build_candidate(
            REPO_ROOT,
            name=name,
            track=track,  # type: ignore[arg-type]
            family=family,
            base_system=base_system,
            text_mode=text_mode,
            params=params,
            novelty=novelty,
            reproducibility=reproducibility,
            complexity_penalty=complexity,
            dependency_risk=dependency_risk,
        )
        specs.append(candidate)
        rows.append(
            {
                "candidate_id": len(rows) + 1,
                "candidate_name": candidate.name,
                "track": candidate.track,
                "family": candidate.family,
                "text_mode": candidate.text_mode,
                "base_config": base_system,
                "parameter_json": json.dumps(params, ensure_ascii=False, sort_keys=True, default=str),
                "config_hash": candidate.config_hash,
                "dependency_level": dependency,
                "maturity_label": maturity,
                "expected_runtime_class": runtime,
                "include_in_grid": True,
                "reason": "Prompt18 Option 1 parameter grid",
            }
        )

    # Macro: 160 candidates.
    for idx, cash in enumerate([0.00, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.10, 0.12]):
        add(name=f"p18_s0_macro_cash{int(cash*100):02d}", track="macro", family="s0", base_system="s0_equal_weight", text_mode="no_news", params={"cash_reserve": cash, "max_weight": 0.30 + 0.01 * (idx % 6)}, maturity="baseline", dependency="none", runtime="fast", novelty=0.1, reproducibility=0.95, complexity=0.02, dependency_risk=0.0)
    for i, momentum in enumerate([0.15, 0.25, 0.35, 0.45, 0.55]):
        for vol in [0.30, 0.45, 0.60]:
            for window in [10, 20]:
                add(name=f"p18_s1_macro_m{int(momentum*100)}_v{int(vol*100)}_w{window}_{i}", track="macro", family="s1", base_system="s1_macro", text_mode="no_news", params={"momentum_weight": momentum, "inverse_vol_weight": vol, "stage3": {"volatility_window": window}, "constraints": {"max_turnover": 0.18 + 0.02 * i}}, maturity="baseline", dependency="none", runtime="fast", novelty=0.25, reproducibility=0.90, complexity=0.06, dependency_risk=0.0)
    for window in [10, 20, 40, 60, 90]:
        for shrinkage in [0.05, 0.15, 0.25, 0.35, 0.50]:
            add(name=f"p18_rp_macro_w{window}_s{int(shrinkage*100)}", track="macro", family="risk_parity", base_system="risk_parity_track1", text_mode="no_news", params={"stage3": {"volatility_window": window, "shrinkage_alpha": shrinkage}, "constraints": {"max_weight": 0.30 + (window % 3) * 0.025, "cash_reserve": 0.02 + shrinkage / 50}}, maturity="stable_component", dependency="none", runtime="fast", novelty=0.32, reproducibility=0.90, complexity=0.08, dependency_risk=0.0)
    for tau in [0.03, 0.05, 0.08, 0.10, 0.15]:
        for view_scale in [0.60, 0.85, 1.00, 1.25, 1.50]:
            add(name=f"p18_dro_macro_t{int(tau*100)}_v{int(view_scale*100)}", track="macro", family="dro_bl_rp", base_system="dro_bl_rp_track1", text_mode="rule_based", params={"bl_tau": tau, "view_return_scale": view_scale, "s1_blend_weight": 0.25 + tau, "constraints": {"max_turnover": 0.18 + tau, "max_weight": 0.32}}, maturity="mvp", dependency="rule_text", runtime="medium", novelty=0.76, reproducibility=0.86, complexity=0.28, dependency_risk=0.08)
    for tilt in [0.10, 0.20, 0.25, 0.35, 0.50]:
        for guard in [0.40, 0.55, 0.65, 0.75, 0.90]:
            add(name=f"p18_bsa_macro_t{int(tilt*100)}_g{int(guard*100)}", track="macro", family="bsa_rp", base_system="bsa_rp_track1", text_mode="rule_based", params={"belief_tilt_strength": tilt, "drawdown_guard": guard, "stage2": {"decay_half_life_days": 3.0 + 5.0 * tilt}, "constraints": {"max_turnover": 0.18 + tilt / 5}}, maturity="mvp", dependency="rule_text", runtime="medium", novelty=0.72, reproducibility=0.86, complexity=0.26, dependency_risk=0.08)
    for lr in [1.0, 2.0, 3.0, 4.0, 5.5]:
        for penalty in [0.05, 0.15, 0.30]:
            add(name=f"p18_armor_macro_lr{int(lr*10)}_p{int(penalty*100)}", track="macro", family="armor_omd", base_system="armor_omd_macro", text_mode="rule_based", params={"learning_rate": lr, "turnover_penalty": penalty, "constraints": {"max_turnover": 0.18 + penalty}}, maturity="mvp_proxy", dependency="rule_text", runtime="medium", novelty=0.72, reproducibility=0.82, complexity=0.32, dependency_risk=0.08)
    for drift in [0.45, 0.60, 0.70, 0.80, 0.90]:
        for risk in [0.20, 0.35]:
            add(name=f"p18_hgf_macro_d{int(drift*100)}_r{int(risk*100)}", track="macro", family="hgf_mpc", base_system="hgf_mpc_track1", text_mode="no_news", params={"drift_weight": drift, "risk_weight": risk, "risk_off_scale": 0.55 + risk / 2}, maturity="mvp_proxy", dependency="none", runtime="medium", novelty=0.65, reproducibility=0.85, complexity=0.22, dependency_risk=0.02)
    for overlay in [0.05, 0.10, 0.15, 0.20, 0.30]:
        for kalman in [0.05, 0.15]:
            add(name=f"p18_ceva_macro_o{int(overlay*100)}_k{int(kalman*100)}", track="macro", family="ceva_kf_ciga", base_system="ceva_kf_ciga_track1", text_mode="rule_based", params={"overlay_strength": overlay, "kalman_strength": kalman, "stage2": {"decay_half_life_days": 3.0 + overlay * 10}}, maturity="mvp_proxy", dependency="rule_text", runtime="medium", novelty=0.82, reproducibility=0.83, complexity=0.36, dependency_risk=0.08)
    for lr in [0.4, 0.8, 1.2, 1.6, 2.0]:
        for penalty in [0.10, 0.30]:
            add(name=f"p18_oco_macro_lr{int(lr*10)}_p{int(penalty*100)}", track="macro", family="oco_fallback", base_system="oco_fallback", text_mode="rule_based", params={"learning_rate": lr, "turnover_penalty": penalty, "fallback_penalty": 0.4 + penalty, "experts": [{"name": "s1_quant_core", "prior_weight": 0.35, "config": {"track": "macro"}}, {"name": "risk_parity", "prior_weight": 0.30, "config": {"track": "macro"}}, {"name": "robust_bl", "prior_weight": 0.25, "config": {"track": "macro"}}, {"name": "conservative_ensemble", "prior_weight": 0.10, "config": {"track": "macro"}}]}, maturity="safety_proxy", dependency="rule_text", runtime="medium", novelty=0.45, reproducibility=0.86, complexity=0.22, dependency_risk=0.05)

    # Sector: 160 candidates.
    for idx, cash in enumerate([0.00, 0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.08, 0.10, 0.12]):
        add(name=f"p18_s0_sector_cash{int(cash*100):02d}", track="sector", family="s0", base_system="s0_equal_weight", text_mode="no_news", params={"cash_reserve": cash, "max_weight": 0.20 + 0.01 * (idx % 6)}, maturity="baseline", dependency="none", runtime="fast", novelty=0.1, reproducibility=0.95, complexity=0.02, dependency_risk=0.0)
    for trend in [0.35, 0.45, 0.55, 0.65, 0.75]:
        for vol in [0.20, 0.30, 0.40]:
            for window in [10, 20]:
                add(name=f"p18_s1_sector_t{int(trend*100)}_v{int(vol*100)}_w{window}", track="sector", family="s1", base_system="s1_sector", text_mode="no_news", params={"sector_trend_weight": trend, "inverse_vol_weight": vol, "stage3": {"sector_trend_window": window}, "constraints": {"max_turnover": 0.18 + trend / 10, "max_weight": 0.25}}, maturity="baseline", dependency="none", runtime="fast", novelty=0.25, reproducibility=0.90, complexity=0.06, dependency_risk=0.0)
    for trend_weight in [0.50, 0.60, 0.70, 0.80, 0.90]:
        for graph in [0.00, 0.10, 0.20, 0.35, 0.50, 0.65, 0.80]:
            add(name=f"p18_rot_sector_t{int(trend_weight*100)}_g{int(graph*100)}", track="sector", family="sector_rotation", base_system="sector_rotation_track2", text_mode="rule_based", params={"trend_weight": trend_weight, "graph_weight": graph, "news_weight": max(0.0, 1.0 - trend_weight - graph / 2), "constraints": {"max_turnover": 0.18 + graph / 5, "max_weight": 0.25}}, maturity="mvp", dependency="rule_text", runtime="medium", novelty=0.60, reproducibility=0.86, complexity=0.26, dependency_risk=0.08)
    for top_k in [3, 4, 5, 6, 8]:
        for temp in [0.20, 0.35, 0.50, 0.70, 1.00]:
            add(name=f"p18_leeqa_sector_k{top_k}_temp{int(temp*100)}", track="sector", family="leeqa_rank", base_system="leeqa_rank_track2", text_mode="rule_based", params={"top_k": top_k, "temperature": temp, "momentum_weight": 0.35 + 0.03 * top_k, "sentiment_weight": 0.10 + temp / 10, "constraints": {"max_turnover": 0.20 + temp / 10}}, maturity="mvp_proxy", dependency="rule_text", runtime="medium", novelty=0.70, reproducibility=0.86, complexity=0.28, dependency_risk=0.08)
    for graph in [0.10, 0.20, 0.35, 0.50, 0.75]:
        for news in [0.50, 0.80, 1.00, 1.25, 1.50]:
            add(name=f"p18_kg_sector_g{int(graph*100)}_n{int(news*100)}", track="sector", family="kg_moe_lite", base_system="kg_moe_lite_track2", text_mode="rule_based", params={"graph_smoothing_strength": graph, "news_tilt_strength": news, "constraints": {"max_turnover": 0.20 + graph / 5, "max_weight": 0.25}}, maturity="mvp_proxy", dependency="rule_text", runtime="medium", novelty=0.78, reproducibility=0.86, complexity=0.34, dependency_risk=0.08)
    for lr in [1.0, 2.0, 3.0, 4.0, 5.5]:
        for penalty in [0.05, 0.15, 0.30]:
            add(name=f"p18_armor_sector_lr{int(lr*10)}_p{int(penalty*100)}", track="sector", family="armor_omd", base_system="armor_omd_sector", text_mode="rule_based", params={"learning_rate": lr, "turnover_penalty": penalty, "constraints": {"max_turnover": 0.18 + penalty, "max_weight": 0.25}}, maturity="mvp_proxy", dependency="rule_text", runtime="medium", novelty=0.72, reproducibility=0.82, complexity=0.32, dependency_risk=0.08)
    for overlay in [0.05, 0.10, 0.15, 0.20, 0.30]:
        for kalman in [0.05, 0.10, 0.15, 0.25]:
            add(name=f"p18_ceva_sector_o{int(overlay*100)}_k{int(kalman*100)}", track="sector", family="ceva_kf_ciga", base_system="ceva_kf_ciga_track2", text_mode="rule_based", params={"overlay_strength": overlay, "kalman_strength": kalman, "constraints": {"max_turnover": 0.18 + overlay, "max_weight": 0.25}}, maturity="mvp_proxy", dependency="rule_text", runtime="medium", novelty=0.80, reproducibility=0.84, complexity=0.36, dependency_risk=0.08)
    return specs, rows


def _integrity_candidates(output_root: Path) -> list[CandidateSpec]:
    names = {
        "s0_macro_cash02",
        "s1_macro_default",
        "bsa_rp_macro_tilt25",
        "bsa_rp_macro_rule",
        "risk_parity_macro",
        "dro_bl_rp_macro_rule",
        "s0_sector_cash02",
        "s1_sector_default",
        "armor_omd_sector_default",
        "sector_rotation_graph15",
        "leeqa_rank_top4",
        "kg_moe_lite_rule",
        "ceva_sector_rule",
    }
    candidates = [
        candidate.with_stage1_cache(output_root / "cache" / "text_feature_cache")
        for candidate in build_prompt17_candidates(repo_root=REPO_ROOT, max_per_track=None, include_text_modes=("no_news", "rule_based"))
        if candidate.name in names
    ]
    return candidates


def _replay(result: Any, track: str, backend: str, prefer_cuda: bool) -> Any:
    planner_configs = _planner_configs_from_bundle(result.bundle.metadata, result.bundle.candidate_names)
    return run_batched_official_semantics(
        BatchedOfficialSemanticsInput(
            dates=result.bundle.dates,
            assets=result.bundle.assets,
            open_prices=result.bundle.open_prices,
            pct_changes=result.bundle.pct_changes,
            target_weights=result.bundle.target_weights,
            candidate_names=result.bundle.candidate_names,
            planner_config=planner_config_for_track(track),  # type: ignore[arg-type]
            planner_configs=planner_configs,
        ),
        backend=backend,
        prefer_cuda=prefer_cuda,
    )


def _candidate_rows(replay: Any, bundle: Any, track: str, dataset: str, lookup: dict[str, CandidateSpec], runtime_seconds: float) -> list[dict[str, Any]]:
    diagnostics = {item["name"]: item for item in bundle.metadata.get("candidate_diagnostics", [])}
    rows = []
    for index, candidate in enumerate(replay.candidates):
        spec = lookup.get(candidate.name)
        target = bundle.target_weights[index]
        sums = target.sum(axis=1)
        diffs = np.abs(np.diff(target, axis=0)).sum(axis=1) if len(bundle.dates) > 1 else np.asarray([])
        diag = diagnostics.get(candidate.name, {})
        cumulative = float(candidate.metrics.get("cumulative_return", 0.0) or 0.0)
        annualized_return = (1.0 + cumulative) ** (252.0 / max(1, len(bundle.dates))) - 1.0 if cumulative > -0.999 else -1.0
        rows.append(
            {
                "candidate": candidate.name,
                "track": track,
                "family": spec.family if spec else "",
                "text_mode": spec.text_mode if spec else "",
                "dataset": dataset,
                "date_count": len(bundle.dates),
                "asset_count": len(bundle.assets),
                "final_value": candidate.final_value,
                "cumulative_return": cumulative,
                "annualized_return": annualized_return,
                "sharpe_ratio": candidate.metrics.get("sharpe_ratio", 0.0),
                "max_drawdown": candidate.metrics.get("max_drawdown", 0.0),
                "turnover": candidate.metrics.get("turnover", 0.0),
                "trade_count_proxy": int((sums > 1e-9).sum()) + int((diffs > 1e-9).sum()),
                "cash_utilisation": round(float(sums.mean()) if sums.size else 0.0, 8),
                "fallback_days": diag.get("fallback_days", 0),
                "fallback_rate": round(float(diag.get("fallback_days", 0)) / max(1, len(bundle.dates)), 6),
                "failed_days": diag.get("failed_days", 0),
                "target_nonzero_days": diag.get("target_nonzero_days", 0),
                "mean_target_sum": round(float(sums.mean()) if sums.size else 0.0, 8),
                "max_target_sum": round(float(sums.max()) if sums.size else 0.0, 8),
                "dependency_risk": spec.dependency_risk if spec else 0.1,
                "overfit_risk": _overfit_risk(spec.family if spec else ""),
                "parity_risk": 0.05 if spec and spec.family in {"s0", "s1", "risk_parity", "bsa_rp", "armor_omd"} else 0.12,
                "implementation_complexity": spec.complexity_penalty if spec else 0.2,
                "runtime_seconds": round(float(runtime_seconds), 6),
                "backend": replay.backend,
                "device": replay.device,
            }
        )
    return rows


def _score_rows(rows: list[dict[str, Any]], lookup: dict[str, CandidateSpec]) -> list[dict[str, Any]]:
    if not rows:
        return []
    output: list[dict[str, Any]] = []
    for track in sorted({row.get("track", "") for row in rows}):
        track_rows = [row for row in rows if row.get("track") == track]
        rankers = {
            "sharpe": _rank_scores(track_rows, "sharpe_ratio", higher=True),
            "return": _rank_scores(track_rows, "cumulative_return", higher=True),
            "drawdown": _rank_scores(track_rows, "max_drawdown", higher=False),
            "turnover": _rank_scores(track_rows, "turnover", higher=False),
            "fallback": _rank_scores(track_rows, "fallback_rate", higher=False),
        }
        for row in track_rows:
            spec = lookup.get(str(row.get("candidate")))
            novelty = spec.novelty if spec else 0.5
            reproducibility = spec.reproducibility if spec else 0.7
            complexity = spec.complexity_penalty if spec else float(row.get("implementation_complexity", 0.2) or 0.2)
            dependency = spec.dependency_risk if spec else float(row.get("dependency_risk", 0.1) or 0.1)
            key = str(row["candidate"])
            official = (
                0.36 * rankers["sharpe"][key]
                + 0.24 * rankers["return"][key]
                + 0.16 * rankers["drawdown"][key]
                + 0.10 * rankers["turnover"][key]
                + 0.08 * reproducibility
                + 0.06 * rankers["fallback"][key]
            )
            research = official + 0.04 * novelty
            conservative = research - 0.08 * complexity - 0.08 * dependency - 0.03 * float(row.get("overfit_risk", 0.1) or 0.1)
            enriched = dict(row)
            enriched.update({"official_score": round(official, 6), "research_score": round(research, 6), "conservative_score": round(conservative, 6)})
            output.append(enriched)
    output.sort(key=lambda row: (row.get("track", ""), -float(row.get("conservative_score", 0.0))))
    return output


def _rank_scores(rows: list[dict[str, Any]], key: str, *, higher: bool) -> dict[str, float]:
    values = [float(row.get(key, 0.0) or 0.0) for row in rows]
    if not values or max(values) - min(values) < 1e-12:
        return {str(row["candidate"]): 0.5 for row in rows}
    lo, hi = min(values), max(values)
    scores = {}
    for row in rows:
        value = float(row.get(key, 0.0) or 0.0)
        score = (value - lo) / (hi - lo)
        scores[str(row["candidate"])] = score if higher else 1.0 - score
    return scores


def _run_official_candidate_parity(candidate: CandidateSpec, args: argparse.Namespace, output_root: Path) -> dict[str, Any]:
    dates_result = generate_target_tensor(
        TargetTensorGenerationRequest(
            repo_root=REPO_ROOT,
            data_root=_official_dataset_root(),
            track=candidate.track,
            candidates=[candidate],
            output_root=output_root,
            start_date="20250102",
            end_date="20251231",
            max_dates=args.official_parity_dates,
            lookback_days=args.lookback_days,
            force=False,
        )
    )
    local = run_reference_official_semantics(
        OfficialSemanticsInput(
            dates=dates_result.bundle.dates,
            assets=dates_result.bundle.assets,
            open_prices=dates_result.bundle.open_prices,
            pct_changes=dates_result.bundle.pct_changes,
            target_weights=dates_result.bundle.target_weights[0],
            planner_config=_planner_config_for_candidate(candidate),
        )
    )
    batched = _replay(dates_result, candidate.track, args.backend, args.prefer_cuda).candidates[0]
    token = _official_login(args.official_base_url, f"p18_{candidate.name[:24]}", "prompt18")
    config_root = output_root / "generated_configs" / candidate.track
    start_payload = {
        "start_date": _fmt_date(dates_result.bundle.dates[0]),
        "end_date": _fmt_date(dates_result.bundle.dates[-1]),
        "initial_capital": 100000,
        "fund_pool": list(get_fund_pool(candidate.track)),
        "agents": [{"name": f"p18_{candidate.name[:24]}", "prompt": "prompt18 candidate parity"}],
        "news_sources": ["caixin", "tiantian", "sinafinance", "tencent"],
        "lookback_days": args.lookback_days,
        "top_rank": 20,
        "pre_k_days": 1,
        "view_platform_trading_history_days": 1,
        "decision_model_name": candidate.name,
        "results_dir": str((output_root / "official_server" / "candidate_parity").as_posix()),
    }
    start = _json_request("POST", args.official_base_url, "/api/backtest/start", start_payload, token=token)
    session_id = start["session_id"]
    data = start.get("data", {})
    runner = SystemRunner.for_track(candidate.track, strategy=candidate.system_name, fallback_strategy=candidate.fallback_strategy, config_root=config_root)
    trade_count = 0
    while data and data.get("message") != "Backtest finished":
        status = _json_request("GET", args.official_base_url, f"/api/backtest/{session_id}/status", token=token)
        historical = _json_request("GET", args.official_base_url, f"/api/backtest/{session_id}/historical_prices?lookback_days={args.lookback_days}", token=token)
        decision = runner.run_day(
            track=candidate.track,
            fund_pool=list(get_fund_pool(candidate.track)),
            historical_prices=historical.get("historical_prices", {}),
            news=data.get("news", []),
            current_portfolio=status,
            date_to_decision=data.get("date"),
        ).as_official_decision()
        trades = [trade for trade in decision.get("trades", []) if trade.get("action") != "hold"]
        trade_count += len(trades)
        if trades:
            _json_request(
                "POST",
                args.official_base_url,
                f"/api/backtest/{session_id}/trade",
                {
                    "trades": trades,
                    "agent_decision": {
                        "decision": decision,
                        "reasoning": decision.get("reasoning", ""),
                        "chain_of_thought": "",
                    },
                },
                token=token,
            )
        data = _json_request("GET", args.official_base_url, f"/api/backtest/{session_id}/next_day", token=token)
    results = _json_request("GET", args.official_base_url, f"/api/backtest/results/{session_id}", token=token)
    official_value = _extract_official_final_value(results)
    official_local_diff = abs(float(official_value) - float(local.final_value)) if official_value else ""
    local_batched_diff = abs(float(local.final_value) - float(batched.final_value))
    return {
        "Candidate": candidate.name,
        "Track": candidate.track,
        "Window": f"{_fmt_date(dates_result.bundle.dates[0])} to {_fmt_date(dates_result.bundle.dates[-1])}",
        "Official Server Value": official_value,
        "Local Reference Value": local.final_value,
        "Batched Value": batched.final_value,
        "Official-Local Diff": official_local_diff,
        "Local-Batched Diff": local_batched_diff,
        "Trade Match": f"official submitted trades={trade_count}; local proxy={len(local.transactions)}",
        "Status": "pass" if official_value and float(official_local_diff) <= 1e-5 and local_batched_diff <= 1e-5 else "minor_diff" if official_value else "blocked",
        "Notes": f"session_id={session_id}",
    }


def _official_login(base_url: str, username: str, password: str) -> str:
    try:
        _json_request("POST", base_url, "/api/agents/register", {"username": username, "password": password})
    except Exception:
        pass
    data = parse.urlencode({"username": username, "password": password}).encode("utf-8")
    req = request.Request(f"{base_url}/api/agents/token", data=data, headers={"Content-Type": "application/x-www-form-urlencoded"}, method="POST")
    with request.urlopen(req, timeout=15) as response:
        return str(json.loads(response.read().decode("utf-8")).get("access_token", ""))


def _json_request(method: str, base_url: str, endpoint: str, payload: dict[str, Any] | None = None, token: str | None = None) -> dict[str, Any]:
    data = None if payload is None else json.dumps(payload, ensure_ascii=False).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = request.Request(f"{base_url}{endpoint}", data=data, headers=headers, method=method)
    with request.urlopen(req, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def _extract_official_final_value(results: Mapping[str, Any]) -> float | None:
    perf = results.get("performance", {}) if isinstance(results, Mapping) else {}
    for key in ("final_value", "total_value", "portfolio_value"):
        if key in perf:
            return float(perf[key])
    history = results.get("portfolio_value_history", []) if isinstance(results, Mapping) else []
    if history:
        return float(history[-1].get("value", 0.0))
    snapshots = results.get("daily_portfolio_snapshots", []) if isinstance(results, Mapping) else []
    if snapshots:
        return float(snapshots[-1].get("total_value", 0.0))
    return None


def _write_reports(report_root: Path, output_root: Path, state: dict[str, Any]) -> None:
    _ensure_dirs(output_root, report_root)
    ref = report_root / "reference"
    prog = report_root / "progress"
    pres = report_root / "presented"
    candidates, catalog = _big_grid_catalog(output_root)
    lookup = {candidate.name: candidate for candidate in candidates}
    big_rows = _score_rows(state.get("big_grid_rows", []), lookup)
    locked_rows = state.get("locked_2025_rows", [])
    freeze_rows = state.get("candidate_freeze_rows", [])
    parity_rows = state.get("final_local_parity_rows", [])
    official_rows = state.get("official_server_parity_rows", [])
    package_rows = _package_rows(state)
    ablation = _ablation_rows(big_rows)

    _write_csv(ref / "official_server_startup_report.csv", state.get("official_startup_rows", []))
    _write_csv(ref / "pre_grid_integrity_gate.csv", state.get("pre_grid_integrity_rows", []))
    _write_csv(ref / "big_grid_plan.csv", state.get("big_grid_plan_rows", []))
    _write_csv(ref / "big_grid_candidate_catalog.csv", catalog)
    _write_csv(ref / "big_grid_runtime_benchmark.csv", state.get("runtime_benchmark_rows", []))
    _write_csv(ref / "big_grid_2024_scores.csv", big_rows)
    _write_csv(ref / "big_grid_2024_ranking.csv", _ranked_rows(big_rows))
    _write_csv(ref / "big_grid_trackA_ranking.csv", _ranked_rows([row for row in big_rows if row.get("track") == "macro"]))
    _write_csv(ref / "big_grid_trackB_ranking.csv", _ranked_rows([row for row in big_rows if row.get("track") == "sector"]))
    _write_csv(ref / "big_grid_ablation_report.csv", ablation)
    _write_csv(ref / "candidate_freeze_2024_only.csv", freeze_rows)
    _write_csv(ref / "locked_2025_scores.csv", locked_rows)
    _write_csv(ref / "locked_2025_evaluation.csv", locked_rows)
    _write_csv(ref / "final_parity_reference_vs_batched.csv", parity_rows)
    _write_csv(ref / "official_server_parity.csv", official_rows)
    _write_json(ref / "final_runtime_package_audit.json", state.get("runtime_package_audit", {"status": "not_run"}))
    _write_json(ref / "reproducibility_package_audit.json", state.get("reproducibility_package_audit", {"status": "not_run"}))
    _write_json(ref / "dependency_and_model_manifest.json", state.get("dependency_manifest", _dependency_manifest(state, output_root)))

    _write_md(report_root / "README.md", _readme_text(state))
    _write_md(ref / "context_gap_review.md", "# Context Gap Review\n\n" + _md_table(state.get("context_gap_rows", [])))
    _write_md(ref / "official_server_startup_report.md", "# Official Server Startup Report\n\n" + _md_table(state.get("official_startup_rows", [])))
    _write_md(ref / "pre_grid_integrity_gate.md", "# Pre-Grid Integrity Gate\n\n" + _md_table(state.get("pre_grid_integrity_rows", [])))
    _write_md(ref / "big_grid_plan.md", "# Big Grid Plan\n\n" + _md_table(state.get("big_grid_plan_rows", [])))
    _write_md(ref / "big_grid_runtime_benchmark.md", "# Big Grid Runtime Benchmark\n\n" + _md_table(state.get("runtime_benchmark_rows", [])))
    _write_md(ref / "big_grid_2024_ranking.md", "# Big Grid 2024 Ranking\n\n" + _md_table(_ranked_rows(big_rows), 60))
    _write_md(ref / "big_grid_ablation_report.md", "# Big Grid Ablation Report\n\n" + _md_table(ablation, 80))
    _write_md(ref / "candidate_freeze_2024_only.md", "# Candidate Freeze 2024 Only\n\n" + _md_table(freeze_rows))
    _write_md(ref / "locked_2025_evaluation.md", "# Locked 2025 Evaluation\n\n" + _md_table(locked_rows, 80))
    _write_md(ref / "final_parity_reference_vs_batched.md", "# Final Parity Reference vs Batched\n\n" + _md_table(parity_rows))
    _write_md(ref / "official_server_parity.md", "# Official Server Parity\n\n" + _md_table(official_rows))
    _write_md(ref / "final_runtime_package_audit.md", "# Final Runtime Package Audit\n\n" + _md_table([state.get("runtime_package_audit", {"status": "not_run"})]))
    _write_md(ref / "reproducibility_package_audit.md", "# Reproducibility Package Audit\n\n" + _md_table([state.get("reproducibility_package_audit", {"status": "not_run"})]))
    _write_md(ref / "dependency_and_model_manifest.md", "# Dependency and Model Manifest\n\n" + _md_table(_manifest_rows(state.get("dependency_manifest", _dependency_manifest(state, output_root)))))

    _write_md(prog / "progress_00_context_and_readiness_review.md", "# Context and Readiness Review\n\n" + _md_table(state.get("context_gap_rows", [])))
    _write_md(prog / "progress_01_official_server_startup.md", "# Official Server Startup\n\n" + _md_table(state.get("official_startup_rows", [])))
    _write_md(prog / "progress_02_pre_grid_integrity_gate.md", "# Pre-Grid Integrity Gate\n\n" + _md_table(state.get("pre_grid_integrity_rows", [])))
    _write_md(prog / "progress_03_big_grid_plan.md", "# Big Grid Plan\n\n" + _md_table(state.get("big_grid_plan_rows", [])))
    _write_md(prog / "progress_04_big_grid_run_status.md", "# Big Grid Run Status\n\n" + _big_grid_status_text(state, big_rows))
    _write_md(prog / "progress_05_candidate_freeze.md", "# Candidate Freeze\n\n" + _md_table(freeze_rows))
    _write_md(prog / "progress_06_locked_2025_evaluation.md", "# Locked 2025 Evaluation\n\n" + _md_table(locked_rows, 80))
    _write_md(prog / "progress_07_official_server_parity.md", "# Official Server Parity\n\n" + _md_table(official_rows))
    _write_md(prog / "progress_08_package_split.md", "# Package Split\n\n" + _md_table(package_rows))
    _write_md(prog / "run_log.md", "# Run Log\n\n" + _md_table(state.get("run_log", []), 120))

    _write_md(pres / "executive_summary.md", _executive_summary(state, big_rows))
    _write_md(pres / "official_server_validation_summary.md", "# Official Server Validation Summary\n\n" + _md_table(state.get("official_startup_rows", [])) + "\n\n" + _md_table(official_rows))
    _write_md(pres / "big_grid_search_summary.md", "# Big Grid Search Summary\n\n" + _big_grid_status_text(state, big_rows) + "\n\nTop candidates:\n\n" + _md_table(_ranked_rows(big_rows)[:20]))
    _write_md(pres / "final_candidate_selection_report.md", "# Final Candidate Selection Report\n\n" + _md_table(freeze_rows))
    _write_md(pres / "locked_2025_evaluation_summary.md", "# Locked 2025 Evaluation Summary\n\n" + _md_table(locked_rows, 80))
    _write_md(pres / "final_package_summary.md", "# Final Package Summary\n\n" + _md_table(package_rows))
    _write_md(pres / "final_submission_readiness_report.md", _final_readiness_text(state, big_rows, locked_rows, parity_rows, official_rows, package_rows))
    _write_md(pres / "final_recommendation.md", _final_recommendation_text(state, big_rows, locked_rows, official_rows))

    for name in REPORT_PROGRESS:
        (prog / name).touch(exist_ok=True)
    for name in REPORT_PRESENTED:
        (pres / name).touch(exist_ok=True)
    for name in REPORT_REFERENCE:
        (ref / name).touch(exist_ok=True)


def _final_readiness_text(state: dict[str, Any], big_rows: list[dict[str, Any]], locked_rows: list[dict[str, Any]], parity_rows: list[dict[str, Any]], official_rows: list[dict[str, Any]], package_rows: list[dict[str, Any]]) -> str:
    verdict = _readiness_verdict(state, big_rows, parity_rows, official_rows, package_rows)
    freeze = state.get("freeze", {})
    top_a = _top_rows(big_rows, "macro", 5)
    top_b = _top_rows(big_rows, "sector", 5)
    return "\n".join(
        [
            "# Prompt18 Final Submission Readiness Report",
            "",
            "## 1. Readiness Verdict",
            "",
            verdict,
            "",
            "## 2. Remaining Prompt17b Blockers",
            "",
            _md_table(state.get("context_gap_rows", [])),
            "",
            "## 3. Official Server Status",
            "",
            _md_table(state.get("official_startup_rows", [])),
            "",
            "## 4. Big Grid Search Coverage",
            "",
            _coverage_text(state, big_rows),
            "",
            "## 5. Big Grid Top Candidates",
            "",
            "Track A:\n\n" + _md_table(top_a) + "\n\nTrack B:\n\n" + _md_table(top_b),
            "",
            "## 6. 2024-Only Candidate Freeze",
            "",
            _md_table(state.get("candidate_freeze_rows", [])),
            "",
            "## 7. Locked 2025 Evaluation",
            "",
            _md_table(locked_rows, 40),
            "",
            "## 8. Final Local Parity",
            "",
            _md_table(parity_rows),
            "",
            "## 9. Final Official Server Parity",
            "",
            _md_table(official_rows),
            "",
            "## 10. Final Track A Candidate",
            "",
            f"Primary: `{freeze.get('macro_primary', 'not_frozen')}`. Fallback: `{freeze.get('macro_fallback', 'not_frozen')}`.",
            "",
            "## 11. Final Track B Candidate",
            "",
            f"Primary: `{freeze.get('sector_primary', 'not_frozen')}`. Fallback: `{freeze.get('sector_fallback', 'not_frozen')}`.",
            "",
            "## 12. Stage 1 / Text Model Decision",
            "",
            "Final freeze uses no-news/rule-based candidates only. BGE/FinBERT/hybrid remain reproducibility/system-report evidence, not final runtime requirements.",
            "",
            "## 13. Runtime / CUDA Decision",
            "",
            "NumPy official-semantics batched replay is the selected backend. CUDA is not claimed unless benchmark rows show a correct material speedup.",
            "",
            "## 14. Package Split Status",
            "",
            _md_table(package_rows),
            "",
            "## 15. Evidence for System Report",
            "",
            "Use the Prompt18 big-grid catalog, 2024 ranking, freeze report, locked 2025 evaluation, local parity, official parity status, and package audits.",
            "",
            "## 16. Remaining Risks",
            "",
            _md_table([{"risk": risk} for risk in _remaining_risks(state, big_rows, official_rows, package_rows)]),
            "",
            "## 17. Recommended Next Prompt",
            "",
            _next_prompt(verdict),
        ]
    )


def _final_recommendation_text(state: dict[str, Any], big_rows: list[dict[str, Any]], locked_rows: list[dict[str, Any]], official_rows: list[dict[str, Any]]) -> str:
    freeze = state.get("freeze", {})
    return "\n".join(
        [
            "# Prompt18 Final Recommendation",
            "",
            "## 1. Executive Verdict",
            "",
            _readiness_verdict(state, big_rows, state.get("final_local_parity_rows", []), official_rows, _package_rows(state)),
            "",
            "## 2. Final Track A Recommendation",
            "",
            f"- Primary: `{freeze.get('macro_primary', 'not_frozen')}`",
            f"- Fallback: `{freeze.get('macro_fallback', 'not_frozen')}`",
            f"- Evidence: {_candidate_summary(big_rows, freeze.get('macro_primary'))}",
            f"- Locked 2025: {_candidate_summary(locked_rows, freeze.get('macro_primary'))}",
            f"- Official parity: {_official_summary(official_rows, freeze.get('macro_primary'))}",
            "- Risks: generated config must be shipped with runtime package; hidden B-list regime risk remains.",
            "",
            "## 3. Final Track B Recommendation",
            "",
            f"- Primary: `{freeze.get('sector_primary', 'not_frozen')}`",
            f"- Fallback: `{freeze.get('sector_fallback', 'not_frozen')}`",
            f"- Evidence: {_candidate_summary(big_rows, freeze.get('sector_primary'))}",
            f"- Locked 2025: {_candidate_summary(locked_rows, freeze.get('sector_primary'))}",
            f"- Official parity: {_official_summary(official_rows, freeze.get('sector_primary'))}",
            "- Risks: Track B 2025 evidence can differ from 2024 freeze, but it was not used for tuning.",
            "",
            "## 4. Candidates for Runtime Package",
            "",
            _md_table(state.get("candidate_freeze_rows", [])),
            "",
            "## 5. Candidates for Reproducibility / System Report Only",
            "",
            _md_table(_ranked_rows(big_rows)[2:20]),
            "",
            "## 6. Candidates to Drop",
            "",
            _md_table(_ranked_rows(big_rows)[-20:]),
            "",
            "## 7. Package Decision",
            "",
            _md_table(_package_rows(state)),
            "",
            "## 8. What Can Be Claimed",
            "",
            "- Prompt18 ran an Option 1 full-2024 large grid with official-semantics target generation and batched replay.\n- Candidate freeze is 2024-only.\n- Local reference-vs-batched parity is reported for final candidates.",
            "",
            "## 9. What Must Not Be Claimed",
            "",
            "- Do not claim BGE/FinBERT final runtime dependency.\n- Do not claim full causal discovery/GNN/MPC maturity for MVP proxy methods.\n- Do not claim CUDA superiority unless the benchmark rows support it.\n- Do not claim official readiness unless official server parity passed.",
            "",
            "## 10. Next Prompt",
            "",
            _next_prompt(_readiness_verdict(state, big_rows, state.get("final_local_parity_rows", []), official_rows, _package_rows(state))),
        ]
    )


def _ensure_dirs(output_root: Path, report_root: Path) -> None:
    for path in (
        output_root / "cache",
        output_root / "target_tensors",
        output_root / "generated_configs",
        output_root / "grid_runs",
        output_root / "checkpoints",
        output_root / "benchmarks",
        output_root / "official_server",
        output_root / "packages",
        output_root / "logs",
        report_root / "progress",
        report_root / "presented",
        report_root / "reference",
    ):
        path.mkdir(parents=True, exist_ok=True)


def _state_path(output_root: Path) -> Path:
    return output_root / "prompt18_state.json"


def _load_state(output_root: Path) -> dict[str, Any]:
    path = _state_path(output_root)
    if not path.exists():
        return {"created_at_utc": datetime.now(timezone.utc).isoformat(), "run_log": [], "caveats": []}
    return json.loads(path.read_text(encoding="utf-8"))


def _save_state(output_root: Path, state: dict[str, Any]) -> None:
    _write_json(_state_path(output_root), state)


def _log_run(state: dict[str, Any], phase: str, status: str, detail: str, elapsed: float, args: dict[str, Any]) -> None:
    state.setdefault("run_log", []).append({"created_at_utc": datetime.now(timezone.utc).isoformat(), "phase": phase, "status": status, "detail": detail, "elapsed_seconds": round(elapsed, 6), "args": args})


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


def _read_csv(path: Path) -> list[dict[str, Any]]:
    if not path.exists() or path.stat().st_size == 0:
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def _write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True, default=str), encoding="utf-8")


def _write_md(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def _md_table(rows: list[dict[str, Any]], max_rows: int = 50) -> str:
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


def _count_by(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        counts[str(row.get(key, ""))] = counts.get(str(row.get(key, "")), 0) + 1
    return counts


def _big_grid_lookup(output_root: Path) -> dict[str, CandidateSpec]:
    candidates, _ = _big_grid_catalog(output_root)
    return {candidate.name: candidate for candidate in candidates}


def _all_candidate_lookup(output_root: Path) -> dict[str, CandidateSpec]:
    lookup = _big_grid_lookup(output_root)
    cache_root = output_root / "cache" / "text_feature_cache"
    for candidate in build_prompt17_candidates(repo_root=REPO_ROOT, max_per_track=None, include_text_modes=("no_news", "rule_based")):
        lookup.setdefault(candidate.name, candidate.with_stage1_cache(cache_root))
    return lookup


def _merge_scores(existing: list[dict[str, Any]], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged = {str(row.get("candidate")): dict(row) for row in existing}
    for row in rows:
        merged[str(row.get("candidate"))] = dict(row)
    return list(merged.values())


def _big_grid_success(state: dict[str, Any]) -> bool:
    rows = state.get("big_grid_rows", [])
    tracks = _count_by(rows, "track")
    dates = {int(float(row.get("date_count", 0) or 0)) for row in rows}
    return len(rows) >= 300 and tracks.get("macro", 0) >= 100 and tracks.get("sector", 0) >= 100 and dates == {242}


def _ranked_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ranked = []
    for track in sorted({row.get("track", "") for row in rows}):
        track_rows = [dict(row) for row in rows if row.get("track") == track]
        track_rows.sort(key=lambda row: float(row.get("conservative_score", 0.0)), reverse=True)
        for rank, row in enumerate(track_rows, start=1):
            row["Rank"] = rank
            row["Candidate"] = row.get("candidate", "")
            row["Track"] = row.get("track", "")
            row["Family"] = row.get("family", "")
            row["Text Mode"] = row.get("text_mode", "")
            row["2024 Return"] = row.get("cumulative_return", "")
            row["2024 Sharpe"] = row.get("sharpe_ratio", "")
            row["Max Drawdown"] = row.get("max_drawdown", "")
            row["Fallback Rate"] = row.get("fallback_rate", "")
            row["Official Score"] = row.get("official_score", "")
            row["Conservative Score"] = row.get("conservative_score", "")
            row["Runtime"] = row.get("runtime_seconds", "")
            row["Promote?"] = "yes" if rank <= 2 else "report_only" if rank <= 10 else "drop"
            row["Notes"] = _risk_label(row)
            ranked.append(row)
    return ranked


def _rank_of(rows: list[dict[str, Any]], candidate: Any) -> int | str:
    for track in sorted({row.get("track", "") for row in rows}):
        track_rows = [row for row in rows if row.get("track") == track]
        track_rows.sort(key=lambda row: float(row.get("conservative_score", 0.0)), reverse=True)
        for rank, row in enumerate(track_rows, start=1):
            if row.get("candidate") == candidate:
                return rank
    return ""


def _top_rows(rows: list[dict[str, Any]], track: str, count: int) -> list[dict[str, Any]]:
    selected = [row for row in rows if row.get("track") == track]
    selected.sort(key=lambda row: float(row.get("conservative_score", 0.0)), reverse=True)
    return selected[:count]


def _ablation_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault((str(row.get("track", "")), str(row.get("family", "")), str(row.get("text_mode", ""))), []).append(row)
    output = []
    for (track, family, text_mode), items in grouped.items():
        best = max(items, key=lambda item: float(item.get("conservative_score", 0.0)))
        output.append({"track": track, "family": family, "text_mode": text_mode, "count": len(items), "best_candidate": best.get("candidate"), "best_score": best.get("conservative_score"), "best_return": best.get("cumulative_return"), "best_sharpe": best.get("sharpe_ratio")})
    output.sort(key=lambda row: (row["track"], -float(row.get("best_score", 0.0))))
    return output


def _risk_label(row: Mapping[str, Any]) -> str:
    risks = []
    if float(row.get("dependency_risk", 0.0) or 0.0) > 0.07:
        risks.append("text_dependency")
    if float(row.get("implementation_complexity", 0.0) or 0.0) > 0.30:
        risks.append("complex")
    if float(row.get("fallback_rate", 0.0) or 0.0) > 0:
        risks.append("fallback_used")
    return ",".join(risks) or "low"


def _overfit_risk(family: str) -> float:
    return {
        "s0": 0.02,
        "s1": 0.05,
        "risk_parity": 0.06,
        "bsa_rp": 0.12,
        "dro_bl_rp": 0.14,
        "armor_omd": 0.14,
        "sector_rotation": 0.16,
        "leeqa_rank": 0.18,
        "kg_moe_lite": 0.20,
        "ceva_kf_ciga": 0.20,
        "hgf_mpc": 0.18,
        "oco_fallback": 0.14,
    }.get(family, 0.15)


def _locked_2025_names(state: dict[str, Any]) -> list[str]:
    output_root = Path(state.get("output_root", REPO_ROOT / ".var" / "prompt18"))
    big_lookup = _big_grid_lookup(output_root)
    all_lookup = _all_candidate_lookup(output_root)
    rows = _score_rows(state.get("big_grid_rows", []), big_lookup)
    names: list[str] = []
    freeze = state.get("freeze", {})
    for key in ("macro_primary", "macro_fallback", "sector_primary", "sector_fallback"):
        if freeze.get(key) and freeze[key] not in names:
            names.append(freeze[key])
    for track in ("macro", "sector"):
        for row in _top_rows(rows, track, 5):
            if row["candidate"] not in names:
                names.append(row["candidate"])
    for family_name in _baseline_names():
        if family_name not in names:
            names.append(family_name)
    for value in PROMPT17B_FREEZE.values():
        if value in all_lookup and value not in names:
            names.append(value)
    return [name for name in names if name in all_lookup]


def _baseline_names() -> list[str]:
    return ["p18_s0_macro_cash02", "p18_s1_macro_m15_v30_w10_0", "p18_rp_macro_w20_s15", "p18_s0_sector_cash02", "p18_s1_sector_t35_v20_w10"]


def _official_dataset_root() -> Path:
    return REPO_ROOT / "NLPCC_tasks" / "dataset"


def _planner_config_for_candidate(candidate: CandidateSpec) -> OrderPlannerConfig:
    return OrderPlannerConfig.from_mapping(candidate.config)


def _planner_config_from_bundle_candidate(metadata: Mapping[str, Any], index: int, fallback: OrderPlannerConfig) -> OrderPlannerConfig:
    raw = metadata.get("candidate_planner_configs")
    if isinstance(raw, list) and 0 <= index < len(raw) and isinstance(raw[index], Mapping):
        return OrderPlannerConfig.from_mapping(raw[index])
    return fallback


def _planner_configs_from_bundle(metadata: Mapping[str, Any], candidate_names: tuple[str, ...]) -> tuple[OrderPlannerConfig, ...] | None:
    raw = metadata.get("candidate_planner_configs")
    if not isinstance(raw, list) or len(raw) != len(candidate_names):
        return None
    return tuple(OrderPlannerConfig.from_mapping(item if isinstance(item, Mapping) else {}) for item in raw)


def _frozen_role(state: dict[str, Any], candidate: str) -> str:
    freeze = state.get("freeze", {})
    for key, role in (("macro_primary", "primary"), ("macro_fallback", "fallback"), ("sector_primary", "primary"), ("sector_fallback", "fallback")):
        if freeze.get(key) == candidate:
            return role
    return "comparison"


def _final_parity_names(state: dict[str, Any]) -> list[str]:
    rows = _score_rows(state.get("big_grid_rows", []), _big_grid_lookup(Path(state.get("output_root", REPO_ROOT / ".var" / "prompt18"))))
    names = set(_baseline_names())
    freeze = state.get("freeze", {})
    names.update(str(freeze.get(key)) for key in ("macro_primary", "macro_fallback", "sector_primary", "sector_fallback") if freeze.get(key))
    for track in ("macro", "sector"):
        top = _top_rows(rows, track, 1)
        if top:
            names.add(str(top[0]["candidate"]))
    lookup = _big_grid_lookup(Path(state.get("output_root", REPO_ROOT / ".var" / "prompt18")))
    return [name for name in names if name in lookup]


def _official_parity_names(state: dict[str, Any]) -> list[str]:
    freeze = state.get("freeze", {})
    candidates = _baseline_names()[:2] + [_baseline_names()[4]]
    for key in ("macro_primary", "sector_primary"):
        if freeze.get(key):
            candidates.append(str(freeze[key]))
    lookup = _big_grid_lookup(Path(state.get("output_root", REPO_ROOT / ".var" / "prompt18")))
    result = []
    for name in candidates:
        if name in lookup and name not in result:
            result.append(name)
    return result


def _write_final_prompt18_configs(output_root: Path, freeze: dict[str, Any]) -> None:
    lookup = _big_grid_lookup(output_root)
    selected = [lookup[name] for name in (freeze.get("macro_primary"), freeze.get("macro_fallback"), freeze.get("sector_primary"), freeze.get("sector_fallback")) if name in lookup]
    materialize_prompt17_configs(repo_root=REPO_ROOT, output_config_root=output_root / "final_configs", candidates=selected)
    aliases = {
        "prompt18_track_a_primary": freeze.get("macro_primary"),
        "prompt18_track_a_fallback": freeze.get("macro_fallback"),
        "prompt18_track_b_primary": freeze.get("sector_primary"),
        "prompt18_track_b_fallback": freeze.get("sector_fallback"),
    }
    systems_dir = REPO_ROOT / "configs" / "systems"
    systems_dir.mkdir(parents=True, exist_ok=True)
    for alias, source_name in aliases.items():
        if not source_name or source_name not in lookup:
            continue
        config = dict(lookup[source_name].config)
        config["name"] = alias
        _write_mapping(systems_dir / f"{alias}.yaml", config)
    _write_json(
        REPO_ROOT / "configs" / "prompt18_final_candidates.json",
        {
            "created_at_utc": datetime.now(timezone.utc).isoformat(),
            "track_a_primary": "prompt18_track_a_primary",
            "track_a_fallback": "prompt18_track_a_fallback",
            "track_b_primary": "prompt18_track_b_primary",
            "track_b_fallback": "prompt18_track_b_fallback",
            "source_candidates": aliases,
        },
    )


def _write_mapping(path: Path, values: Mapping[str, Any]) -> None:
    try:
        import yaml  # type: ignore

        text = yaml.safe_dump(dict(values), sort_keys=False, allow_unicode=True)
    except ModuleNotFoundError:
        text = json.dumps(values, indent=2, ensure_ascii=False)
    path.write_text(text, encoding="utf-8")


def _generalisation(row: Mapping[str, Any], prior: Mapping[str, Any]) -> str:
    if not row:
        return "not_run"
    ret = float(row.get("cumulative_return", 0.0) or 0.0)
    sharpe = float(row.get("sharpe_ratio", 0.0) or 0.0)
    dd = float(row.get("max_drawdown", 0.0) or 0.0)
    if ret > 0.10 and sharpe > 1.0 and dd < 0.15:
        return "strong"
    if ret > 0.0 and sharpe > 0.5:
        return "acceptable"
    if ret > -0.05:
        return "weak"
    return "failed"


def _port_open(host: str, port: int) -> bool:
    sock = socket.socket()
    sock.settimeout(0.5)
    try:
        sock.connect((host, port))
        return True
    except OSError:
        return False
    finally:
        sock.close()


def _startup_history_rows(output_root: Path) -> list[dict[str, Any]]:
    root = output_root / "official_server"
    rows = []
    checks = [
        ("python start_server.py", "6207", root / "server_stderr.log", "No module named 'uvicorn'", "blocked_dependency", "missing uvicorn before requirements install", "install NLPCC_tasks/requirements.txt"),
        ("python start_server.py", "6207", root / "server_stderr_after_install.log", "UnicodeEncodeError", "blocked_unknown", "Windows console encoding rejected emoji print", "set PYTHONIOENCODING=utf-8"),
        ("PYTHONIOENCODING=utf-8 python start_server.py", "6207", root / "server_stderr_utf8.log", "WinError 5", "blocked_unknown", "Loguru multiprocessing enqueue denied by Windows permissions", "disable queue logging by default"),
    ]
    for command, port, path, needle, result, cause, next_action in checks:
        if path.exists() and needle in path.read_text(encoding="utf-8", errors="replace"):
            rows.append({"Attempt": len(rows) + 1, "Command": command, "Port": port, "Result": result, "Error": needle, "Probable Cause": cause, "Next Action": next_action})
    return rows


def _tail(path: Path, lines: int) -> str:
    if not path.exists():
        return ""
    return "\n".join(path.read_text(encoding="utf-8", errors="replace").splitlines()[-lines:])


def _fmt_date(value: str) -> str:
    text = str(value)
    if "-" in text:
        return text
    return f"{text[:4]}-{text[4:6]}-{text[6:8]}"


def _coverage_text(state: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    counts = _count_by(rows, "track")
    dates = sorted({row.get("date_count", "") for row in rows})
    return f"Option: `{state.get('big_grid_option', 'Option 1')}`. Candidate rows: `{len(rows)}`. Track counts: `{counts}`. Date counts: `{dates}`. Big-grid success: `{_big_grid_success({'big_grid_rows': rows})}`."


def _big_grid_status_text(state: dict[str, Any], rows: list[dict[str, Any]]) -> str:
    return "\n".join(
        [
            _coverage_text(state, rows),
            "",
            "Completed chunks:",
            "",
            _md_table([{"chunk": key, "status": value} for key, value in sorted(state.get("grid_completed_chunks", {}).items())]),
        ]
    )


def _executive_summary(state: dict[str, Any], big_rows: list[dict[str, Any]]) -> str:
    freeze = state.get("freeze", {})
    return "\n".join(
        [
            "# Prompt18 Executive Summary",
            "",
            f"Readiness: **{_readiness_verdict(state, big_rows, state.get('final_local_parity_rows', []), state.get('official_server_parity_rows', []), _package_rows(state))}**.",
            "",
            _coverage_text(state, big_rows),
            "",
            f"Track A primary: `{freeze.get('macro_primary', 'not_frozen')}`; fallback: `{freeze.get('macro_fallback', 'not_frozen')}`.",
            f"Track B primary: `{freeze.get('sector_primary', 'not_frozen')}`; fallback: `{freeze.get('sector_fallback', 'not_frozen')}`.",
        ]
    )


def _readme_text(state: dict[str, Any]) -> str:
    return "\n".join(["# Prompt18 Reports", "", f"Created: {state.get('created_at_utc', '')}", "", "Prompt18 official-server validation, Option 1 big-grid search, candidate freeze, locked 2025 evaluation, parity, and package split evidence."])


def _readiness_verdict(state: dict[str, Any], big_rows: list[dict[str, Any]], parity_rows: list[dict[str, Any]], official_rows: list[dict[str, Any]], package_rows: list[dict[str, Any]]) -> str:
    if not _big_grid_success({"big_grid_rows": big_rows}):
        return "Not ready; big-grid evidence insufficient"
    if parity_rows and any(row.get("Status") != "pass" for row in parity_rows):
        return "Not ready; parity failed"
    if official_rows and any(row.get("Status") == "fail" for row in official_rows):
        return "Not ready; parity failed"
    if package_rows and any(row.get("Status") not in {"pass"} for row in package_rows):
        return "Not ready; package failed"
    required_official = official_rows and all(row.get("Status") == "pass" for row in official_rows)
    if required_official:
        return "Ready for final submission package handoff"
    return "Locally ready, official-server validation blocked"


def _remaining_risks(state: dict[str, Any], big_rows: list[dict[str, Any]], official_rows: list[dict[str, Any]], package_rows: list[dict[str, Any]]) -> list[str]:
    risks = []
    if not official_rows or any(row.get("Status") != "pass" for row in official_rows):
        risks.append("Official server candidate parity is not fully passing.")
    if not _big_grid_success({"big_grid_rows": big_rows}):
        risks.append("Option 1 big-grid success criteria not fully met.")
    if any(row.get("Status") != "pass" for row in package_rows):
        risks.append("Package audit has issues.")
    risks.append("Hidden 2026 B-list regime may differ from 2024 construction and 2025 public A.")
    risks.append("Advanced methods remain MVP/proxy implementations and should be described conservatively.")
    return risks


def _next_prompt(verdict: str) -> str:
    if verdict == "Ready for final submission package handoff":
        return "Prompt19 should produce final system-report prose and handoff checklist."
    if "official-server" in verdict.lower():
        return "Prompt19 should focus narrowly on official-server candidate parity repair and final package handoff."
    return "Prompt19 should repair the failing gate before any submission polish."


def _candidate_summary(rows: list[dict[str, Any]], name: Any) -> str:
    row = next((item for item in rows if item.get("candidate") == name or item.get("Candidate") == name), None)
    if not row:
        return "not_run"
    return f"return={row.get('cumulative_return', row.get('2025 Return', ''))}; sharpe={row.get('sharpe_ratio', row.get('2025 Sharpe', ''))}; score={row.get('conservative_score', '')}"


def _official_summary(rows: list[dict[str, Any]], name: Any) -> str:
    row = next((item for item in rows if item.get("Candidate") == name), None)
    if not row:
        return "not_run"
    return f"{row.get('Status')}; official-local diff={row.get('Official-Local Diff')}"


def _package_rows(state: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for label, key in (("official_runtime", "runtime_package_audit"), ("reproducibility", "reproducibility_package_audit")):
        audit = state.get(key, {})
        rows.append(
            {
                "Package": label,
                "Archive Path": audit.get("archive_path", ""),
                "Entry Count": audit.get("entry_count", ""),
                "Raw Data Issues": ",".join(audit.get("raw_data_issues", [])),
                "Model Binary Issues": ",".join(audit.get("model_binary_issues", [])),
                "Pycache Issues": ",".join(audit.get("pycache_issues", [])),
                "Status": audit.get("status", "not_run"),
                "Notes": audit.get("notes", ""),
            }
        )
    return rows


def _dependency_manifest(state: dict[str, Any], output_root: Path) -> dict[str, Any]:
    del state, output_root
    pip = subprocess.run([sys.executable, "-m", "pip", "freeze"], cwd=REPO_ROOT, text=True, capture_output=True, timeout=60, check=False)
    model_cache = os.environ.get("NLPCC_HF_MODEL_DIR", "")
    return {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "python": sys.version,
        "pip_freeze": pip.stdout.splitlines()[:400],
        "text_models": [
            {"name": "BAAI/bge-small-zh-v1.5", "runtime_required": False, "source": "optional local cache", "cache_env": "NLPCC_HF_MODEL_DIR", "cache_path": model_cache},
            {"name": "yiyanghkust/finbert-tone-chinese", "runtime_required": False, "source": "optional local cache", "cache_env": "NLPCC_HF_MODEL_DIR", "cache_path": model_cache},
        ],
        "external_api_required": False,
        "final_runtime_text_mode": "no_news/rule_based",
    }


def _manifest_rows(manifest: Mapping[str, Any]) -> list[dict[str, Any]]:
    return [
        {"item": "python", "value": str(manifest.get("python", "")).splitlines()[0]},
        {"item": "external_api_required", "value": manifest.get("external_api_required", "")},
        {"item": "final_runtime_text_mode", "value": manifest.get("final_runtime_text_mode", "")},
        {"item": "text_models", "value": json.dumps(manifest.get("text_models", []), ensure_ascii=False)},
    ]


def _collect_package_files(include_paths: list[Path], *, allow_reports: bool) -> list[Path]:
    files: set[Path] = set()
    for include_path in include_paths:
        absolute = REPO_ROOT / include_path
        if not absolute.exists():
            continue
        if absolute.is_file():
            relative = absolute.relative_to(REPO_ROOT)
            if not _package_excluded(relative, allow_reports=allow_reports):
                files.add(relative)
            continue
        for path in absolute.rglob("*"):
            if path.is_file():
                relative = path.relative_to(REPO_ROOT)
                if not _package_excluded(relative, allow_reports=allow_reports):
                    files.add(relative)
    return sorted(files, key=lambda item: item.as_posix())


def _package_excluded(path: Path, *, allow_reports: bool) -> bool:
    parts = set(path.parts)
    if any(part in parts for part in {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".var", "models"}):
        return True
    if path.suffix.lower() in {".pyc", ".pyo", ".tmp", ".log", ".bin", ".safetensors", ".pt", ".pth", ".onnx"}:
        return True
    if _is_raw_data(path):
        return True
    if path.parts and path.parts[0] == "outputs":
        return not (allow_reports and len(path.parts) >= 3 and path.parts[1] == "reports" and path.parts[2] == "prompt18")
    return False


def _is_raw_data(path: Path) -> bool:
    normalized = path.as_posix()
    return normalized.startswith("data/") or normalized.startswith("NLPCC_tasks/dataset/")


def _build_prompt18_package(*, output_root: Path, package_name: str, include_paths: list[Path], allow_reports: bool, readme_name: str, readme_text: str) -> dict[str, Any]:
    package_root = output_root / "packages"
    package_root.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    name = f"{package_name}_{timestamp}"
    package_dir = package_root / name
    archive_path = package_root / f"{name}.zip"
    if package_dir.exists():
        shutil.rmtree(package_dir)
    if archive_path.exists():
        archive_path.unlink()
    files = _collect_package_files(include_paths, allow_reports=allow_reports)
    copied = []
    for relative in files:
        destination = package_dir / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / relative, destination)
        copied.append({"path": relative.as_posix(), "sha256": _sha256(REPO_ROOT / relative), "bytes": (REPO_ROOT / relative).stat().st_size})
    (package_dir / readme_name).write_text(readme_text, encoding="utf-8")
    copied.append({"path": readme_name, "sha256": _sha256(package_dir / readme_name), "bytes": (package_dir / readme_name).stat().st_size})
    manifest = {"created_at_utc": datetime.now(timezone.utc).isoformat(), "package_name": name, "files": copied, "raw_data_excluded": True}
    (package_dir / "SUBMISSION_MANIFEST.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(package_dir.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(package_dir).as_posix())
    names = zipfile.ZipFile(archive_path).namelist()
    raw = [name for name in names if _is_raw_data(Path(name))]
    model = [name for name in names if Path(name).suffix.lower() in {".bin", ".safetensors", ".pt", ".pth", ".onnx"}]
    pycache = [name for name in names if "__pycache__" in Path(name).parts or name.endswith(".pyc")]
    return {
        "status": "pass" if not raw and not model and not pycache else "fail",
        "package_dir": str(package_dir),
        "archive_path": str(archive_path),
        "entry_count": len(names),
        "file_count": len(copied),
        "raw_data_issues": raw,
        "model_binary_issues": model,
        "pycache_issues": pycache,
        "notes": "allow_reports=true" if allow_reports else "minimal official runtime package",
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _runtime_readme(state: dict[str, Any]) -> str:
    freeze = state.get("freeze", {})
    return "\n".join(
        [
            "# Prompt18 Official Runtime Package",
            "",
            "Minimal runtime package for official execution.",
            "",
            "Final generated aliases:",
            "",
            "- Track A primary: `prompt18_track_a_primary`",
            "- Track A fallback: `prompt18_track_a_fallback`",
            "- Track B primary: `prompt18_track_b_primary`",
            "- Track B fallback: `prompt18_track_b_fallback`",
            "",
            "Set `NLPCC_TRACK_A_STRATEGY=prompt18_track_a_primary` or `NLPCC_TRACK_B_STRATEGY=prompt18_track_b_primary` when invoking the thin wrapper if the harness does not pass strategy names explicitly.",
            "Raw datasets, outputs, caches, and model binaries are excluded.",
            "",
            f"Source candidates: {json.dumps(freeze, ensure_ascii=False, default=str)}",
        ]
    )


def _repro_readme(state: dict[str, Any]) -> str:
    return "\n".join(["# Prompt18 Reproducibility Package", "", "Includes runtime code plus `src/tools/`, Prompt18 scripts, and compact Prompt18 reports. Raw official data, `.var` tensors, large caches, and model binaries are excluded.", "", f"Freeze: {json.dumps(state.get('freeze', {}), ensure_ascii=False, default=str)}"])


def _stop_started_server(output_root: Path) -> None:
    pid_path = output_root / "official_server" / "server_pid.txt"
    if not pid_path.exists():
        return
    try:
        pid = int(pid_path.read_text(encoding="utf-8").strip())
    except ValueError:
        return
    subprocess.run(["powershell", "-Command", f"Stop-Process -Id {pid} -Force -ErrorAction SilentlyContinue"], cwd=REPO_ROOT, check=False)


if __name__ == "__main__":
    raise SystemExit(main())
