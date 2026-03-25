from __future__ import annotations

import random
from itertools import count

from health_scheduler.domain.activities.activity import Activity
from health_scheduler.domain.enums.activity_category import ActivityCategory
from health_scheduler.services.generation.activity_generator import create_random_activity

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
    return activities
