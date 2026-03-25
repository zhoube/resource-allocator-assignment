from __future__ import annotations

from calendar import monthrange
from datetime import date, datetime, time, timedelta
from typing import Iterable


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


def isoformat_zless(value: datetime) -> str:
    return value.strftime("%Y%m%dT%H%M%S")
