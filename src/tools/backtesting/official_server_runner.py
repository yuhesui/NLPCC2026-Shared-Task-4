"""Official local server process runner."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import subprocess
import sys
import time
from typing import Any
from urllib.error import URLError
from urllib.request import Request, urlopen


@dataclass
class OfficialServerRunner:
    repo_root: Path = Path(".")
    base_url: str = "http://localhost:6207"
    timeout_seconds: float = 3.0
    process: subprocess.Popen | None = None

    @property
    def nlpcc_tasks_root(self) -> Path:
        return (self.repo_root / "NLPCC_tasks").resolve()

    @property
    def start_script(self) -> Path:
        return (self.nlpcc_tasks_root / "start_server.py").resolve()

    def request_json(self, method: str, path: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        request = Request(
            f"{self.base_url.rstrip('/')}/{path.lstrip('/')}",
            data=body,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        with urlopen(request, timeout=self.timeout_seconds) as response:
            raw = response.read().decode("utf-8")
        return json.loads(raw) if raw else {}

    def probe(self) -> dict[str, Any]:
        for path in ("/api/health/ready", "/api/health", "/api"):
            try:
                return {"status": "ok", "path": path, "response": self.request_json("GET", path)}
            except (OSError, URLError, json.JSONDecodeError):
                continue
        return {"status": "blocked", "blocker": f"Official server is not reachable at {self.base_url}."}

    def can_start(self) -> dict[str, Any]:
        if not self.start_script.exists():
            return {"startable": False, "blocker": f"Missing server script: {self.start_script}"}
        return {"startable": True, "command": [sys.executable, str(self.start_script)]}

    def start(self, *, wait_seconds: float = 30.0) -> dict[str, Any]:
        startable = self.can_start()
        if not startable["startable"]:
            return {"status": "blocked", **startable}
        already_running = self.probe()
        if already_running["status"] == "ok":
            return {"status": "ok", "already_running": True, "probe": already_running}
        if self.process and self.process.poll() is None:
            return {"status": "ok", "already_running": False, "pid": self.process.pid}

        log_dir = self.repo_root.resolve() / "outputs" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        stdout_path = log_dir / "official_server_stdout.log"
        stderr_path = log_dir / "official_server_stderr.log"
        stdout = stdout_path.open("a", encoding="utf-8")
        stderr = stderr_path.open("a", encoding="utf-8")
        self.process = subprocess.Popen(
            [sys.executable, str(self.start_script)],
            cwd=str(self.nlpcc_tasks_root),
            stdout=stdout,
            stderr=stderr,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )

        deadline = time.time() + wait_seconds
        while time.time() < deadline:
            if self.process.poll() is not None:
                return {
                    "status": "blocked",
                    "blocker": f"Official server exited with code {self.process.returncode}.",
                    "stdout": str(stdout_path),
                    "stderr": str(stderr_path),
                }
            probe = self.probe()
            if probe["status"] == "ok":
                return {"status": "ok", "already_running": False, "pid": self.process.pid, "probe": probe}
            time.sleep(0.5)
        return {
            "status": "blocked",
            "blocker": f"Official server did not become ready within {wait_seconds} seconds.",
            "pid": self.process.pid,
            "stdout": str(stdout_path),
            "stderr": str(stderr_path),
        }

    def stop(self) -> dict[str, Any]:
        if not self.process or self.process.poll() is not None:
            return {"status": "ok", "stopped": False}
        self.process.terminate()
        try:
            self.process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            self.process.kill()
            self.process.wait(timeout=5)
        return {"status": "ok", "stopped": True}


def probe_official_server(base_url: str = "http://localhost:6207") -> dict[str, Any]:
    return OfficialServerRunner(base_url=base_url).probe()


def ensure_official_server_startable(repo_root: Path = Path(".")) -> dict[str, Any]:
    return OfficialServerRunner(repo_root=repo_root).can_start()
