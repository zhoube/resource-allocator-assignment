from __future__ import annotations

import random
from datetime import date

from health_scheduler.domain.constraints.allied_health import AlliedHealth
from health_scheduler.domain.constraints.client_schedule import ClientSchedule
from health_scheduler.domain.constraints.equipment import Equipment
from health_scheduler.domain.constraints.specialists import Specialists
from health_scheduler.domain.constraints.travel_plans import TravelPlans


def generate_constraints(start_date: date, end_date: date, rng: random.Random) -> dict[str, list[dict]]:
    return {
        "client_schedule": ClientSchedule.generate_rows(start_date, end_date, rng),
        "travel_plans": TravelPlans.generate_rows(start_date),
        "specialists": Specialists.generate_rows(start_date, end_date, rng),
        "allied_health": AlliedHealth.generate_rows(start_date, end_date, rng),
        "equipment": Equipment.generate_rows(start_date, end_date, rng),
    }
