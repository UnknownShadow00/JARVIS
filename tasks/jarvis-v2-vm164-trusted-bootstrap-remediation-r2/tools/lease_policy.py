"""Pure host-fence policy/replay. NO host adapter, transport or execution authority.

Host CLOCK_BOOTTIME nanoseconds are supplied by a backend in a future reviewed
implementation. A replay receipt NEVER admits a real boot, even with good claims.
"""
import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
UUID = 'faeb1db8-0df9-482d-b3e4-f6ccc1602193'
SERIAL = 'g6k164-12821f6b54a2'
DISK = 'downloads:164/vm-164-disk-0.raw'
NS = 1_000_000_000

class Refusal(ValueError):
    pass

def need(ok, reason):
    if not ok:
        raise Refusal(reason)

def integer(n):
    return type(n) is int and n >= 0

def check_target(f):
    need(type(f) is dict, 'target_schema')
    need(f.get('node') == 'pve' and type(f.get('vmid')) is int and f['vmid'] == 164,
         'node_or_vmid')
    need(f.get('uuid') == UUID and f.get('disk') == DISK and f.get('serial') == SERIAL
         and type(f.get('disk_bytes')) is int and f['disk_bytes'] == 64 * 1024**3,
         'target_identity')
    need(f.get('state') == 'stopped' and f.get('boot') == 'order=scsi0', 'stopped_disk_boot')
    need(f.get('no_nic') is True and f.get('no_agent') is True
         and f.get('no_pending') is True and f.get('hotplug') == '0', 'isolation')
    need(type(f.get('digest')) is str and re.fullmatch('[0-9a-f]{40}', f['digest']),
         'digest_required')

@dataclass(frozen=True)
class Lease:
    host_boot_id: str
    session: str
    armed_ns: int
    revoke_ns: int
    hard_stop_ns: int
    identity_digest: str

    @classmethod
    def arm(cls, target, proof, now_ns):
        check_target(target)
        need(integer(now_ns), 'clock_type')
        need(type(proof) is dict and proof.get('scope') == 'synthetic_policy_only',
             'replay_only_no_runtime_adapter')
        need(proof.get('host_owned') is True and proof.get('independent_of_guest') is True
             and proof.get('independent_of_cleanup') is True, 'independent_owner_required')
        need(proof.get('hard_stop_authorized') is True and proof.get('backend_qualified') is True
             and proof.get('both_workers_active') is True, 'qualified_enforcement_required')
        need(proof.get('clock') == 'CLOCK_BOOTTIME' and proof.get('no_extension') is True,
             'fixed_suspend_inclusive_deadline')
        need(proof.get('target_digest') == target['digest'], 'proof_binding')
        need(type(proof.get('host_boot_id')) is str
             and re.fullmatch('[0-9a-f-]{36}', proof['host_boot_id']), 'host_boot_binding')
        need(type(proof.get('session')) is str
             and re.fullmatch('[A-Za-z0-9_-]{1,64}', proof['session']), 'session')
        need(all(integer(proof.get(k)) for k in ('armed_ns','revoke_ns','hard_stop_ns')),
             'deadline_types')
        a, r, h = (proof[k] for k in ('armed_ns','revoke_ns','hard_stop_ns'))
        need(a <= now_ns <= a + 15*NS and r == a + 540*NS and h == a + 600*NS,
             'fixed_deadline_or_stale_arm')
        return cls(proof['host_boot_id'], proof['session'], a, r, h, target['digest'])

    def before_start(self, now_ns, host_boot_id, digest, worker_active, consumed=False):
        need(integer(now_ns) and self.armed_ns <= now_ns <= self.armed_ns + 15*NS,
             'fresh_preboot_deadline')
        need(host_boot_id == self.host_boot_id and digest == self.identity_digest,
             'host_or_config_changed')
        need(worker_active is True and consumed is False, 'worker_lost_or_duplicate_start')
        return 'POLICY_PRECONDITIONS_ONLY_NOT_AUTHORIZATION'

    def tick(self, now_ns, host_boot_id, vm_state):
        need(integer(now_ns) and vm_state in ('running','stopped','unknown'), 'clock_or_state')
        if host_boot_id != self.host_boot_id or now_ns < self.armed_ns:
            return 'UNSAFE_CLOCK_OR_HOST_REBOOT_NO_ADMISSION'
        if vm_state == 'stopped':
            return 'KEEP_FENCE_ARMED_UNTIL_EXTERNAL_FINAL_PROOF'
        if now_ns >= self.hard_stop_ns:
            return 'HARD_STOP_DUE_UNTIL_INDEPENDENT_STOP_PROOF'
        if now_ns >= self.revoke_ns:
            return 'REVOKE_AND_GRACEFUL_SHUTDOWN_DUE'
        return 'KEEP_FENCE_ARMED'

def receipt(lease):
    return {'status':'PASS_SYNTHETIC_POLICY_ONLY','root_boot_go':False,
            'live_enforcement_verified':False,'authorization_granted':False,
            'runtime_backend_implemented':False,'actions_executed':False,
            'lease_model':lease.__dict__}

if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--fixture', type=Path, required=True)
    a = p.parse_args()
    try:
        if a.fixture.stat().st_size > 16384:
            raise Refusal('fixture_size')
        d=json.loads(a.fixture.read_bytes());lease=Lease.arm(d['target'],d['proof'],d['now_ns'])
        print(json.dumps(receipt(lease),indent=2))
    except (ValueError,KeyError,TypeError,OSError) as exc:
        print(json.dumps({'status':'NO_GO','reason':str(exc) if isinstance(exc,Refusal)
                          else type(exc).__name__,'root_boot_go':False,'actions_executed':False}))
        raise SystemExit(1)
