# Manuscript (`manuscript/`)

BOND suite — bond-utilities (codename Q-BRANCH) manuscript source tree.

## File inventory

| File | Role |
| --- | --- |
| `config.yaml` | Paper metadata + mission parameters; source of every `{{TOKEN}}` |
| `config.yaml.example` | Richer copy-and-customize reference copy |
| `00_abstract.md` … `07_scope_and_related_work.md` | Prose sections using `{{TOKEN}}`s and `[@fig:schedule]` |
| `99_references.md` / `references.bib` | Bibliography (`@citation_key`, `[@key]`) |
| `SYNTAX.md` | Token + figure + citation syntax reference |
| `preamble.md` | LaTeX injections shared by PDF output |
| `layer_contract.yaml` | Dependency-layer contract enforced by gates |

## Token protocol

All dynamic values use `{{TOKEN}}` syntax. The authoritative map is produced
by `src/bond_utilities/manuscript_variables.py::generate_variables()` and
persisted by `scripts/z_generate_manuscript_variables.py` to
`output/data/manuscript_variables.json`. Never hand-author metrics in prose.
Three tests in `tests/test_manuscript_variables.py` enforce it:

- `TestManuscriptCrossReference` — fails if prose uses a token the generator
  does not produce.
- `TestNoHandAuthoredNumbers` — fails on a bare numeral surviving in
  `00_abstract.md`, `03_results.md`, `04_conclusion.md`, or
  `06_reproducibility.md`, after stripping code, tokens, link targets, Pandoc
  attribute braces, and a short allow-list of non-metric identifiers. It ships
  with a positive control so the guard cannot go vacuous.
- `TestGateNumbersAgreeWithEnforcement` — fails if the prose coverage gate or
  Python floor diverges from `pyproject.toml`.

To state a new quantity: add it to `generate_variables()` first, then reference
the token.

## Figure protocol

Reference figures via `[@fig:schedule]` and `[@fig:freq]` (Pandoc-crossref);
never use `\ref{}` or a hardcoded number. The PNGs are generated from the
mission schedule and codename sample by
`scripts/z_generate_manuscript_variables.py`.
