from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from src.enums.activity_category import ActivityCategory

from .activity import Activity


@dataclass(slots=True)
class TherapyActivity(Activity):
    CATEGORY: ClassVar[ActivityCategory] = ActivityCategory.THERAPY
