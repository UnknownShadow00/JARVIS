"""SO_PEERCRED is the caller identity; guest text is never executable input."""
import secrets
from contextlib import ExitStack, contextmanager, nullcontext

from .policy import config, vm_state
from .protocol import (Deadline, Refusal, binding, encode, need, public_request, ready, response)


class Broker:
    def __init__(self, grant, ledger, transport, revalidate=lambda: None):
        self.grant = grant
        self.ledger = ledger
        self.transport = transport
        self.revalidate = revalidate

    @contextmanager
    def conversation(self, raw, peer_uid):
        """Serialize dispatch through the authenticated local receipt commit."""
        with ExitStack() as stack:
            try:
                stack.enter_context(self.ledger.operation())
            except Refusal:
                yield {'v': 1, 'result': 'REJECTED'}
                return
            yield self._handle(raw, peer_uid, already_locked=True)

    def handle(self, raw, peer_uid):
        return self._handle(raw, peer_uid)

    def _handle(self, raw, peer_uid, *, already_locked=False):
        request = None
        reserved = False
        channel = None
        try:
            request = public_request(raw)
            need(type(peer_uid) is int and peer_uid == self.grant['caller_uid'], 'CALLER_UID')
            need(request['action'] in self.grant['actions'], 'CATALOG')
            with (nullcontext() if already_locked else self.ledger.operation()):
                try:
                    deadline = Deadline()
                    config(self.grant)
                    self.revalidate()
                    self.ledger.available()
                    self.ledger.unseen(request['request_id'])
                    before = vm_state(self.transport.snapshot(deadline))
                    channel = self.transport.open_serial(deadline)
                    challenge = secrets.token_hex(16)
                    advertisement = ready(channel.synchronize(request, self.grant, peer_uid, challenge, deadline), self.grant)
                    context = binding(request, advertisement, self.grant, peer_uid, challenge)
                    # Recheck grant/source/revocation immediately before durable reservation and send.
                    config(self.grant)
                    self.revalidate()
                    deadline.remaining()
                    self.ledger.reserve(request['request_id'], request['action'], peer_uid)
                    reserved = True
                    channel.send({'v': 1, 'type': 'inspect', 'binding': context, 'action': request['action']}, deadline)
                    reply = channel.receive(deadline)
                    report = response(reply, context, request['action'])
                    config(self.grant)
                    self.revalidate()
                    after = vm_state(self.transport.snapshot(deadline))
                    need(before[0] == after[0] and after[1] >= before[1], 'PVE_STATE_DRIFT')
                    deadline.remaining()
                    self.ledger.finish(request['request_id'], 'REPORTED', report)
                    return {'v': 1, 'result': 'REPORTED', 'request_id': request['request_id'],
                            'action': request['action'], 'guest_report_untrusted': True, 'report': report}
                except BaseException:
                    if reserved:
                        try:
                            self.ledger.finish(request['request_id'], 'UNKNOWN')
                        except Exception:
                            pass
                    raise
                finally:
                    if channel is not None:
                        channel.close()
        except (Exception, KeyboardInterrupt):
            # No error strings, raw serial data, credential headers or tracebacks.
            result = {'v': 1, 'result': 'UNKNOWN' if reserved else 'REJECTED'}
            if request is not None:
                result['request_id'] = request['request_id']
            return result
