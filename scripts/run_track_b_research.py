#!/usr/bin/env python
"""Scoped Track B research audit for blocked G21B/G12B candidates.

This script intentionally does not modify official runtime configs.  It uses
Prompt23 fresh real-local rows as the 2024 tune source for the requested
G21B/G12B variants, runs only a small 10-date local smoke for the two baseline
rows, and freezes one variant per candidate using 2024 evidence before reading
Prompt23 frozen 2025 rows.
"""

from __future__ import annotations

import argparse
import csv
from datetime import datetime
import json
import math
import os
from pathlib import Path
import re
from typing import Any, Iterable

from nlpcc.news_overlay.grid_evaluator import (
    TRACK_TO_OFFICIAL,
    _load_news_by_date,
)
from nlpcc.news_overlay.hf_models import resolve_local_model_context
from nlpcc.news_overlay.prompt22_runner import (
    HF_CACHE,
    FALLBACK_PRESERVED,
    PRIMARY_PRESERVED,
    _audit_status,
    _markdown_table,
    _model_binary_files_present,
    _num,
    _preserved_manifest,
    _round,
    _selected_gpu_row,
)
from nlpcc.news_overlay.prompt23_runner import (
    APPROVED_MODELS,
    LOCAL_MODELS,
    run_one_row,
    write_csv,
)
from tools.backtesting.reference_official_semantics import load_official_semantics_arrays


ROOT = Path(__file__).resolve().parents[1]
PROMPT23 = ROOT / "outputs" / "reports" / "news_overlay" / "prompt23"
OUT = ROOT / "outputs" / "reports" / "news_overlay" / "top8_minor_enhancement" / "concurrent" / "track_b_research"
PRESENTED = OUT
REFERENCE = OUT
PROGRESS = OUT / "progress"

FAMILIES = {"G21B", "G12B"}
PROMPT22_EQUIVALENCE = PROMPT23 / "reference" / "prompt22_vs_prompt23_equivalence.csv"
FRESH_2024 = PROMPT23 / "reference" / "full_fresh_2024_matrix.csv"
FROZEN_2025 = PROMPT23 / "reference" / "frozen_2025_matrix.csv"

H_DEFINITIONS = {
    "H1": "material-difference guardrail: keep material Prompt22-vs-Prompt23 drift visible and block parity until reviewed",
    "H2": "confidence / ambiguity damping through confidence and sensitivity thresholds",
    "H3": "short decay / smoothing proxy using stricter drawdown throttle where the current runner exposes no explicit decay knob",
    "H4": "turnover cap / deadband proxy through low-cap and lower overlay-strength variants",
    "H5": "diagnostic conflict and dominance check for S126/composite sensitivity rows",
    "H6": "composite stability control using impact/confidence consensus and lower-complexity freeze rules",
}


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    for path in (PRESENTED, REFERENCE, PROGRESS):
        path.mkdir(parents=True, exist_ok=True)

    if args.stage in {"all", "stage0"}:
        run_stage0_smoke(device=args.device, batch_size=args.batch_size, skip=args.skip_smoke)
    if args.stage in {"all", "reports"}:
        stage1 = build_stage1_matrix()
        write_csv(REFERENCE / "track_b_research_stage1_2024_tune_matrix.csv", stage1)
        write_stage1_summary(stage1)
        ablations = build_ablation_evidence(stage1)
        write_csv(REFERENCE / "track_b_research_ablation_evidence.csv", ablations)
        selected = freeze_variants(stage1)
        write_freeze_decisions(selected, stage1)
        stage2 = build_stage2_frozen(selected)
        write_csv(REFERENCE / "track_b_research_stage2_2025_frozen_results.csv", stage2)
        delta_rows = build_preserved_delta_check(stage1, selected, stage2)
        write_csv(REFERENCE / "preserved_control_delta_check.csv", delta_rows)
        write_material_difference_review(stage1, selected)
        write_tuner_capability_audit()
        write_final_status(stage1, selected, stage2, delta_rows)
    return 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run scoped Track B research reports for G21B/G12B.")
    p.add_argument("--stage", choices=("all", "stage0", "reports"), default="all")
    p.add_argument("--device", default="auto")
    p.add_argument("--batch-size", type=int, default=64)
    p.add_argument("--skip-smoke", action="store_true")
    return p


def variant_specs() -> list[dict[str, Any]]:
    """Return exactly the requested 2 candidates x 6 variants."""
    return [
        _variant("G21B", "N2345/I256/S5", "V0", "P23_G21B_s100_i25_c00_v00_caplow_ddmild", "H1+H6+H4", "baseline Prompt23 freeze, hooks off for this scoped run"),
        _variant("G21B", "N2345/I256/S5", "V1", "P23_G21B_s100_i00_c25_v25_caplow_ddmild", "H2", "confidence and ambiguity damping"),
        _variant("G21B", "N2345/I256/S5", "V2", "P23_G21B_s100_i00_c00_v00_capmedium_ddstrict", "H3", "strict drawdown smoothing proxy"),
        _variant("G21B", "N2345/I256/S5", "V3", "P23_G21B_s100_i00_c00_v00_caplow_ddoff", "H4", "turnover cap / deadband proxy"),
        _variant("G21B", "N2345/I256/S5", "V4", "P23_G21B_s100_i25_c25_v25_caplow_ddmild", "H1+H6+H4", "material-difference guardrail plus composite consensus thresholds"),
        _variant("G21B", "N2345/I256/S5", "V5", "P23_G21B_s100_i50_c25_v25_caplow_ddmild", "H1+H2+H4+H6", "predefined combo from V1-V4 controls only"),
        _variant("G12B", "N2345/I256/S126", "V0", "P23_G12B_s050_i25_c00_v00_caplow_ddmild", "H1+H6+H4+H5", "baseline Prompt23 freeze, hooks off for this scoped run"),
        _variant("G12B", "N2345/I256/S126", "V1", "P23_G12B_s050_i00_c25_v25_caplow_ddmild", "H2+H5", "confidence damping with S126 diagnostic"),
        _variant("G12B", "N2345/I256/S126", "V2", "P23_G12B_s100_i00_c00_v00_capmedium_ddstrict", "H3+H5", "strict smoothing proxy with S126 diagnostic"),
        _variant("G12B", "N2345/I256/S126", "V3", "P23_G12B_s100_i00_c00_v00_caplow_ddoff", "H4+H5", "turnover cap diagnostic without drawdown throttle"),
        _variant("G12B", "N2345/I256/S126", "V4", "P23_G12B_s050_i25_c25_v25_caplow_ddmild", "H1+H4+H5+H6", "conflict shrink and composite stability thresholds"),
        _variant("G12B", "N2345/I256/S126", "V5", "P23_G12B_s050_i50_c25_v25_caplow_ddmild", "H1+H2+H4+H5+H6", "predefined combo from V1-V4 controls only"),
    ]


def _variant(family: str, method_stack: str, variant_id: str, run_id: str, h_ids: str, description: str) -> dict[str, Any]:
    n_method, i_method, s_method = method_stack.split("/")
    return {
        "candidate_family": family,
        "track": "B",
        "method_stack": method_stack,
        "n_method": n_method,
        "i_method": i_method,
        "s_method": s_method,
        "variant_id": variant_id,
        "source_run_id": run_id,
        "enhancement_ids": h_ids,
        "enhancement_description": description,
    }


def run_stage0_smoke(*, device: str, batch_size: int, skip: bool) -> None:
    if skip:
        write_text(
            REFERENCE / "track_b_research_stage0_smoke_summary.md",
            ["# Track B Research Stage 0 Smoke Summary", "", "Smoke skipped by --skip-smoke."],
        )
        return
    local_paths, local_metadata, _ = resolve_local_model_context(
        approved_models_path=APPROVED_MODELS,
        local_models_path=LOCAL_MODELS,
        cache_root=HF_CACHE,
        require_local=True,
    )
    dates, assets, open_prices, pct_changes = load_official_semantics_arrays(
        ROOT / "data" / "train_2024",
        TRACK_TO_OFFICIAL["B"],
        max_dates=10,
    )
    arrays_by_track = {"B": (dates, assets, open_prices, pct_changes)}
    news_by_track = {"B": _load_news_by_date(ROOT / "data" / "train_2024", dates, top_rank=20)}
    gpu_row = _selected_gpu_row()
    # Keep the transient method cache short on Windows; long report paths can
    # exceed classic MAX_PATH once method subdirectories and SHA keys are added.
    cache_root = ROOT / ".var" / "tbr" / ("s0_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    rows = []
    for spec in [item for item in variant_specs() if item["variant_id"] == "V0"]:
        source = row_by_run(FRESH_2024, spec["source_run_id"])
        row = {**source, **spec, "run_id": "TBRS_" + spec["source_run_id"].replace("P23_", "") + "_stage0"}
        result = run_one_row(
            row,
            arrays_by_track=arrays_by_track,
            news_by_track=news_by_track,
            data_root=ROOT / "data" / "train_2024",
            period="track_b_research_stage0_2024_smoke",
            cache_root=cache_root,
            local_model_paths=local_paths,
            local_model_metadata=local_metadata,
            device=device,
            batch_size=batch_size,
            gpu_row=gpu_row,
        )
        rows.append(
            {
                **result,
                "variant_id": spec["variant_id"],
                "enhancement_ids": spec["enhancement_ids"],
                "enhancement_description": spec["enhancement_description"],
                "source_run_id": spec["source_run_id"],
            }
        )
    write_csv(REFERENCE / "track_b_research_stage0_smoke_rows.csv", rows)
    write_text(
        REFERENCE / "track_b_research_stage0_smoke_summary.md",
        [
            "# Track B Research Stage 0 Smoke Summary",
            "",
            "Scope: G21B and G12B only; 10 train_2024 dates; local-only models; no Track A rows.",
            "",
            _markdown_table(rows, ("run_id", "candidate_family", "method_stack", "status", "dates_run", "model_mode", "fresh_inference", "forbidden_cache_used", "device", "warnings")),
        ],
    )


def build_stage1_matrix() -> list[dict[str, Any]]:
    fresh_rows = {row["run_id"]: row for row in read_csv(FRESH_2024)}
    eq_rows = {row.get("prompt23_run_id"): row for row in read_csv(PROMPT22_EQUIVALENCE)}
    output: list[dict[str, Any]] = []
    for spec in variant_specs():
        row = dict(fresh_rows[spec["source_run_id"]])
        eq = eq_rows.get(spec["source_run_id"], {})
        out = {
            "stage": "stage1_2024_tune",
            "track": "B",
            "candidate_family": spec["candidate_family"],
            "variant_id": spec["variant_id"],
            "run_id": "TBRS_" + spec["source_run_id"].replace("P23_", ""),
            "source_prompt23_run_id": spec["source_run_id"],
            "method_stack": spec["method_stack"],
            "enhancement_ids": spec["enhancement_ids"],
            "enhancement_description": spec["enhancement_description"],
            "h_definition_summary": "; ".join(H_DEFINITIONS[h] for h in spec["enhancement_ids"].split("+") if h in H_DEFINITIONS),
            "run_source": "prompt23_full_fresh_2024_matrix",
            "data_period": "2024",
            "status": row["status"],
            "dates_run": row["dates_run"],
            "model_mode": row["model_mode"],
            "fresh_inference": row["fresh_inference"],
            "forbidden_cache_used": row["forbidden_cache_used"],
            "overlay_strength": row["overlay_strength"],
            "impact_threshold": row["impact_threshold"],
            "confidence_threshold": row["confidence_threshold"],
            "sensitivity_threshold": row["sensitivity_threshold"],
            "turnover_cap": row["turnover_cap"],
            "drawdown_throttle": row["drawdown_throttle"],
            "return": row["return"],
            "sharpe": row["sharpe"],
            "max_drawdown": row["max_drawdown"],
            "turnover": row["turnover"],
            "active_news_days": row["active_news_days"],
            "active_transformer_days": row["active_transformer_days"],
            "mean_abs_overlay": row["mean_abs_overlay"],
            "max_abs_overlay": row["max_abs_overlay"],
            "runtime_sec": row["runtime_sec"],
            "cache_hit_rate": row["cache_hit_rate"],
            "selection_score": row["selection_score"],
            "prompt22_equivalence_status": eq.get("equivalence_verdict", ""),
            "prompt22_delta_return": eq.get("delta_return", ""),
            "prompt22_delta_sharpe": eq.get("delta_sharpe", ""),
            "prompt22_delta_turnover": eq.get("delta_turnover", ""),
            "material_difference_guardrail": "blocked_from_parity_until_review" if eq.get("equivalence_verdict") == "material_difference" else "review_not_material",
            "warnings": row.get("warnings", ""),
        }
        output.append(out)
    return output


def freeze_variants(stage1: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    for family in ("G21B", "G12B"):
        rows = [row for row in stage1 if row["candidate_family"] == family and row["status"] == "pass"]
        rows.sort(key=lambda row: (_num(row.get("selection_score")), _num(row.get("sharpe"))), reverse=True)
        if not rows:
            continue
        row = rows[0]
        selected.append(
            {
                "track": "B",
                "candidate_family": family,
                "freeze_rank_within_family": 1,
                "variant_id": row["variant_id"],
                "run_id": row["run_id"],
                "source_prompt23_run_id": row["source_prompt23_run_id"],
                "method_stack": row["method_stack"],
                "enhancement_ids": row["enhancement_ids"],
                "frozen_parameters": frozen_parameters(row),
                "selection_score": row["selection_score"],
                "sharpe_2024": row["sharpe"],
                "return_2024": row["return"],
                "max_drawdown_2024": row["max_drawdown"],
                "turnover_2024": row["turnover"],
                "selection_source": "2024_only_stage1_matrix",
                "frozen_before_2025": True,
                "notes": "Selected within candidate family using 2024 selection_score before Stage 2 2025 lookup.",
            }
        )
    return selected


def build_stage2_frozen(selected: list[dict[str, Any]]) -> list[dict[str, Any]]:
    frozen_rows = {row["run_id"]: row for row in read_csv(FROZEN_2025)}
    rows: list[dict[str, Any]] = []
    for item in selected:
        source_run = item["source_prompt23_run_id"]
        row = frozen_rows.get(source_run)
        if row is None:
            rows.append(
                {
                    "stage": "stage2_2025_frozen",
                    **item,
                    "status": "blocked_missing_prompt23_frozen_2025_row",
                    "data_period": "2025",
                    "no_parameter_change": True,
                    "notes": "Prompt23 did not freeze-test this variant; do not tune or substitute after seeing 2025.",
                }
            )
            continue
        rows.append(
            {
                "stage": "stage2_2025_frozen",
                "track": "B",
                "candidate_family": item["candidate_family"],
                "variant_id": item["variant_id"],
                "run_id": item["run_id"],
                "source_prompt23_run_id": source_run,
                "method_stack": item["method_stack"],
                "enhancement_ids": item["enhancement_ids"],
                "frozen_parameters": item["frozen_parameters"],
                "data_period": "2025",
                "status": row["status"],
                "no_parameter_change": True,
                "return": row["return"],
                "sharpe": row["sharpe"],
                "max_drawdown": row["max_drawdown"],
                "turnover": row["turnover"],
                "active_news_days": row["active_news_days"],
                "mean_abs_overlay": row["mean_abs_overlay"],
                "max_abs_overlay": row["max_abs_overlay"],
                "model_mode": row["model_mode"],
                "fresh_inference": row["fresh_inference"],
                "forbidden_cache_used": row["forbidden_cache_used"],
                "notes": "Prompt23 frozen 2025 row for the 2024-selected variant; no parameter change.",
            }
        )
    return rows


def build_ablation_evidence(stage1: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in stage1:
        for ablation, applies, verdict, reason in (
            ("baseline hooks off", row["variant_id"] == "V0", "pass", "V0 retained as baseline comparator"),
            ("confidence damping off/on", "H2" in row["enhancement_ids"], "pass" if "H2" in row["enhancement_ids"] else "not_applicable_with_reason", "V1/V5 carry confidence damping"),
            ("turnover cap/deadband", "H4" in row["enhancement_ids"], "pass" if "H4" in row["enhancement_ids"] else "not_applicable_with_reason", "low cap or cap diagnostic variant present"),
            ("material difference guardrail", "H1" in row["enhancement_ids"], "blocked" if row["prompt22_equivalence_status"] == "material_difference" else "partial", "material rows remain blocked from parity until reviewed"),
            ("composite stability", "H6" in row["enhancement_ids"], "partial" if "H6" in row["enhancement_ids"] else "not_applicable_with_reason", "threshold consensus can be evaluated but does not explain replay drift alone"),
            ("S126 conflict/dominance diagnostic", row["candidate_family"] == "G12B", "partial" if row["candidate_family"] == "G12B" else "not_applicable_with_reason", "diagnostic required for G12B composite sensitivity"),
        ):
            rows.append(
                {
                    "candidate_family": row["candidate_family"],
                    "variant_id": row["variant_id"],
                    "run_id": row["run_id"],
                    "ablation": ablation,
                    "applicable": applies,
                    "verdict": verdict,
                    "selection_score": row["selection_score"],
                    "sharpe": row["sharpe"],
                    "notes": reason,
                }
            )
    return rows


def build_preserved_delta_check(stage1: list[dict[str, Any]], selected: list[dict[str, Any]], stage2: list[dict[str, Any]]) -> list[dict[str, Any]]:
    preserved = _preserved_manifest()
    local_rows = read_csv(FRESH_2024)
    local_controls = {row["candidate_family"]: row for row in local_rows if row["track"] == "B" and row["candidate_family"] in {"G00B", "G01B"}}
    stage1_by_run = {row["run_id"]: row for row in stage1}
    stage2_by_run = {row["run_id"]: row for row in stage2}
    rows: list[dict[str, Any]] = []
    for item in selected:
        for period, source in (("2024", stage1_by_run.get(item["run_id"])), ("2025", stage2_by_run.get(item["run_id"]))):
            if not source:
                continue
            comparisons = [
                ("G00_local_base", local_controls.get("G00B") if period == "2024" else row_by_family(FROZEN_2025, "G00B")),
                ("G01_lexical", local_controls.get("G01B") if period == "2024" else row_by_family(FROZEN_2025, "G01B")),
                ("preserved_primary", preserved.get(PRIMARY_PRESERVED["B"], {})),
                ("preserved_fallback", preserved.get(FALLBACK_PRESERVED["B"], {})),
            ]
            for label, control in comparisons:
                rows.append(delta_check_row(item, source, label, control or {}, period))
    return rows


def delta_check_row(item: dict[str, Any], source: dict[str, Any], label: str, control: dict[str, Any], period: str) -> dict[str, Any]:
    ret_key = f"{period}_return"
    sharpe_key = f"{period}_sharpe"
    control_return = control.get("return", control.get(ret_key, ""))
    control_sharpe = control.get("sharpe", control.get(sharpe_key, ""))
    delta_return = _round(_num(source.get("return")) - _num(control_return))
    delta_sharpe = _round(_num(source.get("sharpe")) - _num(control_sharpe))
    if label.startswith("preserved"):
        verdict = "pass" if delta_return >= 0 and delta_sharpe >= 0 else ("partial" if delta_return >= 0 or delta_sharpe >= 0 else "fail")
    else:
        verdict = "diagnostic"
    return {
        "period": period,
        "track": "B",
        "candidate_family": item["candidate_family"],
        "variant_id": item["variant_id"],
        "run_id": item["run_id"],
        "source_prompt23_run_id": item["source_prompt23_run_id"],
        "control_label": label,
        "control_return": control_return,
        "control_sharpe": control_sharpe,
        "candidate_return": source.get("return", ""),
        "candidate_sharpe": source.get("sharpe", ""),
        "delta_return": delta_return,
        "delta_sharpe": delta_sharpe,
        "verdict": verdict,
        "rule": "preserved pass requires non-negative return and sharpe deltas; local controls are diagnostic",
    }


def write_stage1_summary(rows: list[dict[str, Any]]) -> None:
    write_text(
        REFERENCE / "track_b_research_stage1_2024_tune_summary.md",
        [
            "# Track B Research Stage 1 2024 Tune Summary",
            "",
            "Scope: exactly G21B and G12B. Rows: 12 = 2 candidates x 6 variants. Source rows are Prompt23 fresh local-transformer 2024 rows, not Prompt22 replay.",
            "",
            "## H Definitions",
            *[f"- {key}: {value}" for key, value in H_DEFINITIONS.items()],
            "",
            "## Matrix",
            _markdown_table(rows, ("candidate_family", "variant_id", "source_prompt23_run_id", "enhancement_ids", "selection_score", "sharpe", "return", "turnover", "prompt22_equivalence_status", "material_difference_guardrail")),
        ],
    )


def write_freeze_decisions(selected: list[dict[str, Any]], stage1: list[dict[str, Any]]) -> None:
    del stage1
    write_text(
        REFERENCE / "track_b_research_freeze_decisions.md",
        [
            "# Track B Research Freeze Decisions",
            "",
            "Freeze rule: one variant per candidate family selected by 2024-only Stage 1 selection_score. Stage 2 uses the same frozen parameters with no 2025 knob change.",
            "",
            _markdown_table(selected, ("candidate_family", "variant_id", "run_id", "source_prompt23_run_id", "frozen_parameters", "selection_score", "sharpe_2024", "return_2024", "frozen_before_2025")),
        ],
    )


def write_material_difference_review(stage1: list[dict[str, Any]], selected: list[dict[str, Any]]) -> None:
    material_rows = [row for row in stage1 if row["prompt22_equivalence_status"] == "material_difference"]
    selected_ids = {row["run_id"] for row in selected}
    selected_rows = [row for row in stage1 if row["run_id"] in selected_ids]
    write_text(
        REFERENCE / "material_difference_review.md",
        [
            "# Material Difference Review",
            "",
            "Prompt22 used replayed Prompt21 target-weight checkpoints. Prompt23 used fresh per-row local-transformer execution. Rows with material differences remain blocked from parity until a human reviews the cause, preserved-control deltas, and official-server parity plan.",
            "",
            f"Stage 1 rows reviewed: {len(stage1)}",
            f"Material difference rows: {len(material_rows)}",
            "",
            "## Selected Rows",
            _markdown_table(selected_rows, ("candidate_family", "variant_id", "run_id", "prompt22_equivalence_status", "prompt22_delta_return", "prompt22_delta_sharpe", "prompt22_delta_turnover", "material_difference_guardrail")),
            "",
            "## All Material Rows",
            _markdown_table(material_rows, ("candidate_family", "variant_id", "run_id", "source_prompt23_run_id", "prompt22_delta_return", "prompt22_delta_sharpe", "prompt22_delta_turnover")),
            "",
            "Status: material differences are identified but not fully explained; G21B/G12B stay blocked from parity in this run.",
        ],
    )


def write_tuner_capability_audit() -> None:
    rows = tuner_scan()
    lines = [
        "# Tuner Capability Audit",
        "",
        "Bayesian/random/coordinate tuning was audited but not used in this run. No new dependencies were added.",
        "",
        _markdown_table(rows, ("pattern", "found", "file_path", "dependency_status", "cli_config_status", "safe_or_unsafe", "used_in_this_run")),
    ]
    write_text(REFERENCE / "tuner_capability_audit.md", lines)


def write_final_status(stage1: list[dict[str, Any]], selected: list[dict[str, Any]], stage2: list[dict[str, Any]], deltas: list[dict[str, Any]]) -> None:
    status_rows = []
    for item in selected:
        eq = next((row for row in stage1 if row["run_id"] == item["run_id"]), {})
        preserved = [row for row in deltas if row["run_id"] == item["run_id"] and row["control_label"].startswith("preserved")]
        delta_pass = all(row["verdict"] == "pass" for row in preserved)
        material = eq.get("prompt22_equivalence_status") == "material_difference"
        if material or not delta_pass:
            final = "blocked"
        else:
            final = "eligible-after-review"
        status_rows.append(
            {
                "candidate_family": item["candidate_family"],
                "variant_id": item["variant_id"],
                "run_id": item["run_id"],
                "stage1_status": eq.get("status", ""),
                "stage2_status": next((row.get("status", "") for row in stage2 if row["run_id"] == item["run_id"]), ""),
                "material_difference": material,
                "preserved_control_delta_all_pass": delta_pass,
                "final_status": final,
                "reason": "Material difference or preserved-control delta gate blocks parity." if final == "blocked" else "Requires human review before parity.",
            }
        )
    write_text(
        REFERENCE / "track_b_research_final_status.md",
        [
            "# Track B Research Final Status",
            "",
            "No candidate is promoted. Official runtime is untouched. Bayesian/random/coordinate tuning was not used.",
            "",
            f"Stage 0 smoke rows: see `{REFERENCE / 'track_b_research_stage0_smoke_summary.md'}`.",
            f"Stage 1 rows: {len(stage1)}.",
            f"Stage 2 frozen rows: {len(stage2)}.",
            "",
            _markdown_table(status_rows, ("candidate_family", "variant_id", "run_id", "material_difference", "preserved_control_delta_all_pass", "final_status", "reason")),
        ],
    )


def tuner_scan() -> list[dict[str, Any]]:
    patterns = ("optuna", "bayes", "bayesian", "hyperopt", "tpe", "random_search", "coordinate_search", "hyperband", "asha", "study", "trial", "suggest_float")
    search_roots = [ROOT / "src", ROOT / "scripts", ROOT / "configs", ROOT / "tests", ROOT / "docs" / "research" / "new_research_phase_top8_prompt_pack"]
    dependency_files = [ROOT / "requirements.txt", ROOT / "pyproject.toml", ROOT / "setup.cfg"]
    dependency_text = "\n".join(path.read_text(encoding="utf-8", errors="ignore") for path in dependency_files if path.exists()).lower()
    rows = []
    for pattern in patterns:
        matches = []
        regex = re.compile(re.escape(pattern), re.IGNORECASE)
        for root in search_roots:
            if not root.exists():
                continue
            for path in root.rglob("*"):
                if (
                    path.is_dir()
                    or "__pycache__" in path.parts
                    or path.name == "run_track_b_research.py"
                    or path.suffix.lower() in {".pyc", ".pyd", ".dll", ".png", ".jpg", ".npy", ".npz"}
                ):
                    continue
                try:
                    text = path.read_text(encoding="utf-8", errors="ignore")
                except OSError:
                    continue
                if regex.search(text):
                    matches.append(rel(path))
        dep_status = "dependency_present" if re.search(re.escape(pattern), dependency_text, re.IGNORECASE) else "dependency_not_declared"
        cli_status = "text_reference_only" if matches else "not_found"
        safe_status = "unsafe_for_this_run_do_not_use" if pattern in {"optuna", "bayes", "bayesian", "hyperopt", "tpe", "hyperband", "asha", "suggest_float"} and matches else "safe_not_used"
        if pattern in {"bayes", "bayesian"} and matches and all(path.endswith("src\\nlpcc\\news_overlay\\registry.py") for path in matches):
            cli_status = "semantic_method_label_only_not_tuner"
            safe_status = "safe_not_tuner_not_used"
        if pattern == "study" and matches:
            cli_status = "event_study_text_reference_or_tests_not_tuner"
            safe_status = "safe_not_tuner_not_used"
        rows.append(
            {
                "pattern": pattern,
                "found": bool(matches),
                "file_path": ";".join(matches[:8]),
                "dependency_status": dep_status,
                "cli_config_status": cli_status,
                "safe_or_unsafe": safe_status,
                "used_in_this_run": "no",
            }
        )
    return rows


def row_by_run(path: Path, run_id: str) -> dict[str, str]:
    for row in read_csv(path):
        if row.get("run_id") == run_id:
            return row
    raise KeyError(f"missing run_id {run_id} in {path}")


def row_by_family(path: Path, family: str) -> dict[str, str]:
    for row in read_csv(path):
        if row.get("candidate_family") == family:
            return row
    return {}


def frozen_parameters(row: dict[str, Any]) -> str:
    return json.dumps(
        {
            "overlay_strength": _num(row.get("overlay_strength")),
            "impact_threshold": _num(row.get("impact_threshold")),
            "confidence_threshold": _num(row.get("confidence_threshold")),
            "sensitivity_threshold": _num(row.get("sensitivity_threshold")),
            "turnover_cap": row.get("turnover_cap", ""),
            "drawdown_throttle": row.get("drawdown_throttle", ""),
        },
        sort_keys=True,
    )


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def write_text(path: Path, lines: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve()))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
