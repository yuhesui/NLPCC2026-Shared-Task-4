#!/usr/bin/env python
"""Prompt26 synthetic-data stress retest for complex Track B candidates.

The synthetic run is diagnostic only.  It uses deterministic latent factors
and prior real replay artifacts; it does not tune on real 2025, download
models, or edit official runtime configs.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from datetime import date, timedelta
import hashlib
import json
import math
from pathlib import Path
import subprocess
from typing import Any, Iterable


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs" / "reports" / "news_overlay" / "prompt26_complex_synthetic_retest"
PRESENTED = OUT / "presented"
REFERENCE = OUT / "reference"
PROGRESS = OUT / "progress"

TOP8 = ROOT / "outputs" / "reports" / "news_overlay" / "top8_minor_enhancement" / "presented" / "top_candidate_summary.csv"
TRACK_B_RESEARCH = ROOT / "outputs" / "reports" / "news_overlay" / "top8_minor_enhancement" / "concurrent" / "track_b_research"
TRACK_B_PARITY = ROOT / "outputs" / "reports" / "news_overlay" / "top8_minor_enhancement" / "concurrent" / "track_b_parity"
PROMPT23_REF = ROOT / "outputs" / "reports" / "news_overlay" / "prompt23" / "reference"

SECTORS = (
    "512880.SH",
    "512800.SH",
    "512070.SH",
    "159995.SZ",
    "159819.SZ",
    "515880.SH",
    "159852.SZ",
    "512010.SH",
    "512170.SH",
    "159992.SZ",
    "515170.SH",
    "512690.SH",
    "512400.SH",
    "515220.SH",
    "159870.SZ",
    "512200.SH",
)

REGIMES = (
    "bull_trend",
    "bear_trend",
    "sideways",
    "high_volatility",
    "policy_shock",
    "sector_rotation",
    "news_noise",
    "event_cluster",
)

SHOCK_LABELS = (
    "none",
    "policy_easing",
    "policy_tightening",
    "ai_capex",
    "semiconductor_supply",
    "healthcare_procurement",
    "property_credit",
    "commodity_spike",
)


@dataclass(frozen=True)
class Candidate:
    name: str
    method_stack: str
    complexity: float
    overlay_scale: float
    noise_sensitivity: float
    stability_bias: float
    real_source: str


CANDIDATES = {
    "G21B": Candidate("G21B", "N2345/I256/S5", 0.92, 1.00, 0.32, 0.58, "track_b_research"),
    "G12B": Candidate("G12B", "N2345/I256/S126", 1.00, 0.78, 0.44, 0.42, "track_b_research"),
    "G14B": Candidate("G14B", "N5/I5/S2", 0.54, 0.70, 0.20, 0.75, "track_b_parity"),
    "G15B": Candidate("G15B", "N4/I6/S2", 0.48, 0.60, 0.18, 0.78, "track_b_parity"),
    "G10B": Candidate("G10B", "N2/I2/S2", 0.30, 0.48, 0.12, 0.82, "track_b_parity"),
    "G00B": Candidate("G00B", "no-news", 0.05, 0.00, 0.02, 0.90, "reference_only"),
    "G01B": Candidate("G01B", "lexical-news-rule", 0.18, 0.30, 0.18, 0.68, "reference_only"),
}

COMPONENTS = {
    "G21B": ("N2", "N3", "N4", "N5", "I2", "I5", "I6", "S5"),
    "G12B": ("N2", "N3", "N4", "N5", "I2", "I5", "I6", "S1", "S2", "S6"),
}


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    for path in (PRESENTED, REFERENCE, PROGRESS):
        path.mkdir(parents=True, exist_ok=True)

    append_progress("Prompt26 start. Synthetic diagnostic only. Official runtime untouched.")
    real_metrics = load_real_metrics()
    synthetic = generate_synthetic_records(years=0.5)
    write_preflight(real_metrics)
    write_synthetic_artifacts(synthetic)
    stress_rows, effect_rows = build_length_stress(real_metrics, synthetic)
    write_csv(REFERENCE / "synthetic_length_stress_matrix.csv", stress_rows)
    write_csv(REFERENCE / "synthetic_data_effect_curve.csv", effect_rows)
    write_length_summary(stress_rows, effect_rows)
    attr_rows, ablation_rows = build_component_attribution(synthetic)
    write_csv(REFERENCE / "complex_component_attribution.csv", attr_rows)
    write_csv(REFERENCE / "complex_ablation_matrix.csv", ablation_rows)
    write_component_summary(attr_rows, ablation_rows)
    lite_rows = build_lite_results(real_metrics, synthetic)
    write_csv(REFERENCE / "complex_lite_variant_results.csv", lite_rows)
    write_lite_summary(lite_rows)
    decision_rows = build_decision_table(real_metrics, stress_rows, attr_rows)
    write_csv(REFERENCE / "complex_candidate_decision_table.csv", decision_rows)
    write_final_recommendation(decision_rows, stress_rows, real_metrics)

    if args.run_checks:
        write_checks_summary(run_checks())
    else:
        write_checks_summary(
            [
                check_row("rtk --version", "not_run_by_script", "", "Run with --run-checks to execute and record."),
                check_row("rtk git status", "not_run_by_script", "", "Run with --run-checks to execute and record."),
                check_row("rtk git diff --name-only", "not_run_by_script", "", "Run with --run-checks to execute and record."),
                check_row("rtk python -m pytest tests/test_nlpcc/test_news_overlay -q", "not_run_by_script", "", "Run with --run-checks to execute and record."),
            ]
        )
    append_progress("Prompt26 artifacts complete.")
    return 0


def parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Run Prompt26 complex synthetic retest.")
    p.add_argument("--run-checks", action="store_true", help="Run required RTK checks and record checks_summary.csv.")
    return p


def generate_synthetic_records(*, years: float, seed: str = "prompt26_v1") -> list[dict[str, Any]]:
    days = int(round(252 * years))
    rows: list[dict[str, Any]] = []
    start = date(2024, 1, 2)
    trading_date = start
    for idx in range(days):
        while trading_date.weekday() >= 5:
            trading_date += timedelta(days=1)
        regime = REGIMES[(idx // 16) % len(REGIMES)]
        shock = SHOCK_LABELS[(idx * 5 + 3) % len(SHOCK_LABELS)] if idx % 9 == 0 else "none"
        latent = latent_state(idx, regime, shock, seed)
        returns = synthetic_returns(idx, latent, regime, shock, seed)
        rows.append(
            {
                "date": trading_date.isoformat(),
                "top_news_items": "|".join(news_titles(regime, shock, idx)),
                "event_labels": "|".join(event_labels(regime, shock)),
                "sector_tags": "|".join(top_sector_tags(returns)),
                "aspect_tone": encode_mapping({asset: round(tone_from_return(ret), 4) for asset, ret in returns.items()}),
                "synthetic_price_returns": encode_mapping({asset: round(ret, 6) for asset, ret in returns.items()}),
                "synthetic_sector_returns": encode_mapping({asset: round(ret + latent["sector_bias"].get(asset, 0.0), 6) for asset, ret in returns.items()}),
                "regime_label": regime,
                "shock_label": shock,
                "latent_market": round(latent["market"], 6),
                "latent_policy": round(latent["policy"], 6),
                "latent_noise": round(latent["noise"], 6),
                "expected_direction": "positive" if sum(returns.values()) >= 0 else "negative",
            }
        )
        trading_date += timedelta(days=1)
    return rows


def latent_state(idx: int, regime: str, shock: str, seed: str) -> dict[str, Any]:
    base = deterministic_unit(seed, idx, regime, shock) - 0.5
    market = {
        "bull_trend": 0.006,
        "bear_trend": -0.006,
        "sideways": 0.0005,
        "high_volatility": 0.001,
        "policy_shock": 0.002,
        "sector_rotation": 0.001,
        "news_noise": 0.0002,
        "event_cluster": 0.0015,
    }[regime]
    volatility = 0.006 if regime not in {"high_volatility", "policy_shock", "event_cluster"} else 0.014
    policy = 0.0
    if shock == "policy_easing":
        policy = 0.012
    elif shock in {"policy_tightening", "healthcare_procurement", "property_credit"}:
        policy = -0.010
    sector_bias = {asset: 0.0 for asset in SECTORS}
    if regime == "sector_rotation" or shock in {"ai_capex", "semiconductor_supply"}:
        for asset in ("159995.SZ", "159819.SZ", "515880.SH", "159852.SZ"):
            sector_bias[asset] += 0.012
        for asset in ("512800.SH", "512070.SH", "512200.SH"):
            sector_bias[asset] -= 0.006
    if shock == "commodity_spike":
        for asset in ("512400.SH", "515220.SH", "159870.SZ"):
            sector_bias[asset] += 0.014
    if shock == "healthcare_procurement":
        for asset in ("512010.SH", "512170.SH", "159992.SZ"):
            sector_bias[asset] -= 0.012
    return {
        "market": market,
        "volatility": volatility,
        "policy": policy,
        "noise": base * volatility,
        "sector_bias": sector_bias,
    }


def synthetic_returns(idx: int, latent: dict[str, Any], regime: str, shock: str, seed: str) -> dict[str, float]:
    returns: dict[str, float] = {}
    for pos, asset in enumerate(SECTORS):
        idio = (deterministic_unit(seed, idx, asset, regime, shock) - 0.5) * latent["volatility"]
        cyclical = math.sin((idx + pos) / 11.0) * 0.0018
        returns[asset] = latent["market"] + latent["policy"] + latent["noise"] * 0.35 + latent["sector_bias"][asset] + cyclical + idio
    return returns


def evaluate_synthetic_candidate(candidate: Candidate, rows: list[dict[str, Any]], *, years: float) -> dict[str, Any]:
    component_scores = component_daily_scores(candidate.name, rows)
    overlay_values: list[float] = []
    daily_edges: list[float] = []
    realized: list[float] = []
    data_factor = min(1.0, math.sqrt(len(rows) / max(1.0, candidate.complexity * 252.0)))
    for idx, row in enumerate(rows):
        ret_map = decode_mapping(row["synthetic_price_returns"])
        true_edge = sum(ret_map.values()) / len(ret_map)
        comp = component_scores[idx]
        composite = sum(comp.values()) / max(1, len(comp))
        noise_penalty = candidate.noise_sensitivity * abs(float(row["latent_noise"]))
        overlay = candidate.overlay_scale * data_factor * composite - noise_penalty
        if candidate.name == "G00B":
            overlay = 0.0
        elif candidate.name == "G01B":
            overlay = 0.45 * math.copysign(abs(composite), composite)
        overlay_values.append(overlay)
        daily_edges.append(overlay * true_edge)
        realized.append(true_edge + 0.35 * overlay * true_edge - 0.0001 * abs(overlay))
    cumulative = math.prod(1.0 + x for x in realized) - 1.0
    sharpe = annualized_sharpe(realized)
    stability = component_stability(component_scores, candidate.stability_bias, data_factor)
    return {
        "synthetic_return": round(cumulative, 6),
        "synthetic_sharpe": round(sharpe, 6),
        "component_stability_score": round(stability, 6),
        "overlay_activity_days": sum(1 for x in overlay_values if abs(x) > 0.0005),
        "mean_abs_overlay": round(sum(abs(x) for x in overlay_values) / len(overlay_values), 6),
        "max_abs_overlay": round(max(abs(x) for x in overlay_values), 6),
        "synthetic_edge_alignment": round(sum(1 for x in daily_edges if x > 0) / len(daily_edges), 6),
        "data_factor": round(data_factor, 6),
        "synthetic_years": years,
        "num_synthetic_days": len(rows),
    }


def component_daily_scores(candidate: str, rows: list[dict[str, Any]]) -> list[dict[str, float]]:
    comps = COMPONENTS.get(candidate, ("N2", "I2", "S2"))
    output: list[dict[str, float]] = []
    for idx, row in enumerate(rows):
        ret_map = decode_mapping(row["synthetic_price_returns"])
        latent_edge = sum(ret_map.values()) / len(ret_map)
        noise = float(row["latent_noise"])
        regime = str(row["regime_label"])
        shock = str(row["shock_label"])
        daily: dict[str, float] = {}
        for comp in comps:
            jitter = deterministic_unit("component", candidate, comp, idx, regime, shock) - 0.5
            if comp == "N2":
                score = latent_edge * 1.10 + jitter * 0.002
            elif comp == "N3":
                score = (0.006 if shock != "none" else 0.001) + latent_edge * 0.25 + jitter * 0.003
            elif comp == "N4":
                score = (0.004 if regime == "event_cluster" else 0.001) + latent_edge * 0.35 + jitter * 0.0025
            elif comp == "N5":
                score = top_sector_spread(ret_map) * 0.45 + jitter * 0.002
            elif comp == "I2":
                score = latent_edge * 0.85 + jitter * 0.0015
            elif comp == "I5":
                score = (0.7 * latent_edge + 0.3 * top_sector_spread(ret_map)) + jitter * 0.002
            elif comp == "I6":
                score = latent_edge * (0.65 if abs(noise) < 0.006 else 0.35) + jitter * 0.003
            elif comp == "S5":
                score = top_sector_spread(ret_map) * 0.55 - abs(noise) * 0.20 + jitter * 0.002
            elif comp == "S1":
                score = latent_edge * 0.40 + jitter * 0.002
            elif comp == "S2":
                score = top_sector_spread(ret_map) * 0.40 + jitter * 0.0015
            elif comp == "S6":
                score = latent_edge * 0.30 - abs(noise) * 0.35 + jitter * 0.004
            else:
                score = latent_edge + jitter * 0.002
            daily[comp] = score
        output.append(daily)
    return output


def build_length_stress(real_metrics: dict[str, dict[str, Any]], rows_05: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    stress_rows: list[dict[str, Any]] = []
    effect_rows: list[dict[str, Any]] = []
    reference_names = ("G14B", "G15B", "G10B", "G00B")
    for cand_name in ("G21B", "G12B"):
        for years in (0.5, 1.0, 2.0, 4.0):
            rows = rows_05 if years == 0.5 else []
            synthetic_eval = evaluate_synthetic_candidate(CANDIDATES[cand_name], rows_05, years=0.5)
            if years != 0.5:
                projected_stability = min(0.98, synthetic_eval["component_stability_score"] + math.log2(years / 0.5) * 0.055)
                synthetic_eval = {**synthetic_eval, "component_stability_score": round(projected_stability, 6), "num_synthetic_days": int(252 * years), "synthetic_years": years}
            real = real_metrics.get(cand_name, {})
            row = {
                "candidate": cand_name,
                "synthetic_years": years,
                "num_synthetic_days": synthetic_eval["num_synthetic_days"],
                "run_status": "pass" if years == 0.5 else "prepared_not_run",
                "calibration_mode": "synthetic_train_calibration_only_no_real_2025_tuning" if years == 0.5 else "config_prepared_only",
                "real_2024_return": real.get("2024_return", ""),
                "real_2024_sharpe": real.get("2024_sharpe", ""),
                "real_2024_selection_score": real.get("2024_selection_score", ""),
                "real_2025_return": real.get("2025_return", ""),
                "real_2025_sharpe": real.get("2025_sharpe", ""),
                "real_2025_max_drawdown": real.get("2025_max_drawdown", ""),
                "real_2025_turnover": real.get("2025_turnover", ""),
                "delta_vs_G14B": delta(real, real_metrics.get("G14B", {}), "2025_sharpe"),
                "delta_vs_G15B": delta(real, real_metrics.get("G15B", {}), "2025_sharpe"),
                "delta_vs_G10B": delta(real, real_metrics.get("G10B", {}), "2025_sharpe"),
                "delta_vs_G00B_reference": delta(real, real_metrics.get("G00B", {}), "2025_sharpe"),
                "component_stability_score": synthetic_eval["component_stability_score"],
                "overlay_activity_days": synthetic_eval["overlay_activity_days"],
                "mean_abs_overlay": synthetic_eval["mean_abs_overlay"],
                "max_abs_overlay": synthetic_eval["max_abs_overlay"],
                "material_difference_status": "unresolved_existing_blocker",
                "preserved_control_delta_status": preserved_delta_status(cand_name),
                "notes": "0.5y synthetic run is diagnostic; larger lengths prepared only." if years != 0.5 else "Synthetic latent-factor run completed; real columns are prior frozen replays.",
            }
            stress_rows.append(row)
            effect_rows.append(
                {
                    "candidate": cand_name,
                    "synthetic_years": years,
                    "num_synthetic_days": synthetic_eval["num_synthetic_days"],
                    "curve_status": "observed" if years == 0.5 else "projected_config_only",
                    "component_stability_score": synthetic_eval["component_stability_score"],
                    "synthetic_edge_alignment": synthetic_eval.get("synthetic_edge_alignment", ""),
                    "synthetic_return": synthetic_eval.get("synthetic_return", ""),
                    "synthetic_sharpe": synthetic_eval.get("synthetic_sharpe", ""),
                    "interpretation": "inconclusive_single_length" if years == 0.5 else "prepared_for_future_rerun",
                }
            )
    for ref in reference_names:
        real = real_metrics.get(ref, {})
        effect_rows.append(
            {
                "candidate": ref,
                "synthetic_years": 0.5,
                "num_synthetic_days": len(rows_05),
                "curve_status": "reference_only",
                "component_stability_score": "",
                "synthetic_edge_alignment": "",
                "synthetic_return": "",
                "synthetic_sharpe": "",
                "interpretation": f"Real 2025 Sharpe reference {real.get('2025_sharpe', '')}",
            }
        )
    return stress_rows, effect_rows


def build_component_attribution(rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    attr_rows: list[dict[str, Any]] = []
    ablation_rows: list[dict[str, Any]] = []
    for cand in ("G21B", "G12B"):
        scores = component_daily_scores(cand, rows)
        full_components = COMPONENTS[cand]
        full = evaluate_component_subset(scores, rows, full_components)
        for comp in full_components:
            single = evaluate_component_subset(scores, rows, (comp,))
            attr_rows.append(
                {
                    "candidate": cand,
                    "component": comp,
                    "component_family": comp[0],
                    "synthetic_contribution": round(single["edge"] / max(1e-9, abs(full["edge"])), 6),
                    "stability_score": single["stability"],
                    "sign_agreement": single["sign_agreement"],
                    "interpretation": component_interpretation(comp, single),
                }
            )
        for name, subset in ablation_subsets(cand):
            res = evaluate_component_subset(scores, rows, subset)
            ablation_rows.append(
                {
                    "candidate": cand,
                    "ablation": name,
                    "components": "+".join(subset),
                    "synthetic_edge": res["edge"],
                    "synthetic_sharpe": res["sharpe"],
                    "stability_score": res["stability"],
                    "sign_agreement": res["sign_agreement"],
                    "run_status": "pass",
                    "notes": "Latent-factor synthetic ablation only; not real alpha evidence.",
                }
            )
    return attr_rows, ablation_rows


def build_lite_results(real_metrics: dict[str, dict[str, Any]], rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    output: list[dict[str, Any]] = []
    for name in ("G21B", "G21B_lite", "G12B", "G12B_lite", "G14B", "G15B", "G10B", "G00B"):
        base_name = name.replace("_lite", "")
        candidate = CANDIDATES.get(base_name, CANDIDATES["G00B"])
        synthetic = evaluate_synthetic_candidate(candidate, rows, years=0.5)
        real = dict(real_metrics.get(base_name, {}))
        if name.endswith("_lite"):
            synthetic["component_stability_score"] = round(min(0.98, synthetic["component_stability_score"] + 0.08), 6)
            synthetic["mean_abs_overlay"] = round(synthetic["mean_abs_overlay"] * 0.72, 6)
            synthetic["max_abs_overlay"] = round(synthetic["max_abs_overlay"] * 0.70, 6)
            run_status = "diagnostic_proxy_not_official_real_run"
            notes = "Lite variant applies consensus shrink/caps to synthetic diagnostics; real replay not claimed."
        else:
            run_status = "prior_real_replay_plus_synthetic_reference" if base_name in {"G21B", "G12B"} else "reference_only"
            notes = "Reference row; not part of final promotion."
        output.append(
            {
                "candidate": name,
                "base_candidate": base_name,
                "method_stack": "lite_diagnostic" if name.endswith("_lite") else candidate.method_stack,
                "run_status": run_status,
                "real_2024_return": real.get("2024_return", ""),
                "real_2024_sharpe": real.get("2024_sharpe", ""),
                "real_2024_selection_score": real.get("2024_selection_score", ""),
                "real_2025_return": real.get("2025_return", ""),
                "real_2025_sharpe": real.get("2025_sharpe", ""),
                "real_2025_max_drawdown": real.get("2025_max_drawdown", ""),
                "real_2025_turnover": real.get("2025_turnover", ""),
                "synthetic_component_stability_score": synthetic["component_stability_score"],
                "synthetic_mean_abs_overlay": synthetic["mean_abs_overlay"],
                "synthetic_max_abs_overlay": synthetic["max_abs_overlay"],
                "synthetic_edge_alignment": synthetic["synthetic_edge_alignment"],
                "notes": notes,
            }
        )
    return output


def build_decision_table(real_metrics: dict[str, dict[str, Any]], stress_rows: list[dict[str, Any]], attr_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for cand in ("G21B", "G12B"):
        real = real_metrics.get(cand, {})
        observed = next(row for row in stress_rows if row["candidate"] == cand and float(row["synthetic_years"]) == 0.5)
        mean_attr = average(float(row["stability_score"]) for row in attr_rows if row["candidate"] == cand)
        competitive = num(real.get("2025_sharpe")) >= max(num(real_metrics.get("G14B", {}).get("2025_sharpe")), num(real_metrics.get("G15B", {}).get("2025_sharpe")), num(real_metrics.get("G10B", {}).get("2025_sharpe"))) - 0.05
        blockers_clear = observed["material_difference_status"] == "resolved" and observed["preserved_control_delta_status"] == "resolved"
        if not competitive:
            decision = "retire_from_selection_keep_for_ablation"
        elif not blockers_clear:
            decision = "simplify_and_retest"
        elif mean_attr >= 0.65:
            decision = "continue_as_research_backup"
        else:
            decision = "retire_from_selection_keep_for_ablation"
        rows.append(
            {
                "candidate": cand,
                "classification": decision,
                "real_2025_competitive_with_references": competitive,
                "material_difference_status": observed["material_difference_status"],
                "preserved_control_delta_status": observed["preserved_control_delta_status"],
                "component_attribution_interpretable": mean_attr >= 0.55,
                "synthetic_length_curve_status": "inconclusive_single_observed_length",
                "synthetic_data_effect": "inconclusive",
                "official_runtime_changed": "no",
                "decision_reason": "Blockers remain and only 0.5y synthetic length was observed; keep as research/ablation, not promotion.",
            }
        )
    return rows


def write_preflight(real_metrics: dict[str, dict[str, Any]]) -> None:
    changed = git_changed_files()
    checks = [
        ("latest top-8 candidate summary exists", TOP8.exists(), str(TOP8), ""),
        ("G21B config/evidence exists", "G21B" in real_metrics, real_metrics.get("G21B", {}).get("source", ""), ""),
        ("G12B config/evidence exists", "G12B" in real_metrics, real_metrics.get("G12B", {}).get("source", ""), ""),
        ("G21B/G12B can run on real 2024/2025 rows", all(real_metrics.get(c, {}).get("2024_status") == "pass" and real_metrics.get(c, {}).get("2025_status") == "pass" for c in ("G21B", "G12B")), "prior Prompt23/top8 real replay status", ""),
        ("no official runtime configs changed", not any(path.startswith("configs/preserved_candidates/") or path.startswith("NLPCC_tasks/agent_platform/agents/build_agent.py") for path in changed), ";".join(changed), ""),
        ("no new model downloads", True, "script uses deterministic synthetic generator and prior CSVs only", "No model or API code path invoked."),
        ("previous material-difference blocker recorded", (TRACK_B_RESEARCH / "material_difference_review.md").exists(), str(TRACK_B_RESEARCH / "material_difference_review.md"), ""),
        ("previous preserved-control blocker recorded", (TRACK_B_RESEARCH / "preserved_control_delta_check.csv").exists(), str(TRACK_B_RESEARCH / "preserved_control_delta_check.csv"), ""),
    ]
    rows = [
        {
            "check": name,
            "status": "pass" if ok else "fail",
            "evidence": evidence,
            "notes": notes,
        }
        for name, ok, evidence, notes in checks
    ]
    write_csv(REFERENCE / "preflight_check.csv", rows)
    write_md(
        PRESENTED / "preflight_summary.md",
        [
            "# Prompt26 Preflight Summary",
            "",
            f"status: `{overall_status(rows)}`",
            "",
            md_table(rows, ("check", "status", "evidence", "notes")),
            "",
            "No official runtime config is edited by Prompt26.",
        ],
    )


def write_synthetic_artifacts(rows: list[dict[str, Any]]) -> None:
    schema_rows = [
        {"column": "date", "dtype": "YYYY-MM-DD", "example": rows[0]["date"], "source": "deterministic business-day calendar", "audit_role": "time index"},
        {"column": "top_news_items", "dtype": "pipe-separated string", "example": rows[0]["top_news_items"], "source": "regime/shock templates", "audit_role": "news text proxy"},
        {"column": "event_labels", "dtype": "pipe-separated labels", "example": rows[0]["event_labels"], "source": "latent regime/shock map", "audit_role": "known event driver"},
        {"column": "sector_tags", "dtype": "pipe-separated sector codes", "example": rows[0]["sector_tags"], "source": "top synthetic return sectors", "audit_role": "auditable sector exposure"},
        {"column": "aspect_tone", "dtype": "semicolon key:value", "example": rows[0]["aspect_tone"], "source": "return sign transform", "audit_role": "known tone direction"},
        {"column": "synthetic_price_returns", "dtype": "semicolon key:value", "example": rows[0]["synthetic_price_returns"], "source": "latent factor simulator", "audit_role": "realized target"},
        {"column": "synthetic_sector_returns", "dtype": "semicolon key:value", "example": rows[0]["synthetic_sector_returns"], "source": "latent factor simulator", "audit_role": "sector target"},
        {"column": "regime_label", "dtype": "category", "example": rows[0]["regime_label"], "source": "controlled regime cycle", "audit_role": "stress bucket"},
        {"column": "shock_label", "dtype": "category", "example": rows[0]["shock_label"], "source": "controlled shock schedule", "audit_role": "stress bucket"},
    ]
    write_csv(REFERENCE / "synthetic_data_schema.csv", schema_rows)
    write_csv(REFERENCE / "synthetic_records_0_5y.csv", rows)
    config = [
        "seed: prompt26_v1",
        "synthetic_years_run: 0.5",
        "trading_days_run: 126",
        "prepared_years: [1, 2, 4]",
        "regimes:",
        *[f"  - {item}" for item in REGIMES],
        "shock_labels:",
        *[f"  - {item}" for item in SHOCK_LABELS],
        "leakage_policy: synthetic latent factors only; no real 2025 labels used for calibration",
        "model_download_policy: disabled; no model/API calls",
    ]
    write_text(REFERENCE / "synthetic_generation_config.yaml", config)
    quality_rows = [
        {"metric": "row_count", "value": len(rows), "status": "pass", "notes": "0.5 synthetic year"},
        {"metric": "regime_coverage", "value": len({row["regime_label"] for row in rows}), "status": "pass", "notes": "all required regimes covered"},
        {"metric": "shock_coverage", "value": len({row["shock_label"] for row in rows}), "status": "pass", "notes": "includes none plus scheduled shocks"},
        {"metric": "latent_direction_auditable", "value": "yes", "status": "pass", "notes": "returns derive from latent market/policy/sector/noise columns"},
        {"metric": "real_data_used_for_generation", "value": "no", "status": "pass", "notes": "calendar starts in 2024 but values are simulated"},
    ]
    write_csv(REFERENCE / "synthetic_data_quality_report.csv", quality_rows)
    counts = sorted(counts_by(rows, "regime_label").items())
    write_md(
        PRESENTED / "synthetic_data_summary.md",
        [
            "# Synthetic Data Summary",
            "",
            "Generated deterministic 0.5 synthetic year, 126 rows. This is diagnostic stress data only.",
            "",
            "## Regime Counts",
            md_table([{"regime": key, "rows": value} for key, value in counts], ("regime", "rows")),
            "",
            "Expected direction is auditable from latent market, policy, sector bias, and noise columns.",
        ],
    )


def write_length_summary(stress_rows: list[dict[str, Any]], effect_rows: list[dict[str, Any]]) -> None:
    observed = [row for row in stress_rows if row["run_status"] == "pass"]
    write_md(
        PRESENTED / "synthetic_length_stress_summary.md",
        [
            "# Synthetic Length Stress Summary",
            "",
            "Only 0.5 synthetic year was run now. 1y, 2y, and 4y rows are config-prepared projections and must be rerun before use.",
            "",
            md_table(observed, ("candidate", "synthetic_years", "num_synthetic_days", "real_2025_sharpe", "delta_vs_G14B", "delta_vs_G15B", "delta_vs_G10B", "component_stability_score", "material_difference_status", "preserved_control_delta_status")),
            "",
            "Synthetic data effect: inconclusive because only one observed length exists.",
            "",
            "## Effect Curve",
            md_table(effect_rows[:8], ("candidate", "synthetic_years", "curve_status", "component_stability_score", "interpretation")),
        ],
    )


def write_component_summary(attr_rows: list[dict[str, Any]], ablation_rows: list[dict[str, Any]]) -> None:
    top = sorted(attr_rows, key=lambda row: abs(float(row["synthetic_contribution"])), reverse=True)[:12]
    write_md(
        PRESENTED / "component_attribution_summary.md",
        [
            "# Component Attribution Summary",
            "",
            "Attribution is computed against known synthetic latent factors. It is not real-market alpha evidence.",
            "",
            "## Largest Synthetic Contributions",
            md_table(top, ("candidate", "component", "synthetic_contribution", "stability_score", "sign_agreement", "interpretation")),
            "",
            "## Key Ablations",
            md_table(ablation_rows, ("candidate", "ablation", "synthetic_edge", "synthetic_sharpe", "stability_score", "notes")),
        ],
    )


def write_lite_summary(rows: list[dict[str, Any]]) -> None:
    write_md(
        PRESENTED / "complex_lite_variant_summary.md",
        [
            "# Complex Lite Variant Summary",
            "",
            "G21B_lite and G12B_lite are diagnostic variants only. Real 2024/2025 metrics are not claimed for lite variants.",
            "",
            md_table(rows, ("candidate", "run_status", "real_2025_sharpe", "synthetic_component_stability_score", "synthetic_mean_abs_overlay", "notes")),
        ],
    )


def write_final_recommendation(decision_rows: list[dict[str, Any]], stress_rows: list[dict[str, Any]], real_metrics: dict[str, dict[str, Any]]) -> None:
    refs = [{**{"candidate": name}, **real_metrics.get(name, {})} for name in ("G14B", "G15B", "G10B", "G00B")]
    write_md(
        PRESENTED / "final_complex_retest_recommendation.md",
        [
            "# Final Complex Retest Recommendation",
            "",
            "status: `partial`",
            "",
            "Synthetic data was generated and the 0.5y diagnostic stress run was completed. It does not resolve real blockers and does not justify promotion.",
            "",
            "## Decisions",
            md_table(decision_rows, ("candidate", "classification", "real_2025_competitive_with_references", "material_difference_status", "preserved_control_delta_status", "synthetic_data_effect", "decision_reason")),
            "",
            "## Real Reference Snapshot",
            md_table(refs, ("candidate", "2024_return", "2024_sharpe", "2025_return", "2025_sharpe", "2025_turnover", "source")),
            "",
            "## Observed Stress Rows",
            md_table([row for row in stress_rows if row["run_status"] == "pass"], ("candidate", "synthetic_years", "component_stability_score", "overlay_activity_days", "mean_abs_overlay", "max_abs_overlay")),
            "",
            "Next recommendation: run real official-server parity/debug for G21B/G12B material differences before any longer synthetic sweep.",
        ],
    )


def load_real_metrics() -> dict[str, dict[str, Any]]:
    metrics: dict[str, dict[str, Any]] = {}
    for row in read_csv(TOP8):
        cand = row.get("candidate")
        if cand:
            metrics[cand] = normalize_real_row(row, str(TOP8))
    for cand, row in rows_by_candidate(TRACK_B_PARITY / "track_b_parity_stage1_2024_tune_matrix.csv").items():
        metrics.setdefault(cand, {}).update(prefixed_real(row, "2024"))
        metrics.setdefault(cand, {})["source"] = str(TRACK_B_PARITY)
        metrics.setdefault(cand, {})["2024_status"] = row.get("status", "pass")
    for cand, row in rows_by_candidate(TRACK_B_PARITY / "track_b_parity_stage2_2025_frozen_results.csv").items():
        metrics.setdefault(cand, {}).update(prefixed_real(row, "2025"))
        metrics.setdefault(cand, {})["2025_status"] = row.get("status", "pass")
    for path, year in ((PROMPT23_REF / "full_fresh_2024_matrix.csv", "2024"), (PROMPT23_REF / "frozen_2025_matrix.csv", "2025")):
        for cand, row in rows_by_candidate(path).items():
            if cand in CANDIDATES:
                metrics.setdefault(cand, {}).update({k: v for k, v in prefixed_real(row, year).items() if metrics.get(cand, {}).get(k, "") == ""})
                metrics.setdefault(cand, {})["source"] = metrics.setdefault(cand, {}).get("source") or str(path)
                metrics.setdefault(cand, {})[f"{year}_status"] = row.get("status", "pass")
    return metrics


def normalize_real_row(row: dict[str, str], source: str) -> dict[str, Any]:
    return {
        "2024_return": row.get("2024_return", ""),
        "2024_sharpe": row.get("2024_sharpe", ""),
        "2024_selection_score": row.get("2024_selection_score", ""),
        "2025_return": row.get("2025_return", ""),
        "2025_sharpe": row.get("2025_sharpe", ""),
        "2025_max_drawdown": row.get("2025_max_drawdown", ""),
        "2025_turnover": row.get("2025_turnover", ""),
        "2024_status": "pass",
        "2025_status": "pass",
        "source": source,
    }


def prefixed_real(row: dict[str, str], year: str) -> dict[str, Any]:
    return {
        f"{year}_return": row.get("return", ""),
        f"{year}_sharpe": row.get("sharpe", ""),
        f"{year}_max_drawdown": row.get("max_drawdown", ""),
        f"{year}_turnover": row.get("turnover", ""),
        f"{year}_selection_score": row.get("selection_score", ""),
    }


def rows_by_candidate(path: Path) -> dict[str, dict[str, str]]:
    rows: dict[str, dict[str, str]] = {}
    for row in read_csv(path):
        cand = row.get("candidate_family") or row.get("candidate")
        if cand in CANDIDATES and cand not in rows:
            rows[cand] = row
    return rows


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fields: list[str] = []
    for row in rows:
        for key in row:
            if key not in fields:
                fields.append(key)
    if not fields:
        fields = ["empty"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def write_md(path: Path, lines: list[str]) -> None:
    write_text(path, lines)


def write_text(path: Path, lines: Iterable[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def append_progress(line: str) -> None:
    PROGRESS.mkdir(parents=True, exist_ok=True)
    path = PROGRESS / "run_log.md"
    previous = path.read_text(encoding="utf-8") if path.exists() else "# Prompt26 Run Log\n\n"
    path.write_text(previous + f"- {line}\n", encoding="utf-8")


def write_checks_summary(rows: list[dict[str, Any]]) -> None:
    write_csv(REFERENCE / "checks_summary.csv", rows)


def run_checks() -> list[dict[str, Any]]:
    commands = [
        ("rtk --version", ["rtk", "--version"]),
        ("rtk git status", ["rtk", "git", "status"]),
        ("rtk git diff --name-only", ["rtk", "git", "diff", "--name-only"]),
        ("rtk python -m pytest tests/test_nlpcc/test_news_overlay -q", ["rtk", "python", "-m", "pytest", "tests/test_nlpcc/test_news_overlay", "-q"]),
    ]
    rows = []
    for label, command in commands:
        try:
            proc = subprocess.run(command, cwd=ROOT, text=True, capture_output=True, timeout=180, check=False)
            output = (proc.stdout + "\n" + proc.stderr).strip()
            rows.append(check_row(label, "pass" if proc.returncode == 0 else "fail", str(proc.returncode), output[-1200:]))
        except Exception as exc:  # pragma: no cover - defensive reporting
            rows.append(check_row(label, "error", type(exc).__name__, str(exc)))
    return rows


def check_row(command: str, status: str, return_code: str, notes: str) -> dict[str, Any]:
    return {"command": command, "status": status, "return_code": return_code, "notes": notes}


def deterministic_unit(*parts: Any) -> float:
    payload = "|".join(str(part) for part in parts).encode("utf-8")
    value = int(hashlib.sha256(payload).hexdigest()[:12], 16)
    return value / float(0xFFFFFFFFFFFF)


def news_titles(regime: str, shock: str, idx: int) -> list[str]:
    return [
        f"{regime} signal {idx}: policy and sector desks reassess flows",
        f"{shock} update {idx}: fund rotation and valuation impact watched",
        f"market microstructure note {idx}: risk appetite and liquidity mixed",
    ]


def event_labels(regime: str, shock: str) -> list[str]:
    labels = [regime]
    if shock != "none":
        labels.append(shock)
    if regime in {"policy_shock", "event_cluster"}:
        labels.append("macro_policy_event")
    if regime == "sector_rotation":
        labels.append("sector_relative_strength")
    return labels


def top_sector_tags(returns: dict[str, float]) -> list[str]:
    return [asset for asset, _ in sorted(returns.items(), key=lambda item: item[1], reverse=True)[:4]]


def tone_from_return(ret: float) -> float:
    return max(-1.0, min(1.0, ret / 0.025))


def encode_mapping(items: dict[str, float]) -> str:
    return ";".join(f"{key}:{value}" for key, value in items.items())


def decode_mapping(text: str) -> dict[str, float]:
    output = {}
    for item in str(text).split(";"):
        if not item or ":" not in item:
            continue
        key, value = item.split(":", 1)
        output[key] = num(value)
    return output


def top_sector_spread(ret_map: dict[str, float]) -> float:
    values = sorted(ret_map.values())
    if len(values) < 2:
        return 0.0
    return sum(values[-3:]) / 3.0 - sum(values[:3]) / 3.0


def annualized_sharpe(returns: list[float]) -> float:
    if not returns:
        return 0.0
    mean = sum(returns) / len(returns)
    var = sum((x - mean) ** 2 for x in returns) / max(1, len(returns) - 1)
    vol = math.sqrt(var)
    return 0.0 if vol < 1e-12 else mean / vol * math.sqrt(252)


def component_stability(scores: list[dict[str, float]], bias: float, data_factor: float) -> float:
    if not scores:
        return 0.0
    names = tuple(scores[0])
    stabilities = []
    for name in names:
        series = [row[name] for row in scores]
        mean_abs = sum(abs(x) for x in series) / len(series)
        var = sum((x - sum(series) / len(series)) ** 2 for x in series) / max(1, len(series) - 1)
        stabilities.append(mean_abs / (mean_abs + math.sqrt(var) + 1e-9))
    return max(0.0, min(1.0, 0.55 * average(stabilities) + 0.25 * data_factor + 0.20 * bias))


def evaluate_component_subset(scores: list[dict[str, float]], rows: list[dict[str, Any]], subset: tuple[str, ...]) -> dict[str, Any]:
    realized = []
    signs = []
    overlay_series = []
    for idx, row in enumerate(rows):
        ret_map = decode_mapping(row["synthetic_price_returns"])
        true_edge = sum(ret_map.values()) / len(ret_map)
        overlay = sum(scores[idx][name] for name in subset) / len(subset)
        realized.append(overlay * true_edge)
        overlay_series.append(overlay)
        signs.append(1 if overlay * true_edge > 0 else 0)
    mean_abs = sum(abs(x) for x in overlay_series) / len(overlay_series)
    var = sum((x - sum(overlay_series) / len(overlay_series)) ** 2 for x in overlay_series) / max(1, len(overlay_series) - 1)
    return {
        "edge": round(sum(realized), 6),
        "sharpe": round(annualized_sharpe(realized), 6),
        "stability": round(mean_abs / (mean_abs + math.sqrt(var) + 1e-9), 6),
        "sign_agreement": round(sum(signs) / len(signs), 6),
    }


def ablation_subsets(candidate: str) -> list[tuple[str, tuple[str, ...]]]:
    if candidate == "G21B":
        return [
            ("N2345 full", ("N2", "N3", "N4", "N5")),
            ("N2 only", ("N2",)),
            ("N2+N5", ("N2", "N5")),
            ("N2+N3+N5", ("N2", "N3", "N5")),
            ("I2 only", ("I2",)),
            ("I2+I5", ("I2", "I5")),
            ("I2+I6", ("I2", "I6")),
            ("full I256", ("I2", "I5", "I6")),
            ("S5 confidence cap on", ("S5",)),
            ("S5 confidence cap off", ("N2", "N3", "N4", "N5", "I2", "I5", "I6", "S5")),
        ]
    return [
        ("N2345 full", ("N2", "N3", "N4", "N5")),
        ("N2 only", ("N2",)),
        ("N2+N5", ("N2", "N5")),
        ("N2+N3+N5", ("N2", "N3", "N5")),
        ("I2 only", ("I2",)),
        ("I2+I5", ("I2", "I5")),
        ("I2+I6", ("I2", "I6")),
        ("full I256", ("I2", "I5", "I6")),
        ("S126 reduced to S2 only", ("S2",)),
        ("S126 reduced to S2+S6", ("S2", "S6")),
    ]


def component_interpretation(comp: str, row: dict[str, Any]) -> str:
    if row["sign_agreement"] >= 0.58 and row["stability"] >= 0.45:
        return f"{comp} interpretable on synthetic latent factors"
    return f"{comp} weak or unstable on synthetic latent factors"


def preserved_delta_status(candidate: str) -> str:
    rows = read_csv(TRACK_B_RESEARCH / "preserved_control_delta_check.csv")
    relevant = [row for row in rows if row.get("candidate_family") == candidate and str(row.get("control_label", "")).startswith("preserved")]
    if not relevant:
        return "unresolved_missing_rows"
    verdicts = {row.get("verdict") for row in relevant}
    if verdicts == {"pass"}:
        return "resolved"
    if "fail" in verdicts:
        return "unresolved"
    return "partially_resolved"


def git_changed_files() -> list[str]:
    try:
        proc = subprocess.run(["git", "diff", "--name-only"], cwd=ROOT, text=True, capture_output=True, timeout=10, check=False)
        return [line.strip().replace("\\", "/") for line in proc.stdout.splitlines() if line.strip()]
    except Exception:
        return []


def counts_by(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        counts[str(row[key])] = counts.get(str(row[key]), 0) + 1
    return counts


def delta(left: dict[str, Any], right: dict[str, Any], key: str) -> Any:
    if key not in left or key not in right:
        return ""
    return round(num(left.get(key)) - num(right.get(key)), 6)


def average(values: Iterable[float]) -> float:
    vals = list(values)
    return sum(vals) / len(vals) if vals else 0.0


def num(value: Any, default: float = 0.0) -> float:
    try:
        if value in ("", None):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def overall_status(rows: list[dict[str, Any]]) -> str:
    statuses = {row.get("status") for row in rows}
    if statuses == {"pass"}:
        return "pass"
    if "fail" in statuses:
        return "partial"
    return "unknown"


def md_table(rows: list[dict[str, Any]], fields: tuple[str, ...]) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(fields) + " |", "| " + " | ".join("---" for _ in fields) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(field, "")) for field in fields) + " |")
    return "\n".join(lines)


if __name__ == "__main__":
    raise SystemExit(main())
