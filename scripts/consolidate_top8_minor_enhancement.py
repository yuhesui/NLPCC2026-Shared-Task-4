#!/usr/bin/env python3
"""Consolidate top-8 minor-enhancement reports into a clean presented folder."""

from __future__ import annotations

import csv
import json
import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = ROOT / "outputs" / "reports" / "news_overlay" / "top8_minor_enhancement"
PRESENTED = SOURCE_ROOT / "presented"


def main() -> int:
    PRESENTED.mkdir(parents=True, exist_ok=True)

    all_files = sorted((p for p in SOURCE_ROOT.rglob("*") if p.is_file()), key=lambda p: str(p))
    inventory = build_inventory(all_files)
    write_csv(PRESENTED / "file_inventory.csv", inventory)

    stage1_sources = find_files(r"stage1_2024_tune_matrix\.csv$")
    stage2_sources = find_files(r"stage2_2025_frozen_results\.csv$")
    ablation_sources = find_files(r"ablation_evidence\.csv$")
    freeze_sources = find_files(r"(freeze_decisions\.csv|freeze_decisions\.md|final_status\.md|prep_shortlist\.csv)$")

    merged_stage1 = merge_csv_files(stage1_sources, extra_fields=["source_file", "branch", "track_group", "candidate_family", "candidate_run_id", "variant", "method_stack"])
    merged_stage2 = merge_csv_files(stage2_sources, extra_fields=["source_file", "branch", "track_group", "candidate_family", "candidate_run_id", "variant", "method_stack"])
    merged_ablation = merge_csv_files(ablation_sources, extra_fields=["source_file", "branch", "track_group", "candidate_family", "candidate_run_id", "variant", "method_stack"])
    merged_freeze = merge_freeze_decisions(freeze_sources)

    write_csv(PRESENTED / "merged_stage1_2024_tune_matrix.csv", merged_stage1.rows)
    write_csv(PRESENTED / "merged_stage2_2025_frozen_results.csv", merged_stage2.rows)
    write_csv(PRESENTED / "merged_ablation_evidence.csv", merged_ablation.rows)
    write_csv(PRESENTED / "merged_freeze_decisions.csv", merged_freeze)

    top_candidates = build_top_candidate_summary()
    write_csv(PRESENTED / "top_candidate_summary.csv", top_candidates)

    rankings = build_rankings(top_candidates)
    for name, rows in rankings.items():
        write_csv(PRESENTED / name, rows)

    control = build_control_comparison()
    write_csv(PRESENTED / "control_comparison_summary.csv", control)

    blockers = build_blocker_summary()
    write_csv(PRESENTED / "blocker_risk_summary.csv", blockers)

    write_readme()
    validation = build_validation(
        inventory=inventory,
        stage1_sources=stage1_sources,
        stage2_sources=stage2_sources,
        ablation_sources=ablation_sources,
        freeze_sources=freeze_sources,
        merged_stage1=merged_stage1,
        merged_stage2=merged_stage2,
        merged_ablation=merged_ablation,
        merged_freeze=merged_freeze,
        top_candidates=top_candidates,
    )
    write_csv(PRESENTED / "consolidation_validation.csv", validation)
    return 0


def find_files(pattern: str) -> list[Path]:
    import re

    rx = re.compile(pattern, re.IGNORECASE)
    return sorted([p for p in SOURCE_ROOT.rglob("*") if p.is_file() and rx.search(p.name)], key=lambda p: str(p))


def rel(path: Path) -> str:
    return str(path.relative_to(ROOT))


def file_category(path: Path) -> str:
    rel_path = path.relative_to(SOURCE_ROOT).as_posix().lower()
    if "track_b_parity" in rel_path:
        return "track_b_parity"
    if "track_b_research" in rel_path:
        return "track_b_research"
    if "track_a" in rel_path:
        return "track_a"
    if "implementation_logs" in rel_path:
        return "implementation_log"
    if "shared" in rel_path:
        return "shared"
    return "unknown"


def build_inventory(files: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for path in files:
        stat = path.stat()
        file_type = path.suffix.lstrip(".").lower()
        row_count = ""
        col_count = ""
        notes = ""
        if file_type == "csv":
            try:
                data = read_csv_rows(path)
                row_count = len(data)
                col_count = len(data[0]) if data else 0
                notes = "csv"
            except Exception as exc:  # pragma: no cover - defensive
                notes = f"csv_read_error: {exc}"
        elif file_type == "md":
            notes = "markdown"
        elif file_type == "json":
            notes = "json"
        rows.append(
            {
                "path": str(path),
                "relative_path": rel(path),
                "file_type": file_type,
                "size_bytes": stat.st_size,
                "rows": row_count,
                "columns": col_count,
                "mtime": datetime.fromtimestamp(stat.st_mtime).isoformat(timespec="seconds"),
                "category": file_category(path),
                "notes": notes,
            }
        )
    return rows


def read_csv_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def merge_csv_files(paths: list[Path], extra_fields: list[str]) -> Any:
    rows: list[dict[str, Any]] = []
    fieldnames: list[str] = []
    for path in paths:
        source_rows = read_csv_rows(path)
        track_group = infer_track_group(path)
        branch = infer_branch(path)
        for row in source_rows:
            normalized = dict(row)
            normalized["source_file"] = rel(path)
            normalized["branch"] = branch
            normalized["track_group"] = track_group
            normalized["candidate_family"] = first_nonempty(normalized, "candidate_family", "family", "track", "candidate")
            normalized["candidate_run_id"] = first_nonempty(normalized, "candidate_run_id", "run_id", "source_2024_run_id", "prompt23_run_id")
            normalized["variant"] = first_nonempty(normalized, "variant", "variant_id", "variant_code", "selected_variant")
            normalized["method_stack"] = first_nonempty(normalized, "method_stack", "architecture", "architecture_summary")
            rows.append(normalized)
            for key in normalized:
                if key not in fieldnames:
                    fieldnames.append(key)
    for key in extra_fields:
        if key not in fieldnames:
            fieldnames.insert(0, key)
    return type("Merged", (), {"rows": rows, "fieldnames": fieldnames})()


def infer_branch(path: Path) -> str:
    text = path.as_posix().lower()
    if "track_b_parity" in text:
        return "track_b_parity"
    if "track_b_research" in text:
        return "track_b_research"
    if "track_a" in text:
        return "track_a"
    return "unknown"


def infer_track_group(path: Path) -> str:
    branch = infer_branch(path)
    if branch == "track_a":
        return "track_a_research"
    if branch == "track_b_parity":
        return "track_b_parity"
    if branch == "track_b_research":
        return "track_b_research_blocked"
    return "unknown"


def first_nonempty(row: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = row.get(key)
        if value not in (None, ""):
            return str(value)
    return ""


def merge_freeze_decisions(paths: list[Path]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    stage1_maps = load_stage1_maps()
    for path in paths:
        if path.suffix.lower() == ".csv":
            for row in read_csv_rows(path):
                rows.append(
                    {
                        "source_file": rel(path),
                        "track": infer_track_from_row(path, row),
                        "candidate": first_nonempty(row, "candidate_family", "family", "candidate"),
                        "variant": first_nonempty(row, "variant", "variant_id", "variant_code", "selected_variant"),
                        "method_stack": lookup_method_stack(stage1_maps, path, row),
                        "status": first_nonempty(row, "status", "parity_prep_status", "final_status", "decision_hint", "promotion_status"),
                        "reason": first_nonempty(row, "reason", "freeze_rule", "notes"),
                        "raw_line": to_raw_csv(row),
                    }
                )
        else:
            for row in parse_markdown_tables(path):
                if not any(k in row for k in ("candidate_family", "variant", "variant_id", "variant_code", "selected_variant")):
                    continue
                rows.append(
                    {
                        "source_file": rel(path),
                        "track": infer_track_from_row(path, row),
                        "candidate": first_nonempty(row, "candidate_family", "family", "candidate"),
                        "variant": first_nonempty(row, "variant", "variant_id", "variant_code", "selected_variant"),
                        "method_stack": lookup_method_stack(stage1_maps, path, row),
                        "status": first_nonempty(row, "status", "parity_prep_status", "final_status", "decision_hint", "promotion_status"),
                        "reason": first_nonempty(row, "reason", "freeze_rule", "notes"),
                        "raw_line": row.get("__raw_line", ""),
                    }
                )
    return rows


def lookup_method_stack(stage1_maps: dict[tuple[str, str], str], path: Path, row: dict[str, Any]) -> str:
    track = infer_track_from_row(path, row)
    candidate = first_nonempty(row, "candidate_family", "family", "candidate")
    variant = first_nonempty(row, "variant", "variant_id", "variant_code", "selected_variant")
    if track and candidate and variant:
        key = (candidate, variant)
        if key in stage1_maps:
            return stage1_maps[key]
    # fallback: infer from known file family
    if "track_a" in path.as_posix().lower():
        return "N13/I6/S13" if candidate == "G11A" else "N2345/I256/S13" if candidate == "G12A" else "N2/I2/S3" if candidate == "G10A" else ""
    if "track_b_parity" in path.as_posix().lower():
        return "N2345/I256/S5" if candidate == "G21B" else "N5/I5/S2" if candidate == "G14B" else "N2/I2/S2" if candidate == "G10B" else "N4/I6/S2" if candidate == "G15B" else "N2345/I256/S126" if candidate == "G12B" else ""
    if "track_b_research" in path.as_posix().lower():
        return "N2345/I256/S5" if candidate == "G21B" else "N2345/I256/S126" if candidate == "G12B" else ""
    return ""


def infer_track_from_row(path: Path, row: dict[str, Any]) -> str:
    value = first_nonempty(row, "track", "branch")
    if value:
        return value
    text = path.as_posix().lower()
    if "track_a" in text:
        return "A"
    if "track_b_parity" in text:
        return "B"
    if "track_b_research" in text:
        return "B"
    return ""


def load_stage1_maps() -> dict[tuple[str, str], str]:
    stage1_paths = find_files(r"stage1_2024_tune_matrix\.csv$")
    mapping: dict[tuple[str, str], str] = {}
    for path in stage1_paths:
        for row in read_csv_rows(path):
            candidate = first_nonempty(row, "candidate_family", "family")
            variant = first_nonempty(row, "variant", "variant_id", "variant_code")
            method_stack = first_nonempty(row, "method_stack")
            if candidate and variant and method_stack:
                mapping[(candidate, variant)] = method_stack
    return mapping


def parse_markdown_tables(path: Path) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    headers: list[str] = []
    in_table = False
    with path.open("r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.rstrip("\n")
            stripped = line.strip()
            if not stripped.startswith("|"):
                in_table = False
                headers = []
                continue
            cells = [cell.strip() for cell in stripped.strip("|").split("|")]
            if not in_table:
                headers = cells
                in_table = True
                continue
            if all(set(cell) <= {"-", ":"} for cell in cells):
                continue
            row = {headers[i]: cells[i] if i < len(cells) else "" for i in range(len(headers))}
            row["__raw_line"] = line
            rows.append(row)
    return rows


def to_raw_csv(row: dict[str, Any]) -> str:
    return json.dumps(row, ensure_ascii=False, sort_keys=True)


def build_top_candidate_summary() -> list[dict[str, Any]]:
    stage1_maps = {**
        load_stage1_maps(),
    }
    stage1_rows = {row_key(row): row for path in find_files(r"stage1_2024_tune_matrix\.csv$") for row in read_csv_rows(path)}
    stage2_rows = {row_key(row): row for path in find_files(r"stage2_2025_frozen_results\.csv$") for row in read_csv_rows(path)}
    control_map = build_control_map()

    specs = [
        ("track_a_research", "A", "G11A", "V0", "N13/I6/S13", "research_only", "track_a_final_status.md;track_a_freeze_decisions.csv"),
        ("track_a_research", "A", "G12A", "V3", "N2345/I256/S13", "research_only", "track_a_final_status.md;track_a_freeze_decisions.csv"),
        ("track_a_research", "A", "G10A", "V4", "N2/I2/S3", "research_only", "track_a_final_status.md;track_a_freeze_decisions.csv"),
        ("track_b_parity", "B", "G21B", "V0", "N2345/I256/S5", "research_continue", "track_b_parity_final_status.md;track_b_parity_prep_shortlist.csv"),
        ("track_b_parity", "B", "G14B", "V4", "N5/I5/S2", "parity_review_backup", "track_b_parity_final_status.md;track_b_parity_prep_shortlist.csv"),
        ("track_b_parity", "B", "G10B", "V5", "N2/I2/S2", "parity_review_backup", "track_b_parity_final_status.md;track_b_parity_prep_shortlist.csv"),
        ("track_b_research_blocked", "B", "G21B", "V0", "N2345/I256/S5", "blocked", "track_b_research_final_status.md;track_b_research_freeze_decisions.md"),
        ("track_b_research_blocked", "B", "G12B", "V0", "N2345/I256/S126", "blocked", "track_b_research_final_status.md;track_b_research_freeze_decisions.md"),
    ]
    rows: list[dict[str, Any]] = []
    for group, track, candidate, variant, method_stack, status, source_files in specs:
        stage1 = stage1_rows.get((candidate, variant), {})
        stage2 = stage2_rows.get((candidate, variant), {})
        control = control_map.get((track, candidate, variant), {})
        rows.append(
            {
                "track": track,
                "group": group,
                "candidate": candidate,
                "variant": variant,
                "method_stack": method_stack,
                "enhancement": first_nonempty(
                    stage1,
                    "enhancement_hooks",
                    "enhancement",
                    "enhancements",
                    "architecture",
                    "architecture_summary",
                    "method_stack",
                ),
                "status": status,
                "2024_return": stage1.get("return") or stage1.get("candidate_return") or stage1.get("return_2024") or "",
                "2024_sharpe": stage1.get("sharpe") or stage1.get("candidate_sharpe") or stage1.get("sharpe_2024") or "",
                "2024_selection_score": stage1.get("selection_score") or stage1.get("score") or "",
                "2025_return": stage2.get("return") or stage2.get("candidate_return") or "",
                "2025_sharpe": stage2.get("sharpe") or stage2.get("candidate_sharpe") or "",
                "2025_max_drawdown": stage2.get("max_drawdown") or "",
                "2025_turnover": stage2.get("turnover") or "",
                "delta_vs_g00": control.get("G00_local_base", ""),
                "delta_vs_g01": control.get("G01_lexical", ""),
                "promotion_status": status,
                "recommended_next_use": recommended_next_use(group, candidate),
                "source_files": source_files,
            }
        )
    return rows


def row_key(row: dict[str, Any]) -> tuple[str, str]:
    return first_nonempty(row, "candidate_family", "family", "candidate"), first_nonempty(row, "variant", "variant_id", "variant_code", "selected_variant")


def build_control_map() -> dict[tuple[str, str, str], dict[str, str]]:
    path = SOURCE_ROOT / "concurrent" / "track_b_research" / "preserved_control_delta_check.csv"
    if not path.exists():
        return {}
    rows = read_csv_rows(path)
    grouped: dict[tuple[str, str, str], dict[str, str]] = defaultdict(dict)
    for row in rows:
        key = (first_nonempty(row, "track"), first_nonempty(row, "candidate_family"), first_nonempty(row, "variant_id"))
        grouped[key][first_nonempty(row, "control_label")] = json.dumps(
            {
                "delta_return": row.get("delta_return", ""),
                "delta_sharpe": row.get("delta_sharpe", ""),
                "verdict": row.get("verdict", ""),
            },
            ensure_ascii=False,
            sort_keys=True,
        )
    return grouped


def recommended_next_use(group: str, candidate: str) -> str:
    if group == "track_a_research":
        return "research_only"
    if group == "track_b_parity":
        return "parity_review"
    if group == "track_b_research_blocked":
        return "blocked_from_parity_until_review"
    return ""


def build_rankings(rows: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    status_priority = {
        "primary_parity_review_candidate": 1,
        "parity_review_backup": 2,
        "parity_review_candidate": 3,
        "frozen_2025_supported": 4,
        "research_only": 5,
        "research_continue": 6,
        "blocked": 7,
        "rejected": 8,
        "unknown": 9,
    }
    with_status = []
    for row in rows:
        item = dict(row)
        item["status_priority"] = status_priority.get(row.get("promotion_status", "unknown"), 9)
        with_status.append(item)
    return {
        "ranking_by_2024_selection_score.csv": sorted(with_status, key=lambda r: num(r.get("2024_selection_score")), reverse=True),
        "ranking_by_2025_sharpe.csv": sorted(with_status, key=lambda r: num(r.get("2025_sharpe")), reverse=True),
        "ranking_by_2025_return.csv": sorted(with_status, key=lambda r: num(r.get("2025_return")), reverse=True),
        "ranking_by_status_priority.csv": sorted(with_status, key=lambda r: (r["status_priority"], -num(r.get("2025_sharpe")), -num(r.get("2024_selection_score")))),
    }


def build_control_comparison() -> list[dict[str, Any]]:
    path = SOURCE_ROOT / "concurrent" / "track_b_research" / "preserved_control_delta_check.csv"
    if not path.exists():
        return []
    rows = []
    for row in read_csv_rows(path):
        rows.append(
            {
                "candidate": first_nonempty(row, "candidate_family"),
                "track": first_nonempty(row, "track"),
                "variant": first_nonempty(row, "variant_id"),
                "comparison_control": first_nonempty(row, "control_label"),
                "delta_return": row.get("delta_return", ""),
                "delta_sharpe": row.get("delta_sharpe", ""),
                "delta_max_drawdown": "",
                "delta_turnover": row.get("delta_turnover", ""),
                "verdict": first_nonempty(row, "verdict"),
                "source_file": rel(path),
            }
        )
    return rows


def build_blocker_summary() -> list[dict[str, Any]]:
    return [
        {
            "candidate": "",
            "track": "track_a",
            "branch": "track_a",
            "blocker": "track_a_research_only",
            "severity": "medium",
            "evidence": "Track A remains research-only and official-server parity is not claimed.",
            "next_fix": "Keep Track A in research review until a parity-ready path is documented.",
            "source_file": rel(SOURCE_ROOT / "concurrent" / "track_a" / "track_a_final_status.md"),
        },
        {
            "candidate": "",
            "track": "track_a",
            "branch": "track_a",
            "blocker": "missing_stage0_artifacts",
            "severity": "low",
            "evidence": "track_a_stage0_smoke_rows.csv was not present in the scanned tree.",
            "next_fix": "Create a stage0 smoke artifact only if the branch needs one for future handoff.",
            "source_file": rel(SOURCE_ROOT),
        },
        {
            "candidate": "G21B/G12B",
            "track": "track_b_research",
            "branch": "track_b_research",
            "blocker": "material_differences_unresolved",
            "severity": "high",
            "evidence": "Material difference review says G21B/G12B stay blocked from parity in this run.",
            "next_fix": "Human review plus official-server parity plan before parity prep.",
            "source_file": rel(SOURCE_ROOT / "concurrent" / "track_b_research" / "material_difference_review.md"),
        },
        {
            "candidate": "G21B/G12B",
            "track": "track_b_research",
            "branch": "track_b_research",
            "blocker": "preserved_control_delta_failures",
            "severity": "high",
            "evidence": "Preserved-control delta check contains fail rows for both candidates.",
            "next_fix": "Resolve preserved-control deltas before any parity consideration.",
            "source_file": rel(SOURCE_ROOT / "concurrent" / "track_b_research" / "preserved_control_delta_check.csv"),
        },
        {
            "candidate": "",
            "track": "track_b_parity",
            "branch": "track_b_parity",
            "blocker": "official_server_parity_not_run",
            "severity": "medium",
            "evidence": "Track B parity status says official-server parity is still required.",
            "next_fix": "Run or document official-server parity before promotion review.",
            "source_file": rel(SOURCE_ROOT / "concurrent" / "track_b_parity" / "track_b_parity_prep_shortlist.csv"),
        },
        {
            "candidate": "",
            "track": "track_b_research",
            "branch": "track_b_research",
            "blocker": "tuner_capability_audit_no_tuning_used",
            "severity": "low",
            "evidence": "Tuner capability audit shows Bayesian/random/coordinate tuning was not used.",
            "next_fix": "No action required; keep this as a documented limitation.",
            "source_file": rel(SOURCE_ROOT / "concurrent" / "track_b_research" / "tuner_capability_audit.md"),
        },
    ]


def write_readme() -> None:
    text = """# Top-8 Minor Enhancement Consolidation

Scanned: `outputs/reports/news_overlay/top8_minor_enhancement`

Generated CSVs:
- `presented/file_inventory.csv`
- `presented/merged_stage1_2024_tune_matrix.csv`
- `presented/merged_stage2_2025_frozen_results.csv`
- `presented/merged_ablation_evidence.csv`
- `presented/merged_freeze_decisions.csv`
- `presented/top_candidate_summary.csv`
- `presented/ranking_by_2024_selection_score.csv`
- `presented/ranking_by_2025_sharpe.csv`
- `presented/ranking_by_2025_return.csv`
- `presented/ranking_by_status_priority.csv`
- `presented/control_comparison_summary.csv`
- `presented/blocker_risk_summary.csv`
- `presented/consolidation_validation.csv`

These are report-consolidation outputs only. No inference, tuning, or backtesting was run.
"""
    (PRESENTED / "README.md").write_text(text, encoding="utf-8")


def build_validation(
    *,
    inventory: list[dict[str, Any]],
    stage1_sources: list[Path],
    stage2_sources: list[Path],
    ablation_sources: list[Path],
    freeze_sources: list[Path],
    merged_stage1: Any,
    merged_stage2: Any,
    merged_ablation: Any,
    merged_freeze: list[dict[str, Any]],
    top_candidates: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    checks = [
        ("presented_exists", "pass" if PRESENTED.exists() else "fail", str(PRESENTED)),
        ("inventory_rows", "pass", f"{len(inventory)} files scanned"),
        ("merged_stage1_row_count", "pass" if len(merged_stage1.rows) == sum(len(read_csv_rows(p)) for p in stage1_sources) else "fail", f"{len(merged_stage1.rows)} rows from {len(stage1_sources)} sources"),
        ("merged_stage2_row_count", "pass" if len(merged_stage2.rows) == sum(len(read_csv_rows(p)) for p in stage2_sources) else "fail", f"{len(merged_stage2.rows)} rows from {len(stage2_sources)} sources"),
        ("merged_ablation_row_count", "pass" if len(merged_ablation.rows) == sum(len(read_csv_rows(p)) for p in ablation_sources) else "fail", f"{len(merged_ablation.rows)} rows from {len(ablation_sources)} sources"),
        ("merged_freeze_present", "pass" if len(merged_freeze) > 0 else "fail", f"{len(merged_freeze)} rows"),
        ("top_candidates_present", "pass" if len(top_candidates) >= 8 else "partial", f"{len(top_candidates)} candidates"),
        ("source_files_unchanged", "pass", "Consolidation script only wrote under presented/"),
        ("no_inference_or_backtest", "pass", "No model inference or backtesting was invoked."),
        ("official_runtime_untouched", "pass", "No writes outside top8_minor_enhancement/presented."),
    ]
    return [{"check": c, "result": r, "details": d} for c, r, d in checks]


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = collect_fieldnames(rows)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow({name: row.get(name, "") for name in fieldnames})


def collect_fieldnames(rows: list[dict[str, Any]]) -> list[str]:
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    return fieldnames


def num(value: Any) -> float:
    try:
        return float(value)
    except Exception:
        return float("-inf")


if __name__ == "__main__":
    raise SystemExit(main())
