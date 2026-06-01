"""Prompt17 candidate universe construction."""

from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import hashlib
import json
from pathlib import Path
import re
from typing import Any, Mapping

from nlpcc.core.fund_universe import TrackName
from nlpcc.runtime.system_runner import load_frozen_system_config
from nlpcc.stage1_news.feature_cache import stage1_config_for_mode


@dataclass(frozen=True)
class CandidateSpec:
    name: str
    system_name: str
    track: TrackName
    family: str
    base_system: str
    fallback_strategy: str
    text_mode: str
    load_news: bool
    config: dict[str, Any]
    config_hash: str
    novelty: float = 0.5
    reproducibility: float = 0.8
    complexity_penalty: float = 0.2
    dependency_risk: float = 0.1

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)

    def with_stage1_cache(self, cache_path: Path | str | None, *, cache_mode: str = "read_write") -> "CandidateSpec":
        if cache_path is None:
            return self
        config = _deep_copy(self.config)
        config["stage1"] = stage1_config_for_mode(self.text_mode, cache_path=cache_path, cache_mode=cache_mode)
        digest = config_hash(config)
        return replace(self, config=config, config_hash=digest, system_name=_system_name(self.name, digest))


def build_prompt17_candidates(
    *,
    repo_root: Path | None = None,
    max_per_track: int | None = None,
    include_text_modes: tuple[str, ...] | None = None,
) -> list[CandidateSpec]:
    root = repo_root or Path(__file__).resolve().parents[3]
    modes = set(include_text_modes or ("no_news", "rule_based", "bge_small_zh", "finbert_tone_chinese", "hybrid_rule_bge_finbert"))
    candidates: list[CandidateSpec] = []
    for item in _candidate_templates():
        if item["text_mode"] not in modes:
            continue
        candidates.append(_build_candidate(root, **item))
    if max_per_track is None:
        return candidates
    limited: list[CandidateSpec] = []
    counts: dict[str, int] = {}
    for candidate in candidates:
        counts.setdefault(candidate.track, 0)
        if counts[candidate.track] >= max_per_track:
            continue
        limited.append(candidate)
        counts[candidate.track] += 1
    return limited


def config_hash(config: Mapping[str, Any]) -> str:
    text = json.dumps(config, ensure_ascii=False, sort_keys=True, default=str)
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _build_candidate(
    repo_root: Path,
    *,
    name: str,
    track: TrackName,
    family: str,
    base_system: str,
    text_mode: str,
    params: Mapping[str, Any] | None = None,
    fallback_strategy: str | None = None,
    novelty: float = 0.5,
    reproducibility: float = 0.8,
    complexity_penalty: float = 0.2,
    dependency_risk: float = 0.1,
) -> CandidateSpec:
    config = load_frozen_system_config(base_system, config_root=repo_root / "configs", track=track)
    config = _deep_merge(config, dict(params or {}))
    config["track"] = track
    config["fallback"] = fallback_strategy or ("s1_sector" if track == "sector" else "s1_macro")
    config["stage1"] = stage1_config_for_mode(text_mode)
    config["prompt17_family"] = family
    config["prompt17_text_mode"] = text_mode
    pre_hash = config_hash({key: value for key, value in config.items() if key != "name"})
    system_name = _system_name(name, pre_hash)
    config["name"] = system_name
    return CandidateSpec(
        name=name,
        system_name=system_name,
        track=track,
        family=family,
        base_system=base_system,
        fallback_strategy=str(config["fallback"]),
        text_mode=text_mode,
        load_news=text_mode != "no_news",
        config=config,
        config_hash=config_hash(config),
        novelty=novelty,
        reproducibility=reproducibility,
        complexity_penalty=complexity_penalty,
        dependency_risk=dependency_risk,
    )


def _candidate_templates() -> list[dict[str, Any]]:
    return [
        _t("s0_macro_cash02", "macro", "s0", "s0_equal_weight", "no_news", {"cash_reserve": 0.02}, 0.1, 0.95, 0.02, 0.0),
        _t("s0_macro_cash03", "macro", "s0", "s0_equal_weight", "no_news", {"cash_reserve": 0.03}, 0.1, 0.95, 0.02, 0.0),
        _t("s1_macro_default", "macro", "s1", "s1_macro", "no_news", {}, 0.25, 0.90, 0.06, 0.0),
        _t("s1_macro_momentum35", "macro", "s1", "s1_macro", "no_news", {"momentum_weight": 0.35, "inverse_vol_weight": 0.50}, 0.28, 0.90, 0.06, 0.0),
        _t("risk_parity_macro", "macro", "risk_parity", "risk_parity_track1", "no_news", {}, 0.32, 0.90, 0.08, 0.0),
        _t("hgf_mpc_macro_default", "macro", "hgf_mpc", "hgf_mpc_track1", "no_news", {}, 0.65, 0.85, 0.22, 0.02),
        _t("hgf_mpc_macro_drift60", "macro", "hgf_mpc", "hgf_mpc_track1", "no_news", {"drift_weight": 0.60, "risk_weight": 0.40}, 0.65, 0.85, 0.22, 0.02),
        _t("robust_bl_macro_rule", "macro", "robust_bl", "robust_bl_track1", "rule_based", {}, 0.70, 0.85, 0.25, 0.08),
        _t("robust_bl_macro_hybrid", "macro", "robust_bl", "robust_bl_track1", "hybrid_rule_bge_finbert", {"s1_blend_weight": 0.35}, 0.78, 0.75, 0.35, 0.25),
        _t("dro_bl_rp_macro_rule", "macro", "dro_bl_rp", "dro_bl_rp_track1", "rule_based", {}, 0.76, 0.86, 0.28, 0.08),
        _t("dro_bl_rp_macro_tau08", "macro", "dro_bl_rp", "dro_bl_rp_track1", "rule_based", {"bl_tau": 0.08}, 0.76, 0.86, 0.28, 0.08),
        _t("dro_bl_rp_macro_bge", "macro", "dro_bl_rp", "dro_bl_rp_track1", "bge_small_zh", {"s1_blend_weight": 0.40}, 0.80, 0.75, 0.35, 0.22),
        _t("dro_bl_rp_macro_hybrid", "macro", "dro_bl_rp", "dro_bl_rp_track1", "hybrid_rule_bge_finbert", {"s1_blend_weight": 0.40}, 0.82, 0.74, 0.38, 0.28),
        _t("bsa_rp_macro_rule", "macro", "bsa_rp", "bsa_rp_track1", "rule_based", {}, 0.72, 0.86, 0.26, 0.08),
        _t("bsa_rp_macro_tilt25", "macro", "bsa_rp", "bsa_rp_track1", "rule_based", {"belief_tilt_strength": 0.25}, 0.72, 0.86, 0.26, 0.08),
        _t("armor_omd_macro_default", "macro", "armor_omd", "armor_omd_macro", "rule_based", {}, 0.72, 0.82, 0.32, 0.08),
        _t("armor_omd_macro_lr25", "macro", "armor_omd", "armor_omd_macro", "rule_based", {"learning_rate": 2.5}, 0.72, 0.82, 0.32, 0.08),
        _t("ceva_macro_rule", "macro", "ceva_kf_ciga", "ceva_kf_ciga_track1", "rule_based", {}, 0.82, 0.83, 0.36, 0.08),
        _t("ceva_macro_overlay10", "macro", "ceva_kf_ciga", "ceva_kf_ciga_track1", "rule_based", {"overlay_strength": 0.10}, 0.82, 0.83, 0.36, 0.08),
        _t("ceva_macro_finbert", "macro", "ceva_kf_ciga", "ceva_kf_ciga_track1", "finbert_tone_chinese", {"overlay_strength": 0.15}, 0.84, 0.74, 0.40, 0.25),
        _t("s0_sector_cash02", "sector", "s0", "s0_equal_weight", "no_news", {"cash_reserve": 0.02, "max_weight": 0.25}, 0.1, 0.95, 0.02, 0.0),
        _t("s0_sector_cash03", "sector", "s0", "s0_equal_weight", "no_news", {"cash_reserve": 0.03, "max_weight": 0.25}, 0.1, 0.95, 0.02, 0.0),
        _t("s1_sector_default", "sector", "s1", "s1_sector", "no_news", {}, 0.25, 0.90, 0.06, 0.0),
        _t("s1_sector_trend60", "sector", "s1", "s1_sector", "no_news", {"sector_trend_weight": 0.60, "inverse_vol_weight": 0.30}, 0.28, 0.90, 0.06, 0.0),
        _t("sector_rotation_rule", "sector", "sector_rotation", "sector_rotation_track2", "rule_based", {}, 0.60, 0.86, 0.26, 0.08),
        _t("sector_rotation_graph15", "sector", "sector_rotation", "sector_rotation_track2", "rule_based", {"graph_weight": 0.15, "news_weight": 0.15}, 0.62, 0.86, 0.26, 0.08),
        _t("sector_rotation_bge", "sector", "sector_rotation", "sector_rotation_track2", "bge_small_zh", {"news_tilt_strength": 1.25}, 0.68, 0.74, 0.34, 0.22),
        _t("leeqa_rank_rule", "sector", "leeqa_rank", "leeqa_rank_track2", "rule_based", {}, 0.70, 0.86, 0.28, 0.08),
        _t("leeqa_rank_top4", "sector", "leeqa_rank", "leeqa_rank_track2", "rule_based", {"top_k": 4}, 0.70, 0.86, 0.28, 0.08),
        _t("leeqa_rank_finbert", "sector", "leeqa_rank", "leeqa_rank_track2", "finbert_tone_chinese", {}, 0.74, 0.74, 0.36, 0.24),
        _t("kg_moe_lite_rule", "sector", "kg_moe_lite", "kg_moe_lite_track2", "rule_based", {}, 0.78, 0.86, 0.34, 0.08),
        _t("kg_moe_lite_news10", "sector", "kg_moe_lite", "kg_moe_lite_track2", "rule_based", {"news_tilt_strength": 1.0}, 0.78, 0.86, 0.34, 0.08),
        _t("kg_moe_lite_bge", "sector", "kg_moe_lite", "kg_moe_lite_track2", "bge_small_zh", {}, 0.82, 0.74, 0.42, 0.24),
        _t("kg_moe_lite_hybrid", "sector", "kg_moe_lite", "kg_moe_lite_track2", "hybrid_rule_bge_finbert", {}, 0.84, 0.72, 0.46, 0.30),
        _t("armor_omd_sector_default", "sector", "armor_omd", "armor_omd_sector", "rule_based", {}, 0.72, 0.82, 0.32, 0.08),
        _t("ceva_sector_rule", "sector", "ceva_kf_ciga", "ceva_kf_ciga_track2", "rule_based", {}, 0.80, 0.84, 0.36, 0.08),
        _t("ceva_sector_finbert", "sector", "ceva_kf_ciga", "ceva_kf_ciga_track2", "finbert_tone_chinese", {"overlay_strength": 0.15}, 0.82, 0.74, 0.40, 0.25),
    ]


def _t(
    name: str,
    track: str,
    family: str,
    base_system: str,
    text_mode: str,
    params: Mapping[str, Any],
    novelty: float,
    reproducibility: float,
    complexity_penalty: float,
    dependency_risk: float,
) -> dict[str, Any]:
    return {
        "name": name,
        "track": track,
        "family": family,
        "base_system": base_system,
        "text_mode": text_mode,
        "params": params,
        "novelty": novelty,
        "reproducibility": reproducibility,
        "complexity_penalty": complexity_penalty,
        "dependency_risk": dependency_risk,
    }


def _deep_merge(left: Mapping[str, Any], right: Mapping[str, Any]) -> dict[str, Any]:
    merged = _deep_copy(left)
    for key, value in right.items():
        if isinstance(value, Mapping) and isinstance(merged.get(key), Mapping):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = _deep_copy(value)
    return merged


def _deep_copy(value: Any) -> Any:
    return json.loads(json.dumps(value, ensure_ascii=False, default=str))


def _system_name(name: str, digest: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9_]+", "_", name.lower()).strip("_")
    return f"p17_{slug}_{digest[:8]}"
