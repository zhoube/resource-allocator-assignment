from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date, time

from health_scheduler.domain.enums.location import Location
from health_scheduler.domain.enums.roles import AlliedHealthRole
from health_scheduler.utils.datetime_utils import format_compact_range, format_weekday_pattern

@dataclass(slots=True)
class AlliedHealth:
    resource_id: str
    name: str
    role: str
    days: list[int]
    start: time
    end: time
    location: str
    remote_supported: bool

    def to_csv_row(self) -> dict:
        return {
            "resource_id": self.resource_id,
            "name": self.name,
            "role": self.role,
            "location": self.location,
            "remote_supported": str(self.remote_supported).lower(),
            "weekday_pattern": format_weekday_pattern(self.days),
            "available_ranges": format_compact_range(self.start, self.end),
            "notes": "",
        }

    @classmethod
    def defaults(cls) -> list[AlliedHealth]:
        return [
            cls("allied_01", "Aaron Lee", AlliedHealthRole.PHYSIOTHERAPIST.value, [0, 2, 4], time(8, 0), time(12, 0), Location.CLINIC.value, True),
            cls("allied_02", "Chloe Ng", AlliedHealthRole.DIETITIAN.value, [1, 3], time(10, 0), time(17, 0), Location.CLINIC.value, True),
            cls("allied_03", "Ben Kumar", AlliedHealthRole.EXERCISE_PHYSIOLOGIST.value, [0, 2], time(17, 0), time(20, 30), Location.GYM.value, True),
            cls("allied_04", "Felicia Ong", AlliedHealthRole.HEALTH_COACH.value, [1, 4], time(18, 0), time(20, 30), Location.HOME.value, True),
            cls("allied_05", "Naomi Tan", AlliedHealthRole.OCCUPATIONAL_THERAPIST.value, [2], time(9, 0), time(13, 0), Location.CLINIC.value, True),
            cls("allied_06", "Marcus Ho", AlliedHealthRole.STRENGTH_COACH.value, [1, 3], time(7, 0), time(10, 0), Location.GYM.value, True),
        ]

    @classmethod
    def generate_rows(cls, start_date: date, end_date: date, rng: random.Random) -> list[dict]:
        return [provider.to_csv_row() for provider in cls.defaults()]
