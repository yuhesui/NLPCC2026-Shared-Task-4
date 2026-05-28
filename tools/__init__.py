"""Repo-root shim so `python -m tools...` works from the workspace root."""

from __future__ import annotations

import sys
from pathlib import Path
from pkgutil import extend_path


REPO_ROOT = Path(__file__).resolve().parent.parent
SRC_ROOT = REPO_ROOT / "src"
SRC_TOOLS = SRC_ROOT / "tools"

if SRC_ROOT.is_dir():
    src_path = str(SRC_ROOT)
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

__path__ = extend_path(__path__, __name__)
if SRC_TOOLS.is_dir():
    src_tools_path = str(SRC_TOOLS)
    if src_tools_path not in __path__:
        __path__.append(src_tools_path)

