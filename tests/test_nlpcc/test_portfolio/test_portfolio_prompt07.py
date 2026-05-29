import numpy as np

from nlpcc.portfolio.black_litterman import black_litterman_posterior, build_bl_inputs
from nlpcc.portfolio.constraints import PortfolioConstraints, validate_weight_constraints
from nlpcc.portfolio.risk_parity import covariance_to_matrix, solve_risk_parity_weights
from nlpcc.portfolio.robust_optimizer import OptimizerConfig, optimize_long_only_mean_variance
from nlpcc.portfolio.target_weights import weights_to_vector
from nlpcc.portfolio.turnover_control import apply_turnover_limit, portfolio_turnover
from nlpcc.stage2_text_store.schema import BLViewRecord, ConfidenceMatrix, DecayedEventMemory, Stage2TextState


def _covariance() -> dict[str, dict[str, float]]:
    return {
        "000300.SH": {"000300.SH": 0.0004, "399006.SZ": 0.0001, "518880.SH": 0.00002},
        "399006.SZ": {"000300.SH": 0.0001, "399006.SZ": 0.0009, "518880.SH": 0.00001},
        "518880.SH": {"000300.SH": 0.00002, "399006.SZ": 0.00001, "518880.SH": 0.0002},
    }


def test_risk_parity_weights_are_long_only_capped_and_invested() -> None:
    assets = ("000300.SH", "399006.SZ", "518880.SH")
    constraints = PortfolioConstraints(max_weight=0.5, cash_reserve=0.03)

    weights = solve_risk_parity_weights(_covariance(), assets, constraints=constraints)

    assert not validate_weight_constraints(weights, constraints)
    assert abs(sum(weights.values()) - 0.97) < 1e-8
    assert max(weights.values()) <= 0.5 + 1e-8


def test_turnover_limit_preserves_cap() -> None:
    constraints = PortfolioConstraints(max_weight=0.7, cash_reserve=0.03, max_turnover=0.10)
    current = {"000300.SH": 0.7}
    target = {"399006.SZ": 0.7}

    limited = apply_turnover_limit(target, current, constraints)

    assert portfolio_turnover(current, limited) <= 0.10 + 1e-8
    assert not validate_weight_constraints(limited, constraints)


def test_black_litterman_and_robust_optimizer_produce_valid_weights() -> None:
    assets = ("000300.SH", "399006.SZ", "518880.SH")
    constraints = PortfolioConstraints(max_weight=0.7, cash_reserve=0.03)
    anchor = weights_to_vector({"000300.SH": 0.32, "399006.SZ": 0.25, "518880.SH": 0.40}, assets)
    text_state = Stage2TextState(
        flat_features=(),
        event_table=(),
        bl_views=(BLViewRecord("technology_growth:positive", "technology_growth", "positive", 25.0, 0.8, "unit"),),
        confidence_matrix=ConfidenceMatrix(labels=("technology_growth",), values=((0.8,),)),
        decayed_memory=DecayedEventMemory(None, {}, 5.0, 0),
    )

    bl_inputs = build_bl_inputs(
        covariance=_covariance(),
        assets=assets,
        anchor_weights=anchor,
        text_state=text_state,
    )
    posterior = black_litterman_posterior(bl_inputs)
    weights = optimize_long_only_mean_variance(
        expected_returns=posterior.posterior_returns,
        covariance_matrix=covariance_to_matrix(_covariance(), assets),
        assets=assets,
        constraints=constraints,
        anchor_weights=anchor,
        config=OptimizerConfig(max_iter=50),
        confidence=np.array([0.8]),
    )

    assert posterior.view_count == 1
    assert weights["399006.SZ"] > 0
    assert not validate_weight_constraints(weights, constraints)
