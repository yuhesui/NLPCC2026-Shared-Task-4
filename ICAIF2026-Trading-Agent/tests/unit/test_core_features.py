from __future__ import annotations

from datetime import date, timedelta

import numpy as np
import pytest

from conftest import utc
from icaif.backtest.walk_forward import walk_forward_windows
from icaif.core.config import ConfigError, config_hash, load_config
from icaif.core.leakage_guard import LeakageViolation
from icaif.core.schemas import content_hash
from icaif.core.universe import N_ASSETS, SECTOR_OF, SYMBOLS, sector_members, validate_symbol_set
from icaif.features.cross_sectional import rank_score, sector_demean, zscore
from icaif.features.momentum import momentum, multi_horizon_score
from icaif.features.regime import regime_state
from icaif.models.ensemble.expert_weights import ExpertWeights
from icaif.models.text.linear import fit_ridge


def test_universe_invariants():
    assert N_ASSETS == 30 and len(set(SYMBOLS)) == 30
    assert sector_members("AAPL") == ("MSFT", "NVDA", "INTC", "CRM") and SECTOR_OF["NEE"] == "Communication & Utilities"
    validate_symbol_set(list(SYMBOLS))
    with pytest.raises(ValueError):
        validate_symbol_set(list(SYMBOLS[:-1]) + ["SPY"])


def test_config_extends_and_hash(tmp_path):
    (tmp_path / "base.yaml").write_text("a: 1\nnested: {x: 1, y: 2}\nlist: [1, 2]\n")
    (tmp_path / "child.yaml").write_text("extends: base.yaml\nnested: {y: 3}\nlist: [9]\n")
    cfg = load_config(tmp_path / "child.yaml")
    assert cfg == {"a": 1, "nested": {"x": 1, "y": 3}, "list": [9]}
    assert config_hash(cfg) == config_hash({"list": [9], "nested": {"y": 3, "x": 1}, "a": 1})
    (tmp_path / "loop.yaml").write_text("extends: loop.yaml\n")
    with pytest.raises(ConfigError):
        load_config(tmp_path / "loop.yaml")
    assert content_hash({"b": 1, "a": 2}) == content_hash({"a": 2, "b": 1})


def test_horizon_to_bars_and_momentum(world):
    view = world.panel.as_of(world.panel.available_at[-1])
    assert view.bars(1.0) == 2 and view.bars(6.5) == 13 and view.bars(130.0) == 260
    m = momentum(view, "1d")
    expected = view.close[-1] / view.close[-14] - 1
    assert np.allclose(m, expected)
    short = world.panel.as_of(world.panel.available_at[5])
    assert np.isnan(momentum(short, "20d")).all()
    s = multi_horizon_score(short, {"20d": 1.0})  # missing horizon -> zero score, not an error
    assert np.all(s == 0)


def test_cross_sectional_transforms():
    x = np.arange(30, dtype=float)
    x[3] = np.nan
    z = zscore(x)
    assert np.isnan(z[3]) and abs(np.nanmean(z)) < 1e-12
    r = rank_score(x)
    assert np.nanmin(r) == -1 and np.nanmax(r) == 1
    d = sector_demean(np.arange(30, dtype=float))
    assert abs(d[:5].sum()) < 1e-12


def test_regime_state_bounds(world):
    rs = regime_state(world.panel.as_of(world.panel.available_at[-1]))
    assert 0 <= rs.breadth <= 1 and 0 <= rs.vol_percentile <= 1 and rs.index_drawdown >= 0


def test_walk_forward_windows_have_embargo():
    days = [date(2026, 1, 1) + timedelta(days=i) for i in range(30)]
    wins = walk_forward_windows(days, train_days=10, test_days=5, step_days=5, embargo_days=2)
    assert wins and all(test[0] > train[-1] + timedelta(days=2) for train, test in wins)


def test_expert_weights_learn_from_realised_returns():
    ew = ExpertWeights(2, learning_rate=50.0)
    for _ in range(20):
        ew.update(np.array([0.01, -0.01]))
    assert ew.weights[0] > 0.9 and ew.weights.sum() == pytest.approx(1.0)
    targets = np.array([np.full(30, 1 / 30), np.zeros(30)])
    assert ew.blend(targets).sum() <= 1.0


def test_ridge_text_model_records_cutoff(rng):
    x = rng.normal(size=(50, 3))
    y = x @ np.array([1.0, -0.5, 0.0]) + rng.normal(0, 0.01, 50)
    ends = [utc(2026, 1, 1) + timedelta(hours=i) for i in range(50)]
    model = fit_ridge(x, y, ends, train_end=utc(2026, 1, 5), feature_names=("a", "b", "c"), l2=1e-3)
    assert np.allclose(model.coef, [1.0, -0.5, 0.0], atol=0.05) and model.trained_through == utc(2026, 1, 5)
    with pytest.raises(LeakageViolation):
        fit_ridge(x, y, ends, train_end=utc(2026, 1, 2), feature_names=("a", "b", "c"))
