"""Calendar tool for reading local .ics events by day."""
from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
from typing import Any

from app.config import settings
from app.logs.audit import audit

SAFETY_LEVEL = 0
DESCRIPTION = "Read calendar events from local .ics files"

SEARCH_PATHS = [
    Path.home() / "Calendar",
    Path.home() / "Documents",
    Path.cwd(),
]


def execute(params: dict[str, Any]) -> dict[str, Any]:
    """Read matching VEVENT entries from local .ics files for a given date."""
    date_str = str(params.get("date") or date.today().isoformat())

    if settings.safety.dry_run:
        return {"dry_run": True, "note": "Would read calendar events for " + date_str}

    try:
        target_date = date.fromisoformat(date_str)
    except ValueError:
        return {"events": [], "date": date_str, "count": 0}

    try:
        from icalendar import Calendar
    except ImportError:
        return {"events": [], "date": date_str, "count": 0, "note": "icalendar not installed"}

    events: list[dict[str, str | None]] = []

    for ics_file in _iter_ics_files():
        try:
            calendar = Calendar.from_ical(ics_file.read_bytes())
        except Exception:  # noqa: BLE001
            continue

        for component in calendar.walk():
            if getattr(component, "name", "") != "VEVENT":
                continue

            start = _extract_value(component.get("DTSTART"))
            if start is None or _event_date(start) != target_date:
                continue

            end = _extract_value(component.get("DTEND"))
            events.append(
                {
                    "summary": str(component.get("SUMMARY") or ""),
                    "start": _to_iso(start),
                    "end": _to_iso(end) if end is not None else None,
                    "location": _optional_text(component.get("LOCATION")),
                }
            )

    result = {"events": events, "date": date_str, "count": len(events)}
    audit.log("tool_calendar", {"date": date_str, "event_count": len(events)})
    return result


def _iter_ics_files() -> list[Path]:
    files: list[Path] = []
    seen: set[Path] = set()

    for base_path in SEARCH_PATHS:
        try:
            resolved = base_path.expanduser().resolve()
        except OSError:
            continue
        if not resolved.exists() or not resolved.is_dir():
            continue
        for item in resolved.glob("*.ics"):
            try:
                candidate = item.resolve()
            except OSError:
                continue
            if candidate not in seen and candidate.is_file():
                seen.add(candidate)
                files.append(candidate)

    return files


def _extract_value(field: Any) -> date | datetime | None:
    if field is None:
        return None
    if hasattr(field, "dt"):
        return field.dt
    return field


def _event_date(value: date | datetime) -> date:
    if isinstance(value, datetime):
        return value.date()
    return value


def _to_iso(value: date | datetime) -> str:
    if isinstance(value, datetime):
        return value.isoformat()
    return value.isoformat()


def _optional_text(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return str(value)
