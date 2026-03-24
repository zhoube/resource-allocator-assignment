from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, ClassVar

from src.enums.activity_category import ActivityCategory
from src.enums.location import TravelFriendlyLocation
from src.enums.roles import AlliedHealthRole, SpecialistRole

from .frequency import Frequency


def classify_role(role: str) -> str:
    if SpecialistRole.has_value(role):
        return "specialist"
    if AlliedHealthRole.has_value(role):
        return "allied_health"
    return "self"


@dataclass(slots=True)
class Activity:
    id: str
    title: str
    priority: int
    duration_minutes: int
    details: str
    frequency: Frequency
    facilitator_role: str
    location: str
    remote_allowed: bool
    equipment_required: list[str] = field(default_factory=list)
    prep_required: list[str] = field(default_factory=list)
    backup_activity_ids: list[str] = field(default_factory=list)
    skip_adjustment: str = ""
    metrics: list[str] = field(default_factory=list)
    preferred_time_windows: list[str] = field(default_factory=list)
    category: str = field(init=False)
    resource_pool: str = field(init=False)

    CATEGORY: ClassVar[ActivityCategory | None] = None

    def __post_init__(self) -> None:
        self.frequency = Frequency.from_value(self.frequency)
        self.category = self.normalized_category().value
        self.resource_pool = classify_role(self.facilitator_role)

    @classmethod
    def normalized_category(cls) -> ActivityCategory:
        if cls.CATEGORY is None:
            raise ValueError("Base Activity does not define a category.")
        return ActivityCategory(cls.CATEGORY)

    @classmethod
    def from_payload(cls, payload: dict[str, Any]) -> Activity:
        return cls(
            id=payload["id"],
            title=payload["title"],
            priority=int(payload["priority"]),
            duration_minutes=int(payload["duration_minutes"]),
            details=payload["details"],
            frequency=Frequency.from_value(payload["frequency"]),
            facilitator_role=payload["facilitator_role"],
            location=payload["location"],
            remote_allowed=bool(payload["remote_allowed"]),
            equipment_required=list(payload.get("equipment_required", [])),
            prep_required=list(payload.get("prep_required", [])),
            backup_activity_ids=list(payload.get("backup_activity_ids", [])),
            skip_adjustment=payload.get("skip_adjustment", ""),
            metrics=list(payload.get("metrics", [])),
            preferred_time_windows=list(payload.get("preferred_time_windows", [])),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "priority": self.priority,
            "duration_minutes": self.duration_minutes,
            "details": self.details,
            "frequency": self.frequency.to_dict(),
            "facilitator_role": self.facilitator_role,
            "resource_pool": self.resource_pool,
            "location": self.location,
            "remote_allowed": self.remote_allowed,
            "equipment_required": list(self.equipment_required),
            "prep_required": list(self.prep_required),
            "backup_activity_ids": list(self.backup_activity_ids),
            "skip_adjustment": self.skip_adjustment,
            "metrics": list(self.metrics),
            "preferred_time_windows": list(self.preferred_time_windows),
        }

    def to_csv_row(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "category": self.category,
            "priority": self.priority,
            "duration_minutes": self.duration_minutes,
            "details": self.details,
            "frequency": json.dumps(self.frequency.to_dict()),
            "facilitator_role": self.facilitator_role,
            "resource_pool": self.resource_pool,
            "location": self.location,
            "remote_allowed": self.remote_allowed,
            "equipment_required": json.dumps(self.equipment_required),
            "prep_required": json.dumps(self.prep_required),
            "backup_activity_ids": json.dumps(self.backup_activity_ids),
            "skip_adjustment": self.skip_adjustment,
            "metrics": json.dumps(self.metrics),
            "preferred_time_windows": json.dumps(self.preferred_time_windows),
        }

    def constraint_weight(self) -> int:
        return (self.resource_pool != "self") * 3 + len(self.equipment_required) * 2 + int(not self.remote_allowed)

    def supports_work_microtask_exception(self) -> bool:
        return False

    def travel_placement(self) -> tuple[str, str] | None:
        if self.remote_allowed and self.resource_pool != "self":
            return ("remote", "remote")
        if self.resource_pool == "self" and (TravelFriendlyLocation.has_value(self.location) or not self.equipment_required):
            if TravelFriendlyLocation.has_value(self.location):
                return ("in_person", self.location)
            return ("in_person", "travel")
        return None
