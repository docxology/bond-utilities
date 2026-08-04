# Style guide — bond-utilities

Seven rules govern all code in this package.

1. **Zero-Mock.** Tests exercise real algorithms with real data. No mock
   framework, ever.
2. **Dependency Floor.** `src/bond_utilities/` imports only stdlib + numpy +
   matplotlib + pyyaml. No `infrastructure.*`, no other bond package.
3. **Thin Orchestrator.** `scripts/` hold no business logic — they parse
   args, call `src`, and render output.
4. **Determinism.** Every random draw uses a seeded generator. Document any
   wall-clock default (`now=None`) and never rely on it in tests.
5. **Show-Not-Tell.** Manuscript prose references explicit file/function
   names (e.g. `src/bond_utilities/ciphers.py::caesar_encrypt`).
6. **Type Hints + Docstrings.** All public functions are annotated and
   documented; run `mypy` clean.
7. **Provenance.** Persisted records carry an input hash, schema version,
   and seed so outcomes are reproducible.

## Conventions

- Format with `uv run ruff format` (120-column line length); check with
  `uv run ruff check`.
- `{{TOKEN}}`s in the manuscript are always generated, never hand-authored.
- Keep public exports centralized in `src/bond_utilities/__init__.py`.
