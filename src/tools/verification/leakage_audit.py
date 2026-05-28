"""Leakage audit helpers for saved local runs."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class AuditIssue:
    code: str
    message: str
    location: str | None = None


def audit_decision_metadata(result: dict[str, Any]) -> list[AuditIssue]:
    issues: list[AuditIssue] = []
    for index, item in enumerate(result.get("decisions", [])):
        decision = item.get("decision", {})
        metadata = decision.get("metadata", {})
        forbidden = metadata.get("forbidden_current_fields_used", [])
        if forbidden:
            issues.append(
                AuditIssue(
                    code="forbidden_current_fields_used",
                    message=f"Decision metadata reports forbidden current-day fields: {forbidden}",
                    location=f"decisions[{index}]",
                )
            )
    return issues


def audit_backtest_file(path: Path) -> list[AuditIssue]:
    return audit_decision_metadata(json.loads(path.read_text(encoding="utf-8")))
