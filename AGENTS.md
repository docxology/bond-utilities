# bond-utilities (Q-BRANCH)

The shared foundation package of the **BOND suite** — Layer 0. It ships
dependency-light primitives that every other bond package imports: classic
ciphers, deterministic codenames, mission clock math, seeded randomness,
mission-record persistence with provenance, plain-text reporting, and shared
test fixtures.

**Codename:** Q-BRANCH · **Version:** 0.3.0 · **License:** MIT

This is a **LOCAL-ONLY working tree** — there is no remote and nothing is
ever pushed.

## Layer contract

| Surface | Rule |
| --- | --- |
| `src/bond_utilities/*.py` | Pure primitives. No `infrastructure.*` imports; deterministic whenever a seed is supplied. |
| `src/bond_utilities/testing.py` | Shared fixtures + helpers; depends only on `pytest` + stdlib (never a mock framework). |
| `src/bond_utilities/figures/`, `manuscript_variables.py` | Orchestration: read config, write artifacts, delegate math to primitives. |
| `scripts/` | Thin orchestrators only. |
| `tests/` | Real data + computation only; **zero mocks**. |

Dependencies point one way: `scripts/ → src/`, `src/ → stdlib + numpy +
matplotlib + pyyaml`, `tests/ → src/`. See
[`manuscript/layer_contract.yaml`](manuscript/layer_contract.yaml).

## Modules

| Module | Responsibility |
| --- | --- |
| [`src/bond_utilities/ciphers.py`](src/bond_utilities/ciphers.py) | 9 classical ciphers (Caesar, Vigenère, OTP, XOR, Atbash, Beaufort, rail-fence, Playfair, columnar) + 8 cryptanalysis helpers; codename encoding |
| [`src/bond_utilities/codenames.py`](src/bond_utilities/codenames.py) | 5 deterministic codename schemes (adjective–noun, alliterative, NATO, numeric, token) |
| [`src/bond_utilities/clock.py`](src/bond_utilities/clock.py) | Elapsed time, schedule windows, overlap/merge, duration, T-minus; `MissionSchedule` |
| [`src/bond_utilities/randomness.py`](src/bond_utilities/randomness.py) | Seeded RNG factory, `seeded` helper, seeded scalar/sequence draws |
| [`src/bond_utilities/mission_io.py`](src/bond_utilities/mission_io.py) | JSON/YAML records, schema validation, provenance persistence + verify/append/summary |
| [`src/bond_utilities/reporting.py`](src/bond_utilities/reporting.py) | Plain-text table/KV/banner/schedule-table output for thin CLIs |
| [`src/bond_utilities/testing.py`](src/bond_utilities/testing.py) | Two shared pytest fixtures (`seeded_rng`, `mission_record`) + two plain helpers (`temp_dir`, `seeded_codenames`) |
| [`src/bond_utilities/manuscript_variables.py`](src/bond_utilities/manuscript_variables.py) | `{{TOKEN}}` map from `manuscript/config.yaml` |
| [`src/bond_utilities/figures/plots.py`](src/bond_utilities/figures/plots.py) | Schedule + letter-frequency figures |

## Installation

```bash
uv sync --extra dev
```

## Usage examples

### Ciphers

```python
from bond_utilities import caesar_encrypt, caesar_decrypt, xor_bytes

ciphertext = caesar_encrypt("ATTACK AT DAWN", 5)
assert caesar_decrypt(ciphertext, 5) == "ATTACK AT DAWN"

payload = b"mission payload"
key = b"\x2a\x1b\x4c"
assert xor_bytes(xor_bytes(payload, key), key) == payload
```

### Cryptanalysis

```python
from bond_utilities import caesar_break, caesar_encrypt, vigenere_encrypt, vigenere_break
from bond_utilities.ciphers import kasiski_key_lengths, index_of_coincidence

# Both breakers are statistical, so both need a letter-rich sample.
sample = (
    "THEQUICKBROWNFOXJUMPSOVERTHELAZYDOGANDTHENGATHERSGRACEFULACORNS"
    "FROMEVERYMAPLETREEBYTHERIVERBANKWHILETHEHUNTERSLEEPSSILENTLYIN"
    "THESHADOWOFTHECASTLECLOCKTOWERCOUNTINGTHEMINUTESUNTILTHEDAWN"
    "BREAKSOVERHORIZON"
)                                               # 202 letters

shift, plaintext = caesar_break(caesar_encrypt(sample, 7))  # shift == 7, plaintext == sample
vig = vigenere_encrypt(sample, "LEMON")
key, decoded = vigenere_break(vig, 5)           # key == 'LEMON', decoded == sample
print(kasiski_key_lengths(vig)[0], index_of_coincidence(vig))
```

**Short samples return a confident wrong answer.** On the 21-letter
`"THEQUICKBROWNFOXJUMPS"`, `caesar_break` of a shift-7 ciphertext returns
`(8, 'SGDPTHBJAQNVMENWITLOR')`, and `vigenere_break(..., 5)` of the same
ciphertext returns the key `'MTSMQ'`. Neither function reports confidence, so
the recovery claim holds only for letter-rich text.
[`tests/test_documented_examples.py`](tests/test_documented_examples.py)
asserts both the successes and these two failures.

### Codenames (deterministic)

```python
from bond_utilities import generate_codenames, codename_for, nato_codename

names = generate_codenames(6, seed=20260804)
# Same seed -> same list, every run.
stable = codename_for("HQ-07", seed="ops")
alliterative = generate_codenames(6, seed=20260804, scheme="alliterative")
print(nato_codename("QB7"))  # 'QUEBEC-BRAVO-7'
```

### Clock / scheduling

```python
from datetime import datetime, timezone
from bond_utilities import window_open, t_minus, format_elapsed

win = (datetime(2026, 8, 4, tzinfo=timezone.utc), datetime(2026, 8, 10, tzinfo=timezone.utc))
open_now = window_open(*win, now=datetime(2026, 8, 6, tzinfo=timezone.utc))  # True
```

### Seeded randomness

```python
import random

from bond_utilities import SEEDED_HELPERS, make_rng, seeded, seeded_bytes

rng = make_rng("ops")            # reproducible generator, fresh per call
key = seeded_bytes("ops", 32)    # 32 deterministic bytes from the same seed
print(SEEDED_HELPERS)            # the registry the manuscript counts

@seeded(20260804)
def draw() -> float:
    # The global `random` module is seeded for this call and restored after.
    return random.random()
```

### Provenance mission records (bond-api integration point)

```python
from bond_utilities import __version__, record_provenance_outcome, verify_provenance

record = record_provenance_outcome(
    mission_id="M-001",
    seed="ops",
    version=__version__,
    input_payload={"target": "grid", "count": 3},
    outcome={"matched_refs": 3, "status": "ok"},
    path="output/data/missions/M-001.json",
)
# record["provenance"]["input_hash"] reproducibly fingerprints the inputs.
assert verify_provenance(record)   # recomputes hash + seed + schema version
```

**No `MissionProvider` here.** The protocol (`brief`/`recon`/`plan`/`execute`/
`debrief`) and the `GADGETS` registry belong to `bond-api` and the film
packages. Layer 0 supplies the primitives those providers are built from — see
[`docs/architecture.md`](docs/architecture.md) for the boundary and rationale.

### Reporting

```python
from bond_utilities import format_table, format_kv, banner

print(banner("Q-BRANCH"))
print(format_table([["1", "SILENT-JAGUAR"]], headers=["#", "codename"]))
```

## Testing

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90      # line+branch on src/
uv run ruff check src/ scripts/
uv run ruff format --check src/ scripts/
uv run mypy src/ scripts/                               # mypy_path="src" in pyproject
rg -n "unittest\.mock|MagicMock|@patch|create_autospec" tests/ || echo clean
```

The enforced floor is `pyproject.toml → [tool.coverage.report] fail_under`.
Measured coverage and test counts are intentionally **not** quoted in this file
— run the command and read them. Quoting a snapshot here guarantees it is stale
by the next commit, and a stale number in an AGENTS file is worse than none.

Falsifiable guards in the suite (details in
[`docs/testing_philosophy.md`](docs/testing_philosophy.md)): manuscript token
cross-reference, hand-authored-numeral guard with a positive control,
`__all__` completeness, registry-drift binding for `SEEDED_HELPERS`,
`CIPHER_NAMES`, `CRYPTANALYSIS_HELPERS` and `CODENAME_SCHEMES`, provenance
mutation rejection, byte-determinism for *both* figures, end-to-end
regeneration determinism (`scripts/z_generate_manuscript_variables.py` run
twice across a real clock tick, whole-tree digest compared), documented-example
verification (every worked example in this file, the README and the quickstart
is executed and its quoted output is required to appear verbatim), and CLI flag
behaviour.

## Scripts

- [`scripts/generate_codenames.py`](scripts/generate_codenames.py) — print deterministic codenames (any scheme)
- [`scripts/record_mission.py`](scripts/record_mission.py) — persist (and `--verify`) a provenance-outcome mission record
- [`scripts/cryptanalyze.py`](scripts/cryptanalyze.py) — frequency/IC/Kasiski/Caesar/Vigenère analysis
- [`scripts/z_generate_manuscript_variables.py`](scripts/z_generate_manuscript_variables.py) — hydrate manuscript tokens + render both figures

## Documentation

Agent-facing docs live in [`docs/`](docs/AGENTS.md) (read-first:
[`docs/agent_instructions.md`](docs/agent_instructions.md)). The manuscript
source is in [`manuscript/`](manuscript/AGENTS.md). A Hermes skill for this
package lives at [`.agents/skills/bond-utilities/SKILL.md`](.agents/skills/bond-utilities/SKILL.md).
