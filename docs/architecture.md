# Architecture — bond-utilities (Q-BRANCH)

## Layer boundaries

```
manuscript/config.yaml
        │  (mission parameters)
        ▼
src/bond_utilities/                 scripts/            tests/
  primitives:                        thin CLIs           real data
  ciphers.py        ◄─────────────── generate_codenames    no mocks
  codenames.py      ◄─────────────── record_mission
  clock.py
  randomness.py
  mission_io.py     ◄─────────────── z_generate_manuscript_variables
  reporting.py
  orchestration:
  manuscript_variables.py ◄────────────┘
  figures/plots.py   ◄───────────────────┘
  testing.py         (shared fixtures, consumed by tests)
```

Dependencies point one way: `scripts/ → src/`, `src/ → stdlib + numpy + matplotlib + pyyaml`, `tests/ → src/`. Nothing imports upward.

## Primitive modules

| Module | Pure logic | Side effects |
| --- | --- | --- |
| `ciphers.py` | Caesar/Vigenère/OTP/XOR, codename encoding | none |
| `codenames.py` | Word lists + sampling | none (deterministic) |
| `clock.py` | elapsed/window/T-minus math | none |
| `randomness.py` | `derive_seed`, `make_rng`, `seeded` | mutates global `random` briefly, restored |
| `mission_io.py` | schema + hashing | reads/writes files |
| `reporting.py` | text rendering | writes to an explicit stream |

## Forbidden patterns

- Importing `infrastructure.*` inside `src/bond_utilities/`.
- Implementing business logic inside `scripts/`.
- Using mocks in tests.
- Hardcoding a manuscript metric in prose instead of a `{{TOKEN}}`.

## Adding a primitive

1. Add a pure function to the relevant `src/bond_utilities/*.py` module with
   type hints and a docstring.
2. Export it from `src/bond_utilities/__init__.py` if it is public API.
3. Add a real-data unit test in `tests/test_<module>.py`.
4. Run `uv run pytest tests/ --cov=src --cov-fail-under=90`.
