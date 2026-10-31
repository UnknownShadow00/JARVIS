"""Installed entry points. Paths are fixed; templates remain disabled by default."""
import grp
import hashlib
import os
from pathlib import Path
import pwd
import select
import signal
import socket
import struct
import termios
import threading
import time
import tty

from .broker import Broker
from .journal import Ledger, initialize
from .policy import config
from .protocol import (ACTIONS, BEACON, TARGET, Deadline, Lines, Refusal, decode, document, encode, exact_dict,
                       need, public_metadata, validate_report)
from .securefs import SOURCE_FILES, open_checked, read_checked, verify_release
from .transport import PVETransport
from .worker import Inspector, Worker

INSTALL = Path('/opt/g6k-serial')
CONFIG = Path('/etc/g6k-serial')
HOST_STATE = Path('/var/lib/g6k-serial-host')
WORKER_STATE = Path('/var/lib/g6k-serial-worker')
SOCKET = '/run/g6k-serial/request.sock'
PRECHECK_SOCKET = '/run/g6k-serial/precheck.sock'
PRIVILEGED_GROUPS = frozenset(('root', 'sudo', 'wheel', 'docker', 'lxd', 'incus-admin', 'libvirt', 'disk'))


def peer_credentials(conn):
    raw = conn.getsockopt(socket.SOL_SOCKET, socket.SO_PEERCRED, struct.calcsize('3i'))
    pid, uid, gid = struct.unpack('3i', raw)
    # CPython's getsockopt byte buffer is limited to1024. More than256 groups
    # produces a kernel error and refuses authentication rather than truncating.
    groups_raw = conn.getsockopt(socket.SOL_SOCKET, getattr(socket, 'SO_PEERGROUPS', 59), 1024)
    need(len(groups_raw) % 4 == 0, 'PEER_GROUPS')
    groups = struct.unpack(str(len(groups_raw) // 4) + 'I', groups_raw)
    return uid, gid, frozenset(groups)


def safe_account(uid, gid):
    entry = pwd.getpwuid(uid)
    need(uid > 0 and gid > 0 and entry.pw_gid == gid, 'ACCOUNT')
    memberships = [g for g in grp.getgrall() if entry.pw_name in g.gr_mem or g.gr_gid == gid]
    need(not any(g.gr_name in PRIVILEGED_GROUPS for g in memberships), 'PRIVILEGED_ACCOUNT')
    need(all(g.gr_gid == gid for g in memberships), 'SUPPLEMENTARY_GROUPS')


def authorize_peer(conn, grant):
    uid, gid, groups = peer_credentials(conn)
    need(uid == grant['caller_uid'] and gid == grant['caller_gid'] and groups <= {gid}, 'PEER_IDENTITY')
    safe_account(uid, gid)
    return uid


def settings(worker=False, *, precheck=False):
    path = CONFIG / ('worker.json' if worker else 'host.json')
    raw = read_checked(path, limit=8192)
    value = document(raw, 8192)
    if precheck:
        need(not worker and value.get('enabled') is False, 'PRECHECK_DISABLED_GRANT_REQUIRED')
        config({**value, 'enabled': True})
    else:
        config(value, worker=worker)
    expected_uid = value['worker_uid'] if worker else value['broker_uid']
    expected_gid = value['worker_gid'] if worker else value['broker_gid']
    need(os.geteuid() == expected_uid and os.getegid() == expected_gid and os.geteuid() != 0, 'SERVICE_IDENTITY')
    need(set(os.getgroups()) <= {expected_gid}, 'SERVICE_GROUPS')
    safe_account(expected_uid, expected_gid)
    if not worker:
        safe_account(value['caller_uid'], value['caller_gid'])
    # Independent root-controlled activation marker; installation never creates it.
    marker = CONFIG / ('HOST-PRECHECK' if precheck else 'WORKER-ACTIVATE' if worker else 'HOST-ACTIVATE')
    expiry_deadline = time.monotonic() + max(0, value['expires_at'] - time.time())

    def revalidate():
        need(time.monotonic() < expiry_deadline, 'GRANT_EXPIRED')
        need(read_checked(path, limit=8192) == raw, 'GRANT_CHANGED')
        need(read_checked(marker, limit=64) == (value['grant_id'] + '\n').encode(), 'NOT_ACTIVATED')
        if precheck:
            need(not os.path.lexists(CONFIG / 'HOST-ACTIVATE'), 'PRECHECK_ACTIVATION_CONFLICT')
            config({**value, 'enabled': True})
        else:
            config(value, worker=worker)
        verify_release(INSTALL, value['release'])

    revalidate()
    return value, revalidate


def connection(conn, broker, *, authorize=authorize_peer, precheck=False):
    """One request and authenticated receipt per AF_UNIX connection."""
    with conn:
        try:
            uid = authorize(conn, broker.grant)
            deadline = Deadline(2)

            def receive(d):
                conn.settimeout(d.remaining())
                return conn.recv(2048)

            lines = Lines(receive, limit=1024, budget=2048)
            request = lines.raw_line(deadline)
            need(not lines.buffer, 'MULTIPLE_REQUESTS')
            if precheck:
                from .protocol import public_request
                parsed = public_request(request)
                broker.revalidate()
                need(broker.grant['enabled'] is False, 'PRECHECK_DISABLED_GRANT_REQUIRED')
                conn.settimeout(1)
                conn.sendall(encode({'v': 1, 'result': 'PRECHECK_AUTHENTICATED', 'caller_uid': uid,
                                    'request_id': parsed['request_id'], 'transport_enabled': False}))
                return
            with broker.conversation(request, uid) as result:
                conn.settimeout(Deadline(2).remaining())
                conn.sendall(encode(result))
                if result['result'] == 'REPORTED':
                    receipt = lines.line(Deadline(2))
                    exact_dict(receipt, ('v', 'type', 'request_id'))
                    need(type(receipt['v']) is int and receipt['v'] == 1 and receipt['type'] == 'receipt' and
                         receipt['request_id'] == result['request_id'] and not lines.buffer, 'RECEIPT')
                    broker.ledger.acknowledge_held(result['request_id'], uid)
        except (Exception, KeyboardInterrupt):
            # A missing receipt leaves REPORTED pending and halts future requests.
            # The generic rejection itself may be lost; never retry delivery.
            try:
                conn.settimeout(0.1)
                conn.sendall(encode({'v': 1, 'result': 'REJECTED'}))
            except Exception:
                pass


class DisabledTransport:
    """Structural no-transport capability used only during pre-issuance checks."""
    def snapshot(self, deadline):
        raise Refusal('PRECHECK_NO_TRANSPORT')

    def open_serial(self, deadline):
        raise Refusal('PRECHECK_NO_TRANSPORT')

    def abort(self):
        pass


def make_broker(grant, revalidate, *, precheck=False):
    if precheck:
        need(grant['enabled'] is False, 'PRECHECK_DISABLED_GRANT_REQUIRED')
        need(not os.path.lexists(HOST_STATE / 'token.json'), 'PRECHECK_CREDENTIAL_ALREADY_PRESENT')
        return Broker(grant, None, DisabledTransport(), revalidate)
    ledger = Ledger(HOST_STATE, 'host', grant['grant_id'])
    try:
        credential = document(read_checked(HOST_STATE / 'token.json', frozenset((0, os.geteuid())), mode=0o600, limit=4096), 4096)
        ca = read_checked(CONFIG / 'pve-root-ca.pem', limit=65536)
        return Broker(grant, ledger, PVETransport(credential, ca, grant), revalidate)
    except BaseException:
        ledger.close()
        raise


def host(*, precheck=False):
    grant, revalidate = settings(precheck=precheck)
    from .hardening import undumpable
    undumpable()
    broker = make_broker(grant, revalidate, precheck=precheck)
    ledger, transport = broker.ledger, broker.transport
    need(os.environ.get('LISTEN_PID') == str(os.getpid()) and os.environ.get('LISTEN_FDS') == '1', 'SOCKET_ACTIVATION')
    listener = socket.socket(fileno=3)
    need(listener.family == socket.AF_UNIX and listener.type == socket.SOCK_STREAM and
         listener.getsockname() == (PRECHECK_SOCKET if precheck else SOCKET), 'LISTEN_SOCKET')
    listener.settimeout(0.25)
    stop = threading.Event()
    active = set()
    guard = threading.RLock()  # SIGTERM can interrupt the main thread while it owns this lock.
    slots = threading.BoundedSemaphore(4)

    def shutdown(*_):
        stop.set()
        transport.abort()
        with guard:
            for conn in active:
                try:
                    conn.shutdown(socket.SHUT_RDWR)
                except OSError:
                    pass

    def watch():
        while not stop.wait(0.1):
            try:
                revalidate()
            except Exception:
                shutdown()

    def run(conn):
        try:
            connection(conn, broker, precheck=precheck)
        finally:
            with guard:
                active.discard(conn)
            slots.release()

    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    watcher = threading.Thread(target=watch, daemon=True)
    watcher.start()
    threads = []
    try:
        while not stop.is_set():
            try:
                conn, _ = listener.accept()
            except socket.timeout:
                continue
            if not slots.acquire(blocking=False):
                conn.close()
                continue
            with guard:
                active.add(conn)
            thread = threading.Thread(target=run, args=(conn,), daemon=True)
            thread.start()
            threads = [t for t in threads if t.is_alive()] + [thread]
    finally:
        shutdown()
        listener.close()
        for thread in threads:
            thread.join(timeout=6)
        if ledger is not None:
            ledger.close()


def fd_read(fd, maximum, deadline):
    while True:
        readable, _, _ = select.select([fd], [], [], deadline.remaining())
        need(bool(readable), 'TIMEOUT')
        raw = os.read(fd, maximum)
        need(bool(raw), 'CHANNEL')
        return raw


def fd_write(fd, raw, deadline):
    while raw:
        _, writable, _ = select.select([], [fd], [], deadline.remaining())
        need(bool(writable), 'TIMEOUT')
        sent = os.write(fd, raw)
        need(sent > 0, 'CHANNEL')
        raw = raw[sent:]


def worker_loop(worker, input_fd, output_fd, *, stopped=lambda: False, action_alarm=False):
    """Testable real FD loop; each advertisement session is single use."""
    while not stopped():
        # Only a fixed beacon is emitted while idle. A blocked output retains
        # at most one unfinished beacon and never kills or grows an idle worker.
        pending = BEACON
        next_beacon = time.monotonic()
        while not stopped():
            worker.revalidate()
            readable, writable, _ = select.select([input_fd], [output_fd] if pending else [], [], 0.25)
            if readable:
                break
            if writable:
                try:
                    pending = pending[os.write(output_fd, pending):]
                except BlockingIOError:
                    pass
            if not pending and time.monotonic() >= next_beacon:
                pending = BEACON
                next_beacon = time.monotonic() + 0.25
        if stopped():
            return
        # Fresh framing/budget for this exchange, not for the worker lifetime.
        lines = Lines(lambda d: fd_read(input_fd, 4096, d), limit=4096, budget=8192)
        handshake = lines.line(Deadline(2))
        need(not lines.buffer, 'MULTIPLE_REQUESTS')
        synchronized = worker.synchronize(handshake)
        if pending:
            fd_write(output_fd, pending, Deadline(1))
        fd_write(output_fd, encode(synchronized), Deadline(1))
        try:
            request = lines.line(Deadline(2))
        except Refusal as error:
            # No action/reservation yet. An abandoned empty handshake can return
            # to idle; partial/malformed action input must not be discarded.
            if str(error) == 'TIMEOUT' and not lines.buffer:
                worker.discard_session()
                continue
            raise
        need(not lines.buffer, 'MULTIPLE_REQUESTS')
        if action_alarm:
            signal.setitimer(signal.ITIMER_REAL, 5)
        try:
            result = worker.process(request)
        finally:
            if action_alarm:
                signal.setitimer(signal.ITIMER_REAL, 0)
        fd_write(output_fd, encode(result), Deadline(1))


def worker():
    binding, revalidate = settings(worker=True)
    from .hardening import install_worker_guard
    install_worker_guard()
    ledger = Ledger(WORKER_STATE, 'worker', binding['grant_id'])
    need(os.isatty(0) and os.isatty(1), 'WORKER_TTY')
    need(os.ttyname(0) == '/dev/ttyS0' and os.ttyname(1) == '/dev/ttyS0', 'WORKER_CHANNEL')
    # O_NONBLOCK makes the select deadlines effective for partial reads/writes.
    os.set_blocking(0, False)
    os.set_blocking(1, False)
    tty.setraw(0, termios.TCSANOW)
    attributes = termios.tcgetattr(0)
    attributes[0] &= ~(termios.IXON | termios.IXOFF | getattr(termios, 'IXANY', 0))
    attributes[2] |= termios.CLOCAL | termios.CREAD
    attributes[2] &= ~getattr(termios, 'CRTSCTS', 0)
    attributes[4] = attributes[5] = termios.B115200
    termios.tcsetattr(0, termios.TCSANOW, attributes)
    def timeout(*_):
        raise Refusal('WORKER_ACTION_TIMEOUT')
    signal.signal(signal.SIGALRM, timeout)
    try:
        worker_loop(Worker(binding, ledger, Inspector(binding), revalidate), 0, 1, action_alarm=True)
    finally:
        ledger.close()


def client(action, request_id, *, precheck=False):
    from .protocol import hexid
    need(action in ACTIONS, 'ACTION')
    hexid(request_id)
    grant = document(read_checked(CONFIG / 'host.json', limit=8192), 8192)
    if precheck:
        need(grant.get('enabled') is False, 'PRECHECK_DISABLED_GRANT_REQUIRED')
        config({**grant, 'enabled': True})
    else:
        config(grant)
    conn = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    deadline = Deadline(10)
    try:
        conn.settimeout(deadline.remaining())
        conn.connect(PRECHECK_SOCKET if precheck else SOCKET)
        uid, gid, _ = peer_credentials(conn)
        # systemd creates/listens on the socket as root before handing fd3 to
        # the non-root broker; SO_PEERCRED can therefore report PID1's UID/GID.
        need((uid, gid) in ((0, 0), (grant['broker_uid'], grant['broker_gid'])), 'BROKER_IDENTITY')
        conn.sendall(encode({'v': 1, **TARGET, 'action': action, 'request_id': request_id}, 1024))
        def receive(d):
            conn.settimeout(d.remaining())
            return conn.recv(4096)
        lines = Lines(receive)
        result = lines.line(deadline)
        if precheck:
            exact_dict(result, ('v', 'result', 'caller_uid', 'request_id', 'transport_enabled'))
            need(type(result['v']) is int and result['v'] == 1 and
                 result['result'] == 'PRECHECK_AUTHENTICATED' and
                 type(result['caller_uid']) is int and result['caller_uid'] == grant['caller_uid'] and
                 result['transport_enabled'] is False and result['request_id'] == request_id and not lines.buffer,
                 'PRECHECK_RESULT')
            return result
        if result.get('result') == 'REPORTED':
            exact_dict(result, ('v', 'result', 'request_id', 'action', 'guest_report_untrusted', 'report'))
            need(type(result['v']) is int and result['v'] == 1 and result['request_id'] == request_id and
                 result['action'] == action and result['guest_report_untrusted'] is True, 'CLIENT_REPORT')
            if action == 'identity':
                public_metadata(result['report'])
                need(result['report']['machine_id'] == grant['machine_id'] and
                     result['report']['release'] == grant['release'] and
                     result['report']['worker_uid'] == grant['worker_uid'], 'CLIENT_REPORT')
            else:
                validate_report(action, result['report'], {})
            need(not lines.buffer, 'CLIENT_REPORT')
            conn.sendall(encode({'v': 1, 'type': 'receipt', 'request_id': request_id}))
            return result
        need(result.get('result') in ('UNKNOWN', 'REJECTED'), 'CLIENT_REPORT')
        need(set(result) <= {'v', 'result', 'request_id'} and type(result.get('v')) is int and result['v'] == 1 and
             result.get('request_id', request_id) == request_id, 'CLIENT_REPORT')
        return result
    except Exception:
        return {'v': 1, 'result': 'UNKNOWN', 'request_id': request_id}
    finally:
        conn.close()


def initialize_state(worker=False):
    need(os.geteuid() == 0, 'OPERATOR_ROOT_REQUIRED')
    path = CONFIG / ('worker.json' if worker else 'host.json')
    value = document(read_checked(path, limit=8192), 8192)
    need(value.get('enabled') is False, 'INSTALL_DISABLED_CONFIG_REQUIRED')
    config({**value, 'enabled': True}, worker=worker)
    verify_release(INSTALL, value['release'])
    directory = WORKER_STATE if worker else HOST_STATE
    uid = value['worker_uid'] if worker else value['broker_uid']
    gid = value['worker_gid'] if worker else value['broker_gid']
    safe_account(uid, gid)
    fd = open_checked(directory, frozenset((0, uid)), directory=True)
    os.close(fd)
    created = initialize(directory, 'worker' if worker else 'host', value['grant_id'])
    for path in created:
        os.chown(path, uid, gid, follow_symlinks=False)


def revoke(worker=False):
    need(os.geteuid() == 0, 'OPERATOR_ROOT_REQUIRED')
    marker = CONFIG / ('WORKER-ACTIVATE' if worker else 'HOST-ACTIVATE')
    # No state deletion. The marker is public authorization, never a credential.
    raw = read_checked(marker, limit=64)
    need(len(raw) == 33, 'ACTIVATION_MARKER')
    marker.unlink()
    fd = os.open(CONFIG, os.O_RDONLY | os.O_DIRECTORY)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def probe_paths():
    """Unprivileged, fixed-path synthetic-canary checks; never opens a token."""
    grant = document(read_checked(CONFIG / 'host.json', limit=8192), 8192)
    need(grant.get('enabled') is False, 'PRECHECK_DISABLED_GRANT_REQUIRED')
    config({**grant, 'enabled': True})
    need(os.geteuid() == grant['caller_uid'] and os.getegid() == grant['caller_gid'] and
         set(os.getgroups()) <= {grant['caller_gid']}, 'PEER_IDENTITY')
    safe_account(grant['caller_uid'], grant['caller_gid'])
    def denied(path, flags):
        try:
            fd = os.open(path, flags | os.O_NOFOLLOW | os.O_CLOEXEC | os.O_NONBLOCK)
        except PermissionError:
            return True
        except OSError:
            return False  # Absence/type errors are not proof of access denial.
        os.close(fd)
        return False
    return {'synthetic_secret_denied': denied(HOST_STATE / 'secret-canary.txt', os.O_RDONLY),
            'source_not_writable': all(denied(INSTALL / p, os.O_WRONLY) for p in SOURCE_FILES),
            'config_not_writable': denied(CONFIG / 'host.json', os.O_WRONLY),
            'units_not_writable': all(denied(Path('/etc/systemd/system') / p, os.O_WRONLY) for p in
                                      ('g6k-serial.service', 'g6k-serial.socket',
                                       'g6k-serial-precheck.service', 'g6k-serial-precheck.socket')),
            'protected_directories_not_writable': all(not os.access(p, os.W_OK) for p in
                                                      (INSTALL, CONFIG, HOST_STATE))}
