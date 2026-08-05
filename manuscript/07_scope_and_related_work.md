# Scope and related work

## Scope

This package implements *utility* cryptography and scheduling primitives —
obfuscation, reproducible sampling, frequency analysis, and window math — for
the internal BOND suite. It is explicitly **not** a security product: the
ciphers are educational and deterministic, and must never be used for real
secrecy.

## Related work

The cipher primitives follow the classical constructions catalogued by Kahn
[@kahn_codebreakers] and formalised in Shannon's information-theoretic
treatment of secrecy systems [@shannon_1949]. The cryptanalysis helpers build
on Friedman's index of coincidence [@friedman_1922] and Kasiski's
examination for repeated key segments [@kasiski_1863]. Deterministic seeded
generation uses the Mersenne Twister [@matsumoto_1998] as exposed by Python's
`random` module. Mission window and elapsed-time semantics follow ISO-8601
date/time representations [@iso8601].

## Limitations

- The ciphers do not provide authentication, integrity, or non-repudiation.
- Determinism trades secrecy for reproducibility by design.
- `vigenere_break` recovers keys reliably on letter-rich ciphertext (per-column
  frequency statistics need enough samples); very short texts may mis-estimate
  a column shift.
- The word lists are deliberately small and curated; they are not a secure
  randomness source.
