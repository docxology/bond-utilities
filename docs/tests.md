# Verify bond-utilities

From the package root, install the locked development dependencies as shown
in the [quickstart](quickstart.md). Run the behavioral suite, Ruff, and mypy.

```bash
uv run --no-sync pytest tests/ --cov=src --cov-fail-under=90
uv run --no-sync --with ruff ruff check src/ scripts/
uv run --no-sync --with ruff ruff format --check src/ scripts/
uv run --no-sync --with mypy --with types-PyYAML mypy src/ scripts/
```

The project locks the runtime dependencies and test tools. Ruff, mypy, and
the YAML stubs are resolved for these commands. The
[testing philosophy](testing_philosophy.md) lists the source and manuscript
contracts that the tests exercise.
