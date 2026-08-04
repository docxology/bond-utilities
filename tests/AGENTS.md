# tests/ — test suite

BOND suite — bond-utilities. All tests use **real data and real
computation**; no mocks. Coverage is measured over `src/` with
`--cov=src --cov-fail-under=90` (≥90% line+branch; currently 100%).

## Test files

| File | Coverage focus |
| --- | --- |
| `conftest.py` | `MPLBACKEND=Agg`, `sys.path`, re-exports shared fixtures |
| `test_ciphers.py` | All ciphers + codename encoding |
| `test_codenames.py` | Deterministic generator |
| `test_clock.py` | Elapsed/window/T-minus math |
| `test_randomness.py` | Seeded RNG + decorator |
| `test_mission_io.py` | Persistence + schema + provenance |
| `test_reporting.py` | Table/KV/banner rendering |
| `test_testing.py` | Shared fixtures/helpers in a live session |
| `test_manuscript_variables.py` | Token map + `{{TOKEN}}` cross-reference |
| `test_figures.py` | Schedule figure PNG output |
| `test_scripts_smoke.py` | Subprocess smoke of CLI scripts |

## Run

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run pytest tests/test_ciphers.py -q          # single module
```

## Patterns

- Deterministic, seeded draws only.
- Explicit `now=...` passed to any function with a wall-clock default.
- `io.StringIO` for capturing `reporting` output (no mocks).
- Fixtures come from `src/bond_utilities/testing.py` via `conftest.py`.
