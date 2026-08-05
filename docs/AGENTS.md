# docs/ — agent-facing documentation hub

Operational rulebook for agents working inside `bond-utilities` (codename
**Q-BRANCH**), Layer 0 of the BOND suite.

## File inventory

| File | Purpose |
| --- | --- |
| `README.md` | Entry point and reading order |
| `AGENTS.md` | This index — conventions and verification commands |
| `agent_instructions.md` | Hard behavioural constraints (read-first) |
| `architecture.md` | Layer position, MissionProvider boundary, per-module contracts |
| `testing_philosophy.md` | Zero-mock doctrine, coverage mechanics, falsifiable guards |
| `style_guide.md` | Code style rules |
| `syntax_guide.md` | `{{VARIABLE}}` tokens and the figure registry |
| `quickstart.md` | Five-minute first run |
| `output_conventions.md` | `output/` layout and regeneration |

## Key conventions

- **Read-first**: read `agent_instructions.md` before modifying any file.
- **Zero-mock**: no `unittest.mock`, `MagicMock`, `@patch`, or
  `create_autospec` anywhere in `tests/` — real data and real computation only.
  `pytest.MonkeyPatch` for environment isolation (`chdir`, constant swaps) is
  permitted and inventoried in `testing_philosophy.md`.
- **Dependency floor**: `src/bond_utilities/` imports only the standard library
  plus numpy/matplotlib/pyyaml. No `infrastructure.*`, no sibling bond package.
- **Determinism**: every random draw flows through a seeded generator; every
  wall-clock default takes an explicit `now=` in tests.
- **No `mission.py` here**: the `MissionProvider` protocol belongs to
  `bond-api` (Layer 1). This package is what providers are built from — see
  `architecture.md`.
- **Generated numbers only**: manuscript metrics are `{{TOKEN}}`s produced by
  `src/bond_utilities/manuscript_variables.py`. A numeral guard test fails the
  build on a hand-authored number in the quantitative sections.
- **Public API is load-bearing**: the film fleet and the upper layers import
  from `bond_utilities`. Extend the surface; do not reshape or rename it.

## Verification commands

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
uv run ruff check src/ scripts/
uv run ruff format --check src/ scripts/
uv run mypy src/ scripts/
rg -n "unittest\.mock|MagicMock|@patch|create_autospec" tests/ || echo clean
git status --short
```

The coverage floor is whatever `pyproject.toml → [tool.coverage.report]
fail_under` says; a test asserts the manuscript quotes that same value. Do not
paste a measured percentage into prose — run the command and read it.
