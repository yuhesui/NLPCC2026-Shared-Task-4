from tools.backtesting.compare_official_local import compare_metric_dicts


def test_compare_metric_dicts_accepts_values_within_tolerance() -> None:
    official = {"cumulative_return": 0.10, "sharpe_ratio": 1.25}
    local = {"cumulative_return": 0.1004, "sharpe_ratio": 1.251}

    result = compare_metric_dicts(
        official,
        local,
        tolerances={"cumulative_return": 0.001, "sharpe_ratio": 0.01},
    )

    assert result.ok


def test_compare_metric_dicts_flags_missing_or_out_of_tolerance_metric() -> None:
    official = {"cumulative_return": 0.10, "sharpe_ratio": 1.25}
    local = {"cumulative_return": 0.12}

    result = compare_metric_dicts(
        official,
        local,
        tolerances={"cumulative_return": 0.001, "sharpe_ratio": 0.01},
    )

    differences = {item.metric: item for item in result.differences}
    assert not result.ok
    assert not differences["cumulative_return"].within_tolerance
    assert not differences["sharpe_ratio"].within_tolerance
