#!/usr/bin/env python3
"""Thin CLI: persist a provenance-outcome mission record via bond-utilities.

This is the integration point bond-api will call to record outcomes: it
writes a mission record with an input hash, schema version, and seed. All
logic lives in src/bond_utilities/mission_io.py.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from bond_utilities import record_provenance_outcome  # noqa: E402
from bond_utilities.reporting import banner, print_kv  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Persist a BOND provenance-outcome mission record.")
    parser.add_argument("--mission-id", required=True, help="stable mission identifier")
    parser.add_argument("--codename", default=None, help="optional mission codename")
    parser.add_argument("--seed", type=str, default="20260804", help="reproducibility seed")
    parser.add_argument("--version", default="0.1.0", help="package/schema version")
    parser.add_argument("--payload", default="{}", help="JSON input payload, e.g. '{\"n\": 3}'")
    parser.add_argument("--out", required=True, help="destination file (.json or .yaml)")
    parser.add_argument("--fmt", choices=["json", "yaml"], default=None, help="record format")
    args = parser.parse_args()

    payload = json.loads(args.payload)
    record = record_provenance_outcome(
        mission_id=args.mission_id,
        seed=args.seed,
        version=args.version,
        input_payload=payload,
        outcome={},
        path=args.out,
        fmt=args.fmt,
        codename=args.codename,
    )
    print(banner("MISSION RECORD SAVED"))
    print_kv(
        [
            ("path", str(Path(args.out).resolve())),
            ("mission_id", record["mission_id"]),
            ("codename", record["codename"]),
            ("seed", record["seed"]),
            ("input_hash", record["provenance"]["input_hash"]),
            ("schema_version", record["provenance"]["schema_version"]),
        ]
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
