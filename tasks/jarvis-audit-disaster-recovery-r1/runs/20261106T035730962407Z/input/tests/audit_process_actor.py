"""Independent cage-only audit crash helper; extended by process tests."""
from pathlib import Path
if not Path('/input/source').is_dir():raise SystemExit('isolated test runner required')
