#!/usr/bin/env python3
"""CLI stub for future ablation runs."""

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    parser.add_argument("--ablation", required=True)
    args = parser.parse_args()
    print(
        "PLANNED - not implemented yet: run ablation "
        f"{args.ablation} using {args.config}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
