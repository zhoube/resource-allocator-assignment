from __future__ import annotations

import argparse
import random

from health_scheduler.config.paths import ACTION_PLAN_CSV, ACTION_PLAN_JSON, ACTIVITY_CATALOG_JSON, ensure_directories
from health_scheduler.domain.enums.activity_field import activity_fieldnames
from health_scheduler.io.storage.files import read_json, write_csv, write_json
from health_scheduler.services.generation.action_plan_builder import DEFAULT_ACTION_PLAN_SIZE, build_action_plan
from health_scheduler.services.generation.activity_factory import parse_activities, serialize_activities_for_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Choose a realistic action plan scenario from the saved activity catalog.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--plan-size", type=int, default=DEFAULT_ACTION_PLAN_SIZE)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_directories()
    if not ACTIVITY_CATALOG_JSON.exists():
        raise FileNotFoundError(f"Activity catalog not found at {ACTIVITY_CATALOG_JSON}. Run generate_activities first.")

    activity_catalog = parse_activities(read_json(ACTIVITY_CATALOG_JSON))
    action_plan = build_action_plan(activity_catalog, args.plan_size, random.Random(args.seed))

    write_json(ACTION_PLAN_JSON, [activity.to_dict() for activity in action_plan])
    write_csv(ACTION_PLAN_CSV, serialize_activities_for_csv(action_plan), activity_fieldnames())
    print(f"Selected {len(action_plan)} activities into {ACTION_PLAN_JSON.parent}.")


if __name__ == "__main__":
    main()
