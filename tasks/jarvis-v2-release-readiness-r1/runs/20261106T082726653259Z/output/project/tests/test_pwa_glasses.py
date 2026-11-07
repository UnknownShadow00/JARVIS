from pathlib import Path


def test_glasses_toggle_in_html():
    content = Path("frontend/pwa/index.html").read_text(encoding="utf-8")
    assert "glasses-toggle" in content


def test_glasses_mode_in_js():
    content = Path("frontend/pwa/app.js").read_text(encoding="utf-8")
    assert "glassesMode" in content
    assert "jarvis_glasses_mode" in content
