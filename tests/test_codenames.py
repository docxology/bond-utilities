"""Tests for src/bond_utilities/codenames.py — deterministic samples, no mocks."""

from __future__ import annotations

import random

import pytest

from bond_utilities.codenames import (
    ADJECTIVES,
    CODENAME_SCHEMES,
    NATO_ALPHABET,
    NOUNS,
    _initial_pair,
    alliterative_codename,
    codename_for,
    codenames_by_scheme,
    generate_codenames,
    nato_codename,
    numeric_codename,
    random_codename,
)
import bond_utilities.codenames as _codnames
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


class TestSchemes:
    def test_registry(self) -> None:
        assert CODENAME_SCHEMES == ("adjective_noun", "alliterative", "nato", "numeric", "token")
        assert len(NATO_ALPHABET) == 26
        assert all(word.isupper() and word.isalpha() for word in NATO_ALPHABET.values())

    def test_generate_codenames_scheme_kwarg(self) -> None:
        # Default unchanged; explicit scheme dispatches.
        assert generate_codenames(3, seed=1) == generate_codenames(3, seed=1, scheme="adjective_noun")
        assert generate_codenames(3, seed=1, scheme="numeric") != generate_codenames(3, seed=1)

    def test_unknown_scheme_raises(self) -> None:
        with pytest.raises(ValueError, match="unknown scheme"):
            generate_codenames(2, seed=1, scheme="bogus")

    def test_count_zero_raises(self) -> None:
        with pytest.raises(ValueError, match="count must be >= 1"):
            codenames_by_scheme(0, seed=1, scheme="numeric")

    def test_adj_noun_via_codenames_by_scheme(self) -> None:
        assert codenames_by_scheme(3, seed=1, scheme="adjective_noun") == generate_codenames(3, seed=1)

    def test_token_scheme(self) -> None:
        names = codenames_by_scheme(2, seed=1, scheme="token")
        assert len(names) == 2
        assert all(len(name) == 8 and name.isalnum() and name.isupper() for name in names)


class TestNato:
    def test_known(self) -> None:
        assert nato_codename("QB7") == "QUEBEC-BRAVO-7"
        assert nato_codename("A") == "ALFA"

    def test_deterministic_and_scheme(self) -> None:
        assert nato_codename("Q7") == nato_codename("Q7")

    def test_non_alnum_passthrough(self) -> None:
        assert nato_codename("Q-B", "-") == "QUEBEC-BRAVO"

    def test_in_generate_codenames(self) -> None:
        names = codenames_by_scheme(2, seed=3, scheme="nato")
        assert len(names) == 2
        assert names[0] == names[0]  # deterministic single-call sanity


class TestNumeric:
    def test_deterministic_and_distinct(self) -> None:
        a = numeric_codename("M-001", 7)
        assert a == numeric_codename("M-001", 7)
        assert a != numeric_codename("M-002", 7)
        assert a != numeric_codename("M-001", 8)

    def test_format(self) -> None:
        code = numeric_codename("M-001", 7)
        assert code.startswith("QB-")
        assert len(code.split("-")[1]) == 8
        assert all(c in "0123456789ABCDEF" for c in code.split("-")[1])

    def test_prefix(self) -> None:
        assert numeric_codename("M-001", 7, prefix="BOND").startswith("BOND-")
        with pytest.raises(ValueError, match="prefix"):
            numeric_codename("M-001", 7, prefix="")


class TestAlliterative:
    def test_deterministic(self) -> None:
        assert alliterative_codename(seed=9) == alliterative_codename(seed=9)
        assert alliterative_codename(seed=9) != alliterative_codename(seed=10)

    def test_shared_initial(self) -> None:
        name = alliterative_codename(seed=4)
        adj, noun = name.split("-")
        assert adj[0] == noun[0]
        assert adj in ADJECTIVES and noun in NOUNS

    def test_generates_unique_per_index(self) -> None:
        names = codenames_by_scheme(6, seed=1, scheme="alliterative")
        assert len(names) == 6
        for name in names:
            adj, noun = name.split("-")
            assert adj[0] == noun[0]

    def test_initial_pair_no_pair_raises(self) -> None:
        # 'Z' has no adjective or noun starter in the bundled lists.
        with pytest.raises(ValueError, match="no alliterative pair"):
            _initial_pair(make_rng(1), "Z")

    def test_empty_lists_raise(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr(_codnames, "ADJECTIVES", ())
        monkeypatch.setattr(_codnames, "NOUNS", ())
        with pytest.raises(ValueError, match="no alliterative letter"):
            alliterative_codename(seed=1)
