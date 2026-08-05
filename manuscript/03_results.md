# Results

## Round-trip fidelity

Every cipher in `src/bond_utilities/ciphers.py` passes a round-trip identity
on real streams: Caesar and Atbash (letters, case preserved), Vigenère and
Beaufort (non-letters pass through), rail-fence and columnar (exact
transposition, no padding), Playfair (against its prepared form), XOR and
one-time-pad (bytes). None of the tests use mocks — they exercise the actual
algorithms.

## Cryptanalysis demos

For an English plaintext, `caesar_break` recovers the exact shift and
plaintext; `vigenere_break` recovers a keyword of known length and decrypts.
`kasiski_key_lengths` returns the true key length among its candidates for
repeated plaintext, and `index_of_coincidence` cleanly separates repetitive
(more-structured) text from uniform random text. The figure
`[@fig:freq]` shows the A-Z counts of the mission codename sample.

![Letter frequency of the codename sample.](../output/figures/letter_frequency.png){#fig:freq width=70%}

## Determinism

All **{{CIPHER_COUNT}}** ciphers ({{CIPHER_NAMES_CSV}}) and the codename
generator are deterministic under a fixed seed. The default adjective–noun
sample of {{CONFIG_NUM_CODENAMES}} names drawn with seed
{{CONFIG_DEFAULT_SEED}}:

> {{RESULT_CODENAME_SAMPLE}}

An alliterative sample under the same seed:

> {{RESULT_SCHEME_SAMPLE}}

The scheme registry is {{CODENAME_SCHEMES}}; the alliterative scheme yields
ADJ-NOUN pairs sharing an initial. Word-list capacity for the default scheme
is {{WORDLIST_SIZE}} unique pairs.

## Mission schedule

The primary mission window spans {{RESULT_WINDOW_HOURS}} hours, from
{{CONFIG_SCHEDULE_START}} to {{CONFIG_SCHEDULE_END}} (UTC), rendered in
[@fig:schedule]. The secondary window overlaps the primary by
{{RESULT_OVERLAP_HOURS}} hours — computed by `windows_overlap`, not
hand-authored. Window math is exact under the half-open `[start, end)`
semantics; elapsed and remaining durations clamp at zero.

![Mission schedule window with the reference "now" marker.](../output/figures/mission_schedule.png){#fig:schedule width=80%}
