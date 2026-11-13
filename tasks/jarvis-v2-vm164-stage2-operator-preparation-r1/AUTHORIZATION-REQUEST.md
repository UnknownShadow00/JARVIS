# Future Stage 2 authorization request — NOT GRANTED

No response is requested to finish this offline task. Stage 2 remains NOT
AUTHORIZED. This is a reviewable proposal for a later separate operator decision.

The proposed authority covers one supervised local pve session lasting no more
than45 minutes, with explicit UTC start/expiration and BOOTTIME anchor; exact
current host/source/binary/policy/evidence bindings; one exclusive public callback
copy at the approved path; and only this packet's twelve named non-VM cases under
one fresh nonce. Setup uses existing administrator privileges; callback services
use existing UID/GID65534, Type=exec, fixed limits and the reviewed sandbox.

Before approval, the following must be concrete and independently reviewed:

```text
Operator / supervisor identity: MANDATORY INPUT
Independent reviewer and signed review reference: MANDATORY INPUT
Approval reference and exact packet MANIFEST.json SHA256: MANDATORY INPUT
pve boot UUID / fresh kernel / package and binary evidence hashes: MANDATORY INPUT
Complete nobody authority/credential-denial review hashes: MANDATORY INPUT
Console evidence storage, recording capability and custody: MANDATORY INPUT
Root-controlled staged callback path and verified source SHA256: MANDATORY INPUT
Session nonce and all twelve timer/service names: MANDATORY INPUT
UTC START (YYYY-MM-DDTHH:MM:SSZ): MANDATORY INPUT
UTC EXPIRATION (YYYY-MM-DDTHH:MM:SSZ; <= START + 45 minutes): MANDATORY INPUT
Initial BOOTTIME/paired-clock evidence and expiry translation: MANDATORY INPUT
Exact rendered argv review procedure and ownership ledger: MANDATORY INPUT
Acknowledged unresolved clock/version/negative-case limitations: MANDATORY INPUT
Cleanup cutoff and exact owned-unit stop authority within this same window: MANDATORY INPUT
```

An eventual sufficient decision must expressly approve only those concrete
fields, the exact installation command body, the enumerated negative cases,
root-system-manager transient setup/WakeSystem=yes, nonroot callbacks, evidence
capture and scoped cleanup. Approval of read-only checks alone is not permission
to install/activate; stage installation needs its separate explicit authorization
within that decision. Approval does not replace failed admission evidence.

No transfer/network/credential operation, new account/ACL/token, privilege probe,
root callback, root shell, VM request/status/config/boot/stop/guest action,
console guest input, forced VM stop, host reboot/suspend/reexec/manager restart,
package installation, unrelated unit action, full R3 runtime/private grant
installation, Gate6K, JARVIS or production change is included. VM162, VM163, the
AI server and all other VMs remain outside scope. VM164 stays stopped/no NIC.

Do not approve unfilled synthetic templates. A successful awake-host test does
not establish strict expiration, physical wake, reboot/reexec survival or Stage3
readiness. If the mandatory UID denial proof cannot be established, the decision
is blocked before placement; there is no fallback UID/root route in this packet.
