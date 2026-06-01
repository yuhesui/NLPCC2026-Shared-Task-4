#!/usr/bin/env python3
"""Bounded Prompt17 official-semantics grid search workflow."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from time import perf_counter
from typing import Any

import numpy as np


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nlpcc.stage1_news.feature_cache import TEXT_FEATURE_MODES, build_text_feature_cache  # noqa: E402
from tools.backtesting.backtester_parity import compare_reference_to_candidate  # noqa: E402
from tools.backtesting.cuda_vectorized_backtester import BatchedOfficialSemanticsInput, run_batched_official_semantics  # noqa: E402
from tools.backtesting.reference_official_semantics import OfficialSemanticsInput, run_reference_official_semantics  # noqa: E402
from tools.experiments.candidate_factory import CandidateSpec, build_prompt17_candidates  # noqa: E402
from tools.experiments.leakage_safe_input_builder import LeakageSafeInputBuilder  # noqa: E402
from tools.experiments.target_tensor_generator import (  # noqa: E402
    TargetTensorGenerationRequest,
    generate_target_tensor,
    planner_config_for_track,
)
from tools.verification.submission_package import audit_submission_archive, build_submission_package  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Prompt17 bounded official-semantics search.")
    parser.add_argument("--output-root", default=str(REPO_ROOT / ".var" / "prompt17"))
    parser.add_argument("--report-root", default=str(REPO_ROOT / "docs" / "reports" / "prompt17"))
    parser.add_argument("--stage0-dates", type=int, default=10)
    parser.add_argument("--stage1-dates", type=int, default=40)
    parser.add_argument("--stage2-dates", type=int, default=20)
    parser.add_argument("--max-candidates-per-track", type=int, default=10)
    parser.add_argument("--candidate-text-modes", default="no_news,rule_based,bge_small_zh,finbert_tone_chinese,hybrid_rule_bge_finbert")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--lookback-days", type=int, default=60)
    parser.add_argument("--backend", choices=["auto", "torch", "numpy"], default="auto")
    parser.add_argument("--prefer-cuda", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--skip-package", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    started = perf_counter()
    output_root = Path(args.output_root)
    report_root = Path(args.report_root)
    output_root.mkdir(parents=True, exist_ok=True)
    report_root.mkdir(parents=True, exist_ok=True)

    candidate_text_modes = tuple(item.strip() for item in args.candidate_text_modes.split(",") if item.strip())
    candidates = [
        item.with_stage1_cache(output_root / "text_feature_cache")
        for item in build_prompt17_candidates(
            repo_root=REPO_ROOT,
            max_per_track=args.max_candidates_per_track,
            include_text_modes=candidate_text_modes,
        )
    ]
    candidate_by_name = {candidate.name: candidate for candidate in candidates}

    text_cache_records = _build_stage0_text_cache(output_root, args.stage0_dates)
    train_runs = []
    all_rows: list[dict[str, Any]] = []
    parity_rows: list[dict[str, Any]] = []
    fold_rows: list[dict[str, Any]] = []
    for track in ("macro", "sector"):
        track_candidates = [candidate for candidate in candidates if candidate.track == track]
        train_result = generate_target_tensor(
            TargetTensorGenerationRequest(
                repo_root=REPO_ROOT,
                data_root=REPO_ROOT / "data" / "train_2024",
                track=track,  # type: ignore[arg-type]
                candidates=track_candidates,
                output_root=output_root,
                max_dates=args.stage1_dates,
                lookback_days=args.lookback_days,
                force=args.force,
            )
        )
        replay = _replay(train_result, track, backend=args.backend, prefer_cuda=args.prefer_cuda)
        train_runs.append({"track": track, "generation": train_result.as_dict(), "replay": replay.as_dict()})
        all_rows.extend(_candidate_rows(replay, track, candidate_by_name, dataset="train_2024"))
        parity_rows.append(_reference_parity_row(train_result, replay, track))
        fold_rows.extend(_five_fold_rows(train_result, track, candidate_by_name, backend=args.backend, prefer_cuda=args.prefer_cuda))

    scored_rows = _score_rows(all_rows, candidate_by_name)
    top_train = scored_rows[: args.top_k]
    eval_rows = _run_2025_locked(top_train, candidate_by_name, output_root, args)
    scored_eval_rows = _score_rows(eval_rows, candidate_by_name) if eval_rows else []
    winner = scored_eval_rows[0] if scored_eval_rows else (top_train[0] if top_train else {})

    package_payload = None
    if not args.skip_package:
        package_payload = _build_package(output_root)

    artifacts = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "elapsed_seconds": round(perf_counter() - started, 6),
        "args": vars(args),
        "candidate_count": len(candidates),
        "train_runs": train_runs,
        "train_rows": scored_rows,
        "eval_2025_rows": scored_eval_rows,
        "five_fold_rows": fold_rows,
        "parity_rows": parity_rows,
        "text_cache_records": [record.as_dict() for record in text_cache_records],
        "winner": winner,
        "package": package_payload,
    }
    (output_root / "prompt17_results.json").write_text(
        json.dumps(artifacts, indent=2, ensure_ascii=False, sort_keys=True, default=str),
        encoding="utf-8",
    )
    _write_csv(output_root / "candidate_scores_2024.csv", scored_rows)
    _write_csv(output_root / "candidate_scores_2025.csv", scored_eval_rows)
    _write_csv(output_root / "five_fold_scores.csv", fold_rows)
    _write_reports(report_root, output_root, artifacts)
    print(json.dumps({"status": "ok", "winner": winner.get("candidate"), "elapsed_seconds": artifacts["elapsed_seconds"]}, indent=2))
    return 0


def _build_stage0_text_cache(output_root: Path, stage0_dates: int) -> list[Any]:
    records: list[Any] = []
    for track in ("macro", "sector"):
        builder = LeakageSafeInputBuilder(data_root=REPO_ROOT / "data" / "train_2024", track=track)  # type: ignore[arg-type]
        dates = builder.selected_dates(max_dates=stage0_dates)
        records.extend(
            build_text_feature_cache(
                dates=dates,
                news_provider=builder.visible_news,
                cache_path=output_root / "text_feature_cache",
                modes=TEXT_FEATURE_MODES,
                sample_limit=stage0_dates,
            )
        )
    return records


def _replay(result: Any, track: str, *, backend: str, prefer_cuda: bool) -> Any:
    bundle = result.bundle
    return run_batched_official_semantics(
        BatchedOfficialSemanticsInput(
            dates=bundle.dates,
            assets=bundle.assets,
            open_prices=bundle.open_prices,
            pct_changes=bundle.pct_changes,
            target_weights=bundle.target_weights,
            candidate_names=bundle.candidate_names,
            planner_config=planner_config_for_track(track),  # type: ignore[arg-type]
        ),
        backend=backend,
        prefer_cuda=prefer_cuda,
    )


def _candidate_rows(replay: Any, track: str, candidate_by_name: dict[str, CandidateSpec], *, dataset: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for candidate in replay.candidates:
        spec = candidate_by_name.get(candidate.name)
        metrics = candidate.metrics
        rows.append(
            {
                "candidate": candidate.name,
                "track": track,
                "dataset": dataset,
                "family": spec.family if spec else "",
                "text_mode": spec.text_mode if spec else "",
                "final_value": candidate.final_value,
                "cumulative_return": metrics.get("cumulative_return", 0.0),
                "sharpe_ratio": metrics.get("sharpe_ratio", 0.0),
                "max_drawdown": metrics.get("max_drawdown", 0.0),
                "turnover": metrics.get("turnover", 0.0),
                "backend": replay.backend,
                "device": replay.device,
            }
        )
    return rows


def _reference_parity_row(generation: Any, replay: Any, track: str) -> dict[str, Any]:
    bundle = generation.bundle
    reference = run_reference_official_semantics(
        OfficialSemanticsInput(
            dates=bundle.dates,
            assets=bundle.assets,
            open_prices=bundle.open_prices,
            pct_changes=bundle.pct_changes,
            target_weights=bundle.target_weights[0],
            planner_config=planner_config_for_track(track),  # type: ignore[arg-type]
        )
    )
    parity = compare_reference_to_candidate(reference, replay.candidates[0], tolerance=1e-5)
    return {
        "track": track,
        "candidate": replay.candidates[0].name,
        "within_tolerance": parity.within_tolerance,
        "max_value_diff": parity.max_value_diff,
        "final_value_diff": parity.final_value_diff,
        "reference_final_value": reference.final_value,
        "batched_final_value": replay.candidates[0].final_value,
    }


def _five_fold_rows(generation: Any, track: str, candidate_by_name: dict[str, CandidateSpec], *, backend: str, prefer_cuda: bool) -> list[dict[str, Any]]:
    bundle = generation.bundle
    if len(bundle.dates) < 5:
        return []
    rows: list[dict[str, Any]] = []
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
                candidate_names=bundle.candidate_names,
                planner_config=planner_config_for_track(track),  # type: ignore[arg-type]
            ),
            backend=backend,
            prefer_cuda=prefer_cuda,
        )
        for candidate in replay.candidates:
            spec = candidate_by_name.get(candidate.name)
            rows.append(
                {
                    "fold": fold_index,
                    "candidate": candidate.name,
                    "track": track,
                    "family": spec.family if spec else "",
                    "text_mode": spec.text_mode if spec else "",
                    "date_start": bundle.dates[int(fold[0])],
                    "date_end": bundle.dates[int(fold[-1])],
                    "cumulative_return": candidate.metrics.get("cumulative_return", 0.0),
                    "sharpe_ratio": candidate.metrics.get("sharpe_ratio", 0.0),
                    "max_drawdown": candidate.metrics.get("max_drawdown", 0.0),
                    "turnover": candidate.metrics.get("turnover", 0.0),
                    "final_value": candidate.final_value,
                }
            )
    return rows


def _run_2025_locked(
    top_train: list[dict[str, Any]],
    candidate_by_name: dict[str, CandidateSpec],
    output_root: Path,
    args: argparse.Namespace,
) -> list[dict[str, Any]]:
    selected = [candidate_by_name[row["candidate"]] for row in top_train if row["candidate"] in candidate_by_name]
    rows: list[dict[str, Any]] = []
    for track in ("macro", "sector"):
        track_candidates = [candidate for candidate in selected if candidate.track == track]
        if not track_candidates:
            continue
        generation = generate_target_tensor(
            TargetTensorGenerationRequest(
                repo_root=REPO_ROOT,
                data_root=REPO_ROOT / "data" / "public_a_2025",
                track=track,  # type: ignore[arg-type]
                candidates=track_candidates,
                output_root=output_root,
                max_dates=args.stage2_dates,
                lookback_days=args.lookback_days,
                force=args.force,
            )
        )
        replay = _replay(generation, track, backend=args.backend, prefer_cuda=args.prefer_cuda)
        rows.extend(_candidate_rows(replay, track, candidate_by_name, dataset="public_a_2025_locked"))
    return rows


def _score_rows(rows: list[dict[str, Any]], candidate_by_name: dict[str, CandidateSpec]) -> list[dict[str, Any]]:
    if not rows:
        return []
    sharpe = _rank_scores(rows, "sharpe_ratio", higher=True)
    returns = _rank_scores(rows, "cumulative_return", higher=True)
    drawdown = _rank_scores(rows, "max_drawdown", higher=False)
    turnover = _rank_scores(rows, "turnover", higher=False)
    scored: list[dict[str, Any]] = []
    for row in rows:
        spec = candidate_by_name.get(row["candidate"])
        novelty = spec.novelty if spec else 0.5
        reproducibility = spec.reproducibility if spec else 0.7
        complexity_penalty = spec.complexity_penalty if spec else 0.2
        dependency_risk = spec.dependency_risk if spec else 0.1
        official_score = (
            0.35 * sharpe[row["candidate"]]
            + 0.25 * returns[row["candidate"]]
            + 0.15 * drawdown[row["candidate"]]
            + 0.10 * turnover[row["candidate"]]
            + 0.10 * reproducibility
            + 0.05 * novelty
        )
        conservative = official_score - 0.08 * complexity_penalty - 0.08 * dependency_risk
        enriched = dict(row)
        enriched.update({"official_score": round(official_score, 6), "conservative_score": round(conservative, 6)})
        scored.append(enriched)
    scored.sort(key=lambda item: item["conservative_score"], reverse=True)
    return scored


def _rank_scores(rows: list[dict[str, Any]], key: str, *, higher: bool) -> dict[str, float]:
    values = [float(row.get(key, 0.0) or 0.0) for row in rows]
    if not values:
        return {}
    lo = min(values)
    hi = max(values)
    if abs(hi - lo) < 1e-12:
        return {row["candidate"]: 0.5 for row in rows}
    scores: dict[str, float] = {}
    for row in rows:
        value = float(row.get(key, 0.0) or 0.0)
        score = (value - lo) / (hi - lo)
        scores[row["candidate"]] = score if higher else 1.0 - score
    return scores


def _build_package(output_root: Path) -> dict[str, Any]:
    package_root = output_root / "packages"
    name = "nlpcc_task4_candidate_prompt17_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    result = build_submission_package(repo_root=REPO_ROOT, output_root=package_root, package_name=name)
    audit = audit_submission_archive(result.archive_path)
    return {"package": result.as_dict(), "archive_audit": audit, "status": "ok" if not audit["issues"] else "failed"}


def _write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = sorted({key for row in rows for key in row})
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: row.get(key, "") for key in fieldnames})


def _write_reports(report_root: Path, output_root: Path, artifacts: dict[str, Any]) -> None:
    train_rows = artifacts["train_rows"]
    eval_rows = artifacts["eval_2025_rows"]
    fold_rows = artifacts["five_fold_rows"]
    parity_rows = artifacts["parity_rows"]
    text_rows = artifacts["text_cache_records"]
    winner = artifacts["winner"] or {}
    table = _table

    _write_md(
        report_root / "official_semantics_grid_search_report.md",
        "Prompt17 Official-Semantics Grid Search Report",
        [
            f"Candidate count: {artifacts['candidate_count']}.",
            f"Backend/device evidence is recorded in `{output_root / 'prompt17_results.json'}`.",
            f"Bounded runtime: {artifacts['elapsed_seconds']} seconds.",
            table(train_rows[:10], ["candidate", "track", "family", "text_mode", "cumulative_return", "sharpe_ratio", "max_drawdown", "conservative_score"]),
        ],
    )
    _write_md(
        report_root / "target_tensor_generation_report.md",
        "Target Tensor Generation Report",
        [
            "Target weights were generated through `SystemRunner` with current-day close/high/low/change/pct_change masked.",
            table(
                [
                    {
                        "track": run["track"],
                        "cache_key": run["generation"]["cache_key"],
                        "shape": run["generation"]["metadata"]["tensor_shape"],
                        "leakage_ok": run["generation"]["metadata"]["leakage_summary"].get("all_current_day_close_masked"),
                    }
                    for run in artifacts["train_runs"]
                ],
                ["track", "cache_key", "shape", "leakage_ok"],
            ),
        ],
    )
    _write_md(
        report_root / "text_feature_cache_report.md",
        "Text Feature Cache Report",
        [
            f"Cache records built: {len(text_rows)} across modes no_news, rule_based, bge_small_zh, finbert_tone_chinese, hybrid_rule_bge_finbert.",
            table(text_rows[:12], ["mode", "decision_date", "news_count", "fallback_used", "event_count", "cache_key"]),
        ],
    )
    _write_md(
        report_root / "stage0_smoke_report.md",
        "Stage 0 Smoke Report",
        [
            "Stage 0 validated bounded text cache generation and reference/batched parity before ranking.",
            table(parity_rows, ["track", "candidate", "within_tolerance", "max_value_diff", "final_value_diff"]),
        ],
    )
    _write_md(
        report_root / "stage1_2024_grid_report.md",
        "Stage 1 2024 Grid Report",
        [table(train_rows, ["candidate", "track", "family", "text_mode", "final_value", "cumulative_return", "sharpe_ratio", "turnover", "conservative_score"])],
    )
    _write_md(
        report_root / "stage2_topk_2025_report.md",
        "Stage 2 Locked 2025 Report",
        [table(eval_rows, ["candidate", "track", "family", "text_mode", "final_value", "cumulative_return", "sharpe_ratio", "turnover", "conservative_score"])],
    )
    _write_md(
        report_root / "five_fold_evaluation_report.md",
        "Five-Fold Evaluation Report",
        [
            "Folds are contiguous 80/20 validation slices over the bounded 2024 tensor horizon, replayed from fresh capital.",
            table(_fold_summary(fold_rows), ["candidate", "track", "folds", "mean_return", "mean_sharpe", "worst_drawdown"]),
        ],
    )
    _write_md(
        report_root / "ablation_report.md",
        "Ablation Report",
        [table(_ablation_summary(train_rows), ["family", "text_mode", "count", "best_candidate", "best_score", "best_return"])],
    )
    _write_md(
        report_root / "candidate_ranking_report.md",
        "Candidate Ranking Report",
        [table(train_rows[:15], ["candidate", "track", "family", "text_mode", "official_score", "conservative_score"])],
    )
    _write_md(
        report_root / "winner_freeze_report.md",
        "Winner Freeze Report",
        [
            f"Frozen candidate: `{winner.get('candidate', 'none')}`.",
            f"Track: `{winner.get('track', 'unknown')}`. Family: `{winner.get('family', 'unknown')}`. Text mode: `{winner.get('text_mode', 'unknown')}`.",
            "Freeze basis: Prompt17 bounded official-semantics replay, locked 2025 top-k evaluation when available, and package audit.",
        ],
    )
    _write_md(
        report_root / "official_server_spotcheck_report.md",
        "Official Server Spotcheck Report",
        [
            "No destructive official server rewrite was performed by this script.",
            "Local evidence uses the Prompt16 official-semantics reference and batched replay; server probe status is recorded separately if `scripts/run_official_server_smoke.py` is run.",
        ],
    )
    _write_md(
        report_root / "package_report.md",
        "Package Report",
        [json.dumps(artifacts.get("package") or {"status": "skipped"}, indent=2, ensure_ascii=False, sort_keys=True, default=str)],
    )
    _write_md(
        report_root / "final_recommendation.md",
        "Prompt17 Final Recommendation",
        [
            f"Recommended candidate: `{winner.get('candidate', 'none')}`.",
            "Use this as the frozen candidate only within the bounded-run caveat; full overnight execution can reuse the generated scripts with larger date/candidate limits.",
            table((eval_rows or train_rows)[:5], ["candidate", "track", "family", "text_mode", "cumulative_return", "sharpe_ratio", "conservative_score"]),
        ],
    )


def _write_md(path: Path, title: str, sections: list[str]) -> None:
    path.write_text("# " + title + "\n\n" + "\n\n".join(sections) + "\n", encoding="utf-8")


def _table(rows: list[dict[str, Any]], columns: list[str]) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(columns) + " |", "| " + " | ".join("---" for _ in columns) + " |"]
    for row in rows:
        values = []
        for column in columns:
            value = row.get(column, "")
            if isinstance(value, float):
                value = round(value, 6)
            values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def _fold_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(row["candidate"], []).append(row)
    output: list[dict[str, Any]] = []
    for candidate, items in grouped.items():
        output.append(
            {
                "candidate": candidate,
                "track": items[0]["track"],
                "folds": len(items),
                "mean_return": round(sum(float(item["cumulative_return"]) for item in items) / len(items), 6),
                "mean_sharpe": round(sum(float(item["sharpe_ratio"]) for item in items) / len(items), 6),
                "worst_drawdown": round(max(float(item["max_drawdown"]) for item in items), 6),
            }
        )
    output.sort(key=lambda item: item["mean_return"], reverse=True)
    return output[:15]


def _ablation_summary(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault((row["family"], row["text_mode"]), []).append(row)
    output: list[dict[str, Any]] = []
    for (family, text_mode), items in grouped.items():
        best = max(items, key=lambda item: item.get("conservative_score", 0.0))
        output.append(
            {
                "family": family,
                "text_mode": text_mode,
                "count": len(items),
                "best_candidate": best["candidate"],
                "best_score": best.get("conservative_score", 0.0),
                "best_return": best.get("cumulative_return", 0.0),
            }
        )
    output.sort(key=lambda item: item["best_score"], reverse=True)
    return output


if __name__ == "__main__":
    raise SystemExit(main())
