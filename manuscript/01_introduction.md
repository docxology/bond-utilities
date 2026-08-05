# Introduction

`bond-utilities` is Layer 0 of the BOND suite: the shared, dependency-free
foundation imported by every other bond package. It deliberately keeps its
dependency surface to the standard library plus `numpy`, `matplotlib`, and
`pyyaml`, and it never imports a mock framework.

Three principles govern the design:

1. **Determinism.** Every random draw flows through a seeded generator
   (`src/bond_utilities/randomness.py`). The same seed produces the same
   codenames, cipher keys, and test streams on every run and machine.
2. **Round-trip guarantees.** Each cipher is accompanied by a test proving
   `decrypt(encrypt(x)) == x` on real streams, and codename obfuscation
   satisfies `restore(obfuscate(x)) == x`.
3. **Provenance-first persistence.** Mission records written by
   `mission_io.py` bundle a canonical input hash, the schema version, and
   the producing seed, so every outcome can be reproduced from its
   persisted inputs — the contract bond-api outcomes rely on.

## Module map

| Module | Responsibility |
| --- | --- |
| `ciphers.py` | 9 classical ciphers + 8 cryptanalysis helpers; codename encoding |
| `codenames.py` | 5 deterministic codename schemes (adjective–noun, alliterative, NATO, numeric, token) |
| `clock.py` | Elapsed time, schedule windows, overlap/merge, duration parsing, T-minus, `MissionSchedule` |
| `randomness.py` | Seeded RNG factory, `seeded()` decorator, and scalar/sequence draw helpers |
| `mission_io.py` | JSON/YAML records, schema validation, provenance verify/append/summary |
| `reporting.py` | Plain-text table, key/value, banner, and schedule-table output |
| `testing.py` | Shared pytest fixtures/helpers (import-light, no mocks) |
| `figures/` | Deterministic schedule and letter-frequency figures |

## Reader's guide

`02_methodology.md` defines the cipher math and cryptanalysis, the codename
schemes, the seeding, and the clock/window semantics. `03_results.md` reports
the measured round-trips, determinism, cryptanalysis demos, and schedule
results. `05_experimental_setup.md` documents the mission parameters that
drive every token in this manuscript.
