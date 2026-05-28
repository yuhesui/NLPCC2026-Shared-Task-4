from pathlib import Path

from tools.experiments.ablations import make_s1_ablation_configs
from tools.experiments.experiment_config import ExperimentConfig
from tools.experiments.result_store import ResultStore
from tools.experiments.runner import run_experiment


def test_experiment_runner_and_result_store() -> None:
    config = ExperimentConfig(
        name="prompt04_s0_macro",
        agent_name="s0_equal_weight",
        data_root=Path("data/sample/smoke_test"),
        track="macro",
        lookback_days=2,
        output_dir=Path("outputs/test_tools_prompt04/experiments"),
        agent_params={"max_weight": 1.0},
    )

    result = run_experiment(config)
    store = ResultStore(Path("outputs/test_tools_prompt04/result_store"))
    store.write("prompt04_s0_macro", result)

    loaded = store.read("prompt04_s0_macro")
    assert loaded["status"] == "ok"
    assert "prompt04_s0_macro" in store.list_results()


def test_s1_ablation_configs_are_named_and_deterministic() -> None:
    base = ExperimentConfig(
        name="s1_base",
        agent_name="s1_quant_core",
        data_root=Path("data/sample/smoke_test"),
        agent_params={"track": "macro"},
    )

    configs = make_s1_ablation_configs(base)

    assert [config.name for config in configs] == [
        "s1_base_base",
        "s1_base_no_momentum",
        "s1_base_no_sector_trend",
        "s1_base_low_turnover",
    ]
