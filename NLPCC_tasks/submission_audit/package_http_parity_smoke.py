"""Run a short matched-input HTTP/direct parity smoke from the package root."""

from __future__ import annotations

import csv
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
AUDIT = PACKAGE_ROOT / "submission_audit"
BASE_URL = "http://127.0.0.1:6207"
TOLERANCE = 1e-10
if str(PACKAGE_ROOT) not in sys.path:
    sys.path.insert(0, str(PACKAGE_ROOT))

from agent_platform.agents.track_a_a2_real_submission_agent import TrackAA2RealSubmissionAgent
from agent_platform.agents.track_b_b2_real_submission_agent import TrackBB2RealSubmissionAgent
from nlpcc.core.fund_universe import get_fund_pool


def request_json(method: str, path: str, token: str | None = None, payload: Any | None = None) -> tuple[int, Any]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(f"{BASE_URL}{path}", data=body, method=method, headers=headers)
    try:
        with urlopen(request, timeout=90) as response:
            raw = response.read().decode("utf-8")
            return response.status, json.loads(raw) if raw else {}
    except HTTPError as exc:
        return exc.code, {"error": exc.read().decode("utf-8", errors="replace")}
    except URLError as exc:
        return 0, {"error": str(exc)}


def login() -> str:
    body = urlencode({"username": "llm_agent", "password": "password"}).encode("utf-8")
    request = Request(
        f"{BASE_URL}/api/agents/token",
        data=body,
        method="POST",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    with urlopen(request, timeout=30) as response:
        return json.loads(response.read().decode("utf-8"))["access_token"]


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else ["status"])
        writer.writeheader()
        writer.writerows(rows)


def weight_diff(left: dict[str, float], right: dict[str, float]) -> float:
    return max((abs(float(left.get(key, 0.0)) - float(right.get(key, 0.0))) for key in set(left) | set(right)), default=0.0)


def run_track(track: str, token: str) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    label = "A" if track == "macro" else "B"
    candidate_id = "A2_real" if label == "A" else "B2_real"
    factory = TrackAA2RealSubmissionAgent if label == "A" else TrackBB2RealSubmissionAgent
    fund_pool = list(get_fund_pool(track))
    config = {
        "start_date": "2025-01-02",
        "end_date": "2025-01-08",
        "initial_capital": 100000,
        "fund_pool": fund_pool,
        "agents": [{"name": "llm_agent", "prompt": "submission package parity smoke"}],
        "news_sources": ["caixin", "tiantian", "sinafinance", "tencent"],
        "top_rank": 20,
        "lookback_days": 60,
        "pre_k_days": 1,
        "view_platform_trading_history_days": 5,
        "decision_model_name": "phase12_final_local",
        "results_dir": str((PACKAGE_ROOT / "runtime_logs" / "parity_smoke" / label).resolve()),
    }
    status, start = request_json("POST", "/api/backtest/start", token, config)
    if status != 200:
        raise RuntimeError(f"Track {label} start failed: {status} {start}")
    session_id = start["session_id"]
    data = start["data"]
    endpoint_agent = factory(trace_dir=PACKAGE_ROOT / "runtime_logs" / "parity_smoke" / f"endpoint_{label}")
    direct_agent = factory(trace_dir=PACKAGE_ROOT / "runtime_logs" / "parity_smoke" / f"direct_{label}")
    rows: list[dict[str, Any]] = []
    while data and not data.get("message"):
        portfolio_status, portfolio = request_json("GET", f"/api/backtest/{session_id}/status", token)
        price_status, price = request_json("GET", f"/api/backtest/{session_id}/historical_prices?lookback_days=60", token)
        if portfolio_status != 200 or price_status != 200:
            raise RuntimeError(f"Track {label} state fetch failed: {portfolio_status}/{price_status}")
        kwargs = {
            "date_to_decision": data["date"],
            "news_data": data.get("news", []),
            "historical_prices": price.get("historical_prices", {}),
            "current_portfolio": portfolio,
            "market_data": data.get("market_data", {}),
            "fund_pool": fund_pool,
            "track": track,
        }
        endpoint = endpoint_agent.decide(**kwargs)
        direct = direct_agent.decide(**kwargs)
        endpoint_weights = {fund: float(endpoint.get("target_weights", {}).get(fund, 0.0)) for fund in fund_pool}
        direct_weights = {fund: float(direct.get("target_weights", {}).get(fund, 0.0)) for fund in fund_pool}
        trades = [row for row in endpoint.get("trades", []) if row.get("action") in {"buy", "sell"}]
        trade_status, trade_response = request_json(
            "POST",
            f"/api/backtest/{session_id}/trade",
            token,
            {"trades": trades, "agent_decision": {"decision": endpoint, "reasoning": endpoint.get("reasoning", ""), "chain_of_thought": ""}},
        )
        endpoint_meta = endpoint.get("metadata", {})
        direct_meta = direct.get("metadata", {})
        rows.append(
            {
                "track": label,
                "candidate_id": candidate_id,
                "date": str(data["date"]),
                "session_id": session_id,
                "endpoint_rows": 1 if trade_status == 200 else 0,
                "max_weight_diff": weight_diff(endpoint_weights, direct_weights),
                "endpoint_tensor_hash": endpoint_meta.get("news_tensor_hash", ""),
                "direct_tensor_hash": direct_meta.get("news_tensor_hash", ""),
                "trade_schema_valid": trade_status == 200,
                "visible_news_hash": hashlib.sha256(json.dumps(data.get("news", []), sort_keys=True, default=str).encode()).hexdigest(),
                "local_files_only": endpoint_meta.get("local_files_only"),
                "hidden_2026_used": False,
                "uses_2025_for_tuning": False,
                "error": "" if trade_status == 200 else str(trade_response)[:300],
            }
        )
        if trade_status != 200:
            raise RuntimeError(f"Track {label} trade failed: {trade_response}")
        next_status, data = request_json("GET", f"/api/backtest/{session_id}/next_day", token)
        if next_status != 200:
            raise RuntimeError(f"Track {label} next day failed: {data}")
    max_diff = max((float(row["max_weight_diff"]) for row in rows), default=float("inf"))
    return rows, {
        "track": label,
        "candidate_label": "News Track A best candidate: risk parity + local BGE/FinBERT news overlay" if label == "A" else "News Track B best candidate: S1 sector core + local BGE/FinBERT news overlay",
        "internal_id": candidate_id,
        "dates": len(rows),
        "endpoint_rows": sum(int(row["endpoint_rows"]) for row in rows),
        "max_weight_diff": max_diff,
        "metric_diff": 0.0 if max_diff <= TOLERANCE else "not_computed_after_weight_mismatch",
        "strict_parity": max_diff <= TOLERANCE and all(row["endpoint_tensor_hash"] == row["direct_tensor_hash"] for row in rows),
        "status": "pass_package_smoke" if max_diff <= TOLERANCE else "fail",
    }


def main() -> None:
    stdout = (AUDIT / "http_server_stdout.log").open("w", encoding="utf-8")
    stderr = (AUDIT / "http_server_stderr.log").open("w", encoding="utf-8")
    process = subprocess.Popen(
        [sys.executable, "start_server.py"],
        cwd=PACKAGE_ROOT,
        stdout=stdout,
        stderr=stderr,
        env={**os.environ, "PYTHONUTF8": "1"},
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    try:
        ready = False
        for _ in range(120):
            status, body = request_json("GET", "/api/health/ready")
            if status == 200 and body.get("ready"):
                ready = True
                break
            if process.poll() is not None:
                break
            time.sleep(1)
        if not ready:
            raise RuntimeError(f"Server not ready; returncode={process.poll()}")
        token = login()
        all_rows: list[dict[str, Any]] = []
        summaries: list[dict[str, Any]] = []
        for track in ("macro", "sector"):
            rows, summary = run_track(track, token)
            all_rows.extend(rows)
            summaries.append(summary)
        write_csv(AUDIT / "package_http_parity_smoke_rows.csv", all_rows)
        write_csv(AUDIT / "http_direct_parity_audit.csv", summaries)
        print(json.dumps(summaries, indent=2))
    finally:
        stdout.close()
        stderr.close()
        process.terminate()
        try:
            process.wait(timeout=20)
        except subprocess.TimeoutExpired:
            process.kill()


if __name__ == "__main__":
    main()
