"""Tests for src/bond_utilities/reporting.py — real rendered text, no mocks."""

from __future__ import annotations

import contextlib
import io
from datetime import datetime, timezone

import pytest

from bond_utilities.clock import MissionSchedule
from bond_utilities.reporting import (
    banner,
    format_kv,
    format_table,
    print_kv,
    print_schedule_table,
    print_table,
    schedule_table,
)


class TestBanner:
    def test_renders_three_lines(self) -> None:
        lines = banner("Q-BRANCH", width=12).split("\n")
        assert len(lines) == 3
        assert set(lines[0]) == {"="}
        assert len(lines[0]) == 12

    def test_title_centered(self) -> None:
        lines = banner("AB", width=10).split("\n")
        assert lines[1].strip() == "AB"

    def test_custom_fill(self) -> None:
        assert banner("X", width=6, fill="-").split("\n")[0] == "------"

    def test_width_too_small_raises(self) -> None:
        with pytest.raises(ValueError, match="width"):
            banner("X", width=3)

    def test_empty_fill_raises(self) -> None:
        with pytest.raises(ValueError, match="fill"):
            banner("X", width=8, fill="")


class TestFormatTable:
    def test_with_headers(self) -> None:
        text = format_table([["a", "bb"], ["cc", "d"]], headers=["h1", "h2"])
        lines = text.split("\n")
        assert lines[0] == "h1  h2"  # header row
        assert lines[1] == "--  --"  # dash separator
        assert len(lines) == 4  # header, dashes, two data rows
        assert "a   bb" in lines[2]

    def test_without_headers(self) -> None:
        text = format_table([["x", "yyy"], ["zz", "w"]])
        assert text.split("\n") == ["x   yyy", "zz  w"]

    def test_empty_rows_no_headers(self) -> None:
        assert format_table([]) == ""

    def test_ragged_rows_raise(self) -> None:
        with pytest.raises(ValueError, match="same number of cells"):
            format_table([["a"], ["b", "c"]])

    def test_empty_rows_with_headers(self) -> None:
        text = format_table([], headers=["a", "b"])
        assert "a  b" in text


class TestFormatKv:
    def test_aligned_pairs(self) -> None:
        text = format_kv([("a", 1), ("longkey", "x")])
        lines = text.split("\n")
        assert lines[0].startswith("a")
        assert " : " in lines[0]

    def test_empty_pairs(self) -> None:
        assert format_kv([]) == ""

    def test_values_by_index(self) -> None:
        text = format_kv([("k", "v")])
        assert text == "k : v"


class TestPrintHelpers:
    def test_print_table_to_stream(self) -> None:
        stream = io.StringIO()
        print_table([["1", "SILENT-JAGUAR"]], headers=["#", "codename"], stream=stream)
        out = stream.getvalue()
        assert "SILENT-JAGUAR" in out
        assert out.endswith("\n")

    def test_print_kv_to_stream(self) -> None:
        stream = io.StringIO()
        print_kv([("path", "/tmp/x.json")], stream=stream)
        assert "/tmp/x.json" in stream.getvalue()

    def test_default_stream_follows_redirected_stdout(self) -> None:
        """The stdout default resolves at call time, not at import time.

        Binding ``stream=sys.stdout`` in the signature would capture the
        interpreter's original stdout, and this redirect would capture nothing.
        """
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            print_table([["1", "SILENT-JAGUAR"]], headers=["#", "codename"])
            print_kv([("mission", "M-001")])
        captured = buffer.getvalue()
        assert "SILENT-JAGUAR" in captured
        assert "mission : M-001" in captured


class TestScheduleTable:
    def _windows(self) -> list[MissionSchedule]:
        utc = timezone.utc
        return [
            MissionSchedule("grid", datetime(2026, 8, 4, 0, tzinfo=utc), datetime(2026, 8, 6, 0, tzinfo=utc)),
            MissionSchedule("recon", datetime(2026, 8, 2, 0, tzinfo=utc), datetime(2026, 8, 3, 0, tzinfo=utc)),
        ]

    def test_renders_rows_and_status(self) -> None:
        now = datetime(2026, 8, 5, 0, tzinfo=timezone.utc)
        text = schedule_table(self._windows(), now=now)
        assert "grid" in text
        assert "recon" in text
        assert "ACTIVE" in text
        assert "COMPLETE" in text
        assert "PENDING" not in text

    def test_custom_headers(self) -> None:
        text = schedule_table(
            self._windows(), now=datetime(2026, 8, 5, tzinfo=timezone.utc), headers=["n", "s", "e", "st"]
        )
        assert "st" in text

    def test_non_schedule_raises(self) -> None:
        with pytest.raises(ValueError, match="MissionSchedule"):
            schedule_table(["not-a-schedule"])  # type: ignore[list-item]

    def test_print_to_stream(self) -> None:
        stream = io.StringIO()
        print_schedule_table(self._windows(), now=datetime(2026, 8, 5, tzinfo=timezone.utc), stream=stream)
        assert "grid" in stream.getvalue()

    def test_default_stream_follows_redirected_stdout(self) -> None:
        buffer = io.StringIO()
        with contextlib.redirect_stdout(buffer):
            print_schedule_table(self._windows(), now=datetime(2026, 8, 5, tzinfo=timezone.utc))
        assert "grid" in buffer.getvalue()
