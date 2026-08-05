# Testing Philosophy — bond-utilities (Q-BRANCH)

## Zero-mock policy

A core tenet of the BOND suite: **all tests use real data and real
computation** — no `unittest.mock`, `MagicMock`, `@patch`, or `create_autospec`
anywhere in `tests/`. A mock passes when the real algorithm is wrong; real data
does not. Audit it with:

```bash
rg -n "unittest\.mock|MagicMock|@patch|create_autospec" tests/ || echo clean
```

This package is where the policy has teeth for the whole fleet, because
`src/bond_utilities/testing.py` is the fixture module every other bond package
imports in its `conftest.py`. That module depends only on `pytest`, the
standard library, and this package's pure primitives — so importing it can
never pull a mock framework (or numpy, or matplotlib) into a consumer's test
session. Keep it that way.

### What we use instead

| Instead of mocking | We do this |
| --- | --- |
| A fake filesystem | `tmp_path` and the real `temp_dir` context manager; records are really written and really re-read |
| A patched stdout | An `io.StringIO` passed as `stream=`, or `contextlib.redirect_stdout` for the default path |
| A stubbed RNG | A seeded `random.Random` from `make_rng(seed)` — deterministic without being fake |
| A stubbed clock | An explicit `now=` argument on every function that has a wall-clock default |
| A fake plotting backend | The real Agg backend writing a real PNG, asserted on its magic bytes and, for both figures, byte-for-byte determinism at fixed inputs |
| A subprocess double | A real `subprocess.run` of the actual script, asserting on exit code and rendered stdout |

`pytest.MonkeyPatch` appears in two places (`monkeypatch.chdir` for
default-path tests, and swapping the word-list constants to empty tuples to
reach an otherwise-unreachable guard). That is environment isolation, not
dependency replacement: no behaviour is faked, and no framework object stands
in for a real one.

## Coverage

Coverage is measured over `src/` only — test code is excluded from the metric,
so the number cannot be inflated by testing the tests. Both **line and branch**
coverage are collected (`branch = true` in `pyproject.toml`).

```bash
uv run pytest tests/ --cov=src --cov-fail-under=90
```

The enforced floor is the `fail_under` value in
`pyproject.toml → [tool.coverage.report]`. The manuscript quotes that same
number through `{{COVERAGE_GATE_PERCENT}}`, and
`tests/test_manuscript_variables.py::TestGateNumbersAgreeWithEnforcement`
asserts the two agree — prose cannot drift away from the enforced gate.

**Measured coverage is deliberately not quoted in these docs.** A committed
percentage is stale the moment the next module lands; run the command and read
the real number. What is stable, and therefore documented, is the gate.

## Tests that can actually fail

Coverage alone proves lines executed, not that anything was checked. These
tests exist specifically to be falsifiable:

| Guard | Lives in | Fails when |
| --- | --- | --- |
| Manuscript token cross-reference | `test_manuscript_variables.py::TestManuscriptCrossReference` | Prose uses a `{{TOKEN}}` the generator does not produce |
| Hand-authored numeral guard | `test_manuscript_variables.py::TestNoHandAuthoredNumbers` | A bare number appears in abstract/introduction/results/conclusion/reproducibility prose. Ships with a **positive control** asserting the scrubber still detects a planted number, so the guard cannot go vacuous |
| Hand-copied metric guard | `test_manuscript_variables.py::TestGeneratedMetricsAreNotHandCopied` | *Any* manuscript section (including the methodology and scope sections, which the numeral guard deliberately does not cover) writes a currently-generated metric value as a literal instead of its token. The metric list is checked against the live token map so a rename cannot make it vacuous |
| Cipher / helper registry binding | `test_ciphers.py::TestRegistryBinding` | A registered cipher has no real entrypoint or no round-trip, a new `*_encrypt` is not registered, or any public function of `ciphers` is in neither registry nor the explicit utility set |
| Codename scheme registry binding | `test_codenames.py::TestSchemeRegistryBinding` | `CODENAME_SCHEMES` and the `codenames_by_scheme` dispatch branches disagree in either direction |
| Alliterative capacity | `test_codenames.py::TestAlliterativeCapacity` | The word lists stop admitting the documented number of shared initials / distinct pairs, or the manuscript's own sample stops repeating |
| Documented examples | `test_documented_examples.py` | A worked example in the README, `AGENTS.md` or the quickstart quotes an output the code does not produce — in either direction, since each value is computed here and then required to appear verbatim in the file |
| Shared-fixture shape | `test_testing.py::TestSharedSurfaceShape` | `temp_dir` / `seeded_codenames` become fixtures (or the two real fixtures stop being fixtures) without the docs being updated |
| Gate/enforcement agreement | `test_manuscript_variables.py::TestGateNumbersAgreeWithEnforcement` | The prose coverage gate or Python floor diverges from `pyproject.toml` |
| `__all__` completeness | `test_mission_io.py::TestModuleSurface` | A public function or class is added without being exported |
| Registry drift | `test_randomness.py::TestSeededHelperRegistry` | A `seeded_*` helper is added, renamed, or removed without updating `SEEDED_HELPERS` |
| Provenance mutation | `test_mission_io.py::TestVerifyProvenance` | `verify_provenance` accepts tampered parameters, a wrong seed, or a wrong schema version |
| Figure determinism (both figures) | `test_figures.py::TestPlotFrequencyAnalysis::test_deterministic_bytes`, `::TestPlotMissionSchedule::test_deterministic_bytes` | Two renders of identical input differ byte-for-byte. The schedule figure is tested at an explicit `now`, with a negative control asserting a different `now` does change the bytes |
| Flag actually does something | `test_scripts_smoke.py` | `--no-figure` still touches the figure artifacts, or figures leak into the working directory |

## What each test file covers

| File | Coverage |
| --- | --- |
| `test_ciphers.py` | Round-trip, known-vector, and error branches for all nine ciphers, Playfair J/key handling, and the eight cryptanalysis helpers |
| `test_codenames.py` | Determinism, uniqueness, bounds, separators, `codename_for`, and all five schemes |
| `test_clock.py` | Elapsed/window/T-minus math, timezone normalisation, schedule parsing, overlap/merge, duration parsing, `MissionSchedule` |
| `test_randomness.py` | Seed derivation, reproducible streams, decorator state restore, every seeded draw helper, and the `SEEDED_HELPERS` registry binding |
| `test_mission_io.py` | Schema validation, JSON/YAML round-trips, provenance hashing and mutation rejection, `load_records`, `record_summary`, `append_outcome` (including a record with no `outcomes` key), `__all__` completeness |
| `test_reporting.py` | Table/KV/banner rendering, explicit-stream output, and the call-time stdout default under `redirect_stdout` |
| `test_testing.py` | The shared fixtures work in a real pytest session |
| `test_manuscript_variables.py` | Token map, config defaults and error branches, live `{{TOKEN}}` cross-reference, the numeral guard, and gate/enforcement agreement |
| `test_figures.py` | Real PNG output (schedule + frequency), deterministic bytes, default path, error branches |
| `test_scripts_smoke.py` | Subprocess smoke of every thin CLI, including flag behaviour and artifact anchoring |
| `test_documented_examples.py` | Every worked example printed in `README.md`, `AGENTS.md` and `docs/quickstart.md`, executed against the live functions and cross-checked against the quoted text; plus the short-text failure cases and the two corrected bibliography claims |

## Determinism

Every random draw is seeded. Every function with a wall-clock default takes an
explicit `now=` in tests. `MPLBACKEND=Agg` is pinned in `tests/conftest.py`
before any plotting import, so figures render identically headless. The shared test
surface hangs off `src/bond_utilities/testing.py`: two pytest fixtures
(`seeded_rng`, `mission_record`) and two plain helpers imported directly
(`temp_dir`, a context manager; `seeded_codenames`, a function).

## Reference

- Fixture inventory: [`tests/AGENTS.md`](../tests/AGENTS.md)
- Patterns: [`tests/PATTERNS.md`](../tests/PATTERNS.md)
- Architecture and module contracts: [`architecture.md`](architecture.md)
