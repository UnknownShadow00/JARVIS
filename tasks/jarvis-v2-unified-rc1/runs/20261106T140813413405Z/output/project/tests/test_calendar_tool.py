from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path
from types import ModuleType, SimpleNamespace

from app.config import settings
from app.tools.calendar import SAFETY_LEVEL, execute
from app.tools.registry import registry


def test_safety_level() -> None:
    assert SAFETY_LEVEL == 0


def test_dry_run(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr(settings.safety, "dry_run", True)
    result = execute({})
    assert result.get("dry_run") is True


def test_no_ics_files(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr(settings.safety, "dry_run", False)
    result = execute({"date": "2000-01-01"})
    assert "events" in result
    assert result["count"] == 0


def test_execute_with_ics(monkeypatch) -> None:  # noqa: ANN001
    from app.tools import calendar

    temp_dir = Path("tasks/.calendar_test_tmp").resolve()
    try:
        temp_dir.mkdir(parents=True, exist_ok=True)
        ics_path = temp_dir / "sample.ics"
        ics_path.write_text(
            "\n".join(
                [
                    "BEGIN:VCALENDAR",
                    "VERSION:2.0",
                    "BEGIN:VEVENT",
                    "DTSTART;VALUE=DATE:20000101",
                    "DTEND;VALUE=DATE:20000102",
                    "SUMMARY:Millennium Event",
                    "LOCATION:Test Lab",
                    "END:VEVENT",
                    "END:VCALENDAR",
                ]
            ),
            encoding="utf-8",
        )

        class FakeEvent:
            name = "VEVENT"

            def __init__(self, fields: dict[str, object]) -> None:
                self._fields = fields

            def get(self, key: str) -> object | None:
                return self._fields.get(key)

        class FakeCalendar:
            def __init__(self, events: list[FakeEvent]) -> None:
                self._events = events

            @classmethod
            def from_ical(cls, raw_data: bytes) -> "FakeCalendar":
                text = raw_data.decode("utf-8")
                fields: dict[str, object] = {}
                for line in text.splitlines():
                    if line.startswith("DTSTART"):
                        fields["DTSTART"] = SimpleNamespace(dt=date(2000, 1, 1))
                    elif line.startswith("DTEND"):
                        fields["DTEND"] = SimpleNamespace(dt=date(2000, 1, 2))
                    elif line.startswith("SUMMARY:"):
                        fields["SUMMARY"] = line.split(":", 1)[1]
                    elif line.startswith("LOCATION:"):
                        fields["LOCATION"] = line.split(":", 1)[1]
                return cls([FakeEvent(fields)])

            def walk(self) -> list[FakeEvent]:
                return self._events

        fake_module = ModuleType("icalendar")
        fake_module.Calendar = FakeCalendar
        monkeypatch.setattr(settings.safety, "dry_run", False)
        monkeypatch.setattr(calendar, "SEARCH_PATHS", [temp_dir])
        monkeypatch.setitem(__import__("sys").modules, "icalendar", fake_module)

        result = execute({"date": "2000-01-01"})

        assert result["count"] == 1
        assert result["events"][0]["summary"]
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_registered() -> None:
    assert "calendar" in registry.TOOLS
