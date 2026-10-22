"""Supplemental final-bundle probes, executed only by the isolated harness."""
import socket,struct,time
import pytest
from candidate_v3.contracts import canonical,Refused,strict_json
from tests.execution.v3_protected_runtime_test import protected,packet

def test_wire_malformed_utf8(protected):
    assert packet(protected,b'{"version":1,"operation":"READ","arguments":{"bad":"\xff"}}')['accepted'] is False

def test_wire_symlink_substitution(protected):
    path=protected.socket_dir/'service';path.unlink();path.symlink_to(protected.socket_dir/'operator')
    try:
        with pytest.raises(Refused):protected.high.read()
    finally:path.unlink()

def test_operator_disconnect_after_send_never_refunds_nonce(protected):
    f=protected;raw,sig=f.approval('OPEN_HOLD');body=strict_json(raw)
    wire=canonical(dict(version=1,operation='SIGNED',arguments=dict(body=body,signature=sig.hex())))
    with socket.socket(socket.AF_UNIX,socket.SOCK_STREAM) as connection:
        connection.connect(str(f.socket_dir/'operator'));connection.sendall(struct.pack('!I',len(wire))+wire)
    deadline=time.monotonic()+3
    while body['nonce'] not in f.journal.read()['commands'] and time.monotonic()<deadline:time.sleep(0.01)
    assert body['nonce'] in f.journal.read()['commands']
    with pytest.raises(Refused):f.operator.submit(raw,sig)
    assert f.runtime.state=='CLOSED_INITIAL' and not f.calls
