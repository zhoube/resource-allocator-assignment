from __future__ import annotations

import random
from datetime import date

from entities.constraints.allied_health import AlliedHealth
from entities.constraints.client_schedule import ClientSchedule
from entities.constraints.equipment import Equipment
from entities.constraints.specialists import Specialists
from entities.constraints.travel_plans import TravelPlans


def generate_constraints(start_date: date, end_date: date, rng: random.Random) -> dict[str, list[dict]]:
    return {
        "client_schedule": ClientSchedule.generate_rows(start_date, end_date, rng),
        "travel_plans": TravelPlans.generate_rows(start_date),
        "specialists": Specialists.generate_rows(start_date, end_date, rng),
        "allied_health": AlliedHealth.generate_rows(start_date, end_date, rng),
        "equipment": Equipment.generate_rows(start_date, end_date, rng),
    }
