"""Operator-root-only credential issuance. Never used by broker or worker.

No PVE passwords, no observer credential access, no command-line/env secrets.
Existing private management session ticket/CSRF are read through /dev/tty only.
Token output goes directly to an exclusive protected file; no stdout/tracebacks.
"""
import getpass
import hashlib
import json
import os
import re
import ssl
import warnings
from urllib.parse import urlencode

from .policy import config, token
from .protocol import Deadline, Refusal, document, need
from .runtime import CONFIG, HOST_STATE, INSTALL, safe_account
from .preissuance import require_preissuance
from .securefs import open_checked, read_checked, verify_release
from .transport import ADDRESS, SERVER_NAME, Wire, http_body, http_head


def issue(*, prompt=getpass.getpass, dial=None):
    need(os.geteuid() == 0, 'OPERATOR_ROOT_REQUIRED')
    need(os.isatty(0) and os.isatty(2), 'PRIVATE_TTY_REQUIRED')
    from .hardening import undumpable
    undumpable()
    settings = document(read_checked(CONFIG / 'host.json', limit=8192), 8192)
    need(settings.get('enabled') is False, 'INSTALL_DISABLED_CONFIG_REQUIRED')
    config({**settings, 'enabled': True})
    safe_account(settings['broker_uid'], settings['broker_gid'])
    safe_account(settings['caller_uid'], settings['caller_gid'])
    verify_release(INSTALL, settings['release'])
    ca = read_checked(CONFIG / 'pve-root-ca.pem')
    need(hashlib.sha256(ca).hexdigest() == settings['ca_sha256'], 'TLS_CA_PIN')
    context = ssl.create_default_context(cadata=ca.decode('ascii'))
    context.minimum_version = ssl.TLSVersion.TLSv1_2
    require_preissuance(settings)
    parent = open_checked(HOST_STATE, frozenset((0, settings['broker_uid'])), directory=True)
    fd = -1
    wire = None
    try:
        # Reserve output before the API call; never silently overwrite a partial
        # result or retry a possibly successful credential creation.
        fd = os.open('token.json', os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC,
                     0o600, dir_fd=parent)
        with warnings.catch_warnings():
            warnings.simplefilter('error', getpass.GetPassWarning)
            session = prompt('Existing private PVEAuthCookie (hidden; never a password): ')
            csrf = prompt('Existing private CSRFPreventionToken (hidden): ')
        need(type(session) is str and re.fullmatch('[!-~]{16,4096}', session) and
             ';' not in session and type(csrf) is str and re.fullmatch('[A-Za-z0-9+/:=._-]{16,4096}', csrf),
             'PRIVATE_SESSION_FORMAT')
        # Private prompts may block indefinitely. Recheck root-controlled policy
        # and fresh operator evidence after that delay, before opening a network.
        try:
            current = document(read_checked(CONFIG / 'host.json', limit=8192), 8192)
            need(current.get('enabled') is False and current == settings, 'PREISSUANCE_REQUIRED')
            config({**current, 'enabled': True})
            safe_account(settings['broker_uid'], settings['broker_gid'])
            safe_account(settings['caller_uid'], settings['caller_gid'])
            verify_release(INSTALL, settings['release'])
            current_ca = read_checked(CONFIG / 'pve-root-ca.pem')
            need(current_ca == ca and hashlib.sha256(current_ca).hexdigest() == settings['ca_sha256'],
                 'PREISSUANCE_REQUIRED')
            require_preissuance(settings)
        except Exception:
            raise Refusal('PREISSUANCE_REQUIRED') from None
        deadline = Deadline(10)
        if dial is None:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.settimeout(deadline.remaining())
                sock.connect(ADDRESS)
                wire = Wire(context.wrap_socket(sock, server_hostname=SERVER_NAME))
            except BaseException:
                sock.close()
                raise Refusal('TLS_CONNECTION') from None
        else:
            wire = dial(deadline)
        body = urlencode({'privsep': '1', 'expire': settings['expires_at']}).encode('ascii')
        request = ('POST /api2/json/access/users/g6k-bridge164@pve/token/serial HTTP/1.1\r\n'
                   'Host: pve:8006\r\nCookie: PVEAuthCookie=' + session + '\r\nCSRFPreventionToken: ' + csrf +
                   '\r\nAccept-Encoding: identity\r\nConnection: close\r\nContent-Type: application/x-www-form-urlencoded\r\n'
                   'Content-Length: ' + str(len(body)) + '\r\n\r\n').encode('ascii')
        wire.send(request + body, deadline)
        status, headers = http_head(wire, deadline)
        need(status == 200, 'PROVISION_API_RESPONSE')
        from .protocol import _pairs
        value = json.loads(http_body(wire, headers, deadline), object_pairs_hook=_pairs)
        need(type(value) is dict and type(value.get('data')) is dict, 'PROVISION_RESPONSE')
        data = value['data']
        credential = token({'id': data.get('full-tokenid'), 'secret': data.get('value')})
        info = data.get('info')
        need(type(info) is dict and ((type(info.get('privsep')) is int and info['privsep'] == 1) or
             info.get('privsep') is True) and type(info.get('expire')) is int and
             info['expire'] == settings['expires_at'], 'PROVISION_POLICY')
        raw = json.dumps(credential, sort_keys=True, separators=(',', ':')).encode('ascii') + b'\n'
        with os.fdopen(fd, 'wb', closefd=False) as stream:
            stream.write(raw)
            stream.flush()
        os.fchmod(fd, 0o600)
        os.fchown(fd, settings['broker_uid'], settings['broker_gid'])
        os.fsync(fd)
        os.fsync(parent)
        return 'CREDENTIAL_STORED_NO_VALUE_OUTPUT'
    finally:
        if wire is not None:
            wire.close()
        if fd >= 0:
            os.close(fd)
        os.close(parent)
