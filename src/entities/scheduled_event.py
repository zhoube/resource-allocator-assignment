from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .occurrence import Occurrence


@dataclass(slots=True)
class ScheduledEvent:
    event_id: str
    activity_id: str
    activity_title: str
    category: str
    priority: int
    start: datetime
    end: datetime
    duration_minutes: int
    location: str
    mode: str
    assigned_provider: str = ""
    assigned_equipment: list[str] = field(default_factory=list)
    backup_for: str = ""
    details: str = ""
    metrics: list[str] = field(default_factory=list)

    @classmethod
    def from_occurrence(
        cls,
        occurrence: Occurrence,
        start: datetime,
        end: datetime,
        location: str,
        mode: str,
        assigned_provider: str = "",
        assigned_equipment: list[str] | None = None,
        backup_for: str = "",
    ) -> ScheduledEvent:
        activity = occurrence.activity
        return cls(
            event_id=occurrence.occurrence_id,
            activity_id=activity.id,
            activity_title=activity.title,
            category=activity.category,
            priority=activity.priority,
            start=start,
            end=end,
            duration_minutes=activity.duration_minutes,
            location=location,
            mode=mode,
            assigned_provider=assigned_provider,
            assigned_equipment=list(assigned_equipment or []),
            backup_for=backup_for,
            details=activity.details,
            metrics=list(activity.metrics),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "activity_id": self.activity_id,
            "activity_title": self.activity_title,
            "category": self.category,
            "priority": self.priority,
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "duration_minutes": self.duration_minutes,
            "location": self.location,
            "mode": self.mode,
            "assigned_provider": self.assigned_provider,
            "assigned_equipment": list(self.assigned_equipment),
            "backup_for": self.backup_for,
            "details": self.details,
            "metrics": list(self.metrics),
        }

    def to_csv_row(self) -> dict[str, Any]:
        return {
            "event_id": self.event_id,
            "activity_id": self.activity_id,
            "activity_title": self.activity_title,
            "category": self.category,
            "priority": self.priority,
            "start": self.start.isoformat(),
            "end": self.end.isoformat(),
            "duration_minutes": self.duration_minutes,
            "location": self.location,
            "mode": self.mode,
            "assigned_provider": self.assigned_provider,
            "assigned_equipment": ", ".join(self.assigned_equipment),
            "backup_for": self.backup_for,
            "details": self.details,
            "metrics": ", ".join(self.metrics),
        }
