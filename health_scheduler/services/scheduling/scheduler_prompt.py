from __future__ import annotations

SCHEDULER_PROMPT_TEMPLATE = """
Create a complete schedule for all activity instances implied by each activity's frequency within the planning window.

Follow this procedure:
1. First, understand the constraint sections:
   - `PLANNING_WINDOW`: the overall start and end dates that bound the schedule.
   - `CLIENT_AVAILABILITY`: the client's free time. Every scheduled event must fit inside one of these available ranges.
   - `TRAVEL_PLANS`: travel periods that may limit where an activity can happen.
   - `SPECIALISTS`: specialist providers, each with a role, location, remote support flag, and availability.
   - `ALLIED_HEALTH`: allied health providers, each with a role, location, remote support flag, and availability.
   - `EQUIPMENT`: equipment resources, each with a type, location, and availability.
2. Process the activities in the order provided. They are already ordered from highest priority to lowest priority.
3. For each activity, explicitly consider each of its constraints before choosing times:
   - `frequency`: infer how many events are needed from the planning window and distribute them across days, weeks, or months according to the activity cadence.
   - `duration_minutes`: each event must fit this full duration.
   - `location`: place the event where the activity is meant to occur.
   - `remote_allowed`: if false, do not convert the activity to remote.
   - `facilitator_role`: if present, the event must match an available provider with that exact role.
   - `equipment_required`: every listed equipment type must be available for the chosen slot.
4. For the current activity, infer how many events are required from its frequency and the planning window.
5. For each required event of the current activity:
   - search for a valid 30-minute aligned start time
   - check the candidate time against client availability, travel, provider availability, equipment availability, location requirements, remote rules, and all previously placed events
   - if the candidate time fails any constraint, discard it and continue searching for another valid slot
   - do not output invalid events
6. After placing each valid event, immediately treat that time as occupied in the client schedule so no later event can overlap it.
7. Only omit an event if you have already searched the planning window and could not find any valid slot for it.
8. Do not invent new activity ids, providers, equipment, or times outside the supplied data.
9. Return JSON only in the required format, with no explanations or markdown.

Return JSON only in this exact shape:
{{
  "scheduled_events": [
    {{
      "activity_id": "string",
      "start": "YYYY-MM-DDTHH:MM:SS"
    }}
  ]
}}

<ACTIVITIES>
{activities}
</ACTIVITIES>

<PLANNING_WINDOW>
{planning_window}
</PLANNING_WINDOW>

<CLIENT_AVAILABILITY>
{client_availability}
</CLIENT_AVAILABILITY>

<TRAVEL_PLANS>
{travel_plans}
</TRAVEL_PLANS>

<SPECIALISTS>
{specialists}
</SPECIALISTS>

<ALLIED_HEALTH>
{allied_health}
</ALLIED_HEALTH>

<EQUIPMENT>
{equipment}
</EQUIPMENT>
""".strip()
