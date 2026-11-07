# Supervised uncertainties and fail-closed recovery

Nothing in this document authorizes or performs a host/guest operation. The
operator's current supervised scope and exact target must be established on
return. No unattended fallback, pending-change repair or timer extension exists.

## CD ejection with hotplug 0

The packet specifies an existing ide2 drive, exact nonboot CD and `hotplug: 0`.
Changing a drive's inserted medium is conceptually different from adding/removing
its controller or device. That distinction alone does **not** establish what this
installed PVE/QEMU version applies live. The repo contains no version-bound
successful execution, drive-lock behavior or supported API schema proving it.
External documentation and infrastructure were not accessed for this audit.

Before any start, resolve the ejection design disposition with the operator. If
the unchanged design is retained for a specifically supervised attempt, success
requires **all** these observations in the same debug boot:

| Checkpoint | Required observation | Stop condition |
|---|---|---|
| Before media transition | Current exact running/attached config/status/pending, no pending, disk-only boot, correct digest; RAM_STAGED and successful guest unmount | Missing, old, inconsistent or wrong-scope evidence |
| Host change result | Media-only action matches the approved operator procedure and succeeds | Unsupported command, task failure, error or different effective transition |
| Fresh effective host readback | Explicit current config says existing `ide2=none,media=cdrom`; running; no pending row/change of any kind; protected config unchanged | Attached current value, pending-only empty value, extra change or ambiguous view |
| Guest physical-medium observation | Wrapper sees no nonzero `sr*` size; unchanged probe reports optical absence | Mounted/busy/inaccessible device, nonzero size or uncertain absence |
| Evidence | Same-boot identity, fresh readback hashes and captured result retained | Hash/identity/boot mismatch or lost evidence |

This is a success criterion, **not evidence that it is feasible**. A host config
change receipt is not guest physical ejection. An empty pending list alone is not
guest physical ejection. An unmounted filesystem is not either observation.

If ejection fails, do not execute the probe from mounted media, skip its optical
check, or fabricate `optical_media_present=false`. Preserve errors/screens and
follow the original supervised poweroff failure path only while its scope remains
valid. The operator must confirm actual stopped state. If shutdown fails, do not
automatically force Stop/reset. If pending media remains, record it truthfully;
do not claim the required final empty/no-pending state. Resolving it requires an
exact reviewed operator action, not a success-path guard receipt. The new
validator refuses these states rather than emitting a recovery authorization.

Shutdown loses `/run` and its raw probe/staged helper. A stopped-state detach
followed by another boot does not resume the previous procedure. The temporary
boot-id and staged bytes cannot be reused, and the allowed GRUB attempts must not
silently increase. Keep the uploaded ISO and disk intact.

## Alternative designs for later review

| Alternative | What it might solve | Open issue / required human scope |
|---|---|---|
| Qualify the existing medium-only operation on a separately authorized disposable target | Establish exact PVE/QEMU semantics and drive-lock/pending behavior without guessing | New target identity, live trial and failure/preservation authorization; no VM162/163/200 or AI-server substitute |
| Reviewed console transfer of the tiny pinned public helper/probe into tmpfs, without CD | Avoid optical-media presence entirely | New exact delivery/hash/transcription procedure and supervised console authorization; no unverified payload execution |
| Separately authorized dormant root-protected file staging on disk | Survive a stopped-state detach and boot | Persistent writes, custody/destination/manifest, clean entry and removal/preservation design need new authorization |
| Reviewed early-boot ephemeral watchdog integration | Reduce or remove human pre-arming delay | New trusted boot artifact/boot-chain review, identity, failure semantics, hash and explicit boot authorization |
| Change hotplug policy, remove hardware or use low-level QMP eject | Could alter media-change behavior | Not an approved workaround; requires new exact configuration/management authorization and safety review |

None is implemented, selected, installed or authorized by this sprint. A modified
probe waiving optical absence would also change the evidence contract and need a
separate design/release review; it cannot convert the existing pinned path to PASS.

## Temporary root and watchdog

The root shell is passwordless and can control the whole guest. No NIC/agent
reduces ingress but does not restrict root or protect other console viewers.
Keep console custody and supervision continuous. Root lock does not block the
debug shell. Restricting keyboard access is an operator control, not a tested
software boundary here.

| Interval | Actual protection | Required supervised disposition |
|---|---|---|
| Guest starts until shell appears | Trusted target/boot source and operator presence; no armed guest watchdog | Observe timing and ability to invoke the existing approved host ACPI failure path; do not claim automated cutoff |
| Shell appears until successful timer creation | Manual identity/TTY checks; root already available | Any check/entry/timer failure ends the attempt; preserve and close under approved scope |
| Timer nominally armed | Transient monotonic timer requesting graceful poweroff | Establish actual timer deadline, trigger service/command and remaining time with supported read-only evidence in the supervised procedure; `is-active` alone is insufficient |
| Staging/ejection/capture | Supervision and functioning watchdog | No extension to rescue capture; incomplete capture remains incomplete |
| Independent closer | Runtime mask/stop/kill/cgroup check, subject to H3/H4 | Do not treat submission, disappearing prompt or `exit` as successful closure; failed receipt/timeout requires original supervised failure handling |
| Following normal boot | Runtime state should be gone; clean GRUB/login observations required | Any debug arguments, unauthenticated root or inability to inspect is incomplete cleanup; no credential/boot-file repair |

The helper's local fallback does not cover its pre-`try` failures, and its unit's
45-second deadline is not justified against composed command budgets. A robust
future revision should test preconditions, command timeouts, timeout signals,
remaining children, failed poweroff and capture failure, with independent
shutdown-request coverage and a well-defined bounded budget. It must establish
identity before any target-sensitive action and avoid unsafe cleanup on a wrong
target. Those design constraints require review; simply wrapping every failure
in poweroff would risk acting on an unverified target. No new cleanup helper was
created or delivered in this sprint.

GRUB interception, installed generator compatibility, runtime masks, true cgroup
closure and ACPI shutdown remain supervised real-world checks. No repeated boot
or key-injection experiment is authorized by this document.

## Persistence and evidence recovery

Before executing any helper, the approved procedure must verify whole-CD size and
SHA256, mount read-only with restrictive flags, verify BOOT.PY against the pinned
hash, and only then execute it. The helper verifies LABPKG.PY before handing off.
An internal manifest alone is not a trusted helper pin. Do not execute anything
from an unknown medium to discover whether it is trusted.

Only unsaved kernel-line changes are allowed; preserve original/modified/clean
GRUB evidence. No saved GRUB state, bootloader regeneration, root unlock, password,
account, group, SSH, authentication or networking edits belong to this path.
The public-file snapshot has the limits in M5. A new baseline must not expose
credential content or silently broaden this authorization.

Capture approval reference and expiry, operator UTC/monotonic timeline, target
identity, complete raw config/status/pending outputs privately, current-view
selection, digest/readback hashes, host ISO storage identity/content verification,
GRUB/watchdog/error/closure screenshots and losslessly decoded probe pages in new
per-step directories. Retain the exact raw bytes separately from any JSON envelope;
do not normalize them and call the hash unchanged. Hash and retain the execution
packet through the existing trusted operator custody channel.

The offline validator's hash chain detects inconsistent supplied history, not
omitted observations, tampered clocks, fabricated origin or subsequent changes.
Reacquire immediately before each action; an earlier PASS expires as evidence for
the next state. A later invalid observation invalidates the chain. An absent final
receipt is incomplete, not proof that shutdown or cleanup happened.
