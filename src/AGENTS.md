# `src/` — bond-utilities (Q-BRANCH) importable package

## Purpose

`src/bond_utilities/` is the shared, dependency-free foundation of the BOND
suite. Every other bond package imports from it.

## Modules

| Module | Responsibility | Purity |
| --- | --- | --- |
| `ciphers.py` | 9 classical ciphers + 8 cryptanalysis helpers; codename encoding | pure |
| `codenames.py` | 5 deterministic codename schemes (adjective–noun, alliterative, NATO, numeric, token) | pure |
| `clock.py` | Elapsed time, schedule windows, overlap/merge, duration, T-minus; `MissionSchedule` | pure |
| `randomness.py` | `derive_seed`, `make_rng`, `seeded()`, seeded scalar/sequence draws | pure (restores global state) |
| `mission_io.py` | JSON/YAML persistence, schema, provenance verify/append/summary | file I/O |
| `reporting.py` | Table/KV/banner/schedule-table output | writes to an explicit stream |
| `testing.py` | Two pytest fixtures (`seeded_rng`, `mission_record`) + two plain helpers (`temp_dir`, `seeded_codenames`) | import-light, no mocks |
| `manuscript_variables.py` | `{{TOKEN}}` map from `manuscript/config.yaml` | reads config |
| `figures/plots.py` | Schedule + letter-frequency figures | writes PNG |

## Rules

- No `infrastructure.*` imports.
- No other bond package imports.
- Default dependency surface: stdlib + numpy + matplotlib + pyyaml.
- `testing.py` additionally imports `pytest` (dev-only) and must never pull a
  mock framework.
- Public API is centralized in `__init__.py`.

## See also

- [`../docs/architecture.md`](../docs/architecture.md)
- [`../manuscript/layer_contract.yaml`](../manuscript/layer_contract.yaml)
