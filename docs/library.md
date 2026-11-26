# Library and worked examples

## What's inside

| Module | What it gives you |
| --- | --- |
| `ciphers` | 9 ciphers (Caesar, Vigenère, OTP, XOR, Atbash, Beaufort, rail-fence, Playfair, columnar) + 8 cryptanalysis helpers (frequency, IC, chi-squared, Caesar/Vigenère breaking, Kasiski) + codename encoding |
| `codenames` | 5 deterministic schemes (adjective–noun, alliterative, NATO, numeric, token) over curated 12x12 word pools, plus `codename_for` for a stable per-mission name |
| `clock` | `elapsed_time`, `window_open/elapsed/remaining`, `windows_overlap`, `merge_windows`, `parse_duration`, `schedule_status`, `t_minus`, and the frozen `MissionSchedule` dataclass — all half-open `[start, end)` UTC math |
| `randomness` | `derive_seed`, `make_rng`, the `seeded` decorator, and the `SEEDED_HELPERS` draw set (`seeded_bytes/int/float/choice/choices/shuffle/sample`) |
| `mission_io` | JSON/YAML record save/load, schema validation, `record_provenance_outcome`, `verify_provenance`, `append_outcome`, `load_records`, `record_summary` |
| `reporting` | `format_table`, `format_kv`, `banner`, `schedule_table`, and stream print helpers whose stdout default resolves at call time |
| `manuscript_variables` | Computes the whole `{{TOKEN}}` map for the manuscript from `docs/manuscript/config.yaml` |
| `figures/plots` | Deterministic `plot_mission_schedule` and `plot_frequency_analysis` PNGs |
| `testing` | Two shared pytest fixtures (`seeded_rng`, `mission_record`) plus two plain helpers imported directly (`temp_dir`, a context manager; `seeded_codenames`, a function) — import-light so consumers never pull numpy, matplotlib, or a mock framework |

## Usage

### Ciphers + cryptanalysis

```python
from bond_utilities import (
    atbash, caesar_break, caesar_encrypt, columnar_decrypt, columnar_encrypt,
    kasiski_key_lengths, rail_fence_decrypt, rail_fence_encrypt,
    vigenere_break, vigenere_encrypt,
)

ciphertext = caesar_encrypt("ATTACK AT DAWN", 5)
shift, plaintext = caesar_break(ciphertext)     # (5, 'ATTACK AT DAWN')

# Both breakers are statistical (chi-squared against English letter
# frequencies), so both need a letter-rich sample — this one is 202 letters.
sample = (
    "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOGANDTHENGATHERSGRACEFULACORNS"
    "FROMEVERYMAPLETREEBYTHERIVERBANKWHILETHEHUNTERSLEEPSSILENTLYIN"
    "THESHADOWOFTHECASTLECLOCKTOWERCOUNTINGTHEMINUTESUNTILTHEDAWN"
    "BREAKSOVERHORIZON"
)
cipher = vigenere_encrypt(sample, "LEMON")
key, decoded = vigenere_break(cipher, 5)        # key == 'LEMON', decoded == sample

# On short text they return a wrong answer with no confidence signal: for the
# 21-letter "THEQUICKBROWNFOXJUMPS", vigenere_break(..., 5) yields 'MTSMQ', and
# caesar_break of its shift-7 ciphertext yields shift 8. Measured, not
# hypothetical — asserted in tests/test_documented_examples.py.

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
print(numeric_codename("M-001", seed=7))    # 'QB-B6050C24' (format: QB-<8 hex digits>)
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
from bond_utilities import (
    __version__, append_outcome, record_provenance_outcome, verify_provenance,
)

record = record_provenance_outcome(
    mission_id="M-001", seed="ops", version=__version__,
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
uv run pytest tests/ --cov=src --cov-fail-under=90      # line+branch on src/
uv run --with ruff ruff check src/ scripts/
uv run --with ruff ruff format --check src/ scripts/
uv run --with mypy --with types-PyYAML mypy src/ scripts/
```

**The gate, not a snapshot.** The enforced coverage floor is the `fail_under`
value in `pyproject.toml → [tool.coverage.report]`; the manuscript quotes that
same number through a generated token, and a test asserts the two agree. No
measured percentage or test count is pasted into this README — run the command
above and read the real number, which is the only one that is ever current.

Beyond line coverage, the suite carries guards designed to fail: a manuscript
token cross-reference, a bare-numeral guard (with a positive control), a
hand-copied-metric guard across every manuscript section, `__all__` completeness
checks, registry-drift binding for `SEEDED_HELPERS`, `CIPHER_NAMES`,
`CRYPTANALYSIS_HELPERS` and `CODENAME_SCHEMES`, byte-determinism for both
figures, end-to-end regeneration determinism (the documented regeneration
command is run twice across a real clock tick and the whole `output/` tree must
hash the same), provenance mutation tests, and checks for quoted cipher and
codename results in this guide, `AGENTS.md`, and the quickstart. See
[the testing philosophy](testing_philosophy.md).

## Scripts

- `scripts/generate_codenames.py` — print deterministic codenames (any scheme)
- `scripts/record_mission.py` — persist (and `--verify`) a provenance mission record
- `scripts/cryptanalyze.py` — frequency/IC/Kasiski/Caesar/Vigenère analysis
- `scripts/z_generate_manuscript_variables.py` — hydrate tokens + render both figures
