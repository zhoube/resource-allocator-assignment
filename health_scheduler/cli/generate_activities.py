from __future__ import annotations

import argparse
import random

from health_scheduler.config.paths import ACTIVITY_CATALOG_CSV, ACTIVITY_CATALOG_JSON, ensure_directories
from health_scheduler.domain.enums.activity_field import activity_fieldnames
from health_scheduler.io.storage.files import write_csv, write_json
from health_scheduler.services.generation.activity_catalog_builder import (
    CATEGORY_TARGETS,
    CURATED_SCENARIO_ACTIVITY_COUNT,
    generate_activity_catalog,
)
from health_scheduler.services.generation.activity_factory import serialize_activities_for_csv


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the activity catalog.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--catalog-size", type=int, default=sum(CATEGORY_TARGETS.values()) + CURATED_SCENARIO_ACTIVITY_COUNT)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    ensure_directories()
    activity_catalog = generate_activity_catalog(random.Random(args.seed))
    if args.catalog_size < len(activity_catalog):
        activity_catalog = activity_catalog[: args.catalog_size]

    write_json(ACTIVITY_CATALOG_JSON, [activity.to_dict() for activity in activity_catalog])
    write_csv(ACTIVITY_CATALOG_CSV, serialize_activities_for_csv(activity_catalog), activity_fieldnames())
    print(f"Generated {len(activity_catalog)} activities in {ACTIVITY_CATALOG_JSON.parent}.")


if __name__ == "__main__":
    main()
