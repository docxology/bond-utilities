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

Running that command twice on the same commit rewrites every artifact above
**byte for byte**. Nothing in the pipeline reads the wall clock: the token map
is a pure function of `manuscript/config.yaml` and the library registries, and
the schedule figure's reference marker is pinned to `paper.date` through
`manuscript_variables.manuscript_instant()` rather than to `datetime.now()`.
The claim is bound by `tests/test_regeneration_determinism.py`, which runs the
command above twice — separated by a real clock tick, so a reinstated
timestamp cannot slip through — and compares a digest of the whole `output/`
tree. The scope is exactly that artifact tree; nothing here is a claim about
the wider environment, which the experimental-setup section pins separately.

## Determinism claims

- Codenames: `generate_codenames(count, seed=S, scheme=...)` returns the same
  list on every run and machine, for every scheme.
- Cipher keys and byte draws: `generate_otp_key(length, seed=S)` delegates to
  `seeded_bytes(S, length)`, so both return the same bytes for the same seed.
- Every other seeded helper ({{SEEDED_HELPERS_CSV}}) builds its own
  `random.Random` from the seed, so a draw never depends on call order.
- Cryptanalysis: frequency, IC, chi-squared, Kasiski, and Caesar/Vigenère
  breaking are deterministic functions of the input text.
- Mission records: `record_provenance_outcome` stores the canonical input
  hash; `verify_provenance` recomputes it, so any outcome can be audited and
  re-derived from its persisted inputs.

## Quality gate

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/
uv run ruff format --check src/ scripts/
uv run mypy src/ scripts/
```

The gate enforces at least {{COVERAGE_GATE_PERCENT}}% line **and** branch
coverage on `src/`, and tolerates at most {{MAX_TEST_FAILURES}} failing tests.
Both numbers come from `manuscript/config.yaml`, and a test asserts the
coverage figure equals the `fail_under` value actually enforced by
`pyproject.toml` — the prose cannot drift away from the enforced gate. The
measured coverage of any given run is deliberately not quoted here; run the
command above to read it. `ruff check`, `ruff format --check`, and
`mypy src/ scripts/` must also pass clean.
