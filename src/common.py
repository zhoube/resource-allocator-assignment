from __future__ import annotations

import csv
import json
from calendar import monthrange
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any, Iterable

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
OUTPUT_DIR = ROOT_DIR / "output"
ACTIVITIES_DIR = DATA_DIR / "activities"
CONSTRAINTS_DIR = DATA_DIR / "constraints"
ACTION_PLANS_DIR = DATA_DIR / "action_plans"

ACTIVITY_CATALOG_JSON = ACTIVITIES_DIR / "activity_catalog.json"
ACTIVITY_CATALOG_CSV = ACTIVITIES_DIR / "activity_catalog.csv"

ACTION_PLAN_JSON = ACTION_PLANS_DIR / "action_plan.json"
ACTION_PLAN_CSV = ACTION_PLANS_DIR / "action_plan.csv"

CLIENT_SCHEDULE_CSV = CONSTRAINTS_DIR / "client_schedule.csv"
TRAVEL_PLANS_CSV = CONSTRAINTS_DIR / "travel_plans.csv"
SPECIALISTS_CSV = CONSTRAINTS_DIR / "specialists.csv"
ALLIED_HEALTH_CSV = CONSTRAINTS_DIR / "allied_health.csv"
EQUIPMENT_CSV = CONSTRAINTS_DIR / "equipment.csv"
CONSTRAINTS_BUNDLE_JSON = CONSTRAINTS_DIR / "constraints_bundle.json"

DEFAULT_START_DATE = date(2026, 4, 1)
DEFAULT_MONTHS = 3
SLOT_MINUTES = 30

TIME_WINDOWS = {
    "early_morning": (time(6, 0), time(8, 0)),
    "morning": (time(8, 0), time(11, 0)),
    "midday": (time(11, 30), time(14, 0)),
    "afternoon": (time(14, 0), time(17, 0)),
    "evening": (time(17, 30), time(21, 0)),
}


def ensure_directories() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ACTIVITIES_DIR.mkdir(parents=True, exist_ok=True)
    CONSTRAINTS_DIR.mkdir(parents=True, exist_ok=True)
    ACTION_PLANS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


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


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


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
