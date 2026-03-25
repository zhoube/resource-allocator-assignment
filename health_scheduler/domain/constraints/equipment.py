from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import date, time

from health_scheduler.domain.enums.equipment_type import EquipmentType
from health_scheduler.domain.enums.location import Location
from health_scheduler.utils.datetime_utils import format_compact_range, format_weekday_pattern


@dataclass(slots=True)
class Equipment:
    resource_id: str
    equipment_type: str
    location: str
    days: list[int]
    start: time
    end: time

    def to_csv_row(self) -> dict:
        return {
            "resource_id": self.resource_id,
            "equipment_type": self.equipment_type,
            "location": self.location,
            "weekday_pattern": format_weekday_pattern(self.days),
            "available_ranges": format_compact_range(self.start, self.end),
            "notes": "",
        }

    @classmethod
    def defaults(cls) -> list[Equipment]:
        return [
            cls("equipment_01", EquipmentType.TREADMILL.value, Location.GYM.value, [0, 1, 2, 3, 4, 5, 6], time(6, 0), time(21, 0)),
            cls("equipment_02", EquipmentType.STATIONARY_BIKE.value, Location.GYM.value, [0, 1, 2, 3, 4, 5, 6], time(6, 0), time(21, 0)),
            cls("equipment_03", EquipmentType.DUMBBELL_SET.value, Location.GYM.value, [0, 1, 2, 3, 4, 5, 6], time(6, 0), time(21, 0)),
            cls("equipment_04", EquipmentType.YOGA_MAT.value, Location.HOME.value, [0, 1, 2, 3, 4, 5, 6], time(6, 0), time(22, 0)),
            cls("equipment_05", EquipmentType.SAUNA_ROOM.value, Location.RECOVERY_CENTER.value, [0, 1, 2, 3, 4, 5, 6], time(16, 0), time(21, 30)),
            cls("equipment_06", EquipmentType.ICE_BATH.value, Location.RECOVERY_CENTER.value, [0, 1, 2, 3, 4, 5, 6], time(16, 0), time(21, 30)),
            cls("equipment_07", EquipmentType.COMPRESSION_BOOTS.value, Location.RECOVERY_CENTER.value, [0, 1, 2, 3, 4, 5, 6], time(17, 0), time(21, 0)),
            cls("equipment_08", EquipmentType.BLENDER_STATION.value, Location.HOME.value, [0, 1, 2, 3, 4, 5, 6], time(6, 0), time(9, 30)),
            cls("equipment_09", EquipmentType.LAB_KIT.value, Location.LAB.value, [0, 1, 2, 3, 4, 5], time(8, 0), time(12, 0)),
            cls("equipment_10", EquipmentType.BLOOD_PRESSURE_CUFF.value, Location.HOME.value, [0, 1, 2, 3, 4, 5, 6], time(6, 0), time(22, 0)),
        ]

    @classmethod
    def generate_rows(cls, start_date: date, end_date: date, rng: random.Random) -> list[dict]:
        return [resource.to_csv_row() for resource in cls.defaults()]
