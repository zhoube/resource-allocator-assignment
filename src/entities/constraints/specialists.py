from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date, datetime, time

from common import daterange

from enums.location import Location
from enums.roles import SpecialistRole

@dataclass(slots=True)
class Specialists:
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
    def defaults(cls) -> list[Specialists]:
        return [
            cls("specialist_01", "Dr Miriam Tan", SpecialistRole.PRIMARY_CARE_PHYSICIAN.value, [1], time(9, 0), time(13, 0), Location.CLINIC.value, True),
            cls("specialist_02", "Dr Daniel Lim", SpecialistRole.ENDOCRINOLOGIST.value, [2], time(14, 0), time(18, 0), Location.CLINIC.value, True),
            cls("specialist_03", "Dr Aisha Rahman", SpecialistRole.CARDIOLOGIST.value, [3], time(9, 0), time(13, 0), Location.CLINIC.value, True),
            cls("specialist_04", "Dr Wei Chen", SpecialistRole.SLEEP_PHYSICIAN.value, [0, 3], time(18, 0), time(20, 30), Location.HOME.value, True),
            cls("specialist_05", "Dr Sofia Perera", SpecialistRole.SPORTS_PHYSICIAN.value, [4], time(10, 0), time(14, 0), Location.CLINIC.value, False),
            cls("specialist_06", "City Lab Team", SpecialistRole.LAB_TECHNICIAN.value, [0, 1, 2, 3, 4], time(8, 0), time(12, 0), Location.LAB.value, False),
        ]

    @classmethod
    def generate_rows(cls, start_date: date, end_date: date, rng: random.Random) -> list[dict]:
        rows: list[dict] = []
        for specialist in cls.defaults():
            rows.extend(specialist.generate_availability_rows(start_date, end_date, rng))
        return rows
