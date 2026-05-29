#!/usr/bin/env python3
"""Prompt13 verification-heavy audit runner.

This script generates prompt13 audit artifacts without changing strategy logic.
It intentionally treats official/server parity as evidence to test, not as an
assumption.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any
from urllib import error, parse, request
import zipfile


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nlpcc.core.fund_universe import get_fund_pool  # noqa: E402
from nlpcc.stage1_news.cache import stage1_cache_key  # noqa: E402
from nlpcc.stage1_news.pipeline import run_stage1_news_pipeline  # noqa: E402
from nlpcc.stage2_text_store.pipeline import build_stage2_text_state  # noqa: E402
from nlpcc.stage4_agent.models.robust_bl_agent import RobustBLAgent  # noqa: E402
from tools.backtesting.local_backtester import LocalSmokeBacktester  # noqa: E402
from tools.backtesting.metrics import compute_backtest_metrics  # noqa: E402
from tools.experiments.runner import build_agent  # noqa: E402


REPORT_DIR = REPO_ROOT / "outputs" / "reports" / "prompt13"
BACKTEST_DIR = REPO_ROOT / "outputs" / "backtests" / "prompt13"
PARITY_DIR = REPORT_DIR / "parity_runs"

MACRO_CONSTRAINTS = {"max_weight": 0.7, "cash_reserve": 0.03, "max_turnover": 0.6}
SECTOR_CONSTRAINTS = {"max_weight": 0.5, "cash_reserve": 0.03, "max_turnover": 0.6}


@dataclass(frozen=True)
class RunSpec:
    name: str
    track: str
    agent_name: str
    agent_params: dict[str, Any]
    load_news: bool = False
    notes: str = ""


FULL_YEAR_SPECS = (
    RunSpec("s0_macro", "macro", "s0_equal_weight", {"max_weight": 0.7}),
    RunSpec("s1_macro", "macro", "s1_quant_core", {"track": "macro", "max_weight": 0.7}),
    RunSpec("robust_bl_track1", "macro", "robust_bl", {"track": "macro", "constraints": MACRO_CONSTRAINTS}, True),
    RunSpec("robust_bl_no_news", "macro", "robust_bl", {"track": "macro", "constraints": MACRO_CONSTRAINTS}),
    RunSpec(
        "robust_bl_no_confidence",
        "macro",
        "robust_bl",
        {
            "track": "macro",
            "constraints": MACRO_CONSTRAINTS,
            "min_view_confidence": 0.0,
            "stage2": {"min_confidence": 0.0, "max_confidence": 1.0},
        },
        True,
    ),
    RunSpec(
        "robust_bl_no_turnover_control",
        "macro",
        "robust_bl",
        {
            "track": "macro",
            "constraints": {"max_weight": 0.7, "cash_reserve": 0.03, "max_turnover": 1.0, "rebalance_threshold": 0.0},
        },
        True,
    ),
    RunSpec(
        "robust_bl_rule_based_views",
        "macro",
        "robust_bl",
        {"track": "macro", "constraints": MACRO_CONSTRAINTS, "stage1": {"use_llm": False}},
        True,
        "Stage 1 is deterministic rule-based by default, so this is expected to match the base robust BL run.",
    ),
    RunSpec("oco_fallback_macro", "macro", "oco_ensemble", {"track": "macro", "constraints": MACRO_CONSTRAINTS}, True),
    RunSpec("s0_sector", "sector", "s0_equal_weight", {"max_weight": 0.5}),
    RunSpec("s1_sector", "sector", "s1_quant_core", {"track": "sector", "max_weight": 0.5}),
    RunSpec("sector_rotation_track2", "sector", "sector_rotation", {"track": "sector", "constraints": SECTOR_CONSTRAINTS}, True),
    RunSpec(
        "sector_without_news",
        "sector",
        "sector_rotation",
        {"track": "sector", "constraints": SECTOR_CONSTRAINTS, "use_news": False, "news_weight": 0.0},
    ),
    RunSpec(
        "sector_without_graph",
        "sector",
        "sector_rotation",
        {"track": "sector", "constraints": SECTOR_CONSTRAINTS, "use_graph": False, "graph_weight": 0.0},
        True,
    ),
    RunSpec(
        "sector_momentum_only",
        "sector",
        "sector_rotation",
        {
            "track": "sector",
            "constraints": SECTOR_CONSTRAINTS,
            "use_news": False,
            "use_graph": False,
            "use_trend": True,
            "trend_weight": 1.0,
            "news_weight": 0.0,
            "graph_weight": 0.0,
        },
        False,
        "Uses the sector trend sleeve only; this is the available momentum/trend-only proxy.",
    ),
)

PUBLIC_A_SPECS = (
    RunSpec("s0_macro", "macro", "s0_equal_weight", {"max_weight": 0.7}),
    RunSpec("s1_macro", "macro", "s1_quant_core", {"track": "macro", "max_weight": 0.7}),
    RunSpec("robust_bl_track1", "macro", "robust_bl", {"track": "macro", "constraints": MACRO_CONSTRAINTS}, True),
    RunSpec("oco_fallback_macro", "macro", "oco_ensemble", {"track": "macro", "constraints": MACRO_CONSTRAINTS}, True),
    RunSpec("s0_sector", "sector", "s0_equal_weight", {"max_weight": 0.5}),
    RunSpec("s1_sector", "sector", "s1_quant_core", {"track": "sector", "max_weight": 0.5}),
    RunSpec("sector_rotation_track2", "sector", "sector_rotation", {"track": "sector", "constraints": SECTOR_CONSTRAINTS}, True),
)

PARITY_SPECS = (
    RunSpec("s0_equal_weight_macro", "macro", "s0_equal_weight", {"max_weight": 0.7}),
    RunSpec("s1_macro", "macro", "s1_quant_core", {"track": "macro", "max_weight": 0.7}),
    RunSpec("robust_bl_track1", "macro", "robust_bl", {"track": "macro", "constraints": MACRO_CONSTRAINTS}, True),
)

NEWS_CACHE: dict[str, list[tuple[Any, datetime, int, dict[str, Any]]]] = {}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate prompt13 audit artifacts.")
    parser.add_argument("--skip-backtests", action="store_true", help="Collect existing outputs only.")
    parser.add_argument("--skip-official-parity", action="store_true", help="Do not call the official HTTP server.")
    parser.add_argument("--base-url", default="http://localhost:6207")
    parser.add_argument("--parity-start", default="2024-01-02")
    parser.add_argument("--parity-end", default="2024-01-31")
    return parser.parse_args()


def rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")


def md_table(headers: list[str], rows: list[list[Any]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(format_cell(value) for value in row) + " |")
    return "\n".join(lines)


def format_cell(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6f}"
    text = str(value)
    return text.replace("\n", " ").replace("|", "\\|")


def read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def path_status(path: str) -> str:
    return "ok" if (REPO_ROOT / path).exists() else "missing"


def count_files(path: Path, pattern: str = "*") -> int:
    return sum(1 for item in path.rglob(pattern) if item.is_file()) if path.exists() else 0


def get_common_date_count(data_root: Path, track: str, start: str, end: str) -> int:
    start_int = int(start.replace("-", ""))
    end_int = int(end.replace("-", ""))
    assets = [fund for fund in get_fund_pool(track) if (data_root / "price_data" / f"{fund}.csv").exists()]
    common_dates: set[str] | None = None
    for fund_id in assets:
        with (data_root / "price_data" / f"{fund_id}.csv").open("r", encoding="utf-8-sig", newline="") as handle:
            dates = {row["date"] for row in csv.DictReader(handle) if start_int <= int(row["date"]) <= end_int}
        common_dates = dates if common_dates is None else common_dates & dates
    return len(common_dates or set())


def run_local_spec(data_root: Path, spec: RunSpec, output_path: Path, *, max_dates: int | None = None) -> dict[str, Any]:
    backtester = LocalSmokeBacktester(
        data_root=data_root,
        track=spec.track,  # type: ignore[arg-type]
        agent=build_agent(spec.agent_name, spec.agent_params),
        lookback_days=60,
        load_news=spec.load_news,
        news_lookback_calendar_days=1,
        max_dates=max_dates,
    )
    if spec.load_news:
        key = str(data_root.resolve())
        if key not in NEWS_CACHE:
            NEWS_CACHE[key] = backtester._load_all_news_rows()
        backtester._news_cache = NEWS_CACHE[key]
    result = backtester.run(output_path)
    result["prompt13_spec"] = {"name": spec.name, "notes": spec.notes}
    output_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    return result


def summarize_result(result: dict[str, Any], name: str, spec: RunSpec, status: str = "ok", notes: str = "") -> dict[str, Any]:
    metrics = result.get("metrics", {}) if result else {}
    history = result.get("portfolio_history", []) if result else []
    dates = [row.get("date") for row in history if row.get("date")]
    date_range = f"{dates[0]}-{dates[-1]}" if dates else ""
    return {
        "run": name,
        "track": spec.track,
        "date_range": date_range,
        "final_value": result.get("final_value") if result else None,
        "cum_return": metrics.get("cumulative_return"),
        "sharpe": metrics.get("sharpe_ratio"),
        "max_drawdown": metrics.get("max_drawdown"),
        "turnover": metrics.get("turnover"),
        "status": status,
        "notes": notes or spec.notes,
    }


def run_backtest_set(
    specs: tuple[RunSpec, ...],
    data_root: Path,
    output_subdir: str,
    *,
    skip: bool,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    summaries: list[dict[str, Any]] = []
    raw_results: list[dict[str, Any]] = []
    for spec in specs:
        out_path = BACKTEST_DIR / output_subdir / f"{spec.name}.json"
        try:
            if skip and out_path.exists():
                result = read_json(out_path)
            else:
                print(f"running {output_subdir}:{spec.name}", flush=True)
                result = run_local_spec(data_root, spec, out_path)
            raw_results.append(result)
            summaries.append(summarize_result(result, spec.name, spec, notes=spec.notes))
        except Exception as exc:  # pragma: no cover - audit diagnostics
            summaries.append(
                {
                    "run": spec.name,
                    "track": spec.track,
                    "date_range": "",
                    "final_value": None,
                    "cum_return": None,
                    "sharpe": None,
                    "max_drawdown": None,
                    "turnover": None,
                    "status": "fail",
                    "notes": f"{type(exc).__name__}: {exc}",
                }
            )
    return summaries, raw_results


def json_request(method: str, base_url: str, endpoint: str, payload: dict[str, Any] | None = None, token: str | None = None) -> dict[str, Any]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = request.Request(f"{base_url.rstrip('/')}{endpoint}", data=data, headers=headers, method=method)
    with request.urlopen(req, timeout=10) as response:
        raw = response.read().decode("utf-8")
    return json.loads(raw) if raw else {}


def form_request(base_url: str, endpoint: str, payload: dict[str, str]) -> dict[str, Any]:
    data = parse.urlencode(payload).encode("utf-8")
    req = request.Request(
        f"{base_url.rstrip('/')}{endpoint}",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with request.urlopen(req, timeout=10) as response:
        return json.loads(response.read().decode("utf-8"))


def official_available(base_url: str) -> tuple[bool, str]:
    for endpoint in ("/api/health/ready", "/api/funds/funds", "/api"):
        try:
            json_request("GET", base_url, endpoint)
            return True, endpoint
        except Exception:
            continue
    return False, f"Official server is not reachable at {base_url}."


def official_login(base_url: str, username: str, password: str) -> str:
    try:
        json_request("POST", base_url, "/api/agents/register", {"username": username, "password": password})
    except Exception:
        pass
    return str(form_request(base_url, "/api/agents/token", {"username": username, "password": password}).get("access_token"))


def official_values_to_metrics(results: dict[str, Any]) -> dict[str, float]:
    values = [float(row.get("value", 0.0) or 0.0) for row in results.get("portfolio_value_history", [])]
    values = [value for value in values if value > 0]
    return compute_backtest_metrics(values).as_dict() if values else {}


def run_official_spec(base_url: str, spec: RunSpec, start: str, end: str) -> dict[str, Any]:
    username = f"prompt13_{spec.name}"
    password = "prompt13_audit"
    token = official_login(base_url, username, password)
    fund_pool = list(get_fund_pool(spec.track))  # type: ignore[arg-type]
    config = {
        "start_date": start,
        "end_date": end,
        "initial_capital": 100000.0,
        "fund_pool": fund_pool,
        "agents": [{"name": username, "prompt": "prompt13 parity"}],
        "news_sources": ["caixin", "tiantian", "sinafinance", "tencent"],
        "lookback_days": 60,
        "top_rank": 20,
        "pre_k_days": 1,
        "view_platform_trading_history_days": 1,
        "decision_model_name": "prompt13_no_api",
        "results_dir": "../../outputs/reports/prompt13/official_server_sessions",
    }
    start_response = json_request("POST", base_url, "/api/backtest/start", config, token=token)
    session_id = start_response["session_id"]
    data = start_response.get("data", {})
    agent = build_agent(spec.agent_name, spec.agent_params)
    decisions: list[dict[str, Any]] = []
    trade_results: list[dict[str, Any]] = []
    while True:
        status = json_request("GET", base_url, f"/api/backtest/{session_id}/status", token=token)
        historical = json_request("GET", base_url, f"/api/backtest/{session_id}/historical_prices?lookback_days=60", token=token)
        decision = agent.make_decision(
            track=spec.track,
            fund_pool=fund_pool,
            historical_prices=historical.get("historical_prices", {}),
            news=data.get("news", []),
            current_portfolio=status,
        )
        trades = [
            trade
            for trade in decision.get("trades", [])
            if trade.get("action") in {"buy", "sell"} and (trade.get("amount") or trade.get("percentage"))
        ]
        submitted = None
        if trades:
            submitted = json_request(
                "POST",
                base_url,
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
            trade_results.extend(submitted.get("trade_execution_results", []))
        decisions.append({"date": data.get("date"), "trades": trades, "submitted": submitted})
        data = json_request("GET", base_url, f"/api/backtest/{session_id}/next_day", token=token)
        if data.get("message") == "Backtest finished":
            break
    results = json_request("GET", base_url, f"/api/backtest/results/{session_id}", token=token)
    return {
        "status": "ok",
        "session_id": session_id,
        "strategy": spec.name,
        "track": spec.track,
        "date_range": f"{start}-{end}",
        "performance": results.get("performance", {}),
        "metrics": official_values_to_metrics(results),
        "results": results,
        "decisions": decisions,
        "trade_execution_results": trade_results,
    }


def run_parity(base_url: str, start: str, end: str, *, skip: bool) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    available, detail = official_available(base_url)
    if not available:
        for spec in PARITY_SPECS:
            rows.append(
                {
                    "strategy": spec.name,
                    "track": spec.track,
                    "date_range": f"{start}-{end}",
                    "local_final_value": None,
                    "official_final_value": None,
                    "abs_diff": None,
                    "rel_diff": None,
                    "metric_match": "no",
                    "trade_match": "no",
                    "status": "blocked",
                    "notes": f"{detail} Rerun: python scripts/run_prompt13_audit.py --base-url {base_url}",
                }
            )
        return rows

    max_dates = get_common_date_count(REPO_ROOT / "data" / "train_2024", "macro", start, end)
    for spec in PARITY_SPECS:
        try:
            local_path = PARITY_DIR / f"local_{spec.name}.json"
            official_path = PARITY_DIR / f"official_{spec.name}.json"
            if skip and local_path.exists() and official_path.exists():
                local = read_json(local_path)
                official = read_json(official_path)
            else:
                print(f"running parity:{spec.name}", flush=True)
                local = run_local_spec(REPO_ROOT / "data" / "train_2024", spec, local_path, max_dates=max_dates)
                official = run_official_spec(base_url, spec, start, end)
                write_json(official_path, official)
            local_final = float(local.get("final_value", 0.0) or 0.0)
            official_final = float(official.get("performance", {}).get("final_portfolio_value", 0.0) or 0.0)
            abs_diff = abs(local_final - official_final)
            rel_diff = abs_diff / local_final if local_final else None
            metric_match = "yes" if rel_diff is not None and rel_diff <= 1e-6 else "no"
            local_trades = len(local.get("transactions", []))
            official_trades = len([item for item in official.get("trade_execution_results", []) if item.get("success")])
            trade_match = "yes" if local_trades == official_trades else "no"
            status = "pass" if metric_match == "yes" and trade_match == "yes" else "fail"
            if status == "fail" and rel_diff is not None and rel_diff < 0.001:
                status = "minor_diff"
            rows.append(
                {
                    "strategy": spec.name,
                    "track": spec.track,
                    "date_range": f"{start}-{end}",
                    "local_final_value": local_final,
                    "official_final_value": official_final,
                    "abs_diff": abs_diff,
                    "rel_diff": rel_diff,
                    "metric_match": metric_match,
                    "trade_match": trade_match,
                    "status": status,
                    "notes": (
                        f"Local trades={local_trades}; official accepted trades={official_trades}. "
                        "Official portfolio exposes holding value, while src agents expect share-like holdings; root official adapter is missing."
                    ),
                }
            )
        except Exception as exc:  # pragma: no cover - audit diagnostics
            rows.append(
                {
                    "strategy": spec.name,
                    "track": spec.track,
                    "date_range": f"{start}-{end}",
                    "local_final_value": None,
                    "official_final_value": None,
                    "abs_diff": None,
                    "rel_diff": None,
                    "metric_match": "no",
                    "trade_match": "no",
                    "status": "blocked",
                    "notes": f"{type(exc).__name__}: {exc}",
                }
            )
    return rows


def load_price_window(data_root: Path, track: str, date_int: str, lookback: int = 60) -> dict[str, list[dict[str, Any]]]:
    prices: dict[str, list[dict[str, Any]]] = {}
    for fund_id in get_fund_pool(track):  # type: ignore[arg-type]
        path = data_root / "price_data" / f"{fund_id}.csv"
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            rows = list(csv.DictReader(handle))
        index = next((idx for idx, row in enumerate(rows) if row["date"] == date_int), None)
        if index is None:
            continue
        start = max(0, index - lookback + 1)
        window: list[dict[str, Any]] = []
        for idx in range(start, index):
            row = rows[idx]
            window.append(
                {
                    "date_int": int(row["date"]),
                    "open": float(row["open"]),
                    "close": float(row["close"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "change": float(row.get("change", 0.0) or 0.0),
                    "pct_change": float(row.get("pctchange", 0.0) or 0.0),
                }
            )
        current = rows[index]
        window.append(
            {
                "date_int": int(current["date"]),
                "open": float(current["open"]),
                "close": None,
                "high": None,
                "low": None,
                "change": None,
                "pct_change": None,
            }
        )
        prices[fund_id] = window
    return prices


def news_for_date(data_root: Path, date_int: str) -> list[dict[str, Any]]:
    loader = LocalSmokeBacktester(data_root=data_root, track="macro", load_news=True)
    key = str(data_root.resolve())
    if key not in NEWS_CACHE:
        NEWS_CACHE[key] = loader._load_all_news_rows()
    loader._news_cache = NEWS_CACHE[key]
    return loader._load_news(date_int)


def trace_stage1() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    data_root = REPO_ROOT / "data" / "train_2024"
    dates = ["20240102", "20240115", "20240205"]
    trace_rows: list[dict[str, Any]] = []
    agent = RobustBLAgent.from_config({"track": "macro", "constraints": MACRO_CONSTRAINTS})
    for date_int in dates:
        news = news_for_date(data_root, date_int)
        stage1 = run_stage1_news_pipeline(news, decision_date=date_int)
        stage2 = build_stage2_text_state(stage1, as_of_date=date_int)
        prices = load_price_window(data_root, "macro", date_int)
        portfolio = {"cash": 100000.0, "holdings": {}}
        with_news = agent.make_decision(
            track="macro",
            fund_pool=list(get_fund_pool("macro")),
            historical_prices=prices,
            news=news,
            current_portfolio=portfolio,
        )
        without_news = agent.make_decision(
            track="macro",
            fund_pool=list(get_fund_pool("macro")),
            historical_prices=prices,
            news=[],
            current_portfolio=portfolio,
        )
        weights_a = with_news.get("target_weights", {})
        weights_b = without_news.get("target_weights", {})
        deltas = {asset: float(weights_a.get(asset, 0.0)) - float(weights_b.get(asset, 0.0)) for asset in set(weights_a) | set(weights_b)}
        max_delta = max((abs(value) for value in deltas.values()), default=0.0)
        trace_rows.append(
            {
                "date": date_int,
                "news_count": len(news),
                "stage1_method": stage1.diagnostics.get("model", "fallback"),
                "extracted_signals": f"events={len(stage1.events)}, sectors={len(stage1.sector_impacts)}, bl_views={len(stage1.bl_views)}",
                "stage2_state": f"events={len(stage2.event_table)}, bl_views={len(stage2.bl_views)}, confidence_labels={len(stage2.confidence_matrix.labels)}",
                "allocation_impact": f"max_abs_weight_delta={max_delta:.6f}",
                "trace_complete": "yes" if news and stage2.bl_views and weights_a else "partial",
                "notes": f"cache_key={stage1_cache_key([item.get('TITLE', '') for item in news])[:12]}; fallback={stage1.fallback_used}",
            }
        )

    components = [
        ["news schema", "src/nlpcc/stage1_news/schema.py", "yes", "yes", "yes", "NormalizedNewsItem and Stage1Output."],
        ["rule-based extraction", "src/nlpcc/stage1_news/models/rule_based_extractor.py", "yes", "yes", "yes", "Default Stage 1 method."],
        ["LLM extraction or cached extraction", "src/nlpcc/stage1_news/models/llm_event_extractor.py", "partial", "no", "partial", "Optional injected callable only; no default model or cache integration."],
        ["event tuple extraction", "src/nlpcc/stage1_news/models/event_tuple_extractor.py", "yes", "yes", "yes", "Rule-based tuple extraction."],
        ["BL view extraction", "src/nlpcc/stage1_news/models/bl_view_extractor.py", "yes", "yes", "yes", "Feeds robust BL through Stage 2."],
        ["sector impact extraction", "src/nlpcc/stage1_news/models/sector_impact_extractor.py", "yes", "yes", "yes", "Used by sector rotation."],
        ["news denoising / relevance filtering", "src/nlpcc/stage1_news/pipeline.py", "partial", "yes", "yes", "Rank, empty text, future date, and cutoff filters; no learned denoiser."],
        ["prompt/version metadata", "src/nlpcc/stage1_news/prompts/", "partial", "no", "partial", "Prompt files exist but are not used by default rule path."],
        ["input hash / cache key", "src/nlpcc/stage1_news/cache.py", "partial", "no", "yes", "Cache key helper exists; pipeline does not automatically cache."],
        ["same-day cutoff handling", "src/nlpcc/stage1_news/pipeline.py", "yes", "yes", "yes", "Filters same-day items at or after 15:00."],
        ["no-LLM fallback", "src/nlpcc/stage1_news/models/no_llm_fallback.py", "yes", "yes", "yes", "Used for missing or invalid news."],
    ]
    component_rows = [
        {
            "component": item[0],
            "path": item[1],
            "implemented": item[2],
            "used": item[3],
            "reproducible": item[4],
            "notes": item[5],
        }
        for item in components
    ]
    return trace_rows, component_rows


def inventory_rows() -> list[dict[str, Any]]:
    rows = [
        ["Source package", "src/nlpcc/", "src/nlpcc/ exists; src/nlpcc4/ absent", "ok", "Implemented package is nlpcc."],
        ["Official wrapper", "NLPCC_tasks/agent_platform/agents/build_agent.py", "missing", "missing", "Required root wrapper is absent."],
        ["System configs", "S0/S1 robust BL sector OCO configs", "configs/systems contains all primary system config files", "ok", ""],
        ["Stage modules", "Stage 1-4 folders with pipeline/schema/validators/models", "folders exist; several Stage 4/runtime/execution files are placeholders", "partial", "system_runner, official_adapter, order_planner, stage4 pipeline are placeholders."],
        ["Outputs", "backtests, experiments, reports, submissions", "all output categories exist", "ok", ""],
        ["Official starter", "NLPCC_tasks server/client/dataset", "starter server, client, price/news data exist", "ok", ""],
        ["Tests", "tests/ coverage for core stages/tools", f"{count_files(REPO_ROOT / 'tests', '*.py')} top-level test files plus nested tests", "ok", "Prompt12 reported 82 passing tests."],
        ["Docs consistency", "docs match actual package and wrapper state", "src/nlpcc is consistent; wrapper and implemented-vs-target maturity are inconsistent", "inconsistent", "Docs describe wrapper and adapters that are missing or placeholders."],
        ["Submission package", "clean code package with official wrapper", "prompt12 package exists but lacks NLPCC_tasks wrapper", "partial", "Packaging helper silently skipped missing wrapper."],
    ]
    return [{"area": r[0], "expected": r[1], "found": r[2], "status": r[3], "notes": r[4]} for r in rows]


def maturity_rows(full_year: list[dict[str, Any]]) -> list[dict[str, Any]]:
    used = {row["run"] for row in full_year if row.get("status") == "ok"}
    rows = [
        ["S0 equal weight", "src/nlpcc/stage4_agent/models/s0_equal_weight_agent.py", "configs/systems/s0_equal_weight.yaml", "test_s0_s1_baselines.py", "production_candidate", "s0_macro" in used and "s0_sector" in used, "2024 and 2025 local runs", "yes, as baseline/fallback", ""],
        ["S1 quant core", "src/nlpcc/stage4_agent/models/s1_quant_core.py", "configs/systems/s1_macro.yaml; configs/systems/s1_sector.yaml", "test_s0_s1_baselines.py", "production_candidate", "s1_macro" in used and "s1_sector" in used, "2024 and 2025 local runs", "yes", ""],
        ["inverse volatility", "src/nlpcc/stage3_trade/models/inverse_volatility.py", "configs/stage3_trade/risk_state.yaml", "test_stage3_pipeline.py", "production_candidate", True, "component of S1", "yes, as component", ""],
        ["momentum", "src/nlpcc/stage3_trade/models/momentum.py", "configs/stage3_trade/momentum.yaml", "test_stage3_pipeline.py", "production_candidate", True, "component of S1", "yes, as component", ""],
        ["sector trend-following", "src/nlpcc/stage3_trade/models/sector_trend.py", "configs/stage3_trade/momentum.yaml", "test_prompt08_sector_agents.py", "production_candidate", True, "S1 sector and sector_momentum_only", "yes, as Track 2 baseline", ""],
        ["robust Black-Litterman", "src/nlpcc/stage4_agent/models/robust_bl_agent.py", "configs/systems/robust_bl_track1.yaml", "test_prompt07_agents.py", "production_candidate", "robust_bl_track1" in used, "best local 2024 Track 1 Sharpe in current evidence", "yes, local candidate only until official parity fixed", ""],
        ["risk parity", "src/nlpcc/stage4_agent/models/risk_parity_agent.py", "configs/systems/risk_parity_track1.yaml", "test_portfolio_prompt07.py", "working_prototype", False, "prompt07 local run exists", "yes, as component/fallback", ""],
        ["belief-state risk parity", "src/nlpcc/stage4_agent/models/belief_rp_agent.py", "none", "none", "research_stub", False, "placeholder only", "no", ""],
        ["HMM / Kalman / MPC", "src/nlpcc/stage4_agent/models/hmm_kalman_mpc_agent.py; src/nlpcc/stage3_trade/models/price_hmm_state.py", "none", "none", "research_stub", False, "placeholder only", "no", ""],
        ["sector impact model", "src/nlpcc/stage1_news/models/sector_impact_extractor.py; src/nlpcc/stage2_text_store/models/sector_impact_panel.py", "configs/stage1_news/sector_impact.yaml", "test_prompt08_sector_mapping.py", "working_prototype", "sector_rotation_track2" in used, "sector runs and traces", "yes, deterministic/rule-based", ""],
        ["KG-MoE", "src/nlpcc/stage4_agent/models/kg_moe_lite_agent.py", "configs/systems/kg_moe_lite_track2.yaml", "test_prompt08_sector_agents.py", "working_prototype", False, "prompt08 local run exists, not prompt13 promoted", "limited: KG-MoE-Lite only", "No full GNN/MoE."],
        ["retrieval analogue memory", "src/nlpcc/stage2_text_store/models/retrieval_index.py; src/nlpcc/stage4_agent/models/retrieval_meta_agent.py", "configs/stage2_text_store/retrieval_index.yaml", "none", "research_stub", False, "placeholder only", "no", ""],
        ["transformer-style event memory", "none", "none", "none", "documented_only", False, "no code", "no", ""],
        ["OCO / online mirror descent ensemble", "src/nlpcc/stage4_agent/models/oco_ensemble_agent.py", "configs/systems/oco_fallback.yaml", "test_prompt09_ensembles.py", "working_prototype", "oco_fallback_macro" in used, "local 2024/2025 runs", "limited: OCO-inspired gating", "No persistent online state across days."],
        ["learning-to-rank", "src/nlpcc/stage4_agent/models/learning_to_rank_agent.py", "none", "none", "research_stub", False, "placeholder only", "no", ""],
        ["causal/invariant event-impact model", "src/nlpcc/stage4_agent/models/causal_invariant_agent.py; src/nlpcc/stage2_text_store/models/causal_event_graph.py", "configs/stage2_text_store/causal_event_graph.yaml", "none", "research_stub", False, "stub only", "no", ""],
        ["rule-based news extraction", "src/nlpcc/stage1_news/models/rule_based_extractor.py", "configs/stage1_news/rule_based.yaml", "test_stage1_news_mvp.py", "production_candidate", True, "used by BL and sector rotation", "yes", ""],
        ["LLM event extraction", "src/nlpcc/stage1_news/models/llm_event_extractor.py", "configs/stage1_news/event_extraction.yaml", "test_stage1_news_mvp.py", "debug_only", False, "optional injected callable only", "no, not as implemented default", ""],
        ["no-LLM fallback", "src/nlpcc/stage1_news/models/no_llm_fallback.py", "configs/stage1_news/rule_based.yaml", "test_stage1_news_mvp.py", "production_candidate", True, "fallback path in Stage 1 and agents", "yes", ""],
        ["generic RAG summariser", "none", "none", "none", "missing", False, "no code", "no", ""],
        ["pure LLM direct allocator", "src/nlpcc/stage4_agent/models/rejected_direct_llm_allocator.py", "none", "none", "rejected", False, "placeholder rejected baseline", "only as rejected", ""],
        ["deep RL / graph RL", "none", "none", "none", "missing", False, "no code", "no", ""],
    ]
    return [
        {
            "method": r[0],
            "code_path": r[1],
            "config_path": r[2],
            "tests": r[3],
            "maturity": r[4],
            "used_full_year": "yes" if r[5] else "no",
            "performance_evidence": r[6],
            "claim_allowed": r[7],
            "notes": r[8],
        }
        for r in rows
    ]


def docs_claim_rows() -> list[dict[str, Any]]:
    return [
        {
            "document": "README.md",
            "claim": "Official-facing submitted wrapper is NLPCC_tasks/agent_platform/agents/build_agent.py.",
            "evidence": "Path is missing in the root repository and prompt12 package.",
            "risk": "high",
            "edit": "State that the wrapper is pending until Prompt14, or add it before submission.",
        },
        {
            "document": "README.md / docs/REPO_STRUCTURE.md",
            "claim": "Each major stage has pipeline orchestration and production modules.",
            "evidence": "Several files are placeholders, including system_runner.py, official_adapter.py, order_planner.py, and stage4 pipeline.py.",
            "risk": "high",
            "edit": "Mark target-only files as placeholders or complete them before final reporting.",
        },
        {
            "document": "METHODOLOGY.md / docs/strategy/METHODOLOGY.md",
            "claim": "LLM event extraction is a Stage 1 structured extraction method.",
            "evidence": "Default Stage 1 path is deterministic rule-based; LLM extractor only accepts an injected offline callable.",
            "risk": "medium",
            "edit": "Say rule-based extraction is implemented; LLM extraction is optional/stubbed.",
        },
        {
            "document": "METHODOLOGY.md",
            "claim": "OCO / online mirror descent ensemble is a core fallback/meta-allocator.",
            "evidence": "Code performs one-step deterministic expert gating from prior weights and validation penalties; no persisted online weight update/regret state.",
            "risk": "high",
            "edit": "Rename claims to OCO-inspired deterministic gating unless persistence is implemented.",
        },
        {
            "document": "docs/strategy/nlpcc2026_task4_strategy_synthesis.md",
            "claim": "KG-MoE-Lite and causal systems are strong report candidates.",
            "evidence": "KG-MoE-Lite is deterministic sleeve mixing; causal and learning-to-rank agents are placeholders.",
            "risk": "medium",
            "edit": "Limit claims to documented/deferred or lightweight prototype status.",
        },
        {
            "document": "docs/architecture/OFFICIAL_COMPATIBILITY.md",
            "claim": "Official trade adapter validates cash feasibility and server schema.",
            "evidence": "src/nlpcc/execution/official_adapter.py and order_planner.py are placeholders.",
            "risk": "high",
            "edit": "Move this from implemented compatibility to required next fix.",
        },
        {
            "document": "docs/strategy/B_LIST_HARDENING.md",
            "claim": "Final checklist includes official compatibility, fallback, packaging.",
            "evidence": "Package exists but lacks official wrapper; official/local parity fails in prompt13.",
            "risk": "high",
            "edit": "Add current status and blockers before system-report use.",
        },
        {
            "document": "outputs/reports/prompt12/final_run_summary.md",
            "claim": "Full-year candidate local results are final-run artifacts.",
            "evidence": "Results are local-only; official/local parity beyond smoke was explicitly caveated and prompt13 parity fails.",
            "risk": "medium",
            "edit": "Keep local-only language and do not imply official leaderboard parity.",
        },
    ]


def package_rows() -> list[dict[str, Any]]:
    root = REPO_ROOT / "outputs" / "submissions"
    zips = sorted(root.glob("*.zip"), key=lambda path: path.stat().st_mtime if path.exists() else 0, reverse=True)
    dirs = sorted([p for p in root.iterdir() if p.is_dir()], key=lambda path: path.stat().st_mtime, reverse=True) if root.exists() else []
    latest_zip = zips[0] if zips else None
    latest_dir = dirs[0] if dirs else None
    names: list[str] = []
    if latest_zip:
        with zipfile.ZipFile(latest_zip, "r") as archive:
            names = archive.namelist()
    rows = []
    def has_name(prefix: str) -> bool:
        return any(name == prefix or name.startswith(prefix.rstrip("/") + "/") for name in names)
    rows.append({"item": "package exists", "status": "ok" if latest_zip else "missing", "evidence": rel(latest_zip) if latest_zip else "", "notes": ""})
    rows.append({"item": "manifest exists", "status": "ok" if latest_dir and (latest_dir / "SUBMISSION_MANIFEST.json").exists() else "missing", "evidence": rel(latest_dir / "SUBMISSION_MANIFEST.json") if latest_dir else "", "notes": ""})
    rows.append({"item": "no raw official data included", "status": "ok" if latest_zip and not any(name.startswith("data/") or name.startswith("NLPCC_tasks/dataset/") for name in names) else "fail", "evidence": "zip entry scan", "notes": ""})
    rows.append({"item": "no cache data included", "status": "ok" if latest_zip and not any("outputs/cache" in name or ".pytest_cache" in name for name in names) else "fail", "evidence": "zip entry scan", "notes": ""})
    rows.append({"item": "no __pycache__", "status": "ok" if latest_zip and not any("__pycache__" in Path(name).parts for name in names) else "fail", "evidence": "zip entry scan", "notes": ""})
    rows.append({"item": "no .pyc", "status": "ok" if latest_zip and not any(name.endswith(".pyc") for name in names) else "fail", "evidence": "zip entry scan", "notes": ""})
    rows.append({"item": "no notebooks required", "status": "ok" if latest_zip and not any(name.endswith(".ipynb") for name in names) else "fail", "evidence": "zip entry scan", "notes": "No notebooks included."})
    rows.append({"item": "requirements included", "status": "ok" if has_name("requirements.txt") else "missing", "evidence": "requirements.txt" if has_name("requirements.txt") else "", "notes": "No lock file beyond requirements.txt."})
    rows.append({"item": "Dockerfile or equivalent", "status": "missing" if not has_name("Dockerfile") else "ok", "evidence": "zip entry scan", "notes": "No Dockerfile included."})
    rows.append({"item": "configs included", "status": "ok" if has_name("configs") else "missing", "evidence": "configs/" if has_name("configs") else "", "notes": ""})
    rows.append({"item": "official-facing agent included", "status": "missing" if not has_name("NLPCC_tasks/agent_platform/agents/build_agent.py") else "ok", "evidence": "zip entry scan", "notes": "Critical blocker."})
    rows.append({"item": "src/nlpcc included", "status": "ok" if has_name("src/nlpcc") else "missing", "evidence": "src/nlpcc/" if has_name("src/nlpcc") else "", "notes": ""})
    rows.append({"item": "tests or minimal smoke script included", "status": "partial" if has_name("scripts/run_local_smoke.py") else "missing", "evidence": "scripts/run_local_smoke.py" if has_name("scripts/run_local_smoke.py") else "", "notes": "tests/ are not included; smoke scripts are included."})
    return rows


def wrapper_rows() -> list[dict[str, Any]]:
    raw_rows = [
        ["official-facing wrapper path", "NLPCC_tasks/agent_platform/agents/build_agent.py exists", "missing", "fail", "Root wrapper is absent."],
        ["import path into src/nlpcc", "Wrapper imports reusable implementation", "not present", "fail", "Cannot verify without wrapper."],
        ["config loading path", "Wrapper loads frozen configs from configs/", "configs exist; no wrapper loader", "fail", ""],
        ["default strategy selected", "Primary Track 1 robust BL or safe fallback", "not selected in wrapper", "fail", ""],
        ["fallback strategy selected", "S1 or conservative/OCO fallback", "fallback agents exist in src/nlpcc", "partial", "Not wired to official wrapper."],
        ["trade output schema", "official buy amount / sell percentage", "agents emit schema-like trades; execution adapter placeholder", "partial", "No official adapter layer."],
        ["dependency guard", "No unavailable API by default", "dependency_guard.py exists; no wrapper integration", "partial", ""],
        ["decision trace / logging path", "bounded decision trace", "decision_trace.py exists; no wrapper integration", "partial", ""],
        ["crash fallback behavior", "exceptions fall back to S1/conservative", "model-level fallbacks exist; wrapper missing", "partial", ""],
        ["hidden field safety", "does not read current close/high/low/return", "local agents report current_day_fields_used=['open']", "partial", "Official status adapter gap remains."],
        ["official server smoke", "candidate wrapper can run with server", "server smoke script ok, but not candidate wrapper", "partial", "Smoke used SmokeOneUnitAgent, not build_agent.py."],
    ]
    return [{"check": r[0], "expected": r[1], "found": r[2], "status": r[3], "notes": r[4]} for r in raw_rows]


def add_beats_s1(rows: list[dict[str, Any]]) -> None:
    by_track = {}
    for row in rows:
        if row["run"] == "s1_macro":
            by_track["macro"] = row.get("sharpe")
        if row["run"] == "s1_sector":
            by_track["sector"] = row.get("sharpe")
    for row in rows:
        baseline = by_track.get(row["track"])
        row["beats_s1"] = "n/a" if row["run"].startswith("s1_") else ("yes" if row.get("sharpe") is not None and baseline is not None and row["sharpe"] > baseline else "no")


def ranking_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    valid = [row for row in rows if row.get("status") == "ok" and row.get("sharpe") is not None]
    valid.sort(key=lambda row: (float(row["sharpe"]), float(row.get("cum_return") or 0.0)), reverse=True)
    out = []
    for idx, row in enumerate(valid, start=1):
        comparison = "vs s1_macro" if row["track"] == "macro" else "vs s1_sector"
        recommendation = "promote" if row.get("beats_s1") == "yes" and row["run"] in {"robust_bl_track1", "oco_fallback_macro", "s1_sector"} else "keep as ablation"
        if row["run"].startswith("s1_"):
            recommendation = "baseline/fallback"
        out.append(
            {
                "rank": idx,
                "run": row["run"],
                "track": row["track"],
                "primary_comparison": comparison,
                "sharpe": row["sharpe"],
                "cum_return": row["cum_return"],
                "max_drawdown": row["max_drawdown"],
                "turnover": row["turnover"],
                "recommendation": recommendation,
            }
        )
    return out


def write_reports(data: dict[str, Any]) -> None:
    full_year = data["full_year"]
    public_a = data["public_a"]
    add_beats_s1(full_year)
    add_beats_s1(public_a)

    inventory = inventory_rows()
    docs_claims = docs_claim_rows()
    packages = package_rows()
    wrapper = wrapper_rows()
    maturity = maturity_rows(full_year)
    trace_rows, component_rows = data["stage1_trace"], data["stage1_components"]

    parity_headers = ["Strategy", "Track", "Date Range", "Local Final Value", "Official Final Value", "Abs Diff", "Rel Diff", "Metric Match?", "Trade Match?", "Status", "Notes"]
    parity_md = [
        "# Prompt13 Official / Local Parity Report",
        "",
        "This report uses a short deterministic 2024 range and does not assume parity from local results.",
        "",
        md_table(
            parity_headers,
            [
                [
                    r["strategy"],
                    r["track"],
                    r["date_range"],
                    r["local_final_value"],
                    r["official_final_value"],
                    r["abs_diff"],
                    r["rel_diff"],
                    r["metric_match"],
                    r["trade_match"],
                    r["status"],
                    r["notes"],
                ]
                for r in data["parity"]
            ],
        ),
        "",
        "Rerun command: `python scripts/run_prompt13_audit.py --base-url http://localhost:6207`.",
    ]
    write_text(REPORT_DIR / "official_local_parity_report.md", "\n".join(parity_md) + "\n")

    trace_md = [
        "# Prompt13 Stage 1 Trace Report",
        "",
        "Stage 1 is deterministic and rule-based by default. No default LLM extraction was observed.",
        "",
        md_table(
            ["Date", "News Count", "Stage 1 Method", "Extracted Signals", "Stage 2 State", "Allocation Impact", "Trace Complete?", "Notes"],
            [[r["date"], r["news_count"], r["stage1_method"], r["extracted_signals"], r["stage2_state"], r["allocation_impact"], r["trace_complete"], r["notes"]] for r in trace_rows],
        ),
        "",
        md_table(
            ["Stage 1 Component", "Path", "Implemented?", "Used in Current Candidate?", "Reproducible?", "Notes"],
            [[r["component"], r["path"], r["implemented"], r["used"], r["reproducible"], r["notes"]] for r in component_rows],
        ),
    ]
    write_text(REPORT_DIR / "stage1_trace_report.md", "\n".join(trace_md) + "\n")

    maturity_md = [
        "# Prompt13 Module Maturity Matrix",
        "",
        md_table(
            ["Method", "Code Path", "Config Path", "Tests", "Current Maturity", "Used in Full-Year Run?", "Performance Evidence", "Report Claim Allowed?", "Notes"],
            [[r["method"], r["code_path"], r["config_path"], r["tests"], r["maturity"], r["used_full_year"], r["performance_evidence"], r["claim_allowed"], r["notes"]] for r in maturity],
        ),
    ]
    write_text(REPORT_DIR / "module_maturity_matrix.md", "\n".join(maturity_md) + "\n")

    full_year_md = [
        "# Prompt13 Full-Year 2024 Ablation Report",
        "",
        md_table(
            ["Run", "Track", "Date Range", "Final Value", "Cum Return", "Sharpe", "Max Drawdown", "Turnover", "Beats S1?", "Status", "Notes"],
            [[r["run"], r["track"], r["date_range"], r["final_value"], r["cum_return"], r["sharpe"], r["max_drawdown"], r["turnover"], r["beats_s1"], r["status"], r["notes"]] for r in full_year],
        ),
        "",
        "## Ranking",
        "",
        md_table(
            ["Rank", "Run", "Track", "Primary Comparison", "Sharpe", "Cum Return", "Max Drawdown", "Turnover", "Recommendation"],
            [[r["rank"], r["run"], r["track"], r["primary_comparison"], r["sharpe"], r["cum_return"], r["max_drawdown"], r["turnover"], r["recommendation"]] for r in ranking_rows(full_year)],
        ),
    ]
    write_text(REPORT_DIR / "full_year_ablation_report.md", "\n".join(full_year_md) + "\n")

    public_md = [
        "# Prompt13 Public A 2025 Evaluation Report",
        "",
        "2025 tuning policy:",
        "  No parameter changes were made based on these results during this audit.",
        "",
        md_table(
            ["Run", "Track", "Date Range", "Final Value", "Cum Return", "Sharpe", "Max Drawdown", "Turnover", "Beats S1?", "Promote?", "Notes"],
            [
                [
                    r["run"],
                    r["track"],
                    r["date_range"],
                    r["final_value"],
                    r["cum_return"],
                    r["sharpe"],
                    r["max_drawdown"],
                    r["turnover"],
                    r["beats_s1"],
                    "yes" if r["run"] == "robust_bl_track1" and r["beats_s1"] == "yes" else ("fallback" if r["run"].startswith("s1_") else "no"),
                    r["notes"],
                ]
                for r in public_a
            ],
        ),
    ]
    write_text(REPORT_DIR / "public_a_2025_evaluation_report.md", "\n".join(public_md) + "\n")

    wrapper_md = [
        "# Prompt13 Submission Wrapper Audit",
        "",
        md_table(
            ["Check", "Expected", "Found", "Status", "Notes"],
            [[r["check"], r["expected"], r["found"], r["status"], r["notes"]] for r in wrapper],
        ),
    ]
    write_text(REPORT_DIR / "submission_wrapper_audit.md", "\n".join(wrapper_md) + "\n")

    verdict = "Not ready"
    track1 = next((r for r in public_a if r["run"] == "robust_bl_track1"), None)
    track2 = next((r for r in public_a if r["run"] == "s1_sector"), None)
    final_md = [
        "# Prompt13 Final Recommendation",
        "",
        "## 1. Submission Readiness Verdict",
        "",
        verdict,
        "",
        "## 2. Primary Track 1 Candidate",
        "",
        "robust_bl_track1, because it is the strongest local Track 1 candidate in the current evidence. It remains local-only until the official wrapper and parity gaps are fixed.",
        "",
        "## 3. Primary Track 2 Candidate",
        "",
        "s1_sector, because sector_rotation_track2 does not yet beat the S1 sector baseline in the current local evidence.",
        "",
        "## 4. Safe Fallback",
        "",
        "S1 quant core with conservative/OCO-style fallback controls. Do not rely on missing official adapter behavior.",
        "",
        "## 5. Methods to Promote",
        "",
        "- S0/S1 baselines.",
        "- robust_bl_track1 as a Track 1 local candidate.",
        "- risk parity and conservative/OCO-style ensemble as fallback components, with limited claims.",
        "",
        "## 6. Methods to Keep as Ablations",
        "",
        "- sector_rotation_track2.",
        "- KG-MoE-Lite.",
        "- robust BL no-news/no-confidence/no-turnover variants.",
        "- sector no-news/no-graph/momentum-only variants.",
        "",
        "## 7. Methods to Reject or Defer",
        "",
        "- Full KG-MoE, causal/invariant allocator, learning-to-rank, transformer event memory, retrieval memory, HMM/Kalman/MPC, direct LLM allocator, deep RL/graph RL.",
        "",
        "## 8. Required Fixes Before Next Phase",
        "",
        "1. Add the root official-facing build_agent.py wrapper.",
        "2. Implement official_adapter/order_planner/system_runner or remove claims that they exist.",
        "3. Convert official portfolio holdings into the internal share/value schema before agent decisions.",
        "4. Re-run official/local parity for S0, S1, and robust BL over 10-30 trading days.",
        "5. Rebuild the submission package and confirm it includes the official wrapper.",
        "",
        "## 9. Required Evidence Before Final Submission",
        "",
        "1. Passing official/local parity report with daily values, cash, holdings, trades, and costs.",
        "2. Full 2024 and locked 2025 local result pack for promoted systems.",
        "3. Official server smoke using the submitted wrapper, not only SmokeOneUnitAgent.",
        "4. No-API fallback run and dependency audit.",
        "5. Package audit showing no raw data/cache and including all required runtime files.",
        "",
        "## 10. Recommended Next Prompt",
        "",
        "Prompt14 - Submission Wrapper Repair and Official Parity Closure: implement the official-facing wrapper and adapter, then rerun prompt13 parity until S0/S1 match server semantics.",
    ]
    write_text(REPORT_DIR / "final_recommendation.md", "\n".join(final_md) + "\n")

    full_md = [
        "# Prompt13 Full Audit Report",
        "",
        "## Repository Status Inventory",
        "",
        md_table(["Area", "Expected", "Found", "Status", "Notes"], [[r["area"], r["expected"], r["found"], r["status"], r["notes"]] for r in inventory]),
        "",
        "## Documentation and Report Claim Audit",
        "",
        md_table(["Document", "Claim", "Current Evidence", "Risk", "Recommended Edit"], [[r["document"], r["claim"], r["evidence"], r["risk"], r["edit"]] for r in docs_claims]),
        "",
        "## Reproducibility and Package Audit",
        "",
        md_table(["Package Item", "Status", "Evidence", "Notes"], [[r["item"], r["status"], r["evidence"], r["notes"]] for r in packages]),
        "",
        "## High-Level Finding",
        "",
        "The repository has serious local research evidence, but it is not submission-ready because the official wrapper is missing and official/local parity fails or remains unproven for candidate systems.",
    ]
    write_text(REPORT_DIR / "full_audit_report.md", "\n".join(full_md) + "\n")

    structured = {
        "created_at_utc": datetime.now(timezone.utc).isoformat(),
        "verdict": verdict,
        "primary_track1": "robust_bl_track1",
        "primary_track2": "s1_sector",
        "inventory": inventory,
        "official_local_parity": data["parity"],
        "stage1_trace": trace_rows,
        "stage1_components": component_rows,
        "full_year_2024": full_year,
        "public_a_2025": public_a,
        "maturity": maturity,
        "wrapper_audit": wrapper,
        "docs_claim_audit": docs_claims,
        "package_audit": packages,
        "candidate_evidence": {"track1": track1, "track2": track2},
    }
    write_json(REPORT_DIR / "full_audit_report.json", structured)


def main() -> int:
    args = parse_args()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    BACKTEST_DIR.mkdir(parents=True, exist_ok=True)
    data: dict[str, Any] = {}
    data["parity"] = [] if args.skip_official_parity else run_parity(args.base_url, args.parity_start, args.parity_end, skip=args.skip_backtests)
    if args.skip_official_parity:
        data["parity"] = [
            {
                "strategy": spec.name,
                "track": spec.track,
                "date_range": f"{args.parity_start}-{args.parity_end}",
                "local_final_value": None,
                "official_final_value": None,
                "abs_diff": None,
                "rel_diff": None,
                "metric_match": "no",
                "trade_match": "no",
                "status": "not_run",
                "notes": "Skipped by --skip-official-parity.",
            }
            for spec in PARITY_SPECS
        ]
    data["full_year"], _ = run_backtest_set(FULL_YEAR_SPECS, REPO_ROOT / "data" / "train_2024", "full_year_2024", skip=args.skip_backtests)
    data["public_a"], _ = run_backtest_set(PUBLIC_A_SPECS, REPO_ROOT / "data" / "public_a_2025", "public_a_2025", skip=args.skip_backtests)
    data["stage1_trace"], data["stage1_components"] = trace_stage1()
    write_reports(data)
    write_json(REPORT_DIR / "run_summary.json", data)
    print(json.dumps({"status": "ok", "report_dir": rel(REPORT_DIR)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
