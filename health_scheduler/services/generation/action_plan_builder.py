from __future__ import annotations

import random
from dataclasses import dataclass

from health_scheduler.domain.activities.activity import Activity
from health_scheduler.domain.enums.activity_category import ActivityCategory
from health_scheduler.services.generation.activity_factory import parse_activities

DEFAULT_ACTION_PLAN_SIZE = 2


@dataclass(frozen=True)
class ScenarioSlot:
    name: str
    categories: tuple[ActivityCategory, ...]
    preferred_roles: tuple[str, ...] = ()
    preferred_locations: tuple[str, ...] = ()
    preferred_periods: tuple[str, ...] = ()
    include_keywords: tuple[str, ...] = ()
    exclude_keywords: tuple[str, ...] = ()
    allow_same_title_family: bool = False


REAL_WORLD_SCENARIO_SLOTS: tuple[ScenarioSlot, ...] = (
    ScenarioSlot(
        name="core_medication",
        categories=(ActivityCategory.MEDICATION,),
        preferred_roles=("self_guided",),
        preferred_locations=("home",),
        preferred_periods=("day",),
        include_keywords=("medication", "prescription"),
    ),
    ScenarioSlot(
        name="physician_review",
        categories=(ActivityCategory.CONSULTATION,),
        preferred_roles=("primary_care_physician",),
        preferred_locations=("clinic",),
        preferred_periods=("month",),
        include_keywords=("review", "follow-up", "check-in"),
    ),
    ScenarioSlot(
        name="lab_monitoring",
        categories=(ActivityCategory.CONSULTATION,),
        preferred_roles=("lab_technician",),
        preferred_locations=("lab",),
        preferred_periods=("month",),
        include_keywords=("lab", "testing"),
    ),
    ScenarioSlot(
        name="movement_routine",
        categories=(ActivityCategory.FITNESS,),
        preferred_roles=("self_guided", "physiotherapist", "exercise_physiologist"),
        preferred_locations=("home", "park", "gym"),
        preferred_periods=("week",),
        include_keywords=("walk", "yoga", "mobility", "zone", "strength", "recovery"),
    ),
    ScenarioSlot(
        name="stress_or_sleep_therapy",
        categories=(ActivityCategory.THERAPY,),
        preferred_roles=("self_guided", "health_coach"),
        preferred_locations=("home",),
        preferred_periods=("week",),
        include_keywords=("breathing", "stress", "sleep", "recovery"),
    ),
    ScenarioSlot(
        name="nutrition_habit",
        categories=(ActivityCategory.FOOD,),
        preferred_roles=("self_guided", "dietitian"),
        preferred_locations=("home",),
        preferred_periods=("week",),
        include_keywords=("balanced", "protein", "recovery", "metabolic", "smoothie"),
    ),
    ScenarioSlot(
        name="supplement_support",
        categories=(ActivityCategory.MEDICATION,),
        preferred_roles=("self_guided",),
        preferred_locations=("home", "travel"),
        preferred_periods=("day",),
        include_keywords=("vitamin", "magnesium", "supplement"),
    ),
    ScenarioSlot(
        name="adherence_review",
        categories=(ActivityCategory.MEDICATION,),
        preferred_roles=("self_guided", "health_coach"),
        preferred_locations=("home",),
        preferred_periods=("month",),
        include_keywords=("supply check", "medication check", "refill"),
        exclude_keywords=("office",),
    ),
    ScenarioSlot(
        name="nutrition_consult",
        categories=(ActivityCategory.CONSULTATION,),
        preferred_roles=("dietitian",),
        preferred_locations=("clinic", "home"),
        preferred_periods=("month",),
        include_keywords=("dietitian", "consultation", "follow-up", "plan tuning"),
    ),
    ScenarioSlot(
        name="coaching_support",
        categories=(ActivityCategory.CONSULTATION, ActivityCategory.THERAPY, ActivityCategory.FITNESS),
        preferred_roles=("health_coach", "sleep_physician", "physiotherapist"),
        preferred_locations=("home", "clinic"),
        preferred_periods=("week", "month"),
        include_keywords=("sleep", "coaching", "stress", "recovery", "breathing", "follow-up"),
    ),
)


def build_action_plan(activity_catalog: list[Activity], plan_size: int, rng: random.Random) -> list[Activity]:
    ordered_catalog = sorted(
        activity_catalog,
        key=lambda item: (-item.priority, -item.constraint_weight(), item.duration_minutes, item.title),
    )
    selected_catalog_items: list[Activity] = []
    selected_ids: set[str] = set()

    for slot in REAL_WORLD_SCENARIO_SLOTS:
        candidate = select_best_candidate(ordered_catalog, slot, selected_catalog_items, selected_ids, rng)
        if candidate is None:
            continue
        selected_catalog_items.append(candidate)
        selected_ids.add(candidate.id)
        if len(selected_catalog_items) >= plan_size:
            break

    if len(selected_catalog_items) < plan_size:
        fill_with_supporting_activities(ordered_catalog, selected_catalog_items, selected_ids, plan_size, rng)

    selected_catalog_items.sort(key=lambda item: (-item.priority, -item.constraint_weight(), item.duration_minutes, item.title))
    if plan_size < len(selected_catalog_items):
        selected_catalog_items = selected_catalog_items[:plan_size]

    action_plan = parse_activities([activity.to_dict() for activity in selected_catalog_items])
    return action_plan


def select_best_candidate(
    ordered_catalog: list[Activity],
    slot: ScenarioSlot,
    selected_catalog_items: list[Activity],
    selected_ids: set[str],
    rng: random.Random,
) -> Activity | None:
    scored_candidates: list[tuple[tuple[int, int, int, int, str], float, Activity]] = []
    for activity in ordered_catalog:
        if activity.id in selected_ids:
            continue
        score = score_activity_for_slot(activity, slot, selected_catalog_items)
        if score is None:
            continue
        tie_breaker = rng.random()
        sort_key = (
            int(score * 100),
            activity.priority,
            -activity.constraint_weight(),
            -activity.duration_minutes,
            activity.title,
        )
        scored_candidates.append((sort_key, tie_breaker, activity))

    if not scored_candidates:
        return None

    scored_candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
    return scored_candidates[0][2]


def fill_with_supporting_activities(
    ordered_catalog: list[Activity],
    selected_catalog_items: list[Activity],
    selected_ids: set[str],
    plan_size: int,
    rng: random.Random,
) -> None:
    scenario_keywords = collect_scenario_keywords(selected_catalog_items)
    while len(selected_catalog_items) < plan_size:
        scored_candidates: list[tuple[tuple[int, int, int, int, str], float, Activity]] = []
        for activity in ordered_catalog:
            if activity.id in selected_ids:
                continue
            score = score_supporting_activity(activity, selected_catalog_items, scenario_keywords)
            tie_breaker = rng.random()
            sort_key = (
                int(score * 100),
                activity.priority,
                -activity.constraint_weight(),
                -activity.duration_minutes,
                activity.title,
            )
            scored_candidates.append((sort_key, tie_breaker, activity))

        if not scored_candidates:
            break

        scored_candidates.sort(key=lambda item: (item[0], item[1]), reverse=True)
        candidate = scored_candidates[0][2]
        selected_catalog_items.append(candidate)
        selected_ids.add(candidate.id)
        scenario_keywords.update(activity_keywords(candidate))


def score_activity_for_slot(activity: Activity, slot: ScenarioSlot, selected_catalog_items: list[Activity]) -> float | None:
    activity_category = ActivityCategory(activity.category)
    if activity_category not in slot.categories:
        return None

    keywords = activity_keywords(activity)
    if slot.exclude_keywords and keywords.intersection(slot.exclude_keywords):
        return None
    if not slot.allow_same_title_family and any(activity_title_family(activity) == activity_title_family(item) for item in selected_catalog_items):
        return None

    score = float(activity.priority)
    score += max(0, 8 - activity.constraint_weight())
    score += keyword_overlap_score(keywords, slot.include_keywords) * 6

    if slot.preferred_roles and activity.facilitator_role in slot.preferred_roles:
        score += 20
    if slot.preferred_locations and activity.location in slot.preferred_locations:
        score += 12
    if slot.preferred_periods and activity.frequency.period in slot.preferred_periods:
        score += 10

    if activity.facilitator_role == "self_guided":
        score += 3
    if activity.remote_allowed and activity.resource_pool != "self":
        score += 2

    if any(item.facilitator_role == activity.facilitator_role for item in selected_catalog_items):
        score -= 3
    if any(ActivityCategory(item.category) == activity_category for item in selected_catalog_items):
        score -= 1
    return score


def score_supporting_activity(activity: Activity, selected_catalog_items: list[Activity], scenario_keywords: set[str]) -> float:
    score = float(activity.priority)
    score += max(0, 8 - activity.constraint_weight())
    score += keyword_overlap_score(activity_keywords(activity), tuple(sorted(scenario_keywords))) * 3

    if activity.location in {"home", "clinic", "lab", "park"}:
        score += 4
    if activity.facilitator_role == "self_guided":
        score += 2
    if activity.frequency.period == "month":
        score += 1
    if any(activity_title_family(activity) == activity_title_family(item) for item in selected_catalog_items):
        score -= 12
    if any(item.facilitator_role == activity.facilitator_role for item in selected_catalog_items):
        score -= 2
    return score


def collect_scenario_keywords(activities: list[Activity]) -> set[str]:
    keywords: set[str] = set()
    for activity in activities:
        keywords.update(activity_keywords(activity))
    return keywords


def activity_keywords(activity: Activity) -> set[str]:
    parts = [
        activity.title.lower(),
        activity.details.lower(),
        activity.facilitator_role.lower(),
        activity.location.lower(),
        " ".join(metric.lower() for metric in activity.metrics),
    ]
    tokens = set()
    for part in parts:
        normalized = part.replace("-", " ").replace("/", " ").replace("_", " ")
        tokens.update(token for token in normalized.split() if len(token) > 2)
    return tokens


def keyword_overlap_score(activity_keywords_set: set[str], preferred_keywords: tuple[str, ...]) -> int:
    if not preferred_keywords:
        return 0
    score = 0
    normalized_blob = " ".join(sorted(activity_keywords_set))
    for preferred_keyword in preferred_keywords:
        keyword = preferred_keyword.lower()
        if " " in keyword:
            if keyword in normalized_blob:
                score += 1
        elif keyword in activity_keywords_set:
            score += 1
    return score


def activity_title_family(activity: Activity) -> str:
    return activity.title.split(" - ", 1)[0].strip().lower()
