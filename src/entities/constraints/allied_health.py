from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date, datetime, time

from common import daterange

from src.enums.location import Location
from src.enums.roles import AlliedHealthRole

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

    SKIP_PROBABILITY = 0.06

    def generate_availability_rows(self, start_date: date, end_date: date, rng: random.Random) -> list[dict]:
        rows: list[dict] = []
        for day in daterange(start_date, end_date):
            if day.weekday() not in self.days or rng.random() < self.SKIP_PROBABILITY:
                continue
            rows.append(
                {
                    "resource_id": self.resource_id,
                    "name": self.name,
                    "role": self.role,
                    "start": datetime.combine(day, self.start).isoformat(),
                    "end": datetime.combine(day, self.end).isoformat(),
                    "location": self.location,
                    "remote_supported": str(self.remote_supported).lower(),
                }
            )
        return rows

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
        rows: list[dict] = []
        for provider in cls.defaults():
            rows.extend(provider.generate_availability_rows(start_date, end_date, rng))
        return rows
