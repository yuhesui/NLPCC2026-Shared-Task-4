"""Prepare local data mirrors and smoke-test subsets.

This module never mutates ``NLPCC_tasks/dataset``. If official files are still
Git LFS pointers, it records a precise skip reason instead of copying pointer
files as if they were usable CSV data.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import shutil
from typing import Any

from tools.data_tools.manifest_builder import (
    build_manifest,
    inspect_csv,
    read_lfs_pointer,
    sha256_file,
    write_manifest,
)


REPO_ROOT = Path(__file__).resolve().parents[3]
OFFICIAL_DATASET = REPO_ROOT / "NLPCC_tasks" / "dataset"
OFFICIAL_PRICE_DIR = OFFICIAL_DATASET / "price_data" / "export_data"
OFFICIAL_NEWS_DIR = OFFICIAL_DATASET / "news_data" / "export_data"


def _year_from_row(row: dict[str, str]) -> str | None:
    value = row.get("date") or row.get("THEDATE") or row.get("PUBLISH_TIME") or ""
    value = value.strip()
    if len(value) >= 4 and value[:4].isdigit():
        return value[:4]
    return None


def mirror_csvs_by_year(source_dir: Path, destination_dir: Path, year: int) -> list[dict[str, Any]]:
    destination_dir.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, Any]] = []
    for source_path in sorted(source_dir.glob("*.csv")):
        target_path = destination_dir / source_path.name
        pointer = read_lfs_pointer(source_path)
        if pointer:
            records.append(
                {
                    "source_path": str(source_path),
                    "target_path": str(target_path),
                    "status": "skipped_lfs_pointer",
                    "sha256": sha256_file(source_path),
                    **pointer,
                    "blocker": "Official CSV content is not hydrated from Git LFS.",
                }
            )
            continue

        with source_path.open("r", encoding="utf-8-sig", newline="") as source_handle:
            reader = csv.DictReader(source_handle)
            rows = [row for row in reader if _year_from_row(row) == str(year)]
            columns = reader.fieldnames or []

        if not rows:
            records.append(
                {
                    "source_path": str(source_path),
                    "target_path": str(target_path),
                    "status": "skipped_no_rows_for_year",
                    "year": year,
                    "source_inspection": inspect_csv(source_path),
                }
            )
            continue

        with target_path.open("w", encoding="utf-8", newline="") as target_handle:
            writer = csv.DictWriter(target_handle, fieldnames=columns)
            writer.writeheader()
            writer.writerows(rows)

        records.append(
            {
                "source_path": str(source_path),
                "target_path": str(target_path),
                "status": "copied_filtered_rows",
                "year": year,
                "row_count": len(rows),
                "sha256": sha256_file(target_path),
                "inspection": inspect_csv(target_path),
            }
        )
    return records


def create_smoke_subset(output_dir: Path) -> dict[str, Any]:
    price_dir = output_dir / "price_data"
    news_dir = output_dir / "news_data"
    price_dir.mkdir(parents=True, exist_ok=True)
    news_dir.mkdir(parents=True, exist_ok=True)

    price_rows = [
        {"date": "20250102", "open": "10.00", "high": "10.30", "low": "9.90", "close": "10.20", "change": "0.20", "pctchange": "2.0", "volume": "100000"},
        {"date": "20250103", "open": "10.20", "high": "10.40", "low": "10.10", "close": "10.30", "change": "0.10", "pctchange": "0.98", "volume": "110000"},
        {"date": "20250106", "open": "10.30", "high": "10.50", "low": "10.20", "close": "10.40", "change": "0.10", "pctchange": "0.97", "volume": "120000"},
    ]
    price_files = []
    for fund_id in ("000300.SH", "512880.SH"):
        price_path = price_dir / f"{fund_id}.csv"
        with price_path.open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(price_rows[0].keys()))
            writer.writeheader()
            writer.writerows(price_rows)
        price_files.append(str(price_path))

    news_rows = [
        {
            "APP_TYPE": "smoke",
            "LIST_TYPE": "finance",
            "THEDATE": "2025-01-02",
            "TITLE": "Smoke macro news before cutoff",
            "RANKING": "1",
            "CONTENT_ID": "smoke-1",
            "PUBLISH_TIME": "2025-01-02 14:30:00",
            "CONTENT": "Synthetic smoke news item.",
        },
        {
            "APP_TYPE": "smoke",
            "LIST_TYPE": "finance",
            "THEDATE": "2025-01-02",
            "TITLE": "Smoke news after cutoff",
            "RANKING": "2",
            "CONTENT_ID": "smoke-2",
            "PUBLISH_TIME": "2025-01-02 15:30:00",
            "CONTENT": "This should be excluded on the same day.",
        },
    ]
    news_names = [
        "caixin_daily_dedup.csv",
        "sinafinance_daily_dedup.csv",
        "sina_finance_daily_dedup.csv",
        "tencent_daily_dedup.csv",
        "tiantian_daily_dedup.csv",
        "tiantian_fund_daily_dedup.csv",
    ]
    for name in news_names:
        with (news_dir / name).open("w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(news_rows[0].keys()))
            writer.writeheader()
            writer.writerows(news_rows)

    manifest = {
        "price_files": price_files,
        "news_files": [str(news_dir / name) for name in news_names],
        "note": "Synthetic smoke subset for plumbing checks only; not training data.",
    }
    (output_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def prepare_data_foundation(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    train_root = repo_root / "data" / "train_2024"
    public_root = repo_root / "data" / "public_a_2025"
    smoke_root = repo_root / "data" / "sample" / "smoke_test"

    official_price_manifest = build_manifest(
        OFFICIAL_PRICE_DIR,
        train_root / "manifests" / "official_price_source_manifest.json",
        "official_price_source",
    )
    official_news_manifest = build_manifest(
        OFFICIAL_NEWS_DIR,
        train_root / "manifests" / "official_news_source_manifest.json",
        "official_news_source",
    )

    train_records = mirror_csvs_by_year(OFFICIAL_PRICE_DIR, train_root / "price_data", 2024)
    train_records += mirror_csvs_by_year(OFFICIAL_NEWS_DIR, train_root / "news_data", 2024)
    public_records = mirror_csvs_by_year(OFFICIAL_PRICE_DIR, public_root / "price_data", 2025)
    public_records += mirror_csvs_by_year(OFFICIAL_NEWS_DIR, public_root / "news_data", 2025)

    train_manifest = write_manifest(train_records, train_root / "manifests" / "data_copy_manifest.json", "train_2024_copy")
    public_manifest = write_manifest(public_records, public_root / "manifests" / "data_copy_manifest.json", "public_a_2025_copy")
    shutil.copy2(train_root / "manifests" / "official_price_source_manifest.json", public_root / "manifests" / "official_price_source_manifest.json")
    shutil.copy2(train_root / "manifests" / "official_news_source_manifest.json", public_root / "manifests" / "official_news_source_manifest.json")
    smoke_manifest = create_smoke_subset(smoke_root)

    return {
        "official_price_manifest_files": official_price_manifest["file_count"],
        "official_news_manifest_files": official_news_manifest["file_count"],
        "train_records": train_manifest["file_count"],
        "public_records": public_manifest["file_count"],
        "smoke_manifest": smoke_manifest,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare local NLPCC data foundations.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--output-json", default="outputs/smoke_tests/data_setup_summary.json")
    args = parser.parse_args()

    summary = prepare_data_foundation(Path(args.repo_root))
    output_path = Path(args.output_json)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
