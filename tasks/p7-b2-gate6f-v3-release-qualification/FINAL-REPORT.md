# Gate 6F final report

Isolated qualification only. No production modification, credentials, privileged provisioning, real model requests, V2 retirement, V3 deployment, pilot opening or push.

**JARVIS P7 GATE 6F — PARTIAL, EXTERNAL OR PRIVILEGED QUALIFICATION REQUIRED**

## Production continuity: discrepancy at entry, preserved, not repaired

Entry readback 2026-10-15T18:37:19Z. Matched: HEAD `bd53dbc7…`, config `00d7b460…`, installed-source hashes, `Restart=no`, `NRestarts=0`, autostart disabled, D06 `current=None,last=None`, credential metadata, both backups, zero attempts/submissions/receipts, no D04 namespace.

**Differed:** `jarvis.service` is `inactive/dead`, MainPID 0, no InvocationID (expected PID 594042, invocation `103e420f…`). D09 epoch `606a991a…` is `CLOSED_COMPLETE` with one `OPERATOR_STOP` pilot event; audit shows `server_stop`. Cause, read-only: at **2026-10-15T03:42:17Z** Core logged `Power key pressed short` (ACPI power button from the hypervisor), powered off, and booted at 03:42:45Z. The service stopped cleanly through its shutdown hook and, by design, did not restart. The actor was external to this task; no Claude or Codex transcript issued it.

Per the brief, production-dependent work stopped there; nothing was restarted or repaired. Exit readback 18:58:24Z: **zero differences from entry**. So SHADOW is **not** active.

## Isolated candidate

`/home/jarvis/.hermes-poc/gate6f-candidates/release-r1/repo`, manifest digest **`ff2444df135fcf8027d36cca9fa02fd7000884f88f78f76d74ddc68707dce733`** (29 members; full inventory `d31191bc…`, 596 files; patch vs 6E r2 `03a25969…`, 11 files). Not a Git commit. 6E r2 (`c28942a9…`, 593 files, 0 mismatches at exit), 6E r1, 6D and 6C archives preserved; 6E seal `c09c0da0…` and all 100 prior seals verify at entry and exit.

## Fixes (CONTINUOUS-IMPROVEMENT-REGISTER)

F01 High: V2 `OPERATOR_STOP` is written on any shutdown, so it is not operator intent; the predecessor proof now carries `UNATTRIBUTED_V2_SHUTDOWN_HOOK` and retirement comes only from the signed successor payload. Production now has exactly that shape. F02 High: attested resource topology, fail closed on unverified, explicit approval for shared host/service. F03: next permit re-proves the coordinated chain. F04: durable replay check before any effect. F05: known D06 conflicts refused before a possible-send. F06: source-faithful pinned memory snapshot. F07: control-socket whole-request deadline. F08: fixed archive refusal codes.

## Findings

- **L1 compatibility:** rules, classifier request, complexity and prompt construction are source-faithful (byte-equal to `build_prompt` with the pinned snapshot). Deltas are listed and classified, and "exact equivalence" is not claimed. **Normal responder `num_ctx` 32768 is not source-faithful** (source Modelfile 8192; original sends none), so proposal G6F-LP-2 is 8192. The 6E empty memory snapshot changes the experiment.
- **Bounds:** all four inputs and all 11 conditional operations fit 16 KiB with real prompts and memory (max 4,696 B). Oversize is refused before a possible-send, never truncated.
- **Router/responder/Granite:** classifier options equal the original except the added keep-alive. Trivial context depends on an unverified server default. Granite profile untouched (`observation.py` byte-identical).
- **Operations and time:** 3 + 4 + 4 = 11 operations for 4 attempts. Early failures decrease counts truthfully across 7 tested variants. Provider deadline envelope 1,500 s, with no hidden overall deadline; drain does not guarantee remote completion.
- **OS identity:** **NOT QUALIFIED.** No disposable distinct uid exists without new privilege (AppArmor userns restriction, no `newuidmap`, sudo needs a password). A disposable-VM plan is provided.
- **Operator authority:** implemented and isolated-tested (bindings, one-use, replay, restart hold). Human presence and OS separation are not proven.
- **Lineage/antirollback:** local transactional and partial rollback detection proven. **A full coordinated same-UID rollback is not detected** (shown by test). There is no privilege protection or host-loss tolerance.
- **D06/external actors:** in-graph exclusion proven. Topology attestation is now required. External cron, supervisors, the unloader and direct clients are **not covered**.
- **AI host:** fingerprint, placement and model digests **not established**; trust PENDING.
- **Filesystem:** all listed failure modes pass at tested boundaries, including real-kernel short write and EFBIG. Power loss is NOT PROVEN.

## Tests

Focused **303 passed / 0 failed**; full **7,469 passed / 11 deselected / 0 failed / 2 warnings**. Zero real provider transmissions. Golden 12/20 historical, not rerun.

## Evidence

`/home/jarvis/.hermes-poc/evidence/p7-b2-gate6f-v3-release-qualification/`. The seal is the SHA-256 of its `SHA256SUMS`, reported separately to avoid self-reference.

## Outstanding operator decisions

See EXACT-OPERATOR-APPROVALS. In order: 0) V2 state after the unattributed power-off, and finding who issued it; 1) experiment contract X1–X11; 2) independent AI-host/legacy identity attestation; 3) OS/privilege and protected-root design plus disposable qualification; 4) retirement and successor; 5) V3 install and new Gate 5; 6) pilot permits.

**Recommended next separately approvable action:** the operator investigates the 2026-10-15 power event in the Proxmox task log and decides V2's state (decision 0), then runs the human-only AI-host and legacy identity attestation (decision 2). Both are read-only for the systems involved and unblock X4/X5/X10.

GATE 5: COMPLETE FOR V2 ONLY

PRODUCTION SHADOW: **NOT ACTIVE — V2 stopped by the 2026-10-15T03:42:17Z host power-off; preserved, not restarted**

PRODUCTION ADMISSIONS: CLOSED

REAL PILOT ATTEMPTS: 0

V3 CANDIDATE: ISOLATED ONLY

V3 DEPLOYMENT AUTHORIZED: NO

GATE 6 PILOT AUTHORIZED: NO

AI-HOST TRUST: PENDING

MEASUREMENT STARTED: NO

FORMAL P7 EXIT: NOT COMPLETE
