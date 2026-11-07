"""Trusted report builder; never imports application code on the host."""
from pathlib import Path
import ast
import collections
import datetime
import difflib
import hashlib
import json
import re
import shlex
import subprocess

O = Path(__file__).resolve().parent
R = O.parents[1]
F = O / "final-2"
def get(name): return json.loads((O / name).read_text())
def put(name, value):
    (O / name).write_text((value.rstrip() if isinstance(value, str) else json.dumps(value, indent=2)) + "\n")
manifest = get("final-2-manifest.json")
identity = get("SOURCE-IDENTITY.json")
reconciliation = get("final-source-reconciliation.json")
files = {x["path"]: x for x in manifest["files"]}
def line(path, phrase):
    return next(i for i, text in enumerate((F / path).read_text().splitlines(), 1) if phrase in text)
def source(path, phrase):
    return f"[{path}:{line(path, phrase)}](final-2/{path}#L{line(path, phrase)})"
def json_output(path):
    for value in (O / path).read_text().splitlines():
        if value.startswith("{"):
            return json.loads(value)
    raise AssertionError(path)

batches = []
for label, stem in [
    ("HTTP, WebSocket, authentication and ancestry", "http_regressions_updated_final"),
    ("Execution, scheduler, receipts, CLI and lifecycle", "execution_regressions_updated_final"),
    ("Signed transport and offline publication", "transport_regressions_updated_final"),
    ("Ledger, rollover, restoration and witness renewal", "durability_regressions_final"),
]:
    run = get("runs/regression-" + stem + ".json")
    assert run["exit_code"] == 0 and run["snapshot"] == "final"
    assert all(files[x["path"]]["sha256"] == x["sha256"] for x in run["snapshot_files"])
    artifact = "agents/regression/artifacts/" + stem + ".txt"
    text = (O / artifact).read_text()
    count = int(re.search(r"(\d+) passed", text).group(1))
    batches.append(dict(label=label, cases=count, artifact=artifact,
                        manifest="runs/regression-" + stem + ".json",
                        sha256=hashlib.sha256((O / artifact).read_bytes()).hexdigest()))
total = sum(x["cases"] for x in batches)
assert total == 168
integration_artifact = "agents/integration/artifacts/sprint6_replay_final.txt"
integrated = json_output(integration_artifact)
assert len(integrated["passed_scenario_groups"]) == 4
assert get("runs/integration-sprint6_replay_final.json")["exit_code"] == 0
before = json_output("agents/authority/artifacts/authority_socket_probe.txt")
after = json_output("agents/authority/artifacts/authority_socket_final_checked.txt")
assert before["results"][0]["missing"]["status"] == 200
assert before["results"][0]["cancel_missing"]["status"] == 200
assert after["results"][0]["missing"]["status"] == 401
assert after["results"][0]["cancel_missing"]["status"] == 401
assert after["results"][0]["ready"]["status"] == 401
assert after["results"][0]["task_status_after_requests"] == "pending"
assert after["results"][1]["cancel_valid"]["status"] == 200
assert after["stock_startup_error"] == "authority_unenrolled_or_missing"

copy_inputs = []
for text in (F / "Dockerfile").read_text().splitlines():
    if text.startswith("COPY "):
        copy_inputs.extend(shlex.split(text)[1:-1])
assert set(copy_inputs) == {"requirements-core.txt", "app", "assets", "frontend", "config.yaml.example"}
patterns = (F / ".dockerignore").read_text().splitlines()
assert "**" in patterns
assert all("!" + name + ("/" if name in {"app", "assets", "frontend"} else "") in patterns for name in copy_inputs)
put("build-context-review.json", dict(copy_inputs=copy_inputs,
    review="Static review against Docker documented last-match/negation semantics. Only COPY roots included; runtime/config/secrets/evidence outside them excluded; nested env/key/database/cache/node_modules denied.",
    qualification="No Docker daemon, image build, remote context upload or container deployment invoked.",
    reference="https://docs.docker.com/build/concepts/context/#dockerignore-files"))
put("RESULTS.json", dict(final_batches=batches, distinct_pytest_cases=total,
    integrated_scenario_groups=integrated["passed_scenario_groups"], integrated_artifact=integration_artifact,
    socket_before="agents/authority/artifacts/authority_socket_probe.txt",
    socket_after="agents/authority/artifacts/authority_socket_final_checked.txt",
    uid_qualification="agents/authority/artifacts/namespace_probe.txt",
    source_identity=identity, runtime_snapshot="final", package_snapshot="final-2",
    nonruntime_difference="Only .dockerignore added after runtime snapshot; all tested code/test/config bytes identical.",
    counts_policy="Final four batches only; repeated intermediate passes and prior Sprint6 totals are excluded. Four integrated scenario groups and socket/UID experiments are counted separately.",
    expected_red_evidence=["agents/ue5/artifacts/ue5_red.txt", "agents/storage/artifacts/storage_creation_red.txt"],
    intermediate_failures="Retained HTTP batch exposed a then-different binary close code and inherited group-writable fixture ancestors. Subsequent batch hit thread allocation under fixed cage limits. Policy/tests aligned, cage umask explicitly0077, pure auth dependency made async; final runs pass with unchanged CPU/memory/process/disk limits."))

statuses = [
    dict(id="D7", fingerprint="app/server.py:ue5-session-cleanup", status="fixed",
         outcome="Registration, logging, parsing, receive/cancel/close failures clean in finally; policy close delivery bounded; repeated cleanup idempotent; finite active+accepting manager state.",
         evidence=[batches[0]["artifact"], "agents/ue5/artifacts/ue5_red.txt"]),
    dict(id="A", fingerprint="app/server.py:anonymous-loopback-authority", status="anonymous_HTTP_path_closed",
         outcome="Supported synthetic admitted serving mode reproduced old read/cancel exposure using genuine lifespan and separate native process. Final router mandates configured nonblank Bearer on every authority route, including /ready and embedded routers. Actual production/differentUID/browser exploitation was not established.",
         evidence=["agents/authority/artifacts/authority_socket_probe.txt", "agents/authority/artifacts/authority_socket_final_checked.txt", batches[0]["artifact"]]),
    dict(id="B", fingerprint="app/agent/ledger.py:filesystem-ancestor-replacement", status="source_hardened_external_qualification_remains",
         outcome="Current ancestry/owner/mode checks plus lifetime identity fences reviewed and tested. Private descendants are created using validated directory descriptors; unsafe ancestor and racing symlink refused before creation. SameUID/root/privileged filesystem races and actual deployment remain outside proven protection.",
         evidence=["agents/storage/artifacts/storage_creation_red.txt", batches[0]["artifact"], batches[3]["artifact"]]),
    dict(id="POST-CUTOFF", status="reconciled", outcome="All initial9 changedpaths+1newdoc plus all26 final changed/added public paths reviewed; lifecycle/crypto and43 current broker files preserve audited bytes.", evidence=["final-source-reconciliation.json"]),
    dict(id="BUILD-CONTEXT", status="hardened_static_only", outcome="Docker context restricted to explicit COPY inputs and nested runtime/secret exclusions; no actual build qualification.", evidence=["build-context-review.json"]),
]
put("REMEDIATION-STATUS.json", statuses)

summary = f"""# Security remediation and verified offline baseline

Implemented and validated the requested remediation against the active JARVIS V2 source. **{total} distinct selected pytest cases passed**, plus **four integrated scenario groups** and a real isolated-loopback comparison using a separate client process. Prior audit and Sprint6 pass totals are not counted as new.

Primary source: `{identity['base_head']}+dirty:{identity['source_revision_sha256']}`; {identity['source_files']} public files, {identity['app_python_files']} application Python files. [Exact identity](SOURCE-IDENTITY.json), [source hashes](SOURCE.sha256), [manifest](final-2-manifest.json), [run results](RESULTS.json).

## Changes and observed behavior

- `/ue5` no longer leaves stale entries on binary/malformed input, disconnect, cancellation, exceptions, partial registration, audit failure or failed/slow policy close. Cleanup is synchronous and idempotent; valid text and broadcasts survive. Policy-close delivery is limited to two seconds. The 32-slot active-plus-accepting limit and slot reclamation are tested. The sibling `/ws` registration/audit gap was also closed.
- Authority routes now require a configured nonblank matching Bearer credential, even on loopback and in independently embedded routers. `/ready` has no identity exception. Missing/invalid/malformed/query-only credentials are refused. The tiny authorization dependency is async, avoiding a worker thread per check. Valid read/cancel/receipt replay behavior remains functional.
- Private storage creation now validates retained parents before descriptor-relative no-follow creation. Unsafe ancestors cause refusal before descendants appear; new nested directories are0700 even under umask000. Existing owner/inode/mode fences remain fail closed. This is not an atomic SQLite VFS or a hostile-owner guarantee.
- API regression callers now supply explicit synthetic credentials; the authenticated missing-store test still reaches and verifies storage refusal rather than hiding it behind401. Public configuration/docs explain the new contract. `.dockerignore` limits build context to Dockerfile COPY inputs and excludes nested runtime/secret material.

Key implementation: {source('app/server.py','async def ue5_endpoint')}, {source('app/server.py','async def _close_ue5')}, {source('app/agent/api.py','async def require_authority_identity')}, {source('app/agent/storage_paths.py','def _walk')}, {source('app/agent/ledger.py','def private_directory')}.

## Authority-access investigation

The pre-fix source genuinely started with explicitly admitted dummy authority state inside an unshared network namespace. A separate native HTTP process read and cancelled an operator-owned dummy task without a token:200/200. This resolves the prior *synthetic serving reachability* uncertainty; it does not prove a production or distinct-UID attack. Unprovisioned stock startup still refused `authority_unenrolled_or_missing` before creating state.

The final source served the same admitted-empty-token fixture, but task read, cancellation and `/ready` returned401 and the task stayed pending. Configured-token requests rejected missing/wrong/malformed/query credentials; the valid-token control read and cancelled successfully. The actual lifespan and scheduler ran; only unrelated provider/hardware/background housekeeping was inert. [Before](agents/authority/artifacts/authority_socket_probe.txt), [after](agents/authority/artifacts/authority_socket_final_checked.txt).

Host is not an identity allowlist: arbitrary native Host/Origin values cannot replace a missing credential; a valid credential works regardless of those headers. Foreign-origin preflight returned400 without allow-origin. No actual browser was run. Distinct UIDs were infeasible: only one UID is mapped, and changing to another fails with errno22; no privileged mapping helper or host identity was created. [Qualification](agents/authority/artifacts/namespace_probe.txt).

All credential holders still share the one operator's service actor. Other non-authority assistant routes retain their local-mode behavior when the token is empty; configure a token for the whole deployment. No multi-user or hostile same-UID process isolation is claimed.

## Fresh validation

| Batch | Passed cases | Evidence |
|---|---:|---|
""" + ''.join('| '+b['label']+' | '+str(b['cases'])+' | [output]('+b['artifact']+') |\n' for b in batches) + """
The integrated replay used one shared enrolled history: API admission, signed pure transport, real nominal scheduler callbacks, durable receipts, cancellation, witness renewal, lost reply/UNKNOWN, actual FD-only operator reconciliation, restart publication hold, separately permitted publication, inert archive restore and durable nonactivating approval. The four scenario groups passed with zero real-adapter activation. [Full retained demonstration](agents/integration/artifacts/sprint6_replay_final.txt). Existing Sprint6 fixture code was copied; only scratch-root literals were adapted, with hashes in fixture-manifest.json. Background provider/hardware housekeeping was inert; authorization/storage/recovery operations were real product code.

Every execution was sequential and network-isolated, with empty allowlisted environment, readonly target/toolchain, explicit umask0077 and fixed CPU/memory/process/disk/output limits. No new packages were installed. The runtime snapshot is `final`; the final package adds only `.dockerignore`, with every runtime-tested source/test/config byte identical. Docker context was reviewed statically against [Docker's documented matching rules](https://docs.docker.com/build/concepts/context/#dockerignore-files); no image build or daemon call occurred.

## Reconciliation and evidence integrity

[RECONCILIATION.md](RECONCILIATION.md) covers the exact frozen-audit-to-current delta. All ten original excluded paths were reviewed; new auth, WS, ancestry, docs and tests are included. Twelve key lifecycle/crypto implementations and all43 public current-broker files are byte-identical to the audit snapshot. Core decisions, receipts, witnesses and inert restoration were exercised again, not inferred from old totals.

All2,531 prior audit files were read and hashed without modification. Source and public evidence from the completed Sprint6 packet were reviewed. A separate, concurrently assembled release-review record does not match all final source pins, so its PASS is not inherited as approval of this baseline; see related-review-pin-check.json. Original sealed reports/snapshots remain unchanged. This packet is a remediation/delta assessment, not a new independent whole-repository penetration test.

## Limits and remaining work

No production config, real database/credential, model/provider, actual desktop/audio, Proxmox/VM, NIC, guest console, power operation or privileged Gate6K qualification was used. No real executor was enabled. No commit, push or deployment was performed.

Actual different-UID/browser/ingress/TLS behavior, multiworker/global admission, pre-ASGI frame bounds, independent token/key/time/witness custody, deployment ACL/mount/SQLite/WAL/fsync/power-loss semantics and installed broker identities remain unqualified. History is still lifetime-capped and scan-based; canonical Unicode output can conservatively hit the transport frame bound and remain UNKNOWN. Actual dependency advisory/binary provenance was not re-audited or invented from source manifests. These are explicit limits, not confirmed exploits. [Security assessment](SECURITY-ASSESSMENT.md), [reproduction](REPRODUCE.md), [operator/client contract](../../docs/security_baseline.md).
"""
for a,b in {'directories are0700':'directories are 0700','umask000':'umask 000','behind401':'behind 401','returned401':'returned 401','returned400':'returned 400','errno22':'errno 22','and all43':'and all 43','All2,531':'All 2,531','original9 changedpaths+1newdoc':'original 9 changed paths + 1 new document'}.items(): summary=summary.replace(a,b)
put("REPORT.md", summary)
put("SECURITY-ASSESSMENT.md", """# Updated security assessment

Scope is the requested remediation and exact active-source delta after comprehensive audit R1. It closes known code paths; it does not certify deployment or attribute a production exploit. Machine statuses are in REMEDIATION-STATUS.json.

| Prior concern | Final disposition | Evidence boundary |
|---|---|---|
| D7 binary UE5 stale entry | Fixed, with all-exit cleanup, bounded policy close and finite manager capacity | Real ASGI state machine, native TestClient and repeated hostile sessions; no global availability claim |
| A anonymous loopback authority | Supported synthetic exposure reproduced before correction; anonymous authority path now closed | Genuine lifespan/socket plus separate same-UID process; final401/unchanged dummy task and valid credential200 controls; differentUID/browser/production unqualified |
| B ancestor replacement | Stronger source ancestry/creation/fence controls verified; original exploit was not established | Descriptor-relative creation, writable/symlink refusal and same-leaf parent replacement tests; actual privileged/filesystem boundaries remain external |
| Screenshot shared temporary output | Prior rejection remains applicable | Registry/getter/server/dictation effect gates unchanged; no active supported capture adapter introduced |
| Earlier D1-D6 call sites | Existing closures retained | Gate/source hash checks plus execution/CLI/process/audio regressions |
| Build context | Allowlisted and sensitive nested artifacts excluded | Static Dockerfile/pattern review only; no actual build |

No new confirmed exploitable vulnerability is asserted by this bounded pass. The before/after HTTP experiment establishes configuration behavior, not an OS privilege escalation. The inherited single-operator contract trusts process/database control; shared Bearer authentication is not per-principal authorization. Configure a private token for all deployment interfaces and protect its custody.

Queue/scheduler identities, synthetic execution authorization, HMAC receipts/checkpoints, recovery decisions, witness renewal and archive/branch operations retain audited implementation bytes except the reviewed storage ancestry integration. The integrated replay confirms their connection on the final executable source. New ancestry checks do not authorize enrollment, reset checkpoints, repair rollback, replay unknown effects or activate a restore. Proxmox broker files are unchanged and remain unconnected.

Remaining assurance work: distinct OS principals, actual browser/ingress/TLS, global/multiworker admission, upstream frame allocation, physical filesystem/ACL/locking/rename/WAL/fsync/power loss, independent secret/reference/time custody, resolved dependency/advisory/binary provenance and real broker restricted identities. The finite128-grant history bound and full history scans remain deliberate limits; oversized canonical Unicode wire output can remain conservative UNKNOWN. No severity is assigned to these unqualified/hardening notes.
""")

rows = reconciliation['changes']
put("RECONCILIATION.md", "# Audited snapshot to final source\n\n" +
    f"Audited source: comprehensive R1 snapshot-packaged,390 files. Final package:398 public files,26 added/changed paths. Exact hashes below and in final-source-reconciliation.json. Original ten post-cutoff paths were all reviewed.\n\n| Path | State | Final SHA256 |\n|---|---|---|\n" +
    ''.join('| `'+x['path']+'` | '+x['state']+' | `'+x.get('sha256','removed')+'` |\n' for x in rows) + """

## Boundary review

- Authentication/API/WebSocket: router-wide async configured-credential enforcement including `/ready`; normal middleware/Origin controls preserved; UE5 all-exit cleanup, policy close deadline, finite manager state and sibling registration cleanup tested.
- Execution authorization: unchanged exact pure endpoint/type/permit/MAC enforcement. Test forgery now authenticates altered dummy response bodies where needed, testing semantic binding beyond MAC failure; second fixed hash endpoint adds no arbitrary destination.
- Queue/scheduler/receipts: implementation bytes unchanged; real worker API, nominal occurrence identity, cancellation and original receipt replay tested with explicit credentials.
- Recovery decisions/witness renewal/archive restoration: implementation bytes unchanged; same-history integrated witness renewal, UNKNOWN reconciliation, separate publication, inert restore and nonactivating proposal approval tested. New storage checks add refusal, not recovery or activation authority.
- Filesystem: ancestry and lifetime fences integrated; creation validated before mutation through retained no-follow directory descriptors. Parent replacement, bad modes and symlink races tested with dummy paths. No atomic SQLite VFS or hostile-owner guarantee.
- CLI/resource manager: original post-cutoff removal of local offline host effects and stronger child-lease identity checked. No implicit process start/termination fallback remains; regressions use declared inert dummy children only.
- Proxmox: all43 public current-successor files match audited hashes. No broker/worker hookup, token/ACL/guest/NIC/console/power or qualification operation occurred.
- Configuration/docs/build: credential contract corrected, runtime config untouched; Docker context now restricted to explicit COPY inputs. No Docker build or dependency installation occurred.

Initial engineering source was dirty. Concurrent source edits already in progress were preserved and reviewed; this task additionally completed lifecycle, auth/readiness, descriptor-relative creation, tests, docs and context hardening. SOURCE.patch records this task's before-to-final public-source differences; it is not a git reset or a rewrite of prior sprint changes. Separate review/source pins are not conflated with final runtime evidence.
""")

put("REPRODUCE.md", """# Reproduce the offline baseline

Run from the JARVIS root. The runner creates only an isolated ephemeral namespace with readonly source/toolchain and bounded scratch. It needs the already available bwrap, Python3.14 and recorded local dependency tree; it installs nothing and never loads production config/data. Do not substitute live databases or provider settings.

Evidence promotion is exclusive. Copy each named harness to a **fresh basename** in the same owner's scratch directory for every replay, then run:

```sh
python3 tasks/jarvis-security-remediation-r1/sandbox-runner.py regression tasks/jarvis-security-remediation-r1/agents/regression/scratch/NEW_BASENAME.py final-2
```

| Purpose | Existing harness (copy before replay) | Owner |
|---|---|---|
|109 HTTP/WS/ancestry cases|agents/regression/scratch/http_regressions_updated_final.py|regression|
|33 execution/scheduler/lifecycle cases|agents/regression/scratch/execution_regressions_updated_final.py|regression|
|13 transport/publication cases|agents/regression/scratch/transport_regressions_updated_final.py|regression|
|13 ledger/restore/witness cases|agents/regression/scratch/durability_regressions_final.py|regression|
|Genuine lifespan/socket, separate client process|agents/authority/scratch/authority_socket_final_checked.py|authority|
|Four integrated shared-history groups|agents/integration/scratch/sprint6_replay_final.py|integration|

Use the corresponding owner and harness path for the last two rows. All final runtime code/test/config bytes match the runtime-tested `final` snapshot; `final-2` adds only .dockerignore. Per-run manifests bind source, harness, runner and inputs. Source hashes are in SOURCE.sha256.

Pre-fix comparisons are deliberately separate: ue5_red.py targets snapshot `red`; authority_socket_probe.py targets `before`; storage_creation_red.py targets `candidate-3`. Expected failures must not be mixed into final pass totals or replayed as if final source. Original artifacts and intermediate failures remain retained.

Limits: 10CPU seconds,512MiB address space,64 processes,96 descriptors,2MiB individual file size,32MiB scratch,25-second wall,256KiB output, explicit0077 umask, empty allowlisted environment, no external network/host home/credentials/devices/services. Trusted parent code promotes only bounded predeclared regular output using retained no-follow directory descriptors after namespace termination. Network listeners exist only inside the unshared network namespace, on ephemeral loopback ports with dummy state. DifferentUID mapping is unavailable. Docker configuration is statically reviewed; no actual image build was performed.
""")

patch = []
initial = {x['path']:x for x in get('baseline-source.json')}
for path in sorted(set(initial)|set(files)):
    old_text=(O/'before'/path).read_text().splitlines(True) if path in initial else []
    new_text=(F/path).read_text().splitlines(True) if path in files else []
    if old_text != new_text:
        patch.extend(difflib.unified_diff(old_text,new_text,fromfile='before/'+path,tofile='final/'+path))
(O/'SOURCE.patch').write_text(''.join(patch))
put("OUTPUTS.md", """# Remediation outputs

- [Report and validation](REPORT.md)
- [Updated security assessment](SECURITY-ASSESSMENT.md), [machine statuses](REMEDIATION-STATUS.json)
- [Full source reconciliation](RECONCILIATION.md), [machine delta](final-source-reconciliation.json), [before-to-final patch](SOURCE.patch)
- [Fresh results](RESULTS.json), [reproduction](REPRODUCE.md), [run manifests](runs)
- [Exact source identity](SOURCE-IDENTITY.json), [hashes](SOURCE.sha256), [manifest](final-2-manifest.json)
- [Original audit read/verification inventory](audit-input-inventory.json), [related-review pin check](related-review-pin-check.json)
- [Build-context review](build-context-review.json), [fixture adaptation](fixture-manifest.json)
- [Source stability](SOURCE-STABILITY.json), [final validation](VALIDATION.json), [artifact index](artifact-index.json)

The comprehensive audit, completed Sprint6 packet and their sealed evidence remain unchanged. Application source edits and the append-only project loop log are intentional outputs of this remediation. Production, real executor and infrastructure qualification remain excluded.
""")
print(json.dumps(dict(final_cases=total, integrated_groups=4, source_files=len(files), source_delta=len(rows))))
