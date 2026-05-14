from nlpcc4.execution.constraints import project_long_only


def test_constraint_projection_respects_cap_and_cash_buffer():
    weights = project_long_only({"a": 10.0, "b": 1.0, "c": 1.0}, max_weight=0.4, cash_buffer=0.05)
    assert max(weights.values()) <= 0.4 + 1e-12
    assert sum(weights.values()) <= 0.95 + 1e-12
    assert all(value >= 0 for value in weights.values())


def test_constraint_projection_allows_cash_when_cap_binds_every_asset():
    weights = project_long_only({"a": 1.0, "b": 1.0}, max_weight=0.3, cash_buffer=0.0)
    assert weights == {"a": 0.3, "b": 0.3}
    assert sum(weights.values()) < 1.0
