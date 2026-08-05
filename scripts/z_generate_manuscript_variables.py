#!/usr/bin/env python3
"""Thin CLI: hydrate manuscript ``{{TOKEN}}``s and render the figures.

Reads ``manuscript/config.yaml`` via src/bond_utilities/manuscript_variables.py,
writes the resolved token map to ``output/data/manuscript_variables.json``,
and renders two deterministic figures referenced by the manuscript:

- ``output/figures/mission_schedule.png`` — the mission schedule window;
- ``output/figures/letter_frequency.png`` — letter counts of the codename sample.

``z_`` prefix keeps this last in alphabetical orchestration order.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from bond_utilities.clock import parse_schedule  # noqa: E402
from bond_utilities.figures import plot_frequency_analysis, plot_mission_schedule  # noqa: E402
from bond_utilities.manuscript_variables import (  # noqa: E402
    generate_variables,
    load_mission_config,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Hydrate BOND manuscript variables and figures.")
    parser.add_argument("--no-figure", action="store_true", help="skip rendering the figures")
    args = parser.parse_args()

    project_root = Path(__file__).resolve().parent.parent
    variables = generate_variables(project_root=project_root)

    data_dir = project_root / "output" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    out = data_dir / "manuscript_variables.json"
    out.write_text(json.dumps(variables, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    rendered: list[Path] = []
    if not args.no_figure:
        # Figure paths are anchored to the project root (not the working
        # directory) so the artifact tree is identical wherever this is run.
        figure_dir = project_root / "output" / "figures"
        config = load_mission_config(project_root)
        start, end = parse_schedule(config["mission"]["schedule"])
        rendered.append(plot_mission_schedule(start, end, path=figure_dir / "mission_schedule.png"))
        sample_text = " ".join(variables["RESULT_CODENAME_SAMPLE"].split(", "))
        rendered.append(plot_frequency_analysis(sample_text, path=figure_dir / "letter_frequency.png"))

    print(f"wrote {len(variables)} variables -> {out}")
    for path in rendered:
        print(f"rendered figure -> {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
