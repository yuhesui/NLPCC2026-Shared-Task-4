#!/usr/bin/env python3
"""CLI stub for running one future target-weight strategy."""

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--track", choices=["track1", "track2"], required=True)
    parser.add_argument("--strategy", required=True)
    parser.add_argument("--config", required=True)
    args = parser.parse_args()
    print(
        "PLANNED - not implemented yet: run strategy "
        f"{args.strategy} for {args.track} using {args.config}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
