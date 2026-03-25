from __future__ import annotations

from datetime import date, datetime, time, timedelta

from health_scheduler.config.settings import TIME_WINDOWS
from health_scheduler.domain.activities.activity import Activity
from health_scheduler.domain.scheduling.occurrence import Occurrence
from health_scheduler.utils.datetime_utils import add_months, as_datetime, daterange

FALLBACK_WINDOWS = ["early_morning", "morning", "midday", "afternoon", "evening"]


def build_occurrences(activities: list[Activity], start_date: date, end_date: date) -> list[Occurrence]:
    occurrences: list[Occurrence] = []
    for activity in activities:
        frequency = activity.frequency
        if frequency.period == "day":
            occurrences.extend(build_daily(activity, start_date, end_date))
        elif frequency.period == "week":
            occurrences.extend(build_periodic(activity, start_date, end_date, 7))
        elif frequency.period == "month":
            occurrences.extend(build_monthly(activity, start_date, end_date))
        elif frequency.period == "year":
            occurrences.extend(build_yearly(activity, start_date, end_date))
    return occurrences


def build_daily(activity: Activity, start_date: date, end_date: date) -> list[Occurrence]:
    items: list[Occurrence] = []
    sequence = 1
    active_windows = activity.preferred_time_windows or FALLBACK_WINDOWS
    day_window_start, day_window_end = planning_day_bounds()
    for day in daterange(start_date, end_date):
        for index in range(activity.frequency.times):
            name = active_windows[min(index, len(active_windows) - 1)]
            start_time, end_time = TIME_WINDOWS[name]
            items.append(
                Occurrence(
                    f"{activity.id}_occ_{sequence:04d}",
                    activity,
                    sequence,
                    as_datetime(day, day_window_start),
                    as_datetime(day, day_window_end),
                    as_datetime(day, midpoint(start_time, end_time)),
                )
            )
            sequence += 1
    return items


def build_periodic(activity: Activity, start_date: date, end_date: date, period_days: int) -> list[Occurrence]:
    items: list[Occurrence] = []
    sequence = 1
    current = start_date
    windows = activity.preferred_time_windows or FALLBACK_WINDOWS
    day_window_start, day_window_end = planning_day_bounds()
    while current < end_date:
        period_end = min(current + timedelta(days=period_days), end_date)
        last_day = period_end - timedelta(days=1)
        for index, offset in enumerate(spread_offsets(activity.frequency.times, max(1, (period_end - current).days))):
            target_day = min(current + timedelta(days=offset), last_day)
            name = windows[index % len(windows)]
            start_time, end_time = TIME_WINDOWS[name]
            items.append(
                Occurrence(
                    f"{activity.id}_occ_{sequence:04d}",
                    activity,
                    sequence,
                    datetime.combine(current, day_window_start),
                    datetime.combine(last_day, day_window_end),
                    datetime.combine(target_day, midpoint(start_time, end_time)),
                )
            )
            sequence += 1
        current = period_end
    return items


def build_monthly(activity: Activity, start_date: date, end_date: date) -> list[Occurrence]:
    items: list[Occurrence] = []
    sequence = 1
    cursor = date(start_date.year, start_date.month, 1)
    windows = activity.preferred_time_windows or FALLBACK_WINDOWS
    day_window_start, day_window_end = planning_day_bounds()
    while cursor < end_date:
        next_month = add_months(cursor, 1)
        current = max(start_date, cursor)
        period_end = min(end_date, next_month)
        last_day = period_end - timedelta(days=1)
        for index, offset in enumerate(spread_offsets(activity.frequency.times, max(1, (period_end - current).days))):
            target_day = min(current + timedelta(days=offset), last_day)
            name = windows[index % len(windows)]
            start_time, end_time = TIME_WINDOWS[name]
            items.append(
                Occurrence(
                    f"{activity.id}_occ_{sequence:04d}",
                    activity,
                    sequence,
                    datetime.combine(current, day_window_start),
                    datetime.combine(last_day, day_window_end),
                    datetime.combine(target_day, midpoint(start_time, end_time)),
                )
            )
            sequence += 1
        cursor = next_month
    return items


def build_yearly(activity: Activity, start_date: date, end_date: date) -> list[Occurrence]:
    name = (activity.preferred_time_windows or ["morning"])[0]
    start_time, end_time = TIME_WINDOWS[name]
    target = start_date + timedelta(days=max(1, (end_date - start_date).days // 2))
    day_window_start, day_window_end = planning_day_bounds()
    return [
        Occurrence(
            f"{activity.id}_occ_0001",
            activity,
            1,
            datetime.combine(start_date, day_window_start),
            datetime.combine(end_date - timedelta(days=1), day_window_end),
            datetime.combine(target, midpoint(start_time, end_time)),
        )
    ]


def midpoint(start_time: time, end_time: time) -> time:
    start_minutes = start_time.hour * 60 + start_time.minute
    end_minutes = end_time.hour * 60 + end_time.minute
    middle = (start_minutes + end_minutes) // 2
    return time(middle // 60, middle % 60)


def planning_day_bounds() -> tuple[time, time]:
    starts = [start for start, _ in TIME_WINDOWS.values()]
    ends = [end for _, end in TIME_WINDOWS.values()]
    return min(starts), max(ends)


def spread_offsets(times: int, span_days: int) -> list[int]:
    if times <= 1:
        return [max(0, span_days // 2)]
    last_index = max(0, span_days - 1)
    return [round(index * last_index / (times - 1)) for index in range(times)]


def sort_key(occurrence: Occurrence) -> tuple:
    constraints = occurrence.activity.constraint_weight()
    window_width = int((occurrence.window_end - occurrence.window_start).total_seconds() // 60)
    return -occurrence.activity.priority, -constraints, window_width, occurrence.preferred_start
