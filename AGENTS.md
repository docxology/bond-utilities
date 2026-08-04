# bond-utilities (Q-BRANCH)

The shared foundation package of the **BOND suite** — Layer 0. It ships
dependency-light primitives that every other bond package imports: classic
ciphers, deterministic codenames, mission clock math, seeded randomness,
mission-record persistence with provenance, plain-text reporting, and shared
test fixtures.

**Codename:** Q-BRANCH · **Version:** 0.1.0 · **License:** MIT

This is a **LOCAL-ONLY working tree** — there is no remote and nothing is
ever pushed.

## Layer contract

| Surface | Rule |
| --- | --- |
| `src/bond_utilities/*.py` | Pure primitives. No `infrastructure.*` imports; deterministic whenever a seed is supplied. |
| `src/bond_utilities/testing.py` | Shared fixtures; depends only on `pytest` + stdlib (never a mock framework). |
| `src/bond_utilities/figures/`, `manuscript_variables.py` | Orchestration: read config, write artifacts, delegate math to primitives. |
| `scripts/` | Thin orchestrators only. |
| `tests/` | Real data + computation only; **zero mocks**. |

Dependencies point one way: `scripts/ → src/`, `src/ → stdlib + numpy +
matplotlib + pyyaml`, `tests/ → src/`. See
[`manuscript/layer_contract.yaml`](manuscript/layer_contract.yaml).

## Modules

| Module | Responsibility |
| --- | --- |
| [`src/bond_utilities/ciphers.py`](src/bond_utilities/ciphers.py) | Caesar, Vigenère, one-time-pad, XOR; codename encoding helpers |
| [`src/bond_utilities/codenames.py`](src/bond_utilities/codenames.py) | Deterministic adjective–noun codename generator |
| [`src/bond_utilities/clock.py`](src/bond_utilities/clock.py) | Elapsed time, schedule windows, T-minus countdowns |
| [`src/bond_utilities/randomness.py`](src/bond_utilities/randomness.py) | Seeded RNG factory and `seeded(seed)` helper |
| [`src/bond_utilities/mission_io.py`](src/bond_utilities/mission_io.py) | JSON/YAML mission records, schema validation, provenance persistence |
| [`src/bond_utilities/reporting.py`](src/bond_utilities/reporting.py) | Plain-text table/KV output for thin CLIs |
| [`src/bond_utilities/testing.py`](src/bond_utilities/testing.py) | Shared pytest fixtures/helpers |
| [`src/bond_utilities/manuscript_variables.py`](src/bond_utilities/manuscript_variables.py) | `{{TOKEN}}` map from `manuscript/config.yaml` |
| [`src/bond_utilities/figures/plots.py`](src/bond_utilities/figures/plots.py) | Minimal schedule figure |

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

### Codenames (deterministic)

```python
from bond_utilities import generate_codenames, codename_for

names = generate_codenames(6, seed=20260804)
# Same seed -> same list, every run.
stable = codename_for("HQ-07", seed="ops")
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
from bond_utilities import make_rng, seeded
from bond_utilities.randomness import seeded

rng = make_rng("ops")            # reproducible generator

@seeded(20260804)
def draw() -> float:
    import random
    return random.random()
```

### Provenance mission records (bond-api integration point)

```python
from bond_utilities import record_provenance_outcome

record = record_provenance_outcome(
    mission_id="M-001",
    seed="ops",
    version="0.1.0",
    input_payload={"target": "grid", "count": 3},
    outcome={"matched_refs": 3, "status": "ok"},
    path="output/data/missions/M-001.json",
)
# record["provenance"]["input_hash"] reproducibly fingerprints the inputs.
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

Current gate: **100%** line+branch coverage on `src/`, 0 skipped, 0 failed,
zero mocks.

## Scripts

- [`scripts/generate_codenames.py`](scripts/generate_codenames.py) — print deterministic codenames
- [`scripts/record_mission.py`](scripts/record_mission.py) — persist a provenance-outcome mission record
- [`scripts/z_generate_manuscript_variables.py`](scripts/z_generate_manuscript_variables.py) — hydrate manuscript tokens + render schedule figure

## Documentation

Agent-facing docs live in [`docs/`](docs/AGENTS.md) (read-first:
[`docs/agent_instructions.md`](docs/agent_instructions.md)). The manuscript
source is in [`manuscript/`](manuscript/AGENTS.md). A Hermes skill for this
package lives at [`.agents/skills/bond-utilities/SKILL.md`](.agents/skills/bond-utilities/SKILL.md).
