# Fixed-pin framework/test wheel closure R1 — data verification only

One bounded offline verification unit is complete. **The proposed closure contains
22 distributions; no environment was created and nothing was installed, extracted
into executable paths, imported from candidate wheels, or run as an application.**
Current source and all prior sealed packets remain unchanged.

## Exact target and result

The six roots, all with **no requested extras**, are:

| Root | Exact pinned version |
| --- | --- |
| FastAPI |0.141.1|
| Pydantic |2.13.5|
| APScheduler |3.11.3|
| pytest |9.1.1|
| pytest-asyncio |1.4.0|
| httpx |0.28.1|

This is the narrow real FastAPI/Pydantic/ASGI + APScheduler + pytest/httpx fixture
test scope. It is not the earlier12 critical candidate pins or the full JARVIS
application/lifespan dependency set. **pydantic-settings is not selected.** Optional
FastAPI extras, HTTP/2 and other extra-only dependencies are not activated.

- Exact fixed-pin closure:22 distributions,26 active dependency edges out of135
  recorded Requires-Dist evaluations. All active constraints and Requires-Python
  declarations pass against the current Linux/CPython marker environment.
- Inventoried141 wheel filenames/retained hashes; opened only the22 selected ZIPs.
  All selected identities match the127-version lock, artifact record, METADATA,
  WHEEL filename/tag declarations and current interpreter-supported tag set.
- Whole-wheel hashes match. All950 non-RECORD-self payload rows pass RECORD hash/
  size checks, read as data without extraction or execution. Optional signature
  files, if present, are not treated as verified publisher signatures.
- Selected wheel bytes:5,251,072; declared uncompressed bytes:17,019,384. Verifier
  bounded input/metadata/decompressed-hash/evidence accounting:25,733,869 bytes,
  below50MiB. Streamed whole-artifact hashing is separately allowed by scope.
  Metadata/WHEEL/RECORD entries are each capped at1MiB; ZIP structure, member count,
  declared entry/total expansion, duplicates, links and paths are bounded/rejected.
- No blocked network attempt or forbidden payload import was recorded.

The [machine evidence](evidence-20261030T231119946730Z.json) records the complete
artifact paths/hashes, source provenance strings, tags, marker contexts and every
active/skipped requirement. The
[proposed hash-required lock](proposed-closure-20261030T231119946730Z.lock)
includes all22 runtime/test transitive distributions, not merely the roots.

## Tool and input identities

Normal installed evaluator: **packaging26.0** from
`/usr/lib/python3/dist-packages/packaging`, using its Requirement, Version,
SpecifierSet, Marker and wheel-tag APIs. [Tool discovery](TOOL-DISCOVERY.json)
records ordinary installed metadata; pip/wheel are absent. No private runtime
search, wheel import trick, package installation or partial PEP parser was used.
Loaded normal packaging tool-module source hashes are in the machine evidence.

The proposed future closure contains **packaging26.3 as a wheel payload**. That
payload was inspected/hashed only; it did not supply the running evaluator.
This is a validator for one exact pinned version per name, not a version-search
resolver. Missing/incompatible pins, direct URL requirements or unsupported
nonmonotone extra activation stop with a precise blocker; no alternate version,
artifact fallback or network resolution is attempted. Same-hash duplicate copies
of typing_extensions are retained in the public inventory; one target-directory
copy is selected deterministically before hashing, with no fallback on failure.

Inputs are the existing verified public Gate6L bundle and retained provenance:

- Artifact record SHA-256:
  `9cfd2ed635f347521164b4d99ecf1cc82396036ab52e8c377386181dabf3b837`.
- Exact127-version lock SHA-256:
  `b07d5613eb50547b99229b2230bf90bd9d884dfcc869ecc025ffb003449d680a`.
- Proposed22-package lock SHA-256:
  `c33e6a6d1b55691d2ccb32896fc8bc60ebaf213e0060275aadbfd230cfff0ac8`.
- Successful inspection receipt SHA-256:
  `dda702ee87a2a9e0ca6edceb7691eb31ef934bc1b8309595d100af5dac024b3b`.
- Verifier SHA-256:
  `b6e3414c2da4aebe72c38732923be31a605a023cd78e6eedba9b1573f8bbab97`.

`SOURCE-AND-PRESERVATION.json` binds the current code, input/tool/test identities,
prior manifests and dirty base. The3GB outer bundle was not copied or reopened;
selected loose public wheels were streamed directly. No bundle state was modified.

## Meaningful verifier checks and independent review

The one new synthetic suite passed **13 unittest methods /19 subcases**. Its
[receipt](test-evidence-20261030T231444320647Z.txt) binds test/verifier hashes.
Fixtures contain deliberately non-importable Python payload data, valid complete
wheel metadata/records and adversarial mutations. They cover unsafe/duplicate/
prefix/link/oversized entries, wrong whole hash/tags, RECORD digest/size/coverage,
metadata/read budgets, Linux/Python/extra marker include/skip behavior, transitive
test dependencies, missing pins and incompatible constraints. The suite reads no
actual bundle wheels and imports no candidate package. No unrelated passing suite
or historical application baseline was rerun.

The existing separate GPT-6 Astra/high reviewer inspected this verifier, receipt
and lock read-only. It found no blocking issue in fixed-pin closure, deterministic
artifact selection, marker/tag checks or data-only artifact/RECORD verification.
It did not run the verifier/tests or import/install anything. Its closure expressly
excludes runtime/native-ABI, signature, installed-origin and full-app claims.

To reproduce in a future review scope using the existing normal tool only:

```sh
python3 -B tasks/jarvis-framework-closure-r1/test_verifier.py
python3 -B tasks/jarvis-framework-closure-r1/verify_closure.py
```

The second command creates exclusive new evidence/lock files; it would need its own
successor evidence inventory. Do not rerun it merely to overwrite this sealed
milestone, and do not install this proposed lock under the current verification-
only instruction.

## Actual technical limits

The environment is CPython3.14.4, Linux x86_64, SOABI
`cpython-314-x86_64-linux-gnu`. The native pydantic-core wheel matches cp314/cp314
manylinux2014/manylinux_2_17 tags according to the installed evaluator. That is
metadata compatibility, not proof its ELF libraries, symbol versions, native
extensions or runtime behavior work. No native candidate library was loaded.

Wheel RECORD hashes are internal integrity checks; matching retained public
artifact hashes adds no publisher signature/attestation or review of payload code.
Installed origin, sandbox enforcement, installer tooling, native ABI/library
qualification and current-source behavior remain untested. The lock does not
cover full app/lifespan imports, optional hardware/provider packages, audit threads,
real FastAPI/ASGI response processing or real APScheduler timing/lifecycle. The
earlier AST/inert-backend and historical7741/11 evidence stays in its original
scope. No integration environment is started after this unit.

## Unchanged privileged gates and unresolved product decisions

The existing [staged setup packet](../proxmox-automation-phase3-review-r1/APPROVAL-PACKET.md),
[installation](../proxmox-automation-phase3-review-r1/INSTALLATION.md),
[live acceptance](../proxmox-automation-phase3-review-r1/LIVE-ACCEPTANCE.md) and
[stop/revoke](../proxmox-automation-phase3-review-r1/STOP-AND-REVOKE.md) remain pending:

1. Specifically authorized Nexus restricted executor/protected installation with
   actual identity/no-escalation proof. Disabled, no-transport synthetic credential
   denial and code/config/unit protection must pass before real credential issuance;
   fresh root-controlled attestation is limited to600 seconds.
2. Specifically authorized new separated PVE principal/token with only
   VM.Audit+VM.Console on /vms/164, propagate0 and the bounded initial3600-second
   window. Existing observer stays unchanged; Codex receives no root credential.
3. Trusted VM164 installed-root/bootstrap context and actual guest machine-id,
   numeric/filesystem bindings, pinned worker and exclusive ttyS0. Passwords remain
   locked, no SSH/NIC/guest-agent workaround. Missing bootstrap facts require an
   exact separately scoped maintenance plan, not generic rescue authority.
4. Explicit timed live read-only activation/acceptance after those gates. Separate
   authority remains necessary for privileged/mutating catalog expansion and
   privileged Gate6K qualification. VM162, VM163 and the AI server stay excluded.

Nothing was denied, installed, granted or activated here. Kernel/security settings,
identities, credentials, daemon state and shared mount/cache/tmp policies were not
changed. Routine authorized offline engineering does not acquire a blanket human-
approval gate from this technical verification limit.

The owner still has product decisions to make before operational execution:

- **Enforced process ownership:** choose single-owner/fencing/transaction behavior
  before supporting multiple writers; no daemon, migration or hash-check lock exists.
- **HTTP and occurrence idempotency/outbox:** define request/occurrence keys,
  duplicate/lost-response reconciliation and atomic task/audit acknowledgements.
- **Already-admitted enqueue cancellation:** current admitted work can finish
  after remove/stop; stronger cancellation needs an explicit cross-component policy.
- **Executor/tool-authority wiring:** TaskQueue has no production draining executor.
  Define authenticated catalog/grant/approval mappings; arbitrary goal text must not
  silently become shell/tool authority. The broker remains standalone/unactivated.

Stop at this review-ready metadata milestone. No further code/hardening unit or
installation/import is part of this completion.
