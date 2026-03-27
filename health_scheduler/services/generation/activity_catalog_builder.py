from __future__ import annotations

import random
from itertools import count

from health_scheduler.domain.activities.activity import Activity
from health_scheduler.domain.activities.frequency import Frequency
from health_scheduler.domain.enums.activity_category import ActivityCategory
from health_scheduler.services.generation.activity_factory import create_activity
from health_scheduler.services.generation.activity_generator import create_random_activity

CATEGORY_TARGETS = {
    ActivityCategory.FITNESS: 35,
    ActivityCategory.FOOD: 25,
    ActivityCategory.MEDICATION: 20,
    ActivityCategory.THERAPY: 20,
    ActivityCategory.CONSULTATION: 20,
}

CURATED_SCENARIO_ACTIVITY_IDS = (
    "activity_121",
    "activity_122",
    "activity_123",
    "activity_124",
    "activity_125",
    "activity_126",
)


def build_curated_scenario_activities() -> list[Activity]:
    return [
        create_activity(
            category=ActivityCategory.MEDICATION,
            id="activity_121",
            title="Morning Blood Pressure + Medication Routine",
            priority=98,
            duration_minutes=15,
            details="Check blood pressure before the morning dose, take the prescribed medication, and log both readings for clinician review.",
            frequency=Frequency(times=1, period="day"),
            facilitator_role="self_guided",
            location="home",
            remote_allowed=False,
            equipment_required=["blood_pressure_cuff"],
            prep_required=["Medication organizer refilled", "Blood pressure cuff placed near medication"],
            backup_activity_ids=[],
            skip_adjustment="If missed, record the reason and resume the next scheduled dose without doubling medication.",
            metrics=["blood_pressure_reading", "dose_taken", "symptom_flag"],
        ),
        create_activity(
            category=ActivityCategory.FITNESS,
            id="activity_122",
            title="Post-Meal Walk - Glucose Control",
            priority=83,
            duration_minutes=20,
            details="Take a brisk walk after a main meal to support glucose control, blood pressure management, and daily activity consistency.",
            frequency=Frequency(times=4, period="week"),
            facilitator_role="self_guided",
            location="park",
            remote_allowed=False,
            equipment_required=[],
            prep_required=["Walking shoes ready", "Last meal time logged"],
            backup_activity_ids=[],
            skip_adjustment="Move the session to the next available daylight slot within 24 hours and record the reason if skipped.",
            metrics=["steps", "walk_minutes", "post_meal_energy"],
        ),
        create_activity(
            category=ActivityCategory.CONSULTATION,
            id="activity_123",
            title="Dietitian Consultation - Hypertension Meal Plan",
            priority=92,
            duration_minutes=45,
            details="Review sodium intake, meal timing, grocery habits, and adherence to a cardiometabolic-friendly meal plan.",
            frequency=Frequency(times=2, period="month"),
            facilitator_role="dietitian",
            location="clinic",
            remote_allowed=True,
            equipment_required=[],
            prep_required=["3-day food log completed", "Recent blood pressure summary available"],
            backup_activity_ids=[],
            skip_adjustment="Rebook within the same fortnight and send the meal log ahead of the replacement session.",
            metrics=["sodium_target_met", "meal_adherence_score", "action_items_created"],
        ),
        create_activity(
            category=ActivityCategory.CONSULTATION,
            id="activity_124",
            title="Health Coaching Review - Blood Pressure Check-In",
            priority=88,
            duration_minutes=30,
            details="Review home blood pressure trends, symptom notes, walking adherence, and barriers to maintaining the care plan.",
            frequency=Frequency(times=2, period="month"),
            facilitator_role="health_coach",
            location="home",
            remote_allowed=True,
            equipment_required=[],
            prep_required=["Blood pressure log updated", "Questions prepared for coaching call"],
            backup_activity_ids=[],
            skip_adjustment="Reschedule within 7 days and keep logging readings until the follow-up is completed.",
            metrics=["blood_pressure_reading", "habit_adherence_score", "action_items_created"],
        ),
        create_activity(
            category=ActivityCategory.FOOD,
            id="activity_125",
            title="Low-Sodium Dinner Prep - DASH Support",
            priority=82,
            duration_minutes=30,
            details="Prepare a high-fiber, lower-sodium dinner built around vegetables, lean protein, and portion-controlled carbohydrates.",
            frequency=Frequency(times=3, period="week"),
            facilitator_role="self_guided",
            location="home",
            remote_allowed=False,
            equipment_required=[],
            prep_required=["Groceries stocked", "Dinner ingredients thawed"],
            backup_activity_ids=[],
            skip_adjustment="Replace with the closest low-sodium home meal and record the substitution in the nutrition log.",
            metrics=["sodium_estimate_mg", "vegetable_servings", "meal_finish_time"],
        ),
        create_activity(
            category=ActivityCategory.THERAPY,
            id="activity_126",
            title="Evening Breathing Reset - Blood Pressure Support",
            priority=84,
            duration_minutes=15,
            details="Complete guided slow breathing in the evening to lower stress load, support sleep onset, and reinforce blood pressure control habits.",
            frequency=Frequency(times=3, period="week"),
            facilitator_role="self_guided",
            location="home",
            remote_allowed=False,
            equipment_required=[],
            prep_required=["Phone on silent", "Lights dimmed"],
            backup_activity_ids=[],
            skip_adjustment="Move to the next available evening slot in the same week and note any symptoms if it is skipped.",
            metrics=["session_minutes", "stress_score_post", "sleep_latency"],
        ),
    ]


CURATED_SCENARIO_ACTIVITY_COUNT = len(CURATED_SCENARIO_ACTIVITY_IDS)


def generate_activity_catalog(rng: random.Random) -> list[Activity]:
    activities: list[Activity] = []
    used_titles: set[str] = set()
    id_counter = count(1)
    for category, target in CATEGORY_TARGETS.items():
        for _ in range(target):
            activities.append(create_random_activity(category, f"activity_{next(id_counter):03d}", rng, used_titles))
    activities.extend(build_curated_scenario_activities())
    return activities
