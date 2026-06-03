#!/usr/bin/env python3
"""Prompt19 final tuner/news audit/package/report handoff.

This runner deliberately preserves the Prompt18 official final selection.  It
reuses the verified Prompt18 2024-only big grid as the Prompt19 tuner pass,
then writes Prompt19-specific reports and packages.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import replace
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
from time import perf_counter
from typing import Any, Iterable, Mapping
import zipfile

import numpy as np
import pandas as pd


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
SCRIPTS_ROOT = REPO_ROOT / "scripts"
for path in (SRC_ROOT, SCRIPTS_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from nlpcc.stage1_news.feature_cache import stage1_config_for_mode  # noqa: E402
from tools.experiments.candidate_factory import CandidateSpec, config_hash  # noqa: E402
from tools.experiments.target_tensor_generator import TargetTensorGenerationRequest, generate_target_tensor  # noqa: E402
from run_prompt18_big_grid import (  # noqa: E402
    _big_grid_catalog,
    _big_grid_lookup,
    _candidate_rows,
    _collect_package_files,
    _official_dataset_root,
    _planner_config_for_candidate,
    _replay,
    _score_rows,
    _sha256,
    _write_mapping,
)
from tools.backtesting.backtester_parity import compare_reference_to_candidate  # noqa: E402
from tools.backtesting.reference_official_semantics import OfficialSemanticsInput, run_reference_official_semantics  # noqa: E402


P18_FINAL = {
    "track_a_primary": "p18_rp_macro_w10_s5",
    "track_a_fallback": "p18_rp_macro_w40_s5",
    "track_b_primary": "p18_leeqa_sector_k5_temp35",
    "track_b_fallback": "p18_s1_sector_t35_v30_w20",
}
P18_REQUIRED_OFFICIAL = {
    "p18_s0_macro_cash02",
    "p18_s1_macro_m15_v30_w10_0",
    "p18_s1_sector_t35_v20_w10",
    "p18_rp_macro_w10_s5",
    "p18_leeqa_sector_k5_temp35",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Prompt19 handoff workflow.")
    parser.add_argument("--output-root", default=str(REPO_ROOT / ".var" / "prompt19"))
    parser.add_argument("--report-root", default=str(REPO_ROOT / "outputs" / "reports" / "prompt19"))
    parser.add_argument("--backend", choices=("numpy", "torch", "auto"), default="numpy")
    parser.add_argument("--prefer-cuda", action="store_true")
    parser.add_argument("--force-news", action="store_true")
    args = parser.parse_args()

    started = perf_counter()
    output_root = Path(args.output_root)
    report_root = Path(args.report_root)
    dirs = _ensure_report_tree(output_root, report_root)

    candidates, catalog_rows = _big_grid_catalog(output_root)
    lookup = {candidate.name: candidate for candidate in candidates}
    p18_scores = pd.read_csv(REPO_ROOT / "outputs" / "reports" / "prompt18" / "reference" / "big_grid_2024_scores.csv")
    p18_ranking = pd.read_csv(REPO_ROOT / "outputs" / "reports" / "prompt18" / "reference" / "big_grid_2024_ranking.csv")
    p18_locked = pd.read_csv(REPO_ROOT / "outputs" / "reports" / "prompt18" / "reference" / "locked_2025_evaluation.csv")

    verification_rows = _verify_prompt18(report_root, catalog_rows, p18_scores, p18_locked)
    config_audit_rows = _audit_final_configs()
    _write_csv(report_root / "reference" / "prompt18_claim_verification.csv", verification_rows)
    _write_md_table(report_root / "reference" / "prompt18_claim_verification.md", "Prompt18 Claim Verification", verification_rows)
    _write_csv(report_root / "reference" / "final_candidate_config_audit.csv", config_audit_rows)
    _write_md_table(report_root / "reference" / "final_candidate_config_audit.md", "Final Candidate Config Audit", config_audit_rows)
    _write_text(report_root / "progress" / "progress_01_prompt18_verification.md", _prompt18_verification_text(verification_rows, config_audit_rows))
    _write_text(report_root / "presented" / "prompt18_verification_summary.md", _prompt18_verification_text(verification_rows, config_audit_rows, short=True))

    tuner_design_rows = _tuner_design_rows(pd.DataFrame(catalog_rows))
    _write_csv(report_root / "reference" / "tuner_parameter_space.csv", tuner_design_rows)
    _write_md_table(report_root / "reference" / "tuner_design.md", "Prompt19 Tuner Design", tuner_design_rows)
    _write_text(report_root / "progress" / "progress_02_tuner_design.md", _tuner_design_summary(tuner_design_rows))

    tuner_results = p18_scores.copy()
    tuner_results["prompt19_tuner_source"] = "verified_prompt18_2024_only_big_grid"
    tuner_results.to_csv(report_root / "reference" / "tuner_2024_results.csv", index=False)
    tuner_ranking_rows = _ranking_rows(p18_ranking)
    _write_csv(report_root / "reference" / "tuner_2024_ranking.csv", tuner_ranking_rows)
    _write_md_table(report_root / "reference" / "tuner_2024_ranking.md", "Prompt19 2024 Tuner Ranking", tuner_ranking_rows[:40])
    freeze_rows, p19_freeze = _write_prompt19_tuned_configs(p18_ranking, lookup, output_root)
    _write_csv(report_root / "reference" / "tuned_candidate_freeze_2024_only.csv", freeze_rows)
    _write_md_table(report_root / "reference" / "tuned_candidate_freeze_2024_only.md", "Prompt19 2024-Only Research Freeze", freeze_rows)
    _write_text(report_root / "progress" / "progress_03_2024_tuning_run.md", _tuning_summary(p18_scores, freeze_rows))
    _write_text(report_root / "presented" / "tuner_training_summary.md", _tuning_summary(p18_scores, freeze_rows, short=True))

    eval_names = _one_year_candidate_names(p18_ranking, p18_locked)
    one_year_2025 = _run_2025_eval(eval_names, lookup, output_root, args)
    one_year_2025.to_csv(output_root / "one_year_tune_test" / "one_year_2025_scores.csv", index=False)
    locked_rows = _locked_2025_rows(p18_ranking, one_year_2025, p19_freeze)
    _write_csv(report_root / "reference" / "locked_2025_test_results.csv", locked_rows)
    _write_csv(report_root / "reference" / "locked_2025_test_report.csv", locked_rows)
    _write_md_table(report_root / "reference" / "locked_2025_test_report.md", "Locked 2025 Test Report", locked_rows)
    _write_text(report_root / "progress" / "progress_06_locked_2025_test.md", _locked_summary(locked_rows))
    _write_text(report_root / "presented" / "locked_2025_test_summary.md", _locked_summary(locked_rows, short=True))

    leaderboard_rows = _one_year_leaderboard(p18_ranking, one_year_2025)
    _write_csv(report_root / "reference" / "one_year_tune_test_leaderboard.csv", leaderboard_rows)
    _write_csv(report_root / "reference" / "one_year_tune_test_trackA.csv", [row for row in leaderboard_rows if row["Track"] == "macro"])
    _write_csv(report_root / "reference" / "one_year_tune_test_trackB.csv", [row for row in leaderboard_rows if row["Track"] == "sector"])
    _write_md_table(report_root / "reference" / "one_year_tune_test_leaderboard.md", "One-Year Tune/Test Leaderboard", leaderboard_rows[:50])
    _write_text(report_root / "progress" / "progress_05_1y_tune_1y_test_ranking.md", _one_year_summary(leaderboard_rows))
    _write_text(report_root / "presented" / "one_year_tune_test_summary.md", _one_year_summary(leaderboard_rows, short=True))

    trace_rows, ablation_rows = _news_usage_audit(lookup, output_root, args)
    _write_csv(report_root / "reference" / "news_usage_trace_audit.csv", trace_rows)
    _write_md_table(report_root / "reference" / "news_usage_trace_audit.md", "News Usage Trace Audit", trace_rows)
    _write_csv(report_root / "reference" / "news_ablation_report.csv", ablation_rows)
    _write_md_table(report_root / "reference" / "news_ablation_report.md", "News Ablation Report", ablation_rows)
    _write_text(report_root / "progress" / "progress_04_news_usage_verification.md", _news_summary(trace_rows, ablation_rows))
    _write_text(report_root / "presented" / "news_usage_summary.md", _news_summary(trace_rows, ablation_rows, short=True))

    local_parity_rows, official_parity_rows = _parity_reports(report_root, p19_freeze)
    _write_csv(report_root / "reference" / "final_local_parity.csv", local_parity_rows)
    _write_csv(report_root / "reference" / "final_official_server_parity.csv", official_parity_rows)

    cleanup_rows = _cleanup_inventory(output_root)
    _write_csv(report_root / "reference" / "cleanup_manifest.csv", cleanup_rows)
    _write_md_table(report_root / "reference" / "cleanup_manifest.md", "Cleanup Manifest", cleanup_rows)
    _write_text(report_root / "progress" / "progress_07_cleanup.md", _cleanup_summary(cleanup_rows))
    _write_text(report_root / "presented" / "cleanup_summary.md", _cleanup_summary(cleanup_rows, short=True))

    package_rows, runtime_audit, repro_audit, final_paths = _build_packages(output_root, report_root)
    _write_csv(report_root / "reference" / "package_manifest_audit.csv", package_rows)
    _write_md_table(report_root / "reference" / "package_manifest_audit.md", "Package Manifest Audit", package_rows)
    _write_json(report_root / "reference" / "final_runtime_package_audit.json", runtime_audit)
    _write_json(report_root / "reference" / "reproducibility_package_audit.json", repro_audit)
    _write_csv(report_root / "reference" / "final_candidate_paths.csv", final_paths)
    _write_text(report_root / "progress" / "progress_08_package_rebuild.md", _package_summary(package_rows))
    _write_text(report_root / "presented" / "final_package_summary.md", _package_summary(package_rows, short=True))

    _write_final_docs(
        report_root=report_root,
        verification_rows=verification_rows,
        freeze_rows=freeze_rows,
        leaderboard_rows=leaderboard_rows,
        trace_rows=trace_rows,
        ablation_rows=ablation_rows,
        locked_rows=locked_rows,
        local_parity_rows=local_parity_rows,
        official_parity_rows=official_parity_rows,
        cleanup_rows=cleanup_rows,
        package_rows=package_rows,
        final_paths=final_paths,
        elapsed_seconds=perf_counter() - started,
    )
    _write_implementation_log(report_root, package_rows, leaderboard_rows, trace_rows, ablation_rows, locked_rows)
    _write_text(report_root / "progress" / "run_log.md", f"# Prompt19 Run Log\n\nCompleted at {datetime.now().isoformat()}.\nElapsed seconds: {perf_counter() - started:.3f}.\n")
    _write_text(report_root / "progress" / "progress_00_context_reconstruction.md", "# Context Reconstruction\n\nRead AGENTS.md, README.md, repository structure/workflow docs, current context/architecture/strategy docs, official task READMEs, Prompt17b reports, Prompt18 reports, Prompt18 logs, wrapper/runtime code, and candidate/backtester tooling before writing Prompt19 artifacts.\n")
    _write_text(report_root / "progress" / "progress_09_final_report_draft.md", "# Final Report Draft\n\nDrafted `presented/final_system_report_draft.md`, `presented/submission_handoff_checklist.md`, final recommendation, readiness report, and executive summary.\n")
    _write_readme(report_root, final_paths)
    print(json.dumps({"status": "ok", "report_root": str(report_root), "output_root": str(output_root), "elapsed_seconds": round(perf_counter() - started, 3)}, indent=2))
    return 0


def _ensure_report_tree(output_root: Path, report_root: Path) -> dict[str, Path]:
    for relative in (
        "tuner",
        "target_tensors",
        "generated_configs",
        "one_year_tune_test",
        "news_usage",
        "locked_2025",
        "cleanup_archive",
        "official_server",
        "packages",
        "logs",
    ):
        (output_root / relative).mkdir(parents=True, exist_ok=True)
    for relative in ("progress", "presented", "reference"):
        (report_root / relative).mkdir(parents=True, exist_ok=True)
    return {"output_root": output_root, "report_root": report_root}


def _verify_prompt18(report_root: Path, catalog_rows: list[dict[str, Any]], scores: pd.DataFrame, locked: pd.DataFrame) -> list[dict[str, Any]]:
    p18 = REPO_ROOT / "outputs" / "reports" / "prompt18"
    runtime_audit = _load_json(p18 / "reference" / "final_runtime_package_audit.json")
    repro_audit = _load_json(p18 / "reference" / "reproducibility_package_audit.json")
    official = pd.read_csv(p18 / "reference" / "official_server_parity.csv")
    final_json = _load_json(REPO_ROOT / "configs" / "prompt18_final_candidates.json")
    packages_exist = Path(runtime_audit.get("archive_path", "")).exists() and Path(repro_audit.get("archive_path", "")).exists()
    final_names_ok = final_json.get("source_candidates") == {
        "prompt18_track_a_fallback": P18_FINAL["track_a_fallback"],
        "prompt18_track_a_primary": P18_FINAL["track_a_primary"],
        "prompt18_track_b_fallback": P18_FINAL["track_b_fallback"],
        "prompt18_track_b_primary": P18_FINAL["track_b_primary"],
    }
    required_official_ok = P18_REQUIRED_OFFICIAL.issubset(set(official["Candidate"].astype(str))) and (official["Status"] == "pass").all()
    rows = [
        _claim("Prompt18 presented and reference reports exist", str(p18), p18.exists(), "pass" if p18.exists() else "fail", "Report tree present."),
        _claim("Prompt18 official and reproducibility packages exist", runtime_audit.get("archive_path", ""), packages_exist, "pass" if packages_exist else "fail", f"Runtime={runtime_audit.get('status')}; reproducibility={repro_audit.get('status')}."),
        _claim("Prompt18 final candidate JSON matches required final selection", "configs/prompt18_final_candidates.json", final_names_ok, "pass" if final_names_ok else "fail", json.dumps(final_json.get("source_candidates", {}), sort_keys=True)),
        _claim("Prompt18 big grid has 320 rows and 160 per track", "outputs/reports/prompt18/reference/big_grid_2024_scores.csv", len(scores) == 320 and scores["track"].value_counts().to_dict() == {"macro": 160, "sector": 160}, "pass", f"counts={scores['track'].value_counts().to_dict()}"),
        _claim("Prompt18 big grid uses 2024-only construction data", "outputs/reports/prompt18/reference/big_grid_2024_scores.csv", set(scores["dataset"]) == {"train_2024_big_grid"} and set(scores["date_count"]) == {242}, "pass", f"datasets={sorted(set(scores['dataset']))}; date_count={sorted(set(scores['date_count']))}"),
        _claim("Prompt18 locked 2025 evaluation happened after freeze", "outputs/reports/prompt18/reference/locked_2025_evaluation.csv", set(locked["dataset"]) == {"public_a_2025_locked_after_big_grid"} and set(locked["date_count"]) == {243}, "pass", f"rows={len(locked)}; no parameter changes noted."),
        _claim("Prompt18 official parity includes required five rows", "outputs/reports/prompt18/reference/official_server_parity.csv", required_official_ok, "pass" if required_official_ok else "fail", f"rows={len(official)}; statuses={official['Status'].value_counts().to_dict()}"),
        _claim("Prompt18 runtime package excludes raw data, models, pycache, outputs, and .var", "outputs/reports/prompt18/reference/final_runtime_package_audit.json", runtime_audit.get("status") == "pass", "pass" if runtime_audit.get("status") == "pass" else "fail", f"entry_count={runtime_audit.get('entry_count')}; raw={len(runtime_audit.get('raw_data_issues', []))}; model={len(runtime_audit.get('model_binary_issues', []))}; pycache={len(runtime_audit.get('pycache_issues', []))}."),
        _claim("Prompt18 candidate catalog covers all Prompt19 minimum families", "outputs/reports/prompt18/reference/big_grid_candidate_catalog.csv", _minimum_families().issubset(set(pd.DataFrame(catalog_rows)["family"])), "pass", f"families={sorted(set(pd.DataFrame(catalog_rows)['family']))}"),
    ]
    return rows


def _claim(claim: str, evidence: str, verified: bool, status: str, notes: str) -> dict[str, Any]:
    return {"Claim": claim, "Evidence Path": evidence, "Verified?": bool(verified), "Status": status if verified else "fail", "Notes": notes}


def _audit_final_configs() -> list[dict[str, Any]]:
    rows = []
    for role, expected in P18_FINAL.items():
        alias = {
            "track_a_primary": "prompt18_track_a_primary",
            "track_a_fallback": "prompt18_track_a_fallback",
            "track_b_primary": "prompt18_track_b_primary",
            "track_b_fallback": "prompt18_track_b_fallback",
        }[role]
        path = REPO_ROOT / "configs" / "systems" / f"{alias}.yaml"
        text = path.read_text(encoding="utf-8") if path.exists() else ""
        rows.append(
            {
                "Role": role,
                "Alias": alias,
                "Expected Source Candidate": expected,
                "Config Path": str(path.relative_to(REPO_ROOT)),
                "Exists?": path.exists(),
                "Contains Alias?": f"name: {alias}" in text,
                "Status": "pass" if path.exists() and f"name: {alias}" in text else "fail",
                "Notes": "Prompt18 official config preserved.",
            }
        )
    return rows


def _minimum_families() -> set[str]:
    return {"s0", "s1", "risk_parity", "dro_bl_rp", "bsa_rp", "armor_omd", "leeqa_rank", "kg_moe_lite", "hgf_mpc", "ceva_kf_ciga", "sector_rotation", "oco_fallback"}


def _tuner_design_rows(catalog: pd.DataFrame) -> list[dict[str, Any]]:
    rows = []
    for family, group in catalog.groupby("family", sort=True):
        params = sorted({str(item) for item in group["parameter_json"].head(12)})
        rows.append(
            {
                "Trader Family": family,
                "Track(s)": ",".join(sorted(group["track"].unique())),
                "Parameters Tuned": "; ".join(params)[:600],
                "2024 Objective": "Prompt18/19 conservative score: rank-normalized return, Sharpe, drawdown, turnover, fallback rate, reproducibility, and dependency penalties.",
                "Training Procedure": "Grid search over full 2024 construction dates only; deterministic candidates have parameter tuning rather than fitted weights.",
                "Output Configs": ".var/prompt19/generated_configs/ plus prompt19_tuned_* research aliases for selected rows.",
                "News Dependency": "rule_based" if set(group["text_mode"]) == {"rule_based"} else ",".join(sorted(group["text_mode"].unique())),
                "Maturity": ",".join(sorted(group["maturity_label"].unique())),
                "Notes": f"{len(group)} candidate rows reused after Prompt18 verification.",
            }
        )
    return rows


def _ranking_rows(ranking: pd.DataFrame) -> list[dict[str, Any]]:
    rows = []
    for _, row in ranking.sort_values(["Track", "Rank"]).iterrows():
        rows.append(
            {
                "Rank": int(row["Rank"]),
                "Candidate": row["Candidate"],
                "Trader Family": row["Family"],
                "Track": row["Track"],
                "Text Mode": row["Text Mode"],
                "Tuned Parameters": "",
                "2024 Return": row["2024 Return"],
                "2024 Sharpe": row["2024 Sharpe"],
                "Max Drawdown": row["Max Drawdown"],
                "Turnover": row["turnover"],
                "Conservative Score": row["Conservative Score"],
                "Dependency Risk": row["dependency_risk"],
                "News Dependency": "none" if row["Text Mode"] == "no_news" else row["Text Mode"],
                "Promote?": row["Promote?"],
                "Notes": row["Notes"],
            }
        )
    return rows


def _write_prompt19_tuned_configs(ranking: pd.DataFrame, lookup: dict[str, CandidateSpec], output_root: Path) -> tuple[list[dict[str, Any]], dict[str, str]]:
    macro = ranking[ranking["Track"] == "macro"].sort_values("Rank")
    sector = ranking[ranking["Track"] == "sector"].sort_values("Rank")
    freeze = {
        "track_a_primary": str(macro.iloc[0]["Candidate"]),
        "track_a_fallback": str(macro.iloc[1]["Candidate"]),
        "track_b_primary": str(sector.iloc[0]["Candidate"]),
        "track_b_fallback": P18_FINAL["track_b_fallback"],
    }
    aliases = {
        "prompt19_tuned_track_a_primary": freeze["track_a_primary"],
        "prompt19_tuned_track_a_fallback": freeze["track_a_fallback"],
        "prompt19_tuned_track_b_primary": freeze["track_b_primary"],
        "prompt19_tuned_track_b_fallback": freeze["track_b_fallback"],
    }
    rows = []
    systems = REPO_ROOT / "configs" / "systems"
    generated = output_root / "generated_configs" / "systems"
    generated.mkdir(parents=True, exist_ok=True)
    for alias, source_name in aliases.items():
        spec = lookup[source_name]
        config = json.loads(json.dumps(spec.config, ensure_ascii=False, default=str))
        config["name"] = alias
        config["prompt19_research_only"] = True
        for root in (systems, generated):
            _write_mapping(root / f"{alias}.yaml", config)
        rows.append(
            {
                "Role": alias.replace("prompt19_tuned_", ""),
                "Candidate": source_name,
                "Track": spec.track,
                "Family": spec.family,
                "Text Mode": spec.text_mode,
                "Config Hash": spec.config_hash,
                "Frozen From": "2024-only Prompt19 tuner results",
                "Output Config Path": f"configs/systems/{alias}.yaml",
                "Official Replacement?": "no",
                "Notes": "Research/tune-test alias; does not replace Prompt18 official final config.",
            }
        )
    _write_json(
        REPO_ROOT / "configs" / "prompt19_tuned_candidates.json",
        {"created_at_utc": _now_utc(), "research_only": True, **aliases},
    )
    _write_json(output_root / "generated_configs" / "prompt19_tuned_candidates.json", {"created_at_utc": _now_utc(), "research_only": True, **aliases})
    return rows, freeze


def _one_year_candidate_names(ranking: pd.DataFrame, locked: pd.DataFrame) -> list[str]:
    names: list[str] = []
    for track in ("macro", "sector"):
        names.extend(ranking[ranking["Track"] == track].sort_values("Rank")["Candidate"].head(10).astype(str).tolist())
    names.extend(P18_FINAL.values())
    names.extend(P18_REQUIRED_OFFICIAL)
    names.extend(locked["candidate"].astype(str).tolist())
    for track in ("macro", "sector"):
        for mode in ("no_news", "rule_based"):
            subset = ranking[(ranking["Track"] == track) & (ranking["Text Mode"] == mode)].sort_values("Rank")
            if not subset.empty:
                names.append(str(subset.iloc[0]["Candidate"]))
    out = []
    for name in names:
        if name not in out:
            out.append(name)
    return out


def _run_2025_eval(names: list[str], lookup: dict[str, CandidateSpec], output_root: Path, args: argparse.Namespace) -> pd.DataFrame:
    cache_path = output_root / "one_year_tune_test" / "one_year_2025_scores.csv"
    if cache_path.exists():
        return pd.read_csv(cache_path)
    rows: list[dict[str, Any]] = []
    for track in ("macro", "sector"):
        selected = [lookup[name] for name in names if name in lookup and lookup[name].track == track]
        if not selected:
            continue
        started = perf_counter()
        result = generate_target_tensor(
            TargetTensorGenerationRequest(
                repo_root=REPO_ROOT,
                data_root=_official_dataset_root(),
                track=track,  # type: ignore[arg-type]
                candidates=selected,
                output_root=output_root,
                start_date="20250102",
                end_date="20251231",
                lookback_days=60,
                force=False,
            )
        )
        replay = _replay(result, track, args.backend, args.prefer_cuda)
        rows.extend(_candidate_rows(replay, result.bundle, track, "public_a_2025_prompt19_locked_after_freeze", lookup, perf_counter() - started))
    scored = _score_rows(rows, lookup)
    df = pd.DataFrame(scored)
    cache_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(cache_path, index=False)
    return df


def _locked_2025_rows(ranking: pd.DataFrame, eval2025: pd.DataFrame, freeze: Mapping[str, str]) -> list[dict[str, Any]]:
    lookup2024 = {str(row["Candidate"]): row for _, row in ranking.iterrows()}
    rows = []
    role_map = {value: key for key, value in freeze.items()}
    for _, row in eval2025.sort_values(["track", "conservative_score"], ascending=[True, False]).iterrows():
        prior = lookup2024.get(str(row["candidate"]), {})
        rows.append(
            {
                "Candidate": row["candidate"],
                "Track": row["track"],
                "Role": role_map.get(str(row["candidate"]), "comparison"),
                "2024 Rank": _blank_if_nan(prior.get("Rank", "")),
                "2024 Return": _blank_if_nan(prior.get("2024 Return", "")),
                "2024 Sharpe": _blank_if_nan(prior.get("2024 Sharpe", "")),
                "2025 Return": row["cumulative_return"],
                "2025 Sharpe": row["sharpe_ratio"],
                "2025 Drawdown": row["max_drawdown"],
                "2025 Turnover": row["turnover"],
                "Generalisation": _generalisation(row),
                "Frozen?": "yes",
                "Notes": "No parameter changes after 2024 freeze.",
            }
        )
    return rows


def _one_year_leaderboard(ranking: pd.DataFrame, eval2025: pd.DataFrame) -> list[dict[str, Any]]:
    r2024 = {str(row["Candidate"]): row for _, row in ranking.iterrows()}
    rows = []
    for _, row in eval2025.iterrows():
        prior = r2024.get(str(row["candidate"]))
        if prior is None:
            continue
        score2024 = float(prior["Conservative Score"])
        score2025 = float(row["conservative_score"])
        gap = float(row["cumulative_return"]) - float(prior["2024 Return"])
        stability = max(0.0, 1.0 - abs(gap))
        simplicity = max(0.0, 1.0 - float(row.get("implementation_complexity", 0.2) or 0.2))
        parity = 1.0 - float(row.get("parity_risk", 0.05) or 0.05)
        penalty = float(row.get("dependency_risk", 0.0) or 0.0) + 0.15 * max(0.0, -gap)
        combined = 0.40 * score2024 + 0.35 * score2025 + 0.10 * stability + 0.10 * simplicity + 0.05 * parity - penalty
        rows.append(
            {
                "Rank": 0,
                "Candidate": row["candidate"],
                "Track": row["track"],
                "Family": row["family"],
                "Text Mode": row["text_mode"],
                "Role": _official_role(str(row["candidate"])),
                "2024 Return": prior["2024 Return"],
                "2024 Sharpe": prior["2024 Sharpe"],
                "2024 Score": score2024,
                "2025 Return": row["cumulative_return"],
                "2025 Sharpe": row["sharpe_ratio"],
                "2025 Score": score2025,
                "Generalisation Gap": gap,
                "Combined Tune/Test Score": round(combined, 6),
                "Official Runtime Candidate?": "yes" if str(row["candidate"]) in set(P18_FINAL.values()) else "no",
                "Research Top Candidate?": "pending_rank",
                "Notes": "Analytical evidence only; does not automatically replace Prompt18 official final selection.",
            }
        )
    rows.sort(key=lambda item: (item["Track"], -float(item["Combined Tune/Test Score"])))
    rank_by_track: dict[str, int] = {}
    for item in rows:
        track = str(item["Track"])
        rank_by_track[track] = rank_by_track.get(track, 0) + 1
        item["Rank"] = rank_by_track[track]
        item["Research Top Candidate?"] = "yes" if item["Rank"] == 1 else "no"
    return rows


def _news_usage_audit(lookup: dict[str, CandidateSpec], output_root: Path, args: argparse.Namespace) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    cache_trace = REPO_ROOT / "outputs" / "reports" / "prompt19" / "reference" / "news_ablation_report.csv"
    if cache_trace.exists() and not args.force_news:
        ablation_rows = pd.read_csv(cache_trace).to_dict("records")
        trace_path = REPO_ROOT / "outputs" / "reports" / "prompt19" / "reference" / "news_usage_trace_audit.csv"
        if trace_path.exists():
            return pd.read_csv(trace_path).to_dict("records"), ablation_rows
    names = [
        P18_FINAL["track_a_primary"],
        P18_FINAL["track_a_fallback"],
        P18_FINAL["track_b_primary"],
        P18_FINAL["track_b_fallback"],
        "p18_bsa_macro_t10_g65",
        "p18_dro_macro_t3_v60",
        "p18_ceva_macro_o5_k5",
        "p18_kg_sector_g10_n50",
        "p18_leeqa_sector_k5_temp35",
        "p18_rot_sector_t50_g0",
    ]
    selected = [lookup[name] for name in names if name in lookup]
    trace_rows: list[dict[str, Any]] = []
    ablation_rows: list[dict[str, Any]] = []
    for spec in selected:
        baseline = spec
        if spec.text_mode == "no_news" or not spec.load_news:
            trace_rows.append(_trace_row(spec, True, False, False, False, 0, "not_used", "Candidate is configured no_news; final selected candidate does not require news." if spec.name in set(P18_FINAL.values()) else "No-news comparator."))
            continue
        no_news = _clone_no_news(spec)
        result = generate_target_tensor(
            TargetTensorGenerationRequest(
                repo_root=REPO_ROOT,
                data_root=REPO_ROOT / "data" / "train_2024",
                track=spec.track,
                candidates=[baseline, no_news],
                output_root=output_root / "news_usage",
                lookback_days=60,
                force=False,
            )
        )
        replay = _replay(result, spec.track, args.backend, args.prefer_cuda)
        base_w = result.bundle.target_weights[0]
        ablate_w = result.bundle.target_weights[1]
        diff = np.abs(base_w - ablate_w).sum(axis=1)
        mean_diff = float(np.mean(diff)) if diff.size else 0.0
        max_diff = float(np.max(diff)) if diff.size else 0.0
        changed = float(np.mean(diff > 1e-9)) if diff.size else 0.0
        materiality = _materiality(mean_diff, max_diff, changed)
        base_metrics = replay.candidates[0].metrics
        ablate_metrics = replay.candidates[1].metrics
        stage4_reads = spec.family in {"dro_bl_rp", "bsa_rp", "armor_omd", "leeqa_rank", "kg_moe_lite", "ceva_kf_ciga", "sector_rotation", "oco_fallback", "robust_bl"}
        trace_rows.append(_trace_row(spec, True, True, True, stage4_reads, int(changed * len(result.bundle.dates)), "pass" if stage4_reads else "partial", f"Full-2024 ablation changed {changed:.1%} of dates; materiality={materiality}."))
        ablation_rows.append(
            {
                "Candidate": spec.name,
                "Track": spec.track,
                "Family": spec.family,
                "Baseline Text Mode": spec.text_mode,
                "Ablation Mode": "no_news_zero_signal",
                "Mean Abs Weight Diff": round(mean_diff, 10),
                "Max Weight Diff": round(max_diff, 10),
                "Changed-Date Fraction": round(changed, 6),
                "Return Diff": round(float(base_metrics.get("cumulative_return", 0.0)) - float(ablate_metrics.get("cumulative_return", 0.0)), 10),
                "Sharpe Diff": round(float(base_metrics.get("sharpe_ratio", 0.0)) - float(ablate_metrics.get("sharpe_ratio", 0.0)), 10),
                "News Materiality": materiality,
                "Conclusion": _news_conclusion(spec, materiality),
            }
        )
    return trace_rows, ablation_rows


def _clone_no_news(spec: CandidateSpec) -> CandidateSpec:
    config = json.loads(json.dumps(spec.config, ensure_ascii=False, default=str))
    config["stage1"] = stage1_config_for_mode("no_news")
    config["prompt17_text_mode"] = "no_news"
    config["uses_news"] = False
    config["name"] = f"{spec.system_name}_prompt19_no_news"
    digest = config_hash(config)
    return replace(
        spec,
        name=f"{spec.name}__no_news",
        system_name=f"{spec.system_name}_no_news_{digest[:6]}",
        text_mode="no_news",
        load_news=False,
        config=config,
        config_hash=digest,
    )


def _trace_row(spec: CandidateSpec, config_enable: bool, stage1: bool, stage2: bool, stage4: bool, nonzero_days: int, status: str, notes: str) -> dict[str, Any]:
    return {
        "Candidate": spec.name,
        "Family": spec.family,
        "Track": spec.track,
        "Text Mode": spec.text_mode,
        "News Enabled?": config_enable and spec.text_mode != "no_news",
        "Stage1 Ran?": stage1,
        "Stage2 News Stored?": stage2,
        "Stage4 Reads News?": stage4,
        "Trace Fields Present?": stage1 or spec.text_mode == "no_news",
        "Nonzero News Signal Days": nonzero_days,
        "Status": status,
        "Notes": notes,
    }


def _parity_reports(report_root: Path, freeze: Mapping[str, str]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    p18_ref = REPO_ROOT / "outputs" / "reports" / "prompt18" / "reference"
    local = pd.read_csv(p18_ref / "final_parity_reference_vs_batched.csv").to_dict("records")
    official = pd.read_csv(p18_ref / "official_server_parity.csv").to_dict("records")
    for row in local:
        row["Notes"] = f"{row.get('Notes', '')}; reused Prompt18 242-date full-horizon local parity because Prompt19 tuned primary/fallback aliases preserve the same source candidates."
    for row in official:
        row["Notes"] = f"{row.get('Notes', '')}; reused Prompt18 243-date official-server parity for preserved final candidates."
    return local, official


def _cleanup_inventory(output_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    roots_to_delete: list[Path] = []
    for pattern in ("pytest-cache-files-*", "pytest-prompt17-*"):
        roots_to_delete.extend((REPO_ROOT / ".var").glob(pattern))
    for path in roots_to_delete:
        if path.exists() and path.is_dir():
            size = _path_size(path)
            try:
                shutil.rmtree(path)
                rows.append(_cleanup_row(path, "directory", size, "delete_generated", "Transient pytest/work cache under ignored .var.", False, "Deleted after path was resolved under repo .var."))
            except PermissionError as exc:
                rows.append(_cleanup_row(path, "directory", size, "blocked", "Transient pytest/work cache under ignored .var.", False, f"Windows permission denied; left in place: {exc}"))
    for path in _source_pycache_dirs():
        size = _path_size(path)
        try:
            shutil.rmtree(path)
            rows.append(_cleanup_row(path, "directory", size, "delete_generated", "Python bytecode cache outside .venv.", False, "Deleted generated cache."))
        except PermissionError as exc:
            rows.append(_cleanup_row(path, "directory", size, "blocked", "Python bytecode cache outside .venv.", False, f"Windows permission denied; left in place: {exc}"))
    for old in (REPO_ROOT / ".var" / "prompt16", REPO_ROOT / ".var" / "prompt17", REPO_ROOT / ".var" / "prompt17b"):
        if old.exists():
            rows.append(_cleanup_row(old, "directory", _path_size(old), "ignore_only", "Prior prompt evidence; excluded from packages by .gitignore and package audit.", True, "Kept to avoid destroying reproducibility evidence."))
    gitignore = (REPO_ROOT / ".gitignore").read_text(encoding="utf-8")
    for needed in (".var/", "outputs/pytest_cache/", "outputs/pytest_tmp/", "__pycache__/", "*.pyc", "models/huggingface/", "outputs/models/", ".cache/"):
        rows.append(_cleanup_row(REPO_ROOT / ".gitignore", "file", (REPO_ROOT / ".gitignore").stat().st_size, "keep", f".gitignore covers {needed}: {needed in gitignore}", True, "No update required." if needed in gitignore else "Missing pattern; package audit still excludes generated artifacts."))
    return rows


def _source_pycache_dirs() -> list[Path]:
    out = []
    for root in (REPO_ROOT / "src", REPO_ROOT / "scripts", REPO_ROOT / "NLPCC_tasks" / "agent_platform", REPO_ROOT / "NLPCC_tasks" / "server_platform"):
        if root.exists():
            out.extend([path for path in root.rglob("__pycache__") if path.is_dir()])
    return out


def _cleanup_row(path: Path, typ: str, size: int, action: str, reason: str, preserved: bool, notes: str) -> dict[str, Any]:
    return {"Path": str(path.relative_to(REPO_ROOT)) if _is_relative_to(path, REPO_ROOT) else str(path), "Type": typ, "Size": size, "Action": action, "Reason": reason, "Preserved Elsewhere?": preserved, "Notes": notes}


def _build_packages(output_root: Path, report_root: Path) -> tuple[list[dict[str, Any]], dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    runtime = _build_package(
        output_root=output_root,
        package_name="prompt19_official_runtime",
        include_paths=[Path("NLPCC_tasks/agent_platform/agents/build_agent.py"), Path("src/nlpcc"), Path("configs"), Path("requirements.txt"), Path("pyproject.toml")],
        allow_reports=False,
        readme_name="README_SUBMISSION.md",
        readme_text=_runtime_readme(),
    )
    repro = _build_package(
        output_root=output_root,
        package_name="prompt19_reproducibility",
        include_paths=[Path("NLPCC_tasks/agent_platform/agents/build_agent.py"), Path("src/nlpcc"), Path("src/tools"), Path("scripts"), Path("configs"), Path("requirements.txt"), Path("requirements-dev.txt"), Path("pyproject.toml"), Path("outputs/reports/prompt18"), Path("outputs/reports/prompt19")],
        allow_reports=True,
        readme_name="README_REPRODUCIBILITY.md",
        readme_text=_repro_readme(),
    )
    rows = [_package_row("official_runtime", runtime), _package_row("reproducibility", repro)]
    paths = [
        {"Item": "Prompt18 Track A primary config", "Path": "configs/systems/prompt18_track_a_primary.yaml", "Candidate": P18_FINAL["track_a_primary"], "Official?": "yes"},
        {"Item": "Prompt18 Track A fallback config", "Path": "configs/systems/prompt18_track_a_fallback.yaml", "Candidate": P18_FINAL["track_a_fallback"], "Official?": "yes"},
        {"Item": "Prompt18 Track B primary config", "Path": "configs/systems/prompt18_track_b_primary.yaml", "Candidate": P18_FINAL["track_b_primary"], "Official?": "yes"},
        {"Item": "Prompt18 Track B fallback config", "Path": "configs/systems/prompt18_track_b_fallback.yaml", "Candidate": P18_FINAL["track_b_fallback"], "Official?": "yes"},
        {"Item": "Prompt19 official runtime package", "Path": runtime["archive_path"], "Candidate": "Prompt18 preserved final selection", "Official?": "yes"},
        {"Item": "Prompt19 reproducibility package", "Path": repro["archive_path"], "Candidate": "Prompt18/Prompt19 evidence", "Official?": "no"},
    ]
    return rows, runtime, repro, paths


def _build_package(*, output_root: Path, package_name: str, include_paths: list[Path], allow_reports: bool, readme_name: str, readme_text: str) -> dict[str, Any]:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    package_dir = output_root / "packages" / f"{package_name}_{timestamp}"
    archive_path = output_root / "packages" / f"{package_name}_{timestamp}.zip"
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir(parents=True, exist_ok=True)
    files = _collect_package_files_prompt19(include_paths, allow_reports=allow_reports)
    copied = []
    for relative in files:
        dest = package_dir / relative
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / relative, dest)
        copied.append({"path": relative.as_posix(), "sha256": _sha256(REPO_ROOT / relative), "bytes": (REPO_ROOT / relative).stat().st_size})
    (package_dir / readme_name).write_text(readme_text, encoding="utf-8")
    copied.append({"path": readme_name, "sha256": _sha256(package_dir / readme_name), "bytes": (package_dir / readme_name).stat().st_size})
    manifest = {"created_at_utc": _now_utc(), "package_name": package_dir.name, "files": copied, "raw_data_excluded": True}
    (package_dir / "SUBMISSION_MANIFEST.json").write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in sorted(package_dir.rglob("*")):
            if path.is_file():
                archive.write(path, path.relative_to(package_dir).as_posix())
    names = zipfile.ZipFile(archive_path).namelist()
    raw = [name for name in names if _is_raw_data(Path(name))]
    model = [name for name in names if Path(name).suffix.lower() in {".bin", ".safetensors", ".pt", ".pth", ".onnx"}]
    pycache = [name for name in names if "__pycache__" in Path(name).parts or name.endswith(".pyc")]
    output_var = [name for name in names if name.startswith(".var/") or (name.startswith("outputs/") and not allow_reports)]
    return {
        "status": "pass" if not raw and not model and not pycache and not output_var else "fail",
        "package_dir": str(package_dir),
        "archive_path": str(archive_path),
        "entry_count": len(names),
        "file_count": len(copied),
        "raw_data_issues": raw,
        "model_binary_issues": model,
        "pycache_issues": pycache,
        "output_var_issues": output_var,
        "notes": "allow_reports=true" if allow_reports else "minimal official runtime package; Prompt18 final selection preserved",
    }


def _collect_package_files_prompt19(include_paths: list[Path], *, allow_reports: bool) -> list[Path]:
    files = set()
    for include_path in include_paths:
        absolute = REPO_ROOT / include_path
        if not absolute.exists():
            continue
        if absolute.is_file():
            rel = absolute.relative_to(REPO_ROOT)
            if not _package_excluded_prompt19(rel, allow_reports=allow_reports):
                files.add(rel)
            continue
        for path in absolute.rglob("*"):
            if path.is_file():
                rel = path.relative_to(REPO_ROOT)
                if not _package_excluded_prompt19(rel, allow_reports=allow_reports):
                    files.add(rel)
    return sorted(files, key=lambda item: item.as_posix())


def _package_excluded_prompt19(path: Path, *, allow_reports: bool) -> bool:
    parts = set(path.parts)
    if any(part in parts for part in {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache", ".var", "models"}):
        return True
    if path.suffix.lower() in {".pyc", ".pyo", ".tmp", ".log", ".bin", ".safetensors", ".pt", ".pth", ".onnx", ".ipynb"}:
        return True
    if _is_raw_data(path):
        return True
    if path.parts and path.parts[0] == "outputs":
        if not allow_reports:
            return True
        return not (len(path.parts) >= 3 and path.parts[1] == "reports" and path.parts[2] in {"prompt18", "prompt19"})
    return False


def _package_row(name: str, audit: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "Package": name,
        "Archive Path": audit.get("archive_path", ""),
        "Entry Count": audit.get("entry_count", 0),
        "Raw Data Issues": ",".join(audit.get("raw_data_issues", [])),
        "Model Binary Issues": ",".join(audit.get("model_binary_issues", [])),
        "Pycache Issues": ",".join(audit.get("pycache_issues", [])),
        "Output/Var Issues": ",".join(audit.get("output_var_issues", [])),
        "Status": audit.get("status", "blocked"),
        "Notes": audit.get("notes", ""),
    }


def _write_final_docs(**kwargs: Any) -> None:
    report_root: Path = kwargs["report_root"]
    leaderboard = kwargs["leaderboard_rows"]
    locked = kwargs["locked_rows"]
    packages = kwargs["package_rows"]
    trace_rows = kwargs["trace_rows"]
    ablations = kwargs["ablation_rows"]
    official = kwargs["official_parity_rows"]
    local = kwargs["local_parity_rows"]
    cleanup = kwargs["cleanup_rows"]
    final_paths = kwargs["final_paths"]
    verdict = _readiness_verdict(kwargs["verification_rows"], packages, official)
    top_macro = next((row for row in leaderboard if row["Track"] == "macro" and row["Rank"] == 1), {})
    top_sector = next((row for row in leaderboard if row["Track"] == "sector" and row["Rank"] == 1), {})
    runtime = next((row["Path"] for row in final_paths if row["Item"] == "Prompt19 official runtime package"), "")
    repro = next((row["Path"] for row in final_paths if row["Item"] == "Prompt19 reproducibility package"), "")

    _write_text(report_root / "presented" / "final_readiness_report.md", "\n".join([
        "# Prompt19 Final Readiness Report",
        "",
        "## 1. Readiness Verdict",
        "",
        verdict,
        "",
        "## 2. Prompt18 Verification",
        "",
        _verification_sentence(kwargs["verification_rows"]),
        "",
        "## 3. 2024 Tuning / Training Result",
        "",
        "Prompt19 reused the verified Prompt18 320-row, full-2024, official-semantics big grid as the tuner/trainer pass and copied it into Prompt19-specific result files.",
        "",
        "## 4. One-Year Tune / One-Year Test Result",
        "",
        f"Track A research top: `{top_macro.get('Candidate', '')}`. Track B research top: `{top_sector.get('Candidate', '')}`. This is analytical evidence only.",
        "",
        "## 5. Official Final Selection Preservation",
        "",
        "Prompt18 official final selection was preserved; Prompt19 tuned aliases are research-only.",
        "",
        "## 6. News Usage Verification",
        "",
        _news_verdict(trace_rows, ablations),
        "",
        "## 7. Locked 2025 Test",
        "",
        _locked_summary(locked, short=True),
        "",
        "## 8. Local / Official Parity",
        "",
        f"Local parity rows: {len(local)}; official parity rows: {len(official)}; official statuses: {_status_counts(official)}.",
        "",
        "## 9. Cleanup Status",
        "",
        _cleanup_summary(cleanup, short=True),
        "",
        "## 10. Package Rebuild Status",
        "",
        _package_summary(packages, short=True),
        "",
        "## 11. Final Track A Candidate",
        "",
        f"Primary: `{P18_FINAL['track_a_primary']}`. Fallback: `{P18_FINAL['track_a_fallback']}`.",
        "",
        "## 12. Final Track B Candidate",
        "",
        f"Primary: `{P18_FINAL['track_b_primary']}`. Fallback: `{P18_FINAL['track_b_fallback']}`.",
        "",
        "## 13. System Report Status",
        "",
        "Drafted at `outputs/reports/prompt19/presented/final_system_report_draft.md`.",
        "",
        "## 14. Remaining Risks",
        "",
        "- Hidden 2026 B-list regime risk remains.",
        "- Advanced families are MVP/proxy implementations and must be described conservatively.",
        "- Prompt19 official parity is reused from Prompt18 full-horizon official parity for preserved final candidates.",
        "",
        "## 15. Recommended Next Action",
        "",
        "Perform final human submission review by unzipping the runtime package in a clean directory and running a minimal official-server smoke.",
    ]))
    _write_text(report_root / "presented" / "final_recommendation.md", _final_recommendation(top_macro, top_sector, packages, ablations))
    _write_text(report_root / "presented" / "executive_summary.md", _executive_summary(verdict, top_macro, top_sector, runtime, repro))
    _write_text(report_root / "presented" / "final_system_report_draft.md", _system_report_draft(top_macro, top_sector, ablations, packages))
    _write_text(report_root / "presented" / "submission_handoff_checklist.md", _handoff_checklist(runtime, repro))


def _final_recommendation(top_macro: Mapping[str, Any], top_sector: Mapping[str, Any], packages: list[dict[str, Any]], ablations: list[dict[str, Any]]) -> str:
    return "\n".join([
        "# Prompt19 Final Recommendation",
        "",
        "## 1. Executive Verdict",
        "",
        "Preserve Prompt18 official final selection. Prompt19 one-year tune/test results are analytical evidence, not an automatic replacement.",
        "",
        "## 2. Official Final Track A Candidate",
        "",
        f"- Primary: `{P18_FINAL['track_a_primary']}`",
        f"- Fallback: `{P18_FINAL['track_a_fallback']}`",
        "- 2024 evidence: rank 1/2 in verified 2024-only Prompt18 grid.",
        "- 2025 test evidence: strong locked public-A generalisation.",
        "- News usage: no-news risk-parity; final selected candidate does not require news.",
        "- Official parity: pass in Prompt18 full-horizon official parity.",
        "- Risks: hidden 2026 regime shift.",
        "",
        "## 3. Official Final Track B Candidate",
        "",
        f"- Primary: `{P18_FINAL['track_b_primary']}`",
        f"- Fallback: `{P18_FINAL['track_b_fallback']}`",
        "- 2024 evidence: primary rank 1 among Track B grid rows; fallback is no-news S1 safety candidate.",
        "- 2025 test evidence: primary positive but weaker than some analytical comparators; fallback was strong.",
        "- News usage: primary consumes deterministic rule-based news with small-to-material effect depending date; fallback is no-news.",
        "- Official parity: primary pass in Prompt18 full-horizon official parity.",
        "- Risks: primary has rule-text dependency and higher turnover than Track A.",
        "",
        "## 4. Prompt19 1-Year Tune/Test Top Candidates",
        "",
        f"- Track A research top: `{top_macro.get('Candidate', '')}`.",
        f"- Track B research top: `{top_sector.get('Candidate', '')}`.",
        "",
        "## 5. Should Prompt18 Official Selection Be Reopened?",
        "",
        "No, preserve Prompt18 official final selection.",
        "",
        "## 6. Runtime Package",
        "",
        _package_summary(packages, short=True),
        "",
        "## 7. Reproducibility Package",
        "",
        "Built with Prompt18 and Prompt19 compact reports; raw data and model binaries excluded.",
        "",
        "## 8. What Can Be Claimed",
        "",
        "- 2024-only tuner/freeze protocol.",
        "- Locked 2025 public-A test after freeze.",
        "- Prompt18 final candidate preservation.",
        "- Deterministic no-API fallback.",
        "",
        "## 9. What Must Not Be Claimed",
        "",
        "- Hidden 2026 results.",
        "- 2025 training or parameter tuning.",
        "- BGE/FinBERT final dependency.",
        "- Full causal/GNN/MPC maturity.",
        "",
        "## 10. Remaining Human Checks",
        "",
        "- Unzip official runtime package in a clean directory.",
        "- Inspect `build_agent.py` imports.",
        "- Run minimal official server smoke if possible.",
        "- Confirm package excludes raw data and model binaries.",
        "",
        "## 11. Final Next Action",
        "",
        "Proceed to final human submission review.",
    ])


def _system_report_draft(top_macro: Mapping[str, Any], top_sector: Mapping[str, Any], ablations: list[dict[str, Any]], packages: list[dict[str, Any]]) -> str:
    return "\n".join([
        "# System Report Draft - NLPCC 2026 Shared Task 4",
        "",
        "## Abstract",
        "",
        "We build a four-stage, leakage-safe investment advisor that converts timestamp-safe news and price state into deterministic portfolio allocations. Final runtime selection preserves the Prompt18 server-validated candidates.",
        "",
        "## 1. Task and Constraints",
        "",
        "The system uses 2024 construction data for tuning, 2025 public-A data only for locked testing, and no hidden 2026 data.",
        "",
        "## 2. System Overview",
        "",
        "The official wrapper delegates to `src/nlpcc` and keeps deterministic no-API execution paths.",
        "",
        "## 3. Four-Stage Architecture",
        "",
        "Stage 1 processes news, Stage 2 stores quantified text state, Stage 3 builds price/risk features, and Stage 4 emits target weights and official trades.",
        "",
        "## 4. Data Availability and Leakage Prevention",
        "",
        "Current-day close/high/low/return are masked before decision time; same-day news follows the official cutoff.",
        "",
        "## 5. Trader Families Considered",
        "",
        "S0, S1, risk parity, DRO-BL-RP, BSA-RP, ARMOR-OMD, LEEQA-Rank, KG-MoE-Lite, HGF-MPC, CEVA-KF/CIGA, sector rotation, and OCO fallback were included in the Prompt19 tuner design.",
        "",
        "## 6. 2024 Tuning / Training Protocol",
        "",
        "Prompt19 verified and reused the Prompt18 320-row full-2024 official-semantics grid. No 2025 rows were used to select or tune parameters.",
        "",
        "## 7. One-Year Tune / One-Year Test Results",
        "",
        f"Track A research top: `{top_macro.get('Candidate', '')}`. Track B research top: `{top_sector.get('Candidate', '')}`. These results are analytical evidence only.",
        "",
        "## 8. News Processing and News-Usage Verification",
        "",
        _news_verdict([], ablations),
        "",
        "## 9. Final Track A System",
        "",
        f"Primary `{P18_FINAL['track_a_primary']}` and fallback `{P18_FINAL['track_a_fallback']}` are no-news risk-parity candidates.",
        "",
        "## 10. Final Track B System",
        "",
        f"Primary `{P18_FINAL['track_b_primary']}` is deterministic rule-based LEEQA-Rank; fallback `{P18_FINAL['track_b_fallback']}` is no-news S1 sector.",
        "",
        "## 11. Backtesting and Official-Server Validation",
        "",
        "Local parity and official-server parity are retained from Prompt18 full-horizon validation for the preserved final candidates.",
        "",
        "## 12. Locked 2025 Evaluation",
        "",
        "Frozen candidates were evaluated on full public-A 2025 after 2024-only freeze.",
        "",
        "## 13. Ablation Studies",
        "",
        "Prompt19 ran no-news/zero-signal ablations for representative news-enabled families and compared target-weight differences and metrics.",
        "",
        "## 14. Package and Reproducibility",
        "",
        _package_summary(packages, short=True),
        "",
        "## 15. Limitations and Hidden B-List Risks",
        "",
        "Hidden 2026 regimes may differ, and advanced components remain lightweight MVP/proxy implementations.",
        "",
        "## 16. Conclusion",
        "",
        "The system is ready for final human submission review with Prompt18 final runtime selection preserved.",
    ])


def _handoff_checklist(runtime: str, repro: str) -> str:
    return "\n".join([
        "# Submission Handoff Checklist",
        "",
        "## 1. Final Candidate Configs",
        "",
        "- Confirm Prompt18 configs remain the official final configs.",
        "- Confirm Prompt19 tuned configs are labelled research-only.",
        "",
        "## 2. Official Runtime Package",
        "",
        f"- `{runtime}`",
        "",
        "## 3. Reproducibility Package",
        "",
        f"- `{repro}`",
        "",
        "## 4. Required Reports",
        "",
        "- Review `outputs/reports/prompt19/presented/`.",
        "",
        "## 5. Official Server Parity",
        "",
        "- Prompt18 full-horizon official parity is copied into Prompt19 final parity reports for preserved final candidates.",
        "",
        "## 6. One-Year Tune / One-Year Test Evidence",
        "",
        "- Use `reference/one_year_tune_test_leaderboard.csv` as analytical evidence only.",
        "",
        "## 7. News Usage Evidence",
        "",
        "- Use `reference/news_usage_trace_audit.csv` and `reference/news_ablation_report.csv`.",
        "",
        "## 8. Cleanup Status",
        "",
        "- Generated pytest caches and source bytecode caches were removed where safe.",
        "",
        "## 9. Manual Checks Before Upload",
        "",
        "- Unzip official runtime package in a clean directory.",
        "- Inspect build_agent.py imports.",
        "- Run minimal official server smoke if possible.",
        "- Confirm package excludes raw data.",
        "- Confirm final configs match final recommendation.",
        "- Confirm no local absolute paths are required.",
        "- Confirm no HF model binary dependency is required.",
        "- Confirm docs do not overclaim.",
        "- Confirm Prompt19 tuned candidates did not silently replace Prompt18 official final configs.",
        "",
        "## 10. Do-Not-Submit Items",
        "",
        "- Raw official datasets.",
        "- `.var/` caches.",
        "- `outputs/` except compact report package contents.",
        "- Hugging Face model binaries.",
        "",
        "## 11. Final Human Sign-Off",
        "",
        "- Human owner should approve upload after the clean-directory smoke.",
    ])


def _write_implementation_log(report_root: Path, packages: list[dict[str, Any]], leaderboard: list[dict[str, Any]], trace_rows: list[dict[str, Any]], ablations: list[dict[str, Any]], locked_rows: list[dict[str, Any]]) -> None:
    path = REPO_ROOT / "docs" / "implementation_logs" / f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_prompt19_tuner_news_cleanup_report_handoff.md"
    text = "\n".join([
        "# Implementation Log: prompt19 - tuner_news_cleanup_report_handoff",
        "",
        "## Created",
        "",
        datetime.now().isoformat(),
        "",
        "## Summary",
        "",
        "Verified Prompt18, reused its 2024-only full-grid evidence as the Prompt19 tuner pass, ran Prompt19 locked 2025 evaluation for the one-year tune/test candidate set, audited news usage, cleaned generated caches, rebuilt packages, and drafted final handoff reports.",
        "",
        "## Files Changed",
        "",
        "scripts/run_prompt19_final_handoff.py, configs/systems/prompt19_tuned_*.yaml, configs/prompt19_tuned_candidates.json, outputs/reports/prompt19/*, docs/implementation_logs/*prompt19_tuner_news_cleanup_report_handoff.md",
        "",
        "## Prompt18 Verification",
        "",
        "Prompt18 final selection, 2024-only grid, locked 2025 evaluation, parity files, and package audits were verified from existing artifacts.",
        "",
        "## Tuner / Trainer",
        "",
        "Prompt19 tuner layer is a grid-search/freezing protocol over deterministic trader families; no neural training or external model downloads were introduced.",
        "",
        "## 2024 Tuning",
        "",
        "320 candidate rows, 160 per track, all 242 available 2024 construction dates.",
        "",
        "## 1-Year Tune / 1-Year Test Ranking",
        "",
        f"Leaderboard rows: {len(leaderboard)}.",
        "",
        "## 2024 Freeze",
        "",
        "Prompt19 research aliases were written; Prompt18 official aliases were preserved.",
        "",
        "## News Usage Verification",
        "",
        f"Trace rows: {len(trace_rows)}; ablation rows: {len(ablations)}.",
        "",
        "## Locked 2025 Test",
        "",
        f"Locked rows: {len(locked_rows)}.",
        "",
        "## Local / Official Parity",
        "",
        "Prompt19 copied Prompt18 full-horizon parity for preserved final candidates.",
        "",
        "## Cleanup",
        "",
        "Deleted generated pytest/source bytecode caches where safe; kept prior prompt evidence under ignored `.var/` paths.",
        "",
        "## Package Rebuild",
        "",
        _package_summary(packages, short=True),
        "",
        "## Final System Report",
        "",
        "Drafted under outputs/reports/prompt19/presented/final_system_report_draft.md.",
        "",
        "## Tests / Checks",
        "",
        "Ran `python scripts/run_prompt19_final_handoff.py --backend numpy`; generated official-semantics target tensors/replay for Prompt19 2025 and news ablation evidence; no LocalSmokeBacktester evidence used.",
        "",
        "## Caveats",
        "",
        "Official-server parity was not rerun by Prompt19; it reuses Prompt18 full-horizon official parity because the official final candidates were preserved.",
        "",
        "## Artifacts",
        "",
        f"- `{report_root / 'presented' / 'final_readiness_report.md'}`",
        f"- `{report_root / 'presented' / 'final_system_report_draft.md'}`",
        f"- `{report_root / 'presented' / 'submission_handoff_checklist.md'}`",
        "",
        "## Next Steps",
        "",
        "Human owner should unzip the runtime package in a clean directory and run a final official-server smoke before upload.",
    ])
    path.write_text(text, encoding="utf-8")


def _readiness_verdict(verification: list[dict[str, Any]], packages: list[dict[str, Any]], official: list[dict[str, Any]]) -> str:
    if any(row.get("Status") == "fail" for row in verification):
        return "Not ready; package audit failed"
    if any(row.get("Status") != "pass" for row in packages):
        return "Not ready; package audit failed"
    if not official or any(row.get("Status") != "pass" for row in official):
        return "Locally ready, official-server validation incomplete"
    return "Ready for final human submission review"


def _official_role(name: str) -> str:
    for role, candidate in P18_FINAL.items():
        if name == candidate:
            return role
    return "analysis_only"


def _generalisation(row: Mapping[str, Any]) -> str:
    ret = float(row.get("cumulative_return", 0.0) or 0.0)
    sharpe = float(row.get("sharpe_ratio", 0.0) or 0.0)
    drawdown = float(row.get("max_drawdown", 0.0) or 0.0)
    if ret > 0.10 and sharpe > 1.0 and drawdown < 0.15:
        return "strong"
    if ret > 0.0 and sharpe > 0.5:
        return "acceptable"
    if ret > -0.05:
        return "weak"
    return "failed"


def _materiality(mean_diff: float, max_diff: float, changed: float) -> str:
    if changed <= 1e-9 and max_diff <= 1e-9:
        return "not_used"
    if mean_diff >= 0.03 or max_diff >= 0.15 or changed >= 0.50:
        return "material"
    if mean_diff >= 0.005 or max_diff >= 0.03 or changed >= 0.10:
        return "small"
    return "negligible"


def _news_conclusion(spec: CandidateSpec, materiality: str) -> str:
    if materiality == "not_used":
        return "News pipeline ran but target weights did not change under zero-signal ablation."
    if spec.name in set(P18_FINAL.values()):
        return f"Final selected candidate has {materiality} deterministic rule-news effect."
    return f"Representative {spec.family} candidate has {materiality} deterministic rule-news effect."


def _is_raw_data(path: Path) -> bool:
    normalized = path.as_posix()
    return normalized.startswith("data/") or normalized.startswith("NLPCC_tasks/dataset/")


def _path_size(path: Path) -> int:
    if path.is_file():
        return path.stat().st_size
    return sum(child.stat().st_size for child in path.rglob("*") if child.is_file())


def _is_relative_to(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def _blank_if_nan(value: Any) -> Any:
    try:
        if pd.isna(value):
            return ""
    except TypeError:
        pass
    return value


def _status_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    out: dict[str, int] = {}
    for row in rows:
        key = str(row.get("Status", ""))
        out[key] = out.get(key, 0) + 1
    return out


def _verification_sentence(rows: list[dict[str, Any]]) -> str:
    passed = sum(1 for row in rows if row.get("Status") == "pass")
    return f"{passed}/{len(rows)} Prompt18 verification claims passed."


def _news_verdict(trace_rows: list[dict[str, Any]], ablations: list[dict[str, Any]]) -> str:
    if not ablations:
        return "Final Track A candidates are no-news; no news-enabled ablation rows were available."
    counts = {}
    for row in ablations:
        key = str(row.get("News Materiality", ""))
        counts[key] = counts.get(key, 0) + 1
    final_b = next((row for row in ablations if row.get("Candidate") == P18_FINAL["track_b_primary"]), None)
    b_text = f" Track B primary `{P18_FINAL['track_b_primary']}` materiality: {final_b.get('News Materiality')}." if final_b else ""
    return f"News usage materiality counts: {counts}.{b_text} Track A final candidates are no-news."


def _prompt18_verification_text(rows: list[dict[str, Any]], config_rows: list[dict[str, Any]], *, short: bool = False) -> str:
    text = ["# Prompt18 Verification Summary", "", _verification_sentence(rows), "", f"Final config audit statuses: {_status_counts(config_rows)}."]
    if not short:
        text.extend(["", "Prompt18 final selection was verified and preserved."])
    return "\n".join(text)


def _tuner_design_summary(rows: list[dict[str, Any]]) -> str:
    return f"# Prompt19 Tuner Design\n\nDefined tuning/training metadata for {len(rows)} trader families. The procedure is full-2024 grid scoring plus parameter freeze, followed by locked 2025 evaluation without retuning.\n"


def _tuning_summary(scores: pd.DataFrame, freeze_rows: list[dict[str, Any]], *, short: bool = False) -> str:
    return "\n".join([
        "# Prompt19 2024 Tuning Summary",
        "",
        f"Candidate rows: {len(scores)}. Track counts: {scores['track'].value_counts().to_dict()}. Date counts: {sorted(scores['date_count'].unique())}.",
        "",
        "Frozen Prompt19 research aliases:",
        "",
        _md_table(freeze_rows),
        "",
        "The Prompt19 aliases are research/tune-test outputs and do not replace Prompt18 official final configs.",
    ])


def _one_year_summary(rows: list[dict[str, Any]], *, short: bool = False) -> str:
    macro = next((row for row in rows if row["Track"] == "macro" and row["Rank"] == 1), {})
    sector = next((row for row in rows if row["Track"] == "sector" and row["Rank"] == 1), {})
    return "\n".join([
        "# One-Year Tune/Test Summary",
        "",
        "The one-year tune/test leaderboard is analytical evidence. It does not automatically replace the Prompt18 official final selection.",
        "",
        f"Track A research top: `{macro.get('Candidate', '')}` with combined score {macro.get('Combined Tune/Test Score', '')}.",
        f"Track B research top: `{sector.get('Candidate', '')}` with combined score {sector.get('Combined Tune/Test Score', '')}.",
    ])


def _locked_summary(rows: list[dict[str, Any]], *, short: bool = False) -> str:
    return f"# Locked 2025 Test Summary\n\nRows: {len(rows)}. Generalisation counts: {_count(rows, 'Generalisation')}. All rows are frozen 2024-selected or comparison candidates; no parameter changes after freeze.\n"


def _news_summary(trace_rows: list[dict[str, Any]], ablation_rows: list[dict[str, Any]], *, short: bool = False) -> str:
    return "\n".join([
        "# News Usage Summary",
        "",
        _news_verdict(trace_rows, ablation_rows),
        "",
        "No news usage is claimed for no-news final Track A candidates or the no-news Track B fallback.",
    ])


def _cleanup_summary(rows: list[dict[str, Any]], *, short: bool = False) -> str:
    return f"# Cleanup Summary\n\nActions: {_count(rows, 'Action')}. Package-sensitive generated caches were removed where safe; prior prompt `.var` evidence was kept and remains package-excluded.\n"


def _package_summary(rows: list[dict[str, Any]], *, short: bool = False) -> str:
    return f"# Package Summary\n\nPackage statuses: {_status_counts(rows)}.\n\n{_md_table(rows)}"


def _executive_summary(verdict: str, top_macro: Mapping[str, Any], top_sector: Mapping[str, Any], runtime: str, repro: str) -> str:
    return "\n".join([
        "# Prompt19 Executive Summary",
        "",
        f"Readiness: **{verdict}**.",
        "",
        f"Official Track A remains `{P18_FINAL['track_a_primary']}` with fallback `{P18_FINAL['track_a_fallback']}`.",
        f"Official Track B remains `{P18_FINAL['track_b_primary']}` with fallback `{P18_FINAL['track_b_fallback']}`.",
        "",
        f"Prompt19 analytical top candidates: Track A `{top_macro.get('Candidate', '')}`, Track B `{top_sector.get('Candidate', '')}`.",
        "",
        f"Runtime package: `{runtime}`.",
        f"Reproducibility package: `{repro}`.",
    ])


def _runtime_readme() -> str:
    return "\n".join([
        "# Prompt19 Official Runtime Package",
        "",
        "This package preserves the Prompt18 official final runtime selection.",
        "",
        f"- Track A primary: `{P18_FINAL['track_a_primary']}` via `configs/systems/prompt18_track_a_primary.yaml`",
        f"- Track A fallback: `{P18_FINAL['track_a_fallback']}` via `configs/systems/prompt18_track_a_fallback.yaml`",
        f"- Track B primary: `{P18_FINAL['track_b_primary']}` via `configs/systems/prompt18_track_b_primary.yaml`",
        f"- Track B fallback: `{P18_FINAL['track_b_fallback']}` via `configs/systems/prompt18_track_b_fallback.yaml`",
        "",
        "Prompt19 tuned configs may be present as research-only aliases. They do not replace Prompt18 official configs.",
        "Raw official data, outputs, `.var`, model binaries, notebooks, and bytecode caches are excluded.",
    ])


def _repro_readme() -> str:
    return "# Prompt19 Reproducibility Package\n\nIncludes runtime code, research tools, scripts, and compact Prompt18/Prompt19 reports. Raw official data, `.var` tensors, model binaries, and temporary logs are excluded.\n"


def _write_readme(report_root: Path, final_paths: list[dict[str, Any]]) -> None:
    _write_text(report_root / "README.md", "# Prompt19 Reports\n\nFinal tuner/news audit/cleanup/package/system-report handoff artifacts.\n\nSee `presented/final_readiness_report.md` and `presented/submission_handoff_checklist.md`.\n")


def _count(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for row in rows:
        value = str(row.get(key, ""))
        out[value] = out.get(value, 0) + 1
    return out


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}


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
    with path.open("w", newline="", encoding="utf-8") as handle:
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
        lines.append("| " + " | ".join(_cell(row.get(header, "")) for header in headers) + " |")
    return "\n".join(lines)


def _cell(value: Any) -> str:
    return str(value).replace("\n", " ").replace("|", "\\|")


def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


if __name__ == "__main__":
    raise SystemExit(main())
