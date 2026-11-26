# Source notes

These notes connect the cited works to the corresponding implementation.
The bibliography provides the full publication details.

## Classical cryptography

**Classical cipher history.** [@kahn_codebreakers]. Historical grounding for the classical cipher schemes in `ciphers.py`.

**Secrecy systems.** [@shannon_1949]. The secrecy framework that separates
the classical schemes here from cryptographic security; the reason `ciphers.py`
is documented as pedagogical rather than protective.

**Substitution and transposition.** [@stinson_paterson_2018]. Standard modern treatment of
the substitution and transposition families in `ciphers.py`.

## Cryptanalysis

**Index of coincidence.** [@friedman_1922]. The statistic implemented by `ciphers.index_of_coincidence()` and
reported by `scripts/cryptanalyze.py`, where it is a human-facing diagnostic for
distinguishing monoalphabetic from polyalphabetic ciphertext. To be exact about
the code: `ciphers.vigenere_break()` does **not** consult the IC — it takes the
key length as a required argument and breaks each column with
`ciphers.caesar_break()` (chi-squared). Candidate key lengths come from
`ciphers.kasiski_key_lengths()`. IC-based key-length estimation is not
implemented in this package.

**Repeated n-gram distances.** [@kasiski_1863]. Repeated n-gram distance voting for
periodic-key length recovery, implemented as
`ciphers.kasiski_key_lengths()`.

## Pseudo-random generation

**Mersenne Twister.** [@matsumoto_1998]. The generator behind Python's `random` module and
therefore behind every seeded helper in `randomness.py`. Cited specifically to
document that these draws are reproducible but **not** cryptographically
secure.

## Time and provenance

**Timestamp representation.** [@iso8601]. The timestamp format parsed by `clock.parse_timestamp()` (accepting a trailing `Z`)
and written by `mission_io.record_provenance_outcome()` into each record's
`started_at` field via `datetime.isoformat()`. `mission_io.append_outcome()`
writes no timestamp of its own — it merges outcomes and leaves the existing
record's timestamps and provenance block untouched.

## Text encoding

**Unicode and ASCII.** [@unicode_standard]. The reference behind the phrase "alphabetic character"; it is why the cipher
helpers here scope their alphabet to ASCII `A-Z`/`a-z` and treat every other
alphabetic character (`é`, `ñ`, Cyrillic, CJK) as a non-letter. Cited in
`02_methodology.md` and `03_results.md` for the edge-case robustness contract,
and asserted by `tests/test_ciphers.py::TestNonAsciiRobustness`.

## Suite context

The BOND suite documentation and the frozen `bond-api` mission protocol are
internal to the BOND working trees and carry no external citation.
