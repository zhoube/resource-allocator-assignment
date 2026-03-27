from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path

from health_scheduler.config.paths import (
    ACTION_PLAN_JSON,
    ACTIVITY_CATALOG_JSON,
    ALLIED_HEALTH_CSV,
    CLIENT_SCHEDULE_CSV,
    EQUIPMENT_CSV,
    OUTPUTS_DIR,
    PATIENT_PROFILE_MD,
    SPECIALISTS_CSV,
    TRAVEL_PLANS_CSV,
    ensure_directories,
)
from health_scheduler.config.settings import DEFAULT_MONTHS, DEFAULT_START_DATE
from health_scheduler.io.storage.files import read_json
from health_scheduler.services.generation.activity_factory import parse_activities
from health_scheduler.services.scheduling.scheduler import load_rows, run_scheduler
from health_scheduler.utils.datetime_utils import add_months


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Read the saved activities, constraints, and action plan, then run scheduling.")
    parser.add_argument("--start-date", default=DEFAULT_START_DATE.isoformat())
    parser.add_argument("--months", type=int, default=DEFAULT_MONTHS)
    return parser.parse_args()


def require_paths(paths: list[Path]) -> None:
    missing = [path for path in paths if not path.exists()]
    if missing:
        formatted = "\n".join(str(path) for path in missing)
        raise FileNotFoundError(f"Required input files are missing:\n{formatted}")


def main() -> None:
    args = parse_args()
    start_date = date.fromisoformat(args.start_date)
    end_date = add_months(start_date, args.months)
    ensure_directories()
    print(f"[1/5] Preparing run window from {start_date.isoformat()} to {end_date.isoformat()}...")

    required_paths = [
        ACTIVITY_CATALOG_JSON,
        ACTION_PLAN_JSON,
        CLIENT_SCHEDULE_CSV,
        TRAVEL_PLANS_CSV,
        SPECIALISTS_CSV,
        ALLIED_HEALTH_CSV,
        EQUIPMENT_CSV,
        PATIENT_PROFILE_MD,
    ]
    require_paths(required_paths)
    print("[2/5] Loading catalog, action plan, and constraint files...")

    activity_catalog = parse_activities(read_json(ACTIVITY_CATALOG_JSON))
    action_plan = parse_activities(read_json(ACTION_PLAN_JSON))
    catalog_ids = {activity.id for activity in activity_catalog}
    missing_action_plan_ids = [activity.id for activity in action_plan if activity.id not in catalog_ids]
    if missing_action_plan_ids:
        raise ValueError(f"Action plan contains activities not found in the catalog: {', '.join(missing_action_plan_ids)}")
    print(f"      Loaded {len(activity_catalog)} catalog activities and {len(action_plan)} action plan activities.")
    patient_profile_markdown = PATIENT_PROFILE_MD.read_text(encoding="utf-8")

    print("[3/5] Running scheduler...")
    scheduled, unscheduled = run_scheduler(
        action_plan,
        start_date,
        end_date,
        load_rows(CLIENT_SCHEDULE_CSV),
        load_rows(TRAVEL_PLANS_CSV, with_remote=True),
        load_rows(SPECIALISTS_CSV, with_remote=True),
        load_rows(ALLIED_HEALTH_CSV, with_remote=True),
        load_rows(EQUIPMENT_CSV),
        patient_profile_markdown=patient_profile_markdown,
        output_dir=OUTPUTS_DIR,
    )
    print("[5/5] Scheduling finished.")
    print(
        f"Read {len(activity_catalog)} catalog activities, {len(action_plan)} action plan activities, "
        f"and scheduled {len(scheduled)} occurrences with {len(unscheduled)} unscheduled."
    )


if __name__ == "__main__":
    main()
