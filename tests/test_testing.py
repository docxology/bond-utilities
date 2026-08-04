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
        assert set(
            ["mission_id", "codename", "seed", "version", "started_at", "parameters"]
        ) <= set(mission_record.keys())
