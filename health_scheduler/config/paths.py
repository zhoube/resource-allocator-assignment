from __future__ import annotations

import os
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT_DIR / "docs"
ASSIGNMENT_DIR = DOCS_DIR / "assignment"

DATA_DIR = ROOT_DIR / "data"
SCENARIO_NAME = os.getenv("HEALTH_SCHEDULER_SCENARIO", "marcus").strip().lower() or "marcus"
SCENARIO_DIR = DATA_DIR / SCENARIO_NAME
INPUTS_DIR = SCENARIO_DIR / "inputs"
INPUT_ACTIVITIES_DIR = INPUTS_DIR / "activities"
INPUT_CONSTRAINTS_DIR = INPUTS_DIR / "constraints"
INPUT_ACTION_PLANS_DIR = INPUTS_DIR / "action_plans"
OUTPUTS_DIR = SCENARIO_DIR / "outputs"
PATIENT_PROFILE_MD = INPUTS_DIR / "patient_profile.md"

ACTIVITY_CATALOG_JSON = INPUT_ACTIVITIES_DIR / "activity_catalog.json"
ACTIVITY_CATALOG_CSV = INPUT_ACTIVITIES_DIR / "activity_catalog.csv"

ACTION_PLAN_JSON = INPUT_ACTION_PLANS_DIR / "action_plan.json"
ACTION_PLAN_CSV = INPUT_ACTION_PLANS_DIR / "action_plan.csv"

CLIENT_SCHEDULE_CSV = INPUT_CONSTRAINTS_DIR / "client_schedule.csv"
TRAVEL_PLANS_CSV = INPUT_CONSTRAINTS_DIR / "travel_plans.csv"
SPECIALISTS_CSV = INPUT_CONSTRAINTS_DIR / "specialists.csv"
ALLIED_HEALTH_CSV = INPUT_CONSTRAINTS_DIR / "allied_health.csv"
EQUIPMENT_CSV = INPUT_CONSTRAINTS_DIR / "equipment.csv"
CONSTRAINTS_BUNDLE_JSON = INPUT_CONSTRAINTS_DIR / "constraints_bundle.json"


def ensure_directories() -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    SCENARIO_DIR.mkdir(parents=True, exist_ok=True)
    INPUTS_DIR.mkdir(parents=True, exist_ok=True)
    INPUT_ACTIVITIES_DIR.mkdir(parents=True, exist_ok=True)
    INPUT_CONSTRAINTS_DIR.mkdir(parents=True, exist_ok=True)
    INPUT_ACTION_PLANS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    ASSIGNMENT_DIR.mkdir(parents=True, exist_ok=True)
