# `src/` — bond-utilities (Q-BRANCH) importable package

## Purpose

`src/bond_utilities/` is the shared, dependency-free foundation of the BOND
suite. Every other bond package imports from it.

## Modules

| Module | Responsibility | Purity |
| --- | --- | --- |
| `ciphers.py` | Caesar, Vigenère, one-time-pad, XOR; codename encoding | pure |
| `codenames.py` | Deterministic adjective–noun codename generator | pure |
| `clock.py` | Elapsed time, schedule windows, T-minus countdowns | pure |
| `randomness.py` | `derive_seed`, `make_rng`, `seeded()` | pure (restores global state) |
| `mission_io.py` | JSON/YAML record persistence, schema, provenance | file I/O |
| `reporting.py` | Plain-text table/KV output | writes to an explicit stream |
| `testing.py` | Shared pytest fixtures/helpers | import-light, no mocks |
| `manuscript_variables.py` | `{{TOKEN}}` map from `manuscript/config.yaml` | reads config |
| `figures/plots.py` | Minimal schedule figure | writes PNG |

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
