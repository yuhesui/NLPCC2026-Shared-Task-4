"""Implementation log creation utilities.

The helper writes one Markdown file per prompt execution under
``docs/implementation_logs/`` by default. It intentionally has no dependency on
the strategy packages so it can be used during repository bootstrapping.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import re


DEFAULT_OUTPUT_DIR = Path("docs") / "implementation_logs"


@dataclass(frozen=True)
class ImplementationLog:
    """Structured fields recorded for each prompt execution."""

    prompt_id: str
    phase: str
    summary: str
    files: str
    tests: str
    caveats: str
    next_steps: str
    artifacts: tuple[str, ...] = field(default_factory=tuple)


def sanitize_filename_part(value: str) -> str:
    """Return a filesystem-safe filename component."""

    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    cleaned = re.sub(r"_+", "_", cleaned).strip("._-")
    return cleaned or "implementation_log"


def render_implementation_log(log: ImplementationLog, created_at: datetime) -> str:
    """Render an implementation log as Markdown."""

    artifact_lines = "\n".join(f"- `{artifact}`" for artifact in log.artifacts)
    if not artifact_lines:
        artifact_lines = "- None"

    return (
        f"# Implementation Log: {log.prompt_id} - {log.phase}\n\n"
        f"**Created:** {created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        "## Summary\n\n"
        f"{log.summary}\n\n"
        "## Files Changed\n\n"
        f"{log.files}\n\n"
        "## Tests / Checks\n\n"
        f"{log.tests}\n\n"
        "## Caveats\n\n"
        f"{log.caveats}\n\n"
        "## Artifacts\n\n"
        f"{artifact_lines}\n\n"
        "## Next Steps\n\n"
        f"{log.next_steps}\n"
    )


def create_implementation_log(
    log: ImplementationLog,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    now: datetime | None = None,
) -> Path:
    """Create a timestamped implementation log and return its path."""

    if not log.prompt_id.strip():
        raise ValueError("prompt_id cannot be empty")
    if not log.phase.strip():
        raise ValueError("phase cannot be empty")

    created_at = now or datetime.now()
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    timestamp = created_at.strftime("%Y%m%d_%H%M%S")
    prompt_part = sanitize_filename_part(log.prompt_id)
    phase_part = sanitize_filename_part(log.phase)
    path = out_dir / f"{timestamp}_{prompt_part}_{phase_part}.md"
    path.write_text(render_implementation_log(log, created_at), encoding="utf-8")
    return path

