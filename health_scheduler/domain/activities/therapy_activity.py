from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from health_scheduler.domain.enums.activity_category import ActivityCategory

from .activity import Activity


@dataclass(slots=True)
class TherapyActivity(Activity):
    CATEGORY: ClassVar[ActivityCategory] = ActivityCategory.THERAPY
