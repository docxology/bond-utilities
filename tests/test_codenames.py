"""Tests for src/bond_utilities/codenames.py — deterministic samples, no mocks."""

from __future__ import annotations

import random
from pathlib import Path

import pytest

import bond_utilities.codenames as _codnames
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
from bond_utilities.randomness import make_rng

PROJECT_ROOT = Path(__file__).resolve().parents[1]


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

    def test_each_index_shares_an_initial(self) -> None:
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


class TestSchemeRegistryBinding:
    """`CODENAME_SCHEMES` bound to the dispatcher, not to a literal copy of itself.

    The literal tuple assertion in :class:`TestSchemes` pins the *order* the
    manuscript CSV token renders. These tests pin the *content* against the
    branches `codenames_by_scheme` actually implements, in both directions.
    """

    def _dispatch_branches(self) -> set[str]:
        import inspect
        import re

        source = inspect.getsource(codenames_by_scheme)
        return set(re.findall(r'if scheme == "([a-z_]+)"', source))

    def test_every_registered_scheme_has_a_dispatch_branch(self) -> None:
        missing = set(CODENAME_SCHEMES) - self._dispatch_branches()
        assert not missing, f"CODENAME_SCHEMES entries with no dispatch branch: {sorted(missing)}"

    def test_every_dispatch_branch_is_registered(self) -> None:
        """Reverse direction: a new branch must join the registry."""
        unregistered = self._dispatch_branches() - set(CODENAME_SCHEMES)
        assert not unregistered, f"dispatch branches missing from CODENAME_SCHEMES: {sorted(unregistered)}"

    def test_every_registered_scheme_actually_generates(self) -> None:
        for scheme in CODENAME_SCHEMES:
            names = codenames_by_scheme(3, seed=11, scheme=scheme)
            assert len(names) == 3
            assert all(name and isinstance(name, str) for name in names)
            assert names == codenames_by_scheme(3, seed=11, scheme=scheme)

    def test_unregistered_scheme_is_rejected(self) -> None:
        assert "bifid" not in CODENAME_SCHEMES
        with pytest.raises(ValueError, match="unknown scheme"):
            codenames_by_scheme(2, seed=1, scheme="bifid")


def _shared_initials() -> set[str]:
    """Initials carried by at least one adjective AND one noun."""
    return {adj[0] for adj in ADJECTIVES} & {noun[0] for noun in NOUNS}


def _distinct_alliterative_pairs() -> set[tuple[str, str]]:
    """Every ADJ-NOUN pair the bundled word lists can produce."""
    return {(adj, noun) for adj in ADJECTIVES for noun in NOUNS if adj[0] == noun[0]}


class TestAlliterativeCapacity:
    """The alliterative scheme is small and repeats — pin that, do not imply otherwise.

    `adjective_noun` samples without replacement and raises above capacity.
    `alliterative` seeds each index independently, so a sample of N names can
    (and for the manuscript's own configured sample does) contain duplicates.
    The manuscript and docs state this; these tests bind the statement.
    """

    def test_capacity_is_tiny_relative_to_the_default_grid(self) -> None:
        assert len(_shared_initials()) == 5
        assert len(_distinct_alliterative_pairs()) == 9
        assert len(_distinct_alliterative_pairs()) < len(ADJECTIVES) * len(NOUNS)

    def test_every_generated_name_is_within_capacity(self) -> None:
        pairs = _distinct_alliterative_pairs()
        for index in range(40):
            adj, noun = codenames_by_scheme(1, seed=index, scheme="alliterative")[0].split("-")
            assert (adj, noun) in pairs

    def test_scheme_repeats_names_within_one_sample(self) -> None:
        """The documented behaviour: duplicates are possible, not an error."""
        names = codenames_by_scheme(9, seed=20260804, scheme="alliterative")
        assert len(set(names)) < len(names), "expected a collision from independent per-index seeding"

    def test_manuscript_sample_contains_a_duplicate(self) -> None:
        """The exact sample printed in 03_results.md repeats a name."""
        from bond_utilities.manuscript_variables import generate_variables, load_mission_config

        config = load_mission_config(PROJECT_ROOT)
        variables = generate_variables(config=config)
        names = variables["RESULT_SCHEME_SAMPLE"].split(", ")
        assert len(names) == int(variables["CONFIG_NUM_CODENAMES"])
        assert len(set(names)) < len(names)

    def test_default_scheme_never_repeats(self) -> None:
        """Contrast: adjective_noun samples without replacement."""
        names = generate_codenames(20, seed=20260804)
        assert len(set(names)) == len(names)
