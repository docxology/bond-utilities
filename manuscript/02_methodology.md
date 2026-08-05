# Methodology

## Ciphers (`src/bond_utilities/ciphers.py`)

The cipher suite falls into four families. **Monoalphabetic:** Caesar
(`c = (p + shift) mod 26`), Atbash (reverse alphabet, self-inverse), and
Beaufort (`c = (k - p) mod 26`, self-inverse). **Polyalphabetic/keyed:**
Vigenère (keyword advances over letters only), Playfair (digraph
substitution on a 5x5 keyed square with I/J merged, doubles split with `X`).
**Transposition:** rail-fence (zig-zag rows) and columnar (columns read in a
digit-key order, round-trips exactly with no padding). **Byte:** one-time-pad
(XOR with a key at least as long as the data) and XOR (cyclically repeated
key). Every cipher satisfies `decrypt(encrypt(x)) == x` on supported inputs;
the digraph cipher round-trips against its prepared (X-split, padded) form.

## Cryptanalysis helpers

- `letter_frequency` / `frequency_normalized` — A-Z counts and relative
  frequencies.
- `index_of_coincidence` — Friedman's IC: ~0.066 for natural English vs
  ~0.038 for uniform random, used to distinguish substitution from
  polyalphabetic text.
- `english_chi_squared` — chi-squared fit of letter frequencies against
  standard English.
- `caesar_shift_scores` / `caesar_break` — score all 26 shifts by chi-squared
  and return the best `(shift, plaintext)`. The score is a statistic over the
  input's letter counts, so the returned shift is the best-fitting one, not a
  certified one: on short samples the best fit is often the wrong shift, and
  the function returns it with no confidence signal (see Limitations in
  `07_scope_and_related_work.md`).
- `kasiski_key_lengths` — locate repeated n-grams, factor their distances,
  and vote on candidate Vigenère key lengths.
- `vigenere_break` — break each key column independently and re-interleave.

## Deterministic seeding (`randomness.py`)

`derive_seed` folds integer seeds to 32 bits and hashes string seeds
(`int(sha256(seed)[0:8], 16)`). `make_rng(seed)` returns a fresh
`random.Random`; the `seeded(seed)` decorator seeds the global module and
restores the prior state on exit, so a decorated function is deterministic in
isolation without perturbing its caller. The module also exports
{{SEEDED_HELPER_COUNT}} typed draw helpers ({{SEEDED_HELPERS_CSV}}), each
reproducible from a single seed and enumerated in the `SEEDED_HELPERS`
registry that the manuscript reads.

## Codename schemes (`codenames.py`)

- `adjective_noun` (default) — unique pairs sampled without replacement from
  a {{WORDLIST_SIZE}} grid.
- `alliterative` — ADJ-NOUN pairs sharing a starting letter. Unlike
  `adjective_noun`, this scheme seeds each index independently instead of
  sampling without replacement, so a batch may repeat a name; and only
  {{ALLITERATIVE_INITIALS}} initials are carried by both word lists, giving
  {{ALLITERATIVE_CAPACITY}} distinct pairs in total. Repetition in a batch is
  therefore expected, not a defect — `tests/test_codenames.py` asserts both the
  capacity and the repetition.
- `nato` — NATO phonetic spelling of a base codename (e.g. `{{NATO_EXAMPLE}}`).
- `numeric` — `PREFIX-XXXXXXXX` hex codes derived from a mission id.
- `token` — truncated SHA-256 hex tokens.

Each scheme is deterministic under a fixed seed; `generate_codenames(..., scheme=…)`
selects the scheme while preserving the phase-1 default exactly.

## Mission clock (`clock.py`)

Times are timezone-aware (naive treated as UTC). A window is the half-open
interval `[start, end)`. Phase 4 adds `windows_overlap` (shared duration,
clamped at zero), `merge_windows` (minimal sorted cover), `parse_duration`
(`"1d 2h30m"`-style), `schedule_status` (`PENDING`/`ACTIVE`/`COMPLETE`), and
the `MissionSchedule` dataclass tying duration, open/elapsed/remaining,
countdown, and status together.

## Provenance (`mission_io.py`)

`record_provenance_outcome` persists a record whose `provenance` block holds
the canonical input hash (SHA-256 of sorted-compact JSON), the schema version,
and the derived seed. Phase 4 adds `verify_provenance` (recompute and compare
the hash/seed/version), `load_records` (sorted directory batch load),
`record_summary` (flat deterministic digest), and `append_outcome` (merge into
`outcomes` without disturbing provenance).

## Reporting and figures (`reporting.py`, `figures/plots.py`)

`reporting.py` renders the plain-text surface the thin CLIs print: `banner`,
`format_table` (left-aligned, width-fitted, ragged rows rejected), `format_kv`
(right-aligned keys), and `schedule_table`, which projects a sequence of
`MissionSchedule` objects into name/start/end/status rows evaluated at a caller-
supplied instant. The `print_*` wrappers take an explicit `stream`; the default
resolves `sys.stdout` at call time rather than at import time, so redirected
output is captured correctly and tests can assert on real rendered text without
a mock framework.

`figures/plots.py` renders the two manuscript figures. `plot_mission_schedule`
draws the window as a horizontal bar in unix-time coordinates with a dashed
"now" marker; `plot_frequency_analysis` draws the A-Z counts returned by
`ciphers.letter_frequency`. Both are deterministic under the Agg backend — the
same inputs produce byte-identical PNGs, which `tests/test_figures.py` asserts
for each figure by comparing two renders. For the schedule figure the input
includes `now`: the marker moves with the wall clock when `now` is left to its
default, so determinism is claimed and tested for a fixed `now`, and a negative
control asserts that two different `now` values do produce different bytes.

## Shared fixtures (`testing.py`)

`testing.py` carries the shared test surface every bond package reuses through
its own `conftest.py`. Two of the four names are actual pytest fixtures —
`seeded_rng` (a `random.Random` at the suite's default seed) and
`mission_record` (a schema-valid record); the other two are plain callables
imported directly, `temp_dir` (a context manager) and `seeded_codenames` (a
function). A test asserts that split, so the distinction cannot be lost.
It imports only `pytest`, the standard library, and this package's pure
primitives, so importing it can never pull numpy, matplotlib, or — the point of
the constraint — a mock framework into a consumer's test session.

## Scoring and statistics

Frequency scoring uses the standard English letter table in `ENGLISH_FREQUENCIES`
(normalized; sum 1.0). All cryptanalysis outputs are deterministic given the
input text.
