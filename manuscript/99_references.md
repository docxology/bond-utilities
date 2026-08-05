# References

Bibliography of record: `manuscript/references.bib`. Every entry below is a
real, checkable source for a model or convention implemented in
`src/bond_utilities/`.

## Classical cryptography

**[kahn_codebreakers]** D. Kahn, *The Codebreakers: The Comprehensive History of
Secret Communication from Ancient Times to the Internet*, rev. ed., Scribner,
1996. — Historical grounding for the classical cipher schemes in `ciphers.py`.

**[shannon_1949]** C. E. Shannon, "Communication Theory of Secrecy Systems,"
*Bell System Technical Journal* 28(4):656–715, 1949.
doi:10.1002/j.1538-7305.1949.tb00928.x — The secrecy framework that separates
the classical schemes here from cryptographic security; the reason `ciphers.py`
is documented as pedagogical rather than protective.

**[stinson_paterson_2018]** D. R. Stinson and M. B. Paterson, *Cryptography:
Theory and Practice*, 4th ed., CRC Press, 2018. — Standard modern treatment of
the substitution and transposition families in `ciphers.py`.

## Cryptanalysis

**[friedman_1922]** W. F. Friedman, "The Index of Coincidence and Its
Applications in Cryptography," *Riverbank Laboratories Publication* No. 22,
1922. — The statistic implemented by `ciphers.index_of_coincidence()`, used by
`ciphers.vigenere_break()` to score candidate key lengths.

**[kasiski_1863]** F. Kasiski, *Die Geheimschriften und die Dechiffrir-Kunst*,
E. S. Mittler und Sohn, Berlin, 1863. — Repeated n-gram distance voting for
periodic-key length recovery, implemented as
`ciphers.kasiski_key_lengths()`.

## Pseudo-random generation

**[matsumoto_1998]** M. Matsumoto and T. Nishimura, "Mersenne Twister: A
623-Dimensionally Equidistributed Uniform Pseudo-Random Number Generator," *ACM
Transactions on Modeling and Computer Simulation* 8(1):3–30, 1998.
doi:10.1145/272991.272995 — The generator behind Python's `random` module and
therefore behind every seeded helper in `randomness.py`. Cited specifically to
document that these draws are reproducible but **not** cryptographically
secure.

## Time and provenance

**[iso8601]** International Organization for Standardization, *ISO 8601-1:2019 —
Date and Time — Representations for Information Interchange*, 2019. — The
timestamp format parsed by `clock.parse_timestamp()` (accepting a trailing
`Z`) and written by `mission_io.append_outcome()` into every mission-outcome
provenance record.

## Suite context

The BOND suite documentation and the frozen `bond-api` mission protocol are
internal to this local-only working tree and carry no external citation.
