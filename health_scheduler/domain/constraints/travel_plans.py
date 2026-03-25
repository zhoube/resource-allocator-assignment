from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta


@dataclass(slots=True)
class TravelPlans:
    trip_id: str
    offset_days: int
    duration_days: int
    destination: str
    remote_only: bool
    notes: str

    def generate_row(self, start_date: date) -> dict:
        trip_start = start_date + timedelta(days=self.offset_days)
        trip_end = trip_start + timedelta(days=self.duration_days)
        return {
            "trip_id": self.trip_id,
            "start": datetime.combine(trip_start, time(6, 0)).isoformat(),
            "end": datetime.combine(trip_end, time(22, 0)).isoformat(),
            "destination": self.destination,
            "remote_only": str(self.remote_only).lower(),
            "notes": self.notes,
        }

    @classmethod
    def defaults(cls) -> list[TravelPlans]:
        return [
            cls("trip_01", 12, 4, "Tokyo", True, "Work trip with evening hotel availability only."),
            cls("trip_02", 34, 6, "Seoul", True, "Client can only support remote appointments and portable routines."),
            cls("trip_03", 59, 5, "Bangkok", True, "Red-eye return flight at the end of the trip."),
            cls("trip_04", 78, 4, "Sydney", True, "Conference travel with limited gym access."),
        ]

    @classmethod
    def generate_rows(cls, start_date: date) -> list[dict]:
        return [plan.generate_row(start_date) for plan in cls.defaults()]
