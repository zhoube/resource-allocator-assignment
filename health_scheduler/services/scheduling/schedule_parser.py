from __future__ import annotations

import json

SCHEDULE_RESPONSE_SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "scheduled_events": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "properties": {
                    "activity_id": {"type": "string"},
                    "start": {"type": "string"},
                },
                "required": ["activity_id", "start"],
            },
        }
    },
    "required": ["scheduled_events"],
}


def parse_schedule_response(response_text: str) -> list[dict[str, str]]:
    payload = json.loads(response_text)
    scheduled_events = payload.get("scheduled_events", [])
    parsed: list[dict[str, str]] = []
    for item in scheduled_events:
        activity_id = str(item.get("activity_id", "")).strip()
        start = str(item.get("start", "")).strip()
        if not activity_id or not start:
            continue
        parsed.append({"activity_id": activity_id, "start": start})
    return parsed
