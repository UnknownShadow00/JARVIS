import os
os.environ['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'
from app.config import settings
settings.logging.audit_log='/scratch/audit.jsonl'
settings.openjarvis.trace_logging_enabled=False
import pytest
raise SystemExit(pytest.main(['-q', '-p', 'no:cacheprovider', '--basetemp=/scratch/packaged-safety', '/target/tests/test_audit_integration_fixes.py::test_effectful_resource_http_is_inert_even_with_bearer[/resource/shutdown]', '/target/tests/test_audit_integration_fixes.py::test_stop_requires_configured_identity', '/target/tests/test_audit_integration_fixes.py::test_malformed_websocket_closes_and_removes_manager_entry[value0]', '/target/tests/test_audit_integration_fixes.py::test_cli_post_auth_and_status_failure_never_falls_back[401]', '/target/tests/test_audit_integration_fixes.py::test_untracked_same_entrypoint_child_is_never_terminated', '/target/tests/test_audit_integration_fixes.py::test_only_positive_native_child_lease_allows_signal[False]', '/target/tests/test_audit_integration_fixes.py::test_vad_continuous_speech_respects_frame_and_callback_queue_bounds', '/target/tests/test_audit_integration_fixes.py::test_vad_active_capture_cancellation_is_checked_each_frame']))
