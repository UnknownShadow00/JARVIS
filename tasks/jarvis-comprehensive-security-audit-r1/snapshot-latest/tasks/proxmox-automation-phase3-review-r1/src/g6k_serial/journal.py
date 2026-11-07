"""Durable at-most-once reservations and hash-linked audit metadata.

An uncertain/reserved request halts the whole grant, including new request IDs.
There is deliberately no reset, retry, delete, or reconciliation client API.
"""
from contextlib import contextmanager
import fcntl
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import threading
import time

from .protocol import ACTIONS, Refusal, hexid, integer, need
from .securefs import open_checked

SCHEMA = '''
CREATE TABLE metadata (purpose TEXT NOT NULL, grant_id TEXT NOT NULL, revoked INTEGER NOT NULL);
CREATE TABLE requests (id TEXT PRIMARY KEY, action TEXT NOT NULL, uid INTEGER NOT NULL,
 state TEXT NOT NULL CHECK(state IN ('RESERVED','REPORTED','UNKNOWN','ACKED')), report_hash TEXT);
CREATE TABLE events (sequence INTEGER PRIMARY KEY, payload TEXT NOT NULL,
 previous TEXT NOT NULL, digest TEXT NOT NULL);
'''


def initialize(directory, purpose, grant_id):
    """Operator initialization only; existing state is always preserved/refused."""
    need(purpose in ('host', 'worker'), 'STATE_PURPOSE')
    hexid(grant_id)
    directory = Path(directory)
    database, lock = directory / 'ledger.sqlite3', directory / 'operation.lock'
    created = []
    for path in (lock, database):
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
        os.fsync(fd)
        os.close(fd)
        created.append(path)
    conn = sqlite3.connect(str(database))
    try:
        conn.execute('PRAGMA synchronous=EXTRA')
        conn.executescript(SCHEMA)
        conn.execute('INSERT INTO metadata VALUES (?,?,0)', (purpose, grant_id))
        conn.commit()
    finally:
        conn.close()
    fd = os.open(directory, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        os.fsync(fd)
    finally:
        os.close(fd)
    return created


class Ledger:
    def __init__(self, directory, purpose, grant_id, *, anchor=Path('/'), uid=None):
        self.directory = Path(directory)
        self.uid = os.geteuid() if uid is None else uid
        self.purpose = purpose
        self.guard = threading.Lock()
        self.operation_owner = None
        owners = frozenset((0, self.uid))
        fd = open_checked(self.directory, owners, directory=True, anchor=anchor)
        os.close(fd)
        self.lock = open_checked(self.directory / 'operation.lock', owners, mode=0o600, anchor=anchor)
        fd = open_checked(self.directory / 'ledger.sqlite3', owners, mode=0o600, anchor=anchor)
        os.close(fd)
        try:
            self.conn = sqlite3.connect('file:' + str(self.directory / 'ledger.sqlite3') + '?mode=rw',
                                        uri=True, timeout=0.1, isolation_level=None, check_same_thread=False)
            self.conn.execute('PRAGMA trusted_schema=OFF')
            self.conn.execute('PRAGMA synchronous=EXTRA')
            self.conn.execute('PRAGMA journal_mode=DELETE')
            need(self.conn.execute('PRAGMA quick_check').fetchall() == [('ok',)], 'STATE_CORRUPT')
            need(self.conn.execute('SELECT purpose,grant_id FROM metadata').fetchall() == [(purpose, grant_id)],
                 'STATE_BINDING')
            self.verify_audit()
        except (sqlite3.Error, OSError, Refusal):
            if hasattr(self, 'conn'):
                self.conn.close()
            os.close(self.lock)
            raise Refusal('STATE_UNAVAILABLE') from None

    def close(self):
        self.conn.close()
        os.close(self.lock)

    @contextmanager
    def operation(self):
        need(self.guard.acquire(blocking=False), 'BUSY')
        acquired = False
        try:
            try:
                fcntl.flock(self.lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
                acquired = True
            except BlockingIOError:
                raise Refusal('BUSY') from None
            self.operation_owner = threading.get_ident()
            yield
        finally:
            self.operation_owner = None
            if acquired:
                fcntl.flock(self.lock, fcntl.LOCK_UN)
            self.guard.release()

    def verify_audit(self):
        previous = '0' * 64
        for sequence, payload, recorded_previous, digest in self.conn.execute('SELECT * FROM events ORDER BY sequence'):
            calculated = hashlib.sha256((previous + '\n' + payload).encode()).hexdigest()
            need(recorded_previous == previous and calculated == digest, 'AUDIT_CHAIN')
            previous = digest
        return previous

    def _event(self, request_id, action, uid, state, report_hash=None):
        previous = self.conn.execute('SELECT digest FROM events ORDER BY sequence DESC LIMIT 1').fetchone()
        previous = previous[0] if previous else '0' * 64
        payload = json.dumps({'request_id': request_id, 'action': action, 'uid': uid,
                              'state': state, 'at_epoch': int(time.time()), 'report_hash': report_hash},
                             sort_keys=True, separators=(',', ':'))
        digest = hashlib.sha256((previous + '\n' + payload).encode()).hexdigest()
        self.conn.execute('INSERT INTO events(payload,previous,digest) VALUES(?,?,?)', (payload, previous, digest))

    def available(self):
        try:
            need(self.conn.execute('SELECT revoked FROM metadata').fetchall() == [(0,)], 'REVOKED')
            states = ('RESERVED', 'UNKNOWN', 'REPORTED') if self.purpose == 'host' else ('RESERVED', 'UNKNOWN')
            need(self.conn.execute('SELECT count(*) FROM requests WHERE state IN (' +
                                   ','.join('?' for _ in states) + ')', states).fetchone()[0] == 0,
                 'HALTED_UNCERTAIN')
            need(self.conn.execute('SELECT count(*) FROM requests').fetchone()[0] < 10000, 'STATE_CAPACITY')
        except sqlite3.Error:
            raise Refusal('STATE_UNAVAILABLE') from None

    def reserve(self, request_id, action, uid):
        hexid(request_id)
        need(action in ACTIONS, 'ACTION')
        integer(uid, 1)
        try:
            self.conn.execute('BEGIN IMMEDIATE')
            self.available()
            need(self.conn.execute('SELECT 1 FROM requests WHERE id=?', (request_id,)).fetchone() is None, 'REPLAY')
            self.conn.execute('INSERT INTO requests VALUES (?,?,?,\'RESERVED\',NULL)', (request_id, action, uid))
            self._event(request_id, action, uid, 'RESERVED')
            self.conn.execute('COMMIT')
        except (sqlite3.Error, Refusal):
            if self.conn.in_transaction:
                self.conn.execute('ROLLBACK')
            raise Refusal('RESERVATION_REFUSED') from None

    def unseen(self, request_id):
        hexid(request_id)
        try:
            need(self.conn.execute('SELECT 1 FROM requests WHERE id=?', (request_id,)).fetchone() is None, 'REPLAY')
        except sqlite3.Error:
            raise Refusal('STATE_UNAVAILABLE') from None

    def finish(self, request_id, state, report=None):
        need(state in ('REPORTED', 'UNKNOWN'), 'STATE_TRANSITION')
        try:
            self.conn.execute('BEGIN IMMEDIATE')
            row = self.conn.execute('SELECT action,uid,state FROM requests WHERE id=?', (request_id,)).fetchone()
            need(row is not None and row[2] == 'RESERVED', 'STATE_TRANSITION')
            digest = hashlib.sha256(json.dumps(report, sort_keys=True, separators=(',', ':')).encode()).hexdigest() if report is not None else None
            self.conn.execute('UPDATE requests SET state=?,report_hash=? WHERE id=?', (state, digest, request_id))
            self._event(request_id, row[0], row[1], state, digest)
            self.conn.execute('COMMIT')
        except (sqlite3.Error, Refusal):
            if self.conn.in_transaction:
                self.conn.execute('ROLLBACK')
            raise Refusal('AUDIT_UNAVAILABLE') from None

    def revoke(self):
        try:
            self.conn.execute('BEGIN IMMEDIATE')
            self.conn.execute('UPDATE metadata SET revoked=1')
            self._event('0' * 32, 'operator-revoke', 0, 'REVOKED')
            self.conn.execute('COMMIT')
        except sqlite3.Error:
            if self.conn.in_transaction:
                self.conn.execute('ROLLBACK')
            raise Refusal('AUDIT_UNAVAILABLE') from None

    def acknowledge(self, request_id, uid):
        """Only the authenticated client receipt closes a host-side transaction."""
        with self.operation():
            self.acknowledge_held(request_id, uid)

    def acknowledge_held(self, request_id, uid):
        """Commit a receipt while the conversation still owns the operation."""
        need(self.operation_owner == threading.get_ident(), 'OPERATION_LOCK_REQUIRED')
        hexid(request_id)
        need(self.purpose == 'host', 'STATE_PURPOSE')
        try:
            self.conn.execute('BEGIN IMMEDIATE')
            row = self.conn.execute('SELECT action,uid,state FROM requests WHERE id=?', (request_id,)).fetchone()
            need(row is not None and row[1] == uid and row[2] == 'REPORTED', 'RECEIPT')
            self.conn.execute("UPDATE requests SET state='ACKED' WHERE id=?", (request_id,))
            self._event(request_id, row[0], uid, 'ACKED')
            self.conn.execute('COMMIT')
        except (sqlite3.Error, Refusal):
            if self.conn.in_transaction:
                self.conn.execute('ROLLBACK')
            raise Refusal('RECEIPT') from None
