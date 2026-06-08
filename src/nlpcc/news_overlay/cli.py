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
from nlpcc.news_overlay.hf_models import (
    PROMPT20_REFERENCE_DIR,
    detect_hf_environment,
    download_approved_models,
    expected_hf_cache_path,
    resolve_local_model_context,
    write_local_model_manifests,
    write_csv,
)
from nlpcc.news_overlay.model_availability import check_model_availability
from nlpcc.news_overlay.pipeline import ScaffoldNewsOverlayPipeline
from nlpcc.news_overlay.registry import get_method_spec, instantiate_method, list_method_specs, method_status_rows, validate_track_compatibility
from nlpcc.news_overlay.traces import JsonTraceWriter


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="News Overlay scaffold CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("list-methods", help="List registered N/I/S methods")

    download = subparsers.add_parser("download-models", help="Explicitly download approved Hugging Face models once")
    download.add_argument("--approved-models", required=True)
    download.add_argument("--model-id", default=None)
    download.add_argument("--cache-root", default=None)
    download.add_argument("--report-dir", default=str(PROMPT20_REFERENCE_DIR))
    download.add_argument("--include-disabled", action="store_true", default=False)
    download.add_argument("--download-user-approved", action="store_true", default=False)
    download.add_argument("--device", default="auto")

    check = subparsers.add_parser("check-models", help="Check offline model availability")
    check.add_argument("--offline", action="store_true", default=False)
    check.add_argument("--device", default="auto")
    check.add_argument("--batch-size", type=int, default=16)
    check.add_argument("--proxy-mode", action="store_true", default=False)
    check.add_argument("--approved-models", default=None)
    check.add_argument("--local-models", default=None)
    check.add_argument("--cache-root", default=None)
    check.add_argument("--local-only", action="store_true", default=False)
    check.add_argument("--report-dir", default=None)

    build = subparsers.add_parser("build-cache", help="Build cache manifest scaffold for one method")
    build.add_argument("--method", required=True)
    build.add_argument("--track", default="B")
    build.add_argument("--cache-dir", default=".var/news_overlay_prompt01_11/cache")
    build.add_argument("--date", default="2024-01-01")
    build.add_argument("--text", default="smoke news")
    build.add_argument("--source", default="smoke")
    build.add_argument("--local-path-or-revision", default=None)
    build.add_argument("--approved-models", default=None)
    build.add_argument("--local-models", default=None)
    build.add_argument("--cache-root", default=None)
    build.add_argument("--local-only", action="store_true", default=False)
    build.add_argument("--device", default="auto")
    build.add_argument("--batch-size", type=int, default=16)

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
    run.add_argument("--proxy-mode", action="store_true", default=False)
    run.add_argument("--approved-models", default=None)
    run.add_argument("--local-models", default=None)
    run.add_argument("--cache-root", default=None)
    run.add_argument("--local-only", action="store_true", default=False)

    grid = subparsers.add_parser("run-grid", help="Run a smoke grid CSV with run_id,track,n_method,i_method,s_method")
    grid.add_argument("--grid", required=True)
    grid.add_argument("--smoke", action="store_true", default=False)
    grid.add_argument("--offline", action="store_true", default=True)
    grid.add_argument("--device", default="auto")
    grid.add_argument("--batch-size", type=int, default=16)
    grid.add_argument("--cache-dir", default=".var/news_overlay_prompt01_11/cache")
    grid.add_argument("--trace-dir", default=".var/news_overlay_prompt01_11/grid_runs")
    grid.add_argument("--proxy-mode", action="store_true", default=False)
    grid.add_argument("--approved-models", default=None)
    grid.add_argument("--local-models", default=None)
    grid.add_argument("--cache-root", default=None)
    grid.add_argument("--local-only", action="store_true", default=False)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.command == "list-methods":
        for spec in list_method_specs():
            print(json.dumps(spec.as_dict(), sort_keys=True))
        return 0
    if args.command == "download-models":
        paths = download_approved_models(
            approved_models_path=args.approved_models,
            cache_root=args.cache_root,
            report_dir=args.report_dir,
            model_id=args.model_id,
            include_disabled=bool(args.include_disabled),
            download_user_approved=bool(args.download_user_approved),
            device=resolve_device(args.device),
        )
        print(json.dumps({key: str(value) for key, value in paths.items()}, sort_keys=True))
        return 0
    if args.command == "check-models":
        local_paths, local_metadata, model_rows = _resolve_model_args(args)
        context = MethodRunContext(
            track="A",
            offline=True if args.local_only else bool(args.offline),
            device=resolve_device(args.device),
            batch_size=max(1, int(args.batch_size)),
            proxy_mode=False if args.local_only else bool(args.proxy_mode),
            local_model_paths=local_paths,
            local_model_metadata=local_metadata,
        )
        rows = method_status_rows(context)
        if args.report_dir:
            report_dir = Path(args.report_dir)
            if args.approved_models:
                write_local_model_manifests(
                    approved_models_path=args.approved_models,
                    local_model_rows=model_rows,
                    report_dir=report_dir,
                )
            write_csv(rows, report_dir / "model_availability_report.csv")
            _write_error_log(report_dir / "error_log.md", rows, model_rows)
        for row in rows:
            print(json.dumps(row, sort_keys=True))
        return 0
    if args.command == "build-cache":
        spec = get_method_spec(args.method)
        if args.local_only:
            local_paths, local_metadata, _ = _resolve_model_args(args)
            context = MethodRunContext(
                track=normalize_track(args.track),
                offline=True,
                device=resolve_device(args.device),
                cache_dir=args.cache_dir,
                local_model_paths=local_paths,
                local_model_metadata=local_metadata,
                preprocessing_version="news_overlay_v1",
                feature_schema_version="news_overlay_schema_v4",
                batch_size=max(1, int(args.batch_size)),
                proxy_mode=False,
            )
            result = instantiate_method(spec.code).run(context, _smoke_payload(args.date, args.text, args.source))
            manifest_row = {
                "method_code": spec.code,
                "cache_key": result.diagnostics.get("cache_key") or result.outputs.get("cache_key"),
                "cache_hit": bool(result.diagnostics.get("cache_hit", False)),
                "status": result.status.value,
                "asset_status": (result.diagnostics.get("availability") or {}).get("asset_status") or result.outputs.get("asset_status"),
                "hf_model_id": (result.diagnostics.get("availability") or {}).get("hf_model_id"),
                "revision_or_commit": (result.diagnostics.get("availability") or {}).get("revision"),
                "local_model_path": (result.diagnostics.get("availability") or {}).get("local_path"),
                "local_only": True,
                "local_files_only": (result.diagnostics.get("availability") or {}).get("local_files_only", True),
                "proxy_mode": False,
            }
            path = Path(args.cache_dir) / "cache_manifest.csv"
            CsvCacheManifestWriter().write_manifest([manifest_row], path)
            print(str(path))
            return 0
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
        local_paths, local_metadata, _ = _resolve_model_args(args)
        cfg = NewsOverlayConfig(
            track=normalize_track(args.track),
            n_method=args.n_method.upper(),
            i_method=args.i_method.upper(),
            s_method=args.s_method.upper(),
            offline=True if args.local_only else bool(args.offline),
            device=args.device,
            batch_size=max(1, int(args.batch_size)),
            cache_dir=args.cache_dir,
            trace_dir=args.trace_dir,
            proxy_mode=False if args.local_only else bool(args.proxy_mode),
            local_model_paths=local_paths,
            local_model_metadata=local_metadata,
        )
        trace = ScaffoldNewsOverlayPipeline(cfg).run(_default_cli_payload())
        path = JsonTraceWriter().write_trace(trace, Path(cfg.trace_dir) / f"{trace['trace_id']}.json")
        _write_trace_sidecars(trace, Path(cfg.trace_dir), trace["trace_id"])
        print(str(path))
        return 0
    if args.command == "run-grid":
        rows = _read_grid(Path(args.grid))
        local_paths, local_metadata, _ = _resolve_model_args(args)
        out_dir = Path(args.trace_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        status_rows: list[dict[str, Any]] = []
        cache_manifest_rows: list[dict[str, Any]] = []
        runtime_rows: list[dict[str, Any]] = []
        for row in rows:
            track = normalize_track(row["track"])
            codes = (_row_method(row, "n_method", "N").upper(), _row_method(row, "i_method", "I").upper(), _row_method(row, "s_method", "S").upper())
            validate_track_compatibility(track, codes)
            proxy_mode = False if args.local_only else (bool(args.proxy_mode) or _row_bool(row, "proxy_mode"))
            cfg = NewsOverlayConfig(
                track=track,
                n_method=codes[0],
                i_method=codes[1],
                s_method=codes[2],
                offline=True if args.local_only else bool(args.offline),
                device=args.device,
                batch_size=max(1, int(args.batch_size)),
                cache_dir=args.cache_dir,
                trace_dir=str(out_dir),
                proxy_mode=proxy_mode,
                local_model_paths=local_paths,
                local_model_metadata=local_metadata,
            )
            trace = ScaffoldNewsOverlayPipeline(cfg).run(_default_cli_payload())
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


def _row_bool(row: dict[str, str], key: str) -> bool:
    value = row.get(key, "")
    return str(value).strip().lower() in {"1", "true", "yes", "y", "on"}


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
    model_rows = (trace.get("model_status") or {}).get("rows", ())
    execution_status = _execution_status(model_rows)
    return {
        "run_id": run_id,
        "section": row.get("section", ""),
        "track": trace.get("track"),
        "n_method": trace.get("n_method"),
        "i_method": trace.get("i_method"),
        "s_method": trace.get("s_method"),
        "base_config": row.get("base_config", ""),
        "grid_smoke_status": decision_status,
        "asset_status_counts": json.dumps((trace.get("model_status") or {}).get("asset_status_counts", {}), sort_keys=True),
        "model_statuses": json.dumps(
            {item.get("method_code"): item.get("asset_status") for item in (trace.get("model_status") or {}).get("rows", ())},
            sort_keys=True,
        ),
        "network_attempted": (trace.get("model_status") or {}).get("network_attempted", False),
        "proxy_mode": (trace.get("config") or {}).get("proxy_mode", False),
        "local_only": bool((trace.get("runtime_report") or {}).get("offline", True)) and not bool((trace.get("config") or {}).get("proxy_mode", False)),
        "execution_status": execution_status,
        "real_model_methods": ";".join(
            row.get("method_code", "")
            for row in model_rows
            if row.get("transformer_used") and row.get("transformer_execution") and not row.get("proxy")
        ),
        "proxy_only_methods": ";".join(row.get("method_code", "") for row in model_rows if row.get("proxy")),
        "blocked_methods": ";".join(row.get("method_code", "") for row in model_rows if str(row.get("status", "")).startswith("blocked_")),
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


def _execution_status(model_rows: Any) -> str:
    rows = list(model_rows or ())
    if any(str(row.get("status", "")).startswith("blocked_") for row in rows):
        if any(row.get("transformer_used") and row.get("transformer_execution") and not row.get("proxy") for row in rows):
            return "mixed_real_blocked"
        return "blocked_missing_model"
    if any(row.get("proxy") for row in rows):
        return "proxy_only"
    if any(row.get("transformer_used") and row.get("transformer_execution") for row in rows):
        return "real_model_executed"
    return "no_model_required"


def _resolve_model_args(args: Any) -> tuple[dict[str, str], dict[str, dict[str, str]], list[dict[str, Any]]]:
    approved = getattr(args, "approved_models", None)
    local_models = getattr(args, "local_models", None)
    cache_root = getattr(args, "cache_root", None)
    require_local = bool(getattr(args, "local_only", False) and approved)
    return resolve_local_model_context(
        approved_models_path=approved,
        local_models_path=local_models,
        cache_root=cache_root,
        require_local=require_local,
    )


def _smoke_payload(date: str, text: str, source: str) -> dict[str, Any]:
    return {
        "decision_date": date,
        "news": [
            {
                "SOURCE": source,
                "TITLE": text,
                "CONTENT": text,
                "RANKING": 1,
                "THEDATE": date,
                "PUBLISH_TIME": f"{date} 14:20:00",
            }
        ],
    }


def _default_cli_payload() -> dict[str, Any]:
    return _smoke_payload("2024-02-05", "央行宣布降准释放长期流动性", "prompt20_1_smoke")


def _write_error_log(path: Path, rows: list[dict[str, Any]], model_rows: list[dict[str, Any]]) -> Path:
    blocked = [row for row in rows if str(row.get("asset_status")).startswith("blocked_")]
    env = detect_hf_environment()
    lines = [
        "# Prompt20.1 News Overlay Error Log",
        "",
        f"Default cache path: `{expected_hf_cache_path()}`",
        "",
        "## Environment Overrides",
        "",
    ]
    if env:
        lines.extend(f"- `{key}` = `{value}`" for key, value in sorted(env.items()))
    else:
        lines.append("- none detected")
    lines.extend(["", "## Approved Model Local Checks", ""])
    if model_rows:
        for row in model_rows:
            lines.append(f"- `{row.get('model_role')}` `{row.get('hf_model_id')}`: {row.get('load_status')} at `{row.get('local_cache_path')}`")
    else:
        lines.append("- no approved model config supplied")
    lines.extend(["", "## Blocked Method Rows", ""])
    if blocked:
        for row in blocked:
            lines.append(f"- `{row.get('code')}`: {row.get('asset_status')} ({row.get('availability_reason')})")
    else:
        lines.append("- none")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def check_one_model(method_code: str, *, offline: bool = True) -> dict[str, Any]:
    """Convenience helper for tests."""

    spec = get_method_spec(method_code)
    return check_model_availability(spec, MethodRunContext(track="A", offline=offline)).as_dict()


if __name__ == "__main__":
    raise SystemExit(main())
