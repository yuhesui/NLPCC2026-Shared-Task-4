from pathlib import Path


def test_key_docs_exist():
    for path_text in [
        "AGENTS.md",
        "docs/design/repo_architecture.md",
        "docs/command_reference.md",
        "docs/research/strategy_decision_summary.md",
        "docs/reports/implementation_logs/README.md",
        "docs/reports/ablations/README.md",
        "docs/reports/phase_a/README.md",
        "docs/reports/final_submission/README.md",
        "docs/references/README.md",
    ]:
        assert Path(path_text).is_file(), path_text
