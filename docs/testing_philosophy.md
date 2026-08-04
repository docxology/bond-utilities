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

The current suite runs at 100% line+branch on `src/`, with 0 skipped and 0
failed tests.

## What each test file covers

| File | Coverage |
| --- | --- |
| `test_ciphers.py` | Round-trip + known-vector + error branches for all ciphers and codename encoding |
| `test_codenames.py` | Determinism, uniqueness, bounds, separators, `codename_for` |
| `test_clock.py` | Elapsed/window/T-minus math, timezone normalization, schedule parsing errors |
| `test_randomness.py` | Seed derivation, reproducible streams, decorator state restore |
| `test_mission_io.py` | Schema validation, JSON/YAML round-trips, provenance hashing |
| `test_reporting.py` | Table/KV/banner rendering and stream output |
| `test_testing.py` | Shared fixtures/helpers work in a real pytest session |
| `test_manuscript_variables.py` | Token map + live `{{TOKEN}}` cross-reference against `manuscript/*.md` |
| `test_figures.py` | Real PNG output, default path, error branch |
| `test_scripts_smoke.py` | Subprocess smoke of the thin CLI scripts |

## Determinism

Random draws are always seeded. Shared fixtures hang off
`src/bond_utilities/testing.py` (`seeded_rng`, `mission_record`, `temp_dir`,
`seeded_codenames`), which depends only on `pytest` + stdlib so fixtures never
pull a mock framework.

## Reference

- Fixture inventory: [`tests/AGENTS.md`](../tests/AGENTS.md)
- Patterns: [`tests/PATTERNS.md`](../tests/PATTERNS.md)
