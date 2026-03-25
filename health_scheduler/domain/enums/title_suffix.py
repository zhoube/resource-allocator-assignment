from __future__ import annotations

from enum import StrEnum

from .activity_category import ActivityCategory


class FitnessTitleSuffix(StrEnum):
    AEROBIC_BASE = "Aerobic Base"
    MOBILITY_RESET = "Mobility Reset"
    CORE_STABILITY = "Core Stability"
    RECOVERY_FOCUS = "Recovery Focus"
    JOINT_CARE = "Joint Care"


class FoodTitleSuffix(StrEnum):
    METABOLIC_SUPPORT = "Metabolic Support"
    RECOVERY_PLATE = "Recovery Plate"
    ENERGY_STABILIZER = "Energy Stabilizer"
    PROTEIN_REBUILD = "Protein Rebuild"
    GUT_SUPPORT = "Gut Support"


class MedicationTitleSuffix(StrEnum):
    DAILY_ADHERENCE = "Daily Adherence"
    TRAVEL_SAFE_PACK = "Travel-Safe Pack"
    MORNING_ROUTINE = "Morning Routine"
    EVENING_ROUTINE = "Evening Routine"
    MAINTENANCE_CYCLE = "Maintenance Cycle"


class TherapyTitleSuffix(StrEnum):
    RECOVERY_SESSION = "Recovery Session"
    INFLAMMATION_SUPPORT = "Inflammation Support"
    STRESS_RESET = "Stress Reset"
    SLEEP_SUPPORT = "Sleep Support"
    CIRCULATION_BOOST = "Circulation Boost"


class ConsultationTitleSuffix(StrEnum):
    PROGRESS_REVIEW = "Progress Review"
    CHECK_IN = "Check-In"
    PLAN_TUNING = "Plan Tuning"
    QUARTERLY_REVIEW = "Quarterly Review"
    FOLLOW_UP = "Follow-Up"


def title_suffixes_for_category(category: ActivityCategory | str) -> list[str]:
    category = ActivityCategory(category)
    if category == ActivityCategory.FITNESS:
        return [item.value for item in FitnessTitleSuffix]
    if category == ActivityCategory.FOOD:
        return [item.value for item in FoodTitleSuffix]
    if category == ActivityCategory.MEDICATION:
        return [item.value for item in MedicationTitleSuffix]
    if category == ActivityCategory.THERAPY:
        return [item.value for item in TherapyTitleSuffix]
    if category == ActivityCategory.CONSULTATION:
        return [item.value for item in ConsultationTitleSuffix]
    raise ValueError(f"Unsupported category for title suffixes: {category}")
