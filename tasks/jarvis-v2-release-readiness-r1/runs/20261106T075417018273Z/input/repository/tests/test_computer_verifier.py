from __future__ import annotations

from app.computer.verifier import ActionVerifier


def test_verify_no_expectation(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr("app.computer.verifier.screenshot.capture", lambda: "/tmp/test.png")

    result = ActionVerifier().verify("click")

    assert result["verified"] is True
    assert result["screenshot"] == "/tmp/test.png"


def test_verify_with_expectation(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr("app.computer.verifier.screenshot.capture", lambda: "/tmp/test.png")

    result = ActionVerifier().verify("type", expected="hello")

    assert result["verified"] is None
    assert result["screenshot"] == "/tmp/test.png"
    assert result["expected"] == "hello"


def test_verify_capture_fails(monkeypatch) -> None:  # noqa: ANN001
    def fake_capture() -> str:
        raise RuntimeError("mss not installed")

    monkeypatch.setattr("app.computer.verifier.screenshot.capture", fake_capture)

    result = ActionVerifier().verify("click")

    assert result["verified"] is False
    assert result["error"] == "mss not installed"
