#!/usr/bin/env python3
"""Thin CLI: hydrate manuscript ``{{TOKEN}}``s and render the schedule figure.

Reads ``manuscript/config.yaml`` via src/bond_utilities/manuscript_variables.py,
writes the resolved token map to ``output/data/manuscript_variables.json``,
and renders ``output/figures/mission_schedule.png`` from the mission
schedule (the artifact referenced by the manuscript). ``z_`` prefix keeps it
last in alphabetical orchestration order.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from bond_utilities.clock import parse_schedule  # noqa: E402
from bond_utilities.figures import plot_mission_schedule  # noqa: E402
from bond_utilities.manuscript_variables import generate_variables, load_mission_config  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Hydrate BOND manuscript variables and figure.")
    parser.add_argument("--no-figure", action="store_true", help="skip rendering the schedule figure")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    variables = generate_variables(project_root=project_root)

    data_dir = project_root / "output" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    out = data_dir / "manuscript_variables.json"
    out.write_text(json.dumps(variables, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    figure_path: Path | None = None
    if not args.no_figure:
        config = load_mission_config(project_root)
        start, end = parse_schedule(config["mission"]["schedule"])
        figure_path = plot_mission_schedule(start, end)

    print(f"wrote {len(variables)} variables -> {out}")
    if figure_path is not None:
        print(f"rendered schedule figure -> {figure_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
