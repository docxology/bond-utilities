# Output conventions

`output/` is a regenerable artifact tree — never hand-edit it, and it is
git-ignored. Regenerate the variable map, both figures, and their registry with:

```bash
uv run python scripts/z_generate_manuscript_variables.py
```

Two runs of that command on the same commit and toolchain write byte-identical
inputs. The schedule figure uses the date committed in the manuscript config. `tests/test_regeneration_determinism.py`
runs the command twice across a real clock tick and compares a digest of every
file below.

## Layout

| Path | Producer | Consumer |
| --- | --- | --- |
| `output/data/manuscript_variables.json` | `scripts/z_generate_manuscript_variables.py` | manuscript render / validation |
| `output/figures/mission_schedule.png` | same script → `src/bond_utilities/figures/plots.py::plot_mission_schedule` | manuscript `[@fig:schedule]` |
| `output/figures/letter_frequency.png` | same script → `plots.plot_frequency_analysis` | manuscript `[@fig:freq]` |
| `output/figures/figure_registry.json` | Same script | Stage 04 label and filename checks |

Mission records written by `scripts/record_mission.py` are user-specified
files (e.g. `output/data/missions/*.json`), not part of the fixed layout.

The [pinned render](rendering.md) creates `output/manuscript/` as an
intermediate tree. Its artifacts include `output/pdf/bond-utilities_combined.pdf`,
`output/web/index.html`, and individual PDFs in `output/slides/`. Stage 04
writes validation and rendered-provenance reports under `output/reports/`.

## Rules

- Never commit `output/`.
- Never hand-edit a generated artifact; change config or source and
  regenerate.
- Keep `data/` for versioned inputs only (e.g. `claim_ledger.yaml`), never
  for generated CSVs/JSONs/PNGs.
