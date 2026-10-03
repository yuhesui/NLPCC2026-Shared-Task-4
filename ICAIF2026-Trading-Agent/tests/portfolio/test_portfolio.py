from __future__ import annotations

from datetime import date

import numpy as np
import pytest

from icaif.backtest.execution import execute_target
from icaif.competition.portfolio_state import PortfolioState
from icaif.features.covariance import constant_correlation, fixed_shrinkage, ledoit_wolf, make_psd
from icaif.portfolio.constraints import (
    Constraints,
    ZeroSignalError,
    constraint_violations,
    project_capped_simplex,
    project_to_feasible,
    scale_to_capped_simplex,
)
from icaif.portfolio.exposure import decide_gross, drawdown_gross, vol_target_gross
from icaif.portfolio.fusion import apply_overlay, overlay_budget, transform_scores
from icaif.portfolio.inverse_vol import inverse_vol_weights
from icaif.portfolio.optimizer import objective, optimize
from icaif.portfolio.risk_parity import risk_contributions, solve_erc
from icaif.portfolio.target_weights import InvalidTargetError, finalize_target
from icaif.portfolio.turnover import (
    DailyTurnoverBudget,
    TurnoverConfig,
    TurnoverController,
    cap_turnover,
    l1_turnover,
    no_trade_band,
    sparse_changes,
)

N = 30


def random_cov(rng, n=N):
    a = rng.normal(size=(n, n)) * 0.01
    return a @ a.T + np.eye(n) * 1e-4


# --- constraints --------------------------------------------------------------------------------

@pytest.mark.parametrize("total", [0.0, 0.37, 0.97, 1.0])
def test_capped_simplex_projection_is_feasible_and_optimal(rng, total):
    v = rng.normal(0.05, 0.2, N)
    w = project_capped_simplex(v, 0.30, total)
    assert w.min() >= 0 and w.max() <= 0.30 + 1e-12 and w.sum() == pytest.approx(total, abs=1e-9)
    # optimality: no feasible random point is closer to v
    for _ in range(200):
        z = project_capped_simplex(rng.normal(0, 0.3, N), 0.30, total)
        assert np.sum((w - v) ** 2) <= np.sum((z - v) ** 2) + 1e-12


def test_project_to_feasible_respects_gross_and_long_only(rng):
    cons = Constraints()
    for _ in range(50):
        w = project_to_feasible(rng.normal(0.05, 0.3, N), cons, gross=rng.uniform(0, 1))
        assert not constraint_violations(w, cons)
    assert project_capped_simplex(np.full(4, 1.0), 0.3, 1.2).sum() == pytest.approx(1.2)
    with pytest.raises(ValueError):
        project_capped_simplex(np.ones(3), 0.3, 1.0)  # 3 * 0.3 < 1 infeasible


def test_zero_scores_are_explicit():
    z = np.zeros(N)
    assert scale_to_capped_simplex(z, 0.3, 1.0, on_zero="cash").sum() == 0
    assert scale_to_capped_simplex(z, 0.3, 1.0, on_zero="equal") == pytest.approx(np.full(N, 1 / N))
    with pytest.raises(ZeroSignalError):
        scale_to_capped_simplex(z, 0.3, 1.0, on_zero="raise")


def test_scale_projection_caps_and_redistributes():
    s = np.zeros(N)
    s[:3] = [10.0, 1.0, 1.0]
    w = scale_to_capped_simplex(s, 0.3, 0.9)
    assert w[0] == pytest.approx(0.3) and w[1] == pytest.approx(0.3) and w.sum() == pytest.approx(0.9)


def test_constraints_reject_non_icaif_caps():
    with pytest.raises(ValueError):
        Constraints(max_weight=0.35)
    with pytest.raises(ValueError):
        Constraints(max_gross=1.01)


# --- risk models --------------------------------------------------------------------------------

def test_erc_equalises_risk_contributions(rng):
    cov = random_cov(rng)
    res = solve_erc(cov, 0.8)
    assert res.converged and res.weights.sum() == pytest.approx(0.8)
    rc = risk_contributions(res.weights, cov)
    assert rc.max() - rc.min() < 1e-6
    assert not constraint_violations(res.weights)


def test_legacy_multiplicative_erc_can_fail_where_ccd_converges(rng):
    cov = random_cov(rng)
    assert solve_erc(cov, 1.0).converged
    legacy = solve_erc(cov, 1.0, method="multiplicative", max_iter=500)
    assert legacy.max_rc_error > solve_erc(cov, 1.0).max_rc_error


def test_erc_with_binding_cap():
    cov = np.diag(np.r_[np.full(3, 1e-6), np.full(N - 3, 1e-2)])  # 3 very low-vol assets want huge weight
    res = solve_erc(cov, 1.0)
    assert res.weights.max() <= 0.30 + 1e-12 and res.weights.sum() == pytest.approx(1.0)


def test_inverse_vol_monotone_and_unknown_vol_zero():
    vol = np.linspace(0.01, 0.03, N)
    vol[5] = np.nan
    w = inverse_vol_weights(vol, 0.9)
    assert w[5] == 0 and w.sum() == pytest.approx(0.9) and w[0] > w[10] > w[20]


def test_shrinkage_estimators_psd_and_intensity(rng):
    x = rng.normal(0, 0.01, (60, N))
    for fn in (ledoit_wolf, constant_correlation):
        cov, k = fn(x)
        assert 0 <= k <= 1 and np.linalg.eigvalsh(cov).min() > 0
    cov, a = fixed_shrinkage(x, 0.2)
    assert a == 0.2
    assert np.linalg.eigvalsh(make_psd(-np.eye(3))).min() > 0
    sigma = 1e-4 * (0.5 * np.ones((5, 5)) + 0.5 * np.eye(5)) * np.outer(np.arange(1, 6), np.arange(1, 6))
    big = rng.multivariate_normal(np.zeros(5), sigma, 5000)
    _, k_big = ledoit_wolf(big)
    _, k_small = ledoit_wolf(big[:20])
    assert k_big < k_small  # far from the identity target: more data -> less shrinkage


# --- optimizer ----------------------------------------------------------------------------------

def test_optimizer_feasible_and_beats_alternatives(rng):
    cov = random_cov(rng)
    alpha = rng.normal(0, 0.01, N)
    w_prev = scale_to_capped_simplex(rng.uniform(size=N), 0.3, 0.7)
    res = optimize(alpha, cov, w_prev, lam=2.0, gamma=0.002, gross=0.9)
    assert not constraint_violations(res.weights) and res.weights.sum() <= 0.9 + 1e-9
    best = objective(res.weights, alpha, cov, 2.0, 0.002, w_prev)
    for _ in range(300):
        z = project_to_feasible(res.weights + rng.normal(0, 0.02, N), Constraints(), gross=0.9)
        assert objective(z, alpha, cov, 2.0, 0.002, w_prev) <= best + 1e-9


def test_optimizer_large_gamma_means_no_trade(rng):
    cov = random_cov(rng)
    w_prev = scale_to_capped_simplex(rng.uniform(size=N), 0.3, 0.8)
    res = optimize(rng.normal(0, 0.01, N), cov, w_prev, lam=1.0, gamma=10.0, gross=1.0)
    assert l1_turnover(res.weights, w_prev) < 1e-8


def test_optimizer_rejects_nan():
    with pytest.raises(ValueError):
        optimize(np.full(N, np.nan), np.eye(N), np.zeros(N), lam=1.0, gamma=0.0, gross=1.0)


# --- exposure -----------------------------------------------------------------------------------

def test_gross_exposure_components():
    assert vol_target_gross(0.30, 0.15) == pytest.approx(0.5)
    assert vol_target_gross(float("nan"), 0.15) == 1.0
    assert drawdown_gross(0.05, start=0.02, full=0.08, min_gross=0.3) == pytest.approx(0.65)
    d = decide_gross({"base": 0.9, "min_gross": 0.2, "vol_target": {"target_vol_ann": 0.1}}, predicted_vol_ann=1.0)
    assert d.gross == pytest.approx(0.2) and d.components["vol_target"] == pytest.approx(0.1)
    with pytest.raises(ValueError):
        decide_gross({"vol_target": {"target_vol_ann": 0.1}})


# --- turnover -----------------------------------------------------------------------------------

def test_turnover_is_two_sided_l1():
    a, b = np.zeros(N), np.zeros(N)
    a[0], b[1] = 0.3, 0.3
    assert l1_turnover(a, b) == pytest.approx(0.6)


def test_band_sparse_and_cap(rng):
    cur = scale_to_capped_simplex(rng.uniform(size=N), 0.3, 1.0)
    tgt = cur + rng.normal(0, 0.004, N)
    banded = no_trade_band(tgt, cur, 0.005)
    assert np.all((banded == cur) | (np.abs(tgt - cur) >= 0.005))
    sp = sparse_changes(tgt, cur, 3)
    assert np.count_nonzero(sp - cur) == 3
    capped, blend = cap_turnover(tgt, cur, 0.01)
    assert l1_turnover(capped, cur) == pytest.approx(min(0.01, l1_turnover(tgt, cur)))
    assert 0 < blend <= 1


def test_daily_budget_and_min_change_hold():
    ctl = TurnoverController(TurnoverConfig(max_daily=0.3, min_total_change=0.02))
    cur = np.zeros(N)
    tgt = np.zeros(N)
    tgt[:5] = 0.04
    day = date(2026, 10, 8)
    out = ctl.apply(tgt, cur, day)
    assert not out.hold and l1_turnover(out.weights, cur) == pytest.approx(0.2)
    ctl.commit(day, 0.2)
    out2 = ctl.apply(tgt * 2, cur, day)
    assert l1_turnover(out2.weights, cur) == pytest.approx(0.1)  # only 0.1 left today
    assert ctl.apply(tgt * 2, cur, date(2026, 10, 9)).steps["daily_remaining"] == 0.3  # resets next day
    tiny = cur.copy()
    tiny[0] = 0.01
    assert ctl.apply(tiny, cur, day).hold
    assert DailyTurnoverBudget(1.0).remaining(day) == 1.0


# --- bounded overlay ----------------------------------------------------------------------------

@pytest.mark.parametrize("method", ["linear", "rank", "softmax", "sigmoid", "zscore", "topk"])
def test_overlay_zero_sum_and_budget(rng, method):
    base = scale_to_capped_simplex(rng.uniform(size=N), 0.3, 0.9)
    scores = rng.normal(size=N)
    scores[:4] = np.nan
    res = apply_overlay(base, scores, eta=0.05, transform=method, per_asset_cap=0.01, k=4)
    assert res.intended_delta.sum() == pytest.approx(0.0, abs=1e-12)
    assert np.abs(res.intended_delta).sum() <= 0.05 + 1e-12
    assert np.abs(res.intended_delta).max() <= 0.01 + 1e-12
    assert np.all(res.intended_delta[:4] == 0)  # no information -> no tilt
    assert res.weights.sum() == pytest.approx(base.sum(), abs=1e-9)  # gross preserved
    assert not constraint_violations(res.weights)
    assert transform_scores(scores, method, k=4)[np.isfinite(scores)].mean() == pytest.approx(0.0, abs=1e-12)


def test_overlay_noop_cases(rng):
    base = scale_to_capped_simplex(rng.uniform(size=N), 0.3, 1.0)
    assert np.array_equal(apply_overlay(base, rng.normal(size=N), eta=0.0).weights, base)
    assert np.array_equal(apply_overlay(base, np.full(N, np.nan), eta=0.05).weights, base)
    assert np.array_equal(apply_overlay(base, np.full(N, 0.3), eta=0.05).weights, base)  # no cross-section


def test_overlay_budget_modes():
    eta, parts = overlay_budget({"cap": 0.02, "max_cap": 0.03, "modes": ["confidence", "event"]},
                                confidence=0.5, event_multiplier=4.0)
    assert eta == pytest.approx(0.03) and parts["confidence"] == 0.5
    assert overlay_budget({"cap": 0.02}, confidence=0.0)[0] == 0.02  # confidence ignored unless enabled


# --- finalisation / execution -------------------------------------------------------------------

def test_finalize_leaves_fee_cash_and_rejects_nan():
    cur = np.zeros(N)
    tgt = np.full(N, 1 / N)
    final = finalize_target(tgt, cur)
    assert final.gross <= 1 - 0.001 * 1.0 + 1e-12
    with pytest.raises(InvalidTargetError):
        finalize_target(np.full(N, np.nan), cur)


def test_execution_fee_hold_and_liquidation():
    st = PortfolioState.initial()
    px = np.full(N, 100.0)
    tgt = np.full(N, 0.999 / N)
    fill = execute_target(st, tgt, px)
    assert fill.fee == pytest.approx(0.001 * fill.traded_notional) and fill.traded_notional == pytest.approx(999_000)
    assert fill.state.cash == pytest.approx(1_000_000 - 999_000 - 999.0)
    full = execute_target(st, np.full(N, 1 / N), px)  # would overdraw by the fee -> buys scaled
    assert full.funding_scale < 1 and full.state.cash >= -1e-6
    liq = execute_target(fill.state, np.zeros(N), px)
    assert sum(liq.state.shares) == 0 and liq.fee == pytest.approx(0.001 * 999_000)
