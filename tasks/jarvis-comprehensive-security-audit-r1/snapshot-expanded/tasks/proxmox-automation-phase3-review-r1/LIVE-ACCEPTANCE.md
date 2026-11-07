# R1 live read-only acceptance plan — NOT RUN

APPROVAL-PACKET.md Stage1 actual-UID no-transport/canary qualification and fresh
root-retained acceptance must precede credential issuance. Verify the precheck
socket/service are stopped, its marker absent, and normal mode remains separately
authorized. This replaces the original ordering that deferred canary tests.

This plan requires a new, explicit activation-for-acceptance approval after the
limited installation in `INSTALLATION.md`. Phase3 did not run any of it.
Only the three reviewed inspection actions may execute. Audit/replay state and
authorized service/TTY activation are the known setup writes. No shell command,
guest root execution, package, power, NIC, qemu-ga, unrelated VM or qualification
operation is added by an acceptance test.

## Preconditions checked independently by the operator

1. Match node pve, VM164 UUID, exact64GiB disk volume/hardware serial and serial0
   against the independent approval and Phase2 plan. Installed OS/boot and the
   actual machine-id are proven through the trusted guest console, not inferred
   from API running status, a rescue shell or worker assertions.
2. Both code trees match the independently retained source digest. Inspect all
   ancestors, links, modes and interpreter/native-library origins. No extra
   modules/pyc files, user-writable imports or conflicting unit drop-ins.
3. Actual Codex process runs under the approved restricted UID, with exactly its
   private primary group and no elevated/container/management access. Verify its
   complete effective sudo/polkit, group, capability, proc/ptrace and file rights.
   Current Nexus sudo/docker/lxd membership is a blocker until that separation is
   independently established. Do not test escalation using production credentials.
4. From that UID, a synthetic broker-secret canary and audit/config/code/unit
   paths cannot be read for content or modified. Confirm no raw serial devices,
   direct proxy/ticket interface or broker administration is exposed. Neither
   host nor guest service runs as root or with supplementary admin groups.
5. PVE user/token full effective permissions show Audit+Console on164 only;
   privilege separation and finite expiry are correct. Original observer token
   remains unchanged/Audit-only. Use self-permission inspection, never another
   guest's resource endpoint or a broad root token to run the acceptance test.
6. VM164 has no configured NIC, passthrough/shared storage/host socket or active
   setup media; qemu-ga remains disabled. Guest has only loopback, no imported
   credentials, and the distinct Gate6K roles remain protected. No signing key
   has been supplied to the worker. A new credential-policy issue must block;
   do not weaken Gate6K scanning to accommodate it.
7. ttyS0 is exclusively assigned to the reviewed worker. Serial-getty is disabled;
   there is no root autologin/debug shell/kernel or early serial console. The
   worker sets raw115200-baud, CLOCAL/no software or hardware flow control.
   A required bootloader/reboot/rescue change needs its own explicit approval.
8. Verify installed Proxmox termproxy/WebSocket schema and actual token support,
   Linux x86_64 seccomp, systemd restrictions and egress filter support. None of
   these is established by a mock server or syntax validation. Unsupported
   enforcement blocks the test; no broader permission or security fallback.

## Activation for this acceptance window only

In each trusted root context, change only the relevant fully reviewed JSON's
enabled flag from false to true. Leave all bindings/catalog/expiry unchanged.
Do this with an exclusive temporary root-owned file plus fsync/atomic rename;
do not edit an active grant. Then create, exclusively, the matching activation
marker containing the public32-hex grant ID and one LF:

| Context | Config | Marker |
|---|---|---|
| Nexus | `/etc/g6k-serial/host.json` | `/etc/g6k-serial/HOST-ACTIVATE` |
| VM164 | `/etc/g6k-serial/worker.json` | `/etc/g6k-serial/WORKER-ACTIVATE` |

The following bounded root snippet is an **example for VM164**. Run it only in
the authorized activation window after validating the complete bindings. For
Nexus the operator substitutes the exact host filename/marker above; no arbitrary
path or data comes from Codex.

```python
import json, os, re
from pathlib import Path
p = Path('/etc/g6k-serial/worker.json')
record = json.loads(p.read_bytes())
if record.get('enabled') is not False or not re.fullmatch('[0-9a-f]{32}', record.get('grant_id', '')):
    raise SystemExit('STOP: expected disabled, fully reviewed grant')
record['enabled'] = True
tmp = p.with_name('worker.activation-new.json')
fd = os.open(tmp, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
with os.fdopen(fd, 'wb') as f:
    f.write((json.dumps(record, sort_keys=True) + '\n').encode())
    f.flush()
    os.fsync(f.fileno())
os.replace(tmp, p)
marker = p.parent / 'WORKER-ACTIVATE'
fd = os.open(marker, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o644)
with os.fdopen(fd, 'wb') as f:
    f.write((record['grant_id'] + '\n').encode())
    f.flush()
    os.fsync(f.fileno())
fd = os.open(p.parent, os.O_RDONLY | os.O_DIRECTORY)
os.fsync(fd)
os.close(fd)
```

After that explicit authorization, on VM164 only:

```sh
systemctl daemon-reload
systemctl start g6k-serial-worker.service
```

On Nexus only:

```sh
systemctl daemon-reload
systemctl start g6k-serial.socket
```

Do not enable at boot during acceptance. The broker starts only when the root
socket passes fd3 to the non-root service; no network listener is created.
Inspect service UID, capabilities, NoNewPrivs/seccomp, effective sandbox and exact
socket/TTY ownership. Use safe public metadata only, never environment dumps.

## Acceptance matrix

| ID | Test | Required evidence/result |
|---|---|---|
| L01 | Restricted client executes identity, kernel, isolation-summary once each | Exact bindings; bounded schemas; guest_report_untrusted=true; actual UID nonroot; host RESERVED/REPORTED/ACKED and guest reservation/result audit |
| L02 | Independent console comparison | Operator checks public results against trusted observations; still no claim that a compromised guest cannot lie |
| L03 | Deny sudo, shell, qualify, injected strings, arbitrary args/URLs and VM162/163 requests at local socket | REJECTED before any remote send; no unauthorized operation run inside any guest |
| L04 | Wrong UID/group connects to request socket | Filesystem denial or authenticated rejection; no use of real credential content in test |
| L05 | Raw bytes/serial selector/proxy/ticket/credential requests | Rejected locally; no transport data or secrets returned |
| L06 | Repeat an ACKED request ID | No new proxy/action; replay record retained; no new-ID workaround after uncertain request |
| L07 | Two simultaneous distinct read-only requests | At most one dispatched; other rejected/busy with no guest action; no evidence overwritten |
| L08 | Idle and reconnect | Worker remains nonroot/restricted, no prompt or stale-output confusion; inspect after an idle interval and successive fresh channels; stop on banner/framing/flow/backlog incompatibility; test the new fixed-beacon/fresh-hello synchronization, including idle attachment and queued beacons |
| L09 | Current/pending config and version contract | Broker's fresh pre/post config/status/pending checks and self-permission scope work with actual installed API, without widening privileges |
| L10 | Egress and device boundary | Operator verifies installed filter support and actual restricted principal cannot reach broker token, raw devices or other endpoints; do not probe VM162/163/AI |
| L11 | Stop/revoke during a controlled read-only request | Active transport closes, result UNKNOWN if possible send, protected audit persists, all future/new-ID requests blocked |
| L12 | Lost local receipt / broker restart | Pending REPORTED or RESERVED persists and stops later work; no automatic repeat or state reset |
| L13 | Guest role DAC | Worker cannot read authority/signer state, change role identity or use protected role sockets; use only approved harmless fixtures, never production keys |
| L14 | No new credential/log exposure | Public evidence has no token, management ticket, serial auth line, root credentials or arbitrary guest data |

L11/L12 intentionally end the acceptance grant. Perform them last and stop;
they require a separately reviewed fresh grant/state for any next run. Do not
modify the VM's UUID/NIC, real roles or production disks to test drift. Drift,
malicious-response, huge-output and crash-at-every-boundary permutations are
already offline tests; any live fixture variant needs exact extra approval.

Submit routine requests only from the actual restricted process identity:

```sh
/usr/bin/python3 -I -B /opt/g6k-serial/entry.py client identity
/usr/bin/python3 -I -B /opt/g6k-serial/entry.py client kernel
/usr/bin/python3 -I -B /opt/g6k-serial/entry.py client isolation-summary
```

Never automatically repeat UNKNOWN, generate a new ID to repeat it, restart a
halted service, clear a ledger or turn a receipt failure into a successful run.

## Acceptance exit

The operator retains public results, reviewed file/UID/unit/ACL metadata and
ledger audit sequence/hash checkpoints. Close the acceptance window using
`STOP-AND-REVOKE.md`. PASS requires actual evidence for every applicable row;
unattempted/unsupported rows remain NOT RUN/BLOCKED. Routine standing activation
requires the operator's final approval for that exact version/grant and expiry.
Gate6K privileged qualification remains independently authorized and excluded.
