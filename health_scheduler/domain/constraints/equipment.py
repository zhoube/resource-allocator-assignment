from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date, datetime, time
from typing import ClassVar

from health_scheduler.domain.enums.equipment_type import EquipmentType
from health_scheduler.domain.enums.location import Location
from health_scheduler.utils.datetime_utils import daterange


@dataclass(slots=True)
class Equipment:
    resource_id: str
    equipment_type: str
    location: str
    start: time
    end: time

    SKIP_PROBABILITY: ClassVar[float] = 0.05

    def generate_availability_rows(self, start_date: date, end_date: date, rng: random.Random) -> list[dict]:
        rows: list[dict] = []
        for day in daterange(start_date, end_date):
            if day.weekday() == 6 and self.location in {Location.LAB.value, Location.CLINIC.value}:
                continue
            if rng.random() < self.SKIP_PROBABILITY and self.location not in {Location.HOME.value, Location.TRAVEL.value}:
                continue
            rows.append(
                {
                    "resource_id": self.resource_id,
                    "equipment_type": self.equipment_type,
                    "start": datetime.combine(day, self.start).isoformat(),
                    "end": datetime.combine(day, self.end).isoformat(),
                    "location": self.location,
                    "status": "available",
                }
            )
        return rows

    @classmethod
    def defaults(cls) -> list[Equipment]:
        return [
            cls("equipment_01", EquipmentType.TREADMILL.value, Location.GYM.value, time(6, 0), time(21, 0)),
            cls("equipment_02", EquipmentType.STATIONARY_BIKE.value, Location.GYM.value, time(6, 0), time(21, 0)),
            cls("equipment_03", EquipmentType.DUMBBELL_SET.value, Location.GYM.value, time(6, 0), time(21, 0)),
            cls("equipment_04", EquipmentType.YOGA_MAT.value, Location.HOME.value, time(6, 0), time(22, 0)),
            cls("equipment_05", EquipmentType.SAUNA_ROOM.value, Location.RECOVERY_CENTER.value, time(16, 0), time(21, 30)),
            cls("equipment_06", EquipmentType.ICE_BATH.value, Location.RECOVERY_CENTER.value, time(16, 0), time(21, 30)),
            cls("equipment_07", EquipmentType.COMPRESSION_BOOTS.value, Location.RECOVERY_CENTER.value, time(17, 0), time(21, 0)),
            cls("equipment_08", EquipmentType.BLENDER_STATION.value, Location.HOME.value, time(6, 0), time(9, 30)),
            cls("equipment_09", EquipmentType.LAB_KIT.value, Location.LAB.value, time(8, 0), time(12, 0)),
            cls("equipment_10", EquipmentType.BLOOD_PRESSURE_CUFF.value, Location.HOME.value, time(6, 0), time(22, 0)),
        ]

    @classmethod
    def generate_rows(cls, start_date: date, end_date: date, rng: random.Random) -> list[dict]:
        rows: list[dict] = []
        for resource in cls.defaults():
            rows.extend(resource.generate_availability_rows(start_date, end_date, rng))
        return rows
