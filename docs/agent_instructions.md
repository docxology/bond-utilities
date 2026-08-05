# Agent Instructions — bond-utilities (Q-BRANCH)

These are hard constraints for any agent working inside this package. Read
this file before modifying source, tests, scripts, or the manuscript.

## Rule 1 — Work only inside your package

Scope is exactly `projects/working/bond/bond-utilities/`. Do not touch
sibling bond packages, bond root files, or the template repo. Commit with
path-scoped commits inside this directory's own git repo only.

## Rule 2 — Local only

This is a LOCAL-ONLY working tree. There is no remote. Never push.

## Rule 3 — Zero mocks

No mock framework (no `MagicMock`, `mocker.patch`, `unittest.mock`). All tests
use real data and real computation.

## Rule 4 — Thin orchestrators

Business logic lives in `src/bond_utilities/`; `scripts/` only parse args,
call `src`, and render output.

## Rule 5 — Determinism

Every random draw flows through a seeded generator (`make_rng`,
`seeded()`). No untracked random reliance in tests.

## Rule 6 — Dependency floor

`src/bond_utilities/` imports only the standard library plus `numpy`,
`matplotlib`, and `pyyaml`. No `infrastructure.*` imports, no other bond
package imports.

## Rule 7 — Manuscript variables are computed

Never hand-author metrics in prose. Every `{{TOKEN}}` comes from
`manuscript/config.yaml` via `src/bond_utilities/manuscript_variables.py`.

## Rule 8 — Quality gate

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90   # ≥90% line+branch on src/
uv run ruff check src/ scripts/
uv run ruff format --check src/ scripts/
uv run mypy src/ scripts/
```

## Verification checklist (before saying "done")

1. `uv run pytest tests/ --cov=src --cov-fail-under=90` — green, 0 skipped, 0 failed.
2. `rg -n "template[_]code_project"` — zero leftovers.
3. `git status` — clean after your commit(s).
4. Report: modules + concepts built, coverage %, commit SHA.
