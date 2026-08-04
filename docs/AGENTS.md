# docs/ — Agent-Facing Documentation Hub

Technical guide for `projects/working/bond/bond-utilities/docs/` — the
operational rulebook for agents working inside the bond-utilities package.

## File inventory

| File | Purpose |
| --- | --- |
| `README.md` | Quick navigation and entry points |
| `AGENTS.md` | This index |
| `agent_instructions.md` | Behavioral constraints for AI agents (read-first) |
| `architecture.md` | Layer boundaries and dependency contract |
| `testing_philosophy.md` | Zero-mock policy and coverage mechanics |
| `style_guide.md` | Style rules: zero-mock, thin orchestrator, type hints |
| `syntax_guide.md` | `{{VARIABLE}}` token + figure registry |
| `quickstart.md` | 5-minute first-run walkthrough |
| `output_conventions.md` | `output/` layout and regeneration |

## Key conventions

- **Read-first**: read `agent_instructions.md` before modifying any file.
- **Zero-mock**: no `unittest.mock`, `MagicMock`, `@patch`, or
  `create_autospec` anywhere in `tests/` — real data + computation only.
- **Dependency floor**: `src/bond_utilities/` imports only stdlib +
  numpy/matplotlib/pyyaml; scripts are thin orchestrators.
- **Determinism**: every random draw flows through a seeded generator.

## Verification commands

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/
uv run mypy src/ scripts/
rg -n "unittest\.mock|MagicMock|@patch|create_autospec" tests/ || echo clean
```
