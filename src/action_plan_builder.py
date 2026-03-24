from __future__ import annotations

import random

from activity_factory import parse_activities
from entities.activities.activity import Activity
from src.enums.activity_category import ActivityCategory

ACTION_PLAN_TARGETS = {
    ActivityCategory.FITNESS: 2,
    ActivityCategory.FOOD: 2,
    ActivityCategory.MEDICATION: 2,
    ActivityCategory.THERAPY: 2,
    ActivityCategory.CONSULTATION: 2,
}


def assign_backups(activities: list[Activity]) -> None:
    by_category: dict[str, list[Activity]] = {}
    for activity in activities:
        by_category.setdefault(activity.category, []).append(activity)
    for activity in activities:
        candidates = [
            item
            for item in by_category[activity.category]
            if item.id != activity.id and item.duration_minutes <= activity.duration_minutes and item.priority <= activity.priority + 6
        ]
        candidates.sort(key=lambda item: (item.resource_pool != "self", bool(item.equipment_required), item.duration_minutes, item.priority))
        activity.backup_activity_ids = [item.id for item in candidates[:2]]


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

    if plan_size < len(selected_catalog_items):
        selected_catalog_items = selected_catalog_items[:plan_size]

    action_plan = parse_activities([activity.to_dict() for activity in selected_catalog_items])
    assign_backups(action_plan)
    return action_plan[:plan_size] if plan_size < len(action_plan) else action_plan
