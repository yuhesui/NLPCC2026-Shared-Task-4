#!/usr/bin/env python3
"""CLI stub for future submission packaging."""

import argparse


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--track", choices=["track1", "track2"], required=True)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--output-dir", default=".var/submissions")
    args = parser.parse_args()
    print(
        "PLANNED - not implemented yet: package submission "
        f"for {args.track}/{args.run_id} into {args.output_dir}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
