from nlpcc4.common.config import REQUIRED_TOP_LEVEL_SECTIONS, load_config


def test_required_configs_load():
    for path in sorted(__import__("pathlib").Path("configs").rglob("*.yaml")):
        config = load_config(path)
        assert all(section in config for section in REQUIRED_TOP_LEVEL_SECTIONS)
