# bond-utilities TODO

Forward-only backlog for **Q-BRANCH** (Layer 0 of the BOND suite). This file
tracks what is *left*, not what is finished — the shipped surface is described
in [`README.md`](README.md) and [`docs/architecture.md`](docs/architecture.md),
and the history is in `git log`. Nothing here quotes a measured coverage
percentage or test count; those come from the run, not from a document.

## Open

### Rendering

- [ ] **Wire a manuscript render pipeline.** Today
      `scripts/z_generate_manuscript_variables.py` produces the token map and
      both figures, but nothing substitutes the tokens into a rendered PDF/HTML.
      Blocked on the suite choosing one renderer so all 33 packages match. Until
      then, `output/data/manuscript_variables.json` is the deliverable.

### Library gaps

- [ ] **Document (or measure) the `vigenere_break` sample floor.** Recovery is
      reliable on letter-rich ciphertext, but per-column chi-squared needs
      enough samples per column, and short texts can mis-estimate a shift. The
      limitation is stated in `manuscript/07_scope_and_related_work.md`; what is
      missing is an actual measured minimum-column-length curve to cite, which
      would need a new experiment and its own token.
- [ ] **Decide on `generate_codenames(..., allow_repeats=True)`.** The default
      `adjective_noun` scheme samples without replacement and therefore raises
      above the word-list capacity. That is the correct default; a documented
      opt-in for callers who want more names than the grid holds is not built.
      Only worth doing if a film package actually asks for it.
- [ ] **Codename word lists are small and curated by hand.** Fine for mission
      naming, wrong for anything that needs entropy. If a consumer starts
      treating codenames as identifiers with collision requirements, they need
      `codename_token` / `numeric_codename` instead — consider making that
      steering explicit in the API rather than only in prose.

### Suite integration

- [ ] **Confirm the `bond-api` outcome contract against the real dataclasses.**
      `mission_io.record_provenance_outcome` / `verify_provenance` are the
      persistence surface bond-api's `MissionOutcome` and `Provenance` are meant
      to land on, but this package has no test that round-trips an actual
      bond-api object — it cannot import one (Layer 0 depends on nothing). The
      binding test belongs in `bond-api`, and this entry is a reminder that the
      contract is currently asserted only in prose on this side.

### Housekeeping

- [ ] **`build/` reappears on every editable install.** It is gitignored, and
      the stale copy was deleted, but setuptools recreates it under the package
      root where it pollutes tree-wide greps with an outdated duplicate of every
      module. Point the build directory somewhere outside the package root, or
      delete it after each `uv sync`.

## Non-goals (do not "fix" these)

- **No `mission.py` / `MissionProvider` here.** The protocol belongs to
  `bond-api`; implementing it in Layer 0 would invert the dependency direction.
  See [`docs/architecture.md`](docs/architecture.md).
- **No cryptographic strength.** The cipher suite is educational and
  deterministic on purpose. Do not "harden" it; do not use it for secrecy.
- **No new dependencies.** `src/` stays on stdlib + numpy + matplotlib + pyyaml
  so every consumer's import stays cheap and mock-free.
- **No renamed or reshaped public API.** The film fleet and Layers 1-4 import
  from `bond_utilities`. Add; do not rename.

## Verification

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/
uv run ruff format --check src/ scripts/
uv run mypy src/ scripts/
git status --short
```
