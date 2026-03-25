from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date, time

from health_scheduler.domain.enums.location import Location
from health_scheduler.domain.enums.roles import SpecialistRole
from health_scheduler.utils.datetime_utils import format_compact_range, format_weekday_pattern

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
        return [specialist.to_csv_row() for specialist in cls.defaults()]
