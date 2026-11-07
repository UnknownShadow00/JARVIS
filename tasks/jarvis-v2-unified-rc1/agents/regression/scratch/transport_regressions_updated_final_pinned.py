import os
os.environ['PYTEST_DISABLE_PLUGIN_AUTOLOAD']='1'
from app.config import settings
settings.logging.audit_log='/scratch/audit.jsonl'
settings.openjarvis.trace_logging_enabled=False
import pytest,json
outcomes=[]
class Results:
    def pytest_runtest_logreport(self,report):
        if report.when=='call' or report.failed or report.skipped:
            outcomes.append({'nodeid':report.nodeid,'when':report.when,'outcome':report.outcome})
class Capture:
    def pytest_sessionfinish(self,session,exitstatus):
        print('UNIFIED_OUTCOMES='+json.dumps({'exitstatus':int(exitstatus),'outcomes':outcomes}))
raise SystemExit(pytest.main(['-q', '--tb=short', '-p', 'pytest_asyncio.plugin', '-p', 'no:cacheprovider', '--basetemp=/scratch/pytest', '/target/tests/test_secure_transport.py::test_actual_ipc_signed_evidence_single_writer_and_public_metadata', '/target/tests/test_secure_transport.py::test_protocol_forgery_and_bounded_frames', '/target/tests/test_secure_transport.py::test_second_allowlisted_endpoint_runs_only_pure_hash', '/target/tests/test_secure_transport.py::test_operator_promoted_evidence_cannot_auto_publish_on_restart', '/target/tests/test_secure_transport.py::test_recovery_permit_expiring_during_verification_rolls_back', '/target/tests/test_secure_transport.py::test_real_offline_cli_reconciles_and_explicitly_publishes_with_identical_replay'], plugins=[Results(),Capture()]))
