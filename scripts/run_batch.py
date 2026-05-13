#!/usr/bin/env python3
"""CLI stub for future batch experiment runs."""

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--output-dir", default=".var/runs")
    args = parser.parse_args()
    print(
        "PLANNED - not implemented yet: run batch "
        f"using {args.config} into {args.output_dir}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
