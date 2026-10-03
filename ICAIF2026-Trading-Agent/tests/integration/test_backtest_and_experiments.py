from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest

from icaif.backtest.engine import BacktestConfig, CostsDisabledError, run_backtest
from icaif.core import constants
from icaif.core.config import REPO_ROOT, load_config
from icaif.experiments.matrix import expand_matrix
from icaif.experiments.registry import DuplicateExperimentError, ExperimentRegistry
from icaif.experiments.reporting import markdown_table
from icaif.experiments.runner import run_experiment
from icaif.runtime.agent import build_agent

EQUAL = {"name": "eq", "fallback_chain": ["p"], "strict": True,
         "pipelines": {"p": {"base": {"method": "equal"}, "turnover": {}}}}


def test_costs_cannot_be_disabled():
    with pytest.raises(CostsDisabledError):
        BacktestConfig(fee_rate=0.0)
    with pytest.raises(CostsDisabledError):
        BacktestConfig(fee_rate=0.0, research_fee_override=True)  # still "serious"
    assert BacktestConfig(fee_rate=0.0, serious=False, research_fee_override=True).fee_rate == 0.0


def test_buy_and_hold_holds_and_charges_initial_fee(world, eval_schedule):
    system = {**EQUAL, "pipelines": {"p": {"base": {"method": "equal"}, "rebalance": {"mode": "once"}, "turnover": {}}}}
    r = run_backtest(world.panel, build_agent(system), eval_schedule, "validation")
    assert r.rounds[0]["action"] == "SUBMIT" and all(x["action"] == "HOLD" for x in r.rounds[1:])
    assert r.rounds[0]["fee"] == pytest.approx(0.001 * r.rounds[0]["traded_notional"])
    assert all(x["fee"] == 0 and x["traded_notional"] == 0 for x in r.rounds[1:])  # missing decision -> no fee
    shares = np.asarray(r.final_state.shares)
    assert np.all(shares > 0)
    assert r.metrics.turnover == pytest.approx(r.rounds[0]["round_turnover"] / len(r.rounds))


def test_period_accounting_and_valuation_points(world, eval_schedule):
    r = run_backtest(world.panel, build_agent(EQUAL), eval_schedule, "validation")
    assert len(r.periods) == len(eval_schedule.rounds) == r.metrics.periods
    for a, b in zip(r.periods, r.periods[1:], strict=False):
        assert b.nav_before == pytest.approx(a.nav_after_period)
    times = [t for t, _ in r.valuation_points]
    assert times == sorted(times) and len(times) == len(set(times))
    # initial + every endpoint + daily closes, final close shared with last endpoint
    assert len(times) == 1 + len(r.periods) + (len(eval_schedule.trading_days("validation")) - 1)
    assert r.synthetic_data


def test_cash_baseline_is_flat(world, eval_schedule):
    system = {**EQUAL, "pipelines": {"p": {"base": {"method": "cash"}, "exposure": {"base": 0.0}, "turnover": {}}}}
    r = run_backtest(world.panel, build_agent(system), eval_schedule, "validation")
    assert r.metrics.cumulative_return == 0 and r.metrics.maximum_drawdown == 0 and r.metrics.turnover == 0


def test_experiment_ids_deterministic_and_results_reproducible(tmp_path):
    reg = ExperimentRegistry(tmp_path)
    exp = {"experiment": {"family": "t", "name": "q3", "system": "configs/systems/q3_shrinkage_erc.yaml",
                          "data": {"kind": "synthetic", "seed": 3, "days": 26}, "periods": {"warmup_days": 22}, "seed": 3}}
    a = run_experiment(exp, registry=reg)
    b = run_experiment(exp, registry=reg)
    assert a["experiment_id"] == b["experiment_id"] and a["metrics"] == b["metrics"]
    assert a["evidence_grade"] == "synthetic_plumbing"
    c = run_experiment({"experiment": {**exp["experiment"], "seed": 4}}, registry=reg)
    assert c["experiment_id"] != a["experiment_id"]
    rec = reg.load_all()[0]
    for key in ("experiment_id", "git_commit", "dataset_manifest", "validation_period", "config_hash", "seed", "metrics"):
        assert key in rec
    assert (tmp_path / "index.csv").read_text().count("\n") == 3  # header + 2 distinct experiments
    assert "synthetic_plumbing" in markdown_table(reg.load_all())
    path = Path(a["record"])
    body = path.read_text().replace('"cumulative_return": ', '"cumulative_return": 9', 1)
    path.write_text(body)
    with pytest.raises(DuplicateExperimentError):
        run_experiment(exp, registry=reg)


def test_text_experiment_with_ablation_runs(tmp_path):
    exp = {"experiment": {"family": "t", "name": "n1", "system": "configs/systems/n1_erc_text_overlay.yaml",
                          "data": {"kind": "synthetic", "seed": 3, "days": 26}, "periods": {"warmup_days": 23},
                          "text": {"enabled": True, "relevance": "lexical_entity"}, "ablation": "shuffled", "seed": 1}}
    out = run_experiment(exp, registry=ExperimentRegistry(tmp_path), write_traces=True)
    traces = list(Path(out["record"]).parent.joinpath("traces").glob("*.trace.json"))
    assert traces and out["metrics"]["periods"] == 21


def test_matrix_expansion():
    matrix = load_config("configs/experiments/initial_matrix.yaml")
    items = list(expand_matrix(matrix))
    names = [(f, e["name"]) for f, e in items]
    assert len(names) == len(set(names))
    fams = {f for f, _ in items}
    assert {"quant_baselines", "momentum_horizons", "text_ablations", "overlay_caps", "exposure_policies"} <= fams
    assert "embedding_models" not in fams  # blocked families are not run
    horizons = [e for f, e in items if f == "momentum_horizons"]
    assert sorted(e["system_overrides"]["pipelines"]["primary"]["alpha"]["horizon"] for e in horizons) == sorted(
        ["1h", "2h", "4h", "1d", "5d", "20d"])


def test_all_system_configs_build():
    for path in sorted((REPO_ROOT / "configs" / "systems").glob("[!_]*.yaml")):
        cfg = load_config(path)
        agent = build_agent(cfg)
        assert agent.policy.chain[0] == "primary", path.name


def test_competition_config_matches_constants():
    cfg = load_config("configs/competition/icaif2026.yaml")
    assert cfg["fee_rate"] == constants.FEE_RATE and cfg["max_weight"] == constants.MAX_WEIGHT
    assert tuple(cfg["round_deadlines_et"]) == constants.ROUND_DEADLINES_ET
    assert tuple(cfg["round_execution_times_et"]) == constants.ROUND_EXECUTION_TIMES_ET
    assert cfg["sharpe_annualisation"] ** 2 == 252 * 7


@pytest.mark.parametrize("path", sorted((REPO_ROOT / "configs" / "systems").glob("[!_]*.yaml")), ids=lambda p: p.stem)
def test_every_system_runs_its_primary_pipeline_strictly(world, path):
    """Regression: a wiring bug once made Q6 fail every round while the fallback silently traded."""

    from icaif.competition.schedule import generate_standard_schedule
    from icaif.experiments.runner import TextStateBuilder, _relevance, load_event_priors

    cfg = load_config(path)
    cfg["strict"] = True
    sched = generate_standard_schedule("validation", world.panel.trading_days()[24:25])
    text = None
    if cfg["pipelines"]["primary"].get("overlay", {}).get("enabled"):
        text = TextStateBuilder(world.articles, _relevance("lexical_entity"), load_event_priors())
    r = run_backtest(world.panel, build_agent(cfg), sched, "validation", text_provider=text)
    assert not any(row["fallback"] for row in r.rounds), path.name
    assert all(row["pipeline"] in ("primary", None) for row in r.rounds)
