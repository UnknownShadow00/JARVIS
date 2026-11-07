"""Cage-only independent process crash points; synthetic keys and disposable state."""
from pathlib import Path
import sys
if not Path('/input/source').is_dir():raise SystemExit('isolated runner required')
sys.path[:0]=['/input/source','/deps']
# Extended by focused process cases; no host services or providers.
