#!/usr/bin/env python3
"""Run or diagnose an official-server smoke path."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any
from urllib import error, parse, request


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nlpcc.core.fund_universe import get_fund_pool  # noqa: E402
from nlpcc.stage4_agent.models.smoke_one_unit_agent import SmokeOneUnitAgent  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run official server smoke check if a server is available.")
    parser.add_argument("--base-url", default="http://localhost:6207")
    parser.add_argument("--track", choices=["macro", "sector"], default="macro")
    parser.add_argument("--username", default="prompt01_smoke")
    parser.add_argument("--password", default="prompt01_smoke")
    parser.add_argument("--start-date", default="2025-01-02")
    parser.add_argument("--end-date", default="2025-01-06")
    parser.add_argument("--output", default=str(REPO_ROOT / "outputs" / "smoke_tests" / "official_server_smoke.json"))
    return parser.parse_args()


def _json_request(method: str, base_url: str, endpoint: str, payload: dict[str, Any] | None = None, token: str | None = None) -> dict[str, Any]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    req = request.Request(f"{base_url}{endpoint}", data=data, headers=headers, method=method)
    with request.urlopen(req, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def _form_request(base_url: str, endpoint: str, payload: dict[str, str]) -> dict[str, Any]:
    data = parse.urlencode(payload).encode("utf-8")
    req = request.Request(
        f"{base_url}{endpoint}",
        data=data,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with request.urlopen(req, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def _write_result(path: Path, result: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")


def run(args: argparse.Namespace) -> dict[str, Any]:
    try:
        _json_request("GET", args.base_url, "/api/funds/funds")
    except (error.URLError, TimeoutError, ConnectionError) as exc:
        return {
            "status": "blocked",
            "blocker": "official_server_unavailable",
            "detail": str(exc),
            "base_url": args.base_url,
        }

    try:
        _json_request("POST", args.base_url, "/api/agents/register", {"username": args.username, "password": args.password})
        token = _form_request(args.base_url, "/api/agents/token", {"username": args.username, "password": args.password}).get("access_token")
        fund_pool = list(get_fund_pool(args.track))
        config = {
            "start_date": args.start_date,
            "end_date": args.end_date,
            "initial_capital": 100000,
            "fund_pool": fund_pool,
            "agents": [{"name": args.username, "prompt": "prompt01 smoke"}],
            "news_sources": ["caixin", "tiantian", "sinafinance", "tencent"],
            "lookback_days": 2,
            "top_rank": 20,
            "pre_k_days": 1,
            "view_platform_trading_history_days": 1,
            "decision_model_name": "prompt01_smoke_no_llm",
            "results_dir": "outputs/smoke_tests/official_server",
        }
        start = _json_request("POST", args.base_url, "/api/backtest/start", config, token=token)
        session_id = start["session_id"]
        data = start.get("data", {})
        historical = _json_request("GET", args.base_url, f"/api/backtest/{session_id}/historical_prices?lookback_days=2", token=token)
        status = _json_request("GET", args.base_url, f"/api/backtest/{session_id}/status", token=token)
        decision = SmokeOneUnitAgent().make_decision(
            track=args.track,
            fund_pool=fund_pool,
            historical_prices=historical.get("historical_prices", {}),
            news=data.get("news", []),
            current_portfolio=status,
        )
        if decision.get("trades"):
            _json_request(
                "POST",
                args.base_url,
                f"/api/backtest/{session_id}/trade",
                {
                    "trades": decision["trades"],
                    "agent_decision": {
                        "decision": decision,
                        "reasoning": decision.get("reasoning", ""),
                        "chain_of_thought": "",
                    },
                },
                token=token,
            )
        return {
            "status": "ok",
            "session_id": session_id,
            "decision": decision,
        }
    except Exception as exc:
        return {
            "status": "blocked",
            "blocker": "official_server_smoke_failed",
            "detail": repr(exc),
            "base_url": args.base_url,
        }


def main() -> int:
    args = parse_args()
    result = run(args)
    output_path = Path(args.output)
    _write_result(output_path, result)
    print(f"{output_path} status={result['status']}")
    return 0 if result["status"] in {"ok", "blocked"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
