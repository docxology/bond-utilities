"""Binds the byte-identical regeneration claim in `manuscript/06_reproducibility.md`.

The manuscript, `README.md` and `AGENTS.md` all state that running the single
documented regeneration command twice on the same commit rewrites `output/`
byte for byte. That is a claim about the *persisted artifacts produced by the
real command*, so this module tests exactly that: it shells out to
`scripts/z_generate_manuscript_variables.py` twice and compares a SHA-256
digest of the whole artifact tree.

Why not a fixed-clock unit test: this package already had one
(`generate_variables(now=FIXED_NOW)`), and it passed happily for the entire
life of a `GENERATION_TIMESTAMP` token that read `datetime.now()` by default
and was rendered into `05_experimental_setup.md`. Injecting the clock proves
the function is a pure function of its arguments; it says nothing about what
the shipped command writes to disk. Only running the command can say that.

The sleep between the two runs is load-bearing, not padding — see
:func:`_advance_past_a_second_boundary`.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
import time
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
GENERATOR = PROJECT_ROOT / "scripts" / "z_generate_manuscript_variables.py"
OUTPUT_ROOT = PROJECT_ROOT / "output"

#: Files the byte-identical claim covers: everything the generator persists.
#: Not a hand-listed subset — the tree is walked, so a new artifact is covered
#: the moment it is written, and a shrinking tree fails the emptiness guard.
ARTIFACT_SUFFIXES = (".json", ".md", ".png", ".csv", ".yaml")


def _regenerate() -> None:
    """Run the documented regeneration command exactly as the docs give it."""
    proc = subprocess.run(
        [sys.executable, str(GENERATOR)],
        cwd=str(PROJECT_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, f"regeneration failed:\n{proc.stderr}"


def _artifact_paths() -> list[Path]:
    return sorted(path for path in OUTPUT_ROOT.rglob("*") if path.is_file() and path.suffix in ARTIFACT_SUFFIXES)


def _tree_digest() -> tuple[str, list[str]]:
    """Return (digest, relative paths) for the whole generated artifact tree."""
    paths = _artifact_paths()
    digest = hashlib.sha256()
    for path in paths:
        digest.update(path.relative_to(OUTPUT_ROOT).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest(), [p.relative_to(OUTPUT_ROOT).as_posix() for p in paths]


def _per_file_digests() -> dict[str, str]:
    return {
        path.relative_to(OUTPUT_ROOT).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in _artifact_paths()
    }


def _advance_past_a_second_boundary() -> None:
    """Sleep just over one second between the two regeneration runs.

    The defect this test exists to catch stamped
    ``datetime.now(timezone.utc).isoformat(timespec="seconds")`` into the token
    map. At second resolution, two back-to-back runs inside the same wall-clock
    second produce the same stamp — so without this sleep the test would be
    green by construction even with the wall clock fully reinstated.
    """
    time.sleep(1.05)


class TestRegenerationIsByteIdentical:
    def test_artifact_tree_is_non_empty(self) -> None:
        """Guard against the comparison below going vacuous on an empty tree."""
        _regenerate()
        _, names = _tree_digest()
        assert names, "no artifacts found — the byte-equality assertions would be vacuous"
        assert "data/manuscript_variables.json" in names
        assert "figures/mission_schedule.png" in names
        assert "figures/letter_frequency.png" in names

    def test_two_runs_produce_the_same_tree_digest(self) -> None:
        _regenerate()
        first, first_names = _tree_digest()

        _advance_past_a_second_boundary()

        _regenerate()
        second, second_names = _tree_digest()

        assert first_names == second_names, "regeneration changed the artifact inventory"
        assert first == second, (
            "regeneration is not byte-identical: the artifact tree hashed "
            f"{first} then {second}. Something in the pipeline reads the wall "
            "clock or another ambient input."
        )

    def test_every_artifact_is_individually_unchanged(self) -> None:
        """Name the offending file, rather than only failing the tree digest."""
        _regenerate()
        before = _per_file_digests()

        _advance_past_a_second_boundary()

        _regenerate()
        after = _per_file_digests()

        changed = sorted(name for name, digest in before.items() if after.get(name) != digest)
        assert not changed, f"artifacts differ between two regenerations: {changed}"

    def test_json_token_map_carries_no_wall_clock_value(self) -> None:
        """A value equal to 'now' would defeat the digest check on a fast machine."""
        import json

        _regenerate()
        raw = (OUTPUT_ROOT / "data" / "manuscript_variables.json").read_text(encoding="utf-8")
        variables = json.loads(raw)
        assert variables, "empty token map — the scan below would be vacuous"

        today = time.strftime("%Y-%m-%d", time.gmtime())
        offenders = [name for name, value in variables.items() if value == today]
        # The only date-bearing token is CONFIG_MANUSCRIPT_DATE, read from
        # `manuscript/config.yaml`. It may legitimately coincide with today's
        # date, so it is exempt -- but nothing else may.
        offenders = [name for name in offenders if name != "CONFIG_MANUSCRIPT_DATE"]
        assert not offenders, f"tokens holding today's date rather than a committed value: {offenders}"


class TestScheduleFigureIsPinnedToCommittedConfig:
    """The two-run digest alone is too weak for the schedule figure.

    Its dashed marker moves with `now`, but one second of drift is a fraction
    of a pixel across a multi-day window, so a wall clock reinstated *there*
    would survive the back-to-back comparison above. This test closes that gap
    by re-deriving the figure from the committed config and demanding the
    persisted PNG match byte for byte — which fails immediately if the
    generator ever falls back to the library's `datetime.now()` default.
    """

    def test_persisted_png_equals_a_render_at_the_committed_instant(self, tmp_path: Path) -> None:
        from bond_utilities.clock import parse_schedule
        from bond_utilities.figures import plot_mission_schedule
        from bond_utilities.manuscript_variables import load_mission_config, manuscript_instant

        _regenerate()
        persisted = (OUTPUT_ROOT / "figures" / "mission_schedule.png").read_bytes()

        config = load_mission_config(PROJECT_ROOT)
        start, end = parse_schedule(config["mission"]["schedule"])
        reference = manuscript_instant(config)
        expected_path = plot_mission_schedule(start, end, now=reference, path=tmp_path / "expected.png")

        assert persisted == expected_path.read_bytes(), (
            "the persisted schedule figure is not the render pinned to "
            f"{reference.isoformat()} — the generator is using a different "
            "reference instant (most likely the wall-clock default)"
        )

    def test_a_different_instant_really_does_change_the_bytes(self, tmp_path: Path) -> None:
        """Positive control: without this, the check above could be vacuous."""
        from datetime import timedelta

        from bond_utilities.clock import parse_schedule
        from bond_utilities.figures import plot_mission_schedule
        from bond_utilities.manuscript_variables import load_mission_config, manuscript_instant

        config = load_mission_config(PROJECT_ROOT)
        start, end = parse_schedule(config["mission"]["schedule"])
        reference = manuscript_instant(config)

        pinned = plot_mission_schedule(start, end, now=reference, path=tmp_path / "a.png")
        moved = plot_mission_schedule(start, end, now=reference + timedelta(days=1), path=tmp_path / "b.png")

        assert pinned.read_bytes() != moved.read_bytes(), (
            "the marker instant does not affect the rendered bytes — the "
            "binding above would pass no matter what instant the generator used"
        )
