from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from src.enums.activity_category import ActivityCategory

from .activity import Activity


@dataclass(slots=True)
class ConsultationActivity(Activity):
    CATEGORY: ClassVar[ActivityCategory] = ActivityCategory.CONSULTATION

    def constraint_weight(self) -> int:
        return Activity.constraint_weight(self) + 1
