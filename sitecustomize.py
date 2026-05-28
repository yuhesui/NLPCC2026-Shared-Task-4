"""Repo-local Python path bootstrap.

This lets commands like `python -m tools.data_tools.dataset_mirror` work from
the repository root without requiring an editable install first.
"""

from __future__ import annotations

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent
SRC_ROOT = REPO_ROOT / "src"

if SRC_ROOT.is_dir():
    src_path = str(SRC_ROOT)
    if src_path not in sys.path:
        sys.path.insert(0, src_path)

