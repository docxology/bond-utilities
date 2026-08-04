# Results

## Round-trip fidelity

Every cipher implemented in `src/bond_utilities/ciphers.py` passes a
round-trip identity test on real streams: Caesar (letters, case preserved),
Vigenère (non-letters pass through), XOR (cycle the key), one-time-pad (key
length ≥ data length), and codename obfuscation `restore(obfuscate(x)) == x`.
None of the tests use mocks — they exercise the actual algorithms.

## Determinism

All **{{CIPHER_COUNT}}** ciphers and the codename generator are
deterministic under a fixed seed. A default sample of
{{CONFIG_NUM_CODENAMES}} codenames drawn with seed {{CONFIG_DEFAULT_SEED}}:

> {{RESULT_CODENAME_SAMPLE}}

Regenerating with the same seed reproduces the list byte-for-byte; changing
the seed or the mission name changes the output. Word-list capacity is
{{WORDLIST_SIZE}} unique adjective–noun pairs.

## Mission schedule

The reference mission window spans {{RESULT_WINDOW_HOURS}} hours, from
{{CONFIG_SCHEDULE_START}} to {{CONFIG_SCHEDULE_END}} (UTC). The schedule is
rendered in [@fig:schedule].

![Mission schedule window with the reference "now" marker.](../output/figures/mission_schedule.png){#fig:schedule width=80%}

Schedule-window math is exact under the half-open `[start, end)` semantics:
the window is open during the interval and closed at `end`, and elapsed /
remaining durations clamp at zero.
