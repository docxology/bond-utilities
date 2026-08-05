# Methodology

## Ciphers (`src/bond_utilities/ciphers.py`)

The cipher suite falls into three families. **Monoalphabetic:** Caesar
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
  and return the best `(shift, plaintext)`.
- `kasiski_key_lengths` — locate repeated n-grams, factor their distances,
  and vote on candidate Vigenère key lengths.
- `vigenere_break` — break each key column independently and re-interleave.

## Deterministic seeding (`randomness.py`)

`derive_seed` folds integer seeds to 32 bits and hashes string seeds
(`int(sha256(seed)[0:8], 16)`). `make_rng(seed)` returns a fresh
`random.Random`; the `seeded(seed)` decorator seeds the global module and
restores the prior state. Phase 4 adds typed draw helpers — `seeded_bytes`,
`seeded_int`, `seeded_float`, `seeded_choice`, `seeded_choices`,
`seeded_shuffle`, `seeded_sample` — all reproducible from a single seed.

## Codename schemes (`codenames.py`)

- `adjective_noun` (default) — unique pairs sampled without replacement from
  a {{WORDLIST_SIZE}} grid.
- `alliterative` — ADJ-NOUN pairs sharing a starting letter.
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

## Scoring and statistics

Frequency scoring uses the standard English letter table in `ENGLISH_FREQUENCIES`
(normalized; sum 1.0). All cryptanalysis outputs are deterministic given the
input text.
