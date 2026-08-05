# Reproducibility

## Artifact inventory

| Artifact | Producer |
| --- | --- |
| `output/data/manuscript_variables.json` | `scripts/z_generate_manuscript_variables.py` |
| `output/figures/mission_schedule.png` | same script → `src/bond_utilities/figures/plots.py::plot_mission_schedule` |
| `output/figures/letter_frequency.png` | same script → `plots.plot_frequency_analysis` |

All artifacts are regenerated, never hand-edited. Regeneration is a single
command:

```bash
uv run python scripts/z_generate_manuscript_variables.py
```

## Determinism claims

- Codenames: `generate_codenames(count, seed=S, scheme=...)` returns the same
  list on every run and machine, for every scheme.
- Cipher keys and byte draws: `generate_otp_key`/`seeded_bytes(length, seed=S)`
  return the same bytes.
- Cryptanalysis: frequency, IC, chi-squared, Kasiski, and Caesar/Vigenère
  breaking are deterministic functions of the input text.
- Mission records: `record_provenance_outcome` stores the canonical input
  hash; `verify_provenance` recomputes it, so any outcome can be audited and
  re-derived from its persisted inputs.

## Quality gate

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
```

The gate enforces ≥90% line and branch coverage on `src/` (currently 100%),
with zero skipped and zero failed tests. `ruff check` + `ruff format --check`
and `mypy src/ scripts/` must pass clean.
