"""Root operator evidence gate; an attestation is not automated qualification.

Codex must not author acceptance records. This reader never loads a token,
creates state, prompts for secrets, or instantiates a transport.
"""
import os
import time

from .protocol import Refusal, document, exact_dict, need
from .runtime import CONFIG
from .securefs import open_checked, read_checked

BINDINGS = {
    'grant_id': str, 'release': str, 'caller_uid': int, 'caller_gid': int,
    'broker_uid': int, 'broker_gid': int, 'operator_reference': str,
}
CHECKS = ('actual_peer_credentials', 'synthetic_secret_denied',
          'code_config_units_protected', 'escalation_review_passed')
RECORD = 'PREISSUANCE-ACCEPTED.json'
ERROR = 'PREISSUANCE_REQUIRED'
ROOT_ONLY = frozenset((0,))


def require_preissuance(settings, *, now=None):
    """Require fresh grant-bound operator evidence with both host markers absent.

    ``checked_at`` is the acceptance time. Successful reading returns no authority
    beyond allowing the separate operator-only issuance routine to continue.
    """
    descriptor = -1
    try:
        descriptor = open_checked(CONFIG, ROOT_ONLY, directory=True)
        # lstat semantics reject any marker entry, including a dangling symlink.
        # Inspect metadata only: never open a credential or marker for its value.
        for marker in ('HOST-PRECHECK', 'HOST-ACTIVATE'):
            try:
                os.stat(marker, dir_fd=descriptor, follow_symlinks=False)
            except FileNotFoundError:
                pass
            else:
                raise Refusal(ERROR)
        value = document(read_checked(CONFIG / RECORD, ROOT_ONLY, mode=0o600, limit=4096), 4096)
        exact_dict(value, (*BINDINGS, 'checked_at', 'expires_at', 'checks'))
        for key, expected_type in BINDINGS.items():
            need(type(value[key]) is expected_type and type(settings[key]) is expected_type and
                 value[key] == settings[key], ERROR)
        for key in ('checked_at', 'expires_at'):
            need(type(value[key]) is int and 0 < value[key] <= 2**53 - 1, ERROR)
        need(type(settings['expires_at']) is int, ERROR)
        current = time.time() if now is None else now
        need(type(current) in (int, float), ERROR)
        need(value['checked_at'] <= current <= value['expires_at'] and
             value['checked_at'] < value['expires_at'] <= value['checked_at'] + 600 and
             value['expires_at'] <= settings['expires_at'], ERROR)
        exact_dict(value['checks'], CHECKS)
        need(all(value['checks'][check] is True for check in CHECKS), ERROR)
    except Exception:
        raise Refusal(ERROR) from None
    finally:
        if descriptor >= 0:
            try:
                os.close(descriptor)
            except OSError:
                raise Refusal(ERROR) from None
