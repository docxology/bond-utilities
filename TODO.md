# bond-utilities TODO

Forward-only backlog for the bond-utilities package (codename **Q-BRANCH**),
Layer 0 of the BOND suite.

## Current status (phase 1)

- **Built** the 7 primitive modules in `src/bond_utilities/` (ciphers,
  codenames, clock, randomness, mission_io, reporting, testing) + a minimal
  `figures/` subpackage and `manuscript_variables.py`.
- **Tests**: 176 passed, 0 skipped, 0 failed; **100%** line+branch coverage
  on `src/` (gate ≥90%), zero mocks.
- **ruff + mypy**: clean on `src/` and `scripts/`.
- **Manuscript** rewritten for the BOND-UTILITIES identity (Q-BRANCH); every
  `{{TOKEN}}` is computed from `manuscript/config.yaml`.
- **Zero** `template_code_project` leftovers in the tree.

## Verification

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/
uv run mypy src/ scripts/
```

## Integration point (bond-api)

`src/bond_utilities/mission_io.py::record_provenance_outcome` is the
persistence helper bond-api outcomes will call: it writes a mission record
whose `provenance` block holds the canonical input hash, schema version, and
derived seed, so any outcome can be reproduced from its persisted inputs.
`scripts/record_mission.py` is a thin CLI demonstrating the contract.

## Open items

- [ ] Wire the manuscript render pipeline (PDF/output/manuscript) once the
      suite chooses a renderer; currently only tokens + the schedule figure
      are produced.
- [ ] Consider adding a `BOND_ALPHANUM`/base32-ish codename token alphabet if
      later packages need shorter, more readable identifiers than hex.
- [ ] If the word lists grow beyond 12×12, add an explicit
      `generate_codenames(..., allow_repeats=True)` knob (default stays
      unique).
- [ ] Keep `docs/_generated`-style live counts (test count / coverage) out of
      committed prose; this package has no such file — the numbers above are
      snapshots for this commit only.

## Guardrails honored

Path-scoped, local-only commits · no mock framework · ≥90% coverage ·
deterministic seeding · thin orchestrators · computed manuscript variables ·
zero `template_code_project` strings.
