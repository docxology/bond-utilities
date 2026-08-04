---
name: bond-utilities
description: BOND suite Layer 0 foundation (Q-BRANCH) — ciphers, codenames, clock, seeded randomness, mission records, reporting. Guardable, no mocks.
version: 0.1.0
author: docxology
license: MIT
tags: [bond, foundation, ciphers, deterministic, provenance, thin-orchestrator]
---

# bond-utilities (Q-BRANCH)

Project-scoped skill for the BOND suite's shared foundation package at
`projects/working/bond/bond-utilities/`. Load this when working inside the
package.

## When to Use

- Working inside `bond-utilities` — editing source, tests, or scripts.
- Adding a primitive that other bond packages will import.

## Quick Reference

```bash
# From the package root
uv run pytest tests/ --cov=src --cov-fail-under=90   # ≥90% line+branch on src/ (currently 100%)
uv run ruff check src/ scripts/
uv run ruff format --check src/ scripts/
uv run mypy src/ scripts/

# Regenerate manuscript tokens + schedule figure
uv run python scripts/z_generate_manuscript_variables.py
```

## Pitfalls

- **Keep scripts thin.** Business logic belongs in `src/bond_utilities/`, not
  `scripts/`.
- **No mocks.** Real data + computation only; no `unittest.mock`/`MagicMock`/
  `@patch`.
- **Dependency floor.** `src/bond_utilities/` imports only stdlib +
  numpy/matplotlib/pyyaml. No `infrastructure.*`, no other bond package.
- **Determinism.** Every random draw flows through `make_rng` / `seeded()`.
- **Computed tokens.** Never hand-author manuscript metrics; every
  `{{TOKEN}}` comes from `manuscript/config.yaml` via
  `src/bond_utilities/manuscript_variables.py`.
- **Local only.** This tree has no remote; never push.

## Cross-references

- Agent rules: `docs/agent_instructions.md`
- Layer contract: `manuscript/layer_contract.yaml`
- Skill bundle index: `.agents/skills/AGENTS.md`
