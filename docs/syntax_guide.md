# Syntax guide — bond-utilities

## `{{VARIABLE}}` tokens

Dynamic values in the manuscript use `{{TOKEN}}` syntax; never hardcode a
number in prose. The authoritative map is the return value of
`src/bond_utilities/manuscript_variables.py::generate_variables()`. Two tests
in `tests/test_manuscript_variables.py` enforce it:

- `TestManuscriptCrossReference` fails if prose uses a token the generator does
  not produce.
- `TestNoHandAuthoredNumbers` fails if a bare numeral survives in the abstract,
  results, conclusion, or reproducibility sections — with a positive control so
  the guard cannot go vacuous.

Gate numbers (`{{COVERAGE_GATE_PERCENT}}`, `{{MAX_TEST_FAILURES}}`) come from
the `testing:` section of `manuscript/config.yaml`, and
`TestGateNumbersAgreeWithEnforcement` asserts the coverage figure equals the
`fail_under` value `pyproject.toml` actually enforces.

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
`[@kahn_codebreakers]`, `[@stinson_paterson_2018]`, `[@friedman_1922]`,
`[@kasiski_1863]`, `[@matsumoto_1998]`, `[@iso8601]`. Every entry is a real,
checkable publication — never add one you have not verified exists.

## Markdown links

Prefer relative links that resolve within the tree, e.g.
[`../src/bond_utilities/ciphers.py`](../src/bond_utilities/ciphers.py).
