# Syntax guide — bond-utilities

## `{{VARIABLE}}` tokens

Dynamic values in the manuscript use `{{TOKEN}}` syntax; never hardcode a
number in prose. The authoritative map is the return value of
`src/bond_utilities/manuscript_variables.py::generate_variables()`; the live
cross-reference test (`tests/test_manuscript_variables.py`) fails if any
prose token is missing.

Full token list, sources, and the figure registry:
[`../manuscript/SYNTAX.md`](../manuscript/SYNTAX.md).

## Figure registry

| Label | File | Generator |
| --- | --- | --- |
| `{#fig:schedule}` | `output/figures/mission_schedule.png` | `src/bond_utilities/figures/plots.py::plot_mission_schedule` |
| `{#fig:freq}` | `output/figures/letter_frequency.png` | `plots.plot_frequency_analysis` |

Reference figures with `[@fig:schedule]` / `[@fig:freq]` (Pandoc-crossref),
never raw `\ref{}`.

## Citations

Use Pandoc keys from `manuscript/references.bib`: `[@shannon_1949]`,
`[@kahn_codebreakers]`, `[@friedman_1922]`, `[@kasiski_1863]`,
`[@matsumoto_1998]`, `[@iso8601]`.

## Markdown links

Prefer relative links that resolve within the tree, e.g.
[`../src/bond_utilities/ciphers.py`](../src/bond_utilities/ciphers.py).
