# TODO — bond-utilities (Q-BRANCH)

`bond-utilities` is Layer 0 of the BOND suite: a dependency-light Python package
of mission primitives — nine classical ciphers with cryptanalysis helpers, five
deterministic codename schemes, UTC schedule math, seeded randomness,
provenance-carrying mission records, plain-text reporting, and shared pytest
fixtures. Every other bond package imports it; it imports none of them.

**Verified state (measured 2026-08-05, this session, Python 3.14.6):**
`uv run pytest tests/ --cov=src --cov-fail-under=90` → **384 passed**,
**100.00%** line+branch coverage over `src/` (816 statements, 270 branches, 0
missed) against the 90% floor in `pyproject.toml:65`. `ruff check`,
`ruff format --check`, and `mypy src/ scripts/` are all clean. Working tree is
clean at `git status --short`.

This file tracks what is *left*. Completed work is deleted from here — the
shipped surface is described in [`README.md`](README.md) and
[`docs/architecture.md`](docs/architecture.md), and the history is in `git log`.

---

## Open work

### Correctness

**None open.**

What was checked to conclude that: all ten findings in the adversarial audit
(`../output/verify/bond-utilities.json`) were re-tested against the tree today,
and each named location now matches the code.

| Audit finding | Verified resolved by |
| --- | --- |
| SEVERE — intro hard-coded `9 ciphers / 8 helpers / 5 schemes` | `manuscript/01_introduction.md:25-26` now emits `{{CIPHER_COUNT}}`, `{{CRYPTANALYSIS_HELPERS}}`, `{{CODENAME_SCHEME_COUNT}}` |
| SEVERE — three worked examples asserted outputs the code does not produce | `tests/test_documented_examples.py` (22 tests) computes each documented value and requires it verbatim in the quoting file |
| SEVERE — two bibliography annotations described behaviour that does not exist | `tests/test_documented_examples.py:149-206` (`TestBibliographyClaimsMatchTheCode`) |
| MODERATE — only one figure had a determinism test | `tests/test_figures.py:48` and `:79` — `test_deterministic_bytes` now exists in both classes, plus a negative control at `:62` |
| MODERATE — "three families", then four were listed | `manuscript/02_methodology.md:4` reads "four families" |
| MODERATE — three of four registries bound only to literal copies | `tests/test_ciphers.py:121` (`TestRegistryBinding`) and `tests/test_codenames.py:196` (`TestSchemeRegistryBinding`) |
| MODERATE — alliterative repeats unexplained and unguarded | `manuscript/03_results.md:43-49` + `tests/test_codenames.py:263,278` |
| MODERATE — SKILL.md quoted a `100%` coverage snapshot | `.agents/skills/bond-utilities/SKILL.md:25` now reads `# enforced floor = pyproject fail_under` |
| MODERATE — all four `testing.py` names called fixtures | `README.md:71`, `docs/architecture.md:218`, `AGENTS.md:38` all distinguish two fixtures from two plain helpers |
| MODERATE — unqualified `caesar_break` recovery claim | `manuscript/07_scope_and_related_work.md:30-38` carries the short-sample caveat for *both* breakers |

### Verification

Claims that are true today but are not yet bound by a test that can fail.

#### V1 — Algorithm constants in two sections are outside the bare-numeral guard

*From unresolved audit finding 1.* The abstract and conclusion claim generated
numbers *with a stated exception*. The exception is real: `mod 26`
(`manuscript/02_methodology.md:6-7`), the `5x5` Playfair square (`:9`), and the
reference IC values `~0.066` / `~0.038` (`:20-21`) are hand-written literals.
Those two sections are listed in `DEFINITIONAL_SECTIONS`
(`tests/test_manuscript_variables.py:269`) and excluded from
`QUANTITATIVE_SECTIONS` (`:259`), so the bare-numeral guard never sees them.
They are covered only by the hand-copied-metric guard
(`tests/test_manuscript_variables.py:374`), which fails only if a literal
*equals a current metric value*.

- **Residual hole:** a new hand-authored number in `02_methodology.md` or
  `07_scope_and_related_work.md` that does not happen to equal a metric passes
  both guards.
- **Done looks like:** those two sections are scanned by a guard that admits
  only a closed, named set of algorithm constants (each carrying the reason it
  is a constant and not a measurement), and a planted extra numeral in either
  section makes the suite red. The previous author judged an exemption
  allowlist to be a worse boundary than the stated exception — if that judgment
  still holds, move this entry to Known limitations rather than half-building it.
- **Demonstrate:** insert a bare `17` into a prose line of
  `manuscript/02_methodology.md`, then
  `uv run pytest tests/test_manuscript_variables.py -k "HandAuthored or HandCopied" -q`
  must fail; revert and it must pass.

#### V2 — `99_references.md` is excluded from the hand-copied-metric guard

*From unresolved audit finding 2.* Bibliographic volume/page/year numbers
collide with package metrics (journal volume `8` vs `CRYPTANALYSIS_HELPERS`
`8`), so the bibliography is the one section the metric guard skips. The
exclusion itself is pinned — `tests/test_manuscript_variables.py:368`
(`test_only_the_bibliography_is_excluded`) fails if the skip list grows — but
the bibliography's own prose is guarded only by the two code-binding tests at
`tests/test_documented_examples.py:149-206`.

- **Done looks like:** the guard scans `99_references.md` with citation
  metadata (the `volume`/`pages`/`year` fields of each entry, derived from
  `manuscript/references.bib`) subtracted, so a hand-copied metric in a
  bibliography *annotation* is caught while a legitimate volume number is not.
- **Demonstrate:** paste the current `CIPHER_COUNT` value as a standalone
  numeral into an annotation line of `manuscript/99_references.md`; the new
  guard must fail. Then confirm the untouched file passes:
  `uv run pytest tests/test_manuscript_variables.py::TestGeneratedMetricsAreNotHandCopied -q`.

#### V3 — `CRYPTANALYSIS_HELPERS` reverse binding rests on a hand-listed partition

*From unresolved audit finding 3.* `tests/test_ciphers.py:111-113` declares
`_KEY_AND_CODENAME_UTILITIES = {generate_otp_key, obfuscate_codename,
restore_codename, codename_token}` and the partition tests at `:185` and `:194`
require `ciphers.__all__` to be exactly cipher entrypoints ∪
`CRYPTANALYSIS_HELPERS` ∪ that set. Adding a new public function does force a
classification decision (this was verified with two planted functions), but an
author can still mis-classify a genuine analysis helper into the utility set and
keep the gate green while `CRYPTANALYSIS_HELPERS` under-counts.

- **Done looks like:** the registry is derived from the source rather than
  restated in the test — e.g. a marker decorator applied in
  `src/bond_utilities/ciphers.py` that both populates `CRYPTANALYSIS_HELPERS`
  and makes the utility set the *unmarked* remainder, so mis-classification is
  no longer expressible.
- **Demonstrate:** add a new analysis helper to `ciphers.py` without touching
  any test file; `uv run pytest tests/test_ciphers.py -q` must pass with the
  helper counted, and the manuscript token `{{CRYPTANALYSIS_HELPERS}}` must
  change on the next `scripts/z_generate_manuscript_variables.py` run.
- **Note:** this requires editing `src/`, which is out of scope for a docs pass.

#### V4 — The `bond-api` outcome contract is asserted only in prose

`src/bond_utilities/mission_io.py:153` (`record_provenance_outcome`) and `:212`
(`verify_provenance`) are described in `README.md:146-161` and `AGENTS.md:130-145`
as the persistence surface that `bond-api`'s `Provenance`
(`../bond-api/src/bond_api/protocol.py:192`) and `MissionOutcome` (`:213`) land
on. Verified today: `grep -rn "bond_utilities" ../bond-api/` returns nothing —
no code anywhere round-trips an actual `bond-api` object through these
functions. Layer 0 cannot write that test (it depends on nothing in the suite).

- **Done looks like:** a test in `bond-api` constructs a real `MissionOutcome`
  + `Provenance`, persists it through `record_provenance_outcome`, reloads it,
  and asserts `verify_provenance` returns `True` and the field names round-trip.
- **Demonstrate:** `cd ../bond-api && uv run pytest tests/ -k provenance -q`
  passes, and this entry is deleted from here.

#### V5 — The clock and reporting examples in `README.md` / `AGENTS.md` are unbound

`tests/test_documented_examples.py` executes and pins every cipher and codename
example, but stops there. Unbound documented outputs:

- `README.md:127` — `win.status(...)  # 'ACTIVE'`
- `README.md:131` — `windows_overlap(...)  # 48h`
- `README.md:132` — `parse_duration("1d 2h30m")  # 1 day 2:30`
- `README.md:116` — `nato_codename("QB7")  # 'QUEBEC-BRAVO-7'` (the same value
  is pinned for `docs/quickstart.md` at `tests/test_documented_examples.py:70`,
  but not for `README.md`)
- `AGENTS.md:110` — `window_open(...)  # True`

All five were hand-run this session and are correct today; nothing here is
wrong, only unguarded. Note that `# 48h` and `# 1 day 2:30` are prose
paraphrases of `2 days, 0:00:00` and `1 day, 2:30:00`, so a verbatim-substring
assertion needs either a reworded comment or a value-shaped match.

- **Done looks like:** a `TestClockExamples` class in
  `tests/test_documented_examples.py` computing each value and requiring its
  quoted form in the file that prints it, in the same two-directional style as
  the existing classes.
- **Demonstrate:** change `# 'ACTIVE'` to `# 'PENDING'` in `README.md`;
  `uv run pytest tests/test_documented_examples.py -q` must fail.

### Documentation

#### D1 — "Re-derive, don't edit the assertion" is not machine-enforced

*From unresolved audit finding 4.* The documented outputs `'QB-B6050C24'`,
Caesar shift `8`, key `'MTSMQ'`, and the 202-letter sample are pinned in
`tests/test_documented_examples.py`, so a deliberate change to `derive_seed`
(`src/bond_utilities/randomness.py`) or the chi-squared table
(`src/bond_utilities/ciphers.py:676`, `:739`) turns the module red *by design*.
The correct response is to re-derive the documented value, not to edit the
assertion — but that instruction lives only in the module docstring
(`tests/test_documented_examples.py:1-11`), not in any failure message a
maintainer actually reads when a test breaks.

- **Done looks like:** each assertion in that module carries a failure message
  naming the regeneration command
  (`uv run python scripts/z_generate_manuscript_variables.py` and/or the
  one-liner that recomputes the value), so the instruction is delivered at
  failure time. `tests/test_documented_examples.py:68` is the existing example
  of the right shape.
- **Demonstrate:** break one documented value and read the pytest output — the
  remediation command must appear in it.

#### D2 — The API does not steer callers away from codenames as identifiers

`generate_codenames` / `alliterative_codename`
(`src/bond_utilities/codenames.py:119`, `:232`) draw from small hand-curated
12x12 word pools. `manuscript/07_scope_and_related_work.md:44-45` says they are
not a secure randomness source, and `README.md:64` describes the pools — but a
caller reading only the docstring of `generate_codenames` gets no warning, and
the collision-safe alternatives (`numeric_codename` at `:191`, `codename_token`
in `ciphers.py`) are not named there.

- **Done looks like:** the `generate_codenames` and `alliterative_codename`
  docstrings state the capacity limit and point at `numeric_codename` /
  `codename_token` for identifier use.
- **Demonstrate:** `uv run python -c "from bond_utilities import generate_codenames; help(generate_codenames)"`
  shows the steering; `uv run pytest tests/ -q` still green.
- **Note:** this edits docstrings in `src/`, out of scope for a docs-only pass.

### Extension

Genuine future work — nothing here is wrong today.

#### E1 — Wire a manuscript render pipeline

`scripts/z_generate_manuscript_variables.py` produces
`output/data/manuscript_variables.json` plus both figures
(`output/figures/mission_schedule.png`, `letter_frequency.png`), and
`tests/test_manuscript_variables.py:207` cross-references every `{{TOKEN}}` in
prose against the generated map. Nothing substitutes those tokens into a
rendered document. The old blocker ("the suite has not chosen a renderer") no
longer holds: `../bond-manuscript/` carries `_template_resources/`,
`export.toml`, and `docs/rendering_pipeline.md` describing the template PDF
pipeline. `bond-utilities` has no `export.toml` and no `.template-export.json`.

- **Done looks like:** `output/pdf/bond_utilities_combined.pdf` (or the
  suite-standard path) exists, is regenerable from a clean `output/`, and
  contains zero unsubstituted `{{` sequences.
- **Demonstrate:** the render command completes, then a new test asserting the
  extracted text of the rendered document contains no `{{` residue passes —
  `uv run pytest tests/ -k render -q`.

#### E2 — Measure the sample floor for `caesar_break` and `vigenere_break`

Both are chi-squared fits (`src/bond_utilities/ciphers.py:676`, `:739`) and both
return a confident wrong answer on short text. The specific failures — a
16-letter and a 21-letter English sample recovering the wrong Caesar shift, and
the 21-letter Vigenère case recovering key `'MTSMQ'` — are asserted in
`tests/test_documented_examples.py:127-147` and stated in
`manuscript/07_scope_and_related_work.md:30-38`, so nothing overclaims. What is
missing is a *measured* minimum-length curve to cite.

- **Done looks like:** an experiment script sweeping sample length against
  recovery rate over a fixed corpus and seed set, its output persisted under
  `output/data/`, and a generated token (e.g. `{{CAESAR_SAMPLE_FLOOR}}`)
  carrying the number into `07_scope_and_related_work.md` instead of the
  current qualitative caveat.
- **Demonstrate:** `uv run python scripts/<new_script>.py` reproduces the same
  numbers twice, and `uv run pytest tests/test_manuscript_variables.py -q`
  passes with the new token cross-referenced.

#### E3 — Decide on `generate_codenames(..., allow_repeats=True)`

The default `adjective_noun` scheme samples without replacement
(`src/bond_utilities/codenames.py:97`) and raises
`count must be in [1, {len(pairs)}]` above word-list capacity. That is the
correct default. A documented opt-in for callers who want more names than the
grid holds does not exist.

- **Done looks like:** either the keyword ships with a test covering the
  above-capacity path and a docstring stating the collision consequence, **or**
  this entry is deleted with a one-line note that no consumer asked for it.
- **Demonstrate:** `uv run pytest tests/test_codenames.py -q` covers
  `generate_codenames(500, seed=1, allow_repeats=True)` returning 500 names.
- **Trigger:** only worth building if a film package actually requests it.

---

## Known limitations (not bugs)

Accepted scope. These are recorded so they are not re-litigated.

- **The manuscript's honesty claim is scoped, not universal.** The abstract and
  conclusion state that every number is generated *except* algorithm-defining
  constants in `02_methodology.md` and `07_scope_and_related_work.md` — `mod 26`,
  the `5x5` Playfair square, IC `~0.066` / `~0.038`. Those are mathematics, not
  measurements of this package, and they are written as literals on purpose. The
  audit forced this softening; the exception is named in both sections rather
  than hidden. The residual enforcement gap is tracked as **V1** — the *scope
  statement itself* is settled.
- **`99_references.md` is outside the numeric guard.** Bibliographic volume,
  page, and year numbers collide with package metrics by construction. The
  exclusion is pinned by `tests/test_manuscript_variables.py:368` so it cannot
  silently grow. Improving the guard is **V2**; excluding the bibliography from
  a naive numeric scan is correct and stays.
- **Documented outputs are coupled to implementation details.** Pinning
  `'QB-B6050C24'`, shift `8`, and key `'MTSMQ'` means a deliberate change to
  `derive_seed` or the chi-squared table breaks `test_documented_examples.py`.
  That is intended: a doc example that can drift silently is worse than one that
  fails loudly. **D1** only asks for a better failure message.
- **No `mission.py`, no `MissionProvider`, no `GADGETS`.** The protocol belongs
  to `bond-api` (Layer 1). Implementing it here would invert the dependency
  direction. See [`docs/architecture.md`](docs/architecture.md).
- **No cryptographic strength.** The cipher suite is educational and
  deterministic by design. Do not "harden" it; do not use it for secrecy. It
  provides no authentication, integrity, or non-repudiation.
- **The `alliterative` scheme repeats within a batch.** It seeds each index
  independently and the bundled word lists admit only a small number of
  alliterative pairs. Specified behaviour, stated in
  `manuscript/07_scope_and_related_work.md:39-43` and asserted at
  `tests/test_codenames.py:263`. Only `adjective_noun` guarantees distinctness.
- **The word lists are small and hand-curated.** Fine for mission naming, wrong
  for anything needing entropy. **D2** asks only that the API say so; enlarging
  the lists is not planned.
- **No new dependencies.** `src/` stays on stdlib + numpy + matplotlib + pyyaml
  so every consumer's import stays cheap and mock-free. `pytest` is required
  only for `bond_utilities.testing`.
- **No renamed or reshaped public API.** The film fleet and Layers 1-4 import
  from `bond_utilities`. Add; do not rename.
- **No measured coverage percentage or test count is quoted outside this
  file's header.** `README.md:180-184`, `AGENTS.md:171-174` and
  `.agents/skills/bond-utilities/SKILL.md:25` deliberately quote only the
  enforced `fail_under` floor. The header above dates its measurement precisely
  because a snapshot goes stale.

---

## Verification

The gates for this package, with expected outcomes.

```bash
# Primary gate — must be green before any commit.
uv run pytest tests/ --cov=src --cov-fail-under=90
#   expected: all tests pass; "Required test coverage of 90% reached."
#   measured 2026-08-05: 384 passed, TOTAL 100.00% (816 stmts / 270 branches, 0 missed)

uv run ruff check src/ scripts/          # expected: "All checks passed!"
uv run ruff format --check src/ scripts/ # expected: "N files already formatted"
uv run mypy src/ scripts/                # expected: "Success: no issues found"

# No mocks, ever (zero-tolerance layer contract).
rg -n "unittest\.mock|MagicMock|@patch|create_autospec" tests/ || echo clean
#   expected: "clean"

# Regenerate the token map + both figures; output/ is disposable and gitignored.
uv run python scripts/z_generate_manuscript_variables.py
#   expected: writes output/data/manuscript_variables.json,
#             output/figures/mission_schedule.png, output/figures/letter_frequency.png

git status --short                       # expected: empty (output/ is gitignored)
```

Falsifiable guards worth knowing about when a change goes red — each was
verified to fail when the thing it guards is broken:

| Guard | Where |
| --- | --- |
| Every `{{TOKEN}}` in prose exists in the generated map | `tests/test_manuscript_variables.py:208` |
| Bare-numeral guard over quantitative sections, with a positive control | `tests/test_manuscript_variables.py:307-338` |
| Hand-copied-metric guard over every section but the bibliography | `tests/test_manuscript_variables.py:341-386` |
| Prose gate numbers equal the enforced `fail_under` / Python floor | `tests/test_manuscript_variables.py:388-409` |
| Registry drift: ciphers, cryptanalysis helpers, codename schemes, seeded helpers | `tests/test_ciphers.py:121`, `tests/test_codenames.py:196`, `tests/test_randomness.py:196` |
| Byte-determinism for both figures, with a negative control | `tests/test_figures.py:48`, `:62`, `:79` |
| Every documented worked example executed and required verbatim | `tests/test_documented_examples.py` |
| Provenance mutation rejection | `tests/test_mission_io.py` |

Note: `uv` may fail with `Failed to initialize cache at ~/.cache/uv` under a
restrictive sandbox. That is an environment problem, not a package failure —
re-run outside the sandbox.
