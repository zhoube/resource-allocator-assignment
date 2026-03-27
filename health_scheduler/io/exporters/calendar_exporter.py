from __future__ import annotations

import html
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from uuid import uuid4

from health_scheduler.domain.scheduling.scheduled_event import ScheduledEvent
from health_scheduler.io.storage.files import write_csv, write_json
from health_scheduler.utils.datetime_utils import isoformat_zless


def export_schedule_csv(events: list[ScheduledEvent], path: Path) -> None:
    fieldnames = [
        "event_id",
        "activity_id",
        "activity_title",
        "category",
        "priority",
        "frequency",
        "start",
        "end",
        "duration_minutes",
        "location",
        "mode",
        "assigned_provider",
        "assigned_equipment",
        "backup_for",
        "details",
        "metrics",
    ]
    rows = [event.to_csv_row() for event in events]
    write_csv(path, rows, fieldnames)


def export_unscheduled_csv(items: list[dict], path: Path) -> None:
    fieldnames = [
        "activity_id",
        "activity_title",
        "proposed_start",
        "reason",
        "skip_adjustment",
    ]
    write_csv(path, items, fieldnames)


def export_json_bundle(events: list[ScheduledEvent], unscheduled: list[dict], path: Path) -> None:
    write_json(
        path,
        {
            "scheduled_events": [event.to_dict() for event in events],
            "unscheduled_events": unscheduled,
            "scheduled_count": len(events),
            "unscheduled_count": len(unscheduled),
        },
    )


def export_ics(events: list[ScheduledEvent], path: Path) -> None:
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//HealthScheduler//Scheduling Constraints Demo//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
    ]
    generated_at = isoformat_zless(datetime.utcnow())
    for event in events:
        title = event.activity_title
        if event.backup_for:
            title = f"{title} (backup for {event.backup_for})"
        description_parts = [
            event.details,
            f"Frequency: {event.frequency}",
            f"Metrics: {', '.join(event.metrics) or 'None'}",
        ]
        if event.assigned_provider:
            description_parts.append(f"Provider: {event.assigned_provider}")
        if event.assigned_equipment:
            description_parts.append(f"Equipment: {', '.join(event.assigned_equipment)}")
        if event.mode:
            description_parts.append(f"Mode: {event.mode}")
        if event.location:
            description_parts.append(f"Location: {event.location}")
        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:{uuid4()}",
                f"DTSTAMP:{generated_at}",
                f"DTSTART:{event.start.strftime('%Y%m%dT%H%M%S')}",
                f"DTEND:{event.end.strftime('%Y%m%dT%H%M%S')}",
                f"SUMMARY:{_escape_ics(title)}",
                f"DESCRIPTION:{_escape_ics(' | '.join(description_parts))}",
                f"LOCATION:{_escape_ics(event.location)}",
                "END:VEVENT",
            ]
        )
    lines.append("END:VCALENDAR")
    path.write_text("\r\n".join(lines) + "\r\n", encoding="utf-8")


def export_html(events: list[ScheduledEvent], unscheduled: list[dict], path: Path, start_date: date, end_date: date) -> None:
    grouped: dict[str, dict[str, list[ScheduledEvent]]] = defaultdict(lambda: defaultdict(list))
    for event in events:
        month_key = event.start.strftime("%B %Y")
        day_key = event.start.strftime("%A, %d %B %Y")
        grouped[month_key][day_key].append(event)

    month_blocks = []
    for month_key, day_map in grouped.items():
        day_blocks = []
        for day_key, day_events in day_map.items():
            cards = []
            for event in sorted(day_events, key=lambda item: item.start):
                start = event.start.strftime("%H:%M")
                end = event.end.strftime("%H:%M")
                backup_note = ""
                if event.backup_for:
                    backup_note = f"<div class='meta'>Backup for: {html.escape(event.backup_for)}</div>"
                provider_note = ""
                if event.assigned_provider:
                    provider_note = f"<div class='meta'>Provider: {html.escape(event.assigned_provider)}</div>"
                equipment_note = ""
                if event.assigned_equipment:
                    equipment_note = f"<div class='meta'>Equipment: {html.escape(', '.join(event.assigned_equipment))}</div>"
                cards.append(
                    f"""
                    <article class="event-card">
                      <div class="event-time">{start} - {end}</div>
                      <div class="event-title">{html.escape(event.activity_title)}</div>
                      <div class="meta">{html.escape(event.category)} | Priority {event.priority}</div>
                      <div class="meta">Frequency: {html.escape(event.frequency)}</div>
                      <div class="meta">Location: {html.escape(event.location)} | Mode: {html.escape(event.mode)}</div>
                      {provider_note}
                      {equipment_note}
                      {backup_note}
                      <p>{html.escape(event.details)}</p>
                    </article>
                    """
                )
            day_blocks.append(
                f"""
                <section class="day-block">
                  <h3>{html.escape(day_key)}</h3>
                  {''.join(cards)}
                </section>
                """
            )
        month_blocks.append(
            f"""
            <section class="month-block">
              <h2>{html.escape(month_key)}</h2>
              {''.join(day_blocks)}
            </section>
            """
        )

    unscheduled_rows = "".join(
        f"""
        <tr>
          <td>{html.escape(item['activity_title'])}</td>
          <td>{html.escape(item['proposed_start'])}</td>
          <td>{html.escape(item['reason'])}</td>
          <td>{html.escape(item['skip_adjustment'])}</td>
        </tr>
        """
        for item in unscheduled
    )

    document = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Personalized Plan</title>
  <style>
    :root {{
      --paper: #f7f4ec;
      --ink: #1f2a1f;
      --accent: #295f4e;
      --accent-soft: #d7e7dd;
      --card: #fffdf8;
      --border: #d7d1c5;
      --alert: #8a3b2a;
    }}
    body {{
      margin: 0;
      font-family: Georgia, "Times New Roman", serif;
      background: linear-gradient(180deg, #ebe5d8 0%, var(--paper) 38%, #f8f7f1 100%);
      color: var(--ink);
    }}
    main {{
      max-width: 1080px;
      margin: 0 auto;
      padding: 32px 20px 48px;
    }}
    header {{
      background: rgba(255, 253, 248, 0.86);
      border: 1px solid var(--border);
      border-radius: 20px;
      padding: 24px;
      box-shadow: 0 14px 40px rgba(26, 35, 24, 0.08);
    }}
    h1, h2, h3 {{
      margin: 0 0 12px;
      font-weight: 600;
    }}
    .summary {{
      display: flex;
      flex-wrap: wrap;
      gap: 12px;
      margin-top: 16px;
    }}
    .summary-chip {{
      background: var(--accent-soft);
      border-radius: 999px;
      padding: 8px 14px;
      font-size: 0.95rem;
    }}
    .month-block {{
      margin-top: 28px;
      padding: 20px;
      background: rgba(255, 253, 248, 0.88);
      border: 1px solid var(--border);
      border-radius: 18px;
    }}
    .day-block {{
      margin-top: 18px;
    }}
    .event-card {{
      margin-top: 12px;
      padding: 16px;
      border-radius: 16px;
      background: var(--card);
      border: 1px solid var(--border);
      box-shadow: 0 10px 26px rgba(26, 35, 24, 0.06);
    }}
    .event-time {{
      color: var(--accent);
      font-size: 0.95rem;
      font-weight: 700;
      letter-spacing: 0.03em;
      text-transform: uppercase;
    }}
    .event-title {{
      margin-top: 6px;
      font-size: 1.15rem;
      font-weight: 700;
    }}
    .meta {{
      margin-top: 4px;
      font-size: 0.95rem;
      color: #465448;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 18px;
      background: rgba(255, 253, 248, 0.88);
      border-radius: 14px;
      overflow: hidden;
    }}
    th, td {{
      text-align: left;
      padding: 10px 12px;
      border-bottom: 1px solid var(--border);
      vertical-align: top;
    }}
    th {{
      background: #efe6d4;
    }}
    .warning {{
      color: var(--alert);
      font-weight: 700;
    }}
    @media (max-width: 640px) {{
      main {{
        padding: 20px 14px 34px;
      }}
      header, .month-block {{
        border-radius: 14px;
      }}
      .event-card {{
        padding: 14px;
      }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>Personalized Plan</h1>
      <p>Generated schedule window: {start_date.isoformat()} to {end_date.isoformat()}</p>
      <div class="summary">
        <span class="summary-chip">Scheduled events: {len(events)}</span>
        <span class="summary-chip">Unscheduled events: {len(unscheduled)}</span>
        <span class="summary-chip">Calendar export: .ics included</span>
      </div>
    </header>
    {''.join(month_blocks)}
    <section class="month-block">
      <h2>Unscheduled Items</h2>
      <p class="warning">These items could not be placed in the planning horizon or required a manual review.</p>
      <table>
        <thead>
          <tr>
            <th>Activity</th>
            <th>Proposed Start</th>
            <th>Reason</th>
            <th>Skip Adjustment</th>
          </tr>
        </thead>
        <tbody>
          {unscheduled_rows or "<tr><td colspan='4'>No unscheduled items.</td></tr>"}
        </tbody>
      </table>
    </section>
  </main>
</body>
</html>
"""
    path.write_text(document, encoding="utf-8")


def _escape_ics(value: str) -> str:
    return value.replace("\\", "\\\\").replace(";", "\\;").replace(",", "\\,").replace("\n", "\\n")
