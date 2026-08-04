# Methodology

## Ciphers (`src/bond_utilities/ciphers.py`)

All four ciphers are defined over byte or character streams and satisfy a
round-trip identity. For letters, the Caesar shift maps character `c` to

```
enc_shift(c) = A + ((c - A + shift) mod 26)
```

where `A` is the case base (`a`/`A`); non-letters pass through unchanged.
Decryption is encryption with the negated shift. The Vigenère cipher advances
the keyword only over letters, so non-letter characters do not consume key
material. The XOR cipher is symmetric byte-wise XOR with a cyclically repeated
key; the one-time pad is the same operation with a key required to be at least
as long as the data. Round-trip tests confirm `decrypt(encrypt(x)) == x` for
every supported input.

## Deterministic seeding (`randomness.py`)

Every generator derives from a single seed value through `derive_seed`:

- integer seeds are folded to 32 bits: `seed & 0xFFFFFFFF`;
- string seeds are hashed: `int(sha256(seed.encode())[0:8], 16)`.

`make_rng(seed)` returns a fresh `random.Random` built from the derived seed,
and the `seeded(seed)` decorator runs a function with the global `random`
module seeded, restoring the prior state afterwards — so decorator-wrapped
functions are deterministic without perturbing callers.

## Codename generation (`codenames.py`)

Codenames are sampled without replacement from the full adjective × noun
product ({{WORDLIST_SIZE}} pairs), using `rng.sample`. A fixed seed therefore
yields a fixed, duplicate-free list of the configured size
({{CONFIG_NUM_CODENAMES}} names by default).

## Mission clock (`clock.py`)

Mission times are timezone-aware; naive datetimes are treated as UTC. A
schedule window is the half-open interval `[start, end)`, so the window is
open when `start <= now < end` and closed exactly at `end`. Elapsed and
remaining durations clamp at zero, and `t_minus` renders a `T-` countdown
before the target and a `T+` count-up after it.

## Provenance (`mission_io.py`)

A mission record must satisfy the schema in `MISSION_SCHEMA` (mission id,
codename, seed, version, started_at, parameters; optional outcomes and
provenance mappings). `record_provenance_outcome` writes a record whose
`provenance` block contains the canonical input hash
(`sha256` of sorted-compact JSON), the schema version, and the derived seed.
