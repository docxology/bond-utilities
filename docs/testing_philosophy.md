# Testing Philosophy — bond-utilities

## Zero-Mock Policy

A core tenet of the BOND suite: **all tests use real data and real
computation** — no `unittest.mock`, `MagicMock`, `@patch`, or
`create_autospec` anywhere in `tests/`. Mocks can pass even when the real
algorithm is wrong; real data cannot. This is enforced by the layer contract
and audited with:

```bash
rg -n "unittest\.mock|MagicMock|@patch|create_autospec" tests/ || echo clean
```

## Coverage

Coverage is measured over `src/` only (test code is excluded from the metric).
The enforced gate is **≥90% line and branch coverage**:

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
```

The current suite runs at 100% line+branch on `src/` (316 tests), with 0
skipped and 0 failed.

## What each test file covers

| File | Coverage |
| --- | --- |
| `test_ciphers.py` | Round-trip + known-vector + error branches for all 9 ciphers, Playfair J/key handling, and the 8 cryptanalysis helpers (frequency, IC, chi-squared, Kasiski, Caesar/Vigenère breaking) |
| `test_codenames.py` | Determinism, uniqueness, bounds, separators, `codename_for`, and all 5 schemes (adjective–noun, alliterative, NATO, numeric, token) |
| `test_clock.py` | Elapsed/window/T-minus math, timezone normalization, schedule parsing, overlap/merge, duration parsing, `MissionSchedule` |
| `test_randomness.py` | Seed derivation, reproducible streams, decorator state restore, and all seeded draw helpers |
| `test_mission_io.py` | Schema validation, JSON/YAML round-trips, provenance hashing, `verify_provenance`, `load_records`, `record_summary`, `append_outcome` |
| `test_reporting.py` | Table/KV/banner rendering, stream output, `schedule_table` |
| `test_testing.py` | Shared fixtures/helpers work in a real pytest session |
| `test_manuscript_variables.py` | Token map + live `{{TOKEN}}` cross-reference against `manuscript/[0-9]*.md` |
| `test_figures.py` | Real PNG output (schedule + frequency), deterministic bytes, default path, error branches |
| `test_scripts_smoke.py` | Subprocess smoke of the thin CLI scripts (codenames, record, cryptanalyze, z-generate) |

## Determinism

Random draws are always seeded. Shared fixtures hang off
`src/bond_utilities/testing.py` (`seeded_rng`, `mission_record`, `temp_dir`,
`seeded_codenames`), which depends only on `pytest` + stdlib so fixtures never
pull a mock framework.

## Reference

- Fixture inventory: [`tests/AGENTS.md`](../tests/AGENTS.md)
- Patterns: [`tests/PATTERNS.md`](../tests/PATTERNS.md)
