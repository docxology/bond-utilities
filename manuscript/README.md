# Manuscript directory

BOND suite — bond-utilities. See [`AGENTS.md`](AGENTS.md) for the full
technical reference. Quick pointers:

- Edit parameters in `config.yaml` (paper + mission sections).
- Regenerate tokens and the schedule figure:
  `uv run python scripts/z_generate_manuscript_variables.py`
- Verify no token drift: `uv run pytest tests/test_manuscript_variables.py -q`
