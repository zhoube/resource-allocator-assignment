from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from .activities.activity import Activity


@dataclass(slots=True)
class Occurrence:
    occurrence_id: str
    activity: Activity
    sequence: int
    window_start: datetime
    window_end: datetime
    preferred_start: datetime
