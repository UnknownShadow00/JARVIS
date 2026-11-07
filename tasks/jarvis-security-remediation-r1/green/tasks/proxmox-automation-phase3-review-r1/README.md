# Serial broker Phase3 — independent review revision R1

Isolated replacement candidate for the uninstalled Phase3 packet. **Not installed,
activated or live-qualified.** Original Phase2/3 files and receipts remain
byte-identical. No identity, permission, credential, service or guest changes.
No Proxmox/guest/provider/AI calls. Other apps/worktrees were not accessed or reused.

Checkout: `7f4ae164261b792262eb9b818421c444c2d4ccff`, branch
`docs/p7-d06-d07-passive-review`. Preexisting edited loop-log and untracked Phase2/3
packets were preserved. No staging/reset/commit was performed. New work is this
revision, the separately documented task-queue reliability unit and appended logs.

## Verified identity

The actual original source-manifest hash independently matches
`58698f4cf814ef267ea010d44280c6bfdea2ce8f46486e51a18f3916d7ae24d5`.
All12 source files and42 packet members verified. The original packet contains no
archive, and the bounded repository inventory found none. This is actual content
verification, not a copied receipt; see `evidence/source-entry.json`.

The revised13-file source digest and new deterministic public archive digest are
in `RELEASE.json`. Packet `SHA256SUMS` covers evidence/docs/tests/units. Independent
operator retention is required; hashes alone are neither approval nor a signature.

## Security scope

Guest catalog remains exactly identity, kernel and isolation-summary: built-in
public-metadata inspection, no subprocess/shell/provider/paths/arguments, no
privileged or mutating command. Only private replay/audit state is written.

The protected Nexus broker authenticates Unix kernel UID/GID/groups and pins a
root-controlled expiring grant, source, TLS/CA/PVE endpoint, VM164 UUID/disk/no-NIC
state and serial0. Its separate token needs only Audit+Console on164. The existing
Codex-readable observer credential is not opened, changed or broadened.

Independent reviewer: separate agent configured **gpt-6-astra, high**; no Claude
review is claimed. See `INDEPENDENT-REVIEW.md`. No authority escalation or secret
disclosure was demonstrated under the stated trusted-root/broker model. Four
medium original defects needed fixes before activation:

| Finding | Revision |
|---|---|
| Worker lifetime64KiB budget exhausted on ordinary use | Fresh per-exchange budget; persistent PTY worker exercised140 times and beyond64KiB |
| Receipt loses operation-lock race | Conversation holds the lock through receipt commit; owner-checked acknowledgement and real contender test |
| Serial attachment starts mid-readiness/behind old output | Fixed idle beacon; at most one exact suffix then a complete beacon, fresh challenge synchronization before reservation; strict report parsing afterward |
| Credentials precede actual-principal qualification | Separate disabled-host precheck, synthetic-canary/path denial probe and root0600 fresh acceptance gate before issuance |

Targeted recheck additionally corrected banner/LF-boundary handling, queues beyond
64 beacons, and grant/evidence/config/source/CA drift while the operator waits at
secret prompts. The issuer revalidates immediately before dialing. No retry or
overwrite of partial issuance is permitted.

## Protocol and failure semantics

Public request schema/target is unchanged. Serial protocol adds hello → fresh
challenge-bound synchronized readiness → inspect → bound report. Idle output is
only a fixed ASCII beacon; partial idle writes retain at most one unfinished
beacon under backpressure. At connection start one exact beacon suffix, including
LF-only, may be followed by a whole beacon; arbitrary prompts/JSON are not skipped.
Exact old beacons may be drained only within existing byte/deadline bounds.
No inspection is reserved until fresh synchronization and identity validation.

The worker resets framing/budget per exchange. An empty abandoned handshake can
return to idle before action; partial/malformed input halts. After a possible
action, ambiguity remains UNKNOWN and blocks new IDs. Host/guest durable
reservations persist across restart; the host lock spans receipt commit.

A receipt means the local client parsed a bounded report, not that a human saw
it or stdout was durably saved. Worker results remain explicitly untrusted: a
compromised guest can fabricate plausible metadata. Returned text is never code.
Audit hashes do not provide external anti-rollback, and request-table state is not
independently reconciled with event history. Preserve independent checkpoints.

## Pre-credential and live gates

The precheck has a separate Unix socket/unit/marker, requires disabled config and
no credential file, and cannot load credentials, open the ledger or construct a
PVE transport. It only returns authenticated peer identity/transport_enabled=false.
Normal mode requires enabled config and its distinct activation marker. Issuance
requires root-retained evidence, both markers absent, stopped precheck, and actual
canary/code/config/unit/escalation checks performed before real credentials.

Current Nexus sudo/docker/lxd membership is not an approved submitting identity.
No removal or isolation is claimed. Actual new identities, guest root context,
machine-id, DAC, QEMU buffering, native runtime and service-filter behavior remain
live prerequisites. Offline results are not protected cross-UID/guest qualification.
Gate6K privileged qualification and all production/provider actions stay excluded.

## Reproduce and continue

```sh
cd '/opt/apps/IT TRAINING PROJECT CODE/projects/JARVIS'
python3 -I -B tasks/proxmox-automation-phase3-review-r1/tests/run_offline.py
python3 -I -B tasks/jarvis-v2-taskqueue-reliability-r1/run_checks.py --save-evidence
```

The guarded broker harness prohibits IP/DNS and real credential opens; local
TLS/Unix/PTY/SQLite/process-exit/seccomp fixtures are synthetic and same-UID.
Current counts are in `evidence/offline-tests.json`; original53/175 and historical
7741/11deselected remain historical, not new-run claims.

The separate task-queue unit implements atomic same-directory publication,
pre-publication rollback, explicit persistence errors and blocked writes after
uncertain replacement durability. Its13 methods include10 isolated existing
regressions and18 write/flush/fsync/replace failure cases; no real app singleton,
provider or runtime data is loaded. Full app integration is not claimed.

Use `APPROVAL-PACKET.md` as the single pending staged request; it has not been
executed. Installation/live acceptance remain separate from offline engineering.
See `PROGRESS.md` for next safe work that can proceed while permission is pending.
