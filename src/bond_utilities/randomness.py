"""Seeded randomness primitives for reproducible mission operations.

Every random draw in the bond suite flows through :func:`make_rng` or the
:func:`seeded` decorator so experiments, codenames, and cipher keys are
byte-for-byte reproducible from a single seed value.

The module is deterministic by construction: the same ``seed`` input always
yields the same generator state, independent of process, platform, or call
order (``random.Random`` is a pure-Python Mersenne Twister).
"""

from __future__ import annotations

import hashlib
import random
from collections.abc import Callable
from functools import wraps
from typing import ParamSpec, TypeVar

P = ParamSpec("P")
R = TypeVar("R")

_MASK32 = 0xFFFFFFFF


def derive_seed(seed: int | str) -> int:
    """Return a stable, non-negative integer seed usable by ``random.Random``.

    Integers are folded to 32 bits; strings are hashed with SHA-256 and the
    first 32 bits of the digest are used. Both paths are deterministic and
    documented so persisted provenance seeds can be replayed exactly.

    Args:
        seed: Any integer or string identifier.

    Returns:
        A deterministic integer in ``[0, 2**32)``.
    """
    if isinstance(seed, int):
        return seed & _MASK32
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()
    return int(digest[:8], 16)


def make_rng(seed: int | str | None = None) -> random.Random:
    """Return a fresh :class:`random.Random` generator.

    With a numeric or string ``seed`` the generator is fully reproducible;
    with ``None`` it is seeded from system entropy (use only where
    reproducibility is not required, e.g. one-off throwaway draws).

    Args:
        seed: Optional seed; strings are hashed via :func:`derive_seed`.

    Returns:
        A new, independent generator instance.
    """
    if seed is None:
        return random.Random()
    return random.Random(derive_seed(seed))


def seeded(seed: int | str) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator that runs ``func`` with the global ``random`` module seeded.

    The previous global RNG state is restored after the call, so decorated
    functions are deterministic in isolation without perturbing callers.

    Args:
        seed: Seed value passed through :func:`derive_seed`.

    Returns:
        A decorator wrapping the decorated function.
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            state = random.getstate()
            random.seed(derive_seed(seed))
            try:
                return func(*args, **kwargs)
            finally:
                random.setstate(state)

        return wrapper

    return decorator


__all__ = ["derive_seed", "make_rng", "seeded"]
