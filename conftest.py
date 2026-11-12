"""Fail closed before pytest imports application, historical or live test modules.

Supported execution is scripts/offline_acceptance.py. The qualified child has a
read-only /source mount, /runner.py, and an explicit pinned suite. An environment
variable alone never enables direct host pytest. This is not a compromised-host
defense; deliberately disabling pytest configuration/plugins is unsupported.
"""
import json
from pathlib import Path
import sys

import pytest

REFUSAL = 'Direct pytest is disabled; use python3 scripts/offline_acceptance.py --output-dir NEW_PATH.'


def _gate_context():
    return (Path(__file__).resolve() == Path('/source/conftest.py')
            and sys.argv[0] == '/runner.py' and len(sys.argv) == 6
            and sys.argv[1] == '--child' and Path('/inventory.json').is_file())


def _allowed_paths():
    # The parent verifies the pinned inventory and all sources; the child
    # independently loads that same immutable inventory before pytest starts.
    try:
        suite = json.loads(Path('/inventory.json').read_text())['suites'][sys.argv[3]]
        return {Path('/source') / node.split('::', 1)[0] for node in suite['nodeids']}
    except (OSError, ValueError, KeyError, IndexError, TypeError):
        raise pytest.UsageError('Invalid qualified collection policy.') from None


def permitted(path, allowed):
    """Permit exact reviewed files and their directory ancestors, never links."""
    path = Path(path)
    if path.is_symlink():
        return False
    return path in allowed or path.is_dir() and any(path in item.parents for item in allowed)


def pytest_configure(config):
    if not _gate_context():
        raise pytest.UsageError(REFUSAL)
    config._jarvis_allowed_paths = _allowed_paths()


def pytest_ignore_collect(collection_path, config):
    return not permitted(collection_path, config._jarvis_allowed_paths)


def pytest_collectstart(collector):
    # pytest can bypass ignore hooks for explicit filename arguments. Refuse
    # those collectors before Module.collect imports their Python code.
    path = getattr(collector, 'path', None)
    if path is not None and Path(path).is_file() and not permitted(path, collector.config._jarvis_allowed_paths):
        raise pytest.UsageError('Test module is outside the qualified suite.')
