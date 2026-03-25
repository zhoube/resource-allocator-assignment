from __future__ import annotations

import random
from datetime import date, datetime, time, timedelta
from itertools import count

from health_scheduler.utils.datetime_utils import daterange


class ClientSchedule:
    @classmethod
    def generate_rows(cls, start_date: date, end_date: date, rng: random.Random) -> list[dict]:
        rows: list[dict] = []
        commitment_id = count(1)
        for day in daterange(start_date, end_date):
            rows.append(cls.build_busy_block(commitment_id, "Sleep", day, time(23, 0), day + timedelta(days=1), time(6, 0), "home", "sleep"))
            if day.weekday() < 5:
                rows.append(cls.build_busy_block(commitment_id, "Work Focus Block", day, time(9, 0), day, time(12, 0), "office", "work"))
                rows.append(cls.build_busy_block(commitment_id, "Work Focus Block", day, time(13, 0), day, time(17, 0), "office", "work"))
                rows.append(cls.build_busy_block(commitment_id, "Commute", day, time(8, 0), day, time(9, 0), "commute", "travel"))
                rows.append(cls.build_busy_block(commitment_id, "Commute", day, time(17, 0), day, time(18, 0), "commute", "travel"))
            if day.weekday() in {1, 3}:
                rows.append(cls.build_busy_block(commitment_id, "Family Dinner", day, time(19, 30), day, time(21, 0), "home", "family"))
            if day.weekday() == 2:
                rows.append(cls.build_busy_block(commitment_id, "Project Review", day, time(20, 0), day, time(21, 0), "home", "work"))
            if day.weekday() == 5 and rng.random() < 0.6:
                rows.append(cls.build_busy_block(commitment_id, "Weekend Errands", day, time(10, 0), day, time(12, 0), "city", "personal"))
            if day.weekday() == 6:
                rows.append(cls.build_busy_block(commitment_id, "Brunch With Family", day, time(11, 0), day, time(13, 0), "city", "family"))
        return rows

    @staticmethod
    def build_busy_block(commitment_id: count, title: str, start_day: date, start_time: time, end_day: date, end_time: time, location: str, commitment_type: str) -> dict:
        return {
            "commitment_id": f"commitment_{next(commitment_id):04d}",
            "title": title,
            "start": datetime.combine(start_day, start_time).isoformat(),
            "end": datetime.combine(end_day, end_time).isoformat(),
            "location": location,
            "commitment_type": commitment_type,
        }
