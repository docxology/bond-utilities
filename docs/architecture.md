# Architecture — bond-utilities (Q-BRANCH)

`bond-utilities` is **Layer 0** of the BOND suite: the only package in the
fleet that depends on no other bond package. Everything above it — `bond-api`
(Layer 1), `bond-coordinator` (Layer 2), `bond-orchestrator` (Layer 3),
`bond-cli` / `bond-ops` (Layer 4), and every film package — imports downward
into this tree. That position is the design constraint: this package must stay
small, pure, deterministic, and cheap to import.

## Where the MissionProvider protocol lives (and why not here)

The suite's mission protocol — `MissionBrief`, `ReconRequest`/`ReconReport`,
`MissionPlan`, `MissionOutcome`, `Debrief`, and the `MissionProvider` Protocol
with its `brief`/`recon`/`plan`/`execute`/`debrief` methods — is defined in
**`bond-api`**, one layer up. A film package implements that protocol in its
own `mission.py` and registers gadgets in its `GADGETS` registry.

**`bond-utilities` deliberately has no `mission.py` and no `GADGETS`
registry.** It is not a mission provider and never will be; it is the
primitive layer providers are built *out of*. Adding a `MissionProvider`
implementation here would invert the dependency direction (Layer 0 importing
Layer 1) and break every package above it.

What this package contributes to the mission lifecycle is the persistence and
reproducibility surface that mission outcomes land on:

| Mission need | Provided by |
| --- | --- |
| Reproducible seeds behind any provider's sampling | `randomness.derive_seed`, `make_rng`, the `SEEDED_HELPERS` draw set |
| Mission codenames for briefs and rosters | `codenames.generate_codenames`, `codename_for`, `codenames_by_scheme` |
| Window math for brief/plan scheduling | `clock.MissionSchedule`, `windows_overlap`, `merge_windows`, `schedule_status` |
| Persisting an outcome with an auditable input hash | `mission_io.record_provenance_outcome` |
| Re-verifying a persisted outcome | `mission_io.verify_provenance` |
| Extending an outcome without disturbing provenance | `mission_io.append_outcome` |
| Batch-reading a mission ledger | `mission_io.load_records`, `record_summary` |
| Obfuscating a codename in transit | `ciphers.obfuscate_codename` / `restore_codename` / `codename_token` |
| Rendering a situation-room table in a thin CLI | `reporting.format_table`, `format_kv`, `schedule_table` |
| Shared, mock-free pytest fixtures for a consumer's suite | `testing.py` |

## Dependency shape

```
manuscript/config.yaml                     (mission parameters — the only inputs)
        │
        ▼
src/bond_utilities/                        scripts/ (thin CLIs)        tests/
  ── pure primitives ──                     generate_codenames.py       real data
  randomness.py  ◄────┐                     cryptanalyze.py             zero mocks
  ciphers.py  ────────┤  (ciphers seed OTP  record_mission.py
  codenames.py ───────┘   keys via          z_generate_manuscript_variables.py
  clock.py                randomness)
  mission_io.py   (hashes + validates; derives seeds via randomness)
  reporting.py    (renders clock.MissionSchedule rows)
  testing.py      (fixtures over codenames + randomness)
  ── orchestration inside src/ ──
  manuscript_variables.py  (config → {{TOKEN}} map; calls clock/codenames/ciphers/randomness)
  figures/plots.py         (matplotlib PNGs; calls ciphers.letter_frequency + clock.to_utc)
```

Rules that hold in both directions:

- `scripts/ → src/` only. No script contains business logic.
- `src/ → stdlib + numpy + matplotlib + pyyaml`. No `infrastructure.*`, no
  sibling bond package, no mock framework.
- `tests/ → src/`. Nothing imports upward, and nothing in `src/` imports a test.
- Only `mission_io.py` and `figures/plots.py` touch the filesystem; only
  `reporting.py` writes to a stream. Everything else is pure.

## Module by module

### `randomness.py` — the seed floor

The root of every non-deterministic operation in the suite. `derive_seed`
normalises any `int | str` into a stable value in `[0, 2**32)` — integers are
masked to 32 bits, strings hashed with SHA-256 and truncated — so a seed
persisted in a mission record replays exactly. `make_rng` returns a *fresh*
`random.Random` per call, which is what keeps draws independent of call order.
The `seeded(seed)` decorator seeds the global `random` module and restores the
prior state in a `finally`, so a decorated function is deterministic in
isolation without perturbing its caller.

`SEEDED_HELPERS` enumerates the typed draw helpers — `seeded_bytes`,
`seeded_int`, `seeded_float`, `seeded_choice`, `seeded_choices`,
`seeded_shuffle`, `seeded_sample`. The registry is bound to reality by a
discovery test that fails if a helper is added, renamed, or removed without
updating the tuple, so the manuscript's `{{SEEDED_HELPER_COUNT}}` cannot drift.

### `ciphers.py` — classical crypto and cryptanalysis

Nine round-trip-verified ciphers in four families: **monoalphabetic** (Caesar,
Atbash, Beaufort), **polyalphabetic/keyed** (Vigenère, Playfair on a 5x5 keyed
I/J-merged square), **transposition** (rail-fence, columnar with a digit key),
and **byte-level** (XOR with a cyclic key, one-time pad requiring a key at
least as long as the data). Every cipher satisfies `decrypt(encrypt(x)) == x`;
Playfair round-trips against its *prepared* form (uppercase, J→I, doubles split
with `X`, odd tail padded), because that normalisation is lossy by construction
and the docstring says so rather than pretending otherwise.

Eight cryptanalysis helpers sit alongside: `letter_frequency` and
`frequency_normalized` (A-Z counts and relative frequencies),
`index_of_coincidence` (Friedman's IC), `english_chi_squared` (fit against
`ENGLISH_FREQUENCIES`), `caesar_shift_scores` / `caesar_break` (scored brute
force over all 26 shifts), `kasiski_key_lengths` (repeated-n-gram distance
factoring and voting), and `vigenere_break` (per-column Caesar breaks
re-interleaved into reading order).

Both breakers are statistics, not oracles: `caesar_break` returns the
best-fitting shift of all 26 and `vigenere_break` breaks each column the same
way, so on short samples both return a wrong answer with no confidence signal.
The measured failure cases are asserted in `tests/test_documented_examples.py`.

`CIPHER_NAMES` and `CRYPTANALYSIS_HELPERS` are bound to the module by
`tests/test_ciphers.py::TestRegistryBinding`: every registered cipher must
resolve to an exported callable and pass a round trip, every `*_encrypt`
function must be registered, and the module's whole public function surface must
partition into the two registries plus a small explicit key/codename utility
set. `CODENAME_SCHEMES` is bound the same way to the `codenames_by_scheme`
dispatch branches.

`generate_otp_key` delegates to `randomness.seeded_bytes` rather than owning
its own byte source — one seed, one path, byte-identical results.
`codename_token` derives a stable truncated SHA-256 token from a name and seed.

**Not a security product.** These are educational and deterministic; the module
docstring and `manuscript/07_scope_and_related_work.md` both say so explicitly.

### `codenames.py` — deterministic naming

Curated 12x12 adjective/noun pools plus five schemes registered in
`CODENAME_SCHEMES`: `adjective_noun` (unique pairs sampled without replacement
from the full product, so capacity is bounded and exceeding it raises rather
than repeating a name), `alliterative` (adjective and noun sharing an initial),
`nato` (ICAO spelling via `NATO_ALPHABET`), `numeric` (`QB-XXXXXXXX` hex folds
of a mission id), and `token` (truncated SHA-256). Only `adjective_noun`
guarantees distinct names. `alliterative` seeds each index independently and the
bundled lists share just five initials across nine distinct pairs, so a batch of
that scheme can — and for the manuscript's own configured sample does — repeat a
name; `tests/test_codenames.py::TestAlliterativeCapacity` asserts both the
capacity and the repetition. `generate_codenames`
dispatches on scheme while preserving its original adjective–noun default
signature exactly — the film fleet calls it and must not break.
`codename_for(name, seed)` folds a name into a derived seed for a stable
per-mission codename.

### `clock.py` — mission time

Timezone-aware throughout; naive datetimes are documented as UTC rather than
silently coerced by local time. A window is the half-open interval
`[start, end)` — the convention that makes `windows_overlap` and
`merge_windows` composable without double-counting endpoints.
`parse_timestamp` accepts a trailing `Z`; `parse_duration` reads compact
`"1d 2h30m"` strings; `elapsed_time` refuses a negative span rather than
returning one; `window_elapsed` / `window_remaining` clamp at zero; `t_minus`
renders `T-` / `T+` countdowns; `schedule_status` classifies a window as
`PENDING` / `ACTIVE` / `COMPLETE`. `MissionSchedule` is a frozen dataclass that
validates its own ordering in `__post_init__` and exposes `duration`, `open`,
`elapsed`, `remaining`, `countdown`, and `status`.

Wall-clock defaults (`now=None`) exist only where the semantics are inherently
"right now"; every test passes an explicit `now`, so nothing in the suite is
time-of-day dependent.

### `mission_io.py` — provenance persistence

The mission-record envelope. `MISSION_SCHEMA` names the required keys and their
types (`mission_id`, `codename`, `seed`, `version`, `started_at`,
`parameters`); `OPTIONAL_KEYS` (`outcomes`, `provenance`) must be mappings when
present. `validate_record` reports *every* failing key in one message rather
than raising on the first. `hash_payload` canonicalises with sorted keys and
compact separators, so the hash is stable across formatting and key order.

`record_provenance_outcome` is the write path the rest of the suite calls: it
bundles the input hash, schema version, and derived seed into `provenance`,
stores measured results under `outcomes`, and persists as JSON or YAML
(inferred from the suffix). `verify_provenance` recomputes all three and
returns `False` on any mismatch — the mutation tests tamper with parameters,
seed, and schema version in turn, so the check is not green by construction.
`append_outcome` merges new results while leaving `provenance` byte-identical
(and tolerates a record that has no `outcomes` key yet, since the key is
optional); `load_records` batch-loads a directory in sorted order and wraps a
malformed file with its filename; `record_summary` flattens a record for
reporting.

### `reporting.py` — plain-text output

`banner`, `format_table` (width-fitted, ragged rows rejected), `format_kv`
(right-aligned keys), and `schedule_table` (a `MissionSchedule` sequence
projected to name/start/end/status at a supplied instant). The `print_*`
wrappers take a `stream`; the default is `None` and resolves `sys.stdout` **at
call time**, so redirected output is captured correctly — binding `sys.stdout`
in the signature would freeze the interpreter's original stdout at import.

### `manuscript_variables.py` — config to `{{TOKEN}}`s

Reads `manuscript/config.yaml` and computes the whole token map by calling the
primitives (`parse_schedule`, `windows_overlap`, `generate_codenames`,
`codenames_by_scheme`, `nato_codename`) plus the registry constants
(`CIPHER_NAMES`, `CRYPTANALYSIS_HELPERS`, `CODENAME_SCHEMES`, `SEEDED_HELPERS`,
`ADJECTIVES`, `NOUNS`). Quality-gate tokens (`COVERAGE_GATE_PERCENT`,
`MAX_TEST_FAILURES`) come from the config's `testing:` section, and a test
asserts the coverage figure equals the `fail_under` value `pyproject.toml`
actually enforces. No manuscript number is authored by hand anywhere here.

### `figures/plots.py` — deterministic figures

`plot_mission_schedule` draws the window as a horizontal bar in unix-time
coordinates with a dashed "now" marker; `plot_frequency_analysis` draws the A-Z
counts from `ciphers.letter_frequency`. Both are byte-deterministic under the
Agg backend (pinned in `tests/conftest.py`) for a fixed input, and
`tests/test_figures.py` asserts that for *each* figure by comparing two renders.
For `plot_mission_schedule` the input includes `now`: left at its library
default the marker tracks the wall clock, so the determinism claim is scoped to
an explicit `now`, and a negative control asserts two different `now` values do
change the bytes. The manuscript pipeline never leaves it at the default —
`scripts/z_generate_manuscript_variables.py` passes
`manuscript_variables.manuscript_instant(config)`, so the persisted PNG is a
function of committed inputs only.

### `testing.py` — shared fixtures

Two pytest fixtures — `seeded_rng` and `mission_record` — plus two plain
callables and a constant: `temp_dir` (a `@contextmanager`, used in a `with`
block), `seeded_codenames` (an ordinary function), and `DEFAULT_TEST_SEED`.
Only the first two can be requested by name in a test signature; the others are
imported directly. `tests/test_testing.py::TestSharedSurfaceShape` asserts that
split. Import-light on purpose: only `pytest`, the standard
library, and this package's pure primitives, so a consumer's `conftest.py` can
re-export these fixtures without dragging numpy, matplotlib, or a mock
framework into its test session.

## Scripts (thin orchestrators)

| Script | Delegates to | Does itself |
| --- | --- | --- |
| `generate_codenames.py` | `codenames.generate_codenames` | argparse, `reporting` output |
| `cryptanalyze.py` | the `ciphers` analysis helpers | argparse, `reporting` output |
| `record_mission.py` | `mission_io.record_provenance_outcome` / `verify_provenance` | argparse, JSON payload parse, `reporting` output |
| `z_generate_manuscript_variables.py` | `manuscript_variables.generate_variables`, `figures.plots` | argparse, writes the JSON token map, anchors figure paths to the project root |

Each script inserts `src/` on `sys.path` so it runs without an install;
`pyproject.toml` sets `mypy_path = "src"` so `mypy src/ scripts/` sees the same
layout and type-checks the orchestrators too.

## Forbidden patterns

- Importing `infrastructure.*` or any sibling bond package inside `src/`.
- Implementing business logic inside `scripts/`.
- Any mock framework in `tests/`.
- Hardcoding a manuscript metric in prose instead of a `{{TOKEN}}` — two guards
  in `tests/test_manuscript_variables.py` fail the build: the numeral guard over
  the quantitative sections, and the hand-copied-metric guard over every
  section, which is what the introduction's hardcoded `9 ciphers / 8 helpers /
  5 schemes` slipped past before.
- Quoting a measured coverage percentage or test count in any document. Only
  the enforced `fail_under` floor is quotable.
- Documenting a worked example whose output the code does not produce —
  `tests/test_documented_examples.py` executes each one and requires the quoted
  text to match.
- Adding a `MissionProvider` implementation here (see the first section).

## Adding a primitive

1. Add a pure, type-hinted, docstringed function to the relevant
   `src/bond_utilities/*.py` module.
2. Add it to that module's `__all__`, then re-export from
   `src/bond_utilities/__init__.py` if it is public API. (`mission_io` and
   `randomness` both carry tests that fail when `__all__` falls behind.)
3. If it belongs to a named registry (`CIPHER_NAMES`, `CODENAME_SCHEMES`,
   `SEEDED_HELPERS`, `CRYPTANALYSIS_HELPERS`), add it there too — the
   corresponding manuscript token counts that registry.
4. Add real-data tests in `tests/test_<module>.py`, including the error
   branches.
5. Run the full gate: `uv run pytest tests/ --cov=src --cov-fail-under=90`,
   `uv run ruff check src/ scripts/`, `uv run ruff format --check src/ scripts/`,
   `uv run mypy src/ scripts/`.
