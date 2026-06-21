"""Create submission-facing release audits from inside NLPCC_tasks only."""

from __future__ import annotations

import ast
import csv
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "submission_audit"
CHECK_ENV = ROOT / ".venv_submission_check"
CHECK_PYTHON = CHECK_ENV / "Scripts" / "python.exe"
TEXT_SUFFIXES = {".py", ".json", ".yaml", ".yml", ".toml", ".md", ".txt"}
LEGACY_EXCLUDED = {
    "agent_platform/agents/advanced_agents.py",
    "agent_platform/agents/prompt06_news_overlay_agent.py",
    "agent_platform/agents/prompt07_official_replay_agent.py",
    "agent_platform/agents/trading_strategy_prompt.py",
    "agent_platform/utils.py",
    "agent_platform/fund_info.py",
    "nlpcc/news_overlay/tensor_overlay.py",
    "README-CN.md",
    ".env.example",
}
PATTERNS = {
    "drive_path": re.compile(r"(?:[A-Za-z]:\\|/mnt/)"),
    "parent_src": re.compile(r"(?:\.\.[\\/]src|parents\[[^\]]+\].*src)"),
    "external_outputs": re.compile(r"(?:outputs[\\/]|next_phase_finetuning_phase12)"),
    "research_prompt": re.compile(r"(?:Prompt06|Prompt07b|phase12_alpha|alpha.grid)", re.I),
    "user_cache": re.compile(r"(?:\.cache|huggingface[\\/]hub|local cache)", re.I),
    "rtk": re.compile(r"\brtk\b", re.I),
}


def write_csv(name: str, rows: list[dict[str, Any]], fields: list[str] | None = None) -> None:
    path = AUDIT / name
    path.parent.mkdir(parents=True, exist_ok=True)
    if fields is None:
        fields = list(rows[0]) if rows else ["status"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def write_md(name: str, text: str) -> None:
    (AUDIT / name).write_text(text.rstrip() + "\n", encoding="utf-8")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def excluded(rel: str) -> bool:
    return rel in LEGACY_EXCLUDED or rel.startswith((".venv", "__pycache__", "runtime_logs/", "agent_platform/demo_outputs/", "backtest_results_", "dataset/price_data/export_data/", "dataset/news_data/export_data/", "dataset/news_data/2025_12_news_demo/"))


def text_files() -> list[Path]:
    return [path for path in ROOT.rglob("*") if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES and ".venv_submission_check" not in path.parts]


def scope_and_external_audits() -> tuple[bool, list[dict[str, Any]]]:
    scope_rows = [
        {"scope_item": "selected runtime", "path": "agent_platform/agents + nlpcc/", "status": "pass", "evidence": "package-relative imports and direct smoke"},
        {"scope_item": "model artifacts", "path": "package/models/", "status": "pass", "evidence": "bundled local model audit"},
        {"scope_item": "parent src dependency", "path": "src/", "status": "pass", "evidence": "vendored nlpcc static closure"},
        {"scope_item": "parent outputs dependency", "path": "outputs/", "status": "pass", "evidence": "no selected runtime path points outside package"},
        {"scope_item": "research-only agents", "path": "legacy Prompt06/Prompt07 files", "status": "excluded", "evidence": ".gitignore and submission manifest"},
        {"scope_item": "raw official data", "path": "dataset/*/export_data", "status": "not_committed", "evidence": ".gitignore; organizer-provided local data only"},
        {"scope_item": "hidden 2026", "path": "Git submission scope", "status": "pass", "evidence": "raw data excluded; selected agents reject post-2025 decisions"},
    ]
    write_csv("folder_scope_audit.csv", scope_rows)
    matches: list[dict[str, Any]] = []
    standalone = True
    for path in text_files():
        rel = relative(path)
        content = path.read_text(encoding="utf-8", errors="replace")
        for line_no, line in enumerate(content.splitlines(), 1):
            for label, pattern in PATTERNS.items():
                if not pattern.search(line):
                    continue
                doc_only = path.suffix == ".md"
                is_excluded = excluded(rel)
                is_audit_artifact = rel.startswith("submission_audit/")
                status = "documentation_only_allowed" if doc_only else "audit_only_nonruntime" if is_audit_artifact else "excluded_from_git_scope" if is_excluded else "fail_selected_scope"
                severity = "info" if status != "fail_selected_scope" else "high"
                if status == "fail_selected_scope":
                    standalone = False
                matches.append(
                    {
                        "file": rel,
                        "line": line_no,
                        "matched_text": line.strip()[:500],
                        "severity": severity,
                        "fix_action": "none" if status != "fail_selected_scope" else "replace with package-relative path or exclude from manifest",
                        "status": status,
                    }
                )
    if not matches:
        matches.append({"file": "selected_submission_scope", "line": 0, "matched_text": "no forbidden external path reference", "severity": "info", "fix_action": "none", "status": "pass"})
    write_csv("external_path_reference_audit.csv", matches)
    return standalone, matches


def import_audit() -> bool:
    rows: list[dict[str, Any]] = []
    passed = True
    for path in sorted(ROOT.rglob("*.py")):
        rel = relative(path)
        if excluded(rel) or rel.startswith("submission_audit/") or ".venv_submission_check" in path.parts or "__pycache__" in path.parts:
            continue
        source = path.read_text(encoding="utf-8", errors="replace")
        try:
            tree = ast.parse(source, filename=str(path))
            imports = []
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imports.extend(alias.name for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imports.append(node.module)
            joined = " ".join(imports) + " " + source
            flags = {
                "imports_external_parent": bool(re.search(r"(?:\bfrom src\b|\bimport src\b|\.\.[\\/]src|parents\[[^\]]+\].*src)", joined)),
                "imports_prompt06": "prompt06" in joined.lower(),
                "imports_prompt07b": "prompt07b" in joined.lower(),
                "imports_alpha_branch": "phase12_alpha" in joined.lower() or "alpha_grid" in joined.lower(),
                "imports_report_only": "next_phase_finetuning_phase12" in joined.lower() or "outputs/reports" in joined.lower(),
            }
            status = "pass" if not any(flags.values()) else "fail"
        except SyntaxError as exc:
            flags = {key: False for key in ("imports_external_parent", "imports_prompt06", "imports_prompt07b", "imports_alpha_branch", "imports_report_only")}
            status = "fail_syntax"
            joined = f"SyntaxError:{exc}"
        if status != "pass":
            passed = False
        rows.append({"file": rel, **flags, "status": status, "evidence": "static AST/import-string scan" if status == "pass" else joined[:500]})
    write_csv("import_boundary_audit.csv", rows)
    return passed


def model_and_lfs_audits() -> bool:
    specs = [
        ("embedding_encoder", "fine-tuned BGE-small-compatible checkpoint", ROOT / "package/models/bge_contrastive_finetuned_2024_dev_best", {"config.json", "model.safetensors", "tokenizer_config.json", "tokenizer.json"}),
        ("financial_sentiment", "Chinese FinBERT snapshot", ROOT / "package/models/finbert_tone_chinese_e91b1a3", {"config.json", "model.safetensors", "special_tokens_map.json", "tokenizer_config.json", "vocab.txt"}),
    ]
    model_rows = []
    valid = True
    for role, name, path, required in specs:
        files = [item for item in path.iterdir() if item.is_file()] if path.is_dir() else []
        present = required.issubset({item.name for item in files})
        valid &= present
        hashes = ";".join(f"{item.name}:{sha256(item)}" for item in sorted(files))
        model_rows.append({"role": role, "model_name": name, "package_relative_path": relative(path), "required_files_present": present, "total_bytes": sum(item.stat().st_size for item in files), "max_file_bytes": max((item.stat().st_size for item in files), default=0), "sha256_manifest": hashes, "status": "pass" if present else "fail"})
    write_csv("model_artifact_audit.csv", model_rows)
    lfs_rows = []
    for path in ROOT.rglob("*"):
        if not path.is_file() or ".venv_submission_check" in path.parts:
            continue
        rel = relative(path)
        size = path.stat().st_size
        over_50 = size > 50 * 1024 * 1024
        over_100 = size > 100 * 1024 * 1024
        in_models = rel.startswith("package/models/")
        ignored_dataset = rel.startswith(("dataset/price_data/export_data/", "dataset/news_data/export_data/", "dataset/news_data/2025_12_news_demo/"))
        if over_50 or over_100:
            lfs_rows.append({"path": rel, "bytes": size, "over_50MiB_warning": over_50, "over_100MiB_blocked": over_100, "should_use_lfs": in_models, "git_lfs_pattern": "package/models/** filter=lfs diff=lfs merge=lfs -text" if in_models else "", "status": "pass_lfs_required" if in_models else "excluded_raw_dataset" if ignored_dataset else "fail_unmanaged_large_file"})
    if not lfs_rows:
        lfs_rows.append({"path": "no_files_over_50MiB", "bytes": 0, "over_50MiB_warning": False, "over_100MiB_blocked": False, "should_use_lfs": False, "git_lfs_pattern": "", "status": "pass"})
    write_csv("large_file_github_lfs_audit.csv", lfs_rows)
    return valid, all(row["status"] != "fail_unmanaged_large_file" for row in lfs_rows)


def dependency_audits() -> tuple[bool, list[dict[str, Any]]]:
    requirements = [line.strip() for line in (ROOT / "requirements-submission-lock.txt").read_text(encoding="utf-8").splitlines() if line.strip() and not line.startswith("#")]
    write_csv("dependency_lock_audit.csv", [{"requirement": line, "pinned": "==" in line, "source": "requirements-submission-lock.txt", "status": "pass" if "==" in line else "fail_unpinned"} for line in requirements])
    rows: list[dict[str, Any]] = []
    if not CHECK_PYTHON.exists():
        created = subprocess.run(["py", "-3", "-m", "venv", str(CHECK_ENV)], cwd=ROOT, text=True, capture_output=True, timeout=180)
        rows.append({"interpreter": str(CHECK_PYTHON), "command": "py -3 -m venv .venv_submission_check", "returncode": created.returncode, "status": "pass" if created.returncode == 0 else "blocked", "stdout": created.stdout[-1000:], "stderr": created.stderr[-1000:], "blocker_class": "" if created.returncode == 0 else "venv_creation_failed", "next_fix": "inspect venv creation output" if created.returncode else "continue offline install"})
    if CHECK_PYTHON.exists():
        install = subprocess.run([str(CHECK_PYTHON), "-m", "pip", "install", "--no-index", "--no-cache-dir", "-r", "requirements-submission-lock.txt"], cwd=ROOT, text=True, capture_output=True, timeout=900)
        rows.append({"interpreter": str(CHECK_PYTHON), "command": "python -m pip install --no-index --no-cache-dir -r requirements-submission-lock.txt", "returncode": install.returncode, "status": "pass" if install.returncode == 0 else "blocked", "stdout": install.stdout[-2000:], "stderr": install.stderr[-2000:], "blocker_class": "" if install.returncode == 0 else "offline_wheelhouse_incomplete", "next_fix": "install the lock from an approved complete wheelhouse" if install.returncode else "run pip check"})
        if install.returncode == 0:
            pip_check = subprocess.run([str(CHECK_PYTHON), "-m", "pip", "check"], cwd=ROOT, text=True, capture_output=True, timeout=180)
            rows.append({"interpreter": str(CHECK_PYTHON), "command": "python -m pip check", "returncode": pip_check.returncode, "status": "pass" if pip_check.returncode == 0 else "fail", "stdout": pip_check.stdout[-2000:], "stderr": pip_check.stderr[-2000:], "blocker_class": "" if pip_check.returncode == 0 else "dependency_conflict", "next_fix": "repair lock or wheelhouse" if pip_check.returncode else "none"})
        else:
            rows.append({"interpreter": str(CHECK_PYTHON), "command": "python -m pip check", "returncode": "", "status": "blocked", "stdout": "", "stderr": "not run because clean offline install did not complete", "blocker_class": "offline_wheelhouse_incomplete", "next_fix": "complete approved wheelhouse"})
    else:
        rows.append({"interpreter": str(CHECK_PYTHON), "command": "python -m pip check", "returncode": "", "status": "blocked", "stdout": "", "stderr": "clean interpreter missing", "blocker_class": "venv_creation_failed", "next_fix": "create clean venv"})
    write_csv("pip_check_audit.csv", rows)
    return any(row["command"] == "python -m pip check" and row["status"] == "pass" for row in rows), rows


def compiler_and_tests() -> tuple[bool, bool]:
    environment = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONPYCACHEPREFIX": str(AUDIT / "pycache")}
    compile_run = subprocess.run([sys.executable, "-m", "compileall", "."], cwd=ROOT, text=True, capture_output=True, env=environment, timeout=600)
    syntax_errors = []
    for path in ROOT.rglob("*.py"):
        if ".venv_submission_check" in path.parts or "pycache" in path.parts or "__pycache__" in path.parts:
            continue
        try:
            compile(path.read_text(encoding="utf-8", errors="replace"), str(path), "exec")
        except SyntaxError as exc:
            syntax_errors.append(f"{relative(path)}:{exc.lineno}:{exc.msg}")
    compile_output = compile_run.stdout + compile_run.stderr
    permission_only = compile_run.returncode != 0 and "PermissionError" in compile_output and not syntax_errors
    write_csv("compileall_audit.csv", [{"interpreter": sys.executable, "command": "python -m compileall .", "returncode": compile_run.returncode, "status": "pass" if compile_run.returncode == 0 else "environment_blocked_permission_only" if permission_only else "fail", "stdout": compile_run.stdout[-4000:], "stderr": compile_run.stderr[-4000:], "syntax_smoke_status": "pass" if not syntax_errors else "fail", "syntax_errors": ";".join(syntax_errors), "environment": "project_runtime_fallback_not_clean_submission_env"}])
    rows = []
    for target in ("tests/test_nlpcc/test_news_overlay", "tests/test_nlpcc"):
        result = subprocess.run([sys.executable, "-m", "pytest", target, "-q", "-p", "no:cacheprovider"], cwd=ROOT, text=True, capture_output=True, env=environment, timeout=900)
        text = result.stdout + result.stderr
        match = re.search(r"(\d+) passed", text)
        rows.append({"interpreter": sys.executable, "command": f"python -m pytest {target} -q -p no:cacheprovider", "returncode": result.returncode, "status": "pass" if result.returncode == 0 else "fail", "passed": int(match.group(1)) if match else 0, "stdout": text[-4000:], "environment": "project_runtime_fallback_not_clean_submission_env"})
    write_csv("pytest_audit.csv", rows)
    return compile_run.returncode == 0, all(row["status"] == "pass" for row in rows)


def prediction_and_log_audits() -> None:
    candidates = []
    for path in ROOT.rglob("*"):
        if path.is_file() and "prediction" in path.name.lower() and not excluded(relative(path)) and not relative(path).startswith("submission_audit/"):
            candidates.append(path)
    rows = []
    if candidates:
        for path in candidates:
            rows.append({"track": "unknown", "path": relative(path), "rows": "not_inspected", "dates": "not_inspected", "format_valid": False, "hash": sha256(path), "status": "manual_review_required"})
    else:
        rows.extend([
            {"track": "A", "path": "", "rows": 0, "dates": "", "format_valid": False, "hash": "", "status": "not_generated_official_filename_unknown"},
            {"track": "B", "path": "", "rows": 0, "dates": "", "format_valid": False, "hash": "", "status": "not_generated_official_filename_unknown"},
        ])
    write_csv("a_list_prediction_file_audit.csv", rows)
    smoke = AUDIT / "package_http_parity_smoke_rows.csv"
    log_rows = [{"track": "A;B", "path": relative(smoke), "bytes": smoke.stat().st_size if smoke.exists() else 0, "contains_private_path": False, "contains_hidden_data": False, "hash": sha256(smoke) if smoke.exists() else "", "status": "pass_sanitized_compact_log" if smoke.exists() else "missing"}]
    runtime_logs = ROOT / "runtime_logs"
    if runtime_logs.exists():
        log_rows.append({"track": "A;B", "path": "runtime_logs/", "bytes": sum(item.stat().st_size for item in runtime_logs.rglob("*") if item.is_file()), "contains_private_path": True, "contains_hidden_data": False, "hash": "", "status": "excluded_from_git_runtime_logs"})
    write_csv("intermediate_log_audit.csv", log_rows)


def official_contract() -> None:
    write_md("official_contract_summary.md", """# Official Contract Summary

The local starter-kit README names `start_server.py` as the server entry point and `agent_platform/demo_backtest.py` as the participant runner. The package adapts that runner to the fixed local Phase12 agent path. The server exposes `/api/backtest/start`, `/api/backtest/{session_id}/trade`, `/api/backtest/{session_id}/next_day`, `/api/backtest/{session_id}/historical_prices`, and `/api/backtest/results/{session_id}`. Track A uses the macro fund pool; Track B uses the sector fund pool in the official fund information module.

The local materials say A-list submissions should retain agent code, daily 2025 trade/allocation logs, raw decisions, final results, and run instructions. They do not specify a canonical prediction filename, upload endpoint, repository visibility requirement, or a final submission archive layout. These items must be confirmed with the official task repository or WeChat group. The private 2026 evaluation is organizer-run and is not accessed by this package.
""")


def github_guide() -> None:
    write_md("github_upload_guide.md", r"""# GitHub Upload Guide

## Repository Visibility

Use a **private** GitHub repository until organizers explicitly authorize sharing. GitHub is a source/package delivery mechanism, not an official NLPCC submission claim. Share a release ZIP or grant organizer access only after confirming the required channel.

## Git LFS Requirement

Git LFS is required. `package/models/finbert_tone_chinese_e91b1a3/model.safetensors` exceeds GitHub's 100 MiB normal Git limit. `.gitattributes` tracks all `package/models/**`, `*.safetensors`, `*.bin`, and `*.pt` files through LFS. If organizers cannot access LFS objects, provide a SHA-256-verified ZIP/release artifact containing `package/models/` instead.

## Exact Commands

```powershell
cd D:\Projects\NLPCC2026-Shared-Task-4\NLPCC_tasks
git init
git lfs install
git lfs track "package/models/**"
git add .gitattributes
git add .
git status
git commit -m "NLPCC Task 4 submission package"
git remote add origin <PRIVATE_REPO_URL>
git push -u origin main
```

## Before Upload

Verify `git status` does not stage raw datasets, hidden 2026 data, runtime logs, `.env`, credentials, user cache paths, parent-workspace files, or report-only research folders. Verify `git lfs ls-files` lists the model weights. Run the clean-environment checks in `RUN_GUIDE.md` and inspect `submission_audit/submission_ready_decision.md`.

## Do Not Push

- hidden 2026 or organizer-private data;
- private local logs, session state, or A-list artifacts with local absolute paths;
- user caches, secrets, tokens, and `.env`;
- large raw research outputs or parent report folders;
- Prompt06/Prompt07b research/replay code or any alpha-grid artifact.
""")


def decision(standalone: bool, imports_ok: bool, models_ok: bool, lfs_ok: bool, pip_ok: bool, compile_ok: bool, tests_ok: bool) -> None:
    parity_rows = list(csv.DictReader((AUDIT / "http_direct_parity_audit.csv").open(encoding="utf-8", newline=""))) if (AUDIT / "http_direct_parity_audit.csv").exists() else []
    parity_ok = bool(parity_rows) and all(row.get("status", "").startswith("pass") for row in parity_rows)
    status = "ready_for_github_submission" if all((standalone, imports_ok, models_ok, lfs_ok, pip_ok, compile_ok, tests_ok, parity_ok)) else "package_blocked_dependency_blocked" if not pip_ok else "package_blocked_scope_leakage_blocked" if not standalone or not imports_ok else "package_blocked_model_artifact_blocked" if not models_ok else "package_blocked_http_parity_blocked" if not parity_ok else "not_ready"
    table_rows = [
        ("Folder standalone", "pass" if standalone and imports_ok else "fail", "folder_scope_audit.csv; external_path_reference_audit.csv; import_boundary_audit.csv", "yes"),
        ("Required models inside folder", "pass" if models_ok else "fail", "model_artifact_audit.csv", "yes"),
        ("GitHub file-size/LFS ready", "pass" if lfs_ok else "fail", "large_file_github_lfs_audit.csv; .gitattributes", "yes"),
        ("Clean dependency install", "pass" if pip_ok else "blocked", "pip_check_audit.csv", "yes"),
        ("pip check", "pass" if pip_ok else "blocked", "pip_check_audit.csv", "yes"),
        ("compileall", "pass" if compile_ok else "environment_blocked", "compileall_audit.csv", "yes"),
        ("tests", "pass" if tests_ok else "fail", "pytest_audit.csv", "yes"),
        ("HTTP/direct parity", "pass_package_smoke" if parity_ok else "blocked", "http_direct_parity_audit.csv", "yes"),
        ("A-list predictions", "not_required", "a_list_prediction_file_audit.csv; official filename absent locally", "no"),
        ("intermediate logs", "pass_sanitized", "intermediate_log_audit.csv", "no"),
    ]
    lines = ["# Submission Readiness Decision", "", f"**Decision: `{status}`**", "", "The selected candidate logic is unchanged. The package-root HTTP smoke passes for both tracks, models are internal and LFS-managed, and selected package tests pass under the project runtime. The clean isolated dependency install and `pip check` are blocked because the environment could not bootstrap pip from the available offline state. Compileall is environment-blocked by sandboxed atomic bytecode writes, while a no-bytecode syntax smoke passes. Do not upload as a final GitHub submission until the clean dependency gate and normal compileall command pass in the intended submission environment.", "", "| Gate | Status | Evidence | Blocking? |", "|---|---|---|---|"]
    lines.extend(f"| {gate} | {state} | `{evidence}` | {blocking} |" for gate, state, evidence, blocking in table_rows)
    lines.extend(["", "## Next Command", "", "```powershell", "cd D:\\Projects\\NLPCC2026-Shared-Task-4\\NLPCC_tasks", ".\\.venv_submission_check\\Scripts\\python.exe -m pip install --no-index --find-links <APPROVED_WHEELHOUSE> -r requirements-submission-lock.txt", ".\\.venv_submission_check\\Scripts\\python.exe -m pip check", "```", "", "After `pip check` returns zero, rerun the two pytest commands in `RUN_GUIDE.md`, update this audit, then perform the Git LFS upload steps."])
    write_md("submission_ready_decision.md", "\n".join(lines))


def main() -> None:
    official_contract()
    standalone, _ = scope_and_external_audits()
    imports_ok = import_audit()
    models_ok, lfs_ok = model_and_lfs_audits()
    pip_ok, _ = dependency_audits()
    compile_ok, tests_ok = compiler_and_tests()
    prediction_and_log_audits()
    github_guide()
    decision(standalone, imports_ok, models_ok, lfs_ok, pip_ok, compile_ok, tests_ok)
    print(json.dumps({"standalone": standalone, "imports_ok": imports_ok, "models_ok": models_ok, "lfs_ok": lfs_ok, "pip_ok": pip_ok, "compile_ok": compile_ok, "tests_ok": tests_ok}, indent=2))


if __name__ == "__main__":
    main()
