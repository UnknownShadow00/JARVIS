from __future__ import annotations

from tasks import readiness_report


def _item(available: bool) -> dict[str, object]:
    return {
        "name": "test",
        "available": available,
        "detail": "detail",
        "remediation": "fix it",
    }


def test_readiness_report_returns_zero_when_required_checks_pass(monkeypatch, capsys) -> None:  # noqa: ANN001
    fake = {key: _item(True) for key in readiness_report.REQUIRED_CHECKS}
    fake["interpreter"] = _item(False)
    monkeypatch.setattr(readiness_report, "check_readiness", lambda: fake)

    exit_code = readiness_report.main()
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "All required readiness checks passed" in output


def test_readiness_report_returns_nonzero_when_required_check_fails(monkeypatch, capsys) -> None:  # noqa: ANN001
    fake = {key: _item(True) for key in readiness_report.REQUIRED_CHECKS}
    fake["audio_devices"] = _item(False)
    fake["interpreter"] = _item(False)
    monkeypatch.setattr(readiness_report, "check_readiness", lambda: fake)

    exit_code = readiness_report.main()
    output = capsys.readouterr().out

    assert exit_code == 1
    assert "need attention" in output
