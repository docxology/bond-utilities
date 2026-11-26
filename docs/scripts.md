# Command-line scripts

Run these from the package root after [setup](quickstart.md).

| Script | Purpose |
| --- | --- |
| [`generate_codenames.py`](../scripts/generate_codenames.py) | Print seeded codenames for a chosen scheme |
| [`record_mission.py`](../scripts/record_mission.py) | Write a JSON or YAML mission record and optionally verify its provenance |
| [`cryptanalyze.py`](../scripts/cryptanalyze.py) | Inspect classical-cipher examples and test recovery on suitable inputs |
| [`z_generate_manuscript_variables.py`](../scripts/z_generate_manuscript_variables.py) | Write the manuscript variable map and both generated figures |

The manuscript generator reads `docs/manuscript/config.yaml`.
`--no-figure` skips drawing the PNGs while writing the variable map.
The [render guide](rendering.md) describes the subsequent substitution and
rendering steps.
