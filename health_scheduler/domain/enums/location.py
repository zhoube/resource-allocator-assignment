from __future__ import annotations

from enum import StrEnum


class Location(StrEnum):
    HOME = "home"
    OFFICE = "office"
    PARK = "park"
    GYM = "gym"
    CLINIC = "clinic"
    LAB = "lab"
    STUDIO = "studio"
    RECOVERY_CENTER = "recovery_center"
    COMMUTE = "commute"
    CITY = "city"
    TRAVEL = "travel"
    REMOTE = "remote"

    @classmethod
    def has_value(cls, value: str) -> bool:
        return value in cls._value2member_map_


class TravelFriendlyLocation(StrEnum):
    PARK = "park"
    OFFICE = "office"
    TRAVEL = "travel"

    @classmethod
    def has_value(cls, value: str) -> bool:
        return value in cls._value2member_map_
