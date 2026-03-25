from __future__ import annotations

from calendar import monthrange
from datetime import date, datetime, time, timedelta
from typing import Iterable

WEEKDAY_NAMES = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")


def add_months(start: date, months: int) -> date:
    month_index = start.month - 1 + months
    year = start.year + month_index // 12
    month = month_index % 12 + 1
    day = min(start.day, monthrange(year, month)[1])
    return date(year, month, day)


def daterange(start: date, end: date) -> Iterable[date]:
    current = start
    while current < end:
        yield current
        current += timedelta(days=1)


def parse_date(value: str) -> date:
    return date.fromisoformat(value)


def parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


def overlaps(start_a: datetime, end_a: datetime, start_b: datetime, end_b: datetime) -> bool:
    return start_a < end_b and start_b < end_a


def contains_window(block_start: datetime, block_end: datetime, start: datetime, end: datetime) -> bool:
    return block_start <= start and end <= block_end


def as_datetime(day: date, value: time) -> datetime:
    return datetime.combine(day, value)


def parse_time(value: str) -> time:
    return time.fromisoformat(value)


def parse_compact_time(value: str) -> time:
    return time(int(value[:2]), int(value[2:4]))


def weekday_name(index: int) -> str:
    return WEEKDAY_NAMES[index]


def format_weekday_pattern(days: list[int]) -> str:
    return ";".join(weekday_name(day) for day in days)


def parse_weekday_pattern(value: str) -> list[int]:
    if not value:
        return []
    return [WEEKDAY_NAMES.index(part.strip()) for part in value.split(";") if part.strip()]


def format_compact_range(start: time, end: time) -> str:
    return f"{start.strftime('%H%M')}-{end.strftime('%H%M')}"


def parse_compact_ranges(value: str) -> list[tuple[time, time]]:
    ranges: list[tuple[time, time]] = []
    for part in value.split(";"):
        cleaned = part.strip()
        if not cleaned:
            continue
        start_text, end_text = cleaned.split("-", maxsplit=1)
        ranges.append((parse_compact_time(start_text), parse_compact_time(end_text)))
    return ranges


def isoformat_zless(value: datetime) -> str:
    return value.strftime("%Y%m%dT%H%M%S")
