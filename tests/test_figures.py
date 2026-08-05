"""Tests for src/bond_utilities/figures/ — real PNG output, no mocks."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from bond_utilities.figures import plot_frequency_analysis, plot_mission_schedule

UTC = timezone.utc


def _dt(hour: int) -> datetime:
    return datetime(2026, 8, 4, hour, tzinfo=UTC)


class TestPlotMissionSchedule:
    def test_writes_png_to_explicit_path(self, tmp_path: Path) -> None:
        target = tmp_path / "figs" / "schedule.png"
        result = plot_mission_schedule(_dt(0), _dt(6), now=_dt(3), path=target)
        assert result == target.resolve()
        assert target.exists()
        assert target.stat().st_size > 0
        # PNG magic bytes.
        assert target.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"

    def test_writes_default_path(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        result = plot_mission_schedule(_dt(0), _dt(23), now=_dt(12))
        default = (tmp_path / "output" / "figures" / "mission_schedule.png").resolve()
        assert result == default
        assert Path(result).exists()
        assert Path(result).stat().st_size > 0

    def test_naive_datetimes_accepted(self, tmp_path: Path) -> None:
        target = tmp_path / "naive.png"
        start = datetime(2026, 8, 4, 0, 0)
        end = datetime(2026, 8, 4, 4, 0)
        plot_mission_schedule(start, end, now=datetime(2026, 8, 4, 2, 0), path=target)
        assert target.exists()

    def test_end_before_start_raises(self, tmp_path: Path) -> None:
        with pytest.raises(ValueError, match="must not precede"):
            plot_mission_schedule(_dt(6), _dt(0), now=_dt(3), path=tmp_path / "x.png")


class TestPlotFrequencyAnalysis:
    def test_writes_png_to_explicit_path(self, tmp_path: Path) -> None:
        target = tmp_path / "freq.png"
        result = plot_frequency_analysis("THEQUICKBROWNFOX", path=target)
        assert result == target.resolve()
        assert target.exists()
        assert target.stat().st_size > 0
        assert target.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"

    def test_deterministic_bytes(self, tmp_path: Path) -> None:
        a = tmp_path / "a.png"
        b = tmp_path / "b.png"
        plot_frequency_analysis("HELLO WORLD", path=a)
        plot_frequency_analysis("HELLO WORLD", path=b)
        assert a.read_bytes() == b.read_bytes()

    def test_default_path(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.chdir(tmp_path)
        result = plot_frequency_analysis("QBRANCH")
        default = (tmp_path / "output" / "figures" / "letter_frequency.png").resolve()
        assert Path(result) == default
        assert Path(result).exists()
