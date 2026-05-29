from pathlib import Path

from tools.experiments.ablations import make_prompt10_ablation_suite
from tools.experiments.experiment_config import ExperimentConfig, ExperimentSuiteConfig
from tools.experiments.result_store import ResultStore
from tools.experiments.runner import build_agent, run_experiment


def test_experiment_config_hash_is_deterministic() -> None:
    config = ExperimentConfig(
        name="hash_check",
        agent_name="s1_quant_core",
        data_root=Path("data/sample/smoke_test"),
        agent_params={"track": "macro"},
    )
    same = ExperimentConfig.from_mapping(config.to_mapping())

    assert config.config_hash() == same.config_hash()
    assert config.run_id.endswith(config.config_hash())


def test_prompt10_suite_contains_required_ablation_names() -> None:
    suite = make_prompt10_ablation_suite(data_root=Path("data/train_2024"), max_dates=5)
    names = {config.name for config in suite.experiments}

    assert "s0_macro" in names
    assert "s1_macro" in names
    assert "robust_bl_no_news" in names
    assert "robust_bl_no_llm" in names
    assert "robust_bl_no_text_store" in names
    assert "robust_bl_no_turnover_control" in names
    assert "robust_bl_no_risk_control" in names
    assert "robust_bl_without_confidence" in names
    assert "sector_without_graph" in names
    assert "sector_without_news" in names
    assert "oco_without_text" in names


def test_suite_config_parses_json_shape() -> None:
    suite = ExperimentSuiteConfig.from_mapping(
        {
            "name": "tiny",
            "defaults": {"data_root": "data/sample/smoke_test", "max_dates": 2},
            "experiments": [
                {"name": "s0", "agent_name": "s0_equal_weight", "agent_params": {"max_weight": 1.0}},
                {"name": "s1", "agent_name": "s1_quant_core", "agent_params": {"track": "macro"}},
            ],
        }
    )

    assert suite.name == "tiny"
    assert len(suite.experiments) == 2
    assert suite.experiments[0].max_dates == 2


def test_build_agent_supports_prompt10_candidates() -> None:
    assert build_agent("s0_equal_weight", {"max_weight": 1.0})
    assert build_agent("s1_quant_core", {"track": "macro"})
    assert build_agent("risk_parity", {"track": "macro"})
    assert build_agent("robust_bl", {"track": "macro"})
    assert build_agent("sector_rotation", {"track": "sector"})
    assert build_agent("oco_ensemble", {"track": "macro"})


def test_run_experiment_stores_config_hash() -> None:
    config = ExperimentConfig(
        name="prompt10_s0_smoke",
        agent_name="s0_equal_weight",
        data_root=Path("data/sample/smoke_test"),
        track="macro",
        lookback_days=2,
        max_dates=2,
        output_dir=Path("outputs/test_tools_prompt10/experiments"),
        agent_params={"max_weight": 1.0},
    )

    result = run_experiment(config)
    store = ResultStore(Path("outputs/test_tools_prompt10/result_store"))
    store.write(config.run_id, result)
    loaded = store.read(config.run_id)

    assert result["experiment"]["config_hash"] == config.config_hash()
    assert loaded["result_hash"]
