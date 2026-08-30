from pathlib import Path


def test_workflow_file_exists():
    assert Path(".github/workflows/tests.yml").exists()


def test_workflow_has_pytest():
    workflow = Path(".github/workflows/tests.yml").read_text(encoding="utf-8")
    assert "pytest" in workflow


def test_workflow_excludes_only_manual_or_hardware_markers():
    workflow = Path(".github/workflows/tests.yml").read_text(encoding="utf-8")
    assert "not manual and not hardware" in workflow
    assert "--ignore=tests/e2e" in workflow
    assert "--ignore=tests/stress" in workflow
    assert "--ignore=tests/perf" in workflow


def test_issue_templates_exist():
    assert Path(".github/ISSUE_TEMPLATE/bug_report.md").exists()
    assert Path(".github/ISSUE_TEMPLATE/feature_request.md").exists()
