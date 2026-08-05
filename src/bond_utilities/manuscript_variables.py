"""Manuscript ``{{TOKEN}}`` generation from ``manuscript/config.yaml``.

Tokens are computed, never hand-authored in prose: every value either comes
straight from the mission config or is derived deterministically from it by
the library modules (clock window math, codename sampling, cipher registry).
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

from .ciphers import CIPHER_NAMES, CRYPTANALYSIS_HELPERS
from .clock import parse_schedule, windows_overlap
from .codenames import (
    ADJECTIVES,
    NOUNS,
    CODENAME_SCHEMES,
    codenames_by_scheme,
    generate_codenames,
    nato_codename,
)

#: Manuscript config path, relative to the project root.
CONFIG_RELATIVE = Path("manuscript") / "config.yaml"


def load_mission_config(project_root: str | Path | None = None) -> dict[str, Any]:
    """Load and return the manuscript ``config.yaml`` contents.

    Args:
        project_root: Project root; defaults to the parent of ``src/``
            (i.e. the bond-utilities package root).

    Returns:
        The parsed config mapping.

    Raises:
        FileNotFoundError: If the config file is missing.
        ValueError: If the file does not contain a mapping.
    """
    root = Path(project_root) if project_root is not None else Path(__file__).resolve().parents[2]
    config_path = root / CONFIG_RELATIVE
    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)
    if not isinstance(config, dict):
        raise ValueError("config.yaml must contain a mapping")
    return config


def generate_variables(
    config: dict[str, Any] | None = None,
    project_root: str | Path | None = None,
    now: datetime | None = None,
) -> dict[str, str]:
    """Compute the full ``{{TOKEN}} -> value`` map for the manuscript.

    Args:
        config: Pre-loaded config mapping (avoids re-reading the file in
            tests); defaults to :func:`load_mission_config`.
        project_root: Root used to locate ``manuscript/config.yaml``.
        now: Clock override for ``GENERATION_TIMESTAMP`` (tests pass a fixed
            value so the map is fully deterministic).

    Returns:
        Mapping of token name to rendered string value.

    Raises:
        ValueError: If the config is missing the mission/paper sections or
            the schedule is invalid.
    """
    loaded = config if config is not None else load_mission_config(project_root)
    mission = loaded.get("mission")
    paper = loaded.get("paper")
    if not isinstance(mission, dict):
        raise ValueError("config.yaml mission section must be a mapping")
    if not isinstance(paper, dict):
        raise ValueError("config.yaml paper section must be a mapping")

    mission_schedule = mission.get("schedule")
    overlap_cfg = mission.get("overlap_window", mission_schedule)
    if not isinstance(mission_schedule, dict) or not isinstance(overlap_cfg, dict):
        raise ValueError("mission schedule and overlap_window must be mappings")
    start, end = parse_schedule(mission_schedule)
    seed = mission.get("default_seed", 0)
    num_codenames = mission.get("num_codenames", 3)
    sample = generate_codenames(num_codenames, seed=seed)
    # Overlap window defaults to the main schedule (full overlap) when absent.
    overlap_start, overlap_end = parse_schedule(overlap_cfg)
    overlap_hours = windows_overlap(start, end, overlap_start, overlap_end).total_seconds() / 3600
    scheme_sample = codenames_by_scheme(num_codenames, seed=seed, scheme="alliterative")
    stamp = (now or datetime.now(timezone.utc)).isoformat(timespec="seconds")

    return {
        "MISSION_CODENAME": str(mission.get("codename", "Q-BRANCH")),
        "PACKAGE_VERSION": str(paper.get("version", "0.1.0")),
        "CONFIG_DEFAULT_SEED": str(seed),
        "CONFIG_NUM_CODENAMES": str(num_codenames),
        "CONFIG_SCHEDULE_START": start.isoformat(timespec="seconds"),
        "CONFIG_SCHEDULE_END": end.isoformat(timespec="seconds"),
        "RESULT_WINDOW_HOURS": f"{(end - start).total_seconds() / 3600:.1f}",
        "RESULT_OVERLAP_HOURS": f"{overlap_hours:.1f}",
        "RESULT_CODENAME_SAMPLE": ", ".join(sample),
        "RESULT_SCHEME_SAMPLE": ", ".join(scheme_sample),
        "CIPHER_COUNT": str(len(CIPHER_NAMES)),
        "CIPHER_NAMES_CSV": ", ".join(CIPHER_NAMES),
        "CODENAME_SCHEMES": ", ".join(CODENAME_SCHEMES),
        "CRYPTANALYSIS_HELPERS": str(len(CRYPTANALYSIS_HELPERS)),
        "NATO_EXAMPLE": nato_codename("QB7"),
        "WORDLIST_SIZE": f"{len(ADJECTIVES)} x {len(NOUNS)}",
        "GENERATION_TIMESTAMP": stamp,
    }


__all__ = ["CONFIG_RELATIVE", "load_mission_config", "generate_variables"]
