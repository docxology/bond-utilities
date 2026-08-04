# Abstract

The BOND suite's shared foundation, codenamed **{{MISSION_CODENAME}}**, ships
seven dependency-light Python modules that every other bond package imports:
classic ciphers, a deterministic codename generator, mission clock math,
seeded randomness, mission-record persistence with provenance, and plain-text
reporting.

The library exposes **{{CIPHER_COUNT}}** classic cipher primitives (Caesar,
Vigenère, one-time-pad, XOR), each verified by byte-for-byte round-trip tests.
Codenames are sampled from a {{WORDLIST_SIZE}} adjective–noun grid through a
seeded generator, so a fixed seed ({{CONFIG_DEFAULT_SEED}}) yields a fixed
list. Mission schedules are expressed as half-open UTC windows, and tokens in
this manuscript are computed — never hand-authored — from
`manuscript/config.yaml` via `src/bond_utilities/manuscript_variables.py`.
