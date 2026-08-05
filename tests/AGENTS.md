# tests/ — test suite

BOND suite — bond-utilities. All tests use **real data and real
computation**; no mocks. Coverage is measured over `src/` with
`--cov=src --cov-fail-under=90` (line+branch on `src/`; the enforced floor
is `fail_under` in `pyproject.toml` — read the measured percentage from the run,
never from a document).

## Test files

| File | Coverage focus |
| --- | --- |
| `conftest.py` | `MPLBACKEND=Agg`, `sys.path`, re-exports shared fixtures |
| `test_ciphers.py` | All 9 ciphers + Playfair details + 8 cryptanalysis helpers |
| `test_codenames.py` | All 5 schemes + determinism + bounds |
| `test_clock.py` | Elapsed/window/overlap/merge/duration + `MissionSchedule` |
| `test_randomness.py` | Seeded RNG + decorator + draw helpers |
| `test_mission_io.py` | Persistence + schema + provenance verify/append/summary |
| `test_reporting.py` | Table/KV/banner + schedule-table rendering |
| `test_testing.py` | Shared fixtures/helpers in a live session |
| `test_manuscript_variables.py` | Token map + `{{TOKEN}}` cross-reference |
| `test_figures.py` | Schedule + frequency figure PNG output |
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
