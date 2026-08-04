"""Tests for src/bond_utilities/clock.py — schedule/window/elapsed math, no mocks."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from bond_utilities.clock import (
    elapsed_time,
    format_elapsed,
    parse_schedule,
    parse_timestamp,
    t_minus,
    to_utc,
    window_elapsed,
    window_open,
    window_remaining,
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
