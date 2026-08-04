# bond-utilities

> **Q-BRANCH** · The shared foundation of the BOND suite (Layer 0).

`bond-utilities` is a small, fully-tested, dependency-light Python package of
field-utility primitives for mission operations: classic ciphers,
deterministic codenames, mission clock math, seeded randomness, provenance
mission records, and plain-text reporting. Every other bond package imports
from it.

**Principles**

- **Deterministic** — one seed fully determines codenames, keys, and test streams.
- **Round-trip verified** — every cipher passes `decrypt(encrypt(x)) == x` with real data.
- **Provenance-first** — mission records carry an input hash, schema version, and seed.
- **Zero mocks** — tests use real data and real computation only.

## Install

```bash
uv sync --extra dev
```

## Quick start

```bash
uv run python scripts/generate_codenames.py --count 6 --seed 20260804
uv run python scripts/z_generate_manuscript_variables.py
uv run pytest tests/ --cov=src --cov-fail-under=90
```

## What's inside

| Module | What it gives you |
| --- | --- |
| `ciphers` | Caesar, Vigenère, one-time-pad, XOR + codename encoding helpers |
| `codenames` | Deterministic `ADJECTIVE-NOUN` codenames from a 12×12 word grid |
| `clock` | `elapsed_time`, `window_open/elapsed/remaining`, `t_minus` |
| `randomness` | `derive_seed`, `make_rng`, `seeded(seed)` |
| `mission_io` | JSON/YAML record load/save, schema validation, `record_provenance_outcome` |
| `reporting` | `format_table`, `format_kv`, `banner`, stream print helpers |
| `testing` | Shared pytest fixtures (`seeded_rng`, `mission_record`, `temp_dir`) |

For full examples see [`AGENTS.md`](AGENTS.md). For contributor rules see
[`docs/agent_instructions.md`](docs/agent_instructions.md).

## Status

- Coverage: **100%** line+branch on `src/` (gate ≥90%)
- Tests: 176 passed, 0 skipped, 0 failed
- ruff + mypy: clean
- Mocks: none

## License

MIT — see [`LICENSE`](LICENSE).
