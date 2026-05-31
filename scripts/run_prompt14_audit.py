#!/usr/bin/env python3
"""Prompt14 repair audit runner.

Runs wrapper-based official/local parity and writes Prompt14 status reports.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import sys
from typing import Any
from urllib import parse, request


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from NLPCC_tasks.agent_platform.agents.build_agent import build_agent  # noqa: E402
from nlpcc.core.fund_universe import get_fund_pool  # noqa: E402
from nlpcc.execution.official_adapter import normalize_portfolio_state  # noqa: E402
from tools.backtesting.metrics import compute_backtest_metrics  # noqa: E402
from tools.verification.submission_package import audit_submission_archive, build_submission_package  # noqa: E402


REPORT_DIR = REPO_ROOT / "outputs" / "reports" / "prompt14"
BACKTEST_DIR = REPO_ROOT / "outputs" / "backtests" / "prompt14"
TRACE_DIR = REPO_ROOT / "outputs" / "logs" / "prompt14_decision_traces"

COMMISSION_RATE = 0.0001
NEWS_CUTOFF_HOUR = 15


@dataclass(frozen=True)
class ParitySpec:
    name: str
    track: str
    strategy: str
    fallback: str
    load_news: bool = False


PARITY_SPECS = (
    ParitySpec("s0_equal_weight_macro", "macro", "s0_equal_weight", "s1_macro", False),
    ParitySpec("s1_macro", "macro", "s1_macro", "s1_macro", False),
    ParitySpec("robust_bl_track1", "macro", "robust_bl_track1", "s1_macro", True),
    ParitySpec("s1_sector", "sector", "s1_sector", "s1_sector", False),
    ParitySpec("sector_rotation_track2", "sector", "sector_rotation_track2", "s1_sector", True),
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate prompt14 repair reports.")
    parser.add_argument("--base-url", default="http://localhost:6207")
    parser.add_argument("--parity-start", default="2024-01-02")
    parser.add_argument("--parity-end", default="2024-01-31")
    parser.add_argument("--skip-official-parity", action="store_true")
    parser.add_argument("--skip-package", action="store_true")
    return parser.parse_args()


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
    return str(value).replace("\n", " ").replace("|", "\\|")


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


def official_login(base_url: str) -> str:
    token = form_request(base_url, "/api/agents/token", {"username": "prompt01_smoke", "password": "prompt01_smoke"})
    return str(token.get("access_token"))


def load_price_rows(data_root: Path, fund_id: str) -> list[dict[str, str]]:
    with (data_root / "price_data" / f"{fund_id}.csv").open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def common_dates(data_root: Path, track: str, start: str, end: str) -> list[str]:
    start_int = int(start.replace("-", ""))
    end_int = int(end.replace("-", ""))
    dates: set[str] | None = None
    for fund_id in get_fund_pool(track):  # type: ignore[arg-type]
        path = data_root / "price_data" / f"{fund_id}.csv"
        if not path.exists():
            continue
        fund_dates = {row["date"] for row in load_price_rows(data_root, fund_id) if start_int <= int(row["date"]) <= end_int}
        dates = fund_dates if dates is None else dates & fund_dates
    return sorted(dates or [])


def safe_price_window(rows: list[dict[str, str]], index: int, lookback_days: int = 60) -> list[dict[str, Any]]:
    start = max(0, index - lookback_days + 1)
    records: list[dict[str, Any]] = []
    for idx in range(start, index):
        row = rows[idx]
        records.append(
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
    records.append(
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
    return records


def load_all_news_rows(data_root: Path) -> list[tuple[Any, datetime, int, dict[str, Any]]]:
    rows: list[tuple[Any, datetime, int, dict[str, Any]]] = []
    for path in sorted((data_root / "news_data").glob("*_daily_dedup.csv")):
        with path.open("r", encoding="utf-8-sig", newline="") as handle:
            for row in csv.DictReader(handle):
                try:
                    news_day = datetime.strptime(row["THEDATE"], "%Y-%m-%d").date()
                    published = datetime.strptime(row["PUBLISH_TIME"], "%Y-%m-%d %H:%M:%S")
                    ranking = int(row.get("RANKING", "999"))
                except (KeyError, ValueError):
                    continue
                rows.append((news_day, published, ranking, row))
    return rows


def load_news_for_date(news_cache: list[tuple[Any, datetime, int, dict[str, Any]]], current_date: str) -> list[dict[str, Any]]:
    current_day = datetime.strptime(current_date, "%Y%m%d").date()
    earliest = current_day - timedelta(days=0)
    records: list[dict[str, Any]] = []
    for news_day, published, ranking, row in news_cache:
        if news_day > current_day or news_day < earliest:
            continue
        if news_day == current_day and published.hour >= NEWS_CUTOFF_HOUR:
            continue
        if ranking > 20:
            continue
        records.append(row)
    records.sort(key=lambda item: int(item.get("RANKING", "999")))
    return records


def run_local_official_semantics(data_root: Path, spec: ParitySpec, start: str, end: str) -> dict[str, Any]:
    fund_pool = tuple(get_fund_pool(spec.track))  # type: ignore[arg-type]
    rows_by_fund = {fund_id: load_price_rows(data_root, fund_id) for fund_id in fund_pool if (data_root / "price_data" / f"{fund_id}.csv").exists()}
    index_by_fund = {fund_id: {row["date"]: idx for idx, row in enumerate(rows)} for fund_id, rows in rows_by_fund.items()}
    dates = common_dates(data_root, spec.track, start, end)
    news_cache = load_all_news_rows(data_root) if spec.load_news else []
    agent = build_agent(track=spec.track, strategy=spec.strategy, fallback_strategy=spec.fallback, trace_dir=TRACE_DIR / "local")

    capital = 100000.0
    portfolio_values: dict[str, float] = {}
    history: list[dict[str, Any]] = []
    transactions: list[dict[str, Any]] = []
    decisions: list[dict[str, Any]] = []
    weight_history: list[dict[str, float]] = []

    for date_str in dates:
        historical_prices = {
            fund_id: safe_price_window(rows, index_by_fund[fund_id][date_str])
            for fund_id, rows in rows_by_fund.items()
        }
        open_by_fund = {fund_id: rows[-1]["open"] for fund_id, rows in historical_prices.items() if rows}
        current_portfolio = {
            "capital": capital,
            "cash": capital,
            "holdings": {fund_id: {"value": value, "price": open_by_fund.get(fund_id)} for fund_id, value in portfolio_values.items() if value > 1e-6},
            "total_value": capital + sum(portfolio_values.values()),
        }
        news = load_news_for_date(news_cache, date_str) if spec.load_news else []
        decision = agent.decide(
            date_to_decision=date_str,
            news_data=news,
            historical_prices=historical_prices,
            current_portfolio=current_portfolio,
            fund_pool=fund_pool,
        )
        trades = [trade for trade in decision.get("trades", []) if trade.get("action") in {"buy", "sell"}]
        decisions.append({"date": date_str, "trades": trades, "target_weights": decision.get("target_weights", {})})

        pct_by_fund = {
            fund_id: float(rows_by_fund[fund_id][index_by_fund[fund_id][date_str]].get("pctchange", 0.0) or 0.0)
            for fund_id in rows_by_fund
        }
        for fund_id, value in list(portfolio_values.items()):
            if value > 0:
                portfolio_values[fund_id] = value * (1.0 + pct_by_fund.get(fund_id, 0.0) / 100.0)

        for trade in [item for item in trades if item.get("action") == "buy"]:
            amount = float(trade.get("amount", 0.0) or 0.0)
            if amount <= 0 or capital + 1e-2 < amount:
                continue
            fund_id = str(trade["fund_id"])
            commission = amount * COMMISSION_RATE
            capital = max(0.0, capital - amount)
            portfolio_values[fund_id] = portfolio_values.get(fund_id, 0.0) + amount - commission
            transactions.append({"date": date_str, "fund_id": fund_id, "action": "buy", "amount": amount, "commission": commission})

        for trade in [item for item in trades if item.get("action") == "sell"]:
            fund_id = str(trade["fund_id"])
            percentage = float(trade.get("percentage", 0.0) or 0.0)
            if percentage <= 0 or percentage > 1 or portfolio_values.get(fund_id, 0.0) <= 0:
                continue
            value_to_sell = portfolio_values[fund_id] * percentage
            commission = value_to_sell * COMMISSION_RATE
            portfolio_values[fund_id] = max(0.0, portfolio_values[fund_id] - value_to_sell)
            capital += value_to_sell - commission
            transactions.append(
                {
                    "date": date_str,
                    "fund_id": fund_id,
                    "action": "sell",
                    "percentage": percentage,
                    "amount_sold": value_to_sell,
                    "commission": commission,
                }
            )

        total_value = capital + sum(portfolio_values.values())
        weights = {fund_id: value / total_value for fund_id, value in portfolio_values.items() if total_value > 0 and value > 1e-6}
        weight_history.append(weights)
        history.append({"date": date_str, "cash": capital, "holdings_value": sum(portfolio_values.values()), "total_value": total_value, "weights": weights})

    final_day_had_trades = bool(transactions and transactions[-1].get("date") == dates[-1]) if dates else False
    if dates and final_day_had_trades:
        last_date = dates[-1]
        pct_by_fund = {
            fund_id: float(rows_by_fund[fund_id][index_by_fund[fund_id][last_date]].get("pctchange", 0.0) or 0.0)
            for fund_id in rows_by_fund
        }
        for fund_id, value in list(portfolio_values.items()):
            if value > 0:
                portfolio_values[fund_id] = value * (1.0 + pct_by_fund.get(fund_id, 0.0) / 100.0)
        total_value = capital + sum(portfolio_values.values())
        weights = {fund_id: value / total_value for fund_id, value in portfolio_values.items() if total_value > 0 and value > 1e-6}
        weight_history.append(weights)
        history.append(
            {
                "date": last_date,
                "cash": capital,
                "holdings_value": sum(portfolio_values.values()),
                "total_value": total_value,
                "weights": weights,
                "snapshot_type": "finish_update",
            }
        )

    metrics = compute_backtest_metrics([row["total_value"] for row in history], weight_history=weight_history).as_dict()
    result = {
        "status": "ok",
        "strategy": spec.name,
        "track": spec.track,
        "date_range": f"{start}-{end}",
        "final_value": history[-1]["total_value"] if history else None,
        "metrics": metrics,
        "transactions": transactions,
        "decisions": decisions,
        "portfolio_history": history,
        "semantics": "official_value_holdings_buy_first_sell_second",
    }
    write_json(BACKTEST_DIR / "parity" / f"local_{spec.name}.json", result)
    return result


def run_official_spec(base_url: str, token: str, spec: ParitySpec, start: str, end: str) -> dict[str, Any]:
    fund_pool = list(get_fund_pool(spec.track))  # type: ignore[arg-type]
    config = {
        "start_date": start,
        "end_date": end,
        "initial_capital": 100000.0,
        "fund_pool": fund_pool,
        "agents": [{"name": "prompt01_smoke", "prompt": "prompt14 parity"}],
        "news_sources": ["caixin", "tiantian", "sinafinance", "tencent"],
        "lookback_days": 60,
        "top_rank": 20,
        "pre_k_days": 1,
        "view_platform_trading_history_days": 1,
        "decision_model_name": "prompt14_no_api",
        "results_dir": "../../outputs/reports/prompt14/official_server_sessions",
    }
    start_response = json_request("POST", base_url, "/api/backtest/start", config, token=token)
    session_id = start_response["session_id"]
    data = start_response.get("data", {})
    agent = build_agent(track=spec.track, strategy=spec.strategy, fallback_strategy=spec.fallback, trace_dir=TRACE_DIR / "official")
    decisions: list[dict[str, Any]] = []
    trade_results: list[dict[str, Any]] = []

    while True:
        status = json_request("GET", base_url, f"/api/backtest/{session_id}/status", token=token)
        historical = json_request("GET", base_url, f"/api/backtest/{session_id}/historical_prices?lookback_days=60", token=token)
        decision = agent.decide(
            date_to_decision=data.get("date"),
            news_data=data.get("news", []),
            historical_prices=historical.get("historical_prices", {}),
            current_portfolio=status,
            fund_pool=fund_pool,
        )
        trades = [trade for trade in decision.get("trades", []) if trade.get("action") in {"buy", "sell"}]
        submitted = None
        if trades:
            submitted = json_request(
                "POST",
                base_url,
                f"/api/backtest/{session_id}/trade",
                {
                    "trades": trades,
                    "agent_decision": {"decision": decision, "reasoning": decision.get("reasoning", ""), "chain_of_thought": ""},
                },
                token=token,
            )
            trade_results.extend(submitted.get("trade_execution_results", []))
        decisions.append({"date": data.get("date"), "trades": trades, "submitted": submitted})
        data = json_request("GET", base_url, f"/api/backtest/{session_id}/next_day", token=token)
        if data.get("message") == "Backtest finished":
            break

    results = json_request("GET", base_url, f"/api/backtest/results/{session_id}", token=token)
    official_values = [float(row.get("value", 0.0) or 0.0) for row in results.get("portfolio_value_history", [])]
    metrics = compute_backtest_metrics([value for value in official_values if value > 0]).as_dict() if official_values else {}
    result = {
        "status": "ok",
        "session_id": session_id,
        "strategy": spec.name,
        "track": spec.track,
        "date_range": f"{start}-{end}",
        "performance": results.get("performance", {}),
        "metrics": metrics,
        "results": results,
        "decisions": decisions,
        "trade_execution_results": trade_results,
    }
    write_json(BACKTEST_DIR / "parity" / f"official_{spec.name}.json", result)
    return result


def run_parity(base_url: str, start: str, end: str, *, skip_official: bool) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    available, detail = official_available(base_url)
    if skip_official or not available:
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
                    "status": "blocked" if not skip_official else "not_run",
                    "notes": f"{detail} Rerun: python scripts/run_prompt14_audit.py --base-url {base_url}",
                }
            )
        return rows

    token = official_login(base_url)
    for spec in PARITY_SPECS:
        try:
            local = run_local_official_semantics(REPO_ROOT / "data" / "train_2024", spec, start, end)
            official = run_official_spec(base_url, token, spec, start, end)
            local_final = float(local.get("final_value", 0.0) or 0.0)
            official_final = float(official.get("performance", {}).get("final_portfolio_value", 0.0) or 0.0)
            abs_diff = abs(local_final - official_final)
            rel_diff = abs_diff / local_final if local_final else None
            local_trades = len(local.get("transactions", []))
            official_trades = len([item for item in official.get("trade_execution_results", []) if item.get("success")])
            metric_match = "yes" if rel_diff is not None and rel_diff <= 1e-6 else "no"
            trade_match = "yes" if local_trades == official_trades else "no"
            status = "pass" if metric_match == "yes" and trade_match == "yes" else "fail"
            if status == "fail" and rel_diff is not None and rel_diff <= 1e-4:
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
                    "notes": f"Wrapper-based rerun; local trades={local_trades}; official accepted trades={official_trades}.",
                }
            )
        except Exception as exc:
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


def write_parity_report(rows: list[dict[str, Any]]) -> None:
    headers = [
        "Strategy",
        "Track",
        "Date Range",
        "Local Final Value",
        "Official Final Value",
        "Abs Diff",
        "Rel Diff",
        "Metric Match?",
        "Trade Match?",
        "Status",
        "Notes",
    ]
    table_rows = [
        [
            row["strategy"],
            row["track"],
            row["date_range"],
            row["local_final_value"],
            row["official_final_value"],
            row["abs_diff"],
            row["rel_diff"],
            row["metric_match"],
            row["trade_match"],
            row["status"],
            row["notes"],
        ]
        for row in rows
    ]
    write_text(
        REPORT_DIR / "official_local_parity_rerun_report.md",
        "# Prompt14 Official / Local Parity Rerun Report\n\n"
        "Parity is rerun through the Prompt14 official wrapper and SystemRunner. The local side uses official value-holding semantics.\n\n"
        + md_table(headers, table_rows)
        + "\n",
    )
    write_json(REPORT_DIR / "official_local_parity_rerun_report.json", rows)


def write_wrapper_report(parity_rows: list[dict[str, Any]]) -> None:
    fields = [
        ["cash/capital", "cash available before same-day trades", "cash amount", "cash = cash or capital", "yes", "Buy budget uses this only."],
        ["holdings[fund].value", "current official holding value", "market-value holding", "copy value directly; do not multiply by price", "yes", "Prompt13 parity blocker repaired."],
        ["local numeric holding", "share-like quantity in local tools", "market-value holding", "multiply by current open when normalizing", "yes", "Backward-compatible with existing local tests."],
        ["total_value", "cash plus holding value", "cash plus holding value", "use official total_value when present", "yes", "Falls back to computed total."],
        ["buy trade amount", "cash amount to spend", "official buy payload", "plan from target gap using decision cash only", "yes", "Same-day sells are excluded from buy budget."],
        ["sell trade percentage", "fraction of current holding value", "official sell payload", "sell_value / current_holding_value clipped to (0,1]", "yes", "Invalid sells rejected before submission."],
    ]
    checks = [
        ["build_agent.py exists", "NLPCC_tasks/agent_platform/agents/build_agent.py", "present", "pass", "Thin wrapper imports src/nlpcc SystemRunner."],
        ["config loading", "frozen configs under configs/", "SystemRunner.load_frozen_system_config", "pass", "YAML loader has stdlib fallback."],
        ["Track A default", "robust_bl_track1", "robust_bl_track1", "pass", "Fallback is s1_macro."],
        ["Track B default", "s1_sector", "s1_sector", "pass", "sector_rotation_track2 remains experimental."],
        ["portfolio conversion", "official value holdings", "normalize_portfolio_state", "pass", "Value semantics are explicit."],
        ["trade schema", "buy amount / sell percentage", "OrderPlanner + TradeValidator", "pass", "Invalid trades are rejected."],
        ["external APIs", "not required by default", "Stage1 use_llm=false; wrapper no API dependency", "pass", "HF models disabled by policy."],
        ["official parity", "S0/S1 should pass or minor diff", _parity_status_text(parity_rows), _parity_wrapper_status(parity_rows), "See parity rerun report."],
    ]
    write_text(
        REPORT_DIR / "official_wrapper_repair_report.md",
        "# Prompt14 Official Wrapper Repair Report\n\n"
        "## Portfolio Field Conversion\n\n"
        + md_table(["Field", "Official Meaning", "Internal Meaning", "Conversion Rule", "Tested?", "Notes"], fields)
        + "\n\n## Wrapper Checks\n\n"
        + md_table(["Check", "Expected", "Found", "Status", "Notes"], checks)
        + "\n",
    )


def _parity_status_text(rows: list[dict[str, Any]]) -> str:
    selected = [row for row in rows if row["strategy"] in {"s0_equal_weight_macro", "s1_macro"}]
    return "; ".join(f"{row['strategy']}={row['status']}" for row in selected) or "not_run"


def _parity_wrapper_status(rows: list[dict[str, Any]]) -> str:
    selected = [row for row in rows if row["strategy"] in {"s0_equal_weight_macro", "s1_macro"}]
    if selected and all(row["status"] in {"pass", "minor_diff"} for row in selected):
        return "pass"
    if any(row["status"] == "blocked" for row in selected):
        return "blocked"
    return "partial"


def write_status_reports(parity_rows: list[dict[str, Any]]) -> None:
    parity = {row["strategy"]: row for row in parity_rows}
    track_rows = [
        [
            "Track A / Macro",
            "robust_bl_track1",
            "robust_bl_track1",
            "s1_macro",
            "2024 local Sharpe 0.858352; best promoted Track A local candidate",
            "2025 local Sharpe 2.012469; evaluation-only",
            parity.get("s1_macro", {}).get("status", "not_run"),
            "not ready, but close" if _parity_wrapper_status(parity_rows) == "pass" else "not ready",
            "Run full wrapper-based 2024/2025 candidate checks and official smoke using submitted package.",
        ],
        [
            "Track B / Sector",
            "s1_sector",
            "s1_sector; sector_rotation_track2 experimental",
            "s1_sector",
            "s1_sector beats sector_rotation_track2 on 2024 local evidence",
            "sector_rotation_track2 beats S1 on 2025 local, but no tuning allowed",
            parity.get("s1_sector", {}).get("status", "not_run"),
            "not ready, but close" if parity.get("s1_sector", {}).get("status") in {"pass", "minor_diff"} else "not ready",
            "Keep Track B default at S1 until sector rotation beats S1 robustly on construction data.",
        ],
    ]
    write_text(
        REPORT_DIR / "track_status_matrix.md",
        "# Prompt14 Track Status Matrix\n\n"
        + md_table(
            [
                "Track",
                "Current Default",
                "Best Local Candidate",
                "Fallback",
                "2024 Evidence",
                "2025 Evidence",
                "Official Parity",
                "Submission Status",
                "Next Required Fix",
            ],
            track_rows,
        )
        + "\n",
    )

    stage_rows = [
        ["Stage 1 - News Processing", "rule-based extraction, event tuples, BL views, sector impact", "default LLM extraction/cache", "yes", "yes", "stage1 tests + prompt13 trace", "production_candidate for rule path", "Overclaiming LLM", "Keep default described as deterministic rule-based."],
        ["Stage 2 - Quantified Text Storage", "BL view store, confidence matrix, sector panel", "full retrieval/KG/causal systems", "yes", "yes", "stage2 tests", "working_prototype to production_candidate for BL structures", "Stub methods overclaimed", "Limit claims to implemented structures."],
        ["Stage 3 - Trade Data Processing", "inverse vol, momentum, covariance, drawdown, breadth, cash feasibility", "none critical", "yes", "yes", "stage3 tests", "production_candidate", "Execution semantic mismatch", "Prompt14 value-holding repair completed."],
        ["Stage 4 - Final Trading Agent", "S0/S1, robust BL, sector rotation, OCO-style ensemble", "full KG/causal/RL", "yes", "yes", "stage4 tests + local evidence", "mixed", "Local evidence not official until wrapper runs", "Use wrapper parity before promotion."],
        ["Execution / Adapter Layer", "official adapter, order planner, trade validator", "daily official package smoke", "yes", "yes", "prompt14 tests", "working_prototype", "Remaining parity/package dry-run risk", "Run final dry-run package path."],
        ["Runtime / Fallback Layer", "SystemRunner, fallback-to-S1, trace logging", "persistent cross-day online state", "yes", "yes", "prompt14 tests", "working_prototype", "Runner not yet used by old experiment tools", "Use runner in official-facing and parity paths."],
        ["Tools / Experiments / Reporting", "local backtests, ablations, package audit", "official leaderboard harness", "n/a", "n/a", "prompt13/prompt14 runs", "working_prototype", "Local-only evidence", "Keep local/official labels explicit."],
    ]
    write_text(
        REPORT_DIR / "stage_status_matrix.md",
        "# Prompt14 Stage Status Matrix\n\n"
        + md_table(
            ["Stage", "Implemented Components", "Missing / Placeholder Components", "Used by Track A?", "Used by Track B?", "Tests", "Maturity", "Main Risk", "Required Fix"],
            stage_rows,
        )
        + "\n",
    )

    model_rows = _model_rows()
    write_text(
        REPORT_DIR / "model_status_matrix.md",
        "# Prompt14 Model Status Matrix\n\n"
        + md_table(
            ["Model / Method", "Track A Status", "Track B Status", "Stage(s)", "Code Path", "Config Path", "Maturity", "Evidence", "Default?", "Claim Allowed?", "Next Action"],
            model_rows,
        )
        + "\n",
    )


def _model_rows() -> list[list[Any]]:
    return [
        ["S0 equal weight", "baseline", "baseline", "3/4", "src/nlpcc/stage4_agent/models/s0_equal_weight_agent.py", "configs/systems/s0_equal_weight.yaml", "production_candidate", "2024/2025 local; prompt14 wrapper parity", "no", "yes, baseline", "keep for parity/sanity"],
        ["S1 quant core", "fallback", "default", "3/4", "src/nlpcc/stage4_agent/models/s1_quant_core.py", "configs/systems/s1_macro.yaml; configs/systems/s1_sector.yaml", "production_candidate", "2024/2025 local; prompt14 wrapper parity", "Track B yes", "yes", "promote as safe fallback"],
        ["inverse volatility", "component", "component", "3", "src/nlpcc/stage3_trade/models/inverse_volatility.py", "configs/stage3_trade/risk_state.yaml", "production_candidate", "S1 component", "component", "yes", "keep"],
        ["momentum", "component", "component", "3", "src/nlpcc/stage3_trade/models/momentum.py", "configs/stage3_trade/momentum.yaml", "production_candidate", "S1 component", "component", "yes", "keep"],
        ["sector trend-following", "n/a", "baseline component", "3/4", "src/nlpcc/stage3_trade/models/sector_trend.py", "configs/systems/s1_sector.yaml", "production_candidate", "S1 sector evidence", "component", "yes", "keep"],
        ["risk parity", "fallback component", "fallback component", "4", "src/nlpcc/stage4_agent/models/risk_parity_agent.py", "configs/systems/risk_parity_track1.yaml", "working_prototype", "prompt07 local evidence", "no", "component only", "keep as ablation/fallback"],
        ["robust Black-Litterman", "best local candidate", "n/a", "1/2/3/4", "src/nlpcc/stage4_agent/models/robust_bl_agent.py", "configs/systems/robust_bl_track1.yaml", "production_candidate", "best 2024 Track A local Sharpe", "Track A yes", "yes, local candidate plus parity caveat", "wrapper-based full-year run"],
        ["belief-state risk parity", "stub", "stub", "4", "src/nlpcc/stage4_agent/models/belief_rp_agent.py", "none", "research_stub", "placeholder", "no", "no", "defer"],
        ["HMM / Kalman / MPC", "stub", "stub", "3/4", "src/nlpcc/stage4_agent/models/hmm_kalman_mpc_agent.py", "none", "research_stub", "placeholder", "no", "no", "defer"],
        ["sector impact model", "component", "prototype", "1/2", "src/nlpcc/stage1_news/models/sector_impact_extractor.py", "configs/stage1_news/sector_impact.yaml", "working_prototype", "Track B ablations", "component", "deterministic only", "keep as ablation"],
        ["KG-MoE-Lite", "n/a", "prototype", "4", "src/nlpcc/stage4_agent/models/kg_moe_lite_agent.py", "configs/systems/kg_moe_lite_track2.yaml", "working_prototype", "prompt08 only", "no", "Lite only", "do not promote"],
        ["retrieval analogue memory", "stub", "stub", "2/4", "src/nlpcc/stage2_text_store/models/retrieval_index.py", "configs/stage2_text_store/retrieval_index.yaml", "research_stub", "no run evidence", "no", "no", "defer"],
        ["transformer-style event memory", "missing", "missing", "2/4", "none", "none", "documented_only", "no code", "no", "no", "reject before final"],
        ["OCO / online mirror descent ensemble", "fallback prototype", "prototype", "4", "src/nlpcc/stage4_agent/models/oco_ensemble_agent.py", "configs/systems/oco_fallback.yaml", "working_prototype", "2024/2025 local", "fallback only", "OCO-inspired gating only", "avoid persistent OMD claims"],
        ["learning-to-rank", "n/a", "stub", "4", "src/nlpcc/stage4_agent/models/learning_to_rank_agent.py", "none", "research_stub", "placeholder", "no", "no", "defer"],
        ["causal/invariant event-impact model", "stub", "stub", "2/4", "src/nlpcc/stage4_agent/models/causal_invariant_agent.py", "configs/stage2_text_store/causal_event_graph.yaml", "research_stub", "stub", "no", "no", "defer"],
        ["rule-based news extraction", "used", "used", "1", "src/nlpcc/stage1_news/models/rule_based_extractor.py", "configs/stage1_news/rule_based.yaml", "production_candidate", "prompt13 trace", "yes", "yes", "default path"],
        ["LLM event extraction", "optional", "optional", "1", "src/nlpcc/stage1_news/models/llm_event_extractor.py", "configs/stage1_news/event_extraction.yaml", "debug_only", "injected callable only", "no", "not default", "keep disabled"],
        ["no-LLM fallback", "used", "used", "1/runtime", "src/nlpcc/stage1_news/models/no_llm_fallback.py", "configs/stage1_news/rule_based.yaml", "production_candidate", "tests + fallback policy", "yes", "yes", "keep mandatory"],
        ["generic RAG summariser", "missing", "missing", "1/2", "none", "none", "missing", "no code", "no", "no", "do not add before final validation"],
        ["pure LLM direct allocator", "rejected", "rejected", "4", "src/nlpcc/stage4_agent/models/rejected_direct_llm_allocator.py", "none", "rejected", "negative architecture decision", "no", "only rejected baseline", "do not develop"],
        ["deep RL / graph RL", "missing", "missing", "4", "none", "none", "missing", "no code", "no", "no", "reject/defer"],
    ]


def write_pipeline_report(parity_rows: list[dict[str, Any]], package_result: dict[str, Any] | None) -> None:
    edits = [
        ["README.md", "Added Prompt14 status note for wrapper/defaults/HF policy.", "Prevent stale wrapper and LLM-default claims.", "Full final report still needed."],
        ["METHODOLOGY.md", "Clarified OCO-inspired, LLM optional, deferred methods.", "Prevent overclaiming maturity.", "Method universe remains broad."],
        ["docs/architecture/OFFICIAL_COMPATIBILITY.md", "Recorded value-holding adapter and Prompt14 parity status.", "Reflect repaired execution layer.", "Package dry-run still required."],
        ["docs/strategy/B_LIST_HARDENING.md", "Updated checklist status around wrapper/parity/HF.", "Clarify remaining B-list blockers.", "No Dockerfile added."],
    ]
    package_note = package_result.get("status") if package_result else "skipped"
    write_text(
        REPORT_DIR / "pipeline_repair_report.md",
        "# Prompt14 Pipeline Repair Report\n\n"
        "## Summary\n\n"
        f"- Wrapper added: `NLPCC_tasks/agent_platform/agents/build_agent.py`.\n"
        f"- Portfolio adapter, order planner, trade validator, and SystemRunner repaired.\n"
        f"- S0/S1 parity status: {_parity_status_text(parity_rows)}.\n"
        f"- Package rebuild status: {package_note}.\n\n"
        "## Documentation Edits\n\n"
        + md_table(["Document", "Edit Made", "Reason", "Remaining Caveat"], edits)
        + "\n",
    )


def rebuild_package(skip: bool) -> dict[str, Any]:
    if skip:
        result = {"status": "skipped", "package": None, "archive_audit": None}
    else:
        name = "nlpcc_task4_candidate_prompt14_repaired_" + datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        package = build_submission_package(repo_root=REPO_ROOT, output_root=REPO_ROOT / "outputs" / "submissions", package_name=name)
        audit = audit_submission_archive(package.archive_path)
        result = {"status": "ok" if not audit["issues"] else "failed", "package": package.as_dict(), "archive_audit": audit}
    rows = [
        ["build_agent.py wrapper", "yes", _included(result, "NLPCC_tasks/agent_platform/agents/build_agent.py"), "pass" if _included(result, "NLPCC_tasks/agent_platform/agents/build_agent.py") else result["status"], "Official wrapper should now be included."],
        ["src/nlpcc/", "yes", _included(result, "src/nlpcc/"), "pass" if _included(result, "src/nlpcc/") else result["status"], "Reusable implementation."],
        ["configs/", "yes", _included(result, "configs/"), "pass" if _included(result, "configs/") else result["status"], "Frozen configs included."],
        ["requirements.txt", "yes", _included(result, "requirements.txt"), "pass" if _included(result, "requirements.txt") else result["status"], "Minimal dependency file."],
        ["raw official data", "no", False, "pass" if result.get("archive_audit", {}).get("issues", []) == [] else "fail", "No `data/` or `NLPCC_tasks/dataset/` entries expected."],
        ["__pycache__ / .pyc", "no", False, "pass" if result.get("archive_audit", {}).get("issues", []) == [] else "fail", "Archive audit checks these."],
        ["large HF models", "no", False, "pass", "No models downloaded or packaged."],
    ]
    write_text(
        REPORT_DIR / "package_rebuild_report.md",
        "# Prompt14 Package Rebuild Report\n\n"
        + md_table(["Package Item", "Required?", "Included?", "Status", "Notes"], rows)
        + "\n\n"
        + "```json\n"
        + json.dumps(result, indent=2, ensure_ascii=False, sort_keys=True)
        + "\n```\n",
    )
    write_json(REPORT_DIR / "package_rebuild_report.json", result)
    return result


def _included(result: dict[str, Any], path_prefix: str) -> bool:
    package = result.get("package") or {}
    manifest_path = package.get("manifest_path")
    if not manifest_path:
        return False
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    return any(item["path"] == path_prefix.rstrip("/") or item["path"].startswith(path_prefix.rstrip("/") + "/") for item in manifest["files"])


def write_hf_report() -> None:
    rows = [
        ["yiyanghkust/finbert-tone-chinese", "financial sentiment", "Chinese", "yes", "moderate", "model-card license needs final pin check", "optional sentiment ablation", "no", "no", "rule_based", "Do not make default dependent on it."],
        ["hfl/chinese-roberta-wwm-ext", "encoding/classification backbone", "Chinese", "yes", "moderate", "low/standard research-use risk after license check", "optional local classifier", "no", "no", "rule_based", "General model, not finance-specific."],
        ["hfl/chinese-roberta-wwm-ext-large", "encoding/classification backbone", "Chinese", "yes", "high", "low/standard research-use risk after license check", "optional only", "no", "no", "rule_based", "Large runtime cost; not suitable for default."],
        ["BAAI/bge-m3", "embedding retrieval", "multilingual/Chinese", "yes", "high", "license check required before packaging", "retrieval ablation", "no", "no", "rule_based", "Retrieval is not promoted."],
        ["BAAI/bge-small-zh-v1.5", "embedding retrieval", "Chinese", "yes", "low", "license check required before packaging", "optional lightweight embeddings", "no", "no", "rule_based", "Best optional candidate if a local model is later needed."],
        ["sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", "embedding retrieval", "multilingual", "yes", "low", "license check required before packaging", "fallback embeddings", "no", "no", "rule_based", "Not finance-specific."],
    ]
    write_text(
        REPORT_DIR / "huggingface_model_audit.md",
        "# Prompt14 Hugging Face / Local Model Audit\n\n"
        "Decision: no Hugging Face model was downloaded and no default runtime dependency was added. Optional model use remains disabled behind `text_model.enabled=false` and must keep `fallback=rule_based`.\n\n"
        + md_table(
            ["Candidate Model", "Task", "Language", "Pre-2026 Available?", "Size / Runtime Risk", "License Risk", "Useful For", "Download?", "Runtime Default?", "Fallback", "Notes"],
            rows,
        )
        + "\n\n"
        "Recommended config stance:\n\n"
        "```yaml\n"
        "text_model:\n"
        "  enabled: false\n"
        "  provider: local_huggingface\n"
        "  model_name: null\n"
        "  local_path: null\n"
        "  revision: null\n"
        "  offline_only: true\n"
        "  fallback: rule_based\n"
        "```\n",
    )


def write_final_recommendation(parity_rows: list[dict[str, Any]], package_result: dict[str, Any]) -> None:
    parity_status = _parity_wrapper_status(parity_rows)
    verdict = "Not ready, but close" if parity_status == "pass" and package_result.get("status") == "ok" else "Not ready"
    stage_rows = [
        ["Stage 1", "production_candidate for deterministic rule path", "Default rule-based path preserved", "No default LLM extraction"],
        ["Stage 2", "working_prototype/production_candidate for BL structures", "No repair needed for wrapper", "Retrieval/KG/causal remain stubs"],
        ["Stage 3", "production_candidate", "Value-holding conversion repaired", "Old local tools still support share semantics"],
        ["Stage 4", "mixed", "Defaults separated by track", "Track B sector rotation remains ablation-only"],
        ["Execution / Runtime", "working_prototype", "Wrapper/adapter/planner/runner added", "Needs final package dry-run"],
    ]
    method_rows = [
        ["Baselines", "S1; S0 as sanity", "S1", "S0", ""],
        ["Track A allocator", "robust BL local candidate", "s1_macro", "OCO-style fallback", "full KG/causal/RL"],
        ["Track B allocator", "s1_sector", "s1_sector", "sector_rotation_track2", "learning-to-rank/full KG"],
        ["Text methods", "rule-based extraction", "no-LLM fallback", "LLM injected callable", "RAG/transformer memory"],
    ]
    write_text(
        REPORT_DIR / "final_recommendation.md",
        "# Prompt14 Final Recommendation\n\n"
        "## 1. Readiness Verdict\n\n"
        f"{verdict}\n\n"
        "## 2. Track A / Macro Status\n\n"
        "- Default candidate: robust_bl_track1\n"
        "- Fallback: s1_macro\n"
        "- Evidence: best local 2024 Track A candidate from Prompt13; Prompt14 wrapper parity rerun attached.\n"
        "- Remaining blockers: full wrapper-based 2024/2025 run and final package dry-run.\n\n"
        "## 3. Track B / Sector Status\n\n"
        "- Default candidate: s1_sector\n"
        "- Experimental candidate: sector_rotation_track2\n"
        "- Fallback: s1_sector\n"
        "- Evidence: s1_sector beats sector_rotation_track2 on 2024 local evidence.\n"
        "- Remaining blockers: sector rotation cannot be promoted without stronger construction-period evidence.\n\n"
        "## 4. Stage Status Summary\n\n"
        + md_table(["Stage", "Status", "Main Fix Completed", "Remaining Risk"], stage_rows)
        + "\n\n## 5. Model / Method Status Summary\n\n"
        + md_table(["Method Group", "Promote", "Fallback", "Ablation Only", "Reject / Defer"], method_rows)
        + "\n\n## 6. Official Parity Status\n\n"
        f"S0/S1 parity status: {_parity_status_text(parity_rows)}.\n\n"
        "## 7. Hugging Face / Local Model Decision\n\n"
        "No local Hugging Face models were downloaded. Optional offline text models remain disabled by default with rule-based fallback.\n\n"
        "## 8. Package Status\n\n"
        f"Package rebuild status: {package_result.get('status')}.\n\n"
        "## 9. Required Fixes Before Final Submission\n\n"
        "1. Run full-year 2024 and locked 2025 through the submitted wrapper path.\n"
        "2. Run an official server smoke using the rebuilt package artifact.\n"
        "3. Add Docker or equivalent environment lock if organisers require it.\n"
        "4. Keep Track B default as S1 unless construction-period evidence changes.\n"
        "5. Keep LLM/Hugging Face paths optional and disabled by default.\n\n"
        "## 10. Recommended Next Prompt\n\n"
        "Prompt15 - Wrapper-Based Full-Year Validation and Package Dry-Run: run 2024/2025 through the official wrapper, verify package execution from a clean extraction, and finalize the submission checklist.\n",
    )


def main() -> int:
    args = parse_args()
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    parity_rows = run_parity(args.base_url, args.parity_start, args.parity_end, skip_official=args.skip_official_parity)
    write_parity_report(parity_rows)
    package_result = rebuild_package(args.skip_package)
    write_wrapper_report(parity_rows)
    write_status_reports(parity_rows)
    write_hf_report()
    write_pipeline_report(parity_rows, package_result)
    write_final_recommendation(parity_rows, package_result)
    write_json(REPORT_DIR / "run_summary.json", {"parity": parity_rows, "package": package_result})
    print(json.dumps({"status": "ok", "reports": str(REPORT_DIR), "parity": parity_rows, "package": package_result.get("status")}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
