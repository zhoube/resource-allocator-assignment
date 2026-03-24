from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

from src.enums.activity_category import ActivityCategory

from .activity import Activity


@dataclass(slots=True)
class MedicationActivity(Activity):
    CATEGORY: ClassVar[ActivityCategory] = ActivityCategory.MEDICATION

    def supports_work_microtask_exception(self) -> bool:
        return self.resource_pool == "self" and self.duration_minutes <= 15

    def travel_placement(self) -> tuple[str, str] | None:
        if self.resource_pool == "self":
            return ("in_person", "travel")
        if self.remote_allowed:
            return ("remote", "remote")
        return None
