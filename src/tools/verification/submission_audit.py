"""Submission-readiness checks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class SubmissionIssue:
    code: str
    message: str
    path: str | None = None


REQUIRED_PATHS = (
    Path("README.md"),
    Path("AGENTS.md"),
    Path("src/nlpcc"),
    Path("NLPCC_tasks/agent_platform/agents"),
)


def audit_required_paths(repo_root: Path = Path(".")) -> list[SubmissionIssue]:
    issues: list[SubmissionIssue] = []
    for relative in REQUIRED_PATHS:
        path = repo_root / relative
        if not path.exists():
            issues.append(SubmissionIssue("missing_required_path", f"Required path is missing: {relative}", str(relative)))
    return issues


def audit_outputs_exist(repo_root: Path = Path(".")) -> list[SubmissionIssue]:
    outputs = repo_root / "outputs"
    if not outputs.exists():
        return [SubmissionIssue("missing_outputs_dir", "outputs/ directory is missing.", "outputs")]
    return []
