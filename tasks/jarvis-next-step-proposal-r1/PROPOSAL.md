# Smallest next step — proposal only

**Proceed next with a bounded local fixture-integration unit; request no privileged
installation approval now.** The current broker precheck is not yet actionable
with truthful bindings and a verified restricted executor path. This task changes
only this proposal/evidence packet and the canonical log: no install, test rerun,
source/security/identity/credential change, PVE/guest access or activation.

## A. Routine offline integration and technical prerequisites

Recommend one future Nexus-local fixture unit using the existing
[22-package hash-required lock](../jarvis-framework-closure-r1/proposed-closure-20261030T231119946730Z.lock),
SHA-256 `c33e6a6d1b55691d2ccb32896fc8bc60ebaf213e0060275aadbfd230cfff0ac8`.
Its six roots have no extras: FastAPI, Pydantic, APScheduler, pytest,
pytest-asyncio and httpx. Metadata compatibility/integrity passed; it is not a
full-app/lifespan lock and does not include pydantic-settings.

Before candidate installation/import, that future unit must establish a pinned
local installer/bootstrap path (ordinary tool discovery found pip/wheel absent),
actual interpreter/native-library compatibility, and an available unprivileged
child boundary that denies network and real data/credential access. Installed
packaging26.0 evaluated the unimported candidates; locked packaging26.3 did not run.
Do not infer a usable installer or sandbox from that successful metadata check.

Use one new task-local environment/source/fixture directory; existing public
artifacts stay read-only. Proposed limits remain2GiB/100000 new files,1GiB child
address space, two children and20 minutes. No global/user-site install, downloads,
source builds, provider/model calls, real app data or VM state. Supply fixture
config/paths before any import. Start with fixture-only real ASGI responses and
bounded scheduler callbacks, not full app.server/lifespan or tool execution.
If installer, sandbox or native requirements cannot be met within those bounds,
stop at the precise technical blocker instead of escalating or importing in the
real configuration namespace.

This is routine offline engineering, not a new blanket human-approval gate. This
documentation task itself authorizes no installation/import/tests. The existing
[integration plan](../jarvis-consolidated-review-r1/INTEGRATION-PLAN.md) supplies
bounds; [closure evidence](../jarvis-framework-closure-r1/README.md) supplies the
narrow candidate lock, not execution approval or full-app compatibility.

## B. Privileged action: wait; no runnable Stage1 request yet

Source inspection of the pinned broker R1 establishes the dependency:

- [runtime.py](../proxmox-automation-phase3-review-r1/src/g6k_serial/runtime.py),
  settings(precheck=True), calls policy.config with only enabled temporarily set
  true. It does not bypass guest, target, release, identity or expiry validation.
- [policy.py](../proxmox-automation-phase3-review-r1/src/g6k_serial/policy.py),
  config, requires a32-hex machine_id/grant_id, nonzero worker UID/GID and caller
  UID, actual broker/caller UID/GID fields, finite unexpired expires_at, source
  digest, operator reference, allowed actions, CA digest and fixed VM164 target.
  These checks are schema/binding checks; a no-transport precheck cannot discover
  or verify the actual guest facts. Plausible dummy values are not those facts.
- runtime.initialize_state also invokes this complete-grant validation. Neither
  init-host nor an enabled=false template resolves missing inputs.
- runtime.probe_paths validates the same complete grant and actual submitting
  identity. It expects all13 installed source files, host.json, a protected
  synthetic canary and **four** Nexus unit files: g6k-serial.service/.socket plus
  g6k-serial-precheck.service/.socket. Absence is not access-denial evidence.
- The precheck service must actually run as g6k-pve-broker; peer/probe identity
  must actually be g6k-submit with no supplementary groups. A human-root
  runuser probe is not proof that the current Codex session has a usable,
  genuinely restricted submission path or lacks its other administrative paths.

The template still leaves guest machine-id/worker UID/GID, host UID/GID bindings,
grant/operator/expiry/release/CA fields null. Known release hashes can be filled
from retained evidence, but **actual guest identity, trusted installed-root
bootstrap, chosen/verified numeric identities and the actual restricted executor
launch/submission path are not established**. A future grant window/expiry and
independently trusted CA binding must also be frozen truthfully. Do not guess
values, run the template, weaken the validator or treat precheck success as guest
identity proof.

[OBSERVATIONS.json](OBSERVATIONS.json) contains bounded public local metadata:
the observation child was UID/GID1000, local name nexus, with kernel groups mapped
locally to sudo/docker/lxd among others. It is not a qualified restricted caller.
The proposed g6k-pve-broker/g6k-submit entries were absent from local passwd/group
files; the fixed install/state/run paths and four unit paths returned ENOENT.
This neither reserves names/IDs nor proves effective NSS absence, ACL policy,
sudo/polkit/container/ptrace isolation or future session behavior. No NSS/network,
escalation or permission probe was performed; no secret value was opened.

A root-owned copy of the13 public sources alone could technically be prepared
without guest bindings, but establishes only protected candidate storage. It
does not make precheck runnable, prove credential denial or provide restricted
executor access. **Recommend waiting rather than creating unused privileged
accounts, directories or units. No privileged authorization text is offered now.**

Once the missing public identity/bootstrap and executor facts are available,
the next security request should be **one Nexus-only, no-transport precheck**,
with actual identities, pinned exact files/permissions and a finite operator-
chosen window. Start only precheck units; normal broker stays disabled, no real
token/activation marker. Stop on binding/source/name/path conflict or failed
identity/denial evidence; retain hashes, ownership metadata, canary and failure
records, with no automatic object/evidence deletion. Operator acceptance remains
fresh for at most600 seconds and cannot exceed the bound grant expiry. Its exact
action language must follow the real facts; it is not an executable grant now.

The existing [APPROVAL-PACKET](../proxmox-automation-phase3-review-r1/APPROVAL-PACKET.md)
and [INSTALLATION](../proxmox-automation-phase3-review-r1/INSTALLATION.md) remain
reference plans, not one broad grant. PVE164-only Audit+Console/token issuance,
VM164 trusted bootstrap/worker changes, live activation and privileged Gate6K
qualification remain separate pending actions. Existing observer stays unchanged;
no PVE-root credential/access, VM162, VM163 or AI-server scope is included.
Nothing was denied or executed; no rollback action is presently needed.

## C. Conservative product defaults — recommended, not implemented

| Decision | Recommended default and consequence |
| --- | --- |
| Authoritative owner | One process owns queue/scheduler state; every API, scheduler, CLI and reporter uses it. Until exclusive ownership is enforced, allow no operational second writer/CLI local fallback and keep execution disabled. Atomic replacement/hashes are not ownership. Restart opens recovery/readback first, without resetting uncertain evidence. No daemon or migration is proposed for immediate execution. |
| Durable idempotency/occurrence/outbox | Require a caller-scoped request key bound to canonical payload and authenticated action/target/authority context. Same key+payload returns its durable receipt subject to current authority; same key+different payload conflicts. Use schedule ID+revision+nominal UTC fire time for occurrence identity. Reserve acceptance and enqueue/outbox state transactionally; retain receipts through reviewed lab archival, with no automatic uncertainty reset. UNKNOWN means reconcile, never blind retry/new key. No such transaction/receipt contract is implemented yet. |
| Remove/stop and admitted work | Commit a barrier against new admissions before acknowledgement. Removing a schedule does not delete accepted tasks. Hold already-admitted but not dispatched work for reconciliation; let an already-issued bounded read-only inspection finish within its deadline and record its result. Return/retain inflight state; never claim cancellation of a possible side effect. Emergency disconnect produces UNKNOWN where necessary, not an automatic replay. Current R4 only blocks new/stale admission: an already-admitted enqueue may still finish after remove/stop; the stronger hold policy is a recommendation. |
| Executor/authority wiring | Executor remains disabled; goal text is data, not shell/tool authority. Before enabling it, explicitly bind authenticated requests to the fixed reviewed catalog, target and expiring grant; initially only identity/kernel/isolation-summary for VM164. Stop on unknown authority/outcome. Any privileged/mutating expansion requires separate authorization. Consequence: queued goals do not run until that wiring and acceptance exist. |

Stop after this proposal. No next code, installation or hardening unit was started.
