from __future__ import annotations

from dataclasses import replace
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Iterable

from health_scheduler.config.paths import OUTPUTS_DIR
from health_scheduler.config.settings import SLOT_MINUTES, TIME_WINDOWS
from health_scheduler.domain.activities.activity import Activity
from health_scheduler.domain.scheduling.occurrence import Occurrence
from health_scheduler.domain.scheduling.scheduled_event import ScheduledEvent
from health_scheduler.io.exporters.calendar_exporter import export_html, export_ics, export_json_bundle, export_schedule_csv, export_unscheduled_csv
from health_scheduler.io.storage.files import read_csv
from health_scheduler.utils.datetime_utils import add_months, as_datetime, contains_window, daterange, overlaps, parse_datetime

FALLBACK_WINDOWS = ["early_morning", "morning", "midday", "afternoon", "evening"]


def load_rows(path, with_remote: bool = False) -> list[dict]:
    rows = []
    for row in read_csv(path):
        parsed = {**row, "start": parse_datetime(row["start"]), "end": parse_datetime(row["end"])}
        if with_remote and "remote_supported" in row:
            parsed["remote_supported"] = row["remote_supported"] == "true"
        if with_remote and "remote_only" in row:
            parsed["remote_only"] = row["remote_only"] == "true"
        rows.append(parsed)
    return rows


def run_scheduler(
    planned_activities: list[Activity],
    start_date: date,
    end_date: date,
    client_busy: list[dict],
    travel_blocks: list[dict],
    specialists: list[dict],
    allied_health: list[dict],
    equipment_rows: list[dict],
    output_dir: Path | None = OUTPUTS_DIR,
) -> tuple[list[ScheduledEvent], list[dict]]:
    activity_by_id = {item.id: item for item in planned_activities}
    occurrences = build_occurrences(planned_activities, start_date, end_date)

    scheduled: list[ScheduledEvent] = []
    unscheduled: list[dict] = []
    for occurrence in sorted(occurrences, key=sort_key):
        event = schedule_occurrence(occurrence, activity_by_id, scheduled, client_busy, travel_blocks, specialists, allied_health, equipment_rows)
        if event is None:
            unscheduled.append(
                {
                    "occurrence_id": occurrence.occurrence_id,
                    "activity_id": occurrence.activity.id,
                    "activity_title": occurrence.activity.title,
                    "window_start": occurrence.window_start.isoformat(),
                    "window_end": occurrence.window_end.isoformat(),
                    "reason": "No valid slot found after checking direct and backup options.",
                    "skip_adjustment": occurrence.activity.skip_adjustment,
                }
            )
        else:
            scheduled.append(event)

    scheduled.sort(key=lambda item: item.start)
    if output_dir is not None:
        export_schedule_csv(scheduled, output_dir / "scheduled_plan.csv")
        export_unscheduled_csv(unscheduled, output_dir / "unscheduled_plan.csv")
        export_json_bundle(scheduled, unscheduled, output_dir / "schedule_bundle.json")
        export_html(scheduled, unscheduled, output_dir / "personalized_plan.html", start_date, end_date)
        export_ics(scheduled, output_dir / "personalized_plan.ics")
    return scheduled, unscheduled


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
    items = []
    sequence = 1
    active_windows = activity.preferred_time_windows or FALLBACK_WINDOWS
    for day in daterange(start_date, end_date):
        for index in range(activity.frequency.times):
            name = active_windows[min(index, len(active_windows) - 1)]
            start_time, end_time = TIME_WINDOWS[name]
            items.append(Occurrence(f"{activity.id}_occ_{sequence:04d}", activity, sequence, as_datetime(day, start_time), as_datetime(day, end_time), as_datetime(day, midpoint(start_time, end_time))))
            sequence += 1
    return items


def build_periodic(activity: Activity, start_date: date, end_date: date, period_days: int) -> list[Occurrence]:
    items = []
    sequence = 1
    current = start_date
    windows = activity.preferred_time_windows or FALLBACK_WINDOWS
    while current < end_date:
        period_end = min(current + timedelta(days=period_days), end_date)
        last_day = period_end - timedelta(days=1)
        for index, offset in enumerate(spread_offsets(activity.frequency.times, max(1, (period_end - current).days))):
            target_day = min(current + timedelta(days=offset), last_day)
            name = windows[index % len(windows)]
            start_time, end_time = TIME_WINDOWS[name]
            items.append(Occurrence(f"{activity.id}_occ_{sequence:04d}", activity, sequence, datetime.combine(current, time(6, 0)), datetime.combine(last_day, time(22, 0)), datetime.combine(target_day, midpoint(start_time, end_time))))
            sequence += 1
        current = period_end
    return items


def build_monthly(activity: Activity, start_date: date, end_date: date) -> list[Occurrence]:
    items = []
    sequence = 1
    cursor = date(start_date.year, start_date.month, 1)
    windows = activity.preferred_time_windows or FALLBACK_WINDOWS
    while cursor < end_date:
        next_month = add_months(cursor, 1)
        current = max(start_date, cursor)
        period_end = min(end_date, next_month)
        last_day = period_end - timedelta(days=1)
        for index, offset in enumerate(spread_offsets(activity.frequency.times, max(1, (period_end - current).days))):
            target_day = min(current + timedelta(days=offset), last_day)
            name = windows[index % len(windows)]
            start_time, end_time = TIME_WINDOWS[name]
            items.append(Occurrence(f"{activity.id}_occ_{sequence:04d}", activity, sequence, datetime.combine(current, time(6, 0)), datetime.combine(last_day, time(22, 0)), datetime.combine(target_day, midpoint(start_time, end_time))))
            sequence += 1
        cursor = next_month
    return items


def build_yearly(activity: Activity, start_date: date, end_date: date) -> list[Occurrence]:
    name = (activity.preferred_time_windows or ["morning"])[0]
    start_time, end_time = TIME_WINDOWS[name]
    target = start_date + timedelta(days=max(1, (end_date - start_date).days // 2))
    return [Occurrence(f"{activity.id}_occ_0001", activity, 1, datetime.combine(start_date, time(6, 0)), datetime.combine(end_date - timedelta(days=1), time(22, 0)), datetime.combine(target, midpoint(start_time, end_time)))]


def midpoint(start_time: time, end_time: time) -> time:
    start_minutes = start_time.hour * 60 + start_time.minute
    end_minutes = end_time.hour * 60 + end_time.minute
    mid = (start_minutes + end_minutes) // 2
    return time(mid // 60, mid % 60)


def spread_offsets(times: int, span_days: int) -> list[int]:
    if times <= 1:
        return [max(0, span_days // 2)]
    last_index = max(0, span_days - 1)
    return [round(index * last_index / (times - 1)) for index in range(times)]


def sort_key(occurrence: Occurrence) -> tuple:
    constraints = occurrence.activity.constraint_weight()
    window_width = int((occurrence.window_end - occurrence.window_start).total_seconds() // 60)
    return -occurrence.activity.priority, -constraints, window_width, occurrence.preferred_start


def schedule_occurrence(occurrence: Occurrence, activity_by_id: dict[str, Activity], scheduled: list[ScheduledEvent], client_busy: list[dict], travel_blocks: list[dict], specialists: list[dict], allied_health: list[dict], equipment_rows: list[dict]) -> ScheduledEvent | None:
    direct = find_valid_placement(occurrence, scheduled, client_busy, travel_blocks, specialists, allied_health, equipment_rows, None)
    if direct is not None:
        return direct
    for backup_id in occurrence.activity.backup_activity_ids:
        backup = activity_by_id.get(backup_id)
        if backup is None:
            continue
        fallback = find_valid_placement(replace(occurrence, activity=backup), scheduled, client_busy, travel_blocks, specialists, allied_health, equipment_rows, occurrence.activity.title)
        if fallback is not None:
            return fallback
    return None


def find_valid_placement(occurrence: Occurrence, scheduled: list[ScheduledEvent], client_busy: list[dict], travel_blocks: list[dict], specialists: list[dict], allied_health: list[dict], equipment_rows: list[dict], backup_for: str | None) -> ScheduledEvent | None:
    activity = occurrence.activity
    for proposed_start in iter_possible_start_times(occurrence, activity.duration_minutes, activity.preferred_time_windows):
        proposed_end = proposed_start + timedelta(minutes=activity.duration_minutes)
        if proposed_end > occurrence.window_end or conflicts_with_client(proposed_start, proposed_end, activity, client_busy, scheduled):
            continue
        mode = "in_person"
        location = activity.location
        travel_match = overlapping_block(proposed_start, proposed_end, travel_blocks)
        if travel_match is not None:
            travel_placement = activity.travel_placement()
            if travel_placement is None:
                continue
            mode, location = travel_placement
        provider = ""
        if activity.resource_pool == "specialist":
            provider = pick_provider(proposed_start, proposed_end, activity.facilitator_role, specialists, mode, activity.location)
            if not provider:
                continue
        if activity.resource_pool == "allied_health":
            provider = pick_provider(proposed_start, proposed_end, activity.facilitator_role, allied_health, mode, activity.location)
            if not provider:
                continue
        assigned_equipment = pick_equipment(proposed_start, proposed_end, activity.equipment_required, equipment_rows, location)
        if assigned_equipment is None:
            continue
        return ScheduledEvent.from_occurrence(
            occurrence,
            start=proposed_start,
            end=proposed_end,
            location=location,
            mode=mode,
            assigned_provider=provider,
            assigned_equipment=assigned_equipment,
            backup_for=backup_for or "",
        )
    return None


def iter_possible_start_times(occurrence: Occurrence, duration_minutes: int, windows: list[str]) -> Iterable[datetime]:
    names = list(dict.fromkeys((windows or []) + FALLBACK_WINDOWS))
    preferred_day = occurrence.preferred_start.date()
    ordered_days = sorted(daterange(occurrence.window_start.date(), occurrence.window_end.date() + timedelta(days=1)), key=lambda day: (abs((day - preferred_day).days), day))
    for day in ordered_days:
        for name in names:
            start_time, end_time = TIME_WINDOWS[name]
            possible_start = datetime.combine(day, start_time)
            last_start = datetime.combine(day, end_time) - timedelta(minutes=duration_minutes)
            while possible_start <= last_start:
                if occurrence.window_start <= possible_start and possible_start + timedelta(minutes=duration_minutes) <= occurrence.window_end:
                    yield possible_start
                possible_start += timedelta(minutes=SLOT_MINUTES)


def conflicts_with_client(proposed_start: datetime, proposed_end: datetime, activity: Activity, client_busy: list[dict], scheduled: list[ScheduledEvent]) -> bool:
    for block in client_busy:
        if activity.supports_work_microtask_exception() and block.get("commitment_type") == "work":
            continue
        if overlaps(proposed_start, proposed_end, block["start"], block["end"]):
            return True
    for event in scheduled:
        if overlaps(proposed_start, proposed_end, event.start, event.end):
            return True
    return False


def overlapping_block(proposed_start: datetime, proposed_end: datetime, rows: list[dict]) -> dict | None:
    for row in rows:
        if overlaps(proposed_start, proposed_end, row["start"], row["end"]):
            return row
    return None


def pick_provider(proposed_start: datetime, proposed_end: datetime, role: str, rows: list[dict], mode: str, preferred_location: str) -> str:
    for row in rows:
        if row["role"] != role or not contains_window(row["start"], row["end"], proposed_start, proposed_end):
            continue
        if mode == "remote" and not row.get("remote_supported", False):
            continue
        if mode == "in_person" and row["location"] != preferred_location:
            continue
        return row["name"]
    return ""


def pick_equipment(proposed_start: datetime, proposed_end: datetime, equipment_required: list[str], rows: list[dict], location: str) -> list[str] | None:
    if location in {"remote", "travel"} and equipment_required:
        return None
    assigned: list[str] = []
    for equipment_type in equipment_required:
        match = ""
        for row in rows:
            if row["equipment_type"] != equipment_type:
                continue
            if location not in {"remote", "travel"} and row["location"] != location:
                continue
            if contains_window(row["start"], row["end"], proposed_start, proposed_end):
                match = row["resource_id"]
                break
        if not match:
            return None
        assigned.append(match)
    return assigned
