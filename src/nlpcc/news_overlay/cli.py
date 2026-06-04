"""CLI skeleton for transformer-first News Overlay scaffolding."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from nlpcc.news_overlay.base import MethodRunContext
from nlpcc.news_overlay.cache import CsvCacheManifestWriter, build_cache_key
from nlpcc.news_overlay.config import NewsOverlayConfig, normalize_track
from nlpcc.news_overlay.gpu import resolve_device
from nlpcc.news_overlay.model_availability import check_model_availability
from nlpcc.news_overlay.pipeline import ScaffoldNewsOverlayPipeline
from nlpcc.news_overlay.registry import get_method_spec, list_method_specs, method_status_rows, validate_track_compatibility
from nlpcc.news_overlay.traces import JsonTraceWriter


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="News Overlay scaffold CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-methods", help="List registered N/I/S methods")

    check = subparsers.add_parser("check-models", help="Check offline model availability")
    check.add_argument("--offline", action="store_true", default=False)
    check.add_argument("--device", default="auto")
    check.add_argument("--batch-size", type=int, default=16)

    build = subparsers.add_parser("build-cache", help="Build cache manifest scaffold for one method")
    build.add_argument("--method", required=True)
    build.add_argument("--cache-dir", default=".var/news_overlay_prompt01_11/cache")
    build.add_argument("--date", default="2024-01-01")
    build.add_argument("--text", default="smoke news")
    build.add_argument("--source", default="smoke")
    build.add_argument("--local-path-or-revision", default=None)

    run = subparsers.add_parser("run", help="Run one N/I/S scaffold composition")
    run.add_argument("--track", required=True)
    run.add_argument("--n-method", required=True)
    run.add_argument("--i-method", required=True)
    run.add_argument("--s-method", required=True)
    run.add_argument("--offline", action="store_true", default=True)
    run.add_argument("--device", default="auto")
    run.add_argument("--batch-size", type=int, default=16)
    run.add_argument("--cache-dir", default=".var/news_overlay_prompt01_11/cache")
    run.add_argument("--trace-dir", default=".var/news_overlay_prompt01_11/logs")

    grid = subparsers.add_parser("run-grid", help="Run a smoke grid CSV with run_id,track,n_method,i_method,s_method")
    grid.add_argument("--grid", required=True)
    grid.add_argument("--smoke", action="store_true", default=False)
    grid.add_argument("--offline", action="store_true", default=True)
    grid.add_argument("--device", default="auto")
    grid.add_argument("--batch-size", type=int, default=16)
    grid.add_argument("--cache-dir", default=".var/news_overlay_prompt01_11/cache")
    grid.add_argument("--trace-dir", default=".var/news_overlay_prompt01_11/grid_runs")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "list-methods":
        for spec in list_method_specs():
            print(json.dumps(spec.as_dict(), sort_keys=True))
        return 0
    if args.command == "check-models":
        context = MethodRunContext(track="A", offline=bool(args.offline), device=resolve_device(args.device), batch_size=max(1, int(args.batch_size)))
        for row in method_status_rows(context):
            print(json.dumps(row, sort_keys=True))
        return 0
    if args.command == "build-cache":
        spec = get_method_spec(args.method)
        key = build_cache_key(
            method_code=spec.code,
            model_identifier=spec.model_identifier,
            local_path_or_revision=args.local_path_or_revision,
            preprocessing_version="news_overlay_v1",
            texts=args.text,
            date=args.date,
            sources=args.source,
            feature_schema_version="news_overlay_schema_v4",
        )
        path = Path(args.cache_dir) / "cache_manifest.csv"
        CsvCacheManifestWriter().write_manifest([key.as_dict()], path)
        print(str(path))
        return 0
    if args.command == "run":
        cfg = NewsOverlayConfig(
            track=normalize_track(args.track),
            n_method=args.n_method.upper(),
            i_method=args.i_method.upper(),
            s_method=args.s_method.upper(),
            offline=bool(args.offline),
            device=args.device,
            batch_size=max(1, int(args.batch_size)),
            cache_dir=args.cache_dir,
            trace_dir=args.trace_dir,
        )
        trace = ScaffoldNewsOverlayPipeline(cfg).run()
        path = JsonTraceWriter().write_trace(trace, Path(cfg.trace_dir) / f"{trace['trace_id']}.json")
        _write_trace_sidecars(trace, Path(cfg.trace_dir), trace["trace_id"])
        print(str(path))
        return 0
    if args.command == "run-grid":
        rows = _read_grid(Path(args.grid))
        out_dir = Path(args.trace_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        status_rows: list[dict[str, Any]] = []
        cache_manifest_rows: list[dict[str, Any]] = []
        runtime_rows: list[dict[str, Any]] = []
        for row in rows:
            track = normalize_track(row["track"])
            codes = (_row_method(row, "n_method", "N").upper(), _row_method(row, "i_method", "I").upper(), _row_method(row, "s_method", "S").upper())
            validate_track_compatibility(track, codes)
            cfg = NewsOverlayConfig(
                track=track,
                n_method=codes[0],
                i_method=codes[1],
                s_method=codes[2],
                offline=bool(args.offline),
                device=args.device,
                batch_size=max(1, int(args.batch_size)),
                cache_dir=args.cache_dir,
                trace_dir=str(out_dir),
            )
            trace = ScaffoldNewsOverlayPipeline(cfg).run()
            JsonTraceWriter().write_trace(trace, out_dir / f"{row.get('run_id', trace['trace_id'])}.json")
            run_id = row.get("run_id", trace["trace_id"])
            status_rows.append(_grid_status_row(run_id, row, trace))
            cache_manifest_rows.extend(_trace_cache_rows(run_id, trace))
            runtime_rows.append(_runtime_row(run_id, trace))
            if args.smoke:
                break
        CsvCacheManifestWriter().write_manifest(status_rows, out_dir / "grid_smoke_status.csv")
        CsvCacheManifestWriter().write_manifest(cache_manifest_rows, out_dir / "cache_manifest.csv")
        (out_dir / "cache_hit_rate_report.json").write_text(
            json.dumps(_cache_hit_rate_report(status_rows, cache_manifest_rows), indent=2, sort_keys=True),
            encoding="utf-8",
        )
        (out_dir / "runtime_report.json").write_text(json.dumps(runtime_rows, indent=2, sort_keys=True), encoding="utf-8")
        print(str(out_dir))
        return 0
    raise SystemExit(f"Unsupported command: {args.command}")


def _read_grid(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def _row_method(row: dict[str, str], snake_key: str, short_key: str) -> str:
    value = row.get(snake_key) or row.get(short_key) or row.get(short_key.lower())
    if not value:
        raise SystemExit(f"Grid row is missing {snake_key}/{short_key}: {row}")
    return value


def _write_trace_sidecars(trace: dict[str, Any], out_dir: Path, trace_id: str) -> None:
    CsvCacheManifestWriter().write_manifest(_trace_cache_rows(trace_id, trace), out_dir / f"{trace_id}_cache_manifest.csv")
    (out_dir / f"{trace_id}_cache_report.json").write_text(json.dumps(trace.get("cache_report", {}), indent=2, sort_keys=True), encoding="utf-8")
    (out_dir / f"{trace_id}_runtime_report.json").write_text(json.dumps(trace.get("runtime_report", {}), indent=2, sort_keys=True), encoding="utf-8")


def _trace_cache_rows(run_id: str, trace: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for item in (trace.get("cache_report") or {}).get("rows", ()):
        rows.append(
            {
                "run_id": run_id,
                "trace_id": trace.get("trace_id"),
                "method_code": item.get("method_code"),
                "cache_key": item.get("cache_key"),
                "cache_hit": item.get("cache_hit"),
                "cache_required": item.get("cache_required"),
            }
        )
    return rows


def _grid_status_row(run_id: str, row: dict[str, str], trace: dict[str, Any]) -> dict[str, Any]:
    statuses = [str(result.get("status")) for result in trace.get("results", ())]
    blocked = [status for status in statuses if status.startswith("blocked_")]
    decision_status = blocked[0] if blocked else "pass"
    return {
        "run_id": run_id,
        "section": row.get("section", ""),
        "track": trace.get("track"),
        "n_method": trace.get("n_method"),
        "i_method": trace.get("i_method"),
        "s_method": trace.get("s_method"),
        "base_config": row.get("base_config", ""),
        "grid_smoke_status": decision_status,
        "cache_hit_rate": (trace.get("cache_report") or {}).get("cache_hit_rate", 0.0),
        "runtime_seconds": (trace.get("runtime_report") or {}).get("total_runtime_seconds", 0.0),
        "warnings": ";".join(trace.get("warnings") or ()),
    }


def _runtime_row(run_id: str, trace: dict[str, Any]) -> dict[str, Any]:
    report = trace.get("runtime_report") or {}
    return {
        "run_id": run_id,
        "trace_id": trace.get("trace_id"),
        "total_runtime_seconds": report.get("total_runtime_seconds", 0.0),
        "device": report.get("device"),
        "batch_size": report.get("batch_size"),
        "offline": report.get("offline"),
        "method_runtime_seconds": json.dumps(report.get("method_runtime_seconds", {}), sort_keys=True),
    }


def _cache_hit_rate_report(status_rows: list[dict[str, Any]], cache_rows: list[dict[str, Any]]) -> dict[str, Any]:
    cacheable = [row for row in cache_rows if str(row.get("cache_required")).lower() == "true" or row.get("cache_required") is True]
    hits = [row for row in cacheable if str(row.get("cache_hit")).lower() == "true" or row.get("cache_hit") is True]
    return {
        "run_count": len(status_rows),
        "cacheable_method_count": len(cacheable),
        "cache_hit_count": len(hits),
        "cache_hit_rate": round(len(hits) / len(cacheable), 6) if cacheable else 0.0,
        "grid_status_counts": _counts(row.get("grid_smoke_status") for row in status_rows),
    }


def _counts(values: Any) -> dict[str, int]:
    counts: dict[str, int] = {}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return counts


def check_one_model(method_code: str, *, offline: bool = True) -> dict[str, Any]:
    """Convenience helper for tests."""

    spec = get_method_spec(method_code)
    return check_model_availability(spec, MethodRunContext(track="A", offline=offline)).as_dict()


if __name__ == "__main__":
    raise SystemExit(main())
