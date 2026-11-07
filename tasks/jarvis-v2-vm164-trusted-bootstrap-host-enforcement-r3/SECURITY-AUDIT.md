# Security review — source/fixtures only

Verdict: **PASS_OFFLINE_HOST_ENFORCEMENT_ENGINEERING_ONLY** after final checks.
No real enforcement, host qualification, root permission, installation readiness
or Gate6K is established. Policy A cannot meet strict access-expiration trust;
Policy B is modeled, disabled and unauthorized. Root bootstrap remains NO-GO.

## Independent work and review chain

A separate read-only prerequisite reviewer inspected retained primary manuals and
repository evidence without network, systemctl/qm/timer or VM execution. A separate
security reviewer wrote adversarial tests, reviewed changes and reran them under
subprocess/signaling tripwires. Evidence is not merely the author's success report:

- evidence/OFFLINE-PREREQUISITE-REVIEW.md: retained source/manual hashes, exact
  version mismatch (local docs259.5 versus operator host257.13), clock and PVE gaps.
- evidence/INDEPENDENT-SECURITY-REVIEW-V2.md: source fixes and resource readback.
- evidence/INDEPENDENT-CLOCK-REVIEW-V3.md: realistic historical-suspend arithmetic,
  unknown domain/skew refusal and a transparently corrected fixture concern.
- evidence/INDEPENDENT-SECURITY-REVIEW-V4.md: protected kind/hash/package binding,
  shared budgets, standalone unprivileged callback and stale-source fencing.
- evidence/INDEPENDENT-AUTHORIZATION-LIFETIME-REVIEW-V5.md: finite callback lifetime,
  session/grant/source binding, pinned generation and worker-idle barrier.
- tests/test_independent_review.py and independent-review-final-v5.log:18 methods,
  zero failures/errors/skips, all host interfaces mocked. Their final methods are
  also in the294-method release regression.

Earlier notes describe review-time source hashes and assumptions. They are
retained history, not the final source manifest. The first same-clock assumption
was corrected, not relabeled as real-host evidence. No live command documentation
for matching Proxmox packages was found; no online retrieval was attempted.

## Code findings eliminated in the candidate

| Finding | Resolution and invariant |
|---|---|
| Initial root exposure before guest timer | No root purpose/stage accepted. Future host jobs arm/read back while stopped, before the separate start; guest timer is never the sole host limit |
| Partial setup unit leak | Attempt cancellation of every attempted verified-owned phase; preserve unknown orphan/quarantine and deny start |
| Snapshot failure burned deadline claim | Snapshot first; per-phase lock and bounded attempts; terminal marker only after terminal outcome, no deadline renewal |
| Unlogged action after evidence failure | Durable ACTION_INTENT is a strict precondition; no command if it fails |
| Stale source/generation/grant | Central exact-plan checks, timer nonce, pinned session directory and context; old callback cannot follow replacement active pointer |
| Retirement race/replayed approval | CLOSED absorbing, worker-idle barriers, actual stopped proof, archived pointer/fsyncs and persistent used-approval digest |
| Root record hashes unbound | Canonical actual prerequisite/review hashes, source/scope/kind binding and root-private custody; synthetic kinds rejected |
| Expiry callback demanded another full lease | Full coverage only for new prepare; callback currently-valid scope plus same immutable grant; expired remains denied |
| Missing bounded execution readback | Strict Type/argv/root/timeouts/kill/restart plus umask/memory/tasks/stdio/SIGKILL properties |
| Clock equality ignored suspend | Declared Stage2-qualified readback domain, paired bounded offset capture and interval-consistent conversion |
| Default/force actuation risk | Default dry-run; installed-path/root/finite A-only gate; no native force implementation or qm-stop allowlist; no generic shell |

The durable-intent rule deliberately chooses no unaudited actuation on a full/
corrupt store. It can leave an expiration blocker. This is not hidden behind a
claim of guaranteed termination. Post-action evidence loss cannot undo a command;
results stay incomplete. Wrong/unknown identity similarly causes no guest action.

## Explicit trust and residual-risk register

| Residual | Current disposition |
|---|---|
| Actual systemd257 parsing/clock domain/wake/scheduling | Stage2 UNKNOWN; fixtures and local259 manuals cannot prove it |
| Future delayed service execution/dependency failure | Type=exec verifies exec only when run; canary cannot prove later callback/VM termination |
| Host reboot/reexec/manager failure/cancellation | No demonstrated continuous expiry guarantee; boot mismatch/stale state refuse, transient jobs are not a hardware fence |
| Shared failure dependencies | Both jobs use same host PID1/Python/storage/kernel/PVE tools; not redundant host fault isolation |
| Unsupported PVE flags, locks/protection/task completion | Matching help/package/source and real Stage3 behavior pending; never bypass to obtain a PASS |
| Non-atomic snapshots/external controller/HA races | Exact current data reduces mistakes but cannot freeze another root controller; exclusive custody/task behavior must be qualified |
| Guest ignores ACPI | A reports hard blocker without force; strict root-access requirement is unsatisfied |
| B/crash preservation tradeoff | Distinct authorization and reviewed promoted code required; forced stop may damage original Ubuntu state and still fail under host faults |
| Host-root malicious/tampered evidence | Root is trusted; local hashes/root-private operator records are not WORM, signatures or independent origin proof |
| Current hardware versus physical media/storage | Latest facts are operator-reported; actual mapping/content/resource readback remains Stage3 work; no raw-disk hashing/mounting or guest repair occurred |
| Source/package update during active lease | Prohibited; pins/context reject changes rather than silently renew. Such rejection itself can prevent expiry and is a blocker, not a guarantee |
| Late or expired callback | LATE/expired scope refuses positive result; UTC/BOOTTIME custody and actual latencies are not verified here |

The subprocess allowlist has literal node/VM164 selectors and only reviewed source
worker/canary reconstructions. No other-VM endpoint, arbitrary command, qm unlock,
skiplock, protection edit, network token or fallback force path is present. Native
calls are still unqualified proposed interfaces until the mandatory reviewed
records exist. All such calls were mocked in tests; no process query or package
metadata command ran against the real host in this sprint.

## Prerequisites and safe alternative

Seven proposed binaries require actual ownership/chain/hash checks: provided
systemd-run/systemctl/qm plus python3/pvesh/pvesm/dpkg-query. Exact package metadata
is rechecked before future actions; script hash alone would not detect every
Proxmox library/package upgrade. Protected kernel/hostname/source/boot/grant/
review records are additional gates, not substitutes for real qualification.
Unknown CPU/RAM/balloon/custody/account/clock facts are not synthesized.

Stage2 callback intentionally cannot be root or access VM APIs; it has no process,
network or private-approval interface. Existing unprivileged UID and safe root-
owned public installation need separate approval. Current source/archive lives
only in this repository; no runtime location/unit was created.

Avoiding an interactive root console through a newly reviewed immutable read-only
one-shot diagnostic is a plausible safer design. It avoids having to crash the
guest to revoke a usable shell, while still needing boot-chain and task controls.
It is not an already-built/qualified guest alternative here.

All247 predecessor regular files/5 links and prior seals are rechecked unchanged.
No source in a sealed predecessor or application was patched. The canonical loop
log was append-only, including independent reviewer completion entries. No secret
or credential changes, provider calls, Gate6K, production or V3 action occurred.
