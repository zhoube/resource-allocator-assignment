from __future__ import annotations

from enum import StrEnum


class ActivityField(StrEnum):
    ID = "id"
    TITLE = "title"
    CATEGORY = "category"
    PRIORITY = "priority"
    DURATION_MINUTES = "duration_minutes"
    DETAILS = "details"
    FREQUENCY = "frequency"
    FACILITATOR_ROLE = "facilitator_role"
    RESOURCE_POOL = "resource_pool"
    LOCATION = "location"
    REMOTE_ALLOWED = "remote_allowed"
    EQUIPMENT_REQUIRED = "equipment_required"
    PREP_REQUIRED = "prep_required"
    BACKUP_ACTIVITY_IDS = "backup_activity_ids"
    SKIP_ADJUSTMENT = "skip_adjustment"
    METRICS = "metrics"
    PREFERRED_TIME_WINDOWS = "preferred_time_windows"


def activity_fieldnames() -> list[str]:
    return [field.value for field in ActivityField]
