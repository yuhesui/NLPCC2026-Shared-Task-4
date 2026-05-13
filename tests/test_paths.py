from pathlib import Path

from nlpcc4.common.paths import official_starter_root, repo_root, runtime_root


def test_expected_directories_exist():
    root = repo_root()
    assert root == Path(__file__).resolve().parents[1]
    assert official_starter_root().is_dir()
    assert runtime_root().name == ".var"
    assert (root / "src" / "nlpcc4" / "strategies").is_dir()
