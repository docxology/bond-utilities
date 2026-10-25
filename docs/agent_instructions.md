# Agent instructions — bond-utilities (Q-BRANCH)

Hard constraints for any agent working inside this package. Read this before
modifying source, tests, scripts, docs, or the manuscript.

## Rule 1 — Work only inside this package

Scope is exactly this package tree, `bond-utilities/` (its own git repo). Do not
touch sibling bond packages, the bond root files, or the template repo. Commit
inside this directory's own git repo only.

## Rule 2 — One repo, one remote

This tree is its own git repo on branch `main`, with a single remote:
`github.com/docxology/bond-utilities`. Publishing goes through the vault tooling
in the parent workspace. Never add a remote, never push another branch, never
force-push, never rewrite history.

## Rule 3 — Zero mocks

No mock framework: no `MagicMock`, `mocker.patch`, `unittest.mock`,
`@patch`, or `create_autospec`. Every test uses real data and real computation.
`pytest.MonkeyPatch` is allowed for *environment* isolation only (`chdir`,
swapping a module constant to reach a guard) — never to replace a dependency's
behaviour. See `testing_philosophy.md` for the substitution table.

## Rule 4 — Thin orchestrators

Business logic lives in `src/bond_utilities/`. A script in `scripts/` may parse
arguments, call `src`, and render output. Nothing else. If you find yourself
writing an algorithm in a script, it belongs in a module.

## Rule 5 — Determinism

Every random draw flows through a seeded generator (`make_rng`, `seeded()`, or
one of the `SEEDED_HELPERS`). Every function with a wall-clock default
(`now=None`) is called with an explicit `now=` in tests. No test may depend on
the time of day, the working directory, or system entropy.

## Rule 6 — Dependency floor

`src/bond_utilities/` imports only the standard library plus `numpy`,
`matplotlib`, and `pyyaml`. No `infrastructure.*`. No sibling bond package —
this is Layer 0 and every other package depends on it, so an upward import
would create a cycle across the whole fleet.

Specifically: `src/bond_utilities/testing.py` must stay importable without
numpy or matplotlib, because every other bond package re-exports its fixtures
from its own `conftest.py`.

## Rule 7 — Do not add a MissionProvider here

The `MissionProvider` protocol (`brief`/`recon`/`plan`/`execute`/`debrief`) and
the `GADGETS` registry belong to `bond-api` and the film packages. This package
supplies the primitives those providers are built from — notably
`mission_io.record_provenance_outcome` and `verify_provenance`. See
`architecture.md` for the full boundary.

## Rule 8 — Manuscript numbers are computed

Never hand-author a metric in prose. Every number in the manuscript arrives as
a `{{TOKEN}}` from `manuscript/config.yaml` via
`src/bond_utilities/manuscript_variables.py`. If you state a new quantitative
result, add the variable first, then reference the token. Two tests enforce
this: a token cross-reference and a bare-numeral guard over the abstract,
results, conclusion, and reproducibility sections.

## Rule 9 — Extend the public API, do not reshape it

The film fleet and Layers 1-4 import from `bond_utilities`. Adding a function
is safe. Renaming, removing, or changing the meaning of an existing parameter
is not. When you add a public name, put it in the module's `__all__` and, if it
is public API, in `src/bond_utilities/__init__.py` — `mission_io` and
`randomness` both carry tests that fail when `__all__` falls behind.

## Rule 10 — Quality gate

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/
uv run ruff format --check src/ scripts/
uv run mypy src/ scripts/
```

## Verification checklist (before saying "done")

1. `uv run pytest tests/ --cov=src --cov-fail-under=90` — green, 0 skipped,
   0 failed, coverage at or above the `fail_under` floor in `pyproject.toml`.
2. `uv run ruff check src/ scripts/` and `uv run ruff format --check src/ scripts/`
   — clean.
3. `uv run mypy src/ scripts/` — clean.
4. `rg -n "template[_]code_project"` — zero leftovers outside docs that
   explicitly explain the exemplar lineage.
5. `git status` — clean after your commit(s).
6. Report what you built, the coverage you actually measured, and the commit
   SHA. Never quote a number you did not run.
