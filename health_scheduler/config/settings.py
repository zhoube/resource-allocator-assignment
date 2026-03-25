from __future__ import annotations

import os
from datetime import date, time

DEFAULT_START_DATE = date(2026, 4, 1)
DEFAULT_MONTHS = 3
SLOT_MINUTES = 30

TIME_WINDOWS = {
    "early_morning": (time(6, 0), time(8, 0)),
    "morning": (time(8, 0), time(11, 0)),
    "midday": (time(11, 30), time(14, 0)),
    "afternoon": (time(14, 0), time(17, 0)),
    "evening": (time(17, 30), time(21, 0)),
}

OPENAI_MODEL = os.getenv("HEALTH_SCHEDULER_OPENAI_MODEL", "gpt-5.4")
OPENAI_API_BASE = os.getenv("HEALTH_SCHEDULER_OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_REASONING_EFFORT = os.getenv("HEALTH_SCHEDULER_OPENAI_REASONING_EFFORT", "medium")
