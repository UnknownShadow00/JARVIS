import os
os.environ['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'
from app.config import settings
settings.logging.audit_log='/scratch/audit.jsonl'
settings.openjarvis.trace_logging_enabled=False
import pytest
raise SystemExit(pytest.main(['-q','--tb=short','-p','no:cacheprovider','--basetemp=/scratch/pytest','/target/tests/test_ue5_security.py','-k','binary_frames or cancellation']))
