# Introduction

`bond-utilities` is Layer 0 of the BOND suite: the shared, dependency-free
foundation imported by every other bond package. It deliberately keeps its
dependency surface to the standard library plus `numpy`, `matplotlib`, and
`pyyaml`, and it never imports a mock framework.

Three principles govern the design:

1. **Determinism.** Every random draw flows through a seeded generator
   (`src/bond_utilities/randomness.py`). The same seed produces the same
   codenames, cipher keys, and test streams on every run and machine.
2. **Round-trip guarantees.** Each cipher in `ciphers.py` is accompanied by a
   test proving `decrypt(encrypt(x)) == x`, and codename obfuscation
   satisfies `restore(obfuscate(x)) == x`.
3. **Provenance-first persistence.** Mission records written by
   `mission_io.py` bundle a canonical input hash, the schema version, and the
   producing seed, so every outcome can be reproduced from its persisted
   inputs — the contract bond-api outcomes will rely on.

## Module map

| Module | Responsibility |
| --- | --- |
| `ciphers.py` | Caesar, Vigenère, one-time-pad, XOR; codename encoding helpers |
| `codenames.py` | Deterministic adjective–noun codename generator |
| `clock.py` | Elapsed time, schedule windows, T-minus countdowns |
| `randomness.py` | Seeded RNG factory and `seeded(seed)` decorator |
| `mission_io.py` | JSON/YAML record persistence, schema validation, provenance |
| `reporting.py` | Plain-text table and key/value output for thin CLIs |
| `testing.py` | Shared pytest fixtures/helpers (import-light, no mocks) |
| `figures/` | Minimal, deterministic matplotlib schedule figure |

## Reader's guide

`02_methodology.md` defines the cipher math, seeding, codename sampling, and
window semantics. `03_results.md` reports the measured round-trip,
determinism, and schedule results. `05_experimental_setup.md` documents the
mission parameters that drive every token in this manuscript.
