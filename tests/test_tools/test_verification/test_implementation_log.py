from datetime import datetime
from pathlib import Path

from tools.utils.implementation_log import (
    ImplementationLog,
    create_implementation_log,
    sanitize_filename_part,
)


def test_sanitize_filename_part_replaces_unsafe_characters():
    assert sanitize_filename_part("prompt00 / repo reset") == "prompt00_repo_reset"


def test_create_implementation_log_writes_markdown():
    log = ImplementationLog(
        prompt_id="prompt00",
        phase="repo_reset",
        summary="Created skeleton.",
        files="src/tools/utils/implementation_log.py",
        tests="unit test",
        caveats="None",
        next_steps="Run prompt01.",
        artifacts=("docs/implementation_logs/example.md",),
    )

    path = create_implementation_log(
        log,
        output_dir=Path("outputs") / "logs" / "test_implementation_log",
        now=datetime(2026, 5, 28, 12, 0, 0),
    )

    assert path.name == "20260528_120000_prompt00_repo_reset.md"
    assert "Created skeleton." in path.read_text(encoding="utf-8")
