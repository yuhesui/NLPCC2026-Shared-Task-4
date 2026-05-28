"""Static dependency-boundary audit."""

from __future__ import annotations

import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DependencyIssue:
    path: str
    line: int
    import_name: str
    message: str


def audit_nlpcc_does_not_import_tools(src_root: Path = Path("src")) -> list[DependencyIssue]:
    issues: list[DependencyIssue] = []
    nlpcc_root = src_root / "nlpcc"
    for path in sorted(nlpcc_root.rglob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except SyntaxError as exc:
            issues.append(DependencyIssue(str(path), exc.lineno or 0, "syntax", str(exc)))
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == "tools" or alias.name.startswith("tools."):
                        issues.append(DependencyIssue(str(path), node.lineno, alias.name, "Production package imports tools."))
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if module == "tools" or module.startswith("tools."):
                    issues.append(DependencyIssue(str(path), node.lineno, module, "Production package imports tools."))
    return issues
