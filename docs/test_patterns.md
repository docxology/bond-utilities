# tests/ — patterns

Patterns every test in this package follows.

## Determinism

All random draws are seeded. Functions with a wall-clock default (`now=None`)
are always called with an explicit `now=` in tests so behavior is
reproducible.

## Capturing output

`src/bond_utilities/reporting.py` writes to an explicit stream. Capture it
with `io.StringIO`, never a mock:

```python
import io
from bond_utilities.reporting import print_table

stream = io.StringIO()
print_table([["1", "SILENT-JAGUAR"]], stream=stream)
assert "SILENT-JAGUAR" in stream.getvalue()
```

## File I/O

Use `tmp_path` (pytest) for files, or `temp_dir()` from
`src/bond_utilities/testing.py` in non-fixture code.

## Shared test surface

`conftest.py` re-exports four names from `src/bond_utilities/testing.py`, but
only two of them are pytest fixtures: `seeded_rng` and `mission_record`, which
can be requested by name in a test signature. `temp_dir` is a context manager
and `seeded_codenames` is a plain function — call them directly.
`test_testing.py::TestSharedSurfaceShape` asserts that split.

## Subprocess smoke

Thin CLIs are exercised via `subprocess.run([sys.executable, ...])` with
exit-code and artifact assertions (see `test_scripts_smoke.py`).
