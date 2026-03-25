from __future__ import annotations

import random

from health_scheduler.domain.activities.activity import Activity
from health_scheduler.domain.enums.activity_category import ActivityCategory
from health_scheduler.services.generation.activity_factory import parse_activities

DEFAULT_ACTION_PLAN_SIZE = 2
ACTION_PLAN_TARGETS = {
    ActivityCategory.FITNESS: 1,
    ActivityCategory.FOOD: 1,
    ActivityCategory.MEDICATION: 1,
    ActivityCategory.THERAPY: 1,
    ActivityCategory.CONSULTATION: 1,
}


def build_action_plan(activity_catalog: list[Activity], plan_size: int, rng: random.Random) -> list[Activity]:
    selected_catalog_items: list[Activity] = []
    by_category: dict[ActivityCategory, list[Activity]] = {}
    for activity in activity_catalog:
        by_category.setdefault(ActivityCategory(activity.category), []).append(activity)

    for items in by_category.values():
        items.sort(key=lambda item: (-item.priority, -item.constraint_weight(), item.duration_minutes, item.title))

    for category, target in ACTION_PLAN_TARGETS.items():
        candidates = by_category.get(category, [])
        if not candidates:
            continue
        shortlist = candidates[: max(target * 3, target)]
        chosen = shortlist if len(shortlist) <= target else rng.sample(shortlist, target)
        selected_catalog_items.extend(sorted(chosen, key=lambda item: (-item.priority, -item.constraint_weight(), item.duration_minutes, item.title)))

    if plan_size > len(selected_catalog_items):
        selected_ids = {activity.id for activity in selected_catalog_items}
        remaining = [
            activity
            for activity in sorted(
                activity_catalog,
                key=lambda item: (-item.priority, -item.constraint_weight(), item.duration_minutes, item.title),
            )
            if activity.id not in selected_ids
        ]
        selected_catalog_items.extend(remaining[: plan_size - len(selected_catalog_items)])

    selected_catalog_items.sort(key=lambda item: (-item.priority, -item.constraint_weight(), item.duration_minutes, item.title))

    if plan_size < len(selected_catalog_items):
        selected_catalog_items = selected_catalog_items[:plan_size]

    action_plan = parse_activities([activity.to_dict() for activity in selected_catalog_items])
    return action_plan[:plan_size] if plan_size < len(action_plan) else action_plan
