"""Deterministic codename generation from adjective + noun word lists.

Codenames are always sampled through a seeded :class:`random.Random`
generator, so a fixed seed yields a fixed list — across runs, processes,
and machines. The word lists are small and curated so every generated name
reads as a plausible mission codename.
"""

from __future__ import annotations

import random
from itertools import product

from .randomness import derive_seed, make_rng

#: Adjective pool for codename generation (kept short and curated).
ADJECTIVES = (
    "SILENT",
    "CRIMSON",
    "VELVET",
    "IRON",
    "GOLDEN",
    "SHADOW",
    "CLEAR",
    "WILD",
    "POLAR",
    "BRAVE",
    "SUBTLE",
    "RAPID",
)

#: Noun pool for codename generation (kept short and curated).
NOUNS = (
    "JAGUAR",
    "FALCON",
    "BEACON",
    "RIVER",
    "LANTERN",
    "RAVEN",
    "SENTINEL",
    "ORACLE",
    "COMET",
    "HARBOR",
    "WOLVERINE",
    "HORIZON",
)

_MAX_PAIRS = len(ADJECTIVES) * len(NOUNS)


def random_codename(rng: random.Random, separator: str = "-") -> str:
    """Sample one ``ADJ{separator}NOUN`` codename from ``rng``.

    Args:
        rng: A (preferably seeded) generator, e.g. from :func:`make_rng`.
        separator: Joiner between adjective and noun.

    Returns:
        A single uppercase codename.
    """
    if not separator:
        raise ValueError("separator must not be empty")
    return f"{rng.choice(ADJECTIVES)}{separator}{rng.choice(NOUNS)}"


def generate_codenames(
    count: int,
    seed: int | str | None = None,
    separator: str = "-",
) -> list[str]:
    """Generate ``count`` deterministic, unique codenames.

    Pairs are sampled without replacement from the full adjective × noun
    product, so the output contains no duplicates.

    Args:
        count: Number of codenames (``1 <= count <= 144`` for the default lists).
        seed: Seed for the generator; ``None`` uses system entropy.
        separator: Joiner between adjective and noun.

    Returns:
        A list of ``count`` unique uppercase codenames.

    Raises:
        ValueError: If ``count`` is out of range or ``separator`` is empty.
    """
    pairs = list(product(ADJECTIVES, NOUNS))
    if not 1 <= count <= len(pairs):
        raise ValueError(f"count must be in [1, {len(pairs)}], got {count}")
    if not separator:
        raise ValueError("separator must not be empty")
    rng = make_rng(seed)
    return [f"{adj}{separator}{noun}" for adj, noun in rng.sample(pairs, count)]


def codename_for(name: str, seed: int | str | None = None) -> str:
    """Derive one stable codename for a mission ``name``.

    The name (and optional seed) is folded into a derived seed, so the same
    inputs always yield the same codename while different names diverge.

    Args:
        name: Mission or operator name.
        seed: Optional extra seed to namespace the derivation.

    Returns:
        A single uppercase codename.
    """
    combined = f"{seed}:{name}" if seed is not None else name
    rng = make_rng(derive_seed(combined))
    return random_codename(rng)


__all__ = [
    "ADJECTIVES",
    "NOUNS",
    "random_codename",
    "generate_codenames",
    "codename_for",
]
