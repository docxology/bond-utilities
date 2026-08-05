"""Tests for src/bond_utilities/clock.py — schedule/window/elapsed math, no mocks."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from bond_utilities.clock import (
    MissionSchedule,
    elapsed_time,
    format_elapsed,
    merge_windows,
    parse_duration,
    parse_schedule,
    parse_timestamp,
    schedule_status,
    t_minus,
    to_utc,
    window_elapsed,
    window_open,
    window_remaining,
    windows_overlap,
)

UTC = timezone.utc


def _dt(year: int, month: int, day: int, hour: int = 0, minute: int = 0) -> datetime:
    return datetime(year, month, day, hour, minute, tzinfo=UTC)


class TestToUtc:
    def test_naive_assumed_utc(self) -> None:
        result = to_utc(datetime(2026, 8, 4, 12, 0))
        assert result.tzinfo is UTC
        assert result.hour == 12

    def test_aware_converted_to_utc(self) -> None:
        aware = datetime(2026, 8, 4, 5, 0, tzinfo=timezone(timedelta(hours=-5)))
        result = to_utc(aware)
        assert result.tzinfo == UTC
        assert result.hour == 10


class TestParseTimestamp:
    def test_z_suffix(self) -> None:
        assert parse_timestamp("2026-08-04T00:00:00Z") == _dt(2026, 8, 4)

    def test_numeric_offset(self) -> None:
        assert parse_timestamp("2026-08-04T00:00:00+00:00") == _dt(2026, 8, 4)

    def test_naive_is_utc(self) -> None:
        assert parse_timestamp("2026-08-04T01:02:03").tzinfo == UTC

    def test_invalid_raises(self) -> None:
        with pytest.raises(ValueError):
            parse_timestamp("not-a-date")


class TestElapsedAndFormat:
    def test_elapsed_basic(self) -> None:
        assert elapsed_time(_dt(2026, 8, 4), _dt(2026, 8, 4, 1, 30)) == timedelta(hours=1, minutes=30)

    def test_elapsed_zero(self) -> None:
        assert elapsed_time(_dt(2026, 8, 4), _dt(2026, 8, 4)) == timedelta(0)

    def test_elapsed_end_before_start_raises(self) -> None:
        with pytest.raises(ValueError, match="must not precede"):
            elapsed_time(_dt(2026, 8, 4, 2), _dt(2026, 8, 4, 1))

    def test_format_with_days(self) -> None:
        assert format_elapsed(timedelta(days=2, hours=3, minutes=4, seconds=5)) == "2d 03:04:05"

    def test_format_without_days(self) -> None:
        assert format_elapsed(timedelta(hours=1, minutes=2, seconds=3)) == "01:02:03"

    def test_format_zero(self) -> None:
        assert format_elapsed(timedelta(0)) == "00:00:00"

    def test_format_negative_raises(self) -> None:
        with pytest.raises(ValueError, match="negative"):
            format_elapsed(timedelta(seconds=-1))


class TestWindow:
    START = _dt(2026, 8, 4, 0, 0)
    END = _dt(2026, 8, 4, 6, 0)

    def test_window_open_true_inside(self) -> None:
        assert window_open(self.START, self.END, now=_dt(2026, 8, 4, 3, 0)) is True

    def test_window_open_false_before(self) -> None:
        assert window_open(self.START, self.END, now=_dt(2026, 8, 3, 23, 0)) is False

    def test_window_open_false_at_end(self) -> None:
        # Half-open: at `end` the window is closed.
        assert window_open(self.START, self.END, now=self.END) is False

    def test_window_open_at_start(self) -> None:
        assert window_open(self.START, self.END, now=self.START) is True

    def test_window_open_end_before_start_raises(self) -> None:
        with pytest.raises(ValueError, match="must not precede"):
            window_open(self.END, self.START, now=self.START)

    def test_window_elapsed_positive(self) -> None:
        assert window_elapsed(self.START, now=_dt(2026, 8, 4, 2, 0)) == timedelta(hours=2)

    def test_window_elapsed_clamped_before_start(self) -> None:
        assert window_elapsed(self.START, now=_dt(2026, 8, 3, 23, 0)) == timedelta(0)

    def test_window_elapsed_at_start_zero(self) -> None:
        assert window_elapsed(self.START, now=self.START) == timedelta(0)

    def test_window_remaining_positive(self) -> None:
        assert window_remaining(self.END, now=_dt(2026, 8, 4, 2, 0)) == timedelta(hours=4)

    def test_window_remaining_clamped_after_end(self) -> None:
        assert window_remaining(self.END, now=_dt(2026, 8, 4, 7, 0)) == timedelta(0)

    def test_window_remaining_at_end_zero(self) -> None:
        assert window_remaining(self.END, now=self.END) == timedelta(0)


class TestTMinus:
    def test_countdown(self) -> None:
        assert t_minus(_dt(2026, 8, 4, 12, 0), now=_dt(2026, 8, 4, 10, 30)) == "T-01:30:00"

    def test_countdown_with_days(self) -> None:
        assert t_minus(_dt(2026, 8, 6, 0, 0), now=_dt(2026, 8, 4, 0, 0)) == "T-2d 00:00:00"

    def test_countup_after_target(self) -> None:
        assert t_minus(_dt(2026, 8, 4, 10, 0), now=_dt(2026, 8, 4, 11, 30)) == "T+01:30:00"

    def test_at_target_is_countdown_zero(self) -> None:
        assert t_minus(_dt(2026, 8, 4, 10, 0), now=_dt(2026, 8, 4, 10, 0)) == "T-00:00:00"


class TestParseSchedule:
    VALID = {"start": "2026-08-04T00:00:00Z", "end": "2026-08-10T00:00:00Z"}

    def test_valid(self) -> None:
        start, end = parse_schedule(self.VALID)
        assert start == _dt(2026, 8, 4)
        assert end == _dt(2026, 8, 10)
        assert (end - start) == timedelta(days=6)

    def test_not_a_mapping(self) -> None:
        with pytest.raises(ValueError, match="mapping"):
            parse_schedule(["start"])  # type: ignore[arg-type]

    def test_missing_key(self) -> None:
        with pytest.raises(ValueError, match="missing required key 'end'"):
            parse_schedule({"start": "2026-08-04T00:00:00Z"})

    def test_bad_timestamp(self) -> None:
        with pytest.raises(ValueError):
            parse_schedule({"start": "nope", "end": "2026-08-10T00:00:00Z"})

    def test_end_before_start(self) -> None:
        with pytest.raises(ValueError, match="must not precede"):
            parse_schedule({"start": "2026-08-10T00:00:00Z", "end": "2026-08-04T00:00:00Z"})


class TestWindowsOverlap:
    A_START = _dt(2026, 8, 4, 0)
    A_END = _dt(2026, 8, 8, 0)
    B_START = _dt(2026, 8, 6, 0)
    B_END = _dt(2026, 8, 10, 0)

    def test_partial_overlap(self) -> None:
        assert windows_overlap(self.A_START, self.A_END, self.B_START, self.B_END) == timedelta(days=2)

    def test_contained(self) -> None:
        # B fully inside A.
        assert windows_overlap(self.A_START, self.A_END, _dt(2026, 8, 5, 0), _dt(2026, 8, 6, 0)) == timedelta(days=1)

    def test_disjoint(self) -> None:
        assert windows_overlap(self.A_START, self.A_END, _dt(2026, 8, 9, 0), _dt(2026, 8, 12, 0)) == timedelta(0)

    def test_touching_is_zero(self) -> None:
        assert windows_overlap(self.A_START, self.A_END, self.A_END, _dt(2026, 8, 12, 0)) == timedelta(0)

    def test_invalid_window_raises(self) -> None:
        with pytest.raises(ValueError, match="window A"):
            windows_overlap(self.A_END, self.A_START, self.B_START, self.B_END)
        with pytest.raises(ValueError, match="window B"):
            windows_overlap(self.A_START, self.A_END, self.B_END, self.B_START)


class TestMergeWindows:
    def test_merges_overlapping(self) -> None:
        windows = [
            (_dt(2026, 8, 4, 0), _dt(2026, 8, 6, 0)),
            (_dt(2026, 8, 5, 0), _dt(2026, 8, 9, 0)),
            (_dt(2026, 8, 10, 0), _dt(2026, 8, 12, 0)),
        ]
        merged = merge_windows(windows)
        assert len(merged) == 2
        assert merged[0] == (_dt(2026, 8, 4, 0), _dt(2026, 8, 9, 0))
        assert merged[1] == (_dt(2026, 8, 10, 0), _dt(2026, 8, 12, 0))

    def test_nested_and_touching(self) -> None:
        merged = merge_windows(
            [
                (_dt(2026, 8, 4, 0), _dt(2026, 8, 10, 0)),
                (_dt(2026, 8, 5, 0), _dt(2026, 8, 6, 0)),
                (_dt(2026, 8, 10, 0), _dt(2026, 8, 11, 0)),
            ]
        )
        assert merged == [(_dt(2026, 8, 4, 0), _dt(2026, 8, 11, 0))]

    def test_sorted_output(self) -> None:
        merged = merge_windows([(_dt(2026, 8, 8, 0), _dt(2026, 8, 9, 0)), (_dt(2026, 8, 4, 0), _dt(2026, 8, 5, 0))])
        assert merged == [(_dt(2026, 8, 4, 0), _dt(2026, 8, 5, 0)), (_dt(2026, 8, 8, 0), _dt(2026, 8, 9, 0))]

    def test_invalid_window_raises(self) -> None:
        with pytest.raises(ValueError, match="must not precede"):
            merge_windows([(_dt(2026, 8, 6, 0), _dt(2026, 8, 4, 0))])

    def test_empty(self) -> None:
        assert merge_windows([]) == []


class TestParseDuration:
    @pytest.mark.parametrize(
        "text,expected",
        [
            ("1d 2h30m", timedelta(days=1, hours=2, minutes=30)),
            ("90m", timedelta(minutes=90)),
            ("45s", timedelta(seconds=45)),
            ("3d", timedelta(days=3)),
            ("2H", timedelta(hours=2)),
        ],
    )
    def test_valid(self, text: str, expected: timedelta) -> None:
        assert parse_duration(text) == expected

    @pytest.mark.parametrize("text", ["", "  ", "5", "1x", "abc", "1h2", "h"])
    def test_invalid(self, text: str) -> None:
        with pytest.raises(ValueError):
            parse_duration(text)


class TestScheduleStatus:
    START = _dt(2026, 8, 4, 0)
    END = _dt(2026, 8, 6, 0)

    def test_pending(self) -> None:
        assert schedule_status(self.START, self.END, now=_dt(2026, 8, 3, 0)) == "PENDING"

    def test_active(self) -> None:
        assert schedule_status(self.START, self.END, now=_dt(2026, 8, 5, 0)) == "ACTIVE"

    def test_active_at_start(self) -> None:
        assert schedule_status(self.START, self.END, now=self.START) == "ACTIVE"

    def test_complete(self) -> None:
        assert schedule_status(self.START, self.END, now=_dt(2026, 8, 7, 0)) == "COMPLETE"

    def test_complete_at_end(self) -> None:
        assert schedule_status(self.START, self.END, now=self.END) == "COMPLETE"

    def test_invalid_raises(self) -> None:
        with pytest.raises(ValueError, match="must not precede"):
            schedule_status(self.END, self.START, now=self.START)


class TestMissionSchedule:
    def _window(self) -> MissionSchedule:
        return MissionSchedule("grid", _dt(2026, 8, 4, 0), _dt(2026, 8, 6, 0))

    def test_from_config(self) -> None:
        window = MissionSchedule.from_config("grid", {"start": "2026-08-04T00:00:00Z", "end": "2026-08-06T00:00:00Z"})
        assert window.name == "grid"
        assert window.duration == timedelta(days=2)

    def test_properties(self) -> None:
        window = self._window()
        assert window.duration == timedelta(days=2)
        assert window.open(now=_dt(2026, 8, 5, 0)) is True
        assert window.open(now=_dt(2026, 8, 7, 0)) is False
        assert window.elapsed(now=_dt(2026, 8, 5, 0)) == timedelta(days=1)
        assert window.elapsed(now=_dt(2026, 8, 2, 0)) == timedelta(0)
        assert window.remaining(now=_dt(2026, 8, 5, 0)) == timedelta(days=1)
        assert window.remaining(now=_dt(2026, 8, 9, 0)) == timedelta(0)
        assert window.countdown(now=_dt(2026, 8, 4, 0)) == "T-00:00:00"
        assert window.status(now=_dt(2026, 8, 5, 0)) == "ACTIVE"

    def test_invalid_raises(self) -> None:
        with pytest.raises(ValueError, match="must not precede"):
            MissionSchedule("bad", _dt(2026, 8, 6, 0), _dt(2026, 8, 4, 0))
