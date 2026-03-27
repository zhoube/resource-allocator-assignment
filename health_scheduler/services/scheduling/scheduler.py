from __future__ import annotations

from datetime import date
from pathlib import Path

from health_scheduler.config.paths import OUTPUTS_DIR
from health_scheduler.domain.activities.activity import Activity
from health_scheduler.domain.scheduling.scheduled_event import ScheduledEvent
from health_scheduler.io.exporters.calendar_exporter import export_html, export_ics, export_json_bundle, export_schedule_csv, export_unscheduled_csv
from health_scheduler.services.scheduling.llm_scheduler import OpenAISchedulingAgent
from health_scheduler.services.scheduling.schedule_parser import parse_schedule_response
from health_scheduler.services.scheduling.schedule_validator import ScheduleValidator, load_rows


def run_scheduler(
    planned_activities: list[Activity],
    start_date: date,
    end_date: date,
    client_availability: list[dict],
    travel_blocks: list[dict],
    specialists: list[dict],
    allied_health: list[dict],
    equipment_rows: list[dict],
    output_dir: Path | None = OUTPUTS_DIR,
) -> tuple[list[ScheduledEvent], list[dict]]:
    activity_by_id = {item.id: item for item in planned_activities}
    print("      Preparing deterministic validator and constraint payload...")
    validator = ScheduleValidator(start_date, end_date, client_availability, travel_blocks, specialists, allied_health, equipment_rows)
    agent = OpenAISchedulingAgent()
    print("      Sending one scheduling request to the LLM...")
    response_text = agent.request_schedule(
        build_activities_payload(planned_activities),
        validator.constraints_prompt_payload(),
    )
    # print(response_text)
    print("      Parsing LLM response...")
    proposed_events = parse_schedule_response(response_text)
    print(f"      Parsed {len(proposed_events)} proposed scheduled events from the LLM.")

    print("[4/5] Validating and materializing scheduled events...")
    scheduled, unscheduled = apply_schedule_events(activity_by_id, proposed_events, validator)
    print(f"      Validation produced {len(scheduled)} scheduled events and {len(unscheduled)} unscheduled events.")

    scheduled.sort(key=lambda item: item.start)
    if output_dir is not None:
        print("      Exporting CSV, JSON, HTML, and ICS outputs...")
        export_schedule_csv(scheduled, output_dir / "scheduled_plan.csv")
        export_unscheduled_csv(unscheduled, output_dir / "unscheduled_plan.csv")
        export_json_bundle(scheduled, unscheduled, output_dir / "schedule_bundle.json")
        export_html(scheduled, unscheduled, output_dir / "personalized_plan.html", start_date, end_date)
        export_ics(scheduled, output_dir / "personalized_plan.ics")
    return scheduled, unscheduled


def apply_schedule_events(
    activity_by_id: dict[str, Activity],
    proposed_events: list[dict[str, str]],
    validator: ScheduleValidator,
    scheduled_so_far: list[ScheduledEvent] | None = None,
) -> tuple[list[ScheduledEvent], list[dict]]:
    accepted_events: list[ScheduledEvent] = []
    unscheduled_items: list[dict] = []
    scheduled = list(scheduled_so_far or [])
    invalid_count = 0

    for proposed_event in proposed_events:
        activity_id = proposed_event.get("activity_id", "")
        proposed_start = proposed_event.get("start", "")
        scheduled_activity = activity_by_id.get(activity_id)
        if scheduled_activity is None:
            unscheduled_items.append(
                build_unscheduled_item(
                    None,
                    activity_id,
                    proposed_start,
                    "Activity id was not found in the action plan.",
                )
            )
            invalid_count += 1
            continue

        event, error = validator.materialize_event(
            scheduled_activity,
            proposed_start,
            scheduled,
        )
        if error:
            unscheduled_items.append(build_unscheduled_item(scheduled_activity, activity_id, proposed_start, error))
            invalid_count += 1
            continue
        if event is None:
            unscheduled_items.append(
                build_unscheduled_item(
                    scheduled_activity,
                    activity_id,
                    proposed_start,
                    "Scheduled event could not be materialized.",
                )
            )
            invalid_count += 1
            continue
        accepted_events.append(event)
        scheduled.append(event)
    print(f"      Accepted {len(accepted_events)} decisions and rejected/unscheduled {invalid_count}.")
    return accepted_events, unscheduled_items


def build_activities_payload(activities: list[Activity]) -> list[dict]:
    items = [
        {
            "id": activity.id,
            "title": activity.title,
            "category": activity.category,
            "priority": activity.priority,
            "duration_minutes": activity.duration_minutes,
            "frequency": activity.frequency.to_dict(),
            "facilitator_role": activity.facilitator_role,
            "location": activity.location,
            "remote_allowed": activity.remote_allowed,
            "equipment_required": list(activity.equipment_required),
        }
        for activity in activities
    ]
    items.sort(key=lambda item: (-item["priority"], item["id"]))
    return items


def build_unscheduled_item(
    activity: Activity | None,
    activity_id: str,
    proposed_start: str,
    reason: str,
) -> dict:
    return {
        "activity_id": activity_id,
        "activity_title": activity.title if activity is not None else "",
        "proposed_start": proposed_start,
        "reason": reason,
        "skip_adjustment": activity.skip_adjustment if activity is not None else "",
    }


__all__ = ["load_rows", "run_scheduler"]
