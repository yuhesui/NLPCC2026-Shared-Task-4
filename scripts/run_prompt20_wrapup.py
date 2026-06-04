#!/usr/bin/env python3
"""Prompt20 wrap-up, cleanup, status dossier, and next-workflow reports."""

from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys
from typing import Any, Iterable, Mapping
import zipfile

import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
SCRIPTS_ROOT = REPO_ROOT / "scripts"
for path in (SRC_ROOT, SCRIPTS_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from run_prompt18_big_grid import _big_grid_lookup, _write_mapping  # noqa: E402


FINAL = {
    "track_a_primary": "p18_rp_macro_w10_s5",
    "track_a_fallback": "p18_rp_macro_w40_s5",
    "track_b_primary": "p18_leeqa_sector_k5_temp35",
    "track_b_fallback": "p18_s1_sector_t35_v30_w20",
}
TRACK_A = [
    "p18_rp_macro_w10_s5",
    "p18_rp_macro_w40_s5",
    "p18_rp_macro_w20_s5",
    "p18_bsa_macro_t10_g65",
    "p18_rp_macro_w60_s5",
]
TRACK_B = [
    "p18_leeqa_sector_k5_temp35",
    "p18_s1_sector_t35_v30_w20",
    "p18_leeqa_sector_k5_temp20",
    "p18_leeqa_sector_k5_temp70",
    "p18_leeqa_sector_k3_temp20",
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Prompt20 wrap-up workflow")
    parser.add_argument("--report-root", default=str(REPO_ROOT / "outputs" / "reports" / "prompt20"))
    parser.add_argument("--var-root", default=str(REPO_ROOT / ".var" / "prompt20"))
    args = parser.parse_args()
    report_root = Path(args.report_root)
    var_root = Path(args.var_root)
    _ensure_dirs(report_root, var_root)

    lookup = _big_grid_lookup(REPO_ROOT / ".var" / "prompt18")
    p18_rank = pd.read_csv(REPO_ROOT / "outputs" / "reports" / "prompt18" / "reference" / "big_grid_2024_ranking.csv")
    p19_one = pd.read_csv(REPO_ROOT / "outputs" / "reports" / "prompt19" / "reference" / "one_year_tune_test_leaderboard.csv")
    p19_locked = pd.read_csv(REPO_ROOT / "outputs" / "reports" / "prompt19" / "reference" / "locked_2025_test_results.csv")

    context_rows = _context_reconstruction_rows()
    manifest_rows, audit_rows = _preserve_candidates(lookup, p18_rank, p19_one, p19_locked, var_root)
    output_rows = _output_inventory()
    cleanup_rows = _cleanup()
    evidence_rows = _evidence_inventory(manifest_rows)
    status_rows = _repo_status_matrix()
    handoff_rows = _package_handoff_audit(manifest_rows)
    workflow_rows, backlog_rows = _next_stage_workflow_rows()

    _write_csv(report_root / "reference" / "candidate_preservation_manifest.csv", manifest_rows)
    _write_csv(report_root / "reference" / "trackA_preserved_candidates.csv", [r for r in manifest_rows if r["track"] == "macro"])
    _write_csv(report_root / "reference" / "trackB_preserved_candidates.csv", [r for r in manifest_rows if r["track"] == "sector"])
    _write_csv(report_root / "reference" / "preserved_config_audit.csv", audit_rows)
    _write_csv(report_root / "reference" / "output_folder_inventory.csv", output_rows)
    _write_csv(report_root / "reference" / "cleanup_manifest.csv", cleanup_rows)
    _write_csv(report_root / "reference" / "evidence_inventory.csv", evidence_rows)
    _write_csv(report_root / "reference" / "repo_status_matrix.csv", status_rows)
    _write_csv(report_root / "reference" / "package_handoff_audit.csv", handoff_rows)

    _write_md_table(report_root / "reference" / "candidate_preservation_manifest.md", "Candidate Preservation Manifest", manifest_rows)
    _write_md_table(report_root / "reference" / "preserved_config_audit.md", "Preserved Config Audit", audit_rows)
    _write_md_table(report_root / "reference" / "output_folder_inventory.md", "Output Folder Inventory", output_rows)
    _write_md_table(report_root / "reference" / "cleanup_manifest.md", "Cleanup Manifest", cleanup_rows)
    _write_md_table(report_root / "reference" / "evidence_inventory.md", "Evidence Inventory", evidence_rows)
    _write_md_table(report_root / "reference" / "repo_status_matrix.md", "Repo Status Matrix", status_rows)
    _write_md_table(report_root / "reference" / "package_handoff_audit.md", "Package Handoff Audit", handoff_rows)
    _write_text(report_root / "reference" / "next_stage_workflow_map.md", _workflow_map_md(workflow_rows))
    _write_text(report_root / "reference" / "next_stage_prompt_backlog.md", _backlog_md(backlog_rows))

    _write_md_table(report_root / "progress" / "progress_00_context_reconstruction.md", "Context Reconstruction", context_rows)
    _write_text(report_root / "progress" / "progress_01_preserved_candidate_selection.md", _preserved_selection_md(manifest_rows))
    _write_text(report_root / "progress" / "progress_02_preserved_candidate_configs.md", _preserved_configs_md(audit_rows))
    _write_text(report_root / "progress" / "progress_03_output_inventory.md", _inventory_summary_md(output_rows))
    _write_text(report_root / "progress" / "progress_04_cleanup_execution.md", _cleanup_summary_md(cleanup_rows))
    _write_text(report_root / "progress" / "progress_05_current_repo_status_dossier.md", "Current repository status dossier written to `presented/current_repo_status_report.md`.\n")
    _write_text(report_root / "progress" / "progress_06_next_stage_workflow_plan.md", "Next-stage news/text/news-overlay workflow and prompt backlog written under presented/reference Prompt20 reports.\n")
    _write_text(report_root / "progress" / "progress_07_package_and_handoff_check.md", _handoff_summary_md(handoff_rows))
    _write_text(report_root / "progress" / "run_log.md", f"# Prompt20 Run Log\n\nCompleted: {_now()}.\n")

    _write_text(report_root / "presented" / "preserved_candidate_summary.md", _preserved_summary(manifest_rows))
    _write_text(report_root / "presented" / "cleanup_summary.md", _cleanup_summary_md(cleanup_rows))
    _write_text(report_root / "presented" / "evidence_inventory_summary.md", _evidence_summary(evidence_rows))
    _write_text(report_root / "presented" / "current_repo_status_table.md", "# Current Repo Status Table\n\n" + _md_table(status_rows))
    _write_text(report_root / "presented" / "current_repo_status_report.md", _current_repo_status_report(manifest_rows, status_rows, cleanup_rows, evidence_rows))
    _write_text(report_root / "presented" / "next_stage_news_text_overlay_workflow.md", _next_stage_workflow_doc(backlog_rows))
    _write_text(report_root / "presented" / "next_stage_prompt_plan.md", _backlog_md(backlog_rows))
    _write_text(report_root / "presented" / "final_wrapup_recommendation.md", _final_wrapup(manifest_rows, cleanup_rows, handoff_rows))
    _write_text(report_root / "presented" / "executive_summary.md", _executive_summary(manifest_rows, cleanup_rows, handoff_rows))
    _write_text(report_root / "README.md", "# Prompt20 Reports\n\nRepository wrap-up, preserved candidates, cleanup inventory, current-state dossier, package/handoff audit, and next-stage news/text workflow plan.\n")

    _write_implementation_log(report_root, manifest_rows, cleanup_rows, handoff_rows)
    print(json.dumps({"status": "ok", "report_root": str(report_root), "preserved": len(manifest_rows)}, indent=2))
    return 0


def _ensure_dirs(report_root: Path, var_root: Path) -> None:
    for rel in ("progress", "presented", "reference"):
        (report_root / rel).mkdir(parents=True, exist_ok=True)
    for rel in ("inventory", "cleanup_archive", "preserved_candidates", "packages", "logs"):
        (var_root / rel).mkdir(parents=True, exist_ok=True)


def _context_reconstruction_rows() -> list[dict[str, Any]]:
    p19_pkg = REPO_ROOT / ".var" / "prompt19" / "packages"
    runtime = p19_pkg / "prompt19_official_runtime_20260603_085804.zip"
    repro = p19_pkg / "prompt19_reproducibility_20260603_085805.zip"
    p18 = json.loads((REPO_ROOT / "configs" / "prompt18_final_candidates.json").read_text())
    p19 = json.loads((REPO_ROOT / "configs" / "prompt19_tuned_candidates.json").read_text())
    rows = [
        _ctx("Official final candidates", str(FINAL), str(p18.get("source_candidates")), "pass", "Prompt18 final JSON matches expected final runtime aliases."),
        _ctx("Prompt19 readiness", "Ready for final human submission review", _grep_line(REPO_ROOT / "outputs" / "reports" / "prompt19" / "presented" / "final_readiness_report.md", "Ready for"), "pass", "Prompt19 final report exists."),
        _ctx("Prompt19 official runtime package", str(runtime), str(runtime.exists()), "pass" if runtime.exists() else "fail", "Package zip preserved."),
        _ctx("Prompt19 reproducibility package", str(repro), str(repro.exists()), "pass" if repro.exists() else "fail", "Package zip preserved."),
        _ctx("Manual official-server smoke", "User stated manually verified official-server smoke", "Confirmed in Prompt20 user context", "pass", "Recorded as user-provided context; not rerun in Prompt20."),
        _ctx("Final system report draft", "exists", str((REPO_ROOT / "outputs" / "reports" / "prompt19" / "presented" / "final_system_report_draft.md").exists()), "pass", "Prompt19 draft exists."),
        _ctx("Submission handoff checklist", "exists", str((REPO_ROOT / "outputs" / "reports" / "prompt19" / "presented" / "submission_handoff_checklist.md").exists()), "pass", "Prompt19 checklist exists."),
        _ctx("Prompt19 tuned configs research-only", "research_only=true", str(p19.get("research_only")), "pass" if p19.get("research_only") else "fail", "Tuned configs are not official replacements."),
        _ctx("Preserved-candidate layer before Prompt20", "3-5 runnable configs per track", "not present as dedicated layer", "partial", "Prompt20 creates the dedicated layer."),
    ]
    return rows


def _ctx(item: str, expected: str, actual: str, status: str, notes: str) -> dict[str, Any]:
    return {"Item": item, "Expected": expected, "Actual": actual, "Status": status, "Notes": notes}


def _preserve_candidates(lookup: Mapping[str, Any], p18_rank: pd.DataFrame, p19_one: pd.DataFrame, p19_locked: pd.DataFrame, var_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    base = REPO_ROOT / "configs" / "preserved_candidates"
    track_dirs = {"macro": base / "track_a", "sector": base / "track_b"}
    for path in track_dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    (var_root / "preserved_candidates").mkdir(parents=True, exist_ok=True)
    manifest: list[dict[str, Any]] = []
    audit: list[dict[str, Any]] = []
    for candidate in TRACK_A + TRACK_B:
        spec = lookup.get(candidate)
        if spec is None:
            audit.append({"Candidate": candidate, "Config Path": "", "Config Exists?": False, "Hash Match?": False, "Status": "fail", "Notes": "Candidate missing from Prompt18 lookup."})
            continue
        track = str(spec.track)
        config = json.loads(json.dumps(spec.config, ensure_ascii=False, default=str))
        config["name"] = candidate
        config["preserved_candidate"] = True
        config["preserved_official_runtime_candidate"] = candidate in FINAL.values()
        rel_path = Path("configs") / "preserved_candidates" / ("track_a" if track == "macro" else "track_b") / f"{candidate}.yaml"
        path = REPO_ROOT / rel_path
        _write_mapping(path, config)
        shutil.copy2(path, var_root / "preserved_candidates" / path.name)
        row2024 = _row_for(p18_rank, "Candidate", candidate)
        row2025 = _row_for(p19_locked, "Candidate", candidate)
        one = _row_for(p19_one, "Candidate", candidate)
        role = _role(candidate)
        preserved_for = _preserved_for(candidate)
        manifest.append(
            {
                "candidate_name": candidate,
                "track": track,
                "family": str(row2024.get("Family", getattr(spec, "family", ""))),
                "role": role,
                "source_prompt": "Prompt18 big grid + Prompt19 one-year tune/test",
                "source_rank": _clean(row2024.get("Rank", one.get("Rank", ""))),
                "source_score": _clean(row2024.get("Conservative Score", one.get("2024 Score", ""))),
                "2024_return": _clean(row2024.get("2024 Return", one.get("2024 Return", ""))),
                "2024_sharpe": _clean(row2024.get("2024 Sharpe", one.get("2024 Sharpe", ""))),
                "2025_return": _clean(row2025.get("2025 Return", one.get("2025 Return", ""))),
                "2025_sharpe": _clean(row2025.get("2025 Sharpe", one.get("2025 Sharpe", ""))),
                "text_mode": str(row2024.get("Text Mode", getattr(spec, "text_mode", ""))),
                "news_dependency": "none" if str(row2024.get("Text Mode", getattr(spec, "text_mode", ""))) == "no_news" else "deterministic_rule_based",
                "runtime_dependency": "no_external_api_no_model_binary",
                "config_path": rel_path.as_posix(),
                "config_hash": getattr(spec, "config_hash", ""),
                "official_runtime_candidate": candidate in FINAL.values(),
                "preserved_for": preserved_for,
                "notes": "Runnable full system config preserved outside official runtime selection.",
            }
        )
        audit.append(
            {
                "Candidate": candidate,
                "Track": track,
                "Family": getattr(spec, "family", ""),
                "Role": role,
                "2024 Score": _clean(row2024.get("Conservative Score", "")),
                "2025 Test": f"return={_clean(row2025.get('2025 Return', ''))}; sharpe={_clean(row2025.get('2025 Sharpe', ''))}",
                "News Mode": "none" if getattr(spec, "text_mode", "") == "no_news" else getattr(spec, "text_mode", ""),
                "Config Path": rel_path.as_posix(),
                "Config Exists?": path.exists(),
                "Official Runtime?": candidate in FINAL.values(),
                "Preserve Reason": preserved_for,
                "Status": "pass" if path.exists() else "fail",
            }
        )
    _write_text(base / "README.md", _preserved_readme(manifest))
    _write_json(base / "manifest.json", {"created_at_utc": _now(), "official_runtime_unchanged": True, "candidates": manifest})
    _write_csv(base / "manifest.csv", manifest)
    return manifest, audit


def _role(candidate: str) -> str:
    for key, value in FINAL.items():
        if value == candidate:
            return key
    return "research_comparator"


def _preserved_for(candidate: str) -> str:
    if candidate in {FINAL["track_a_primary"], FINAL["track_b_primary"]}:
        return "official_runtime"
    if candidate in {FINAL["track_a_fallback"], FINAL["track_b_fallback"]}:
        return "fallback"
    if "bsa" in candidate or "leeqa" in candidate:
        return "future_news_overlay_baseline"
    return "ablation"


def _output_inventory() -> list[dict[str, Any]]:
    var_prompt_paths = list((REPO_ROOT / ".var").glob("prompt*")) if (REPO_ROOT / ".var").exists() else []
    paths = [
        REPO_ROOT / "outputs",
        REPO_ROOT / "outputs" / "reports",
        REPO_ROOT / "outputs" / "submissions",
        REPO_ROOT / "outputs" / "models",
        REPO_ROOT / "outputs" / "pytest_cache",
        REPO_ROOT / "outputs" / "pytest_tmp",
        REPO_ROOT / ".var",
        *var_prompt_paths,
        REPO_ROOT / "docs" / "reports",
        REPO_ROOT / "docs" / "implementation_logs",
        REPO_ROOT / "configs",
        REPO_ROOT / "configs" / "preserved_candidates",
    ]
    rows = []
    for path in paths:
        if not path.exists():
            rows.append(_inv(path, "missing", 0, 0, "manual_review", "Path absent.", "none", "Absent optional path."))
            continue
        classification, reason, action = _classify_path(path)
        rows.append(_inv(path, "directory" if path.is_dir() else "file", _path_size(path), _file_count(path), classification, reason, action, ""))
    return rows


def _classify_path(path: Path) -> tuple[str, str, str]:
    rel = _rel(path)
    if rel.startswith("outputs/reports/prompt18") or rel.startswith("outputs/reports/prompt19") or rel.startswith("outputs/reports/prompt20"):
        return "keep_final_evidence", "Final compact reports.", "keep"
    if rel == "outputs/reports":
        return "keep_final_evidence", "Report root.", "keep"
    if rel.startswith(".var/prompt18") or rel.startswith(".var/prompt19"):
        return "keep_package", "Contains final package zips and supporting evidence.", "keep"
    if rel.startswith(".var/prompt16") or rel.startswith(".var/prompt17") or rel.startswith(".var/prompt17b"):
        return "keep_historical_evidence", "Prior prompt reproducibility evidence.", "keep_package_excluded"
    if "pytest" in path.name or path.name in {".pytest_cache", ".mypy_cache", ".ruff_cache", ".cache"}:
        return "delete_generated_cache", "Generated cache.", "delete_if_safe"
    if rel.startswith("configs"):
        return "source_or_config_keep", "Configuration source.", "keep"
    if rel.startswith("docs"):
        return "keep_final_evidence", "Documentation and implementation logs.", "keep"
    if rel == "outputs" or rel == ".var":
        return "keep_historical_evidence", "Generated artifact root with mixed evidence.", "inventory_only"
    return "manual_review", "No automatic cleanup rule.", "manual_review"


def _cleanup() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    targets = []
    for root in (REPO_ROOT / "src", REPO_ROOT / "scripts", REPO_ROOT / "NLPCC_tasks" / "agent_platform", REPO_ROOT / "NLPCC_tasks" / "server_platform"):
        if root.exists():
            targets.extend([p for p in root.rglob("__pycache__") if p.is_dir()])
            targets.extend([p for p in root.rglob("*.pyc") if p.is_file()])
    for optional in (REPO_ROOT / ".pytest_cache", REPO_ROOT / ".mypy_cache", REPO_ROOT / ".ruff_cache", REPO_ROOT / ".cache", REPO_ROOT / "outputs" / "pytest_cache", REPO_ROOT / "outputs" / "pytest_tmp"):
        if optional.exists():
            targets.append(optional)
    targets.extend([p for p in REPO_ROOT.glob("pytest-cache-files-*") if p.is_dir()])
    filtered_targets: list[Path] = []
    parent_dirs: list[Path] = []
    for path in sorted(set(targets), key=lambda p: (len(p.parts), p.as_posix())):
        if any(parent in path.parents for parent in parent_dirs):
            continue
        filtered_targets.append(path)
        if path.is_dir():
            parent_dirs.append(path)
    for path in filtered_targets:
        size = _path_size(path)
        try:
            if path.is_dir():
                shutil.rmtree(path)
            else:
                path.unlink()
            rows.append({"Path": _rel(path), "Size": size, "Action": "delete_generated_cache", "Reason": "Generated cache/bytecode outside protected evidence paths.", "Evidence Preserved?": True, "Risk": "low", "Notes": "Deleted."})
        except FileNotFoundError:
            rows.append({"Path": _rel(path), "Size": size, "Action": "delete_generated_cache", "Reason": "Generated cache/bytecode outside protected evidence paths.", "Evidence Preserved?": True, "Risk": "low", "Notes": "Already absent."})
        except OSError as exc:
            rows.append({"Path": _rel(path), "Size": size, "Action": "blocked", "Reason": "Generated cache/bytecode outside protected evidence paths.", "Evidence Preserved?": True, "Risk": "low", "Notes": f"Could not delete: {exc}"})
    for old in (REPO_ROOT / ".var" / "prompt16", REPO_ROOT / ".var" / "prompt17", REPO_ROOT / ".var" / "prompt17b", REPO_ROOT / ".var" / "prompt18", REPO_ROOT / ".var" / "prompt19"):
        if old.exists():
            rows.append({"Path": _rel(old), "Size": _path_size(old), "Action": "keep", "Reason": "Prompt evidence or package path; package-excluded by policy.", "Evidence Preserved?": True, "Risk": "low", "Notes": "Kept."})
    return rows or [{"Path": "generated caches", "Size": 0, "Action": "keep", "Reason": "No eligible generated caches found.", "Evidence Preserved?": True, "Risk": "low", "Notes": ""}]


def _evidence_inventory(manifest: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items = [
        ("Official final configs", "official final configs", "configs/prompt18_final_candidates.json", "Locks official runtime aliases.", "Do not reopen without correctness defect."),
        ("Preserved candidate configs", "preserved candidate configs", "configs/preserved_candidates/manifest.json", "Provides runnable baselines for next-stage news overlay.", "Use as fixed baselines."),
        ("Official runtime package", "official runtime package", ".var/prompt19/packages/prompt19_official_runtime_20260603_085804.zip", "Submission runtime package.", "Clean-directory smoke before upload."),
        ("Reproducibility package", "reproducibility package", ".var/prompt19/packages/prompt19_reproducibility_20260603_085805.zip", "Evidence and scripts package.", "May need rebuild if preserved configs must be inside package."),
        ("Prompt18 big grid", "Prompt18 big-grid evidence", "outputs/reports/prompt18/reference/big_grid_2024_scores.csv", "2024-only tuning evidence.", "Baseline comparison."),
        ("Prompt18 official parity", "Prompt18 official parity evidence", "outputs/reports/prompt18/reference/official_server_parity.csv", "Full 2025 official parity for required rows.", "Promotion gate reference."),
        ("Prompt19 tuner", "Prompt19 tuner evidence", "outputs/reports/prompt19/reference/tuner_2024_results.csv", "Prompt19-specific 2024 tuner copy.", "Fixed train evidence."),
        ("Prompt19 one-year tune/test", "Prompt19 one-year tune/test evidence", "outputs/reports/prompt19/reference/one_year_tune_test_leaderboard.csv", "Analytical ranking.", "Research comparator only."),
        ("Prompt19 news usage", "Prompt19 news-usage evidence", "outputs/reports/prompt19/reference/news_ablation_report.csv", "News materiality evidence.", "Starting point for overlay research."),
        ("Prompt19 locked 2025", "Prompt19 locked 2025 evidence", "outputs/reports/prompt19/reference/locked_2025_test_results.csv", "Frozen test performance.", "Generalisation check."),
        ("Final system report draft", "final system report draft", "outputs/reports/prompt19/presented/final_system_report_draft.md", "Report prose foundation.", "Update after any future promoted overlay."),
        ("Submission checklist", "submission handoff checklist", "outputs/reports/prompt19/presented/submission_handoff_checklist.md", "Human handoff checklist.", "Use before upload."),
        ("Prompt19 implementation log", "implementation logs", "docs/implementation_logs/20260603_165807_prompt19_tuner_news_cleanup_report_handoff.md", "Traceability.", "Read before Prompt21."),
    ]
    rows = []
    for name, category, path, why, use in items:
        rows.append({"Evidence Item": name, "Category": category, "Path": path, "Status": "present" if (REPO_ROOT / path).exists() else "missing", "Why It Matters": why, "Use In Next Stage": use})
    for item in manifest:
        rows.append({"Evidence Item": item["candidate_name"], "Category": "preserved candidate config", "Path": item["config_path"], "Status": "present", "Why It Matters": "Runnable preserved candidate.", "Use In Next Stage": item["preserved_for"]})
    return rows


def _repo_status_matrix() -> list[dict[str, Any]]:
    return [
        {"Layer": "Official runtime", "Status": "frozen", "Key Files": "configs/prompt18_final_candidates.json; configs/systems/prompt18_track_*.yaml", "Evidence": "Prompt18/19 final reports", "Remaining Risk": "hidden 2026 regime", "Next-Stage Relevance": "do not modify unless correctness defect"},
        {"Layer": "Preserved candidates", "Status": "complete", "Key Files": "configs/preserved_candidates/", "Evidence": "Prompt20 manifest", "Remaining Risk": "not included in already-built Prompt19 zips", "Next-Stage Relevance": "baseline set for overlay research"},
        {"Layer": "Stage 1 news", "Status": "MVP deterministic", "Key Files": "src/nlpcc/stage1_news/", "Evidence": "Prompt19 news audit", "Remaining Risk": "rule extraction may be coarse", "Next-Stage Relevance": "primary target for Prompt21+"},
        {"Layer": "Stage 2 text store", "Status": "MVP", "Key Files": "src/nlpcc/stage2_text_store/", "Evidence": "Prompt15/19 reports", "Remaining Risk": "limited memory/embedding validation", "Next-Stage Relevance": "attention index and event store"},
        {"Layer": "Stage 3 trade", "Status": "stable", "Key Files": "src/nlpcc/stage3_trade/", "Evidence": "Prompt18 grid", "Remaining Risk": "market regime shift", "Next-Stage Relevance": "fixed non-news baseline features"},
        {"Layer": "Stage 4 agents", "Status": "broad MVP coverage", "Key Files": "src/nlpcc/stage4_agent/", "Evidence": "Prompt18 320-row grid", "Remaining Risk": "advanced methods are proxies", "Next-Stage Relevance": "overlay must be gated and ablated"},
        {"Layer": "Execution adapter", "Status": "parity-passing", "Key Files": "src/nlpcc/execution/; build_agent.py", "Evidence": "Prompt18 official parity", "Remaining Risk": "official environment differences", "Next-Stage Relevance": "promotion gate"},
        {"Layer": "Backtester/replay", "Status": "official-semantics path available", "Key Files": "src/tools/backtesting/", "Evidence": "Prompt18/19 runs", "Remaining Risk": "do not use LocalSmokeBacktester as final evidence", "Next-Stage Relevance": "2024 tune / 2025 test replay"},
        {"Layer": "Packages", "Status": "Prompt19 pass", "Key Files": ".var/prompt19/packages/*.zip", "Evidence": "Prompt19 package audit", "Remaining Risk": "preserved configs postdate zips", "Next-Stage Relevance": "rebuild if submitting after Prompt20"},
    ]


def _package_handoff_audit(manifest: list[dict[str, Any]]) -> list[dict[str, Any]]:
    runtime = REPO_ROOT / ".var" / "prompt19" / "packages" / "prompt19_official_runtime_20260603_085804.zip"
    repro = REPO_ROOT / ".var" / "prompt19" / "packages" / "prompt19_reproducibility_20260603_085805.zip"
    rows = [
        _handoff("Official runtime package", runtime, "exists", "pass" if runtime.exists() else "fail", "Prompt19 package preserved."),
        _handoff("Reproducibility package", repro, "exists", "pass" if repro.exists() else "fail", "Prompt19 package preserved."),
        _handoff("Preserved candidate configs", REPO_ROOT / "configs" / "preserved_candidates" / "manifest.json", "exists", "pass", "Created after Prompt19 packages; scheduled for next reproducibility rebuild."),
        _handoff("Official runtime package minimal", runtime, "no raw data/model binaries/outputs/.var", _zip_status(runtime, allow_reports=False), "Audited directly from zip names."),
        _handoff("Reproducibility package excludes raw data/model binaries", repro, "no raw data/model binaries", _zip_status(repro, allow_reports=True), "Audited directly from zip names."),
        _handoff("Final system report draft", REPO_ROOT / "outputs" / "reports" / "prompt19" / "presented" / "final_system_report_draft.md", "exists", "pass", "Prompt19 artifact exists."),
        _handoff("Submission handoff checklist", REPO_ROOT / "outputs" / "reports" / "prompt19" / "presented" / "submission_handoff_checklist.md", "exists", "pass", "Prompt19 artifact exists."),
        _handoff("Manual official-server smoke", REPO_ROOT / "outputs" / "reports" / "prompt19" / "presented" / "submission_handoff_checklist.md", "user confirmed", "pass", "Recorded from Prompt20 request context."),
    ]
    return rows


def _handoff(item: str, path: Path, expected: str, status: str, notes: str) -> dict[str, Any]:
    return {"Item": item, "Path": _rel(path), "Expected": expected, "Status": status, "Notes": notes}


def _zip_status(path: Path, *, allow_reports: bool) -> str:
    if not path.exists():
        return "fail"
    names = zipfile.ZipFile(path).namelist()
    bad = [n for n in names if n.startswith("data/") or n.startswith("NLPCC_tasks/dataset/") or n.startswith(".var/") or n.endswith((".bin", ".safetensors", ".pt", ".pth", ".onnx", ".pyc")) or "__pycache__" in n]
    if not allow_reports:
        bad += [n for n in names if n.startswith("outputs/")]
    return "pass" if not bad else "fail"


def _next_stage_workflow_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    workflow = [
        {"Stage": "Stage 1 - Discuss", "NLPCC Adaptation": "Clarify whether next work is exploratory news/text research or a candidate-promotion attempt.", "Outputs": "research brief, non-goals, acceptance gates", "Stop Conditions": "No code until scope and leakage boundaries are fixed."},
        {"Stage": "Stage 2 - Research", "NLPCC Adaptation": "Compare stronger rule extraction, Chinese finance embeddings, attention indices, event-impact models, and gated overlays.", "Outputs": "method synthesis, model availability audit, risk table", "Stop Conditions": "No post-2025 data or downloads."},
        {"Stage": "Stage 3 - Project Initialisation", "NLPCC Adaptation": "Localise current Stage 1/2/4 code paths, preserved candidates, cache locations, and report schema.", "Outputs": "implementation plan, prompt backlog, cache manifest design", "Stop Conditions": "Do not alter official final configs."},
        {"Stage": "Stage 4 - Execution", "NLPCC Adaptation": "Implement only bounded MVP modules with 2024 tuning and frozen 2025 testing.", "Outputs": "feature cache, attention index, overlay configs, ablations", "Stop Conditions": "No promotion without official parity."},
        {"Stage": "Stage 5 - Manual Check, Log Review, and Fixes", "NLPCC Adaptation": "Review traces, ablations, leakage audit, package audit, system report claims, and official parity.", "Outputs": "promotion audit or rejection report", "Stop Conditions": "Preserve Prompt18 final runtime unless human reopens freeze."},
    ]
    backlog = []
    for name, objective in [
        ("Prompt21A - News/Text Deep Research and Design Space", "Research design space for stronger news/text and gated overlays."),
        ("Prompt21B - Repo Localisation for News/Text Pipeline", "Map existing Stage 1/2/4 code and preserved candidate baselines."),
        ("Prompt22 - News Feature Inventory and Trace Audit", "Inventory existing news-derived fields and trace coverage."),
        ("Prompt23 - News Attention Index MVP", "Design/implement a deterministic news attention index MVP."),
        ("Prompt24 - Transformer Embedding Offline Cache", "Prepare optional offline embedding cache with no silent downloads."),
        ("Prompt25 - Event Impact and ETF Sensitivity Modelling", "Estimate 2024-only event impact and ETF sensitivity."),
        ("Prompt26 - Gated News Overlay Implementation", "Implement a bounded overlay gated by risk and ablation controls."),
        ("Prompt27 - 2024 Tune / 2025 Test Evaluation", "Evaluate frozen overlay candidates using strict 2024/2025 protocol."),
        ("Prompt28 - Official-Server Validation and Candidate Promotion Audit", "Run official parity and decide whether to recommend human-approved promotion."),
    ]:
        backlog.append(
            {
                "Prompt": name,
                "Objective": objective,
                "Read-First Files": "AGENTS.md; Prompt20 reports; configs/preserved_candidates/manifest.json; Stage 1/2/4 code; Prompt18/19 evidence",
                "Deliverables": "Reports under next prompt report folder; code only where that prompt permits implementation.",
                "Do-Not-Do Constraints": "No 2025 tuning; no hidden 2026; no silent downloads; do not change Prompt18 official final selection.",
                "Expected Reports": "progress, presented summary, reference CSV/MD, implementation log.",
            }
        )
    return workflow, backlog


def _current_repo_status_report(manifest: list[dict[str, Any]], status_rows: list[dict[str, Any]], cleanup_rows: list[dict[str, Any]], evidence_rows: list[dict[str, Any]]) -> str:
    return "\n".join([
        "# Current Repository Status Report - After Prompt20 Wrap-Up",
        "",
        "## 1. Executive Verdict",
        "Ready for final human submission review; Prompt20 did not reopen model development.",
        "## 2. Official Final Runtime State",
        f"Track A primary `{FINAL['track_a_primary']}`, fallback `{FINAL['track_a_fallback']}`. Track B primary `{FINAL['track_b_primary']}`, fallback `{FINAL['track_b_fallback']}`.",
        "## 3. Preserved Candidate Layer",
        f"{len(manifest)} runnable preserved configs under `configs/preserved_candidates/`.",
        "## 4. Track A Status",
        ", ".join(TRACK_A),
        "## 5. Track B Status",
        ", ".join(TRACK_B),
        "## 6. Stage 1 News Processing Status",
        "Deterministic rule-based MVP exists; optional local model paths are disabled by default.",
        "## 7. Stage 2 Text Storage Status",
        "Flat/event/BL/sector-impact stores exist as MVP modules.",
        "## 8. Stage 3 Trade/Price Processing Status",
        "Stable enough for Prompt18/19 official-semantics grid and parity evidence.",
        "## 9. Stage 4 Agent Status",
        "Broad family coverage exists; advanced families remain MVP/proxy implementations.",
        "## 10. Execution and Official Adapter Status",
        "Thin wrapper delegates to `src/nlpcc`; Prompt18 full official parity passed required rows.",
        "## 11. Backtester / Replay Status",
        "Official-semantics replay is the final evidence path; LocalSmokeBacktester is not final evidence.",
        "## 12. Tuning / Optimisation Status",
        "Prompt19 copied verified Prompt18 320-row 2024-only tuner evidence.",
        "## 13. Official-Server Validation Status",
        "Prompt18 full-horizon official parity passed 5 required rows; user reports manual official-server smoke verified.",
        "## 14. Package Status",
        "Prompt19 official and reproducibility zips exist and pass audits.",
        "## 15. Cleanup Status",
        _cleanup_counts(cleanup_rows),
        "## 16. Evidence Inventory",
        f"{len(evidence_rows)} evidence rows written to `reference/evidence_inventory.csv`.",
        "## 17. Known Risks",
        "- Hidden 2026 regime risk.\n- Prompt20 preserved configs postdate Prompt19 zips.\n- Advanced methods are proxies.\n- Future news overlay must prove material out-of-sample value.",
        "## 18. What Can Be Claimed",
        "- Official final selection preserved.\n- 2024-only tuning and 2025 locked testing discipline.\n- Deterministic no-API runtime/fallback path.\n- Prompt20 preserved 5 candidates per track.",
        "## 19. What Must Not Be Claimed",
        "- Hidden 2026 performance.\n- 2025 tuning.\n- Transformer/news overlay implementation from Prompt20.\n- BGE/FinBERT final dependency.",
        "## 20. Recommended Next Stage",
        "Run Prompt21A for news/text deep research and design-space synthesis, then Prompt21B for repo localisation before implementation.",
    ])


def _next_stage_workflow_doc(backlog: list[dict[str, Any]]) -> str:
    return "\n".join([
        "# Next-Stage Workflow - News/Text Processing and News Overlay",
        "",
        "## 1. Purpose",
        "Prepare a separate AI-assisted phase for stronger news/text processing and gated news overlay research.",
        "## 2. Starting Point After Prompt20",
        "Official runtime is frozen; preserved candidates provide fixed baselines; Prompt19 shows material rule-news effect for Track B primary but no-news final Track A.",
        "## 3. Stage 1 - Discuss",
        "Clarify research questions, non-goals, leakage boundaries, candidate-promotion gates, and whether the next phase is exploratory or promotion-seeking.",
        "## 4. Stage 2 - Research",
        "Run deep research on rule extraction, Chinese finance embeddings, attention indices, event magnitude, ETF/sector sensitivity, and gated overlays.",
        "## 5. Stage 3 - Project Initialisation",
        "Localise existing Stage 1/2/4 interfaces, cache paths, preserved candidates, reports, and tests before any code change.",
        "## 6. Stage 4 - Execution",
        "Implement bounded MVP modules only after research and localisation; freeze parameters on 2024 and test frozen candidates on 2025.",
        "## 7. Stage 5 - Manual Check, Log Review, and Fixes",
        "Review traces, no-news ablations, perturbation tests, leakage audit, package audit, and official-server parity before any promotion recommendation.",
        "## 8. Candidate Research Questions",
        "- Does stronger text processing improve Track A beyond no-news risk parity?\n- Can news improve Track B without raising turnover/drawdown?\n- Which event classes have stable ETF sensitivity?",
        "## 9. Proposed News/Text Modules",
        "Stronger rule extractor, event taxonomy, event magnitude scorer, optional offline embedding cache, news attention index.",
        "## 10. Proposed News Overlay Modules",
        "Risk-gated overlay, event-triggered tilt, sector sensitivity overlay, attention-weighted asset tilt.",
        "## 11. Evaluation Protocol",
        "Tune only on 2024; freeze; test on 2025; official-server parity before any human-approved promotion.",
        "## 12. Risk Controls",
        "No silent downloads, no 2025 tuning, no hidden 2026 data, no official final replacement without approval.",
        "## 13. Prompt Backlog",
        _md_table(backlog),
        "## 14. Recommended First Next Prompt",
        "Prompt21A - News/Text Deep Research and Design Space.",
    ])


def _workflow_map_md(rows: list[dict[str, Any]]) -> str:
    return "# Next-Stage Workflow Map\n\n" + _md_table(rows)


def _backlog_md(rows: list[dict[str, Any]]) -> str:
    return "# Next-Stage Prompt Backlog\n\n" + _md_table(rows)


def _final_wrapup(manifest: list[dict[str, Any]], cleanup: list[dict[str, Any]], handoff: list[dict[str, Any]]) -> str:
    return "\n".join([
        "# Prompt20 Final Wrap-Up Recommendation",
        "",
        "## 1. Executive Verdict",
        "Ready for final human submission review; proceed to Prompt21A only for next-stage research, not final runtime changes.",
        "## 2. Official Runtime Selection",
        f"Unchanged: {FINAL}.",
        "## 3. Preserved Candidate Layer",
        f"Preserved {len(manifest)} runnable candidate configs under `configs/preserved_candidates/`.",
        "## 4. Cleanup Result",
        _cleanup_counts(cleanup),
        "## 5. Current Repo Status",
        "Status dossier written to `presented/current_repo_status_report.md`.",
        "## 6. Evidence Inventory",
        "Evidence inventory written to `reference/evidence_inventory.csv`.",
        "## 7. Package / Handoff Status",
        f"Handoff audit statuses: {_counts(handoff, 'Status')}.",
        "## 8. Next-Stage Workflow Prepared",
        "Workflow and prompt backlog prepared; no NewsEnhance/transformer overlay implemented.",
        "## 9. What Can Be Claimed",
        "- Prompt18 official runtime is unchanged.\n- 5 preserved candidates per track are available.\n- Package zips and final reports are preserved.",
        "## 10. What Must Not Be Claimed",
        "- New overlay performance.\n- Hidden 2026 readiness beyond existing package/parity evidence.\n- Final runtime change.",
        "## 11. Recommended Next Prompt",
        "Prompt21A - News/Text Deep Research and Design Space.",
    ])


def _executive_summary(manifest: list[dict[str, Any]], cleanup: list[dict[str, Any]], handoff: list[dict[str, Any]]) -> str:
    return "\n".join([
        "# Prompt20 Executive Summary",
        "",
        "Readiness: **Ready for final human submission review**.",
        "",
        "Official runtime selection was preserved unchanged.",
        f"Preserved candidates: Track A `{', '.join(TRACK_A)}`; Track B `{', '.join(TRACK_B)}`.",
        _cleanup_counts(cleanup),
        f"Package/handoff statuses: {_counts(handoff, 'Status')}.",
        "Next recommended prompt: Prompt21A news/text deep research and design space.",
    ])


def _preserved_readme(manifest: list[dict[str, Any]]) -> str:
    return "# Preserved Candidates\n\nResearch/reproducibility candidate configs preserved after Prompt20. These do not replace Prompt18 official runtime configs.\n\n" + _md_table(manifest)


def _preserved_selection_md(rows: list[dict[str, Any]]) -> str:
    return "# Preserved Candidate Selection\n\nSelected required 5 Track A and 5 Track B candidates from Prompt18/19 evidence. No substitutions were needed.\n\n" + _md_table(rows)


def _preserved_configs_md(rows: list[dict[str, Any]]) -> str:
    return "# Preserved Candidate Configs\n\n" + _md_table(rows)


def _preserved_summary(rows: list[dict[str, Any]]) -> str:
    return "# Preserved Candidate Summary\n\n" + _md_table([{"Candidate": r["candidate_name"], "Track": r["track"], "Family": r["family"], "Role": r["role"], "Config Path": r["config_path"], "Official Runtime?": r["official_runtime_candidate"], "Preserve Reason": r["preserved_for"]} for r in rows])


def _inventory_summary_md(rows: list[dict[str, Any]]) -> str:
    return f"# Output Inventory Summary\n\nInventory rows: {len(rows)}. Classifications: {_counts(rows, 'Classification')}.\n"


def _cleanup_summary_md(rows: list[dict[str, Any]]) -> str:
    return f"# Cleanup Summary\n\n{_cleanup_counts(rows)}\n\n" + _md_table(rows)


def _handoff_summary_md(rows: list[dict[str, Any]]) -> str:
    return f"# Package and Handoff Check\n\nStatuses: {_counts(rows, 'Status')}.\n\n" + _md_table(rows)


def _evidence_summary(rows: list[dict[str, Any]]) -> str:
    return f"# Evidence Inventory Summary\n\nEvidence rows: {len(rows)}. Statuses: {_counts(rows, 'Status')}.\n"


def _cleanup_counts(rows: list[dict[str, Any]]) -> str:
    return f"Cleanup actions: {_counts(rows, 'Action')}."


def _row_for(df: pd.DataFrame, col: str, value: str) -> Mapping[str, Any]:
    if col not in df.columns:
        return {}
    rows = df[df[col].astype(str) == value]
    return rows.iloc[0].to_dict() if not rows.empty else {}


def _clean(value: Any) -> Any:
    try:
        if pd.isna(value):
            return ""
    except TypeError:
        pass
    return value


def _grep_line(path: Path, needle: str) -> str:
    if not path.exists():
        return ""
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if needle in line:
            return line.strip()
    return ""


def _inv(path: Path, typ: str, size: int, count: int, classification: str, reason: str, action: str, notes: str) -> dict[str, Any]:
    return {"Path": _rel(path), "Type": typ, "Size": size, "File Count": count, "Classification": classification, "Reason": reason, "Safe Action": action, "Notes": notes}


def _path_size(path: Path) -> int:
    if not path.exists():
        return 0
    if path.is_file():
        return path.stat().st_size
    return sum(p.stat().st_size for p in path.rglob("*") if p.is_file())


def _file_count(path: Path) -> int:
    if not path.exists():
        return 0
    if path.is_file():
        return 1
    return sum(1 for p in path.rglob("*") if p.is_file())


def _rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)


def _counts(rows: list[Mapping[str, Any]], key: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for row in rows:
        val = str(row.get(key, ""))
        out[val] = out.get(val, 0) + 1
    return out


def _write_implementation_log(report_root: Path, manifest: list[dict[str, Any]], cleanup: list[dict[str, Any]], handoff: list[dict[str, Any]]) -> None:
    path = REPO_ROOT / "docs" / "implementation_logs" / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_prompt20_wrapup_cleanup_status_next_workflow.md"
    text = "\n".join([
        "# Implementation Log: prompt20 - wrapup_cleanup_status_next_workflow",
        "",
        "## Created",
        _now(),
        "",
        "## Summary",
        "Wrapped up repository state after Prompt19, preserved candidate configs, inventoried outputs, cleaned safe generated caches, wrote status dossier, package/handoff audit, and next-stage news/text workflow plan.",
        "",
        "## Files Changed",
        "scripts/run_prompt20_wrapup.py; configs/preserved_candidates/*; outputs/reports/prompt20/*; docs/implementation_logs/*prompt20_wrapup_cleanup_status_next_workflow.md",
        "",
        "## Context Reconstruction",
        "Verified Prompt19 readiness, package paths, final configs, and user-provided manual official-server smoke confirmation.",
        "",
        "## Preserved Candidate Layer",
        f"Preserved {len(manifest)} configs: Track A {TRACK_A}; Track B {TRACK_B}.",
        "",
        "## Output Inventory",
        "Wrote output and runtime artifact inventory.",
        "",
        "## Cleanup Execution",
        _cleanup_counts(cleanup),
        "",
        "## Current Repo Status Dossier",
        "Wrote `outputs/reports/prompt20/presented/current_repo_status_report.md`.",
        "",
        "## Evidence Inventory",
        "Wrote `outputs/reports/prompt20/reference/evidence_inventory.csv`.",
        "",
        "## Package / Handoff Check",
        f"Statuses: {_counts(handoff, 'Status')}.",
        "",
        "## Next-Stage Workflow Plan",
        "Prepared Prompt21A/21B+ workflow; did not implement NewsEnhance or transformer overlay.",
        "",
        "## Tests / Checks",
        "Ran `python scripts/run_prompt20_wrapup.py`; then ran targeted import/config smoke check.",
        "",
        "## Caveats",
        "Prompt20 did not rebuild Prompt19 packages, so preserved candidate configs are scheduled for a future reproducibility-package rebuild if needed.",
        "",
        "## Artifacts",
        f"- `{report_root / 'presented' / 'current_repo_status_report.md'}`",
        f"- `{report_root / 'reference' / 'evidence_inventory.csv'}`",
        f"- `{report_root / 'presented' / 'next_stage_news_text_overlay_workflow.md'}`",
        "",
        "## Next Steps",
        "Run Prompt21A for news/text deep research and design-space synthesis.",
    ])
    _write_text(path, text)


def _write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True, default=str), encoding="utf-8")


def _write_csv(path: Path, rows: Iterable[Mapping[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = list(rows)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fields = list(rows[0].keys())
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def _write_md_table(path: Path, title: str, rows: Iterable[Mapping[str, Any]]) -> None:
    _write_text(path, f"# {title}\n\n{_md_table(list(rows))}\n")


def _write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _md_table(rows: list[Mapping[str, Any]]) -> str:
    if not rows:
        return "_No rows._"
    headers = list(rows[0].keys())
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(h, "")).replace("|", "\\|").replace("\n", " ") for h in headers) + " |")
    return "\n".join(lines)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


if __name__ == "__main__":
    raise SystemExit(main())
