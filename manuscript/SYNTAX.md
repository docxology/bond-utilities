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
| `RESULT_CODENAME_SAMPLE` | `generate_codenames()` |
| `CIPHER_COUNT` | `ciphers.CIPHER_NAMES` length |
| `WORDLIST_SIZE` | `codenames.ADJECTIVES × NOUNS` |
| `GENERATION_TIMESTAMP` | run timestamp (UTC) |

## Figure references

One figure is currently defined, referenced via Pandoc-crossref:

| Label | File | Generator |
| --- | --- | --- |
| `{#fig:schedule}` | `output/figures/mission_schedule.png` | `src/bond_utilities/figures/plots.py::plot_mission_schedule` |

Reference in prose as `[@fig:schedule]` (parenthetical) or `@fig:schedule`
(narrative); never use a raw `\ref{}` or hardcoded number.

## Citations

Cite with Pandoc citation keys defined in `references.bib`, e.g. `[@shannon_1949]`.
