# Reproducibility

## Artifact inventory

| Artifact | Producer |
| --- | --- |
| `output/data/manuscript_variables.json` | `scripts/z_generate_manuscript_variables.py` |
| `output/figures/mission_schedule.png` | `scripts/z_generate_manuscript_variables.py` → `src/bond_utilities/figures/plots.py` |

All artifacts are regenerated, never hand-edited. Regeneration is a single
command:

```bash
uv run python scripts/z_generate_manuscript_variables.py
```

## Determinism claims

- Codenames: `generate_codenames(count, seed=S)` returns the same list on
  every run and machine.
- Cipher keys: `generate_otp_key(length, seed=S)` returns the same bytes.
- Mission records: `record_provenance_outcome` stores the canonical input
  hash so any outcome can be re-derived from its persisted inputs.

## Quality gate

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
```

The gate enforces ≥90% line and branch coverage on `src/` (currently 100%),
with zero skipped and zero failed tests. `ruff check` + `ruff format` and
`mypy src/ scripts/` must pass clean.
