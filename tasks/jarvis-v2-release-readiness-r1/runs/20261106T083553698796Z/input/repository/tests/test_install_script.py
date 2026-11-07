import os


def test_install_script_exists() -> None:
    assert os.path.exists("scripts/install.py")


def test_install_script_has_smoke_test() -> None:
    with open("scripts/install.py", encoding="utf-8") as handle:
        assert "pytest" in handle.read()


def test_powershell_wrapper_exists() -> None:
    assert os.path.exists("scripts/install.ps1")
