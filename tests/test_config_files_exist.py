from pathlib import Path


REQUIRED_CONFIGS = [
    "configs/base.yaml",
    "configs/paths.yaml",
    "configs/logging.yaml",
    "configs/backtest_2024_train.yaml",
    "configs/backtest_2025_phase_a.yaml",
    "configs/track1/s0_baselines.yaml",
    "configs/track1/s1_quant_core.yaml",
    "configs/track1/s2_llm_regime.yaml",
    "configs/track1/s3_llm_alpha_tilt.yaml",
    "configs/track1/s4_event_exposure.yaml",
    "configs/track2/s0_baselines.yaml",
    "configs/track2/s1_quant_core.yaml",
    "configs/track2/s2_llm_regime.yaml",
    "configs/track2/s3_llm_alpha_tilt.yaml",
    "configs/track2/s4_event_exposure.yaml",
]

REQUIRED_SECTIONS = [
    "strategy:",
    "data:",
    "signals:",
    "portfolio:",
    "risk:",
    "execution:",
    "logging:",
]


def test_config_files_exist_and_have_required_sections():
    for path_text in REQUIRED_CONFIGS:
        path = Path(path_text)
        assert path.is_file(), path_text
        text = path.read_text(encoding="utf-8")
        for section in REQUIRED_SECTIONS:
            assert section in text, f"{path_text} missing {section}"
