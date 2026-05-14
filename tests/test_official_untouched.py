import subprocess


def test_official_starter_kit_has_no_worktree_changes():
    result = subprocess.run(
        ["git", "status", "--short", "--", "NLPCC_tasks"],
        check=True,
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip() == ""
