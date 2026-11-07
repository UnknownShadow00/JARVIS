from __future__ import annotations

from tasks import tool_readiness_smoke


def test_run_smoke_all_passes() -> None:
    results = tool_readiness_smoke.run_smoke()

    assert results
    assert all(result.passed for result in results)


def test_main_returns_nonzero_for_failure(monkeypatch, capsys) -> None:  # noqa: ANN001
    monkeypatch.setattr(
        tool_readiness_smoke,
        "CHECKS",
        [lambda: tool_readiness_smoke.SmokeResult("forced failure", False, "boom")],
    )

    exit_code = tool_readiness_smoke.main()
    output = capsys.readouterr().out

    assert exit_code == 1
    assert "FAIL" in output


def test_main_returns_zero_for_pass(monkeypatch, capsys) -> None:  # noqa: ANN001
    monkeypatch.setattr(
        tool_readiness_smoke,
        "CHECKS",
        [lambda: tool_readiness_smoke.SmokeResult("forced pass", True, "ok")],
    )

    exit_code = tool_readiness_smoke.main()
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "PASS" in output
