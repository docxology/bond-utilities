# Manuscript syntax — bond-utilities

## `{{VARIABLE}}` tokens

Numeric and factual values in the manuscript must use `{{TOKEN}}` syntax —
never hardcoded prose numbers. The authoritative source is the return value
of `src/bond_utilities/manuscript_variables.py::generate_variables()`; the
live cross-reference test
`tests/test_manuscript_variables.py::TestManuscriptCrossReference` gates
completeness.

Known tokens (generated from `manuscript/config.yaml`):

| Token | Source |
| --- | --- |
| `MISSION_CODENAME` | `mission.codename` |
| `PACKAGE_VERSION` | `paper.version` |
| `CONFIG_DEFAULT_SEED` | `mission.default_seed` |
| `CONFIG_NUM_CODENAMES` | `mission.num_codenames` |
| `CONFIG_SCHEDULE_START` | `mission.schedule.start` (parsed) |
| `CONFIG_SCHEDULE_END` | `mission.schedule.end` (parsed) |
| `RESULT_WINDOW_HOURS` | computed from schedule |
| `RESULT_OVERLAP_HOURS` | `windows_overlap(schedule, overlap_window)` |
| `RESULT_CODENAME_SAMPLE` | `generate_codenames(..., "adjective_noun")` |
| `RESULT_SCHEME_SAMPLE` | `codenames_by_scheme(..., "alliterative")` |
| `CIPHER_COUNT` | `ciphers.CIPHER_NAMES` length |
| `CIPHER_NAMES_CSV` | `", ".join(CIPHER_NAMES)` |
| `CODENAME_SCHEMES` | `", ".join(codenames.CODENAME_SCHEMES)` |
| `CODENAME_SCHEME_COUNT` | `codenames.CODENAME_SCHEMES` length |
| `CRYPTANALYSIS_HELPERS` | `ciphers.CRYPTANALYSIS_HELPERS` length |
| `SEEDED_HELPER_COUNT` | `randomness.SEEDED_HELPERS` length |
| `SEEDED_HELPERS_CSV` | `", ".join(randomness.SEEDED_HELPERS)` |
| `NATO_EXAMPLE` | `nato_codename("QB7")` |
| `WORDLIST_SIZE` | `len(ADJECTIVES) x len(NOUNS)` grid shape |
| `WORDLIST_CAPACITY` | `len(ADJECTIVES) * len(NOUNS)` unique pairs |
| `COVERAGE_GATE_PERCENT` | `testing.coverage_gate_percent` (asserted equal to `pyproject.toml` `fail_under`) |
| `MAX_TEST_FAILURES` | `testing.max_test_failures` |
| `CONFIG_MANUSCRIPT_DATE` | `paper.date` from the config, via `manuscript_instant()` — a committed value, never the wall clock |

## The numeral guard

`tests/test_manuscript_variables.py::TestNoHandAuthoredNumbers` scans
`00_abstract.md`, `03_results.md`, `04_conclusion.md`, and
`06_reproducibility.md` for digits that are **not** inside a `{{TOKEN}}`,
inline or fenced code, a link/image target, a Pandoc attribute brace, or the
short allow-list of non-metric identifiers (`SHA-256`, `ISO-8601`, `UTF-8`,
`A-Z`). Any survivor fails the suite. The guard ships with a positive control
asserting the scrubber still detects a planted number, so it cannot quietly go
vacuous.

If you need to state a new quantity: add it to `generate_variables()` first,
then reference the token. Never type the number.

## Figure references

Two figures are defined, referenced via Pandoc-crossref:

| Label | File | Generator |
| --- | --- | --- |
| `{#fig:schedule}` | `output/figures/mission_schedule.png` | `src/bond_utilities/figures/plots.py::plot_mission_schedule` |
| `{#fig:freq}` | `output/figures/letter_frequency.png` | `src/bond_utilities/figures/plots.py::plot_frequency_analysis` |

Reference in prose as `[@fig:schedule]` / `[@fig:freq]` (parenthetical) or
`@fig:label` (narrative); never use a raw `\ref{}` or hardcoded number.

## Citations

Cite with Pandoc citation keys defined in `references.bib`, e.g.
`[@shannon_1949]`, `[@friedman_1922]`, `[@kasiski_1863]`.
