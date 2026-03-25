from __future__ import annotations

from typing import Any, Callable, Iterable

from health_scheduler.domain.activities.activity import Activity
from health_scheduler.domain.activities.consultation_activity import ConsultationActivity
from health_scheduler.domain.activities.fitness_activity import FitnessActivity
from health_scheduler.domain.activities.food_activity import FoodActivity
from health_scheduler.domain.activities.medication_activity import MedicationActivity
from health_scheduler.domain.activities.therapy_activity import TherapyActivity
from health_scheduler.domain.enums.activity_category import ActivityCategory


def create_fitness_activity(**kwargs: Any) -> FitnessActivity:
    return FitnessActivity(**kwargs)


def create_food_activity(**kwargs: Any) -> FoodActivity:
    return FoodActivity(**kwargs)


def create_medication_activity(**kwargs: Any) -> MedicationActivity:
    return MedicationActivity(**kwargs)


def create_therapy_activity(**kwargs: Any) -> TherapyActivity:
    return TherapyActivity(**kwargs)


def create_consultation_activity(**kwargs: Any) -> ConsultationActivity:
    return ConsultationActivity(**kwargs)


def parse_fitness_activity(payload: dict[str, Any]) -> FitnessActivity:
    return FitnessActivity.from_payload(payload)


def parse_food_activity(payload: dict[str, Any]) -> FoodActivity:
    return FoodActivity.from_payload(payload)


def parse_medication_activity(payload: dict[str, Any]) -> MedicationActivity:
    return MedicationActivity.from_payload(payload)


def parse_therapy_activity(payload: dict[str, Any]) -> TherapyActivity:
    return TherapyActivity.from_payload(payload)


def parse_consultation_activity(payload: dict[str, Any]) -> ConsultationActivity:
    return ConsultationActivity.from_payload(payload)


def normalize_category(category: ActivityCategory | str) -> ActivityCategory:
    return ActivityCategory(category)


CREATE_DISPATCH: dict[ActivityCategory, Callable[..., Activity]] = {
    FitnessActivity.CATEGORY: create_fitness_activity,
    FoodActivity.CATEGORY: create_food_activity,
    MedicationActivity.CATEGORY: create_medication_activity,
    TherapyActivity.CATEGORY: create_therapy_activity,
    ConsultationActivity.CATEGORY: create_consultation_activity,
}

PARSE_DISPATCH: dict[ActivityCategory, Callable[[dict[str, Any]], Activity]] = {
    FitnessActivity.CATEGORY: parse_fitness_activity,
    FoodActivity.CATEGORY: parse_food_activity,
    MedicationActivity.CATEGORY: parse_medication_activity,
    TherapyActivity.CATEGORY: parse_therapy_activity,
    ConsultationActivity.CATEGORY: parse_consultation_activity,
}


def create_activity(category: ActivityCategory | str, **kwargs: Any) -> Activity:
    return CREATE_DISPATCH[normalize_category(category)](**kwargs)


def parse_activity(payload: dict[str, Any]) -> Activity:
    return PARSE_DISPATCH[normalize_category(payload["category"])](payload)


def parse_activities(payloads: Iterable[dict[str, Any]]) -> list[Activity]:
    return [parse_activity(payload) for payload in payloads]


def serialize_activities_for_csv(activities: Iterable[Activity]) -> list[dict[str, Any]]:
    return [activity.to_csv_row() for activity in activities]
