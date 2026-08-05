# bond-utilities

> **Q-BRANCH** · The shared foundation of the BOND suite (Layer 0).

`bond-utilities` is a small, fully-tested, dependency-light Python package of
field-utility primitives for mission operations: a classic-cipher suite with
cryptanalysis helpers, deterministic codenames (several schemes), mission
clock/schedule math, seeded randomness, provenance mission records, and
plain-text reporting. Every other bond package imports from it.

**Principles**

- **Deterministic** — one seed fully determines codenames, keys, draws, and test streams.
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
uv run python scripts/generate_codenames.py --count 6 --scheme alliterative
uv run python scripts/cryptanalyze.py "THEQUICKBROWNFOX"
uv run python scripts/record_mission.py --mission-id M-001 --verify --out output/m.json
uv run python scripts/z_generate_manuscript_variables.py
uv run pytest tests/ --cov=src --cov-fail-under=90
```

## What's inside

| Module | What it gives you |
| --- | --- |
| `ciphers` | 9 ciphers (Caesar, Vigenère, OTP, XOR, Atbash, Beaufort, rail-fence, Playfair, columnar) + 8 cryptanalysis helpers (frequency, IC, chi-squared, Caesar/Vigenère breaking, Kasiski) + codename encoding |
| `codenames` | 5 deterministic schemes: adjective–noun, alliterative, NATO, numeric, token |
| `clock` | `elapsed_time`, `window_open/elapsed/remaining`, `windows_overlap`, `merge_windows`, `parse_duration`, `t_minus`, `MissionSchedule` |
| `randomness` | `derive_seed`, `make_rng`, `seeded`, `seeded_bytes/int/float/choice/choices/shuffle/sample` |
| `mission_io` | JSON/YAML record save/load, schema validation, `record_provenance_outcome`, `verify_provenance`, `append_outcome`, `load_records`, `record_summary` |
| `reporting` | `format_table`, `format_kv`, `banner`, `schedule_table`, stream print helpers |
| `testing` | Shared pytest fixtures (`seeded_rng`, `mission_record`, `temp_dir`, `seeded_codenames`) |

## Usage

### Ciphers + cryptanalysis

```python
from bond_utilities import (
    atbash, caesar_break, caesar_encrypt, columnar_decrypt, columnar_encrypt,
    kasiski_key_lengths, rail_fence_decrypt, rail_fence_encrypt,
    vigenere_break, vigenere_encrypt,
)

ciphertext = caesar_encrypt("ATTACK AT DAWN", 5)
shift, plaintext = caesar_break(ciphertext)     # (5, "ATTACK AT DAWN")

cipher = vigenere_encrypt("THEQUICKBROWNFOXJUMPS", "LEMON")
key, decoded = vigenere_break(cipher, 5)        # recover the keyword

assert atbash(atbash("HELLO")) == "HELLO"
assert rail_fence_decrypt(rail_fence_encrypt("QBRANCH", 3), 3) == "QBRANCH"
assert columnar_decrypt(columnar_encrypt("QBRANCH", "21"), "21") == "QBRANCH"
```

### Codenames (multiple schemes)

```python
from bond_utilities import generate_codenames, nato_codename, numeric_codename

adj_noun = generate_codenames(6, seed=20260804)
allo = generate_codenames(6, seed=20260804, scheme="alliterative")
print(nato_codename("QB7"))                 # 'QUEBEC-BRAVO-7'
print(numeric_codename("M-001", seed=7))    # 'QB-XXXXXXXX'
```

### Clock / schedule models

```python
from datetime import datetime, timezone
from bond_utilities import MissionSchedule, windows_overlap, parse_duration

win = MissionSchedule("grid", datetime(2026, 8, 4, tzinfo=timezone.utc),
                      datetime(2026, 8, 10, tzinfo=timezone.utc))
print(win.status(now=datetime(2026, 8, 6, tzinfo=timezone.utc)))  # 'ACTIVE'
# Overlap of two windows (in seconds) via windows_overlap:
secondary = (datetime(2026, 8, 6, 12, tzinfo=timezone.utc),
             datetime(2026, 8, 8, 12, tzinfo=timezone.utc))
shared = windows_overlap(win.start, win.end, secondary[0], secondary[1])  # 48h
print(parse_duration("1d 2h30m"))                                # 1 day 2:30
```

### Seeded randomness

```python
from bond_utilities import make_rng, seeded_bytes, seeded_choice, seeded_shuffle

rng = make_rng("ops")                    # reproducible generator
key = seeded_bytes("ops", 32)            # 32 deterministic bytes
choice = seeded_choice(7, ["A", "B", "C"])
deck = seeded_shuffle(7, list(range(52)))
```

### Provenance mission records (bond-api integration point)

```python
from bond_utilities import record_provenance_outcome, verify_provenance, append_outcome

record = record_provenance_outcome(
    mission_id="M-001", seed="ops", version="0.2.0",
    input_payload={"target": "grid", "count": 3},
    outcome={"matched_refs": 3, "status": "ok"},
    path="output/data/missions/M-001.json",
)
assert verify_provenance(record)          # recomputes input_hash + seed + version
append_outcome("output/data/missions/M-001.json", {"consumed": True})
```

### Reporting

```python
from bond_utilities import format_table, format_kv, banner
print(banner("Q-BRANCH"))
print(format_table([["1", "SILENT-JAGUAR"]], headers=["#", "codename"]))
```

## Testing

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90      # ≥90% line+branch on src/
uv run ruff check src/ scripts/
uv run ruff format --check src/ scripts/
uv run mypy src/ scripts/
```

Current gate: **100%** line+branch coverage on `src/` (316 tests), 0 skipped,
0 failed, zero mocks.

## Scripts

- `scripts/generate_codenames.py` — print deterministic codenames (any scheme)
- `scripts/record_mission.py` — persist (and `--verify`) a provenance mission record
- `scripts/cryptanalyze.py` — frequency/IC/Kasiski/Caesar/Vigenère analysis
- `scripts/z_generate_manuscript_variables.py` — hydrate tokens + render both figures

## Documentation

Agent-facing docs live in [`docs/`](docs/AGENTS.md) (read-first:
[`docs/agent_instructions.md`](docs/agent_instructions.md)). The manuscript
source is in [`manuscript/`](manuscript/AGENTS.md). A Hermes skill for this
package lives at [`.agents/skills/bond-utilities/SKILL.md`](.agents/skills/bond-utilities/SKILL.md).

## License

MIT — see [`LICENSE`](LICENSE).
