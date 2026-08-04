"""Plain-text table and key/value reporting for thin CLIs.

Everything here writes to an explicit ``stream`` (default ``sys.stdout``)
so callers and tests can capture output without mocks — pass a
``io.StringIO`` in tests and assert on real rendered text.
"""

from __future__ import annotations

import sys
from collections.abc import Sequence
from typing import TextIO

Cell = object


def banner(title: str, width: int = 60, fill: str = "=") -> str:
    """Return a centered ``title`` wrapped between two ``fill`` lines.

    Args:
        title: Text to center.
        width: Total line width (>= 4).
        fill: Single-character (or repeated) filler.

    Returns:
        A three-line banner string without a trailing newline.

    Raises:
        ValueError: If ``width`` is too small or ``fill`` is empty.
    """
    if width < 4:
        raise ValueError("width must be >= 4")
    if not fill:
        raise ValueError("fill must not be empty")
    line = fill * width
    return f"{line}\n{title.center(width)}\n{line}"


def format_table(
    rows: Sequence[Sequence[Cell]],
    headers: Sequence[str] | None = None,
) -> str:
    """Render ``rows`` as a left-aligned, fixed-width text table.

    Args:
        rows: Row cells; each cell is converted with ``str()``.
        headers: Optional header row, separated from data by dashes.

    Returns:
        The formatted table as a single string (no trailing newline),
        or an empty string when there are no rows and no headers.

    Raises:
        ValueError: If rows have inconsistent cell counts.
    """
    table: list[list[str]] = [[str(cell) for cell in row] for row in rows]
    if headers is not None:
        table.insert(0, [str(header) for header in headers])
    if table and any(len(row) != len(table[0]) for row in table):
        raise ValueError("all table rows must have the same number of cells")
    if not table:
        return ""
    widths = [max(len(row[index]) for row in table) for index in range(len(table[0]))]
    lines: list[str] = []
    for row_index, row in enumerate(table):
        cells = [cell.ljust(widths[index]) if index < len(widths) - 1 else cell for index, cell in enumerate(row)]
        lines.append("  ".join(cells))
        if headers is not None and row_index == 0:
            lines.append("  ".join("-" * len(cell) for cell in cells))
    return "\n".join(lines)


def format_kv(pairs: Sequence[tuple[str, Cell]]) -> str:
    """Render ``key: value`` pairs with right-aligned keys.

    Args:
        pairs: Sequence of ``(key, value)`` pairs; both are stringified.

    Returns:
        One ``key : value`` line per pair (keys aligned), no trailing newline.
    """
    items = [(str(key), str(value)) for key, value in pairs]
    if not items:
        return ""
    width = max(len(key) for key, _ in items)
    return "\n".join(f"{key.ljust(width)} : {value}" for key, value in items)


def print_table(
    rows: Sequence[Sequence[Cell]],
    headers: Sequence[str] | None = None,
    stream: TextIO = sys.stdout,
) -> None:
    """Print :func:`format_table` output to ``stream`` (default stdout)."""
    print(format_table(rows, headers), file=stream)


def print_kv(
    pairs: Sequence[tuple[str, Cell]],
    stream: TextIO = sys.stdout,
) -> None:
    """Print :func:`format_kv` output to ``stream`` (default stdout)."""
    print(format_kv(pairs), file=stream)


__all__ = ["banner", "format_table", "format_kv", "print_table", "print_kv"]
