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
raise SystemExit(pytest.main(['-q', '--tb=short', '-p', 'pytest_asyncio.plugin', '-p', 'no:cacheprovider', '--basetemp=/scratch/pytest', '/target/tests/test_execution_pipeline.py::test_real_api_worker_receipts_and_restart', '/target/tests/test_execution_pipeline.py::test_scheduler_callback_creates_authorized_execution', '/target/tests/test_execution_pipeline.py::test_scheduled_cancellation_policy_and_stopped_admission', '/target/tests/test_execution_pipeline.py::test_admission_body_stream_bound_precedes_json', '/target/tests/test_execution_pipeline.py::test_public_mutations_cannot_reserve_internal_phase_receipts', '/target/tests/test_operator_app.py', '/target/tests/test_audit_integration_fixes.py'], plugins=[Results(),Capture()]))
