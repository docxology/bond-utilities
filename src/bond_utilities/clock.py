"""Mission elapsed-time and schedule-window utilities.

All functions accept timezone-aware datetimes; naive datetimes are treated
as UTC (documented, deterministic). Wall-clock defaults (``now=None``) are
provided only where the semantics are inherently about "right now" — tests
always pass explicit ``now`` values so behavior is fully deterministic.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

_DAY_SECONDS = 86400


def to_utc(value: datetime) -> datetime:
    """Return ``value`` as a timezone-aware UTC datetime.

    Naive datetimes are assumed to already be UTC (documented convention);
    aware datetimes are converted to UTC.

    Args:
        value: Any datetime.

    Returns:
        An equivalent, timezone-aware datetime in UTC.
    """
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def parse_timestamp(text: str) -> datetime:
    """Parse an ISO-8601 timestamp, accepting a trailing ``Z``.

    Args:
        text: ISO-8601 string such as ``"2026-08-04T00:00:00Z"``.

    Returns:
        A timezone-aware UTC datetime.

    Raises:
        ValueError: If ``text`` is not a parseable timestamp.
    """
    normalized = text[:-1] + "+00:00" if text.endswith("Z") else text
    return to_utc(datetime.fromisoformat(normalized))


def elapsed_time(start: datetime, end: datetime) -> timedelta:
    """Return ``end - start`` as a non-negative duration.

    Args:
        start: Mission start (naive treated as UTC).
        end: Mission end (naive treated as UTC).

    Returns:
        ``end - start``.

    Raises:
        ValueError: If ``end`` precedes ``start``.
    """
    delta = to_utc(end) - to_utc(start)
    if delta < timedelta(0):
        raise ValueError("elapsed end must not precede start")
    return delta


def format_elapsed(delta: timedelta) -> str:
    """Format a duration as ``[Nd ]HH:MM:SS`` (the day part is omitted when zero).

    Args:
        delta: A non-negative duration.

    Returns:
        The formatted duration string.

    Raises:
        ValueError: If ``delta`` is negative.
    """
    if delta < timedelta(0):
        raise ValueError("cannot format a negative duration")
    total = int(delta.total_seconds())
    days, remainder = divmod(total, _DAY_SECONDS)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    if days:
        return f"{days}d {hours:02d}:{minutes:02d}:{seconds:02d}"
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def window_open(
    start: datetime,
    end: datetime,
    now: datetime | None = None,
) -> bool:
    """Return True when ``now`` falls inside the half-open window ``[start, end)``.

    Args:
        start: Window start.
        end: Window end (must not precede ``start``).
        now: Reference instant; defaults to the current UTC time.

    Returns:
        True if ``start <= now < end``.

    Raises:
        ValueError: If ``end`` precedes ``start``.
    """
    start_utc, end_utc = to_utc(start), to_utc(end)
    if end_utc < start_utc:
        raise ValueError("window end must not precede start")
    current = to_utc(now) if now is not None else datetime.now(timezone.utc)
    return start_utc <= current < end_utc


def window_elapsed(start: datetime, now: datetime | None = None) -> timedelta:
    """Return the time elapsed since window ``start``, clamped at zero.

    Args:
        start: Window start.
        now: Reference instant; defaults to the current UTC time.

    Returns:
        ``now - start`` when positive, otherwise zero.
    """
    delta = (to_utc(now) if now is not None else datetime.now(timezone.utc)) - to_utc(start)
    return delta if delta > timedelta(0) else timedelta(0)


def window_remaining(end: datetime, now: datetime | None = None) -> timedelta:
    """Return the time remaining until window ``end``, clamped at zero.

    Args:
        end: Window end.
        now: Reference instant; defaults to the current UTC time.

    Returns:
        ``end - now`` when positive, otherwise zero.
    """
    delta = to_utc(end) - (to_utc(now) if now is not None else datetime.now(timezone.utc))
    return delta if delta > timedelta(0) else timedelta(0)


def t_minus(target: datetime, now: datetime | None = None) -> str:
    """Render a ``T-`` countdown (or ``T+`` count-up) relative to ``target``.

    Args:
        target: The target instant.
        now: Reference instant; defaults to the current UTC time.

    Returns:
        ``"T-{elapsed}"`` while ``now`` precedes the target, otherwise
        ``"T+{elapsed}"`` (including at the exact target instant).
    """
    target_utc = to_utc(target)
    current = to_utc(now) if now is not None else datetime.now(timezone.utc)
    if target_utc >= current:
        return f"T-{format_elapsed(target_utc - current)}"
    return f"T+{format_elapsed(current - target_utc)}"


def parse_schedule(schedule: dict) -> tuple[datetime, datetime]:
    """Extract ``(start, end)`` aware UTC datetimes from a mission schedule.

    Args:
        schedule: Mapping with ISO-8601 ``start`` and ``end`` keys.

    Returns:
        The ``(start, end)`` pair, both normalized to UTC.

    Raises:
        ValueError: If the mapping is invalid, a key is missing, a value is
            not a parseable timestamp, or ``end`` precedes ``start``.
    """
    if not isinstance(schedule, dict):
        raise ValueError("schedule must be a mapping")
    try:
        start_text = schedule["start"]
        end_text = schedule["end"]
    except KeyError as exc:
        raise ValueError(f"schedule missing required key {exc.args[0]!r}") from exc
    start = parse_timestamp(start_text)
    end = parse_timestamp(end_text)
    if end < start:
        raise ValueError("schedule end must not precede start")
    return start, end


__all__ = [
    "to_utc",
    "parse_timestamp",
    "elapsed_time",
    "format_elapsed",
    "window_open",
    "window_elapsed",
    "window_remaining",
    "t_minus",
    "parse_schedule",
]
