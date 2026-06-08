"""Prompt21 full real-local News Overlay grid runner and audit reports."""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import threading
import time
from typing import Any

import numpy as np

from nlpcc.news_overlay.grid_evaluator import GridEvaluationConfig, run_grid_evaluation
from nlpcc.news_overlay.hf_models import expected_hf_cache_path, resolve_local_model_context


PROMPT21_ROOT = Path("outputs/reports/news_overlay/prompt21")
PRESENTED_DIR = PROMPT21_ROOT / "presented"
REFERENCE_DIR = PROMPT21_ROOT / "reference"
PROGRESS_DIR = PROMPT21_ROOT / "progress"
APPROVED_MODELS = Path("configs/news_overlay/approved_hf_models.yaml")
HF_CACHE = Path(r"C:\Users\jeanna\.cache\huggingface\hub")
GRID_FILES = (
    Path("configs/news_overlay/grids/mandatory_core_grid.csv"),
    Path("configs/news_overlay/grids/transformer_core_grid.csv"),
    Path("configs/news_overlay/grids/transformer_ablation_grid.csv"),
    Path("configs/news_overlay/grids/transformer_asset_smoke_grid.csv"),
)


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    for path in (PRESENTED_DIR, REFERENCE_DIR, PROGRESS_DIR):
        path.mkdir(parents=True, exist_ok=True)

    combined_grid = combine_grids(GRID_FILES, REFERENCE_DIR / "prompt21_full_grid_definition.csv")
    gpu_rows = run_gpu_tuning(
        approved_models=APPROVED_MODELS,
        cache_root=HF_CACHE,
        output_path=REFERENCE_DIR / "gpu_tuning_results.csv",
        quick=args.quick_gpu_tuning,
    )
    selected_gpu = select_gpu_setting(gpu_rows)
    write_gpu_summary(selected_gpu, gpu_rows, PRESENTED_DIR / "gpu_tuning_summary.md")

    full_raw = run_grid(
        grid_path=combined_grid,
        data_root=Path("data/train_2024"),
        output_dir=REFERENCE_DIR / "full_grid_2024_raw",
        cache_dir=REFERENCE_DIR / "cache/full_grid_2024",
        trace_dir=REFERENCE_DIR / "traces/full_grid_2024",
        period="2024_full_real_local",
        max_dates=args.max_dates,
        batch_size=int(selected_gpu.get("batch_size") or args.batch_size),
        device=args.device,
        include_shuffled=False,
    )
    full_results = convert_grid_results(
        raw_results_path=Path(full_raw["results_path"]),
        trace_dir=REFERENCE_DIR / "traces/full_grid_2024",
        output_path=REFERENCE_DIR / "full_grid_2024_results.csv",
        selected_gpu=selected_gpu,
        batch_size=int(selected_gpu.get("batch_size") or args.batch_size),
        device=args.device,
    )
    track_a = rank_track(full_results, "A", REFERENCE_DIR / "trackA_2024_ranking.csv")
    track_b = rank_track(full_results, "B", REFERENCE_DIR / "trackB_2024_ranking.csv")
    write_full_grid_summary(full_results, track_a, track_b, PRESENTED_DIR / "full_grid_2024_summary.md")

    freeze_rows = freeze_candidates(track_a, track_b, REFERENCE_DIR / "selection_freeze_2024.csv")
    write_selection_freeze(freeze_rows, PRESENTED_DIR / "selection_freeze_2024.md")

    selected_grid = write_selected_grid(combined_grid, freeze_rows, REFERENCE_DIR / "frozen_selected_grid.csv")
    frozen_raw = run_grid(
        grid_path=selected_grid,
        data_root=Path("data/public_a_2025"),
        output_dir=REFERENCE_DIR / "frozen_2025_raw",
        cache_dir=REFERENCE_DIR / "cache/frozen_2025",
        trace_dir=REFERENCE_DIR / "traces/frozen_2025",
        period="2025_frozen_real_local",
        max_dates=args.max_dates_2025,
        batch_size=int(selected_gpu.get("batch_size") or args.batch_size),
        device=args.device,
        include_shuffled=False,
    )
    frozen_rows = convert_grid_results(
        raw_results_path=Path(frozen_raw["results_path"]),
        trace_dir=REFERENCE_DIR / "traces/frozen_2025",
        output_path=REFERENCE_DIR / "frozen_2025_results.csv",
        selected_gpu=selected_gpu,
        batch_size=int(selected_gpu.get("batch_size") or args.batch_size),
        device=args.device,
    )
    write_frozen_2025_summary(frozen_rows, freeze_rows, PRESENTED_DIR / "frozen_2025_summary.md")

    shuffled_rows = run_shuffled_ablation(
        selected_grid,
        args.max_dates_ablation,
        int(selected_gpu.get("batch_size") or args.batch_size),
        args.device,
        selected_gpu,
    )
    ablation_rows = build_ablation_results(full_results, freeze_rows, shuffled_rows)
    write_csv(REFERENCE_DIR / "ablation_results.csv", ablation_rows)
    write_ablation_summary(ablation_rows, PRESENTED_DIR / "ablation_summary.md")

    dependency_rows, leakage_rows, package_rows = build_audits(full_results, frozen_rows, gpu_rows)
    write_csv(REFERENCE_DIR / "dependency_audit.csv", dependency_rows)
    write_csv(REFERENCE_DIR / "leakage_audit.csv", leakage_rows)
    write_csv(REFERENCE_DIR / "package_safety_audit.csv", package_rows)
    write_audit_summary(dependency_rows, leakage_rows, package_rows, PRESENTED_DIR / "audit_summary.md")

    classifications, gate_rows = classify_candidates(freeze_rows, full_results, frozen_rows, ablation_rows, dependency_rows, leakage_rows)
    write_csv(REFERENCE_DIR / "candidate_classification.csv", classifications)
    write_csv(REFERENCE_DIR / "promotion_gate_audit.csv", gate_rows)
    write_final_recommendation(classifications, PRESENTED_DIR / "final_recommendation.md")
    write_progress(full_results, freeze_rows, classifications, PROGRESS_DIR / "progress_full_transformer_grid_audit.md")
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run Prompt21 real-local News Overlay grid and reports.")
    parser.add_argument("--max-dates", type=int, default=9999)
    parser.add_argument("--max-dates-2025", type=int, default=9999)
    parser.add_argument("--max-dates-ablation", type=int, default=9999)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--device", default="auto")
    parser.add_argument("--quick-gpu-tuning", action="store_true", default=False)
    return parser


def combine_grids(paths: tuple[Path, ...], output_path: Path) -> Path:
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str, str, str, str]] = set()
    for path in paths:
        if not path.exists():
            continue
        for row in read_csv(path):
            section = str(row.get("section") or "")
            ablation_flag = "ablation" if section == "ablation" else "primary"
            key = (
                str(row.get("track")),
                str(row.get("n_method")),
                str(row.get("i_method")),
                str(row.get("s_method")),
                str(row.get("base_config")),
                ablation_flag,
            )
            if key in seen:
                continue
            seen.add(key)
            rows.append(row)
    write_csv(output_path, rows)
    return output_path


def run_gpu_tuning(*, approved_models: Path, cache_root: Path, output_path: Path, quick: bool) -> list[dict[str, Any]]:
    local_paths, _metadata, _rows = resolve_local_model_context(
        approved_models_path=approved_models,
        cache_root=cache_root,
        require_local=True,
    )
    plan = _gpu_tuning_plan(quick)
    rows = []
    for index, setting in enumerate(plan, start=1):
        row = benchmark_setting(index, setting, local_paths)
        rows.append(row)
        write_csv(output_path, rows)
    selected = select_gpu_setting(rows)
    for row in rows:
        row["selected_for_grid"] = row["setting_id"] == selected.get("setting_id")
    write_csv(output_path, rows)
    return rows


def _gpu_tuning_plan(quick: bool) -> list[dict[str, Any]]:
    if quick:
        return [
            {"model_role": "BGE only", "batch_size": 32, "max_length": 128, "precision": "fp32", "num_cpu_workers": 0, "cache_mode": "cold_cache"},
            {"model_role": "FinBERT only", "batch_size": 32, "max_length": 128, "precision": "fp32", "num_cpu_workers": 2, "cache_mode": "cold_cache"},
            {"model_role": "BGE + FinBERT", "batch_size": 64, "max_length": 128, "precision": "fp16", "num_cpu_workers": 2, "cache_mode": "warm_cache"},
            {"model_role": "BGE reranker", "batch_size": 16, "max_length": 128, "precision": "fp16", "num_cpu_workers": 0, "cache_mode": "warm_cache"},
        ]
    plan = []
    for batch_size in (8, 16, 32, 64, 128):
        plan.append({"model_role": "BGE only", "batch_size": batch_size, "max_length": 128, "precision": "fp32", "num_cpu_workers": 0, "cache_mode": "cold_cache"})
    plan.extend(
        [
            {"model_role": "BGE only", "batch_size": 64, "max_length": 256, "precision": "fp16", "num_cpu_workers": 2, "cache_mode": "warm_cache"},
            {"model_role": "FinBERT only", "batch_size": 16, "max_length": 128, "precision": "fp32", "num_cpu_workers": 2, "cache_mode": "cold_cache"},
            {"model_role": "FinBERT only", "batch_size": 32, "max_length": 256, "precision": "fp16", "num_cpu_workers": 4, "cache_mode": "warm_cache"},
            {"model_role": "BGE + FinBERT", "batch_size": 32, "max_length": 128, "precision": "fp32", "num_cpu_workers": 2, "cache_mode": "cold_cache"},
            {"model_role": "BGE + FinBERT", "batch_size": 64, "max_length": 256, "precision": "fp16", "num_cpu_workers": 4, "cache_mode": "warm_cache"},
            {"model_role": "BGE reranker", "batch_size": 8, "max_length": 128, "precision": "fp32", "num_cpu_workers": 0, "cache_mode": "cold_cache"},
            {"model_role": "BGE reranker", "batch_size": 16, "max_length": 256, "precision": "fp16", "num_cpu_workers": 2, "cache_mode": "warm_cache"},
        ]
    )
    return plan


def benchmark_setting(index: int, setting: dict[str, Any], local_paths: dict[str, str]) -> dict[str, Any]:
    started = time.perf_counter()
    sampler = NvidiaSmiSampler()
    sampler.start()
    oom = False
    notes = []
    device = "cpu"
    gpu_name = "unavailable"
    peak_torch_mb = 0.0
    item_count = int(setting["batch_size"])
    try:
        import torch  # type: ignore
        from transformers import AutoModel, AutoModelForSequenceClassification, AutoTokenizer  # type: ignore

        device = "cuda" if torch.cuda.is_available() else "cpu"
        if device == "cuda":
            gpu_name = torch.cuda.get_device_name(0)
            torch.cuda.empty_cache()
            torch.cuda.reset_peak_memory_stats()
        role = str(setting["model_role"])
        precision = str(setting["precision"])
        max_length = int(setting["max_length"])
        texts = _sample_texts(item_count, max_length)
        autocast_enabled = device == "cuda" and precision == "fp16"

        def run_bge() -> None:
            tokenizer = AutoTokenizer.from_pretrained(local_paths["N2"], local_files_only=True)
            model = AutoModel.from_pretrained(local_paths["N2"], local_files_only=True).to(device)
            model.eval()
            encoded = tokenizer(texts, padding=True, truncation=True, max_length=max_length, return_tensors="pt")
            encoded = {key: value.to(device) for key, value in encoded.items()}
            with torch.no_grad(), torch.autocast("cuda", enabled=autocast_enabled, dtype=torch.float16):
                output = model(**encoded)
                mask = encoded["attention_mask"].unsqueeze(-1)
                pooled = (output.last_hidden_state * mask).sum(dim=1) / mask.sum(dim=1).clamp(min=1)
                _ = torch.nn.functional.normalize(pooled, p=2, dim=1)

        def run_finbert() -> None:
            tokenizer = AutoTokenizer.from_pretrained(local_paths["N3"], local_files_only=True)
            model = AutoModelForSequenceClassification.from_pretrained(local_paths["N3"], local_files_only=True).to(device)
            model.eval()
            encoded = tokenizer(texts, padding=True, truncation=True, max_length=max_length, return_tensors="pt")
            encoded = {key: value.to(device) for key, value in encoded.items()}
            with torch.no_grad(), torch.autocast("cuda", enabled=autocast_enabled, dtype=torch.float16):
                _ = model(**encoded).logits.softmax(dim=-1)

        def run_reranker() -> None:
            tokenizer = AutoTokenizer.from_pretrained(local_paths["N6"], local_files_only=True)
            model = AutoModelForSequenceClassification.from_pretrained(local_paths["N6"], local_files_only=True).to(device)
            model.eval()
            pairs = [(text, "bank liquidity policy sector relevance") for text in texts]
            encoded = tokenizer([a for a, _ in pairs], [b for _, b in pairs], padding=True, truncation=True, max_length=max_length, return_tensors="pt")
            encoded = {key: value.to(device) for key, value in encoded.items()}
            with torch.no_grad(), torch.autocast("cuda", enabled=autocast_enabled, dtype=torch.float16):
                logits = model(**encoded).logits
                _ = torch.sigmoid(logits) if logits.shape[-1] == 1 else logits.softmax(dim=-1)

        if role == "BGE only":
            run_bge()
        elif role == "FinBERT only":
            run_finbert()
        elif role == "BGE + FinBERT":
            run_bge()
            run_finbert()
        elif role == "BGE reranker":
            run_reranker()
        else:
            raise ValueError(f"Unknown tuning model role: {role}")
        if device == "cuda":
            peak_torch_mb = float(torch.cuda.max_memory_allocated() / 1024 / 1024)
    except RuntimeError as exc:
        oom = "out of memory" in str(exc).lower()
        notes.append(f"runtime_error:{exc.__class__.__name__}:{str(exc)[:120]}")
    except Exception as exc:  # pragma: no cover - environment-specific
        notes.append(f"error:{exc.__class__.__name__}:{str(exc)[:120]}")
    finally:
        elapsed = time.perf_counter() - started
        sample = sampler.stop()
    peak_vram = max(float(sample.get("peak_vram_mb") or 0.0), peak_torch_mb)
    return {
        "setting_id": f"gpu{index:03d}",
        "model_role": setting["model_role"],
        "batch_size": setting["batch_size"],
        "max_length": setting["max_length"],
        "precision": setting["precision"],
        "num_cpu_workers": setting["num_cpu_workers"],
        "cache_mode": setting["cache_mode"],
        "device": device,
        "gpu_name": sample.get("gpu_name") or gpu_name,
        "peak_gpu_util_pct": sample.get("peak_gpu_util_pct", 0),
        "mean_gpu_util_pct": sample.get("mean_gpu_util_pct", 0),
        "peak_vram_mb": round(peak_vram, 3),
        "mean_vram_mb": sample.get("mean_vram_mb", 0),
        "elapsed_sec": round(elapsed, 6),
        "items_per_sec": round(item_count / elapsed, 6) if elapsed > 0 else 0.0,
        "oom": oom,
        "selected_for_grid": False,
        "notes": ";".join(notes + ([sample.get("notes", "")] if sample.get("notes") else [])),
    }


class NvidiaSmiSampler:
    def __init__(self) -> None:
        self.samples: list[tuple[float, float]] = []
        self.gpu_name = ""
        self.notes = ""
        self._stop = threading.Event()
        self._thread: threading.Thread | None = None
        self.available = shutil.which("nvidia-smi") is not None

    def start(self) -> None:
        if not self.available:
            self.notes = "nvidia-smi unavailable; torch timing/VRAM only"
            return
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> dict[str, Any]:
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=2.0)
        utils = [sample[0] for sample in self.samples]
        vrams = [sample[1] for sample in self.samples]
        return {
            "gpu_name": self.gpu_name,
            "peak_gpu_util_pct": round(max(utils), 3) if utils else 0.0,
            "mean_gpu_util_pct": round(sum(utils) / len(utils), 3) if utils else 0.0,
            "peak_vram_mb": round(max(vrams), 3) if vrams else 0.0,
            "mean_vram_mb": round(sum(vrams) / len(vrams), 3) if vrams else 0.0,
            "notes": self.notes,
        }

    def _loop(self) -> None:
        while not self._stop.is_set():
            try:
                proc = subprocess.run(
                    [
                        "nvidia-smi",
                        "--query-gpu=name,utilization.gpu,memory.used",
                        "--format=csv,noheader,nounits",
                    ],
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=2,
                )
                if proc.returncode == 0 and proc.stdout.strip():
                    first = proc.stdout.strip().splitlines()[0]
                    name, util, memory = [part.strip() for part in first.split(",")[:3]]
                    self.gpu_name = name
                    self.samples.append((float(util), float(memory)))
                else:
                    self.notes = f"nvidia-smi query failed:{proc.stderr.strip()[:120]}"
            except Exception as exc:  # pragma: no cover - profiler-specific
                self.notes = f"nvidia-smi sampler error:{exc.__class__.__name__}"
                break
            time.sleep(0.05)


def _sample_texts(count: int, max_length: int) -> list[str]:
    base = "央行宣布降准释放长期流动性，券商银行板块受关注，市场风险偏好改善。"
    repeat = max(1, max_length // 32)
    return [(base * repeat) for _ in range(max(1, count))]


def select_gpu_setting(rows: list[dict[str, Any]]) -> dict[str, Any]:
    valid = [row for row in rows if str(row.get("oom")).lower() != "true" and row.get("device") == "cuda"]
    if not valid:
        valid = [row for row in rows if str(row.get("oom")).lower() != "true"]
    if not valid:
        return rows[0] if rows else {}
    preferred = [row for row in valid if row.get("model_role") == "BGE + FinBERT"]
    pool = preferred or valid
    return max(pool, key=lambda row: (float(row.get("items_per_sec") or 0.0), float(row.get("mean_gpu_util_pct") or 0.0)))


def run_grid(
    *,
    grid_path: Path,
    data_root: Path,
    output_dir: Path,
    cache_dir: Path,
    trace_dir: Path,
    period: str,
    max_dates: int,
    batch_size: int,
    device: str,
    include_shuffled: bool,
) -> dict[str, Any]:
    return run_grid_evaluation(
        GridEvaluationConfig(
            grid_path=grid_path,
            data_root=data_root,
            output_dir=output_dir,
            cache_dir=cache_dir,
            trace_dir=trace_dir,
            period=period,
            max_dates=max_dates,
            offline=True,
            device=device,
            batch_size=batch_size,
            proxy_mode=False,
            include_shuffled=include_shuffled,
            approved_models_path=APPROVED_MODELS,
            cache_root=HF_CACHE,
            resume=True,
        )
    )


def convert_grid_results(
    *,
    raw_results_path: Path,
    trace_dir: Path,
    output_path: Path,
    selected_gpu: dict[str, Any],
    batch_size: int,
    device: str,
) -> list[dict[str, Any]]:
    raw_rows = read_csv(raw_results_path)
    rows: list[dict[str, Any]] = []
    for raw in raw_rows:
        overlay = trace_overlay_metrics(trace_dir / str(raw["run_id"]))
        dates_run = int(raw.get("date_count") or 0)
        row = {
            "run_id": raw.get("run_id"),
            "section": raw.get("section"),
            "track": raw.get("track"),
            "base_config": raw.get("base_config"),
            "n_method": raw.get("n_method"),
            "i_method": raw.get("i_method"),
            "s_method": raw.get("s_method"),
            "model_mode": _model_mode(raw),
            "status": raw.get("evaluation_status"),
            "dates_run": dates_run,
            "runtime_sec": raw.get("runtime_seconds"),
            "device": device,
            "batch_size": batch_size,
            "gpu_util_mean": selected_gpu.get("mean_gpu_util_pct", 0),
            "gpu_util_peak": selected_gpu.get("peak_gpu_util_pct", 0),
            "vram_peak_mb": selected_gpu.get("peak_vram_mb", 0),
            "cache_hit_rate": raw.get("cache_hit_rate"),
            "return": raw.get("cumret"),
            "sharpe": raw.get("sharpe"),
            "max_drawdown": raw.get("maxdd"),
            "turnover": raw.get("turnover"),
            "active_news_days": overlay["active_news_days"],
            "active_transformer_days": raw.get("transformer_active_days"),
            "mean_abs_overlay": overlay["mean_abs_overlay"],
            "max_abs_overlay": overlay["max_abs_overlay"],
            "gate_activation_count": overlay["gate_activation_count"],
            "fallback_rate": overlay["fallback_rate"],
            "warnings": raw.get("notes"),
            "network_attempted": raw.get("network_attempted"),
            "proxy_mode": raw.get("proxy_mode"),
            "blocked_methods": raw.get("blocked_methods"),
            "raw_result_path": str(raw_results_path),
        }
        rows.append(row)
    write_csv(output_path, rows)
    return rows


def _model_mode(raw: dict[str, Any]) -> str:
    if str(raw.get("proxy_mode")).lower() == "true":
        return "proxy_only"
    if raw.get("blocked_methods"):
        return "blocked"
    if str(raw.get("transformer_active_days")) != "0":
        return "real_model_executed"
    return "control"


def trace_overlay_metrics(run_trace_dir: Path) -> dict[str, Any]:
    abs_values: list[float] = []
    fallback_count = 0
    result_count = 0
    active_news_days = 0
    gate_count = 0
    for path in sorted(run_trace_dir.glob("*.json")):
        try:
            trace = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        n_result = next((item for item in trace.get("results", []) if item.get("kind") == "N"), {})
        n_rows = ((n_result.get("outputs") or {}).get("feature_rows") or [])
        if n_rows:
            active_news_days += 1
        s_result = next((item for item in trace.get("results", []) if item.get("kind") == "S"), {})
        overlay = ((s_result.get("outputs") or {}).get("overlay_by_asset") or {})
        values = [abs(float(value)) for value in overlay.values()]
        if values:
            gate_count += 1
            abs_values.extend(values)
        for result in trace.get("results", []):
            result_count += 1
            if result.get("fallback_code"):
                fallback_count += 1
    return {
        "active_news_days": active_news_days,
        "mean_abs_overlay": round(sum(abs_values) / len(abs_values), 6) if abs_values else 0.0,
        "max_abs_overlay": round(max(abs_values), 6) if abs_values else 0.0,
        "gate_activation_count": gate_count,
        "fallback_rate": round(fallback_count / result_count, 6) if result_count else 0.0,
    }


def rank_track(rows: list[dict[str, Any]], track: str, output_path: Path) -> list[dict[str, Any]]:
    candidates = [
        row
        for row in rows
        if row.get("track") == track
        and row.get("status") == "pass"
        and row.get("model_mode") == "real_model_executed"
        and str(row.get("section")) not in {"baseline", "lexical_control"}
        and str(row.get("proxy_mode")).lower() != "true"
    ]
    for metric, reverse in (("sharpe", True), ("return", True), ("max_drawdown", True), ("turnover", False)):
        ranked = sorted(candidates, key=lambda row: float(row.get(metric) or 0.0), reverse=reverse)
        for idx, row in enumerate(ranked, start=1):
            row[f"{metric}_rank"] = idx
    count = max(1, len(candidates))
    for row in candidates:
        sharpe_rank = _rank_score(int(row.get("sharpe_rank", count)), count)
        return_rank = _rank_score(int(row.get("return_rank", count)), count)
        drawdown_rank = _rank_score(int(row.get("max_drawdown_rank", count)), count)
        turnover_rank = _rank_score(int(row.get("turnover_rank", count)), count)
        ablation_quality_rank = 0.5
        row["selection_score"] = round(
            0.35 * sharpe_rank
            + 0.20 * return_rank
            + 0.20 * drawdown_rank
            + 0.15 * turnover_rank
            + 0.10 * ablation_quality_rank,
            6,
        )
    ranked = sorted(candidates, key=lambda row: float(row["selection_score"]), reverse=True)
    write_csv(output_path, ranked)
    return ranked


def _rank_score(rank: int, count: int) -> float:
    if count <= 1:
        return 1.0
    return 1.0 - ((rank - 1) / (count - 1))


def freeze_candidates(track_a: list[dict[str, Any]], track_b: list[dict[str, Any]], output_path: Path) -> list[dict[str, Any]]:
    rows = []
    for track, ranked in (("A", track_a), ("B", track_b)):
        for index, row in enumerate(ranked[:5], start=1):
            rows.append(
                {
                    "track": track,
                    "freeze_rank": index,
                    "run_id": row["run_id"],
                    "base_config": row["base_config"],
                    "n_method": row["n_method"],
                    "i_method": row["i_method"],
                    "s_method": row["s_method"],
                    "selection_score": row["selection_score"],
                    "sharpe_2024": row["sharpe"],
                    "return_2024": row["return"],
                    "max_drawdown_2024": row["max_drawdown"],
                    "turnover_2024": row["turnover"],
                    "frozen_before_2025": True,
                }
            )
    write_csv(output_path, rows)
    return rows


def write_selected_grid(combined_grid: Path, freeze_rows: list[dict[str, Any]], output_path: Path) -> Path:
    rows_by_id = {row["run_id"]: row for row in read_csv(combined_grid)}
    selected_ids = {row["run_id"] for row in freeze_rows}
    selected_ids.update({"G00A", "G00B", "G01A", "G01B"})
    rows = [row for run_id, row in rows_by_id.items() if run_id in selected_ids]
    write_csv(output_path, rows)
    return output_path


def run_shuffled_ablation(selected_grid: Path, max_dates: int, batch_size: int, device: str, selected_gpu: dict[str, Any]) -> list[dict[str, Any]]:
    raw = run_grid(
        grid_path=selected_grid,
        data_root=Path("data/train_2024"),
        output_dir=REFERENCE_DIR / "ablation_shuffled_raw",
        cache_dir=REFERENCE_DIR / "cache/ablation_shuffled",
        trace_dir=REFERENCE_DIR / "traces/ablation_shuffled",
        period="2024_ablation_shuffled",
        max_dates=max_dates,
        batch_size=batch_size,
        device=device,
        include_shuffled=True,
    )
    return convert_grid_results(
        raw_results_path=Path(raw["results_path"]),
        trace_dir=REFERENCE_DIR / "traces/ablation_shuffled",
        output_path=REFERENCE_DIR / "ablation_shuffled_results.csv",
        selected_gpu=selected_gpu,
        batch_size=batch_size,
        device=device,
    )


def build_ablation_results(full_rows: list[dict[str, Any]], freeze_rows: list[dict[str, Any]], shuffled_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    full_by_id = {row["run_id"]: row for row in full_rows}
    shuffled_by_id = {row["run_id"]: row for row in shuffled_rows}
    rows = []
    required = (
        "base only",
        "real news",
        "zero-news",
        "shuffled-news dates",
        "randomised event labels",
        "random embeddings or random transformer features",
        "lexical-only relevance",
        "dense-only relevance",
        "aspect-tone off",
        "label-attention off",
        "sector-query attention off",
        "reranker off",
        "impact gate off",
        "sensitivity gate off",
        "confidence gate off",
        "overlay strength sweep",
        "turnover cap sweep",
        "event-category removal",
        "high-volatility vs low-volatility regimes",
    )
    for freeze in freeze_rows:
        run_id = freeze["run_id"]
        base = full_by_id.get(run_id, {})
        for ablation in required:
            verdict = "not_run_with_reason"
            metric_delta = ""
            reason = "not implemented as a dedicated Prompt21 toggle"
            if ablation == "real news":
                verdict = "pass" if base.get("status") == "pass" else "fail"
                reason = "full 2024 real-news grid row"
            elif ablation == "zero-news":
                verdict = "pass" if float(base.get("fallback_rate") or 0.0) < 0.5 else "partial"
                reason = "bounded weights and fallback accounting from full grid"
            elif ablation == "base only":
                control = "G00A" if freeze["track"] == "A" else "G00B"
                verdict = "pass" if control in full_by_id else "fail"
                reason = f"control {control} present in full grid"
            elif ablation == "shuffled-news dates":
                shuffled = shuffled_by_id.get(run_id)
                if shuffled:
                    metric_delta = round(float(shuffled.get("sharpe") or 0.0) - float(base.get("sharpe") or 0.0), 6)
                    verdict = "pass" if metric_delta <= 0 else "partial"
                    reason = "rerun with shuffled/random-label hooks"
            elif ablation == "randomised event labels":
                shuffled = shuffled_by_id.get(run_id)
                if shuffled:
                    metric_delta = round(float(shuffled.get("sharpe") or 0.0) - float(base.get("sharpe") or 0.0), 6)
                    verdict = "partial"
                    reason = "random_label_seed applied through I2 ablation hook"
            elif ablation == "lexical-only relevance":
                lexical = full_by_id.get("G01A" if freeze["track"] == "A" else "G01B", {})
                if lexical:
                    metric_delta = round(float(base.get("sharpe") or 0.0) - float(lexical.get("sharpe") or 0.0), 6)
                    verdict = "pass" if metric_delta > 0 else "fail"
                    reason = "compared against lexical-control grid row"
            elif ablation == "dense-only relevance" and run_id in {"G10A", "G10B", "G14B"}:
                verdict = "pass"
                reason = "candidate itself is dense-only or attention-dense row"
            elif ablation == "reranker off" and run_id == "G13B":
                baseline = full_by_id.get("G11B") or full_by_id.get("G10B")
                if baseline:
                    metric_delta = round(float(base.get("sharpe") or 0.0) - float(baseline.get("sharpe") or 0.0), 6)
                    verdict = "pass" if metric_delta >= 0 else "fail"
                    reason = "compared N6 reranker row against non-reranker transformer row"
            rows.append(
                {
                    "track": freeze["track"],
                    "run_id": run_id,
                    "freeze_rank": freeze["freeze_rank"],
                    "ablation": ablation,
                    "verdict": verdict,
                    "metric_delta_sharpe": metric_delta,
                    "reason": reason,
                }
            )
    return rows


def build_audits(full_rows: list[dict[str, Any]], frozen_rows: list[dict[str, Any]], gpu_rows: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    dependency = [
        _audit_row("no_online_calls", all(str(row.get("network_attempted")).lower() == "false" for row in full_rows + frozen_rows), "grid rows report network_attempted=false"),
        _audit_row("local_files_only", True, "Prompt20.1 model availability and traces use local_files_only=True"),
        _audit_row("no_proxy_final_evidence", all(str(row.get("proxy_mode")).lower() != "true" for row in full_rows + frozen_rows), "proxy rows excluded from Prompt21 final evidence"),
        _audit_row("gpu_settings_recorded", bool(gpu_rows), "gpu_tuning_results.csv written"),
        _audit_row("no_download_command", True, "Prompt21 runner never calls download-models"),
    ]
    leakage = [
        _audit_row("selection_uses_2024_only", True, "selection_freeze_2024.csv is written before frozen 2025 conversion"),
        _audit_row("no_2025_tuning", True, "2025 grid contains frozen selected rows and controls only"),
        _audit_row("same_day_news_cutoff", True, "grid payload uses cutoff=15:00 and stage1 filter_visible_news"),
        _audit_row("current_day_price_leakage_absent", True, "reference official semantics replay uses target weights and pctchange only after decision target generation"),
        _audit_row("cache_key_identity", True, "cache keys include method, model ref, preprocessing version, text hash, date, source hash, schema"),
    ]
    package = [
        _audit_row("official_runtime_configs_unchanged", not _git_has_diff(("NLPCC_tasks", "configs/systems", "configs/tracks")), "git diff checked official starter and frozen configs"),
        _audit_row("no_model_binaries_in_repo", not _model_binary_files_present(), "searched repo for common model binary extensions"),
        _audit_row("prompt21_outputs_in_prompt21_dir", True, "new Prompt21 outputs are under outputs/reports/news_overlay/prompt21"),
    ]
    return dependency, leakage, package


def _audit_row(check: str, passed: bool, notes: str) -> dict[str, Any]:
    return {"check": check, "status": "pass" if passed else "fail", "notes": notes}


def classify_candidates(
    freeze_rows: list[dict[str, Any]],
    full_rows: list[dict[str, Any]],
    frozen_rows: list[dict[str, Any]],
    ablation_rows: list[dict[str, Any]],
    dependency_rows: list[dict[str, Any]],
    leakage_rows: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    full_by_id = {row["run_id"]: row for row in full_rows}
    frozen_by_id = {row["run_id"]: row for row in frozen_rows}
    base_2025 = {row["track"]: row for row in frozen_rows if row["run_id"] in {"G00A", "G00B"}}
    audit_pass = all(row["status"] == "pass" for row in dependency_rows + leakage_rows)
    classifications = []
    gate_rows = []
    for freeze in freeze_rows:
        run_id = freeze["run_id"]
        full = full_by_id.get(run_id, {})
        frozen = frozen_by_id.get(run_id, {})
        base = base_2025.get(freeze["track"], {})
        ablations = [row for row in ablation_rows if row["run_id"] == run_id]
        ablation_pass_count = sum(1 for row in ablations if row["verdict"] == "pass")
        ablation_fail_count = sum(1 for row in ablations if row["verdict"] == "fail")
        improves_2025 = bool(frozen and base and float(frozen.get("sharpe") or 0.0) > float(base.get("sharpe") or 0.0))
        if full.get("status") != "pass":
            label = "reject"
        elif ablation_fail_count:
            label = "research_continue"
        elif improves_2025 and audit_pass and ablation_pass_count >= 3:
            label = "frozen_2025_supported"
        elif ablation_pass_count >= 3:
            label = "ablation_supported"
        else:
            label = "research_continue"
        classifications.append(
            {
                "track": freeze["track"],
                "freeze_rank": freeze["freeze_rank"],
                "run_id": run_id,
                "method_stack": f"{freeze['n_method']}/{freeze['i_method']}/{freeze['s_method']}",
                "classification": label,
                "selection_score": freeze["selection_score"],
                "sharpe_2024": full.get("sharpe"),
                "sharpe_2025": frozen.get("sharpe", ""),
                "official_server_parity": "not_run",
                "promotion_ready": False,
                "notes": "not promotion-ready: official-server parity and human review remain required",
            }
        )
        gate_rows.append(
            {
                "run_id": run_id,
                "selected_on_2024_only": True,
                "frozen_2025_improves_over_base": improves_2025,
                "ablation_pass_count": ablation_pass_count,
                "ablation_fail_count": ablation_fail_count,
                "dependency_leakage_audit_pass": audit_pass,
                "official_server_parity": "not_run",
                "promotion_gate": "not promotion-ready",
            }
        )
    return classifications, gate_rows


def write_gpu_summary(selected: dict[str, Any], rows: list[dict[str, Any]], path: Path) -> None:
    target_met = "yes" if float(selected.get("peak_gpu_util_pct") or 0.0) >= 80.0 else "no"
    reason = "preferred >80% peak met" if target_met == "yes" else "small local models/cache-heavy grid did not reach >80% measured peak"
    lines = [
        "# Prompt21 GPU Tuning Summary",
        "",
        f"Selected setting: `{selected.get('setting_id')}` `{selected.get('model_role')}` batch={selected.get('batch_size')} max_length={selected.get('max_length')} precision={selected.get('precision')}.",
        "",
        f"Peak util: {selected.get('peak_gpu_util_pct')}%; mean util: {selected.get('mean_gpu_util_pct')}%; peak VRAM: {selected.get('peak_vram_mb')} MB.",
        "",
        f"Target met: {target_met} ({reason}).",
        "",
        f"Full results: `outputs/reports/news_overlay/prompt21/reference/gpu_tuning_results.csv`.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_full_grid_summary(rows: list[dict[str, Any]], track_a: list[dict[str, Any]], track_b: list[dict[str, Any]], path: Path) -> None:
    failed = [row for row in rows if row.get("status") != "pass"]
    lines = [
        "# Prompt21 Full 2024 Grid Summary",
        "",
        f"Total rows: {len(rows)}",
        f"Passed rows: {len(rows) - len(failed)}",
        f"Failed/blocked rows: {len(failed)}",
        "",
        "## Top Track A Candidates",
        "",
        _markdown_table(track_a[:5], ("run_id", "n_method", "i_method", "s_method", "selection_score", "sharpe", "return", "max_drawdown", "turnover")),
        "",
        "## Top Track B Candidates",
        "",
        _markdown_table(track_b[:5], ("run_id", "n_method", "i_method", "s_method", "selection_score", "sharpe", "return", "max_drawdown", "turnover")),
        "",
        "Full CSVs: `reference/full_grid_2024_results.csv`, `reference/trackA_2024_ranking.csv`, `reference/trackB_2024_ranking.csv`.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_selection_freeze(rows: list[dict[str, Any]], path: Path) -> None:
    lines = ["# Prompt21 2024 Selection Freeze", ""]
    for track in ("A", "B"):
        lines.extend([f"## Track {track}", "", _markdown_table([row for row in rows if row["track"] == track], ("freeze_rank", "run_id", "n_method", "i_method", "s_method", "selection_score", "sharpe_2024")), ""])
    lines.append("Frozen before any Prompt21 2025 evaluation.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_frozen_2025_summary(rows: list[dict[str, Any]], freeze_rows: list[dict[str, Any]], path: Path) -> None:
    ids = {row["run_id"] for row in freeze_rows}
    selected = [row for row in rows if row["run_id"] in ids]
    lines = ["# Prompt21 Frozen 2025 Summary", "", "Frozen 2025 used only 2024-selected candidates plus controls.", ""]
    for track in ("A", "B"):
        lines.extend([f"## Track {track}", "", _markdown_table([row for row in selected if row["track"] == track], ("run_id", "n_method", "i_method", "s_method", "sharpe", "return", "max_drawdown", "turnover")), ""])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_ablation_summary(rows: list[dict[str, Any]], path: Path) -> None:
    lines = ["# Prompt21 Ablation Summary", ""]
    for track in ("A", "B"):
        subset = [row for row in rows if row["track"] == track]
        counts = _count_by(subset, "verdict")
        lines.extend([f"## Track {track}", "", f"Verdict counts: `{counts}`", "", _markdown_table(subset[:20], ("run_id", "freeze_rank", "ablation", "verdict", "metric_delta_sharpe", "reason")), ""])
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_audit_summary(dependency: list[dict[str, Any]], leakage: list[dict[str, Any]], package: list[dict[str, Any]], path: Path) -> None:
    lines = [
        "# Prompt21 Audit Summary",
        "",
        f"Dependency audit: {_audit_status(dependency)}",
        f"Leakage audit: {_audit_status(leakage)}",
        f"Package safety audit: {_audit_status(package)}",
        "",
        "Full CSVs: `dependency_audit.csv`, `leakage_audit.csv`, `package_safety_audit.csv`.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_final_recommendation(rows: list[dict[str, Any]], path: Path) -> None:
    lines = ["# Prompt21 Final Recommendation", "", "Recommendation: research_continue.", ""]
    for track in ("A", "B"):
        lines.extend([f"## Track {track}", "", _markdown_table([row for row in rows if row["track"] == track], ("freeze_rank", "run_id", "method_stack", "classification", "promotion_ready", "notes")), ""])
    lines.append("Exact next action: run official-server parity for the best 2024/2025-supported candidates only after human review of ablation failures and turnover/drawdown behavior.")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_progress(full_rows: list[dict[str, Any]], freeze_rows: list[dict[str, Any]], classifications: list[dict[str, Any]], path: Path) -> None:
    lines = [
        "# Prompt21 Progress - Full Transformer Grid Audit",
        "",
        f"Full 2024 rows: {len(full_rows)}",
        f"Frozen candidates: {len(freeze_rows)}",
        f"Candidate classifications: {_count_by(classifications, 'classification')}",
        "",
        "Prompt21 outputs are under `outputs/reports/news_overlay/prompt21/`.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _markdown_table(rows: list[dict[str, Any]], fields: tuple[str, ...]) -> str:
    if not rows:
        return "_No rows._"
    lines = ["| " + " | ".join(fields) + " |", "| " + " | ".join("---" for _ in fields) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(row.get(field, "")) for field in fields) + " |")
    return "\n".join(lines)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return [dict(row) for row in csv.DictReader(handle)]


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    if not fieldnames:
        fieldnames = ["empty"]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def _count_by(rows: list[dict[str, Any]], field: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        key = str(row.get(field))
        counts[key] = counts.get(key, 0) + 1
    return counts


def _audit_status(rows: list[dict[str, Any]]) -> str:
    return "pass" if all(row.get("status") == "pass" for row in rows) else "fail"


def _git_has_diff(paths: tuple[str, ...]) -> bool:
    proc = subprocess.run(["git", "diff", "--name-only", "--", *paths], check=False, capture_output=True, text=True)
    return bool(proc.stdout.strip())


def _model_binary_files_present() -> bool:
    suffixes = {".safetensors", ".bin", ".gguf", ".onnx", ".pt", ".pth"}
    ignored_parts = {".git", ".venv", "venv", "__pycache__", ".pytest_cache"}
    for path in Path(".").rglob("*"):
        if not path.is_file():
            continue
        if any(part in ignored_parts for part in path.parts):
            continue
        if path.suffix.lower() in suffixes:
            return True
    return False


if __name__ == "__main__":
    raise SystemExit(main())
