"""Pytest configuration for bond-utilities tests.

Pins the matplotlib Agg backend (headless), ensures ``src/`` is importable,
and re-exports the shared test surface from ``bond_utilities.testing`` so every
bond package can reuse it.
"""

from __future__ import annotations

import os
import sys

# Force the headless matplotlib backend before any plotting module imports it.
os.environ.setdefault("MPLBACKEND", "Agg")

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
for _path in (SRC, ROOT):
    if _path not in sys.path:
        sys.path.insert(0, _path)

# Re-export the shared test surface. Only `seeded_rng` and `mission_record` are
# pytest fixtures — re-exporting them here makes them requestable by name in any
# test signature. `temp_dir` (a context manager) and `seeded_codenames` (a plain
# function) are re-exported for convenience only; test modules import them
# directly. No mock framework is involved in any of it.
from bond_utilities.testing import (  # noqa: E402
    DEFAULT_TEST_SEED,
    mission_record,
    seeded_codenames,
    seeded_rng,
    temp_dir,
)

__all__ = ["DEFAULT_TEST_SEED", "mission_record", "seeded_codenames", "seeded_rng", "temp_dir"]
