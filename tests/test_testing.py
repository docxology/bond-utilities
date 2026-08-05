"""Tests for src/bond_utilities/testing.py — shared fixtures + helpers.

These use the project-wide fixtures re-exported from conftest, verifying
they work in a real pytest session without mocks.
"""

from __future__ import annotations

import random
from pathlib import Path

from bond_utilities.testing import DEFAULT_TEST_SEED, seeded_codenames, temp_dir


class TestTempDir:
    def test_creates_directory_and_cleans_up(self) -> None:
        with temp_dir() as directory:
            assert isinstance(directory, Path)
            assert directory.is_dir()
            (directory / "f.json").write_text("{}")
            assert (directory / "f.json").exists()
        assert not directory.exists()


class TestSeededCodenames:
    def test_deterministic(self) -> None:
        assert seeded_codenames(4) == seeded_codenames(4)

    def test_distinct_from_other_seed(self) -> None:
        assert seeded_codenames(4, seed=1) != seeded_codenames(4, seed=2)

    def test_default_seed_constant(self) -> None:
        assert isinstance(DEFAULT_TEST_SEED, int)


class TestFixtures:
    def test_seeded_rng_reproducible(self, seeded_rng: random.Random) -> None:
        assert seeded_rng.randrange(1000) == random.Random(DEFAULT_TEST_SEED).randrange(1000)

    def test_mission_record_is_valid_dict(self, mission_record: dict) -> None:
        assert mission_record["mission_id"] == "M-001"
        assert set(["mission_id", "codename", "seed", "version", "started_at", "parameters"]) <= set(
            mission_record.keys()
        )


class TestSharedSurfaceShape:
    """What `testing.py` actually exports: two fixtures and two plain helpers.

    The docs used to call all four "shared pytest fixtures". Only `seeded_rng`
    and `mission_record` carry ``@pytest.fixture``; `temp_dir` is a context
    manager and `seeded_codenames` is an ordinary function, both imported
    directly rather than requested by name in a test signature. This test pins
    that distinction so the docs cannot drift back.
    """

    @staticmethod
    def _is_fixture(obj: object) -> bool:
        """True when ``obj`` was produced by ``@pytest.fixture``.

        pytest 9 returns a ``FixtureFunctionDefinition``; older versions tag
        the plain function. Both markers are accepted.
        """
        return hasattr(obj, "_fixture_function_marker") or hasattr(obj, "_pytestfixturefunction")

    def test_exactly_two_names_are_pytest_fixtures(self) -> None:
        import bond_utilities.testing as module

        fixtures = {name for name in module.__all__ if self._is_fixture(getattr(module, name))}
        assert fixtures == {"seeded_rng", "mission_record"}

    def test_helpers_are_not_fixtures(self) -> None:
        import bond_utilities.testing as module

        for name in ("temp_dir", "seeded_codenames"):
            assert not self._is_fixture(getattr(module, name)), (
                f"{name} became a pytest fixture — update README/architecture/testing_philosophy"
            )

    def test_helpers_are_callable_without_a_fixture_request(self) -> None:
        with temp_dir() as directory:
            assert directory.is_dir()
        assert seeded_codenames(2) == seeded_codenames(2)

    def test_module_imports_no_mock_framework_and_no_heavy_deps(self) -> None:
        """Scan the import statements themselves, not the prose docstring."""
        import ast
        import inspect

        import bond_utilities.testing as module

        tree = ast.parse(inspect.getsource(module))
        imported: set[str] = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module)
        roots = {name.split(".")[0] for name in imported}
        for banned in ("unittest", "mock", "numpy", "matplotlib"):
            assert banned not in roots, f"testing.py must not import {banned} (found {sorted(imported)})"
