"""Thin wrapper around the *official* ICAIF starter kit.

We do not re-implement authentication, upload, receipt recovery or checkpoint
logic: those stay in the organizer's ``kit/original_client.py``
(``OriginalSession``). This module only

* locates a local checkout of the kit (``ICAIF_KIT_ROOT`` or
  ``third_party/icaif_starter_kit/starter-kit``; fetched by
  ``scripts/setup/fetch_official_kit.sh`` at a pinned commit),
* imports its modules without copying them into this repository (the kit has
  no explicit licence, so we do not vendor it),
* exposes the kit's own validator so every decision passes *both* our
  validator and the organizer's, and
* builds an ``OriginalSession`` for the live runner.

Nothing here reads or logs ``TEAM_TOKEN``/``CODABENCH_TOKEN`` values.
"""

from __future__ import annotations

import importlib
import os
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any

from icaif.core.config import REPO_ROOT

DEFAULT_KIT_ROOT = REPO_ROOT / "third_party" / "icaif_starter_kit" / "starter-kit"
PINNED_KIT_COMMIT = "ad237b074d31dca39c5c975b3e5cb61cf85a8feb"


class OfficialKitUnavailable(RuntimeError):
    pass


def kit_root() -> Path:
    return Path(os.environ.get("ICAIF_KIT_ROOT", str(DEFAULT_KIT_ROOT))).resolve()


def kit_available() -> bool:
    root = kit_root()
    return (root / "kit" / "contracts.py").exists() and (root / "universe.json").exists()


@dataclass(frozen=True)
class OfficialKit:
    root: Path
    contracts: ModuleType
    config: ModuleType
    evaluation: ModuleType

    def validate_decision_file(self, path: Path, *, schedule_path: Path | None = None, submitted_at: str | None = None) -> None:
        """Run the organizer's validator on the exact bytes we would upload."""

        self.contracts.validate_submission(path, schedule_path=schedule_path, submitted_at=submitted_at)

    def validate_decision_payload(self, payload: Mapping[str, Any], *, schedule_path: Path | None = None) -> None:
        self.contracts.validate_payload(dict(payload), "decision.json", schedule_path=schedule_path)

    def symbols(self) -> list[str]:
        return list(self.config.load_symbols())

    def schedule(self) -> dict[str, Any]:
        return self.config.load_schedule()

    def competition(self) -> dict[str, Any]:
        return self.config.load_config()

    def calculate_metrics(self, periods: list[dict[str, str]], points: list[str]) -> dict[str, Any]:
        return self.evaluation.calculate_metrics(periods, points)


def load_official_kit(root: Path | None = None) -> OfficialKit:
    base = (root or kit_root()).resolve()
    if not (base / "kit" / "contracts.py").exists():
        raise OfficialKitUnavailable(
            f"official starter kit not found at {base}; run scripts/setup/fetch_official_kit.sh "
            "or set ICAIF_KIT_ROOT"
        )
    if str(base) not in sys.path:
        sys.path.insert(0, str(base))
    try:
        loaded = sys.modules.get("kit.contracts")
        if loaded is not None and not str(getattr(loaded, "__file__", "")).startswith(str(base)):
            raise OfficialKitUnavailable("a different 'kit' package is already imported")
        contracts = importlib.import_module("kit.contracts")
        config = importlib.import_module("kit.config")
        evaluation = importlib.import_module("kit.evaluation")
    except ImportError as error:  # pragma: no cover - depends on local checkout
        raise OfficialKitUnavailable(f"could not import official kit: {error}") from error
    return OfficialKit(root=base, contracts=contracts, config=config, evaluation=evaluation)


def open_official_session(*, profile_path: Path, checkpoint: Path, credentials: Path, token: str) -> Any:
    """Construct the organizer ``OriginalSession`` (requires ``httpx``; live only)."""

    kit = load_official_kit()
    try:
        client = importlib.import_module("kit.original_client")
    except ImportError as error:
        raise OfficialKitUnavailable("official client needs the 'live' extra (httpx)") from error
    profile = client.load_profile(str(profile_path))
    _ = kit  # ensure kit path is on sys.path before import above
    return client.OriginalSession(
        profile=profile, token=token, checkpoint=str(checkpoint), credentials=str(credentials)
    )
