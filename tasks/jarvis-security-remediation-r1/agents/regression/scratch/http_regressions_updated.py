import os
os.environ['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'
from app.config import settings
settings.logging.audit_log='/scratch/audit.jsonl'
settings.openjarvis.trace_logging_enabled=False
import pytest
raise SystemExit(pytest.main(['-q', '--tb=short', '-p', 'pytest_asyncio.plugin', '-p', 'no:cacheprovider', '--basetemp=/scratch/pytest', '/target/tests/test_authority_http_security.py', '/target/tests/test_ue5_security.py', '/target/tests/test_ue5_bridge.py', '/target/tests/test_server_auth.py', '/target/tests/test_enrollment_app.py', '/target/tests/test_release_security.py', '/target/tests/test_storage_ancestry_security.py']))
