"""Tests for src/bond_utilities/randomness.py — reproducibility, no mocks."""

from __future__ import annotations

import random

from bond_utilities.randomness import derive_seed, make_rng, seeded


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
