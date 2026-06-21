"""Vendor the selected Phase12 runtime into NLPCC_tasks for submission use.

This script is a packaging tool only. It copies the static import closure needed
by A2_real/B2_real and the two hash-verified local models. It does not edit or
retune the source implementation outside the submission folder.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path
import shutil


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_ROOT = PACKAGE_ROOT.parent
SOURCE_ROOT = WORKSPACE_ROOT / "src" / "nlpcc"
VENDORED_ROOT = PACKAGE_ROOT / "nlpcc"
MODEL_SOURCE = WORKSPACE_ROOT / "outputs" / "reports" / "next_phase_finetuning_phase12" / "prompt11_submission_ready_code_tex_repair" / "package" / "models"
MODEL_DESTINATION = PACKAGE_ROOT / "package" / "models"
CONFIG_SOURCE = PACKAGE_ROOT / "agent_platform" / "agents" / "phase12_final_candidate_config.json"
CONFIG_DESTINATION = PACKAGE_ROOT / "package" / "configs" / "phase12_final_candidate_config.json"

ROOT_MODULES = {
    "nlpcc.execution.official_adapter",
    "nlpcc.execution.order_planner",
    "nlpcc.news_overlay.production_tensor",
    "nlpcc.stage4_agent.models.risk_parity_agent",
    "nlpcc.stage4_agent.models.s1_quant_core",
}


def module_file(module: str) -> Path | None:
    rel = module.split(".")[1:]
    candidate = SOURCE_ROOT.joinpath(*rel).with_suffix(".py")
    if candidate.exists():
        return candidate
    candidate = SOURCE_ROOT.joinpath(*rel, "__init__.py")
    return candidate if candidate.exists() else None


def resolve_relative(module: str, level: int, imported: str | None) -> str | None:
    package = module.rsplit(".", 1)[0]
    if level:
        parts = package.split(".")
        if level > len(parts):
            return None
        package = ".".join(parts[: len(parts) - level + 1])
    return ".".join(part for part in (package, imported or "") if part)


def imported_modules(module: str, path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    found: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "nlpcc" or alias.name.startswith("nlpcc."):
                    found.add(alias.name)
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                base = resolve_relative(module, node.level, node.module)
            else:
                base = node.module
            if base and (base == "nlpcc" or base.startswith("nlpcc.")):
                found.add(base)
    return found


def ensure_package_inits(destination: Path) -> None:
    current = destination.parent
    while current != PACKAGE_ROOT:
        init = current / "__init__.py"
        if not init.exists():
            init.write_text("", encoding="utf-8")
        current = current.parent


def copy_runtime_closure() -> list[str]:
    pending = list(ROOT_MODULES)
    visited: set[str] = set()
    while pending:
        module = pending.pop()
        if module in visited:
            continue
        source = module_file(module)
        if source is None:
            raise RuntimeError(f"Cannot resolve selected-runtime module: {module}")
        visited.add(module)
        pending.extend(imported_modules(module, source) - visited)
    for module in sorted(visited):
        source = module_file(module)
        assert source is not None
        relative = source.relative_to(SOURCE_ROOT)
        destination = VENDORED_ROOT / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        ensure_package_inits(destination)
    return sorted(visited)


def copy_models() -> None:
    for name in ("bge_contrastive_finetuned_2024_dev_best", "finbert_tone_chinese_e91b1a3"):
        source = MODEL_SOURCE / name
        destination = MODEL_DESTINATION / name
        if not source.is_dir():
            raise RuntimeError(f"Missing verified model source: {source}")
        destination.mkdir(parents=True, exist_ok=True)
        for item in source.iterdir():
            if item.is_file():
                shutil.copy2(item, destination / item.name)


def write_package_config() -> None:
    config = json.loads(CONFIG_SOURCE.read_text(encoding="utf-8"))
    config["bge_model_path"] = "package/models/bge_contrastive_finetuned_2024_dev_best"
    config["submission_package"] = True
    config["submission_path_policy"] = "Paths resolve from the NLPCC_tasks package root; local files only."
    for candidate in config["candidates"].values():
        candidate["bge_path"] = "package/models/bge_contrastive_finetuned_2024_dev_best"
        candidate["finbert_path"] = "package/models/finbert_tone_chinese_e91b1a3"
    CONFIG_DESTINATION.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_DESTINATION.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    CONFIG_SOURCE.write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    copied = copy_runtime_closure()
    copy_models()
    write_package_config()
    manifest = PACKAGE_ROOT / "submission_audit" / "vendored_runtime_modules.txt"
    manifest.write_text("\n".join(copied) + "\n", encoding="utf-8")
    print(f"copied_modules={len(copied)}")


if __name__ == "__main__":
    main()
