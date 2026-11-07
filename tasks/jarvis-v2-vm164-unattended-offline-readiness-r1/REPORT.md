# VM164 offline readiness audit r1

Offline engineering completed. **Do not start the bootstrap from this report.**
The reported `order=scsi0;ide2` fails the official guard. Restoring
`order=scsi0` remains operator-required and has **not** been executed here.
Live ejection with `hotplug: 0` and the temporary root-access lifetime remain
unqualified. Installation, Gate 6K and production promotion remain separate gates.

Work used the `workspace-write` task profile, existing Python standard libraries,
repository bytes, and synthetic fixtures. No external network, package install,
credential access, infrastructure connection, VM command, console interaction,
application startup, Git commit/push or release publication occurred. No pinned
RC1, bootstrap, lab-readiness, incident or production files were changed. The
existing dirty application worktree was left alone. The only shared-file update
is the required append to `tasks/loop-log.md`.

Start with [OPERATOR-HANDOFF.md](OPERATOR-HANDOFF.md), then read
[FINDINGS.md](FINDINGS.md) and [FAILURE-ANALYSIS.md](FAILURE-ANALYSIS.md).

## Evidence categories

| Category | What is established | What is not established |
|---|---|---|
| Verified local facts | All 104 regular files and 5 symlinks match the bootstrap seal; final ISO is 196608 bytes with SHA256 `fd91b8b07243565e41aad3180a6fa569907d0e85edea6f95655b9983e56d8154`; builds 9/10 match it; original log prefix remains intact | Location/content of media on the actual host |
| Operator-reported facts | VM164 was stopped, diagnostic ISO attached, `order=scsi0;ide2`, no NIC/agent, hotplug 0; correction approved but unreported as executed | Current live state or successful correction; no raw fresh readbacks supplied to this sprint |
| Code-derived conclusions | Exact guards, unsafe defaults, cleanup exception paths and timeout composition described in FINDINGS | Actual installed systemd/PVE/QEMU behavior |
| Synthetic findings | 41 new test methods pass: 32 validator methods and 9 pinned-hazard methods; 16 CLI fixtures behave as expected; original 43 methods replay successfully with mocked system operations | Hypervisor behavior, root containment, physical ejection, real shutdown, cross-UID separation |
| Supervised hypotheses | Required tests and stop conditions in FAILURE-ANALYSIS | None silently promoted to verified facts |

The 9 hazard tests pass when they reproduce the existing defect. They do **not**
mean the pinned helper has been fixed. The first new test run found one error in
the synthetic digest generator; it was corrected in the new harness. That log is
retained. No production implementation was changed to make a test pass.

## Deliverables

- [tools/state_validator.py](tools/state_validator.py): standalone local JSON
  validation, strict identity/media/pending/configuration checks, bounded strict
  JSON parsing, UTC freshness policy, readback hashes and transition continuity.
  It has no transport, subprocess or write operation. Receipts always deny live
  evidence, authorization, guest cleanup proof and Gate 6K qualification.
- [VALIDATOR.md](VALIDATOR.md): input contract, replay command and limitations.
  Both synthetic and saved inputs are evaluated offline. No fixture is a live
  readback. No receipt grants authority for a later action.
- [tests/test_state_validator.py](tests/test_state_validator.py) and
  [tests/test_pinned_hazards.py](tests/test_pinned_hazards.py): meaningful negative
  cases plus isolated reproductions against unchanged pinned code.
- [fixtures/INDEX.json](fixtures/INDEX.json): 16 retained synthetic CLI cases,
  including the reported unsafe boot shape and a hypothetical restored shape.
- [evidence/local-artifact-review.json](evidence/local-artifact-review.json):
  local bootstrap inventory/media checks, in-memory bundle/wheel verification,
  dependency and SBOM observations. No payloads were executed or extracted.
- [RC1-OFFLINE-REVIEW.md](RC1-OFFLINE-REVIEW.md): secondary installation blockers,
  native compatibility, dependency/SBOM scope and interrupted-publication recovery.
- `SHA256SUMS`: final new-folder inventory, excluding itself. It is a local
  integrity record, not a signature or operator approval.

## Scope of verification

The packet's complete local inventory was hashed; current policy documents,
all current tools, payload, tests, retained generator/unit outputs and media
inspection were reviewed. Earlier media builds and superseded deliveries were
preserved and inventoried as history. The approved delivery remains r4 only.
[REVIEW-SOURCES.md](REVIEW-SOURCES.md) maps the relevant predecessor records and
their supersession. Historical instructions to leave a failed installer running
do not override the user's newer stopped/installed-OS report or this sprint's
absolute prohibition on infrastructure access.

The full `verify_packet.py` CLI was **not** rerun: it traverses external `/home`
pins and delegates to the entire predecessor verifier. The new local-only review
checks the bootstrap manifest/seal, all packet bytes/links, ISO inspection,
reproducibility bytes, original log prefix, final installation bundle, wheel
RECORDs and installed-manifest pin. It does not relabel the prior reported
`PASS_LOCAL_PREPARATION_ONLY` or `PASS_HOST_READBACK_ONLY` as a fresh execution.
No current advisory lookup or native/OS package qualification was attempted.

## Reproduce offline

From the project root, using existing Python only:

```sh
python3 -I -B -S -m unittest discover -s tasks/jarvis-v2-vm164-unattended-offline-readiness-r1/tests -v
python3 -I -B -S tasks/jarvis-v2-vm164-unattended-offline-readiness-r1/tools/replay_fixtures.py
python3 -I -B -S tasks/jarvis-v2-vm164-unattended-offline-readiness-r1/tools/review_local_artifacts.py
```

Tests create disposable files only beneath this new folder's `evidence/` and
remove their own temporary files. The artifact review hashes repository files
and constructs the proposed install inventory in memory. It does not call
installer/probe entry points, observer/broker clients, shell, system manager or
ISO builder. The replay tool launches only the new local validator.

Acceptance: **PASS for offline audit, validator, adversarial fixtures and handoff**.
**BLOCKED for live bootstrap readiness**, pending the findings' supervised
decisions and proof. No live action is claimed complete.
