# Abstract

The BOND suite's shared foundation, codenamed **{{MISSION_CODENAME}}**, ships
dependency-light Python modules that every other bond package imports: a
classic-cipher suite with cryptanalysis helpers, a deterministic codename
engine with several schemes, mission clock/schedule math, seeded randomness,
mission-record persistence with provenance, and plain-text reporting.

The cipher layer exposes **{{CIPHER_COUNT}}** classic primitives
({{CIPHER_NAMES_CSV}}) — each round-trip verified with real data — and
**{{CRYPTANALYSIS_HELPERS}}** analysis helpers (letter frequency, index of
coincidence, chi-squared scoring, Caesar/Vigenère breaking, Kasiski
examination). Codenames are drawn under **{{CODENAME_SCHEME_COUNT}}**
deterministic schemes ({{CODENAME_SCHEMES}}); the NATO scheme spells a short
identifier as `{{NATO_EXAMPLE}}`. Reproducible sampling runs through
**{{SEEDED_HELPER_COUNT}}** seeded draw helpers ({{SEEDED_HELPERS_CSV}}), each
derived from one seed. Mission schedules are half-open UTC windows with
overlap, merge, and duration models, and persisted mission records carry a
reproducible input hash, the schema version, and the producing seed, so any
outcome can be re-derived from its stored inputs.

Every token in this manuscript is computed from `manuscript/config.yaml` via
`src/bond_utilities/manuscript_variables.py` — never hand-authored. The test
suite enforces that discipline directly: a cross-reference test fails on any
prose token the generator does not produce, and a numeral guard fails on any
hand-authored number in the quantitative sections.
