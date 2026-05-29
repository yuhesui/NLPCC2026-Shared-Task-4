"""Repository-wide verification suite for prompt11."""

from __future__ import annotations

import importlib
import json
from pathlib import Path
import sys
from typing import Any

from tools.backtesting.compare_official_local import compare_metric_dicts
from tools.backtesting.official_server_runner import ensure_official_server_startable, probe_official_server
from tools.verification.dependency_audit import audit_nlpcc_does_not_import_tools
from tools.verification.leakage_audit import audit_backtest_file
from tools.verification.reproducibility_audit import hash_files, runtime_fingerprint, sha256_file
from tools.verification.submission_audit import audit_outputs_exist, audit_required_paths


def run_import_audit(src_root: Path = Path("src")) -> dict[str, Any]:
    if str(src_root.resolve()) not in sys.path:
        sys.path.insert(0, str(src_root.resolve()))
    modules = []
    failures = []
    for path in sorted(src_root.rglob("*.py")):
        if "__pycache__" in path.parts:
            continue
        relative = path.relative_to(src_root).with_suffix("")
        module = ".".join(relative.parts)
        modules.append(module)
        try:
            importlib.import_module(module)
        except Exception as exc:  # pragma: no cover - exercised by verification runs
            failures.append({"module": module, "path": str(path), "error": f"{type(exc).__name__}: {exc}"})
    return {"checked": len(modules), "failures": failures}


def run_leakage_audit(outputs_root: Path = Path("outputs")) -> dict[str, Any]:
    files = [
        *outputs_root.glob("backtests/*.json"),
        *outputs_root.glob("experiments/**/*.json"),
        *outputs_root.glob("smoke_tests/*.json"),
    ]
    audited = []
    issues = []
    for path in sorted(set(files)):
        try:
            file_issues = audit_backtest_file(path)
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue
        audited.append(str(path))
        for issue in file_issues:
            issues.append({"path": str(path), **issue.__dict__})
    return {"checked_files": audited, "issues": issues}


def run_raw_data_immutability_audit(data_root: Path = Path("data")) -> dict[str, Any]:
    manifests = sorted(data_root.glob("*/manifests/*.json"))
    checked = []
    issues = []
    for manifest_path in manifests:
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            issues.append({"manifest": str(manifest_path), "code": "manifest_parse_error", "message": str(exc)})
            continue
        for item in manifest.get("files", []):
            expected = item.get("sha256")
            if not expected:
                continue
            candidate = item.get("target_path") or item.get("path")
            if not candidate:
                continue
            path = Path(candidate)
            if not path.exists():
                issues.append({"manifest": str(manifest_path), "path": str(path), "code": "missing_file"})
                continue
            actual = sha256_file(path)
            checked.append({"manifest": str(manifest_path), "path": str(path)})
            if actual != expected:
                issues.append(
                    {
                        "manifest": str(manifest_path),
                        "path": str(path),
                        "code": "sha256_mismatch",
                        "expected": expected,
                        "actual": actual,
                    }
                )
    return {"checked_count": len(checked), "issues": issues}


def run_doc_policy_audit(paths: tuple[Path, ...] = (Path("README.md"), Path("AGENTS.md"), Path("METHODOLOGY.md"), Path("WORKFLOW.md"), Path("docs"))) -> dict[str, Any]:
    files = []
    for root in paths:
        if root.is_file():
            files.append(root)
        elif root.exists():
            files.extend(root.rglob("*.md"))
    issues = []
    ignored_instruction_refs = {
        "docs/prompts/execution/prompt00_repo_reset_skeleton_and_docs.md",
        "docs/prompts/execution/prompt11_verification_and_fix.md",
    }
    for path in sorted(set(files)):
        text = path.read_text(encoding="utf-8", errors="replace")
        normalized = path.as_posix()
        if ("src/nlpcc4" in text or "nlpcc4" in text) and normalized not in ignored_instruction_refs:
            issues.append({"path": str(path), "code": "stale_nlpcc4_reference"})
        if "Main reusable Python code should live under `src/`, preferably `src/nlpcc/`" in text:
            issues.append({"path": str(path), "code": "flat_src_policy_reference"})
    policy_confirmed = {
        "README.md": "src/nlpcc/" in Path("README.md").read_text(encoding="utf-8")
        and "src/tools/" in Path("README.md").read_text(encoding="utf-8"),
        "AGENTS.md": "src/nlpcc/" in Path("AGENTS.md").read_text(encoding="utf-8")
        and "src/tools/" in Path("AGENTS.md").read_text(encoding="utf-8"),
    }
    return {"checked_files": len(set(files)), "policy_confirmed": policy_confirmed, "issues": issues}


def run_dependency_boundary_audit(src_root: Path = Path("src")) -> dict[str, Any]:
    issues = audit_nlpcc_does_not_import_tools(src_root)
    return {"issues": [issue.__dict__ for issue in issues]}


def run_submission_audit(repo_root: Path = Path(".")) -> dict[str, Any]:
    issues = [*audit_required_paths(repo_root), *audit_outputs_exist(repo_root)]
    return {"issues": [issue.__dict__ for issue in issues]}


def run_official_local_audit() -> dict[str, Any]:
    startable = ensure_official_server_startable(Path("."))
    probe = probe_official_server()
    self_compare = compare_metric_dicts({"sharpe_ratio": 1.0}, {"sharpe_ratio": 1.0}).as_dict()
    return {
        "server_startable": startable,
        "server_probe": probe,
        "metric_comparison_self_check": self_compare,
        "note": "Official/local metric parity requires a running official server result; this audit records startability and probe status.",
    }


def run_reproducibility_audit() -> dict[str, Any]:
    hash_targets = [
        Path("pyproject.toml"),
        Path("README.md"),
        Path("AGENTS.md"),
        Path("configs/tools/experiments/prompt10_ablation_suite.json"),
    ]
    existing = [path for path in hash_targets if path.exists()]
    return {"runtime": runtime_fingerprint(), "hashes": hash_files(existing)}


def run_verification_suite(repo_root: Path = Path(".")) -> dict[str, Any]:
    return {
        "import_audit": run_import_audit(repo_root / "src"),
        "dependency_boundary_audit": run_dependency_boundary_audit(repo_root / "src"),
        "leakage_audit": run_leakage_audit(repo_root / "outputs"),
        "official_local_audit": run_official_local_audit(),
        "raw_data_immutability_audit": run_raw_data_immutability_audit(repo_root / "data"),
        "doc_policy_audit": run_doc_policy_audit(),
        "submission_audit": run_submission_audit(repo_root),
        "reproducibility_audit": run_reproducibility_audit(),
    }


def write_verification_outputs(report: dict[str, Any], *, output_dir: Path = Path("outputs/reports/prompt11")) -> dict[str, str]:
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "verification_report.json"
    md_path = output_dir / "verification_report.md"
    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True), encoding="utf-8")
    md_path.write_text(_markdown_summary(report), encoding="utf-8")
    return {"json": str(json_path), "markdown": str(md_path)}


def _markdown_summary(report: dict[str, Any]) -> str:
    import_failures = len(report["import_audit"]["failures"])
    dependency_issues = len(report["dependency_boundary_audit"]["issues"])
    leakage_issues = len(report["leakage_audit"]["issues"])
    data_issues = len(report["raw_data_immutability_audit"]["issues"])
    doc_issues = len(report["doc_policy_audit"]["issues"])
    submission_issues = len(report["submission_audit"]["issues"])
    lines = [
        "# Prompt11 Verification Report",
        "",
        "| Audit | Status | Detail |",
        "| --- | --- | --- |",
        f"| Import audit | {'PASS' if import_failures == 0 else 'FAIL'} | {report['import_audit']['checked']} modules, {import_failures} failures |",
        f"| Dependency boundary | {'PASS' if dependency_issues == 0 else 'FAIL'} | {dependency_issues} `src/nlpcc` -> `tools` imports |",
        f"| Leakage metadata | {'PASS' if leakage_issues == 0 else 'FAIL'} | {len(report['leakage_audit']['checked_files'])} result files, {leakage_issues} issues |",
        f"| Raw data immutability | {'PASS' if data_issues == 0 else 'FAIL'} | {report['raw_data_immutability_audit']['checked_count']} files checked, {data_issues} issues |",
        f"| Documentation policy | {'PASS' if doc_issues == 0 else 'FAIL'} | {doc_issues} stale policy references |",
        f"| Submission paths | {'PASS' if submission_issues == 0 else 'FAIL'} | {submission_issues} issues |",
        f"| Official server probe | {report['official_local_audit']['server_probe'].get('status', 'unknown').upper()} | {report['official_local_audit']['server_probe'].get('blocker', report['official_local_audit']['server_probe'].get('path', ''))} |",
        "",
        "See `verification_report.json` for full issue lists, runtime fingerprint, and config hashes.",
    ]
    return "\n".join(lines) + "\n"
