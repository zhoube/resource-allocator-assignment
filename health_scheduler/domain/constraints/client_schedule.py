from __future__ import annotations

import random
from datetime import date


class ClientSchedule:
    @classmethod
    def generate_rows(cls, start_date: date, end_date: date, rng: random.Random) -> list[dict]:
        return [
            {"entry_type": "weekday", "weekday": "Mon", "date": "", "available_ranges": "0600-1300;1800-2100", "notes": "Workday template with flexible clinic and lab block before lunch."},
            {"entry_type": "weekday", "weekday": "Tue", "date": "", "available_ranges": "0600-1300;1800-1930", "notes": "Family dinner in the evening, but daytime appointments can be moved around."},
            {"entry_type": "weekday", "weekday": "Wed", "date": "", "available_ranges": "0600-1300;1800-2000", "notes": "Project review in the evening, with flexible morning and midday access."},
            {"entry_type": "weekday", "weekday": "Thu", "date": "", "available_ranges": "0600-1300;1800-1930", "notes": "Family dinner in the evening, but daytime appointments can be moved around."},
            {"entry_type": "weekday", "weekday": "Fri", "date": "", "available_ranges": "0600-1300;1800-2100", "notes": "Workday template with flexible clinic and lab block before lunch."},
            {"entry_type": "weekday", "weekday": "Sat", "date": "", "available_ranges": "0600-1000;1200-2100", "notes": "Weekend errands block in late morning."},
            {"entry_type": "weekday", "weekday": "Sun", "date": "", "available_ranges": "0600-1100;1300-2100", "notes": "Brunch with family at midday."},
        ]
