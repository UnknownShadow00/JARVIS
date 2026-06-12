from __future__ import annotations

from tasks import pre_server_readiness


def test_build_checks_includes_expected_commands(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr(pre_server_readiness, "_npm_command", lambda: "npm")

    checks = pre_server_readiness.build_checks()
    names = [check.name for check in checks]

    assert names == [
        "full pytest",
        "python dependency audit",
        "python dependency consistency",
        "electron dependency audit",
        "readiness report",
        "tool readiness smoke",
    ]
    assert checks[0].command[:4] == [
        pre_server_readiness.sys.executable,
        "-m",
        "pytest",
        "-q",
    ]


def test_build_checks_can_skip_full_tests(monkeypatch) -> None:  # noqa: ANN001
    monkeypatch.setattr(pre_server_readiness, "_npm_command", lambda: "npm")

    checks = pre_server_readiness.build_checks(include_full_tests=False)

    assert [check.name for check in checks][0] == "python dependency audit"
    assert all(check.name != "full pytest" for check in checks)


def test_main_returns_nonzero_when_a_check_fails(monkeypatch, capsys) -> None:  # noqa: ANN001
    checks = [pre_server_readiness.CommandCheck("forced failure", ["cmd"])]
    monkeypatch.setattr(pre_server_readiness, "build_checks", lambda include_full_tests: checks)
    monkeypatch.setattr(
        pre_server_readiness,
        "run_check",
        lambda check: pre_server_readiness.CommandResult(check.name, 1, check.command),
    )

    exit_code = pre_server_readiness.main(["--skip-tests"])
    output = capsys.readouterr().out

    assert exit_code == 1
    assert "FAIL" in output


def test_main_returns_zero_when_checks_pass(monkeypatch, capsys) -> None:  # noqa: ANN001
    checks = [pre_server_readiness.CommandCheck("forced pass", ["cmd"])]
    monkeypatch.setattr(pre_server_readiness, "build_checks", lambda include_full_tests: checks)
    monkeypatch.setattr(
        pre_server_readiness,
        "run_check",
        lambda check: pre_server_readiness.CommandResult(check.name, 0, check.command),
    )

    exit_code = pre_server_readiness.main(["--skip-tests"])
    output = capsys.readouterr().out

    assert exit_code == 0
    assert "PASS" in output
