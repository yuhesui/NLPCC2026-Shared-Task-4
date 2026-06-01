"""Materialize generated SystemRunner configs for Prompt17 candidates."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Mapping

from nlpcc.runtime.system_runner import load_frozen_system_config
from tools.experiments.candidate_factory import CandidateSpec


BASE_SYSTEMS = (
    "s0_equal_weight",
    "s1_macro",
    "s1_sector",
    "risk_parity_track1",
    "robust_bl_track1",
    "dro_bl_rp_track1",
    "bsa_rp_track1",
    "armor_omd_macro",
    "armor_omd_sector",
    "hgf_mpc_track1",
    "ceva_kf_ciga_track1",
    "ceva_kf_ciga_track2",
    "sector_rotation_track2",
    "leeqa_rank_track2",
    "kg_moe_lite_track2",
    "oco_fallback",
)


def materialize_prompt17_configs(
    *,
    repo_root: Path,
    output_config_root: Path,
    candidates: list[CandidateSpec],
) -> dict[str, Path]:
    systems_dir = output_config_root / "systems"
    systems_dir.mkdir(parents=True, exist_ok=True)
    written: dict[str, Path] = {}

    for system_name in BASE_SYSTEMS:
        try:
            track = "sector" if system_name.endswith("track2") or system_name in {"s1_sector", "armor_omd_sector"} else "macro"
            config = load_frozen_system_config(system_name, config_root=repo_root / "configs", track=track)  # type: ignore[arg-type]
        except FileNotFoundError:
            continue
        path = systems_dir / f"{system_name}.yaml"
        _write_mapping(path, config)
        written[system_name] = path

    for candidate in candidates:
        path = systems_dir / f"{candidate.system_name}.yaml"
        _write_mapping(path, candidate.config)
        written[candidate.system_name] = path
    return written


def _write_mapping(path: Path, values: Mapping[str, Any]) -> None:
    try:
        import yaml  # type: ignore

        text = yaml.safe_dump(dict(values), sort_keys=False, allow_unicode=True)
    except ModuleNotFoundError:
        text = _simple_yaml(dict(values))
    path.write_text(text, encoding="utf-8")


def _simple_yaml(values: Mapping[str, Any], *, indent: int = 0) -> str:
    lines: list[str] = []
    prefix = " " * indent
    for key, value in values.items():
        if isinstance(value, Mapping):
            lines.append(f"{prefix}{key}:")
            lines.append(_simple_yaml(value, indent=indent + 2).rstrip())
        elif isinstance(value, list | tuple):
            lines.append(f"{prefix}{key}:")
            for item in value:
                if isinstance(item, Mapping):
                    lines.append(f"{prefix}  -")
                    lines.append(_simple_yaml(item, indent=indent + 4).rstrip())
                else:
                    lines.append(f"{prefix}  - {_scalar(item)}")
        else:
            lines.append(f"{prefix}{key}: {_scalar(value)}")
    return "\n".join(lines) + "\n"


def _scalar(value: Any) -> str:
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int | float):
        return str(value)
    text = str(value)
    if text == "" or any(char in text for char in ":#[]{}&,*?|>-!%@\\\"'"):
        return repr(text)
    return text
