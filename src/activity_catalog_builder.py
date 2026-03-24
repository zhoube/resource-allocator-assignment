from __future__ import annotations

import random
from itertools import count

from action_plan_builder import assign_backups
from activity_generator import create_random_activity
from entities.activities.activity import Activity
from src.enums.activity_category import ActivityCategory

CATEGORY_TARGETS = {
    ActivityCategory.FITNESS: 35,
    ActivityCategory.FOOD: 25,
    ActivityCategory.MEDICATION: 20,
    ActivityCategory.THERAPY: 20,
    ActivityCategory.CONSULTATION: 20,
}


def generate_activity_catalog(rng: random.Random) -> list[Activity]:
    activities: list[Activity] = []
    used_titles: set[str] = set()
    id_counter = count(1)
    for category, target in CATEGORY_TARGETS.items():
        for _ in range(target):
            activities.append(create_random_activity(category, f"activity_{next(id_counter):03d}", rng, used_titles))
    assign_backups(activities)
    return activities
