# Results

## Round-trip fidelity

Every cipher in `src/bond_utilities/ciphers.py` passes a round-trip identity
on real streams: Caesar and Atbash (letters, case preserved), Vigenère and
Beaufort (non-letters pass through), rail-fence and columnar (exact
transposition, no padding), Playfair (against its prepared form), XOR and
one-time-pad (bytes). None of the tests use mocks — they exercise the actual
algorithms.

## Cryptanalysis demos

Both breakers are statistical, and their accuracy is a function of sample
length rather than a guarantee. On the letter-rich English samples used in
`tests/test_documented_examples.py`, `caesar_break` recovers the exact shift and
plaintext, and `vigenere_break` recovers a keyword of known length and
decrypts. On short samples both return a wrong answer with no confidence
signal: a sixteen-letter English plaintext enciphered at a known shift comes
back under a different shift, and the twenty-one-letter case fails likewise for
both breakers. Those failures are asserted as tests, not merely noted, so the
qualification cannot quietly stop being true. `kasiski_key_lengths` returns the
true key length among its candidates for repeated plaintext, and
`index_of_coincidence` cleanly separates repetitive (more-structured) text from
uniform random text. The figure
`[@fig:freq]` shows the A-Z counts of the mission codename sample.

![Letter frequency of the codename sample.](../output/figures/letter_frequency.png){#fig:freq width=70%}

## Edge-case robustness

The cipher alphabet is ASCII `A-Z`/`a-z` by definition ([@unicode_standard]).
Non-ASCII alphabetic characters -- `é`, `ñ`, and letters from other
scripts, which Python's `str.isalpha()` classifies as letters -- are treated as
*nothing to the cipher*: the enciphering functions pass them through byte-for-
byte, and the frequency, index-of-coincidence, and chi-squared helpers ignore
them entirely. That contract is asserted as a regression test
(`tests/test_ciphers.py::TestNonAsciiRobustness`), which pins three properties
that previously failed: the A-Z counting helpers accept mixed-alphabet text
without crashing, a non-ASCII letter never corrupts a cipher round-trip, and
`caesar_break`/`english_chi_squared` treat a non-ASCII-only input as letterless
rather than misinterpreting it. The same hardening closes two validation gaps
in the primitives' edge behaviour: a non-string timestamp raises `ValueError`
rather than leaking an internal `AttributeError`
(`tests/test_clock.py::TestParseTimestampValidation`), and an empty header list
to `format_table` means *no header* rather than tripping the ragged-row guard
(`tests/test_reporting.py::TestFormatTableHeadersEdge`).

## Determinism

All **{{CIPHER_COUNT}}** ciphers ({{CIPHER_NAMES_CSV}}) and the codename
generator are deterministic under a fixed seed. The default adjective–noun
sample of {{CONFIG_NUM_CODENAMES}} names drawn with seed
{{CONFIG_DEFAULT_SEED}}:

> {{RESULT_CODENAME_SAMPLE}}

An alliterative sample under the same seed:

> {{RESULT_SCHEME_SAMPLE}}

That alliterative sample repeats: it holds {{RESULT_SCHEME_DISTINCT}} distinct
names across {{CONFIG_NUM_CODENAMES}} slots. That is the scheme working as
specified, not a bug — `alliterative` seeds each index independently rather
than sampling without replacement, and the bundled word lists share only
{{ALLITERATIVE_INITIALS}} initials between adjectives and nouns, admitting
{{ALLITERATIVE_CAPACITY}} distinct pairs in total. Collisions are therefore
likely in any batch of that size, and a test asserts that this sample contains
one. Callers needing distinct names must use the default scheme.

The scheme registry holds {{CODENAME_SCHEME_COUNT}} entries
({{CODENAME_SCHEMES}}); each is bound to a real dispatch branch by a
registry-drift test. The default scheme draws without replacement from a
{{WORDLIST_SIZE}} adjective/noun grid, so its capacity is
{{WORDLIST_CAPACITY}} unique pairs — `generate_codenames` raises above that
count rather than repeating a name.

## Seeded draw helpers

Reproducible sampling outside the codename engine goes through the
{{SEEDED_HELPER_COUNT}} helpers in `src/bond_utilities/randomness.py`
({{SEEDED_HELPERS_CSV}}). Each takes the seed as its first argument and
constructs a fresh `random.Random`, so draws never depend on call order or on
the global interpreter RNG. `ciphers.generate_otp_key` delegates to
`seeded_bytes`, which is why pad material and any other byte draw are
byte-identical for the same seed. The registry itself is test-bound: a
discovery test in `tests/test_randomness.py` fails if a helper is added,
renamed, or dropped without updating `SEEDED_HELPERS`.

## Provenance round-trip

`record_provenance_outcome` writes a record whose `provenance` block holds the
canonical SHA-256 of the sorted-compact JSON parameters, the schema version,
and the derived seed. `verify_provenance` recomputes all three from the
persisted record and returns `False` on any mismatch — the mutation tests in
`tests/test_mission_io.py` tamper with the parameters, the seed, and the schema
version in turn and confirm each is rejected, so the check is not satisfiable
by construction. `append_outcome` merges new results into `outcomes` and leaves
the provenance block byte-identical, which is what lets a later mission stage
extend a record without invalidating its audit trail.

## Mission schedule

The primary mission window spans {{RESULT_WINDOW_HOURS}} hours, from
{{CONFIG_SCHEDULE_START}} to {{CONFIG_SCHEDULE_END}} (UTC), rendered in
[@fig:schedule]. The secondary window overlaps the primary by
{{RESULT_OVERLAP_HOURS}} hours — computed by `windows_overlap`, not
hand-authored. Window math is exact under the half-open `[start, end)`
semantics; elapsed and remaining durations clamp at zero.

![Mission schedule window with the reference "now" marker.](../output/figures/mission_schedule.png){#fig:schedule width=80%}
