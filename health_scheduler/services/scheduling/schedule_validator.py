from __future__ import annotations

from datetime import date, datetime, timedelta

from health_scheduler.domain.activities.activity import Activity
from health_scheduler.domain.scheduling.scheduled_event import ScheduledEvent
from health_scheduler.io.storage.files import read_csv
from health_scheduler.utils.datetime_utils import (
    contains_window,
    overlaps,
    parse_compact_ranges,
    parse_date,
    parse_datetime,
    parse_weekday_pattern,
)


def load_rows(path, with_remote: bool = False) -> list[dict]:
    rows: list[dict] = []
    for row in read_csv(path):
        parsed = dict(row)
        if row.get("start") and row.get("end"):
            parsed["start"] = parse_datetime(row["start"])
            parsed["end"] = parse_datetime(row["end"])
        if row.get("date"):
            parsed["date"] = parse_date(row["date"])
        if "weekday_pattern" in row:
            parsed["weekdays"] = parse_weekday_pattern(row["weekday_pattern"])
        elif row.get("weekday"):
            parsed["weekdays"] = parse_weekday_pattern(row["weekday"])
        if row.get("available_ranges"):
            parsed["available_ranges"] = parse_compact_ranges(row["available_ranges"])
        if with_remote and "remote_supported" in row:
            parsed["remote_supported"] = row["remote_supported"] == "true"
        if with_remote and "remote_only" in row:
            parsed["remote_only"] = row["remote_only"] == "true"
        rows.append(parsed)
    return rows


class ScheduleValidator:
    def __init__(
        self,
        planning_start_date: date,
        planning_end_date: date,
        client_availability: list[dict],
        travel_blocks: list[dict],
        specialists: list[dict],
        allied_health: list[dict],
        equipment_rows: list[dict],
    ) -> None:
        self.planning_start_date = planning_start_date
        self.planning_end_date = planning_end_date
        self.client_availability = client_availability
        self.travel_blocks = travel_blocks
        self.specialists = specialists
        self.allied_health = allied_health
        self.equipment_rows = equipment_rows

    def constraints_prompt_payload(self) -> dict:
        return {
            "planning_window": {
                "start_date": self.planning_start_date.isoformat(),
                "end_date": self.planning_end_date.isoformat(),
            },
            "client_availability": [self._client_availability_text(row) for row in self.client_availability],
            "travel_plans": [self._serialize_row(row) for row in self.travel_blocks],
            "specialists": [self._provider_prompt_payload(row) for row in self.specialists],
            "allied_health": [self._provider_prompt_payload(row) for row in self.allied_health],
            "equipment": [self._equipment_prompt_payload(row) for row in self.equipment_rows],
        }

    def materialize_event(
        self,
        scheduled_activity: Activity,
        proposed_start_text: str,
        scheduled: list[ScheduledEvent],
    ) -> tuple[ScheduledEvent | None, str | None]:
        if not proposed_start_text:
            return None, "No proposed_start was provided."
        try:
            proposed_start = parse_datetime(proposed_start_text)
        except ValueError:
            return None, "proposed_start is not a valid ISO datetime."

        proposed_end = proposed_start + timedelta(minutes=scheduled_activity.duration_minutes)
        if self._conflicts_with_client(proposed_start, proposed_end, scheduled):
            return None, "Proposed time is outside client availability or overlaps another scheduled event."

        travel_match = self._overlapping_row(proposed_start, proposed_end, self.travel_blocks)
        placements: list[tuple[str, str]] = []
        if travel_match is not None:
            travel_placement = scheduled_activity.travel_placement()
            if travel_placement is None:
                return None, "Proposed time overlaps travel and this activity cannot be performed during travel."
            placements.append(travel_placement)
        else:
            placements.append(("in_person", scheduled_activity.location))
            if scheduled_activity.remote_allowed and scheduled_activity.resource_pool != "self":
                placements.append(("remote", "remote"))

        last_error = "Proposed time could not satisfy activity constraints."
        for mode, location in placements:
            provider = ""
            if scheduled_activity.resource_pool == "specialist":
                provider = self._pick_provider(
                    proposed_start,
                    proposed_end,
                    scheduled_activity.facilitator_role,
                    self.specialists,
                    mode,
                    scheduled_activity.location,
                    scheduled,
                )
                if not provider:
                    last_error = "No matching specialist was available for the proposed time."
                    continue
            elif scheduled_activity.resource_pool == "allied_health":
                provider = self._pick_provider(
                    proposed_start,
                    proposed_end,
                    scheduled_activity.facilitator_role,
                    self.allied_health,
                    mode,
                    scheduled_activity.location,
                    scheduled,
                )
                if not provider:
                    last_error = "No matching allied health provider was available for the proposed time."
                    continue

            assigned_equipment = self._pick_equipment(
                proposed_start,
                proposed_end,
                scheduled_activity.equipment_required,
                self.equipment_rows,
                location,
                scheduled,
            )
            if assigned_equipment is None:
                last_error = self._equipment_failure_reason(
                    scheduled_activity.equipment_required,
                    location,
                    travel_match,
                )
                continue

            return (
                ScheduledEvent.from_activity(
                    scheduled_activity,
                    start=proposed_start,
                    end=proposed_end,
                    location=location,
                    mode=mode,
                    assigned_provider=provider,
                    assigned_equipment=assigned_equipment,
                ),
                None,
            )

        return None, last_error

    def _serialize_row(self, row: dict) -> dict:
        serialized = {}
        for key, value in row.items():
            if key in {"weekdays", "available_ranges"}:
                continue
            if isinstance(value, datetime):
                serialized[key] = value.isoformat()
            elif isinstance(value, date):
                serialized[key] = value.isoformat()
            else:
                serialized[key] = value
        return serialized

    def _client_availability_text(self, row: dict) -> str:
        label = row.get("weekday") or row.get("date", "")
        if isinstance(label, date):
            label = label.isoformat()
        lines = [f"{row.get('entry_type', 'pattern').title()}: {label}", f"Available: {self._format_ranges(row.get('available_ranges', []))}"]
        if row.get("notes"):
            lines.append(f"Notes: {row['notes']}")
        return "\n".join(lines)

    def _provider_prompt_payload(self, row: dict) -> dict:
        return {
            "resource_id": row["resource_id"],
            "name": row["name"],
            "role": row["role"],
            "location": row["location"],
            "remote_supported": bool(row.get("remote_supported", False)),
            "availability": self._template_availability_text(row),
        }

    def _equipment_prompt_payload(self, row: dict) -> dict:
        return {
            "resource_id": row["resource_id"],
            "equipment_type": row["equipment_type"],
            "location": row["location"],
            "availability": self._template_availability_text(row),
        }

    def _template_availability_text(self, row: dict) -> str:
        if row.get("weekday_pattern"):
            label = row["weekday_pattern"]
        elif row.get("weekday"):
            label = row["weekday"]
        elif row.get("date"):
            label = row["date"].isoformat() if isinstance(row["date"], date) else row["date"]
        else:
            label = "Custom"
        lines = [f"Pattern: {label}", f"Available: {self._format_ranges(row.get('available_ranges', []))}"]
        if row.get("notes"):
            lines.append(f"Notes: {row['notes']}")
        return "\n".join(lines)

    def _format_ranges(self, ranges: list[tuple]) -> str:
        if not ranges:
            return "none"
        return ", ".join(f"{start.strftime('%H%M')} to {end.strftime('%H%M')}" for start, end in ranges)

    def _conflicts_with_client(self, proposed_start: datetime, proposed_end: datetime, scheduled: list[ScheduledEvent]) -> bool:
        if not self._fits_client_availability(proposed_start, proposed_end):
            return True
        for event in scheduled:
            if overlaps(proposed_start, proposed_end, event.start, event.end):
                return True
        return False

    def _fits_client_availability(self, proposed_start: datetime, proposed_end: datetime) -> bool:
        for row in self._matching_client_rows(proposed_start.date()):
            if self._availability_row_contains_window(row, proposed_start, proposed_end):
                return True
        return False

    def _matching_client_rows(self, target_day: date) -> list[dict]:
        exact_rows = [row for row in self.client_availability if row.get("date") == target_day]
        if exact_rows:
            return exact_rows
        return [row for row in self.client_availability if target_day.weekday() in row.get("weekdays", [])]

    def _availability_row_contains_window(self, row: dict, proposed_start: datetime, proposed_end: datetime) -> bool:
        if row.get("date") and row["date"] != proposed_start.date():
            return False
        if row.get("weekdays") and proposed_start.weekday() not in row["weekdays"]:
            return False
        for start_time, end_time in row.get("available_ranges", []):
            block_start = datetime.combine(proposed_start.date(), start_time)
            block_end = datetime.combine(proposed_start.date(), end_time)
            if contains_window(block_start, block_end, proposed_start, proposed_end):
                return True
        return False

    def _overlapping_row(self, proposed_start: datetime, proposed_end: datetime, rows: list[dict]) -> dict | None:
        for row in rows:
            if overlaps(proposed_start, proposed_end, row["start"], row["end"]):
                return row
        return None

    def _pick_provider(
        self,
        proposed_start: datetime,
        proposed_end: datetime,
        role: str,
        rows: list[dict],
        mode: str,
        preferred_location: str,
        scheduled: list[ScheduledEvent],
    ) -> str:
        for row in rows:
            if row["role"] != role:
                continue
            if not self._availability_row_contains_window(row, proposed_start, proposed_end):
                continue
            if mode == "remote" and not row.get("remote_supported", False):
                continue
            if mode == "in_person" and row["location"] != preferred_location:
                continue
            if self._provider_booked(row["name"], proposed_start, proposed_end, scheduled):
                continue
            return row["name"]
        return ""

    def _pick_equipment(
        self,
        proposed_start: datetime,
        proposed_end: datetime,
        equipment_required: list[str],
        rows: list[dict],
        location: str,
        scheduled: list[ScheduledEvent],
    ) -> list[str] | None:
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
                if not self._availability_row_contains_window(row, proposed_start, proposed_end):
                    continue
                if self._resource_booked(row["resource_id"], proposed_start, proposed_end, scheduled):
                    continue
                match = row["resource_id"]
                break
            if not match:
                return None
            assigned.append(match)
        return assigned

    def _equipment_failure_reason(
        self,
        equipment_required: list[str],
        location: str,
        travel_match: dict | None,
    ) -> str:
        equipment_label = ", ".join(equipment_required) if equipment_required else "required equipment"
        if travel_match is not None and location in {"remote", "travel"}:
            destination = travel_match.get("destination", "the trip")
            return (
                f"Activity requires {equipment_label}, but the proposed time falls during travel to "
                f"{destination} and that equipment is not available away from home."
            )
        if location in {"remote", "travel"}:
            return f"Activity requires {equipment_label}, but that equipment is not available in {location} mode."
        return f"Activity requires {equipment_label}, but no matching equipment was available at {location} for the proposed time."

    def _provider_booked(self, provider_name: str, proposed_start: datetime, proposed_end: datetime, scheduled: list[ScheduledEvent]) -> bool:
        for event in scheduled:
            if event.assigned_provider == provider_name and overlaps(proposed_start, proposed_end, event.start, event.end):
                return True
        return False

    def _resource_booked(self, resource_id: str, proposed_start: datetime, proposed_end: datetime, scheduled: list[ScheduledEvent]) -> bool:
        for event in scheduled:
            if resource_id in event.assigned_equipment and overlaps(proposed_start, proposed_end, event.start, event.end):
                return True
        return False
