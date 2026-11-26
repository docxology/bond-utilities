# Scope and related work

## Scope

This package implements *utility* cryptography and scheduling primitives —
obfuscation, reproducible sampling, frequency analysis, and window math — for
the internal BOND suite. It is explicitly **not** a security product: the
ciphers are educational and deterministic, and must never be used for real
secrecy.

## Related work

The cipher primitives follow the classical constructions catalogued by Kahn
[@kahn_codebreakers] and presented as textbook algorithms by Stinson and
Paterson [@stinson_paterson_2018], and are formalised in Shannon's
information-theoretic treatment of secrecy systems [@shannon_1949] — which is
also the reference that makes the one-time pad's key-length requirement
non-negotiable rather than a stylistic choice. The cryptanalysis helpers build
on Friedman's index of coincidence [@friedman_1922] and Kasiski's examination
for repeated key segments [@kasiski_1863]. Deterministic seeded generation uses
the Mersenne Twister [@matsumoto_1998] as exposed by Python's `random` module;
that generator is chosen for reproducibility and equidistribution, explicitly
not for cryptographic unpredictability. Mission window and elapsed-time
semantics follow ISO-8601 date/time representations [@iso8601].

## Limitations

- The ciphers do not provide authentication, integrity, or non-repudiation.
- Determinism trades secrecy for reproducibility by design.
- `caesar_break` and `vigenere_break` are chi-squared fits to English letter
  frequencies, so both recover reliably only on letter-rich ciphertext. Neither
  reports confidence: on a short sample the best-fitting shift is often the
  wrong one and is returned as if it were correct. Measured cases —
  a sixteen-letter and a twenty-one-letter English plaintext, both enciphered
  at a known Caesar shift and both recovered under a different shift, and the
  twenty-one-letter Vigenère case recovering the wrong key — are asserted in
  `tests/test_documented_examples.py`. Treat a recovered key from a short text
  as a guess.
- The `alliterative` codename scheme can repeat a name within one batch: it
  seeds each index independently, and the bundled word lists admit only
  {{ALLITERATIVE_CAPACITY}} distinct pairs across {{ALLITERATIVE_INITIALS}}
  shared initials. Only the default `adjective_noun` scheme guarantees
  distinctness (and raises rather than repeating once capacity is exhausted).
- The word lists are deliberately small and curated; they are not a secure
  randomness source.
