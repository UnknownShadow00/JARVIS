# Negative tests, evidence and activation gates

## Executed within this planning task

`tools/test_policy_model.py` uses synthetic grants/guest observations and makes
no connections or subprocess calls. Importing `observe.py` does not connect.
Run from the JARVIS root:

```sh
python3 -B -m unittest discover -s tasks/proxmox-automation-phase2/tools -p 'test_*.py' -v
```

| Boundary | Covered inputs | Status |
|---|---|---|
| Target/type | VM162, VM163, other IDs, traversal, string/float/bool/null VMID | PASS offline |
| Arbitrary execution | Shell, sudo, root, qualify_all.py, guest-exec, reboot, password, file operations, injection strings | PASS offline |
| Extra authority/parameters | argv, command, env, cwd, stdin, URL, node, serial, UID, signature/approval/token/ticket fields | PASS offline |
| Wire parsing | Duplicate/missing/extra keys, oversized/empty/non-ASCII/control frames, JSON constants, trailing or multiple objects | PASS offline |
| Grant binding | Absent/expired grant, null machine/code bindings, overbroad catalog, missing operator reference | PASS offline |
| Peer/replay | Wrong/root/bool caller UID, reused request ID, exact expiry boundary | PASS offline |
| PVE state | Wrong UUID/disk/serial/size, paused/stopped state, lock/pending changes, extra disks/media, NIC/passthrough/share | PASS offline |
| Guest state | Root/bool UID, machine/release/boot mismatch, added NIC, missing role-separation assertion, unsolicited prompt fields | PASS offline |
| Non-execution | Every valid initial catalog action returns executed=false and transport_enabled=false | PASS offline |
| Error privacy | Attacker-controlled sentinel never appears in refusal messages | PASS offline |
| Permission decoding | Zero propagation flag still counts as an effective grant | PASS offline |
| Observer scope | Fixed GET endpoint set has no other VM, console or agent endpoint | PASS offline |

13 test methods group these adversarial inputs. See `evidence/unit-tests.txt` and
`evidence/unit-tests.json` for the retained run. Passing the reference model does
not establish any installed security boundary, guest isolation or durable replay.
Replay rejection here checks supplied synthetic state; atomic reservation,
fsync/crash behavior and concurrent writers are not implemented by the model.

## Executed live, read-only management observations

`tools/observe.py` reuses `/home/nexus/.local/bin/g6k-pve164-readonly` in memory.
The installed client makes its original two VM164 GETs. The collector additionally
GETs version, its own effective permissions, VM164 config and VM164 current status.
Only selected public metadata is emitted. No raw HTTP errors, headers, token
record, returned session ticket, credential contents or environments are emitted.

The returned self-permission map has only VM.Audit at `/vms/164`; no other active
paths were returned. This is permission introspection, **not** a successful live
attempt to touch VM162/VM163, and **not** a full administrator ACL inheritance
audit. No other guest's resource endpoint was requested. This task did not
contact the AI server or establish a new SSH connection.

No POST/PUT/DELETE, console session, terminal bytes, QGA ping/info/exec call,
package operation, power operation, guest mount or guest command was attempted.
Even a console proxy creation creates a task/process, so testing that endpoint is
deferred. Run-local counts are recorded in each observation; they are not a
claim about all processes on Nexus or Proxmox.

## Required after setup authorization — NOT RUN

| Test | Required result and safe method |
|---|---|
| Actual UID boundary | Codex cannot read/stat-for-content broker secret/state, ptrace broker, replace code/imports/units, or invoke management via sudo. Use a synthetic sentinel credential first. Stop before giving real console rights if it is reachable. |
| PVE ACL scope | Operator checks complete user/token effective maps, not just `/vms/164`. Only VM.Audit and VM.Console on VM164. Confirm no inherited, group or pool grant, token privilege separation and finite expiry. |
| Original observer unchanged | Original observer self-permissions remain VM.Audit on164 only; fresh TLS/identity/no-NIC check passes. |
| Other guests / AI | Broker request validator rejects VM162/163, other nodes, URLs and AI destinations before any network send. Verify egress restriction and self-permission absence; do not use other guests as test targets. |
| Raw console bypass | Under actual Codex UID, raw bytes, termproxy/VNC/WebSocket/ticket requests and serial selectors are rejected; token and underlying transport remain inaccessible. API permissions alone cannot enforce this. |
| Guest role DAC | Actual worker UID cannot read operator signing keys/authority data, use role IPC, write trusted code, sudo or change UID. Use dedicated safe qualification fixtures, never copy production keys. |
| Serial/password state | Locked passwords stay locked; no autologin/getty/shell, GRUB/kernel input or SysRq/break escapes. Noise, login prompt or installer output must fail the handshake without transmitting a command. |
| Framing and hostile results | Split/coalesced frames, reconnect/stale bytes, forged boot/session IDs, duplicate keys, ANSI/OSC, oversize output and malicious instructions are bounded and rejected/escaped. Never execute them. |
| Limits | Controlled test worker hits timeout/output/process/memory caps; kill affects only the positively identified disposable child group. No arbitrary PID accepted. |
| Concurrent/replayed requests | Same request ID from two clients executes at most once. Reservation is durable before possible send. No replay after broker/worker restart or lost response. |
| Uncertain delivery | Disconnect/crash at reserve/send/exec/result/fsync boundaries gives explicit UNKNOWN where execution might have happened. No automatic resend or new-ID repeat. |
| Grant and drift | Missing/null/expired/revoked grant, changed machine-id/boot, code digest drift, pending NIC, media or role change refuses before dispatch. Post-dispatch drift invalidates the result. |
| Revocation | Closing broker channel plus token/ACL revocation prevents new operations and terminates active bridge use. Do not rely on token deletion alone for existing sessions. |
| Credential logging | Fake-secret canaries absent from stdout/stderr, journal, process argv/env, exceptions, API tracing and exported evidence. Verify before real credential issuance. |
| Gate 6K interaction | Existing preflight/credential/authority/isolation requirements still pass without policy exceptions; active bridge disposition during later qualification is explicitly approved. No qualification run is included now. |

Any unavailable tool, missing evidence, unexplained credential file, root worker,
unexpected privilege or ambiguous boot/installation state blocks activation.
Do not install packages, repair state or weaken checks as part of a failed test.

## Workspace and preservation verification

The project-level `AGENTS.md` now pins task logs to the absolute JARVIS root.
The original `/home/nexus/tasks/loop-log.md` remains untouched; a byte-for-byte
copy is retained at `evidence/preserved-home-nexus-loop-log.md`. It contains the
earlier VM164 observer success entry. The project log retains its existing prefix
and receives this task's completion entry. No historical entry is rewritten.

`evidence/entry-preservation.json` records baseline log/client hashes and only
metadata of the credential file. `evidence/final-verification.json` records the
matching preservation checks, public VM configuration comparison and test result.
The credential file is never hashed/copied by preservation checks. Its contents
are consumed only internally by the already authenticated client for API use.
