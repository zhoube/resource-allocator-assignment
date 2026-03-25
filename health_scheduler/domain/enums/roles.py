from __future__ import annotations

from enum import StrEnum


class SpecialistRole(StrEnum):
    PRIMARY_CARE_PHYSICIAN = "primary_care_physician"
    ENDOCRINOLOGIST = "endocrinologist"
    CARDIOLOGIST = "cardiologist"
    SLEEP_PHYSICIAN = "sleep_physician"
    SPORTS_PHYSICIAN = "sports_physician"
    LAB_TECHNICIAN = "lab_technician"
    OPHTHALMOLOGIST = "ophthalmologist"

    @classmethod
    def has_value(cls, value: str) -> bool:
        return value in cls._value2member_map_


class AlliedHealthRole(StrEnum):
    PHYSIOTHERAPIST = "physiotherapist"
    DIETITIAN = "dietitian"
    EXERCISE_PHYSIOLOGIST = "exercise_physiologist"
    HEALTH_COACH = "health_coach"
    OCCUPATIONAL_THERAPIST = "occupational_therapist"
    SPEECH_THERAPIST = "speech_therapist"
    STRENGTH_COACH = "strength_coach"

    @classmethod
    def has_value(cls, value: str) -> bool:
        return value in cls._value2member_map_
