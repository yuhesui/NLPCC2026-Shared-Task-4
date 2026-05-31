#!/usr/bin/env python3
"""Prompt15 compatibility-filtered grid search and evidence reports."""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass, field
import json
from pathlib import Path
import sys
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = REPO_ROOT / "src"
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

from nlpcc.runtime.system_runner import SystemRunner  # noqa: E402
from nlpcc.stage1_news.local_model_loader import LocalModelUnavailable, resolve_local_model_path  # noqa: E402
from nlpcc.stage1_news.pipeline import run_stage1_news_pipeline  # noqa: E402
from tools.backtesting.local_backtester import run_local_backtest  # noqa: E402
from tools.experiments.runner import build_agent  # noqa: E402


REPORT_ROOT = REPO_ROOT / "outputs" / "reports" / "prompt15"
EXPERIMENT_ROOT = REPO_ROOT / "outputs" / "experiments" / "prompt15_grid_search"


@dataclass(frozen=True)
class PipelineSpec:
    name: str
    track: str
    stage1: str
    stage2: str
    stage3: str
    stage4: str
    agent: str
    params: dict[str, Any] = field(default_factory=dict)
    load_news: bool = True
    novelty: float = 0.5
    interpretability: float = 0.6
    ablation_cleanliness: float = 0.7
    visualisability: float = 0.5
    reproducibility: float = 0.8
    report_signal: float = 0.5
    robustness: float = 0.5
    dependency_risk: float = 0.1
    parity_risk: float = 0.4
    overfit_risk: float = 0.2
    implementation_complexity: float = 0.3


class SystemRunnerBacktestAgent:
    def __init__(self, *, track: str, strategy: str, fallback: str):
        self.runner = SystemRunner.for_track(track, strategy=strategy, fallback_strategy=fallback)
        self.track = track

    def make_decision(self, **kwargs: Any) -> dict[str, Any]:
        decision = self.runner.run_day(
            track=kwargs.get("track", self.track),
            fund_pool=kwargs.get("fund_pool"),
            historical_prices=kwargs.get("historical_prices"),
            news=kwargs.get("news"),
            current_portfolio=kwargs.get("current_portfolio"),
        )
        return decision.as_official_decision()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-dates", type=int, default=20)
    parser.add_argument("--top5-2025-max-dates", type=int, default=20)
    parser.add_argument("--lookback-days", type=int, default=60)
    args = parser.parse_args()

    REPORT_ROOT.mkdir(parents=True, exist_ok=True)
    EXPERIMENT_ROOT.mkdir(parents=True, exist_ok=True)

    stage1_report = write_stage1_local_model_report()
    specs = compatibility_filtered_specs()
    results = run_2024_grid(specs, max_dates=args.max_dates, lookback_days=args.lookback_days)
    scored = score_results(results)
    top5 = scored[:5]
    write_grid_reports(scored, top5, max_dates=args.max_dates)
    eval_2025 = run_2025_top5(top5, max_dates=args.top5_2025_max_dates, lookback_days=args.lookback_days)
    write_2025_reports(eval_2025)
    wrapper_rows = run_wrapper_validation(top5, max_dates=min(5, args.max_dates), lookback_days=args.lookback_days)
    write_wrapper_report(wrapper_rows)
    write_evidence_pack(scored, top5, eval_2025, wrapper_rows, stage1_report)
    print(json.dumps({"status": "ok", "result_count": len(scored), "top5": [row["pipeline_name"] for row in top5]}, indent=2))
    return 0


def compatibility_filtered_specs() -> list[PipelineSpec]:
    return [
        PipelineSpec("s0_macro_no_news", "macro", "no_news", "flat_feature_table", "s1_trade_state", "s0_equal_weight", "s0_equal_weight", {"cash_reserve": 0.03, "max_weight": 0.35}, False, parity_risk=0.0, implementation_complexity=0.05),
        PipelineSpec("s1_macro_no_news", "macro", "no_news", "flat_feature_table", "s1_trade_state", "s1_quant_core", "s1_quant_core", {"track": "macro"}, False, parity_risk=0.0, implementation_complexity=0.1),
        PipelineSpec("dro_bl_rp_rule_track1", "macro", "rule_based", "bl_view_confidence", "shrinkage_covariance+risk_budget_state", "dro_bl_rp", "dro_bl_rp", {"track": "macro"}, True, 0.75, 0.82, 0.80, 0.70, 0.85, 0.80, 0.70, 0.1, 0.25, 0.25, 0.35),
        PipelineSpec("dro_bl_rp_hybrid_track1", "macro", "hybrid_rule_bge_finbert", "bl_view_confidence", "shrinkage_covariance+risk_budget_state", "dro_bl_rp", "dro_bl_rp", {"track": "macro", "stage1": _stage1_hybrid_config()}, True, 0.82, 0.85, 0.78, 0.75, 0.75, 0.85, 0.65, 0.35, 0.35, 0.35, 0.45),
        PipelineSpec("bsa_rp_rule_track1", "macro", "rule_based", "belief_state+decayed_event_memory", "risk_budget_state", "bsa_rp", "bsa_rp", {"track": "macro"}, True, 0.70, 0.80, 0.82, 0.75, 0.85, 0.82, 0.68, 0.1, 0.35, 0.22, 0.30),
        PipelineSpec("armor_omd_macro", "macro", "rule_based", "retrieval_analogue_index", "base_allocator_performance", "armor_omd", "armor_omd", {"track": "macro"}, True, 0.72, 0.75, 0.78, 0.68, 0.82, 0.75, 0.72, 0.1, 0.35, 0.22, 0.35),
        PipelineSpec("hgf_mpc_track1", "macro", "no_news", "hidden_state_store", "kalman_drift_state+hmm_regime_state", "hgf_mpc", "hgf_mpc", {"track": "macro"}, False, 0.70, 0.78, 0.72, 0.70, 0.85, 0.78, 0.62, 0.05, 0.40, 0.25, 0.40),
        PipelineSpec("ceva_kf_ciga_track1", "macro", "rule_based", "causal_event_graph", "stable_effect_state+kalman_drift_state", "ceva_kf_ciga", "ceva_kf_ciga", {"track": "macro"}, True, 0.82, 0.85, 0.75, 0.82, 0.82, 0.86, 0.60, 0.1, 0.45, 0.35, 0.45),
        PipelineSpec("s0_sector_no_news", "sector", "no_news", "flat_feature_table", "s1_trade_state", "s0_equal_weight", "s0_equal_weight", {"cash_reserve": 0.03, "max_weight": 0.25}, False, parity_risk=0.0, implementation_complexity=0.05),
        PipelineSpec("s1_sector_no_news", "sector", "no_news", "flat_feature_table", "s1_trade_state", "s1_quant_core", "s1_quant_core", {"track": "sector"}, False, parity_risk=0.0, implementation_complexity=0.1),
        PipelineSpec("sector_rotation_rule_track2", "sector", "rule_based", "knowledge_graph_lite", "sector_trend+correlation_graph", "sector_rotation", "sector_rotation", {"track": "sector"}, True, 0.55, 0.72, 0.70, 0.70, 0.85, 0.70, 0.55, 0.1, 0.55, 0.30, 0.30),
        PipelineSpec("leeqa_rank_rule_track2", "sector", "rule_based", "rank_feature_panel", "s1_trade_state", "leeqa_rank", "leeqa_rank", {"track": "sector"}, True, 0.68, 0.78, 0.78, 0.72, 0.85, 0.76, 0.60, 0.1, 0.45, 0.30, 0.35),
        PipelineSpec("leeqa_rank_finbert_track2", "sector", "finbert_tone_chinese", "rank_feature_panel", "s1_trade_state", "leeqa_rank", "leeqa_rank", {"track": "sector", "stage1": _stage1_finbert_config()}, True, 0.72, 0.78, 0.76, 0.72, 0.72, 0.78, 0.56, 0.30, 0.55, 0.35, 0.42),
        PipelineSpec("kg_moe_lite_rule_track2", "sector", "rule_based", "knowledge_graph_lite+sector_impact_panel", "sector_trend+correlation_graph", "kg_moe_lite", "kg_moe_lite", {"track": "sector"}, True, 0.75, 0.82, 0.75, 0.85, 0.85, 0.88, 0.56, 0.1, 0.50, 0.35, 0.38),
        PipelineSpec("kg_moe_lite_bge_track2", "sector", "bge_small_zh", "knowledge_graph_lite+retrieval_analogue_index", "sector_trend+correlation_graph", "kg_moe_lite", "kg_moe_lite", {"track": "sector", "stage1": _stage1_bge_config()}, True, 0.78, 0.82, 0.73, 0.86, 0.72, 0.88, 0.52, 0.30, 0.60, 0.38, 0.45),
        PipelineSpec("armor_omd_sector", "sector", "rule_based", "retrieval_analogue_index", "base_allocator_performance", "armor_omd", "armor_omd", {"track": "sector"}, True, 0.72, 0.75, 0.78, 0.68, 0.82, 0.75, 0.65, 0.1, 0.45, 0.28, 0.35),
        PipelineSpec("ceva_kf_ciga_track2", "sector", "rule_based", "causal_event_graph", "stable_effect_state+kalman_drift_state", "ceva_kf_ciga", "ceva_kf_ciga", {"track": "sector"}, True, 0.80, 0.84, 0.75, 0.82, 0.82, 0.85, 0.55, 0.1, 0.55, 0.38, 0.45),
    ]


def run_2024_grid(specs: list[PipelineSpec], *, max_dates: int, lookback_days: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for spec in specs:
        output_path = EXPERIMENT_ROOT / f"{spec.name}_2024.json"
        try:
            result = run_local_backtest(
                data_root=REPO_ROOT / "data" / "train_2024",
                track=spec.track,  # type: ignore[arg-type]
                agent=build_agent(spec.agent, spec.params),
                output_path=output_path,
                lookback_days=lookback_days,
                load_news=spec.load_news,
                max_dates=max_dates,
            )
            metrics = result["metrics"]
            rows.append(
                {
                    "pipeline_name": spec.name,
                    "track": spec.track,
                    "stage1": spec.stage1,
                    "stage2": spec.stage2,
                    "stage3": spec.stage3,
                    "stage4": spec.stage4,
                    "status": "ok",
                    "date_range": f"first_{max_dates}_2024_trading_dates",
                    "final_value": result["final_value"],
                    "cum_return": metrics.get("cumulative_return", 0.0),
                    "sharpe": metrics.get("sharpe_ratio", 0.0),
                    "max_drawdown": metrics.get("max_drawdown", 0.0),
                    "turnover": metrics.get("turnover", 0.0),
                    "spec": spec,
                    "notes": "construction-sample run; no 2025 tuning",
                }
            )
        except Exception as exc:
            rows.append(
                {
                    "pipeline_name": spec.name,
                    "track": spec.track,
                    "stage1": spec.stage1,
                    "stage2": spec.stage2,
                    "stage3": spec.stage3,
                    "stage4": spec.stage4,
                    "status": "failed",
                    "date_range": f"first_{max_dates}_2024_trading_dates",
                    "final_value": None,
                    "cum_return": None,
                    "sharpe": None,
                    "max_drawdown": None,
                    "turnover": None,
                    "spec": spec,
                    "notes": f"{type(exc).__name__}:{exc}",
                }
            )
    return rows


def score_results(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    ok_rows = [row for row in rows if row["status"] == "ok"]
    sharpe_scores = _rank_scores(ok_rows, "sharpe", higher=True)
    return_scores = _rank_scores(ok_rows, "cum_return", higher=True)
    dd_scores = _rank_scores(ok_rows, "max_drawdown", higher=False)
    turnover_scores = _rank_scores(ok_rows, "turnover", higher=False)
    for row in rows:
        spec: PipelineSpec = row["spec"]
        if row["status"] != "ok":
            row.update({"competition_score": 0.0, "research_score": 0.0, "overall_score": 0.0, "conservative_score": -1.0})
            continue
        parity_or_wrapper = max(0.0, 1.0 - spec.parity_risk)
        simplicity = max(0.0, 1.0 - spec.implementation_complexity)
        competition = (
            0.30 * sharpe_scores[row["pipeline_name"]]
            + 0.20 * return_scores[row["pipeline_name"]]
            + 0.20 * dd_scores[row["pipeline_name"]]
            + 0.15 * turnover_scores[row["pipeline_name"]]
            + 0.10 * parity_or_wrapper
            + 0.05 * simplicity
        )
        research = (
            0.25 * spec.novelty
            + 0.20 * spec.interpretability
            + 0.20 * spec.ablation_cleanliness
            + 0.15 * spec.visualisability
            + 0.10 * spec.reproducibility
            + 0.10 * spec.report_signal
        )
        overall = 0.55 * competition + 0.30 * research + 0.15 * spec.robustness
        conservative = (
            overall
            - 0.10 * spec.overfit_risk
            - 0.08 * spec.dependency_risk
            - 0.08 * spec.parity_risk
            - 0.05 * spec.implementation_complexity
        )
        row.update(
            {
                "competition_score": round(competition, 6),
                "research_score": round(research, 6),
                "overall_score": round(overall, 6),
                "conservative_score": round(conservative, 6),
            }
        )
    rows.sort(key=lambda item: item["conservative_score"], reverse=True)
    return rows


def run_2025_top5(top5: list[dict[str, Any]], *, max_dates: int, lookback_days: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for rank, row in enumerate(top5, start=1):
        spec: PipelineSpec = row["spec"]
        try:
            result = run_local_backtest(
                data_root=REPO_ROOT / "data" / "public_a_2025",
                track=spec.track,  # type: ignore[arg-type]
                agent=build_agent(spec.agent, spec.params),
                output_path=EXPERIMENT_ROOT / f"{spec.name}_2025.json",
                lookback_days=lookback_days,
                load_news=spec.load_news,
                max_dates=max_dates,
            )
            metrics = result["metrics"]
            generalisation = _generalisation(row["cum_return"], metrics.get("cumulative_return", 0.0))
            rows.append(
                {
                    "rank": rank,
                    "pipeline_name": spec.name,
                    "track": spec.track,
                    "rank_2024": rank,
                    "final_value": result["final_value"],
                    "cum_return": metrics.get("cumulative_return", 0.0),
                    "sharpe": metrics.get("sharpe_ratio", 0.0),
                    "max_drawdown": metrics.get("max_drawdown", 0.0),
                    "turnover": metrics.get("turnover", 0.0),
                    "generalisation": generalisation,
                    "promote": "yes" if generalisation in {"strong", "acceptable"} else "hold",
                    "notes": f"locked 2025 sample first {max_dates} dates; no parameter changes",
                }
            )
        except Exception as exc:
            rows.append(
                {
                    "rank": rank,
                    "pipeline_name": spec.name,
                    "track": spec.track,
                    "rank_2024": rank,
                    "final_value": None,
                    "cum_return": None,
                    "sharpe": None,
                    "max_drawdown": None,
                    "turnover": None,
                    "generalisation": "not_run",
                    "promote": "no",
                    "notes": f"{type(exc).__name__}:{exc}",
                }
            )
    return rows


def run_wrapper_validation(top5: list[dict[str, Any]], *, max_dates: int, lookback_days: int) -> list[dict[str, Any]]:
    baseline = [
        ("s0_macro", "macro", "s0_equal_weight", "s1_macro", "pass", "Prompt14 official parity passed."),
        ("s1_macro", "macro", "s1_macro", "s1_macro", "pass", "Prompt14 official parity passed."),
        ("s1_sector", "sector", "s1_sector", "s1_sector", "pass", "Prompt14 official parity passed."),
    ]
    rows: list[dict[str, Any]] = []
    for name, track, strategy, fallback, status, notes in baseline:
        value = _wrapper_value(strategy, track, fallback, max_dates=max_dates, lookback_days=lookback_days)
        rows.append(
            {
                "pipeline": name,
                "track": track,
                "date_range": f"first_{max_dates}_2024_trading_dates",
                "local_wrapper_value": value,
                "official_value": None,
                "abs_diff": None,
                "rel_diff": None,
                "trade_match": "see_prompt14",
                "value_match": "see_prompt14",
                "status": status,
                "notes": notes,
            }
        )
    for row in top5:
        spec: PipelineSpec = row["spec"]
        strategy = _strategy_name_for_spec(spec)
        fallback = "s1_sector" if spec.track == "sector" else "s1_macro"
        try:
            value = _wrapper_value(strategy, spec.track, fallback, max_dates=max_dates, lookback_days=lookback_days)
            status = "not_run" if strategy not in {"s0_equal_weight", "s1_macro", "s1_sector"} else "pass"
            notes = "Local wrapper path ran; official server rerun still required for this candidate."
        except Exception as exc:
            value = None
            status = "blocked"
            notes = f"{type(exc).__name__}:{exc}"
        rows.append(
            {
                "pipeline": spec.name,
                "track": spec.track,
                "date_range": f"first_{max_dates}_2024_trading_dates",
                "local_wrapper_value": value,
                "official_value": None,
                "abs_diff": None,
                "rel_diff": None,
                "trade_match": "not_run",
                "value_match": "not_run",
                "status": status,
                "notes": notes,
            }
        )
    return rows


def _wrapper_value(strategy: str, track: str, fallback: str, *, max_dates: int, lookback_days: int) -> float:
    result = run_local_backtest(
        data_root=REPO_ROOT / "data" / "train_2024",
        track=track,  # type: ignore[arg-type]
        agent=SystemRunnerBacktestAgent(track=track, strategy=strategy, fallback=fallback),
        lookback_days=lookback_days,
        load_news=True,
        max_dates=max_dates,
    )
    return float(result["final_value"])


def write_stage1_local_model_report() -> list[dict[str, str]]:
    models = [
        ("rule_based_extractor", "none", "n/a", "yes", "yes", "events, tags, BL views, sector impact", "n/a", "ok"),
        ("bge_small_zh_embedding_extractor", "BAAI/bge-small-zh-v1.5", "pending", "yes", "no", "embedding_ref, vector_preview, relevance_score, metadata", "rule_based", "ok"),
        ("finbert_tone_chinese_sentiment_extractor", "yiyanghkust/finbert-tone-chinese", "pending", "yes", "no", "sentiment label/score/confidence, metadata", "rule_based", "ok"),
        ("hybrid_rule_bge_finbert_extractor", "BGE + FinBERT", "pending", "yes", "no", "rule events + FinBERT sentiment + BGE refs", "rule_based", "ok"),
        ("no_llm_fallback", "none", "n/a", "yes", "yes", "fallback diagnostics", "n/a", "ok"),
    ]
    rows: list[dict[str, str]] = []
    for extractor, model, path, offline, default, fields, fallback, status in models:
        if model.startswith("BAAI") or model.startswith("yiyang"):
            try:
                path = str(resolve_local_model_path(model))
            except LocalModelUnavailable as exc:
                path = str(exc)
                status = "blocked"
        elif model == "BGE + FinBERT":
            try:
                bge = str(resolve_local_model_path("BAAI/bge-small-zh-v1.5"))
                finbert = str(resolve_local_model_path("yiyanghkust/finbert-tone-chinese"))
                path = f"BGE={bge}; FinBERT={finbert}"
            except LocalModelUnavailable as exc:
                path = str(exc)
                status = "blocked"
        rows.append(
            {
                "Extractor": extractor,
                "Model": model,
                "Local Path Source": path,
                "Offline?": offline,
                "Runtime Default?": default,
                "Output Fields": fields,
                "Fallback": fallback,
                "Status": status,
                "Notes": "No silent download; default production config keeps text_model.enabled=false.",
            }
        )
    _write_md_table(REPORT_ROOT / "stage1_local_model_integration_report.md", "# Prompt15 Stage 1 Local Model Integration Report\n\n", rows)
    return rows


def write_grid_reports(rows: list[dict[str, Any]], top5: list[dict[str, Any]], *, max_dates: int) -> None:
    csv_path = REPORT_ROOT / "grid_search_results.csv"
    fields = [
        "pipeline_name",
        "track",
        "stage1",
        "stage2",
        "stage3",
        "stage4",
        "status",
        "date_range",
        "final_value",
        "cum_return",
        "sharpe",
        "max_drawdown",
        "turnover",
        "competition_score",
        "research_score",
        "overall_score",
        "conservative_score",
        "notes",
    ]
    _write_csv(csv_path, [{field: row.get(field) for field in fields} for row in rows], fields)
    top_rows = []
    for rank, row in enumerate(top5, start=1):
        top_rows.append(
            {
                "Rank": rank,
                "Pipeline Name": row["pipeline_name"],
                "Stage 1": row["stage1"],
                "Stage 2": row["stage2"],
                "Stage 3": row["stage3"],
                "Stage 4": row["stage4"],
                "Track": row["track"],
                "2024 Sharpe": _fmt(row["sharpe"]),
                "2024 Return": _fmt(row["cum_return"]),
                "Drawdown": _fmt(row["max_drawdown"]),
                "Turnover": _fmt(row["turnover"]),
                "Competition Score": _fmt(row["competition_score"]),
                "Research Score": _fmt(row["research_score"]),
                "Conservative Score": _fmt(row["conservative_score"]),
                "Promote?": "candidate" if row["status"] == "ok" else "no",
                "Notes": row["notes"],
            }
        )
    _write_md_table(REPORT_ROOT / "top5_candidate_pipelines.md", "# Prompt15 Top 5 Candidate Pipelines\n\n", top_rows)
    summary = [
        "# Prompt15 Grid Search Summary",
        "",
        f"Coverage: compatibility-filtered grid over {len(rows)} pipelines.",
        f"Date coverage: first {max_dates} 2024 trading dates. This is construction-sample evidence, not full-year final evidence.",
        "Scoring policy: 2024-only selection; no 2025 parameters were changed.",
        "",
        f"Top candidate: {top5[0]['pipeline_name'] if top5 else 'none'}.",
        "",
        "See `grid_search_results.csv` and `top5_candidate_pipelines.md` for details.",
    ]
    (REPORT_ROOT / "grid_search_summary.md").write_text("\n".join(summary) + "\n", encoding="utf-8")


def write_2025_reports(rows: list[dict[str, Any]]) -> None:
    fields = [
        "rank",
        "pipeline_name",
        "track",
        "rank_2024",
        "final_value",
        "cum_return",
        "sharpe",
        "max_drawdown",
        "turnover",
        "generalisation",
        "promote",
        "notes",
    ]
    _write_csv(REPORT_ROOT / "top5_2025_evaluation.csv", rows, fields)
    md_rows = [
        {
            "Rank": row["rank"],
            "Pipeline Name": row["pipeline_name"],
            "Track": row["track"],
            "2024 Rank": row["rank_2024"],
            "2025 Final Value": _fmt(row["final_value"]),
            "2025 Return": _fmt(row["cum_return"]),
            "2025 Sharpe": _fmt(row["sharpe"]),
            "2025 Drawdown": _fmt(row["max_drawdown"]),
            "2025 Turnover": _fmt(row["turnover"]),
            "Generalisation": row["generalisation"],
            "Promote?": row["promote"],
            "Notes": row["notes"],
        }
        for row in rows
    ]
    _write_md_table(
        REPORT_ROOT / "top5_2025_evaluation.md",
        "# Prompt15 Top 5 Locked 2025 Evaluation\n\n2025 tuning policy: no parameter changes were made based on these results during this audit.\n\n",
        md_rows,
    )


def write_wrapper_report(rows: list[dict[str, Any]]) -> None:
    md_rows = [
        {
            "Pipeline": row["pipeline"],
            "Track": row["track"],
            "Date Range": row["date_range"],
            "Local Wrapper Value": _fmt(row["local_wrapper_value"]),
            "Official Value": _fmt(row["official_value"]),
            "Abs Diff": _fmt(row["abs_diff"]),
            "Rel Diff": _fmt(row["rel_diff"]),
            "Trade Match?": row["trade_match"],
            "Value Match?": row["value_match"],
            "Status": row["status"],
            "Notes": row["notes"],
        }
        for row in rows
    ]
    _write_md_table(REPORT_ROOT / "wrapper_parity_validation.md", "# Prompt15 Wrapper Parity Validation\n\n", md_rows)


def write_evidence_pack(
    rows: list[dict[str, Any]],
    top5: list[dict[str, Any]],
    eval_2025: list[dict[str, Any]],
    wrapper_rows: list[dict[str, Any]],
    stage1_rows: list[dict[str, str]],
) -> None:
    final_metrics_fields = ["pipeline_name", "track", "cum_return", "sharpe", "max_drawdown", "turnover", "conservative_score"]
    _write_csv(REPORT_ROOT / "final_metrics_summary.csv", [{field: row.get(field) for field in final_metrics_fields} for row in rows], final_metrics_fields)
    status_lines = [
        "# Prompt15 Model Implementation Status",
        "",
        "| Method | Status | Evidence | Default? | Caveat |",
        "|---|---|---|---|---|",
        "| DRO-BL-RP | functional_mvp | `dro_bl_rp_agent.py`, config, grid row | candidate | Robust BL parity still needs official rerun. |",
        "| BSA-RP | functional_mvp | `bsa_rp_agent.py`, belief state, tests | no | Prototype scoring. |",
        "| ARMOR-OMD | functional_mvp | `armor_omd_agent.py`, base allocator state | no | Exponentiated-weight MVP, not full OCO proof. |",
        "| LEEQA-Rank | functional_mvp | `leeqa_rank_agent.py`, rank feature panel | Track B candidate if evidence supports | Deterministic ranker, not trained LTR. |",
        "| KG-MoE-Lite | functional_mvp | existing agent plus graph store | Track B report candidate | Lite router, not full GNN/MoE. |",
        "| HGF-MPC | functional_mvp | `hgf_mpc_agent.py`, Kalman/HMM state | no | One-step controller. |",
        "| CEVA-KF/CIGA | functional_mvp | `ceva_kf_ciga_agent.py`, causal graph | no | Stable-effect graph MVP, not causal discovery. |",
    ]
    (REPORT_ROOT / "model_implementation_status.md").write_text("\n".join(status_lines) + "\n", encoding="utf-8")
    ablation = [
        "# Prompt15 Final Ablation Summary",
        "",
        "The compatibility-filtered grid includes S0, S1, DRO-BL-RP, BSA-RP, ARMOR-OMD, LEEQA-Rank, KG-MoE-Lite, HGF-MPC, CEVA-KF/CIGA, and sector rotation.",
        "Selection is based on 2024 construction-sample evidence only; 2025 rows are locked evaluation only.",
    ]
    (REPORT_ROOT / "final_ablation_summary.md").write_text("\n".join(ablation) + "\n", encoding="utf-8")
    decision_examples = [
        "# Prompt15 Final Decision Trace Examples",
        "",
        "Wrapper traces were generated for S0/S1 and top candidates over the short local-wrapper window.",
        "",
        json.dumps(wrapper_rows[:3], indent=2, ensure_ascii=False),
    ]
    (REPORT_ROOT / "final_decision_trace_examples.md").write_text("\n".join(decision_examples) + "\n", encoding="utf-8")
    pack = [
        "# Prompt15 Final System Evidence Pack",
        "",
        "## Implemented Methods",
        "",
        "DRO-BL-RP, BSA-RP, ARMOR-OMD, LEEQA-Rank, KG-MoE-Lite, HGF-MPC, and CEVA-KF/CIGA now have functional MVP code paths.",
        "",
        "## Stage 1 Local Model Usage",
        "",
        f"Local model extractor rows: {len(stage1_rows)}. Runtime default remains disabled with rule-based fallback.",
        "",
        "## Overall Top 5",
        "",
    ]
    for rank, row in enumerate(top5, start=1):
        pack.append(f"{rank}. {row['pipeline_name']} ({row['track']}) conservative_score={row['conservative_score']}")
    pack.extend(
        [
            "",
            "## 2025 Locked Evaluation",
            "",
            f"Evaluated top {len(eval_2025)} only. No tuning based on 2025.",
            "",
            "## Wrapper / Parity Status",
            "",
            "S0/S1 parity remains inherited from Prompt14. New top candidates ran through local wrapper but still need official server rerun.",
            "",
            "## Known Caveats",
            "",
            "Grid evidence produced here is a runtime-bounded construction sample, not final full-year evidence.",
        ]
    )
    (REPORT_ROOT / "final_system_evidence_pack.md").write_text("\n".join(pack) + "\n", encoding="utf-8")


def _strategy_name_for_spec(spec: PipelineSpec) -> str:
    mapping = {
        "s0_macro_no_news": "s0_equal_weight",
        "s1_macro_no_news": "s1_macro",
        "s0_sector_no_news": "s0_equal_weight",
        "s1_sector_no_news": "s1_sector",
        "dro_bl_rp_rule_track1": "dro_bl_rp_track1",
        "dro_bl_rp_hybrid_track1": "dro_bl_rp_track1",
        "bsa_rp_rule_track1": "bsa_rp_track1",
        "armor_omd_macro": "armor_omd_macro",
        "hgf_mpc_track1": "hgf_mpc_track1",
        "ceva_kf_ciga_track1": "ceva_kf_ciga_track1",
        "sector_rotation_rule_track2": "sector_rotation_track2",
        "leeqa_rank_rule_track2": "leeqa_rank_track2",
        "leeqa_rank_finbert_track2": "leeqa_rank_track2",
        "kg_moe_lite_rule_track2": "kg_moe_lite_track2",
        "kg_moe_lite_bge_track2": "kg_moe_lite_track2",
        "armor_omd_sector": "armor_omd_sector",
        "ceva_kf_ciga_track2": "ceva_kf_ciga_track2",
    }
    return mapping.get(spec.name, spec.stage4)


def _stage1_finbert_config() -> dict[str, Any]:
    return {
        "extractor": "finbert_tone_chinese",
        "top_rank": 20,
        "use_llm": False,
        "text_model": {
            "enabled": True,
            "provider": "local_huggingface",
            "model_name": "yiyanghkust/finbert-tone-chinese",
            "offline_only": True,
            "fallback": "rule_based",
        },
    }


def _stage1_bge_config() -> dict[str, Any]:
    return {
        "extractor": "bge_small_zh",
        "top_rank": 20,
        "use_llm": False,
        "text_model": {
            "enabled": True,
            "provider": "local_huggingface",
            "model_name": "BAAI/bge-small-zh-v1.5",
            "offline_only": True,
            "fallback": "rule_based",
        },
    }


def _stage1_hybrid_config() -> dict[str, Any]:
    return {
        "extractor": "hybrid_rule_bge_finbert",
        "top_rank": 20,
        "use_llm": False,
        "text_model": {
            "enabled": True,
            "provider": "local_huggingface",
            "model_name": None,
            "offline_only": True,
            "fallback": "rule_based",
        },
    }


def _rank_scores(rows: list[dict[str, Any]], key: str, *, higher: bool) -> dict[str, float]:
    valid = [row for row in rows if row.get(key) is not None]
    sorted_rows = sorted(valid, key=lambda row: row[key], reverse=higher)
    if not sorted_rows:
        return {}
    if len(sorted_rows) == 1:
        return {sorted_rows[0]["pipeline_name"]: 1.0}
    scores: dict[str, float] = {}
    for idx, row in enumerate(sorted_rows):
        scores[row["pipeline_name"]] = 1.0 - (idx / (len(sorted_rows) - 1))
    return scores


def _generalisation(return_2024: float | None, return_2025: float) -> str:
    if return_2024 is None:
        return "not_run"
    if return_2025 > 0 and return_2025 >= 0.5 * max(return_2024, 0.001):
        return "strong"
    if return_2025 > -0.01:
        return "acceptable"
    if return_2025 > -0.04:
        return "weak"
    return "failed"


def _write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _write_md_table(path: Path, prefix: str, rows: list[dict[str, Any]]) -> None:
    if not rows:
        path.write_text(prefix + "No rows.\n", encoding="utf-8")
        return
    headers = list(rows[0])
    lines = [prefix.rstrip(), "", "| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(header, "")) for header in headers) + " |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _fmt(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, float):
        return f"{value:.6f}"
    return str(value)


if __name__ == "__main__":
    raise SystemExit(main())
