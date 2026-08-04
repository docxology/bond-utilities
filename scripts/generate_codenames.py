#!/usr/bin/env python3
"""Thin CLI: print deterministic BOND codenames to stdout.

Business logic lives in src/bond_utilities/codenames.py; this script only
parses CLI flags and renders output through src/bond_utilities/reporting.py.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from bond_utilities import generate_codenames  # noqa: E402
from bond_utilities.reporting import banner, print_table  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate deterministic BOND codenames.")
    parser.add_argument("--count", type=int, default=5, help="number of codenames")
    parser.add_argument("--seed", type=str, default="20260804", help="reproducibility seed")
    parser.add_argument("--separator", type=str, default="-", help="adjective/noun joiner")
    args = parser.parse_args()

    names = generate_codenames(args.count, seed=args.seed, separator=args.separator)
    print(banner("Q-BRANCH CODENAME GENERATOR"))
    print_table(
        [[str(index + 1), name] for index, name in enumerate(names)],
        headers=["#", "codename"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
