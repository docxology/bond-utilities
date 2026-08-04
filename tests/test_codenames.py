"""Tests for src/bond_utilities/codenames.py — deterministic samples, no mocks."""

from __future__ import annotations

import random

import pytest

from bond_utilities.codenames import (
    ADJECTIVES,
    NOUNS,
    codename_for,
    generate_codenames,
    random_codename,
)
from bond_utilities.randomness import make_rng


def test_word_lists_nonempty_and_uppercase() -> None:
    assert len(ADJECTIVES) == 12
    assert len(NOUNS) == 12
    assert all(word.isupper() and word.isalpha() for word in ADJECTIVES)
    assert all(word.isupper() and word.isalpha() for word in NOUNS)


class TestGenerateCodenames:
    def test_deterministic_given_seed(self) -> None:
        assert generate_codenames(5, seed=20260804) == generate_codenames(5, seed=20260804)

    def test_different_seed_differs(self) -> None:
        assert generate_codenames(3, seed=1) != generate_codenames(3, seed=2)

    def test_unique_no_duplicates(self) -> None:
        names = generate_codenames(10, seed=7)
        assert len(set(names)) == len(names) == 10

    def test_shape_and_separator(self) -> None:
        names = generate_codenames(4, seed=5, separator="::")
        assert all(name.count("::") == 1 for name in names)
        assert all(len(name.split("::")) == 2 for name in names)

    def test_all_from_word_lists(self) -> None:
        for name in generate_codenames(8, seed=3):
            adj, noun = name.split("-")
            assert adj in ADJECTIVES
            assert noun in NOUNS

    def test_single_codename(self) -> None:
        assert len(generate_codenames(1, seed=1)) == 1

    def test_count_too_low_raises(self) -> None:
        with pytest.raises(ValueError, match=r"\[1, 144\]"):
            generate_codenames(0, seed=1)

    def test_count_too_high_raises(self) -> None:
        with pytest.raises(ValueError, match=r"\[1, 144\]"):
            generate_codenames(145, seed=1)

    def test_empty_separator_raises(self) -> None:
        with pytest.raises(ValueError, match="separator"):
            generate_codenames(2, seed=1, separator="")


class TestRandomCodenameAndFor:
    def test_random_codename_uses_rng(self) -> None:
        rng = random.Random(1)
        first = random_codename(rng)
        rng2 = random.Random(1)
        assert first == random_codename(rng2)

    def test_random_codename_empty_separator_raises(self) -> None:
        with pytest.raises(ValueError, match="separator"):
            random_codename(make_rng(1), separator="")

    def test_codename_for_is_stable(self) -> None:
        assert codename_for("HQ-07") == codename_for("HQ-07")

    def test_codename_for_differs_by_name(self) -> None:
        assert codename_for("HQ-07") != codename_for("HQ-08")

    def test_codename_for_respects_seed(self) -> None:
        assert codename_for("HQ-07", seed="ops") == codename_for("HQ-07", seed="ops")
        assert codename_for("HQ-07", seed="ops") != codename_for("HQ-07", seed="labs")

    def test_codename_for_uses_word_lists(self) -> None:
        adj, noun = codename_for("HQ-07").split("-")
        assert adj in ADJECTIVES
        assert noun in NOUNS
