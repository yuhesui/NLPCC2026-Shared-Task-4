#!/usr/bin/env python3
"""CLI stub for running a future custom backtest wrapper."""

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    print(f"PLANNED - not implemented yet: run backtest using {args.config}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
