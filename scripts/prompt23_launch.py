#!/usr/bin/env python
"""Windows-safe launcher and monitor for Prompt23 long fresh-inference runs."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROGRESS = ROOT / "outputs" / "reports" / "news_overlay" / "prompt23" / "progress"
REFERENCE = ROOT / "outputs" / "reports" / "news_overlay" / "prompt23" / "reference"
PROCESS_JSON = PROGRESS / "prompt23_full_run_process.json"


def main() -> int:
    args = _parser().parse_args()
    if args.command == "launch":
        return launch(args)
    if args.command == "status":
        print(json.dumps(status(), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    raise ValueError(args.command)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Launch or monitor Prompt23 full run.")
    sub = parser.add_subparsers(dest="command", required=True)
    launch_parser = sub.add_parser("launch")
    launch_parser.add_argument("--device", default="auto")
    launch_parser.add_argument("--batch-size", type=int, default=64)
    launch_parser.add_argument("--cache-run-id", default="full_prompt23_resume")
    launch_parser.add_argument("--force", action="store_true")
    sub.add_parser("status")
    return parser


def launch(args: argparse.Namespace) -> int:
    PROGRESS.mkdir(parents=True, exist_ok=True)
    current = status() if PROCESS_JSON.exists() else {"alive": False}
    if current.get("alive") and not args.force:
        print(json.dumps({"launched": False, "reason": "already_running", "status": current}, indent=2, sort_keys=True))
        return 0

    stdout_path = PROGRESS / "prompt23_full_run.stdout.log"
    stderr_path = PROGRESS / "prompt23_full_run.stderr.log"
    command = [
        sys.executable,
        "-m",
        "nlpcc.news_overlay.prompt23_runner",
        "--device",
        args.device,
        "--batch-size",
        str(args.batch_size),
        "--cache-run-id",
        args.cache_run_id,
    ]
    env = clean_env(os.environ)
    env.update(
        {
            "PYTHONPATH": "src",
            "PYTHONDONTWRITEBYTECODE": "1",
            "TRANSFORMERS_OFFLINE": "1",
            "HF_HUB_OFFLINE": "1",
        }
    )
    stdout = stdout_path.open("ab")
    stderr = stderr_path.open("ab")
    creationflags = 0
    if os.name == "nt":
        creationflags = (
            getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            | getattr(subprocess, "DETACHED_PROCESS", 0)
            | getattr(subprocess, "CREATE_BREAKAWAY_FROM_JOB", 0)
        )
    proc = subprocess.Popen(
        command,
        cwd=ROOT,
        env=env,
        stdout=stdout,
        stderr=stderr,
        stdin=subprocess.DEVNULL,
        close_fds=False if os.name == "nt" else True,
        creationflags=creationflags,
    )
    stdout.close()
    stderr.close()
    metadata = {
        "pid": proc.pid,
        "launched_at": datetime.now().isoformat(timespec="seconds"),
        "command": command,
        "cwd": str(ROOT),
        "stdout_log": str(stdout_path),
        "stderr_log": str(stderr_path),
        "heartbeat_2024": str(PROGRESS / "2024_fresh_real_local_heartbeat.json"),
        "heartbeat_2025": str(PROGRESS / "2025_frozen_fresh_real_local_heartbeat.json"),
        "matrix_csv": str(REFERENCE / "full_fresh_2024_matrix.csv"),
        "frozen_2025_csv": str(REFERENCE / "frozen_2025_matrix.csv"),
        "cache_run_id": args.cache_run_id,
        "resume": True,
    }
    PROCESS_JSON.write_text(json.dumps(metadata, ensure_ascii=False, indent=2, sort_keys=True), encoding="utf-8")
    time.sleep(1.0)
    print(json.dumps({"launched": True, "status": status()}, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def status() -> dict[str, Any]:
    metadata = _read_json(PROCESS_JSON)
    pid = int(metadata.get("pid") or 0)
    matrix = REFERENCE / "full_fresh_2024_matrix.csv"
    frozen = REFERENCE / "frozen_2025_matrix.csv"
    h2024 = PROGRESS / "2024_fresh_real_local_heartbeat.json"
    h2025 = PROGRESS / "2025_frozen_fresh_real_local_heartbeat.json"
    return {
        "pid": pid or "",
        "alive": _pid_alive(pid) if pid else False,
        "metadata_path": str(PROCESS_JSON),
        "matrix_rows": _csv_count(matrix),
        "frozen_2025_rows": _csv_count(frozen),
        "heartbeat_2024": _heartbeat_status(h2024),
        "heartbeat_2025": _heartbeat_status(h2025),
        "stdout_log": metadata.get("stdout_log", str(PROGRESS / "prompt23_full_run.stdout.log")),
        "stderr_log": metadata.get("stderr_log", str(PROGRESS / "prompt23_full_run.stderr.log")),
        "launched_at": metadata.get("launched_at", ""),
        "command": metadata.get("command", []),
    }


def clean_env(source: os._Environ[str]) -> dict[str, str]:
    cleaned: dict[str, str] = {}
    seen_lower: set[str] = set()
    for key, value in source.items():
        lower = key.lower()
        if lower in seen_lower:
            continue
        seen_lower.add(lower)
        cleaned[key] = value
    return cleaned


def _pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    if os.name == "nt":
        proc = subprocess.run(
            ["tasklist", "/FI", f"PID eq {pid}", "/FO", "CSV", "/NH"],
            check=False,
            capture_output=True,
            text=True,
        )
        return proc.returncode == 0 and str(pid) in proc.stdout
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _heartbeat_status(path: Path) -> dict[str, Any]:
    data = _read_json(path)
    if not data:
        return {"exists": False}
    updated = data.get("updated_at", "")
    age_sec = ""
    try:
        age_sec = round((datetime.now() - datetime.fromisoformat(updated)).total_seconds(), 3)
    except Exception:
        pass
    return {"exists": True, "age_sec": age_sec, **data}


def _csv_count(path: Path) -> int:
    if not path.exists():
        return 0
    with path.open("r", encoding="utf-8", newline="") as handle:
        return sum(1 for _ in csv.DictReader(handle))


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"parse_error": str(path)}


if __name__ == "__main__":
    raise SystemExit(main())
