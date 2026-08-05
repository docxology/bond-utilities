# Manuscript directory

BOND suite — bond-utilities. See [`AGENTS.md`](AGENTS.md) for the full
technical reference. Quick pointers:

- Edit parameters in `config.yaml` (paper, mission, and testing sections) —
  never a number in prose.
- Regenerate the token map and both figures (schedule + letter frequency):
  `uv run python scripts/z_generate_manuscript_variables.py`
- Verify no token drift, no hand-authored numerals, and no gate/prose
  divergence: `uv run pytest tests/test_manuscript_variables.py -q`

Sections: `00_abstract`, `01_introduction`, `02_methodology`, `03_results`,
`04_conclusion`, `05_experimental_setup`, `06_reproducibility`,
`07_scope_and_related_work`, `99_references`.
