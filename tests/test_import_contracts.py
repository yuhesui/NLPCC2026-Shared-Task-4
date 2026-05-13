from nlpcc4.common.paths import official_starter_root, repo_root, runtime_root
from nlpcc4.strategies.base import validate_target_weights


def test_path_helpers_resolve_expected_roots():
    root = repo_root()
    assert root.name == "NLPCC2026-Shared-Task-4"
    assert official_starter_root() == root / "NLPCC_tasks"
    assert runtime_root() == root / ".var"


def test_target_weight_validation_allows_cash_residual():
    validate_target_weights({"000300.SH": 0.4, "518880.SH": 0.3})
