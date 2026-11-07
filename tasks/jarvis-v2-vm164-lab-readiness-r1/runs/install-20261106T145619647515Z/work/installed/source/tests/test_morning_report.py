from app.brain.morning_report import compose_morning_report


def test_compose_returns_string() -> None:
    assert isinstance(compose_morning_report(), str)


def test_compose_contains_sir() -> None:
    assert "sir" in compose_morning_report().lower()


def test_compose_contains_time() -> None:
    report = compose_morning_report()
    assert "AM" in report or "PM" in report
