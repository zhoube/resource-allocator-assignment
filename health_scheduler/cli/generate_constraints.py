from __future__ import annotations

import argparse
import random
from datetime import date

from health_scheduler.config.paths import (
    ALLIED_HEALTH_CSV,
    CLIENT_SCHEDULE_CSV,
    CONSTRAINTS_BUNDLE_JSON,
    EQUIPMENT_CSV,
    SPECIALISTS_CSV,
    TRAVEL_PLANS_CSV,
    ensure_directories,
)
from health_scheduler.config.settings import DEFAULT_MONTHS, DEFAULT_START_DATE
from health_scheduler.io.storage.files import write_csv, write_json
from health_scheduler.services.generation.constraints_builder import generate_constraints
from health_scheduler.utils.datetime_utils import add_months


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the scheduling constraints.")
    parser.add_argument("--start-date", default=DEFAULT_START_DATE.isoformat())
    parser.add_argument("--months", type=int, default=DEFAULT_MONTHS)
    parser.add_argument("--seed", type=int, default=42)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    start_date = date.fromisoformat(args.start_date)
    end_date = add_months(start_date, args.months)
    ensure_directories()

    constraints = generate_constraints(start_date, end_date, random.Random(args.seed))

    write_csv(CLIENT_SCHEDULE_CSV, constraints["client_schedule"], list(constraints["client_schedule"][0].keys()))
    write_csv(TRAVEL_PLANS_CSV, constraints["travel_plans"], list(constraints["travel_plans"][0].keys()))
    write_csv(SPECIALISTS_CSV, constraints["specialists"], list(constraints["specialists"][0].keys()))
    write_csv(ALLIED_HEALTH_CSV, constraints["allied_health"], list(constraints["allied_health"][0].keys()))
    write_csv(EQUIPMENT_CSV, constraints["equipment"], list(constraints["equipment"][0].keys()))
    write_json(
        CONSTRAINTS_BUNDLE_JSON,
        {
            "planning_horizon": {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
            **constraints,
        },
    )
    print(f"Generated scheduling constraints in {CLIENT_SCHEDULE_CSV.parent}.")


if __name__ == "__main__":
    main()
