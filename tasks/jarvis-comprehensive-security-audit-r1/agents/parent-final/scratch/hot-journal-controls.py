import os
os.environ['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'
import pytest
raise SystemExit(pytest.main(['-q','-p','no:cacheprovider','--basetemp=/scratch/hot-journal-tests',
 '/target/tests/test_recovery_decisions.py::test_independent_sigkill_hot_sqlite_journal_requires_authenticated_recovery[None]',
 '/target/tests/test_recovery_decisions.py::test_independent_sigkill_hot_sqlite_journal_requires_authenticated_recovery[foreign_custody]']))
