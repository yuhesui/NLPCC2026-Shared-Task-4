"""Run an experiment config end-to-end and register the result.

Experiment config (YAML, see configs/experiments/):

    experiment:
      family: quant_baseline
      name: q3_shrinkage_erc
      system: configs/systems/q3_shrinkage_erc.yaml
      data: {kind: synthetic, seed: 7, days: 60}          # or {kind: csv, paths: [...], bar_minutes: 30}
      periods: {warmup_days: 20, eval_days: null}           # evaluation = days after warm-up
      text: {enabled: false}                                # or {enabled: true, relevance: lexical_entity, signal: {...}}
      ablation: full
      seed: 7
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import asdict
from pathlib import Path
from typing import Any

from icaif.backtest.engine import BacktestConfig, run_backtest
from icaif.competition.schedule import generate_standard_schedule
from icaif.core.config import REPO_ROOT, deep_merge, load_config
from icaif.data.market.loaders import load_panel_csv
from icaif.data.market.synthetic import SyntheticConfig, generate_synthetic_world
from icaif.experiments.ablations import ablate
from icaif.experiments.registry import ExperimentRecord, ExperimentRegistry, grade
from icaif.nlp.embeddings import HashingEncoder
from icaif.nlp.event_impact import load_event_priors
from icaif.nlp.feature_store import TextSignalConfig, TextStateBuilder
from icaif.nlp.relevance import DenseRelevance, HybridRelevance, LexicalEntityRelevance
from icaif.runtime.agent import build_agent


def _relevance(kind: str) -> Any:
    if kind == "lexical_entity":
        return LexicalEntityRelevance()
    if kind == "dense_hash":
        return DenseRelevance(HashingEncoder())
    if kind == "hybrid_hash":
        return HybridRelevance(LexicalEntityRelevance(), DenseRelevance(HashingEncoder()))
    raise ValueError(f"relevance {kind!r} needs a local model; configure it in configs/embeddings and a custom runner")


def load_data(spec: Mapping[str, Any]) -> tuple[Any, list[Any], dict[str, Any]]:
    kind = spec.get("kind", "synthetic")
    if kind == "synthetic":
        cfg = SyntheticConfig(**{k: v for k, v in spec.items() if k != "kind"})
        world = generate_synthetic_world(cfg)
        return world.panel, world.articles, world.manifest.as_dict()
    if kind == "csv":
        paths = [REPO_ROOT / p for p in spec["paths"]]
        panel = load_panel_csv(paths, bar_minutes=int(spec["bar_minutes"]))
        from icaif.data.provenance import build_file_manifest

        manifest = build_file_manifest(spec.get("name", "csv_bars"), "market_bars", paths,
                                       sources=(panel.source,), synthetic=False).as_dict()
        return panel, [], manifest
    raise ValueError(f"unknown data kind {kind!r}")


def run_experiment(config: Mapping[str, Any] | str | Path, *, registry: ExperimentRegistry | None = None,
                   overrides: Mapping[str, Any] | None = None, write_traces: bool = False) -> dict[str, Any]:
    raw = load_config(config) if isinstance(config, str | Path) else dict(config)
    exp = deep_merge(raw["experiment"], overrides or {})
    system = load_config(exp["system"]) if isinstance(exp["system"], str) else dict(exp["system"])
    system = deep_merge(system, exp.get("system_overrides", {}))
    # Research runs are strict: unexpected exceptions raise instead of silently using the fallback.
    system["strict"] = bool(exp.get("strict", True))
    panel, articles, manifest = load_data(exp.get("data", {"kind": "synthetic"}))
    days = panel.trading_days()
    warm = int(exp.get("periods", {}).get("warmup_days", 20))
    eval_days = days[warm:]
    if exp.get("periods", {}).get("eval_days"):
        eval_days = eval_days[: int(exp["periods"]["eval_days"])]
    if not eval_days:
        raise ValueError("no evaluation days after warm-up")
    schedule = generate_standard_schedule("validation", eval_days)

    text_cfg = exp.get("text", {"enabled": False})
    provider = None
    if text_cfg.get("enabled"):
        excluded = tuple(text_cfg.get("exclude_sources", ()))  # source-removal ablation
        if excluded:
            articles = [a for a in articles if not a.source.startswith(excluded)]
        builder = TextStateBuilder(articles, _relevance(text_cfg.get("relevance", "lexical_entity")), load_event_priors(),
                                   TextSignalConfig.from_mapping(text_cfg.get("signal")))
        provider = ablate(builder, exp.get("ablation", "full"), seed=int(exp.get("seed", 0)))
    agent = build_agent(system)
    registry = registry or ExperimentRegistry()
    bt_cfg = BacktestConfig(**exp.get("backtest", {}))
    probe = ExperimentRecord(exp["family"], exp["name"], {"experiment": exp, "system": system}, manifest, None,
                             [eval_days[0].isoformat(), eval_days[-1].isoformat()], int(exp.get("seed", 0)), {})
    if write_traces:
        bt_cfg = BacktestConfig(**{**asdict(bt_cfg), "trace_dir": registry.path_for(probe.experiment_id) / "traces"})
    result = run_backtest(panel, agent, schedule, "validation", config=bt_cfg, text_provider=provider)
    probe.metrics = result.metrics.as_dict()
    probe.summary = result.summary
    probe.market_sources = [panel.source]
    probe.text_sources = sorted({a.source for a in articles}) if provider else []
    probe.features_used = [str(system.get("pipelines", {}).get(system["fallback_chain"][0], {}).get("alpha", {}))]
    probe.evidence_grade = grade(manifest, fee_overridden=bt_cfg.fee_rate != 0.001)
    probe.notes = str(exp.get("notes", ""))
    probe.summary = {**probe.summary, "alerts": result.alerts}
    if write_traces:
        probe.artifact_paths["traces"] = str(bt_cfg.trace_dir)
    path = registry.register(probe)
    return {"experiment_id": probe.experiment_id, "record": str(path), "metrics": probe.metrics, "summary": probe.summary,
            "evidence_grade": probe.evidence_grade, "alerts": result.alerts}
