"""Pytest configuration for bond-utilities tests.

Pins the matplotlib Agg backend (headless), ensures ``src/`` is importable,
and re-exports the shared fixtures from ``bond_utilities.testing`` so every
bond package can reuse them.
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

# Re-export shared fixtures so `seeded_rng` / `mission_record` / `temp_dir`
# are available to every test module without a mock framework.
from bond_utilities.testing import (  # noqa: E402
    DEFAULT_TEST_SEED,
    mission_record,
    seeded_codenames,
    seeded_rng,
    temp_dir,
)

__all__ = ["DEFAULT_TEST_SEED", "mission_record", "seeded_codenames", "seeded_rng", "temp_dir"]
