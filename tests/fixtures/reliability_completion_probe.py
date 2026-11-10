"""Intentionally incomplete/unsafe outputs; selected only by explicit probe mode."""
import os
import pytest

SYNTHETIC_SECRET = 'SYNTHETIC_PRIVATE_PROBE'


@pytest.fixture
def exit_setup():
    pytest.exit('synthetic setup interruption', returncode=0)


def test_early_setup(exit_setup):
    pass


def test_early_call():
    pytest.exit('synthetic call interruption', returncode=0)


@pytest.fixture
def exit_teardown():
    yield
    pytest.exit('synthetic teardown interruption', returncode=0)


def test_early_teardown(exit_teardown):
    pass


def test_final_exit_control():
    pass


def test_final_exit_last():
    pytest.exit('synthetic last-case interruption', returncode=0)


def test_skip():
    pytest.skip(SYNTHETIC_SECRET)


def test_crash():
    os._exit(0)  # Successful OS exit is still missing terminal evidence.


def test_interrupt():
    raise KeyboardInterrupt(SYNTHETIC_SECRET)


def test_leak():
    raise RuntimeError("No module named '" + SYNTHETIC_SECRET + "'")


@pytest.mark.parametrize('value', [SYNTHETIC_SECRET], ids=[SYNTHETIC_SECRET])
def test_parameter_secret(value):
    os.environ['SYNTHETIC_REVIEW_TOKEN'] = value
    class SYNTHETIC_PRIVATE_EXCEPTION(RuntimeError):
        pass
    raise SYNTHETIC_PRIVATE_EXCEPTION(value)


def test_worker_crash():
    import signal
    os.kill(os.getpid(), signal.SIGKILL)


def test_partial_output(request):
    request.config.pluginmanager.getplugin('capturemanager').suspend_global_capture()
    os.write(1, b'{"protocol":')
    os._exit(0)


def test_mismatched_count(request):
    class WrongCount:
        @pytest.hookimpl(tryfirst=True)
        def pytest_sessionfinish(self, session, exitstatus):
            session.testscollected += 1
    request.config.pluginmanager.register(WrongCount())


def test_session_exit(request):
    class ExitAtSessionFinish:
        def pytest_sessionfinish(self, session, exitstatus):
            pytest.exit('synthetic session interruption', returncode=0)
    request.config.pluginmanager.register(ExitAtSessionFinish())
