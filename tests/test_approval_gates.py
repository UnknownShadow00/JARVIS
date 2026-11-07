"""The old public confirmation route cannot activate a real tool."""
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.server import _is_confirmation_required_error,_pending_confirmations,app


def setup_function():_pending_confirmations.clear()
def teardown_function():_pending_confirmations.clear()


def test_pending_dict_starts_empty():assert _pending_confirmations=={}
def test_is_confirmation_error_true():assert _is_confirmation_required_error(Exception('Requires user confirmation'))
def test_is_confirmation_error_false():assert not _is_confirmation_required_error(Exception('blocked'))


def test_confirm_unknown_request_id():
    response=TestClient(app).post('/confirm/badid')
    assert response.status_code==404


def test_confirm_known_request_id_cannot_dispatch():
    _pending_confirmations['abc12345']={'tool':'shell','params':{'command':'synthetic canary'}}
    with patch('app.server.registry.call',side_effect=AssertionError('tool dispatch forbidden')) as call:
        response=TestClient(app).post('/confirm/abc12345')
    assert response.status_code==404
    call.assert_not_called()
