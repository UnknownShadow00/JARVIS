# Offline test results

**71 tests passed; 0 failures, 0 errors, 0 skips.** Actual final invocation and
source digests are in `evidence/OFFLINE-RESULTS.json`; per-method output is in
`evidence/offline-tests.log`. These are synthetic offline tests, not pve evidence.

Coverage exercised:

- Every case's exact argv, source pin, absolute six-decimal boot deadline,
  Type=exec, UID/GID65534, resource/security properties and no VM/root-worker route.
- Namespace format, injection/unknown-case rejection, all collision suffixes,
  consumed-name refusal and distinct rearm without changing session expiry.
- Root/other/string/bool UID refusal, supplementary group/process uncertainty,
  required privilege/custody evidence references and source/package/host drift.
- Explicit UTC expiry, ≤45-minute duration, elapsed BOOTTIME, clock regressions,
  UTC drift, boot changes, suspend-offset change, minute35 cutoff and stale argv.
- MONOTONIC/BOOTTIME conversion with a historical50s offset, ambiguous equal
  clocks, contradictory documentation, invalid samples and UNKNOWN refusal.
- Success/exit7, timeout, missing executable/import failure, missing execution
  proof, early/late callback classification, failed/inactive/fired timer rejection.
- Exact owned timer-then-service cleanup, no foreign/changed-argv/changed-boot
  stop, retained failed state, idempotent terminal handling and interruption
  after timer stop with service still running.
- Result manifests refusing unsupported full qualification, missing evidence,
  unresolved reviewed-pass claims, scope-limit deletion and evidence traversal.
- Catalogue/builder equality, unfilled result template, literal exclusive
  installer safeguards, Python syntax for all future command bodies, original
  sealed canary UID0 rejection and original R3 codec UNKNOWN/offset handling.

The runner installs subprocess, network, os.system and signaling tripwires.
No process is launched by these tests; no real timer/service/callback installation,
VM command, credential operation or network access is part of them. No application
package/dependency was installed. No npm/pip audit or commit was needed because
this task adds standalone standard-library offline tooling and does not commit.

Installation bodies are syntax/static-reviewed, not installed or exercised as
root against real paths. Systemd property support, real callback firing, kernel
limits, UID privilege denial, timer failure serialization and cancellation remain
unqualified until separate approved host evidence exists. Structural evidence
validators cannot authenticate a host, a reviewer or a policy assertion.

Additional actual checks:

- R3 verifier reexecuted locally: PASS_OFFLINE_HOST_ENFORCEMENT_ENGINEERING_ONLY;
  exact source-tree/callback pins and inert archive valid. Its historical294-test
  record was verified; those294 tests were **not rerun** or added to this71 count.
- All96 R3 files read/indexed with SHA256 and rechecked byte-for-byte unchanged.
  The verifier also confirms247 predecessor files,5 links and its original loop
  log prefix. No sealed packet source or evidence changed.
- All new Python files parsed and JSON files decoded by the packet verifier;
  every new artifact is covered by the integrity manifest except the manifest
  and its seal, which bind each other as documented.

Safe reproduction from the JARVIS root:

```text
python3 -I -B -S tasks/jarvis-v2-vm164-stage2-operator-preparation-r1/src/verify_packet.py
```

For a new test run, copy the preparation folder into a NEW local scratch folder
under tasks alongside the sealed R3 directory, then run `tests/run_offline.py`
in that copy. The runner writes a fresh timestamp and results; running it inside
the sealed preparation folder invalidates its manifest. Do not reseal changed
results as if they were this original release.
