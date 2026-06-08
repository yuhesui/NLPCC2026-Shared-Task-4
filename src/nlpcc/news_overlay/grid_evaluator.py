"""Bounded grid evaluation runner for Prompt07 News Overlay evidence.

The runner intentionally stays outside the frozen official runtime. It uses the
News Overlay N/I/S pipeline to produce daily target weights, then replays those
targets through the local official-semantics reference backtester.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from dataclasses import dataclass
from pathlib import Path
from time import perf_counter
from typing import Any

import numpy as np

from nlpcc.news_overlay.config import NewsOverlayConfig, normalize_track
from nlpcc.news_overlay.hf_models import resolve_local_model_context
from nlpcc.news_overlay.pipeline import ScaffoldNewsOverlayPipeline
from nlpcc.news_overlay.registry import validate_track_compatibility
from nlpcc.news_overlay.traces import JsonTraceWriter
from tools.backtesting.reference_official_semantics import (
    OfficialSemanticsInput,
    load_official_semantics_arrays,
    run_reference_official_semantics,
)


TRACK_TO_OFFICIAL = {"A": "macro", "B": "sector"}
REPORT_FIELDNAMES = (
    "run_id",
    "section",
    "track",
    "n_method",
    "i_method",
    "s_method",
    "base_config",
    "period",
    "data_root",
    "date_count",
    "proxy_mode",
    "evaluation_status",
    "grid_status",
    "asset_status_counts",
    "blocked_methods",
    "network_attempted",
    "runtime_seconds",
    "cache_hit_rate",
    "embedding_coverage",
    "aspect_coverage",
    "event_label_confidence",
    "attention_entropy",
    "reranker_coverage",
    "transformer_active_days",
    "changed_date_fraction_vs_lexical",
    "shuffled_news_delta_sharpe",
    "sharpe",
    "cumret",
    "maxdd",
    "turnover",
    "zero_news_pass",
    "shuffled_news_pass",
    "lexical_baseline_beat",
    "decision",
    "notes",
)


@dataclass(frozen=True)
class GridEvaluationConfig:
    grid_path: Path
    data_root: Path
    output_dir: Path
    cache_dir: Path
    trace_dir: Path
    period: str
    max_dates: int = 20
    offline: bool = True
    device: str = "cpu"
    batch_size: int = 8
    proxy_mode: bool = False
    top_rank: int = 20
    cutoff: str = "15:00"
    run_ids: tuple[str, ...] = ()
    include_shuffled: bool = False
    shuffle_news: bool = False
    approved_models_path: Path | None = None
    local_models_path: Path | None = None
    cache_root: Path | None = None
    resume: bool = True


def run_grid_evaluation(config: GridEvaluationConfig) -> dict[str, Any]:
    """Run a bounded dated grid and write Prompt07-compatible CSV artifacts."""

    started = perf_counter()
    config.output_dir.mkdir(parents=True, exist_ok=True)
    config.trace_dir.mkdir(parents=True, exist_ok=True)
    config.cache_dir.mkdir(parents=True, exist_ok=True)
    rows = _read_grid(config.grid_path)
    if config.run_ids:
        allowed = set(config.run_ids)
        rows = [row for row in rows if str(row.get("run_id")) in allowed]
    if not rows:
        raise ValueError(f"No grid rows selected from {config.grid_path}")

    selected_dates = _dates_for_rows(rows, config.data_root, config.max_dates)
    news_by_track = {
        track: _load_news_by_date(config.data_root, tuple(dates), top_rank=config.top_rank)
        for track, dates in selected_dates.items()
    }

    result_rows: list[dict[str, Any]] = []
    trace_summary_rows: list[dict[str, Any]] = []
    cache_manifest_rows: list[dict[str, Any]] = []
    target_weights_by_run: dict[str, np.ndarray] = {}
    row_context: dict[str, dict[str, Any]] = {}
    local_model_paths, local_model_metadata, _model_rows = resolve_local_model_context(
        approved_models_path=config.approved_models_path,
        local_models_path=config.local_models_path,
        cache_root=config.cache_root,
        require_local=bool(config.approved_models_path),
    )

    checkpoint_dir = config.output_dir / "checkpoints"
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    for row in rows:
        run_id = str(row.get("run_id") or f"{row.get('n_method')}_{row.get('i_method')}_{row.get('s_method')}")
        run_result = _load_checkpoint(checkpoint_dir, config.period, run_id, config) if config.resume else None
        if run_result is None:
            run_result = _evaluate_one_run(row, config, selected_dates, news_by_track, local_model_paths, local_model_metadata)
            _write_checkpoint(checkpoint_dir, config.period, run_id, run_result, config)
        result_rows.append(run_result["summary"])
        trace_summary_rows.extend(run_result["trace_rows"])
        cache_manifest_rows.extend(run_result["cache_rows"])
        target_weights_by_run[run_result["summary"]["run_id"]] = run_result["target_weights"]
        row_context[run_result["summary"]["run_id"]] = row

    _attach_comparisons(result_rows, target_weights_by_run, row_context)
    if config.include_shuffled:
        _attach_shuffled_results(result_rows, rows, config, selected_dates, news_by_track)

    results_path = config.output_dir / f"prompt07_{config.period}_grid_results.csv"
    traces_path = config.output_dir / f"prompt07_{config.period}_trace_metrics.csv"
    cache_path = config.output_dir / f"prompt07_{config.period}_cache_manifest.csv"
    _write_csv(results_path, result_rows, REPORT_FIELDNAMES)
    _write_csv(traces_path, trace_summary_rows, _ordered_keys(trace_summary_rows))
    _write_csv(cache_path, cache_manifest_rows, _ordered_keys(cache_manifest_rows))
    summary = {
        "period": config.period,
        "grid_path": str(config.grid_path),
        "data_root": str(config.data_root),
        "run_count": len(result_rows),
        "max_dates": config.max_dates,
        "proxy_mode": config.proxy_mode,
        "include_shuffled": config.include_shuffled,
        "results_path": str(results_path),
        "trace_metrics_path": str(traces_path),
        "cache_manifest_path": str(cache_path),
        "status_counts": _counts(row["evaluation_status"] for row in result_rows),
        "elapsed_seconds": round(perf_counter() - started, 6),
    }
    (config.output_dir / f"prompt07_{config.period}_grid_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True),
        encoding="utf-8",
    )
    return summary


def _evaluate_one_run(
    row: dict[str, str],
    config: GridEvaluationConfig,
    selected_dates: dict[str, tuple[str, ...]],
    news_by_track: dict[str, dict[str, list[dict[str, str]]]],
    local_model_paths: dict[str, str] | None = None,
    local_model_metadata: dict[str, dict[str, str]] | None = None,
) -> dict[str, Any]:
    run_id = str(row.get("run_id") or f"{row.get('n_method')}_{row.get('i_method')}_{row.get('s_method')}")
    track = normalize_track(str(row.get("track")))
    n_method = _row_method(row, "n_method", "N")
    i_method = _row_method(row, "i_method", "I")
    s_method = _row_method(row, "s_method", "S")
    validate_track_compatibility(track, (n_method, i_method, s_method))

    loaded_dates, assets, open_prices, pct_changes = load_official_semantics_arrays(
        config.data_root,
        TRACK_TO_OFFICIAL[track],  # type: ignore[arg-type]
        max_dates=config.max_dates,
    )
    dates, open_prices, pct_changes = _align_official_arrays(
        loaded_dates,
        open_prices,
        pct_changes,
        selected_dates[track],
    )
    if not dates:
        raise ValueError(f"No selected official dates are available for Track {track} in {config.data_root}")
    base_weights = _base_weights(assets)
    targets = np.empty((len(dates), len(assets)), dtype=float)
    trace_rows: list[dict[str, Any]] = []
    cache_rows: list[dict[str, Any]] = []
    statuses: list[str] = []
    asset_status_counts: dict[str, int] = {}
    blocked_methods: set[str] = set()
    network_attempted = False
    runtime_seconds = 0.0
    allow_calibration = _period_allows_calibration(config.period)

    for date_index, date in enumerate(dates):
        decision_date = _date_dash(date)
        payload = {
            "decision_date": decision_date,
            "cutoff": config.cutoff,
            "top_rank": config.top_rank,
            "news": news_by_track[track].get(date, []),
            "base_weights": base_weights,
            "rank_ic_rows": _rank_ic_rows_from_returns(assets, pct_changes, dates, date_index) if allow_calibration else [],
            "current_rank_ic": 0.0,
            "sensitivity_rows": _sensitivity_rows_from_returns(assets, pct_changes, dates, date_index) if allow_calibration else [],
            "volatility_by_asset": _volatility_from_history(assets, pct_changes, date_index),
        }
        if config.shuffle_news:
            payload["shuffle_news"] = True
            payload["random_label_seed"] = f"{run_id}:{date}"

        cfg = NewsOverlayConfig(
            track=track,
            n_method=n_method,
            i_method=i_method,
            s_method=s_method,
            offline=config.offline,
            device=config.device,
            batch_size=config.batch_size,
            cache_dir=str(config.cache_dir),
            trace_dir=str(config.trace_dir / run_id),
            proxy_mode=config.proxy_mode or _row_bool(row, "proxy_mode"),
            feature_schema_version=f"news_overlay_schema_v4_prompt07_{config.period}",
            local_model_paths=dict(local_model_paths or {}),
            local_model_metadata=dict(local_model_metadata or {}),
        )
        trace = ScaffoldNewsOverlayPipeline(cfg).run(payload)
        trace_path = JsonTraceWriter().write_trace(trace, config.trace_dir / run_id / f"{date}.json")
        weights = _weights_for_assets(trace, assets, base_weights)
        targets[date_index, :] = [weights.get(asset, 0.0) for asset in assets]
        trace_metrics = _trace_metrics(trace)
        trace_rows.append(
            {
                "run_id": run_id,
                "date": date,
                "trace_path": str(trace_path),
                **trace_metrics,
            }
        )
        cache_rows.extend(_trace_cache_rows(run_id, date, trace))
        statuses.extend(str(result.get("status")) for result in trace.get("results", ()))
        for status, count in ((trace.get("model_status") or {}).get("asset_status_counts") or {}).items():
            asset_status_counts[str(status)] = asset_status_counts.get(str(status), 0) + int(count)
        blocked_methods.update(str(code) for code in (trace.get("model_status") or {}).get("blocked_methods", ()))
        network_attempted = network_attempted or bool((trace.get("model_status") or {}).get("network_attempted"))
        runtime_seconds += float((trace.get("runtime_report") or {}).get("total_runtime_seconds") or 0.0)

    replay = run_reference_official_semantics(
        OfficialSemanticsInput(
            dates=dates,
            assets=assets,
            open_prices=open_prices,
            pct_changes=pct_changes,
            target_weights=targets,
        )
    )
    metrics = replay.metrics
    status = _evaluation_status(statuses)
    summary = {
        "run_id": run_id,
        "section": row.get("section", ""),
        "track": track,
        "n_method": n_method,
        "i_method": i_method,
        "s_method": s_method,
        "base_config": row.get("base_config", ""),
        "period": config.period,
        "data_root": str(config.data_root),
        "date_count": len(dates),
        "proxy_mode": bool(config.proxy_mode or _row_bool(row, "proxy_mode")),
        "evaluation_status": status,
        "grid_status": status,
        "asset_status_counts": json.dumps(asset_status_counts, sort_keys=True),
        "blocked_methods": ";".join(sorted(blocked_methods)),
        "network_attempted": network_attempted,
        "runtime_seconds": round(runtime_seconds, 6),
        **_aggregate_trace_metrics(trace_rows),
        "changed_date_fraction_vs_lexical": "",
        "shuffled_news_delta_sharpe": "",
        "sharpe": round(float(metrics.get("sharpe_ratio", 0.0)), 6),
        "cumret": round(float(metrics.get("cumulative_return", 0.0)), 6),
        "maxdd": round(float(metrics.get("max_drawdown", 0.0)), 6),
        "turnover": round(float(metrics.get("turnover", 0.0)), 6),
        "zero_news_pass": _zero_news_pass(statuses, targets),
        "shuffled_news_pass": "not_run",
        "lexical_baseline_beat": "",
        "decision": _decision_for_status(
            status,
            bool(config.proxy_mode or _row_bool(row, "proxy_mode")),
            str(row.get("transformer_used", "")).lower() == "yes",
        ),
        "notes": _notes_for_run(row, status, blocked_methods, bool(config.proxy_mode or _row_bool(row, "proxy_mode"))),
    }
    return {"summary": summary, "trace_rows": trace_rows, "cache_rows": cache_rows, "target_weights": targets}


def _dates_for_rows(rows: list[dict[str, str]], data_root: Path, max_dates: int) -> dict[str, tuple[str, ...]]:
    tracks = {normalize_track(str(row.get("track"))) for row in rows}
    selected: dict[str, tuple[str, ...]] = {}
    for track in sorted(tracks):
        dates, _, _, _ = load_official_semantics_arrays(data_root, TRACK_TO_OFFICIAL[track], max_dates=max_dates)  # type: ignore[arg-type]
        selected[track] = dates
    return selected


def _align_official_arrays(
    loaded_dates: tuple[str, ...],
    open_prices: np.ndarray,
    pct_changes: np.ndarray,
    selected_dates: tuple[str, ...],
) -> tuple[tuple[str, ...], np.ndarray, np.ndarray]:
    """Keep price tensors aligned when a grid run selects a date subset."""

    selected = set(selected_dates)
    indices = [idx for idx, date in enumerate(loaded_dates) if date in selected]
    return (
        tuple(loaded_dates[idx] for idx in indices),
        open_prices[indices, :],
        pct_changes[indices, :],
    )


def _load_news_by_date(data_root: Path, dates: tuple[str, ...], *, top_rank: int) -> dict[str, list[dict[str, str]]]:
    wanted = set(dates)
    rows_by_date: dict[str, list[dict[str, str]]] = {date: [] for date in dates}
    news_dir = data_root / "news_data"
    if not news_dir.exists():
        return rows_by_date
    for path in sorted(news_dir.glob("*.csv")):
        if path.name == ".gitkeep":
            continue
        for item in _read_csv_rows_with_fallback(path):
            date = _date_compact(item.get("THEDATE") or item.get("date") or item.get("trade_date"))
            if date not in wanted:
                continue
            item = dict(item)
            item.setdefault("SOURCE", path.stem)
            rows_by_date.setdefault(date, []).append(item)
    for date, items in rows_by_date.items():
        items.sort(key=lambda item: (_ranking(item), str(item.get("SOURCE", "")), str(item.get("CONTENT_ID", ""))))
        rows_by_date[date] = items[: max(1, int(top_rank))]
    return rows_by_date


def _read_csv_rows_with_fallback(path: Path) -> list[dict[str, str]]:
    errors: list[str] = []
    for encoding in ("utf-8-sig", "gb18030", "utf-8"):
        try:
            with path.open("r", encoding=encoding, newline="") as handle:
                return [dict(row) for row in csv.DictReader(handle)]
        except UnicodeDecodeError as exc:
            errors.append(f"{encoding}:{exc}")
    raise UnicodeDecodeError("csv", b"", 0, 1, f"Could not decode {path}: {';'.join(errors)}")


def _rank_ic_rows_from_returns(
    assets: tuple[str, ...],
    pct_changes: np.ndarray,
    dates: tuple[str, ...],
    date_index: int,
    lookback: int = 5,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    start = max(0, date_index - lookback)
    for idx in range(start, date_index):
        returns = {asset: round(float(pct_changes[idx, col]) / 100.0, 6) for col, asset in enumerate(assets)}
        rows.append({"date": _date_dash(dates[idx]), "news_scores": returns, "future_returns": returns})
    return rows


def _sensitivity_rows_from_returns(
    assets: tuple[str, ...],
    pct_changes: np.ndarray,
    dates: tuple[str, ...],
    date_index: int,
    lookback: int = 5,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    start = max(0, date_index - lookback)
    for idx in range(start, date_index):
        for col, asset in enumerate(assets):
            rows.append(
                {
                    "date": _date_dash(dates[idx]),
                    "event_type": "none",
                    "asset": asset,
                    "return": round(float(pct_changes[idx, col]) / 100.0, 6),
                    "expected_return": 0.0,
                }
            )
    return rows


def _volatility_from_history(
    assets: tuple[str, ...],
    pct_changes: np.ndarray,
    date_index: int,
    lookback: int = 20,
) -> dict[str, float]:
    start = max(0, date_index - lookback)
    if start >= date_index:
        return {asset: 0.20 for asset in assets}
    window = pct_changes[start:date_index, :] / 100.0
    return {
        asset: round(max(0.01, float(np.std(window[:, col])) * math.sqrt(252)), 6)
        for col, asset in enumerate(assets)
    }


def _weights_for_assets(trace: dict[str, Any], assets: tuple[str, ...], fallback: dict[str, float]) -> dict[str, float]:
    raw = (trace.get("summaries") or {}).get("final_weights") or {}
    weights = {asset: max(0.0, float(raw.get(asset, 0.0))) for asset in assets}
    if not any(weights.values()):
        weights = dict(fallback)
    total = sum(weights.values())
    if total > 0.98:
        weights = {asset: value * 0.98 / total for asset, value in weights.items()}
    return weights


def _trace_metrics(trace: dict[str, Any]) -> dict[str, Any]:
    results = {result.get("kind"): result for result in trace.get("results", ())}
    n_outputs = (results.get("N") or {}).get("outputs") or {}
    rows = list(n_outputs.get("feature_rows") or ())
    feature_count = len(rows)
    aspect_count = sum(1 for row in rows if any(abs(float(value)) > 1e-12 for value in (row.get("aspect_tone") or {}).values()))
    confidence_values = [
        max((float(value) for value in (row.get("event_probabilities") or {}).values()), default=0.0)
        for row in rows
    ]
    attention_values = []
    for row in rows:
        attention_values.extend(float(value) for value in (row.get("sector_query_attention_weights") or {}).values())
    attention_entropy = _entropy(attention_values)
    transformer_active = any(_transformer_result_active(result) for result in trace.get("results", ()))
    cache_report = trace.get("cache_report") or {}
    return {
        "cache_hit_rate": float(cache_report.get("cache_hit_rate") or 0.0),
        "embedding_coverage": round(sum(1 for row in rows if row.get("relevance_by_sector")) / max(1, feature_count), 6),
        "aspect_coverage": round(aspect_count / max(1, feature_count), 6),
        "event_label_confidence": round(sum(confidence_values) / max(1, len(confidence_values)), 6),
        "attention_entropy": attention_entropy,
        "reranker_coverage": 1.0 if (trace.get("summaries") or {}).get("cross_encoder_scores", {}).get("available") else 0.0,
        "transformer_active": 1.0 if transformer_active else 0.0,
    }


def _aggregate_trace_metrics(trace_rows: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "cache_hit_rate": _mean(trace_rows, "cache_hit_rate"),
        "embedding_coverage": _mean(trace_rows, "embedding_coverage"),
        "aspect_coverage": _mean(trace_rows, "aspect_coverage"),
        "event_label_confidence": _mean(trace_rows, "event_label_confidence"),
        "attention_entropy": _mean(trace_rows, "attention_entropy"),
        "reranker_coverage": _mean(trace_rows, "reranker_coverage"),
        "transformer_active_days": int(sum(float(row.get("transformer_active") or 0.0) > 0.0 for row in trace_rows)),
    }


def _attach_comparisons(
    result_rows: list[dict[str, Any]],
    target_weights_by_run: dict[str, np.ndarray],
    row_context: dict[str, dict[str, Any]],
) -> None:
    metrics_by_run = {row["run_id"]: row for row in result_rows}
    for row in result_rows:
        run_id = str(row["run_id"])
        comparison = row_context.get(run_id, {}).get("comparison_run") or ("G01A" if row.get("track") == "A" else "G01B")
        if not comparison or comparison not in metrics_by_run:
            continue
        current = target_weights_by_run.get(run_id)
        baseline = target_weights_by_run.get(str(comparison))
        if current is not None and baseline is not None and current.shape == baseline.shape:
            changed = np.max(np.abs(current - baseline), axis=1) > 1e-8
            row["changed_date_fraction_vs_lexical"] = round(float(np.mean(changed)), 6)
        if _is_number(row.get("sharpe")) and _is_number(metrics_by_run[comparison].get("sharpe")):
            row["lexical_baseline_beat"] = bool(float(row["sharpe"]) > float(metrics_by_run[comparison]["sharpe"]))


def _attach_shuffled_results(
    result_rows: list[dict[str, Any]],
    rows: list[dict[str, str]],
    config: GridEvaluationConfig,
    selected_dates: dict[str, tuple[str, ...]],
    news_by_track: dict[str, dict[str, list[dict[str, str]]]],
) -> None:
    by_run = {row["run_id"]: row for row in result_rows}
    for grid_row in rows:
        run_id = str(grid_row.get("run_id"))
        if run_id not in by_run or str(grid_row.get("transformer_used", "")).lower() != "yes":
            continue
        shuffled_config = GridEvaluationConfig(
            grid_path=config.grid_path,
            data_root=config.data_root,
            output_dir=config.output_dir,
            cache_dir=config.cache_dir,
            trace_dir=config.trace_dir / "shuffled",
            period=f"{config.period}_shuffled",
            max_dates=config.max_dates,
            offline=config.offline,
            device=config.device,
            batch_size=config.batch_size,
            proxy_mode=config.proxy_mode,
            top_rank=config.top_rank,
            cutoff=config.cutoff,
            run_ids=(run_id,),
            include_shuffled=False,
            shuffle_news=True,
        )
        local_model_paths, local_model_metadata, _model_rows = resolve_local_model_context(
            approved_models_path=config.approved_models_path,
            local_models_path=config.local_models_path,
            cache_root=config.cache_root,
            require_local=bool(config.approved_models_path),
        )
        shuffled = _evaluate_one_run(
            grid_row,
            shuffled_config,
            selected_dates,
            news_by_track,
            local_model_paths,
            local_model_metadata,
        )["summary"]
        if _is_number(shuffled.get("sharpe")) and _is_number(by_run[run_id].get("sharpe")):
            delta = round(float(shuffled["sharpe"]) - float(by_run[run_id]["sharpe"]), 6)
            by_run[run_id]["shuffled_news_delta_sharpe"] = delta
            by_run[run_id]["shuffled_news_pass"] = bool(delta <= 0.0)


def _trace_cache_rows(run_id: str, date: str, trace: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for item in (trace.get("cache_report") or {}).get("rows", ()):
        rows.append(
            {
                "run_id": run_id,
                "date": date,
                "trace_id": trace.get("trace_id"),
                "method_code": item.get("method_code"),
                "cache_key": item.get("cache_key"),
                "cache_hit": item.get("cache_hit"),
                "cache_required": item.get("cache_required"),
            }
        )
    return rows


def _checkpoint_stem(period: str, run_id: str) -> str:
    safe = "".join(ch if ch.isalnum() or ch in {"-", "_"} else "_" for ch in f"{period}_{run_id}")
    return safe


def _write_checkpoint(checkpoint_dir: Path, period: str, run_id: str, run_result: dict[str, Any], config: GridEvaluationConfig) -> None:
    stem = _checkpoint_stem(period, run_id)
    weights_path = checkpoint_dir / f"{stem}_target_weights.npy"
    np.save(weights_path, run_result["target_weights"])
    payload = {
        "summary": run_result["summary"],
        "trace_rows": run_result["trace_rows"],
        "cache_rows": run_result["cache_rows"],
        "target_weights_path": str(weights_path),
        "config_fingerprint": _checkpoint_fingerprint(config),
    }
    (checkpoint_dir / f"{stem}.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")


def _load_checkpoint(checkpoint_dir: Path, period: str, run_id: str, config: GridEvaluationConfig) -> dict[str, Any] | None:
    stem = _checkpoint_stem(period, run_id)
    path = checkpoint_dir / f"{stem}.json"
    if not path.exists():
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("config_fingerprint") != _checkpoint_fingerprint(config):
        return None
    weights_path = Path(payload.get("target_weights_path") or "")
    if not weights_path.exists():
        return None
    return {
        "summary": payload["summary"],
        "trace_rows": payload.get("trace_rows", []),
        "cache_rows": payload.get("cache_rows", []),
        "target_weights": np.load(weights_path),
    }


def _checkpoint_fingerprint(config: GridEvaluationConfig) -> dict[str, Any]:
    return {
        "grid_path": str(config.grid_path),
        "data_root": str(config.data_root),
        "period": config.period,
        "max_dates": config.max_dates,
        "top_rank": config.top_rank,
        "cutoff": config.cutoff,
        "device": config.device,
        "batch_size": config.batch_size,
        "proxy_mode": config.proxy_mode,
        "shuffle_news": config.shuffle_news,
        "approved_models_path": str(config.approved_models_path or ""),
        "local_models_path": str(config.local_models_path or ""),
        "cache_root": str(config.cache_root or ""),
    }


def _evaluation_status(statuses: list[str]) -> str:
    blocked = [status for status in statuses if status.startswith("blocked_")]
    if blocked and len(blocked) == len(statuses):
        return blocked[0]
    if blocked:
        return "partial_blocked"
    return "pass"


def _decision_for_status(status: str, proxy_mode: bool, transformer_used: bool) -> str:
    if status.startswith("blocked_"):
        return "blocked_no_local_model"
    if "blocked" in status:
        return "partial_blocked_no_local_model"
    if not transformer_used:
        return "control_or_comparator"
    if proxy_mode:
        return "research_proxy_only"
    return "evaluation_candidate"


def _transformer_result_active(result: dict[str, Any]) -> bool:
    if not bool(result.get("transformer_used")):
        return False
    diagnostics = result.get("diagnostics") or {}
    availability = diagnostics.get("availability") or {}
    asset_status = str(availability.get("asset_status") or availability.get("status") or result.get("status"))
    return str(result.get("status")) == "available" and asset_status in {
        "available",
        "available_proxy_only",
        "available_via_shared_encoder",
    }


def _notes_for_run(row: dict[str, str], status: str, blocked_methods: set[str], proxy_mode: bool) -> str:
    notes = []
    if proxy_mode and str(row.get("transformer_used", "")).lower() == "yes":
        notes.append("proxy-mode transformer evidence; no local model inference")
    if blocked_methods:
        notes.append(f"blocked methods: {'/'.join(sorted(blocked_methods))}")
    if row.get("base_config"):
        notes.append(f"base config reference preserved: {row['base_config']}")
    if status == "pass" and str(row.get("transformer_used", "")).lower() != "yes":
        notes.append("control run only")
    return "; ".join(notes)


def _zero_news_pass(statuses: list[str], targets: np.ndarray) -> bool:
    if targets.size == 0:
        return False
    return bool(np.isfinite(targets).all() and (targets >= -1e-12).all() and all(sum(row) <= 0.980001 for row in targets))


def _base_weights(assets: tuple[str, ...]) -> dict[str, float]:
    invested = 0.97
    if not assets:
        return {}
    return {asset: round(invested / len(assets), 6) for asset in assets}


def _read_grid(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _period_allows_calibration(period: str) -> bool:
    normalized = str(period).lower()
    return normalized.startswith("2024") or "train_2024" in normalized


def _write_csv(path: Path, rows: list[dict[str, Any]], fieldnames: tuple[str, ...]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _ordered_keys(rows: list[dict[str, Any]]) -> tuple[str, ...]:
    keys: list[str] = []
    for row in rows:
        for key in row:
            if key not in keys:
                keys.append(key)
    return tuple(keys) or ("empty",)


def _row_method(row: dict[str, str], snake_key: str, short_key: str) -> str:
    value = row.get(snake_key) or row.get(short_key) or row.get(short_key.lower())
    if not value:
        raise ValueError(f"Grid row is missing {snake_key}/{short_key}: {row}")
    return value.upper()


def _row_bool(row: dict[str, str], key: str) -> bool:
    return str(row.get(key, "")).strip().lower() in {"1", "true", "yes", "y", "on"}


def _date_compact(value: Any) -> str:
    digits = "".join(ch for ch in str(value or "") if ch.isdigit())
    return digits[:8]


def _date_dash(value: Any) -> str:
    digits = _date_compact(value)
    if len(digits) != 8:
        return str(value)
    return f"{digits[:4]}-{digits[4:6]}-{digits[6:]}"


def _ranking(item: dict[str, str]) -> int:
    try:
        return int(float(item.get("RANKING") or item.get("ranking") or 999))
    except ValueError:
        return 999


def _entropy(values: list[float]) -> float:
    positive = [value for value in values if value > 0]
    total = sum(positive)
    if total <= 0:
        return 0.0
    probs = [value / total for value in positive]
    return round(-sum(prob * math.log(prob) for prob in probs), 6)


def _mean(rows: list[dict[str, Any]], key: str) -> float:
    values = [float(row[key]) for row in rows if _is_number(row.get(key))]
    return round(sum(values) / len(values), 6) if values else 0.0


def _counts(values: Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return counts


def _is_number(value: Any) -> bool:
    try:
        float(value)
        return True
    except (TypeError, ValueError):
        return False


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Bounded News Overlay grid evaluator")
    parser.add_argument("--grid", required=True)
    parser.add_argument("--data-root", required=True)
    parser.add_argument("--output-dir", default="outputs/reports/news_overlay/prompt01_11/progress/prompt07")
    parser.add_argument("--cache-dir", default=".var/news_overlay_prompt01_11/cache/prompt07")
    parser.add_argument("--trace-dir", default=".var/news_overlay_prompt01_11/grid_runs/prompt07")
    parser.add_argument("--period", default="2024_bounded")
    parser.add_argument("--max-dates", type=int, default=20)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--proxy-mode", action="store_true", default=False)
    parser.add_argument("--include-shuffled", action="store_true", default=False)
    parser.add_argument("--run-id", action="append", default=[])
    parser.add_argument("--approved-models", default=None)
    parser.add_argument("--local-models", default=None)
    parser.add_argument("--cache-root", default=None)
    parser.add_argument("--no-resume", action="store_true", default=False)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    summary = run_grid_evaluation(
        GridEvaluationConfig(
            grid_path=Path(args.grid),
            data_root=Path(args.data_root),
            output_dir=Path(args.output_dir),
            cache_dir=Path(args.cache_dir),
            trace_dir=Path(args.trace_dir),
            period=args.period,
            max_dates=max(1, int(args.max_dates)),
            device=args.device,
            batch_size=max(1, int(args.batch_size)),
            proxy_mode=bool(args.proxy_mode),
            include_shuffled=bool(args.include_shuffled),
            run_ids=tuple(args.run_id or ()),
            approved_models_path=Path(args.approved_models) if args.approved_models else None,
            local_models_path=Path(args.local_models) if args.local_models else None,
            cache_root=Path(args.cache_root) if args.cache_root else None,
            resume=not bool(args.no_resume),
        )
    )
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
