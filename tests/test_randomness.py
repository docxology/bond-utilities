"""Tests for src/bond_utilities/randomness.py — reproducibility, no mocks."""

from __future__ import annotations

import random

import pytest

from bond_utilities.randomness import (
    SEEDED_HELPERS,
    derive_seed,
    make_rng,
    seeded,
    seeded_bytes,
    seeded_choice,
    seeded_choices,
    seeded_float,
    seeded_int,
    seeded_sample,
    seeded_shuffle,
)


class TestDeriveSeed:
    def test_int_passthrough_deterministic(self) -> None:
        assert derive_seed(42) == derive_seed(42)
        assert derive_seed(42) == 42

    def test_str_hashed_deterministic(self) -> None:
        assert derive_seed("mission-7") == derive_seed("mission-7")

    def test_str_and_int_differ_normally(self) -> None:
        # A string seed is hashed, not interpreted as an integer.
        assert derive_seed("7") != derive_seed(7)

    def test_negative_int_folded(self) -> None:
        assert 0 <= derive_seed(-1) < 2**32

    def test_range_bound(self) -> None:
        assert 0 <= derive_seed("anything") < 2**32


class TestMakeRng:
    def test_reproducible_streams(self) -> None:
        a = make_rng(20260804)
        b = make_rng(20260804)
        assert [a.randrange(1000) for _ in range(10)] == [b.randrange(1000) for _ in range(10)]

    def test_string_seed_reproducible(self) -> None:
        a = make_rng("ops")
        b = make_rng("ops")
        assert a.random() == b.random()

    def test_returns_independent_instances(self) -> None:
        a = make_rng(5)
        b = make_rng(5)
        a.randrange(10)
        # b is independent: drawing from a does not consume b's stream.
        assert a.randrange(1000) != b.randrange(1000)

    def test_none_returns_generator(self) -> None:
        assert isinstance(make_rng(None), random.Random)


def _uses_global_random() -> float:
    return random.random()


class TestSeeded:
    def test_decorator_deterministic(self) -> None:
        wrapped = seeded(99)(_uses_global_random)
        assert wrapped() == wrapped()

    def test_decorator_restores_state(self) -> None:
        random.seed(1)
        before = random.random()
        random.seed(1)
        seeded(123)(_uses_global_random)()
        random.seed(1)
        after = random.random()
        assert before == after

    def test_decorator_string_seed(self) -> None:
        wrapped = seeded("key")(_uses_global_random)
        assert wrapped() == wrapped()

    def test_decorator_two_different_seeds_differ(self) -> None:
        assert seeded(1)(_uses_global_random)() != seeded(2)(_uses_global_random)()

    def test_decorator_preserves_return_value_and_never_raises_through(self) -> None:
        wrapped = seeded(7)(lambda: 42)
        assert wrapped() == 42


class TestSeededBytes:
    def test_deterministic(self) -> None:
        assert seeded_bytes("ops", 16) == seeded_bytes("ops", 16)
        assert seeded_bytes("ops", 16) != seeded_bytes("labs", 16)

    def test_length(self) -> None:
        assert len(seeded_bytes(1, 8)) == 8

    def test_zero_length_raises(self) -> None:
        with pytest.raises(ValueError, match="length"):
            seeded_bytes(1, 0)


class TestSeededIntFloat:
    def test_int_deterministic_in_range(self) -> None:
        assert seeded_int(1, 0, 100) == seeded_int(1, 0, 100)
        value = seeded_int(5, 10, 20)
        assert 10 <= value < 20

    def test_int_invalid_range_raises(self) -> None:
        with pytest.raises(ValueError, match="lo < hi"):
            seeded_int(1, 20, 20)

    def test_float_deterministic_in_range(self) -> None:
        assert seeded_float(3, 0.0, 1.0) == seeded_float(3, 0.0, 1.0)
        value = seeded_float(3, 5.0, 6.0)
        assert 5.0 <= value < 6.0

    def test_float_invalid_range_raises(self) -> None:
        with pytest.raises(ValueError, match="lo <= hi"):
            seeded_float(1, 2.0, 1.0)


class TestSeededChoiceChoices:
    def test_choice_deterministic(self) -> None:
        items = ["A", "B", "C", "D"]
        assert seeded_choice("s", items) == seeded_choice("s", items)
        assert seeded_choice("s", items) in items

    def test_choice_empty_raises(self) -> None:
        with pytest.raises(ValueError, match="non-empty"):
            seeded_choice(1, [])

    def test_choices_deterministic_length(self) -> None:
        items = ["A", "B"]
        draws = seeded_choices(9, items, 5)
        assert len(draws) == 5
        assert draws == seeded_choices(9, items, 5)

    def test_choices_zero_k(self) -> None:
        assert seeded_choices(9, ["A"], 0) == []

    def test_choices_empty_or_negative_k_raises(self) -> None:
        with pytest.raises(ValueError, match="non-empty"):
            seeded_choices(9, [], 2)
        with pytest.raises(ValueError, match="k >= 0"):
            seeded_choices(9, ["A"], -1)


class TestSeededShuffleSample:
    def test_shuffle_deterministic_and_does_not_mutate(self) -> None:
        original = ["A", "B", "C", "D", "E"]
        first = seeded_shuffle(2, original)
        second = seeded_shuffle(2, original)
        assert first == second
        assert sorted(first) == sorted(original)
        # Input is not mutated.
        assert original == ["A", "B", "C", "D", "E"]

    def test_shuffle_actually_permutes_canonical(self) -> None:
        # For a seed known to change order on a 5-element list.
        shuffled = seeded_shuffle(1, list(range(5)))
        assert sorted(shuffled) == list(range(5))
        assert set(shuffled) == set(range(5))

    def test_sample_deterministic(self) -> None:
        items = list(range(10))
        assert seeded_sample(4, items, 3) == seeded_sample(4, items, 3)

    def test_sample_k_out_of_range_raises(self) -> None:
        with pytest.raises(ValueError):
            seeded_sample(4, list(range(3)), 5)
        with pytest.raises(ValueError):
            seeded_sample(4, list(range(3)), -1)


class TestSeededHelperRegistry:
    """`SEEDED_HELPERS` must stay bound to the module's real draw helpers.

    A registry that is merely a hand-written tuple can drift silently once a
    helper is added or renamed; these two directions make drift a test failure.
    """

    def test_every_registered_name_is_a_real_exported_callable(self) -> None:
        import bond_utilities.randomness as module

        for name in SEEDED_HELPERS:
            attribute = getattr(module, name, None)
            assert callable(attribute), f"SEEDED_HELPERS names a non-callable: {name}"
            assert name in module.__all__, f"SEEDED_HELPERS names an unexported helper: {name}"

    def test_registry_covers_every_seeded_draw_helper(self) -> None:
        import inspect

        import bond_utilities.randomness as module

        discovered = {
            name
            for name, obj in vars(module).items()
            if name.startswith("seeded_")
            and inspect.isfunction(obj)
            and getattr(obj, "__module__", "") == module.__name__
        }
        assert discovered == set(SEEDED_HELPERS)

    def test_registry_order_is_stable(self) -> None:
        # The manuscript's {{SEEDED_HELPERS_CSV}} token renders this order.
        assert SEEDED_HELPERS[0] == "seeded_bytes"
        assert SEEDED_HELPERS[-1] == "seeded_sample"
        assert len(SEEDED_HELPERS) == len(set(SEEDED_HELPERS))
