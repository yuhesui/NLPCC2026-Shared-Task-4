from tools.optimiser.grid_search import run_grid_search
from tools.optimiser.promotion import PromotionGate
from tools.optimiser.random_search import run_random_search
from tools.optimiser.scorer import rank_results, score_metrics
from tools.optimiser.search_space import SearchSpace
from tools.optimiser.walk_forward import make_rolling_splits


def test_search_space_grid_random_and_ranking_are_deterministic() -> None:
    space = SearchSpace.from_mapping({"a": [1, 2], "b": [10, 20]})

    def objective(params):
        value = params["a"] + params["b"]
        return {"metrics": {"sharpe_ratio": value, "cumulative_return": 0.0, "max_drawdown": 0.0, "turnover": 0.0}}

    grid = run_grid_search(space, objective)
    random_results = run_random_search(space, objective, count=2, seed=7)
    ranked = rank_results(grid)

    assert len(grid) == 4
    assert random_results == run_random_search(space, objective, count=2, seed=7)
    assert ranked[0]["params"] == {"a": 2, "b": 20}


def test_scorer_promotion_and_walk_forward() -> None:
    score = score_metrics({"sharpe_ratio": 1.0, "cumulative_return": 0.2, "max_drawdown": 0.1, "turnover": 0.05})
    gate = PromotionGate(min_sharpe_delta=0.1)
    verdict = gate.evaluate(
        {"sharpe_ratio": 1.2, "cumulative_return": 0.2, "max_drawdown": 0.1, "turnover": 0.05},
        {"sharpe_ratio": 1.0, "cumulative_return": 0.1, "max_drawdown": 0.1, "turnover": 0.05},
    )
    splits = make_rolling_splits(["d1", "d2", "d3", "d4", "d5"], train_size=2, test_size=1)

    assert score > 0
    assert verdict["promote"] is True
    assert splits[0].train_start == "d1"
    assert splits[-1].test_end == "d5"
