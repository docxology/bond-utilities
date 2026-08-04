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
`output/data/manuscript_variables.json`. Never hand-author metrics in prose;
the live cross-reference test
`tests/test_manuscript_variables.py::TestManuscriptCrossReference` fails if a
prose token is not generated.

## Figure protocol

Reference the schedule figure via `[@fig:schedule]` (Pandoc-crossref); never
use `\ref{}` or a hardcoded number. The PNG is generated from the mission
schedule by `scripts/z_generate_manuscript_variables.py`.
