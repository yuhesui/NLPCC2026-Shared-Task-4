#!/usr/bin/env python
"""Generate Prompt24 cleanup, top-8, and research handoff artifacts."""

from __future__ import annotations

import csv
from datetime import datetime
import json
import os
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
P23 = ROOT / "outputs" / "reports" / "news_overlay" / "prompt23"
P24 = ROOT / "outputs" / "reports" / "news_overlay" / "prompt24"
PRESENTED = P24 / "presented"
REFERENCE = P24 / "reference"
PROGRESS = P24 / "progress"
HANDOFF = ROOT / "docs" / "research_handoffs" / "news_overlay"
DOCS_NO = ROOT / "docs" / "news_overlay"


ARCHITECTURE = {
    "P23_G11A_s025_i00_c00_v00_capmedium_ddoff": "FinBERT/aspect-tone hybrid + aspect-impact aggregator + Track A sensitivity/risk overlay",
    "P23_G12A_s025_i00_c00_v00_capmedium_ddoff": "Composite BGE/FinBERT transformer news stack + composite impact stack + Track A sensitivity/risk overlay",
    "P23_G10A_s050_i25_c00_v00_caplow_ddmild": "BGE bi-encoder relevance + base impact + macro risk/sensitivity gate",
    "P23_G21B_s100_i25_c00_v00_caplow_ddmild": "Full composite transformer news stack + composite impact stack + BL/sector overlay",
    "P23_G14B_s100_i00_c00_v00_capmedium_ddoff": "Sector-query attention + impact-gated attention + Rank-IC sector gate",
    "P23_G10B_s050_i25_c00_v00_caplow_ddmild": "BGE bi-encoder relevance + base impact + Rank-IC sector gate",
    "P23_G12B_s050_i25_c00_v00_caplow_ddmild": "Full composite transformer stack + composite impact + composite sensitivity gate",
    "P23_G15B_s025_i00_c00_v00_capmedium_ddoff": "BGE event-label / label-attention + FinBERT aspect-impact + Rank-IC sector gate",
}

STATUS = {
    "P23_G11A_s025_i00_c00_v00_capmedium_ddoff": ("research_only", "Track A research candidate; do not parity-prep unless it improves against local and preserved controls."),
    "P23_G12A_s025_i00_c00_v00_capmedium_ddoff": ("research_only", "Track A composite research candidate; useful for ablation-guided minor tuning."),
    "P23_G10A_s050_i25_c00_v00_caplow_ddmild": ("research_only", "Simplest Track A transformer candidate; keep as low-complexity comparator."),
    "P23_G21B_s100_i25_c00_v00_caplow_ddmild": ("research_continue", "Best fresh 2024 Track B score, but Prompt23 equivalence is material_difference."),
    "P23_G14B_s100_i00_c00_v00_capmedium_ddoff": ("parity_review_candidate", "Frozen-2025-supported Track B candidate for human shortlist review."),
    "P23_G10B_s050_i25_c00_v00_caplow_ddmild": ("parity_review_candidate", "Simple frozen-2025-supported Track B candidate for human shortlist review."),
    "P23_G12B_s050_i25_c00_v00_caplow_ddmild": ("research_continue", "Complex Track B backup; Prompt23 equivalence is material_difference."),
    "P23_G15B_s025_i00_c00_v00_capmedium_ddoff": ("parity_review_candidate", "Strong simple Track B frozen-2025-supported candidate."),
}

ALLOWED_THEMES = (
    "threshold schedules",
    "event magnitude smoothing and decay",
    "confidence damping",
    "sector-specific sensitivity calibration",
    "Rank-IC gate stability",
    "low-turnover overlay clipping",
    "Track A risk scaling",
    "Track B sector-rank tilt",
    "candidate-specific ablations",
    "official-runtime dependency minimisation",
)


def main() -> int:
    for path in (PRESENTED, REFERENCE, PROGRESS, HANDOFF, DOCS_NO):
        path.mkdir(parents=True, exist_ok=True)

    data = load_data()
    top8 = build_top8_manifest(data)
    write_csv(REFERENCE / "top8_candidate_manifest.csv", top8)
    write_csv(REFERENCE / "current_state_inventory.csv", build_current_state(data, top8))
    cleanup_inventory, cleanup_actions, preservation = build_cleanup_tables()
    write_csv(REFERENCE / "repo_cleanup_inventory.csv", cleanup_inventory)
    write_csv(REFERENCE / "repo_cleanup_actions.csv", cleanup_actions)
    write_csv(REFERENCE / "evidence_preservation_manifest.csv", preservation)
    backlog = build_research_backlog(top8)
    write_csv(REFERENCE / "research_question_backlog.csv", backlog)
    plan, runtime = build_tune_plan(top8, data)
    write_csv(REFERENCE / "top8_tune_test_plan.csv", plan)
    write_csv(REFERENCE / "top8_runtime_estimate.csv", runtime)

    write_presented(data, top8, cleanup_inventory, cleanup_actions, plan, runtime)
    write_research_handoffs(top8, backlog)
    write_docs_status(top8, data)
    write_progress(data, top8)
    cleanup_inventory, cleanup_actions, preservation = build_cleanup_tables()
    write_csv(REFERENCE / "repo_cleanup_inventory.csv", cleanup_inventory)
    write_csv(REFERENCE / "repo_cleanup_actions.csv", cleanup_actions)
    write_csv(REFERENCE / "evidence_preservation_manifest.csv", preservation)
    write_cleanup_summary(cleanup_inventory, cleanup_actions)
    return 0


def load_data() -> dict[str, Any]:
    return {
        "freeze": read_csv(P23 / "reference" / "selection_freeze_2024.csv"),
        "fresh": read_csv(P23 / "reference" / "full_fresh_2024_matrix.csv"),
        "frozen": read_csv(P23 / "reference" / "frozen_2025_matrix.csv"),
        "deltas_2025": read_csv(P23 / "reference" / "frozen_2025_candidate_vs_control_deltas.csv"),
        "equivalence": read_csv(P23 / "reference" / "prompt22_vs_prompt23_equivalence.csv"),
        "classifications": read_csv(P23 / "reference" / "candidate_classification.csv"),
        "freshness": read_csv(P23 / "reference" / "inference_freshness_audit.csv"),
        "dependency": read_csv(P23 / "reference" / "dependency_audit.csv"),
        "leakage": read_csv(P23 / "reference" / "leakage_audit.csv"),
        "package": read_csv(P23 / "reference" / "package_safety_audit.csv"),
        "preserved": read_csv(ROOT / "configs" / "preserved_candidates" / "manifest.csv"),
    }


def build_top8_manifest(data: dict[str, Any]) -> list[dict[str, Any]]:
    fresh_by_id = {row["run_id"]: row for row in data["fresh"]}
    frozen_by_source = {row.get("source_2024_run_id") or row["run_id"]: row for row in data["frozen"]}
    class_by_id = {row["run_id"]: row for row in data["classifications"]}
    eq_by_id = {row["prompt23_run_id"]: row for row in data["equivalence"] if row.get("prompt23_run_id")}
    preserved = {row["candidate_name"]: row for row in data["preserved"]}
    rows: list[dict[str, Any]] = []
    for item in sorted(data["freeze"], key=lambda r: (r["track"], int(r["freeze_rank"]))):
        run_id = item["run_id"]
        track = item["track"]
        frozen = frozen_by_source.get(run_id, {})
        classification = class_by_id.get(run_id, {})
        eq = eq_by_id.get(run_id, {})
        primary_id = "p18_rp_macro_w10_s5" if track == "A" else "p18_leeqa_sector_k5_temp35"
        fallback_id = "p18_rp_macro_w40_s5" if track == "A" else "p18_s1_sector_t35_v30_w20"
        status, next_use = STATUS.get(run_id, (classification.get("classification", "research_continue"), "review before use"))
        rows.append(
            {
                "track": track,
                "rank": item["freeze_rank"],
                "run_id": run_id,
                "family": item["candidate_family"],
                "method_stack": item["method_stack"],
                "architecture_summary": ARCHITECTURE.get(run_id, ""),
                "frozen_parameters": item["frozen_parameters"],
                "2024_return": item["return_2024"],
                "2024_sharpe": item["sharpe_2024"],
                "2024_selection_score": item["selection_score"],
                "2025_return": frozen.get("return", ""),
                "2025_sharpe": frozen.get("sharpe", ""),
                "delta_vs_G00": delta_summary(run_id, data, "G00_local_base", primary_id, period="both"),
                "delta_vs_G01": delta_summary(run_id, data, "G01_lexical", primary_id, period="both"),
                "delta_vs_preserved_primary": preserved_delta_summary(item, frozen, preserved.get(primary_id, {})),
                "delta_vs_preserved_fallback": preserved_delta_summary(item, frozen, preserved.get(fallback_id, {})),
                "prompt23_equivalence_status": eq.get("equivalence_verdict", classification.get("prompt22_equivalence", "")),
                "freshness_audit_status": audit_status(data["freshness"]),
                "current_status": status,
                "recommended_next_use": next_use,
            }
        )
    return rows


def delta_summary(run_id: str, data: dict[str, Any], label: str, preserved_id: str, period: str) -> str:
    del preserved_id, period
    rows = [r for r in data["deltas_2025"] if r["candidate_run_id"] == run_id and r["control_label"] == label]
    if not rows:
        return ""
    row = rows[0]
    return json.dumps(
        {
            "period": "2025",
            "delta_return": num(row.get("delta_return")),
            "delta_sharpe": num(row.get("delta_sharpe")),
            "delta_turnover": num(row.get("delta_turnover")),
        },
        sort_keys=True,
    )


def preserved_delta_summary(item: dict[str, str], frozen: dict[str, str], preserved: dict[str, str]) -> str:
    if not preserved:
        return ""
    return json.dumps(
        {
            "2024_delta_return": round(num(item.get("return_2024")) - num(preserved.get("2024_return")), 6),
            "2024_delta_sharpe": round(num(item.get("sharpe_2024")) - num(preserved.get("2024_sharpe")), 6),
            "2025_delta_return": round(num(frozen.get("return")) - num(preserved.get("2025_return")), 6),
            "2025_delta_sharpe": round(num(frozen.get("sharpe")) - num(preserved.get("2025_sharpe")), 6),
        },
        sort_keys=True,
    )


def build_current_state(data: dict[str, Any], top8: list[dict[str, Any]]) -> list[dict[str, Any]]:
    eq_counts = counts(row["equivalence_verdict"] for row in data["equivalence"])
    return [
        row_state("prompt23_full_fresh_2024_matrix", P23 / "reference" / "full_fresh_2024_matrix.csv", len(data["fresh"]), "pass" if len(data["fresh"]) == 212 else "partial", "Fresh 2024 matrix; no target-weight replay evidence."),
        row_state("prompt23_frozen_2025_matrix", P23 / "reference" / "frozen_2025_matrix.csv", len(data["frozen"]), "pass" if len(data["frozen"]) == 12 else "partial", "Frozen 2025 replay of controls plus Prompt23 top-8."),
        row_state("top8_candidate_manifest", REFERENCE / "top8_candidate_manifest.csv", len(top8), "pass" if len(top8) == 8 else "fail", "Current top-8 candidate set."),
        row_state("freshness_audit", P23 / "reference" / "inference_freshness_audit.csv", len(data["freshness"]), audit_status(data["freshness"]), "Prompt23 freshness audit."),
        row_state("prompt22_vs_prompt23_equivalence", P23 / "reference" / "prompt22_vs_prompt23_equivalence.csv", len(data["equivalence"]), "partial", f"Equivalence counts: {eq_counts}."),
        row_state("official_runtime_configs", ROOT / "NLPCC_tasks", "", "pass", "No Prompt24 edits; git diff check required in final validation."),
        row_state("prompt18_19_preserved_evidence", ROOT / "configs" / "preserved_candidates" / "manifest.csv", len(data["preserved"]), "pass", "Official runtime evidence preserved separately from News Overlay research."),
        row_state("package_model_binary_exclusion", P23 / "reference" / "package_safety_audit.csv", len(data["package"]), audit_status(data["package"]), "Prompt23 package safety audit excludes local HF external cache."),
    ]


def row_state(name: str, path: Path, rows: Any, status: str, notes: str) -> dict[str, Any]:
    return {
        "item": name,
        "path": rel(path),
        "exists": path.exists(),
        "rows_or_count": rows,
        "status": status,
        "notes": notes,
    }


def build_cleanup_tables() -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    targets = [
        ROOT / ".var",
        ROOT / "outputs" / "reports" / "news_overlay" / "prompt21",
        ROOT / "outputs" / "reports" / "news_overlay" / "prompt22",
        ROOT / "outputs" / "reports" / "news_overlay" / "prompt23",
        ROOT / "outputs" / "reports" / "news_overlay" / "prompt24",
        ROOT / "outputs" / "packages",
        ROOT / "docs" / "implementation_logs",
        ROOT / "configs" / "preserved_candidates",
        ROOT / "data",
    ]
    inventory = []
    for path in targets:
        inventory.append(
            {
                "path": rel(path),
                "type": "directory" if path.is_dir() else "missing",
                "size_mb": round(size_bytes(path) / (1024 * 1024), 3) if path.exists() else 0,
                "file_count": count_files(path) if path.exists() else 0,
                "evidence_status": evidence_status(path),
                "notes": cleanup_notes(path),
            }
        )
    actions = []
    for row in inventory:
        path = row["path"]
        action = "preserve"
        reason = "required evidence or durable repo content"
        safe = False
        archived_to = ""
        if "prompt23\\reference\\fresh_cache" in path:
            action = "archive_after_review"
        if path.endswith(".var"):
            action = "review_then_archive_or_keep"
            reason = "local cache/log area; inspect before archive"
        elif "prompt21" in path or "prompt22" in path:
            action = "preserve"
            reason = "legacy News Overlay evidence required for audit trail"
        elif "prompt23" in path:
            action = "preserve"
            reason = "final fresh-inference evidence"
        actions.append(
            {
                "path": path,
                "type": row["type"],
                "size_mb": row["size_mb"],
                "action": action,
                "reason": reason,
                "safe_to_delete": safe,
                "archived_to": archived_to,
                "evidence_status": row["evidence_status"],
                "notes": "No Prompt24 file moves or deletions performed.",
            }
        )
    preservation = [
        preserve("Prompt18/19 official runtime manifest", ROOT / "configs" / "preserved_candidates" / "manifest.csv", "official_runtime_evidence"),
        preserve("Prompt23 fresh 2024 matrix", P23 / "reference" / "full_fresh_2024_matrix.csv", "final_news_overlay_evidence"),
        preserve("Prompt23 frozen 2025 matrix", P23 / "reference" / "frozen_2025_matrix.csv", "final_news_overlay_evidence"),
        preserve("Prompt23 selection freeze", P23 / "reference" / "selection_freeze_2024.csv", "selection_evidence"),
        preserve("Prompt23 equivalence", P23 / "reference" / "prompt22_vs_prompt23_equivalence.csv", "audit_evidence"),
        preserve("Prompt23 audits", P23 / "reference", "audit_evidence"),
        preserve("Implementation logs", ROOT / "docs" / "implementation_logs", "durable_log_evidence"),
        preserve("Approved model config only", ROOT / "configs" / "news_overlay" / "approved_hf_models.yaml", "metadata_no_model_binary"),
    ]
    return inventory, actions, preservation


def evidence_status(path: Path) -> str:
    text = str(path).replace("/", "\\")
    if "data" in text:
        return "raw_or_input_data_preserve"
    if "preserved_candidates" in text:
        return "official_runtime_evidence_preserve"
    if "prompt23" in text:
        return "fresh_news_overlay_evidence_preserve"
    if "prompt21" in text or "prompt22" in text:
        return "legacy_news_overlay_evidence_preserve"
    if "implementation_logs" in text:
        return "implementation_log_preserve"
    return "review"


def cleanup_notes(path: Path) -> str:
    text = str(path).replace("/", "\\")
    if "fresh_cache" in text:
        return "Generated method cache; keep until final package/evidence review."
    if text.endswith("\\data"):
        return "Raw/input data must not be deleted."
    return ""


def preserve(name: str, path: Path, status: str) -> dict[str, Any]:
    return {
        "artifact": name,
        "path": rel(path),
        "exists": path.exists(),
        "size_mb": round(size_bytes(path) / (1024 * 1024), 3) if path.exists() else 0,
        "preservation_status": status,
        "notes": "Do not delete in Prompt24.",
    }


def build_research_backlog(top8: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows = []
    for candidate in top8:
        for theme in ALLOWED_THEMES:
            priority = "high" if candidate["track"] == "B" and theme in {"Rank-IC gate stability", "low-turnover overlay clipping", "Track B sector-rank tilt"} else "medium"
            if candidate["track"] == "A" and theme in {"Track A risk scaling", "confidence damping"}:
                priority = "high"
            rows.append(
                {
                    "track": candidate["track"],
                    "run_id": candidate["run_id"],
                    "family": candidate["family"],
                    "theme": theme,
                    "priority": priority,
                    "question": research_question(candidate, theme),
                    "constraints": "2024 tune only; 2025 frozen test only; no downloads; no online APIs; ablatable change only.",
                }
            )
    return rows


def research_question(candidate: dict[str, Any], theme: str) -> str:
    return f"For {candidate['run_id']} ({candidate['method_stack']}), propose a minor {theme} modification that preserves bounded overlays and can be ablated against the current frozen parameters."


def build_tune_plan(top8: list[dict[str, Any]], data: dict[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    plan = []
    runtime = []
    for stage, rows, dates, purpose in (
        ("Stage 0 - smoke", 8, 10, "Config/check only; no selection."),
        ("Stage 1 - quick 2024 tune", 8 * 6, 242, "Minor bounded variations on 2024 only."),
        ("Stage 2 - frozen 2025 test", 8, 243, "Frozen from Stage 1 only; no parameter changes."),
        ("Stage 3 - parity preparation", 3, 243, "Track B shortlist unless Track A improves vs controls."),
    ):
        plan.append(
            {
                "stage": stage,
                "candidate_scope": "top8" if stage != "Stage 3 - parity preparation" else "Track B shortlist",
                "rows_planned": rows,
                "date_scope": dates,
                "allowed_data": "2024 only" if "2024" in stage or "smoke" in stage else "2025 frozen test / official parity prep",
                "purpose": purpose,
                "long_grid_allowed": False,
                "notes": "Do not launch without explicit future prompt.",
            }
        )
    avg_runtime = average_runtime(data["fresh"])
    for row in plan:
        scale = num(row["date_scope"]) / 242.0
        estimate = round(num(row["rows_planned"]) * avg_runtime * scale / 60.0, 2)
        runtime.append(
            {
                "stage": row["stage"],
                "rows_planned": row["rows_planned"],
                "date_scope": row["date_scope"],
                "estimated_minutes": estimate,
                "basis": f"Prompt23 average row runtime {round(avg_runtime, 3)} sec over 242 dates.",
                "risk": "medium" if estimate < 60 else "high",
            }
        )
    return plan, runtime


def write_presented(data: dict[str, Any], top8: list[dict[str, Any]], cleanup_inventory: list[dict[str, Any]], cleanup_actions: list[dict[str, Any]], plan: list[dict[str, Any]], runtime: list[dict[str, Any]]) -> None:
    eq_counts = counts(row["equivalence_verdict"] for row in data["equivalence"])
    write_text(
        PRESENTED / "current_state_summary.md",
        [
            "# Prompt24 Current State Summary",
            "",
            "Stage 1 - Discuss / Freeze Current State",
            "",
            f"- Prompt23 fresh 2024 rows: {len(data['fresh'])}; pass rows: {sum(1 for r in data['fresh'] if r['status'] == 'pass')}.",
            f"- Prompt23 frozen 2025 rows: {len(data['frozen'])}; pass rows: {sum(1 for r in data['frozen'] if r['status'] == 'pass')}.",
            f"- Prompt22 vs Prompt23 equivalence: {eq_counts}.",
            f"- Freshness audit: {audit_status(data['freshness'])}; dependency audit: {audit_status(data['dependency'])}; package audit: {audit_status(data['package'])}.",
            "- Official-server parity is not run and no candidate is promoted.",
            "- Prompt18/19 official runtime evidence is preserved under `configs/preserved_candidates/`.",
        ],
    )
    write_text(
        PRESENTED / "top8_candidate_summary.md",
        [
            "# Prompt24 Top-8 Candidate Summary",
            "",
            md_table(top8, ("track", "rank", "run_id", "family", "method_stack", "2024_selection_score", "2025_sharpe", "current_status", "prompt23_equivalence_status")),
        ],
    )
    write_text(
        PRESENTED / "repo_cleanup_summary.md",
        cleanup_summary_lines(cleanup_inventory, cleanup_actions),
    )
    write_text(
        PRESENTED / "research_handoff_summary.md",
        [
            "# Prompt24 Research Handoff Summary",
            "",
            "Stage 2 - Research Context Export",
            "",
            "Handoff docs were generated under `docs/research_handoffs/news_overlay/`. They constrain future research to minor, ablatable improvements to the current top-8 candidates.",
            "",
            "- No new large architecture proposals.",
            "- No online LLM/API calls.",
            "- No 2025 tuning.",
            "- No hidden 2026 data.",
        ],
    )


def write_cleanup_summary(cleanup_inventory: list[dict[str, Any]], cleanup_actions: list[dict[str, Any]]) -> None:
    write_text(PRESENTED / "repo_cleanup_summary.md", cleanup_summary_lines(cleanup_inventory, cleanup_actions))


def cleanup_summary_lines(cleanup_inventory: list[dict[str, Any]], cleanup_actions: list[dict[str, Any]]) -> list[str]:
    return [
        "# Prompt24 Repo Cleanup Summary",
        "",
        "Stage 3 - Project Initialisation / Repo Cleanup",
        "",
        "No files were deleted or moved in Prompt24. Cleanup actions are a review plan only.",
        "",
        "## Inventory",
        md_table(cleanup_inventory, ("path", "type", "size_mb", "file_count", "evidence_status")),
        "",
        "## Actions",
        md_table(cleanup_actions, ("path", "action", "safe_to_delete", "evidence_status", "notes")),
    ]
    write_text(
        PRESENTED / "top8_2024_tune_2025_test_plan.md",
        [
            "# Prompt24 Top-8 2024 Tune / 2025 Test Plan",
            "",
            "Stage 4 - Execution Preparation",
            "",
            md_table(plan, ("stage", "candidate_scope", "rows_planned", "date_scope", "allowed_data", "purpose")),
            "",
            "## Runtime Estimate",
            md_table(runtime, ("stage", "estimated_minutes", "basis", "risk")),
        ],
    )
    checklist = [
        "Prompt23 freshness audit failure reviewed? Current status: no failure; material equivalence differences remain.",
        "Prompt22-vs-Prompt23 material differences understood?",
        "Track A kept research-only unless improved?",
        "Track B parity-review shortlist chosen?",
        "Official runtime untouched?",
        "Raw data untouched?",
        "Model binaries excluded?",
        "2024/2025 discipline preserved?",
        "Research engine handoff generated?",
        "Cleanup actions reviewed?",
    ]
    write_text(PRESENTED / "manual_review_checklist.md", ["# Prompt24 Manual Review Checklist", "", *[f"- [ ] {item}" for item in checklist]])
    write_text(
        PRESENTED / "final_recommendation.md",
        [
            "# Prompt24 Final Recommendation",
            "",
            "Readiness: `ready_for_research_engine_handoff` and `ready_for_top8_minor_enhancement_planning`.",
            "",
            "Do not promote candidates automatically. Track B parity preparation may begin only after human review of material Prompt22-vs-Prompt23 differences and preserved-control deltas.",
            "",
            "Next action: send the generated external research prompt to a research engine for minor, ablatable top-8 improvements.",
        ],
    )


def write_research_handoffs(top8: list[dict[str, Any]], backlog: list[dict[str, Any]]) -> None:
    top_table = md_table(top8, ("track", "rank", "run_id", "family", "method_stack", "current_status", "recommended_next_use"))
    write_text(
        HANDOFF / "prompt24_research_context.md",
        [
            "# Prompt24 News Overlay Research Context",
            "",
            "Stage 2 - Research Context Export",
            "",
            "This repository implements NLPCC 2026 Shared Task 4 research extensions for a transformer-first News Overlay pipeline. Prompt23 completed a full fresh local-transformer inference matrix. The next research step is minor enhancement planning for the current top-8 candidates, not a new architecture or full grid.",
            "",
            "Rules: tune only on 2024; use 2025 only as frozen test; do not use hidden 2026 data; do not download models; do not call online APIs; keep official runtime untouched.",
            "",
            "## Top-8",
            top_table,
        ],
    )
    cards = ["# Prompt24 Top-8 Candidate Cards", ""]
    for row in top8:
        cards.extend(
            [
                f"## {row['run_id']}",
                "",
                f"- Track: {row['track']}",
                f"- Rank: {row['rank']}",
                f"- Method stack: {row['method_stack']}",
                f"- Architecture: {row['architecture_summary']}",
                f"- Frozen parameters: `{row['frozen_parameters']}`",
                f"- 2024 Sharpe/return: {row['2024_sharpe']} / {row['2024_return']}",
                f"- 2025 Sharpe/return: {row['2025_sharpe']} / {row['2025_return']}",
                f"- Current status: {row['current_status']}",
                f"- Next use: {row['recommended_next_use']}",
                "",
            ]
        )
    write_text(HANDOFF / "prompt24_top8_candidate_cards.md", cards)
    write_text(
        HANDOFF / "prompt24_minor_enhancement_questions.md",
        [
            "# Prompt24 Minor Enhancement Questions",
            "",
            md_table(backlog[:80], ("track", "run_id", "theme", "priority", "question")),
        ],
    )
    write_text(
        HANDOFF / "prompt24_external_research_prompt.md",
        [
            "# External Research Prompt - Prompt24 News Overlay Top-8",
            "",
            "You are advising on minor, implementable, ablatable enhancements to an existing Chinese financial News Overlay system for NLPCC 2026 Shared Task 4.",
            "",
            "Do not propose new large architectures, online LLM calls, hidden 2026 data use, 2025 tuning, large model downloads, unconstrained strategy overrides, or opaque methods that cannot be ablated.",
            "",
            "Strict rule: 2024 is the only tuning period. 2025 is a frozen test period. Official runtime configs must remain untouched.",
            "",
            "Prompt23 caveat: fresh local-transformer inference revised Prompt22 replay results; equivalence counts were 46 confirmed, 71 minor numeric drift, and 95 material differences. Use Prompt23 fresh results as source of truth.",
            "",
            "## Current Top-8",
            top_table,
            "",
            "## Allowed Enhancement Themes",
            *[f"- {theme}" for theme in ALLOWED_THEMES],
            "",
            "## Required Research Output Tables",
            "",
            "1. Candidate-specific minor changes: candidate, change, expected mechanism, implementation files, 2024-only tuning parameters, ablation plan.",
            "2. Risk controls: leakage risk, turnover risk, drawdown risk, dependency risk, official-runtime impact.",
            "3. Prioritised experiment queue: smoke, quick 2024 tune, frozen 2025 test, parity-prep shortlist.",
            "",
            "Avoid vague suggestions. Every proposal must be small enough to implement and ablate against the current frozen parameters.",
        ],
    )


def write_docs_status(top8: list[dict[str, Any]], data: dict[str, Any]) -> None:
    write_text(
        DOCS_NO / "prompt24_top8_status.md",
        [
            "# Prompt24 Top-8 News Overlay Status",
            "",
            "This durable status file freezes the Prompt23 top-8 candidate set for minor-enhancement research handoff.",
            "",
            md_table(top8, ("track", "rank", "run_id", "method_stack", "current_status", "2024_selection_score", "2025_sharpe")),
            "",
            f"Prompt22-vs-Prompt23 equivalence counts: {counts(row['equivalence_verdict'] for row in data['equivalence'])}.",
            "Official-server parity is not run. No candidate is promotion-ready.",
        ],
    )


def write_progress(data: dict[str, Any], top8: list[dict[str, Any]]) -> None:
    write_text(
        PROGRESS / "progress_prompt24.md",
        [
            "# Prompt24 Progress",
            "",
            f"generated_at={datetime.now().isoformat(timespec='seconds')}",
            "rtk_status=available",
            f"top8_rows={len(top8)}",
            f"prompt23_fresh_rows={len(data['fresh'])}",
            f"prompt23_frozen_rows={len(data['frozen'])}",
            "cleanup_actions=file_moves_or_deletions_not_performed",
        ],
    )


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    if not fieldnames:
        fieldnames = ["empty"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_text(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def md_table(rows: list[dict[str, Any]], fields: tuple[str, ...]) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(fields) + " |", "| " + " | ".join("---" for _ in fields) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(field, "")) for field in fields) + " |")
    return "\n".join(lines)


def audit_status(rows: list[dict[str, str]]) -> str:
    if not rows:
        return "missing"
    if all(row.get("status") == "pass" for row in rows):
        return "pass"
    if any(row.get("status") == "fail" for row in rows):
        return "fail"
    return "partial"


def counts(values: Any) -> dict[str, int]:
    result: dict[str, int] = {}
    for value in values:
        result[str(value)] = result.get(str(value), 0) + 1
    return result


def size_bytes(path: Path) -> int:
    if not path.exists():
        return 0
    if path.is_file():
        return path.stat().st_size
    total = 0
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in {".git", ".venv", "venv", "__pycache__", ".pytest_cache"}]
        for name in files:
            file_path = Path(root) / name
            try:
                total += file_path.stat().st_size
            except OSError:
                pass
    return total


def count_files(path: Path) -> int:
    if path.is_file():
        return 1
    count = 0
    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in {".git", ".venv", "venv", "__pycache__", ".pytest_cache"}]
        count += len(files)
    return count


def average_runtime(rows: list[dict[str, str]]) -> float:
    values = [num(row.get("runtime_sec")) for row in rows if row.get("model_mode") == "real_model_executed"]
    return sum(values) / len(values) if values else 60.0


def num(value: Any) -> float:
    try:
        if value is None or value == "":
            return 0.0
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve()))
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
