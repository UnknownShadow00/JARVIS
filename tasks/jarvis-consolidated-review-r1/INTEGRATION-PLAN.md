# Proposed next isolated dependency/integration unit — not executed

The current interpreter reports Python3.14.4 but cannot discover FastAPI,
Pydantic, pytest or APScheduler. This is a **technical environment gap**, not a
general requirement for a human to approve routine offline Nexus engineering.
This consolidation task permits documentation/evidence only, so it creates no
environment, installs nothing and imports no inspected payload. A subsequent
bounded offline engineering unit can take up this plan within its stated scope;
it does not require PVE/guest permissions or protected system installation.

## Exact candidate inputs

`INTEGRATION-INPUTS.json` pins public source records, the complete127-version
historical lock and12 critical version/artifact identities. The public Gate6L
record is9cfd2ed635f347521164b4d99ecf1cc82396036ab52e8c377386181dabf3b837;
the version lock isb07d5613eb50547b99229b2230bf90bd9d884dfcc869ecc025ffb003449d680a.
These are retained candidate inputs, not a compatibility conclusion or a new
publisher attestation.

Critical versions include APScheduler3.11.3, FastAPI0.141.1, Starlette1.6.0,
Pydantic2.13.5/pydantic_core2.46.5, pydantic-settings2.15.0, pytest9.1.1,
pytest-asyncio1.4.0 and httpx0.28.1. Every listed artifact's exact hash is in the
JSON. The12-entry subset is **not an installable transitive lock**. Before executing
anything, select the minimal compatible wheel closure from existing public
artifacts, validate METADATA/tags/hashes as data, and emit a full hash-required
lock for that closure. Reject unresolved dependencies, source builds or implicit
downloads. Do not blindly install the127-distribution mixed Ubuntu inventory into
Nexus; its OS packages and historical runtime assumptions need separate treatment.

Bind the actual interpreter executable, ABI/OS/native-library identity and selected
source hashes. Matching Python version text does not establish the Gate6K runtime
or certify that its wheels work with the current source. Keep its historical
signature/integrity distinctions; byte matching adds no publisher signature.

## Storage and side-effect bounds for the future unit

- Use one new task-local directory and a private environment/source/fixture copy;
  no global/site/user installation, existing environment modification, shared
  mount/cache/tmp-policy change or default runtime/data reuse. Keep the verified
  public bundle read-only; do not duplicate its3GB archive.
- Proposed maximum:2GiB total new extracted/environment/fixture bytes,100000
  files,1GiB child address space, two test children and a20-minute overall limit.
  Calculate archive expansion and closure size first; stop if these bounds cannot
  accommodate it rather than silently raising them. Preserve receipts on failure;
  deleting old evidence is not part of this plan.
- Deny external network and real data/credential filesystem access **before** any
  dependency/application import. Use a verified unprivileged child sandbox and a
  reviewed read-only allowlist for interpreter/dependencies/public fixture source,
  with writes confined to new fixture/state/log paths. Close inherited handles
  and remove credential-bearing inherited environment values. Do not repurpose
  HOME or change account, mount or global process policies.
- A Python audit hook, mocks or an alternate working directory alone do not prove
  OS isolation. If the existing host cannot supply a suitably bounded unprivileged
  child environment, retain source-level tests and record that technical blocker;
  do not import the full app into the current account's real configuration/data
  namespace or improvise privileged setup.

## Narrow integration before full application startup

First exercise real FastAPI/Pydantic/ASGI response behavior around the selected
task/schedule handlers mounted in a fixture-only application. Then exercise real
APScheduler registration/parser/callback lifecycle with deterministic fixture
jobs and bounded in-process callbacks. These should enqueue only synthetic task
records, never execute tools, shell commands, providers or models. Mark these as
new framework tests rather than reclassifying the earlier AST/inert-backend suite.

Full app.server import/lifespan is a later scope: statically enumerate its
constructors, audit thread, resource callbacks, config/env readers and optional
provider modules first. Supply fixture-only config/paths before the first import,
disable hardware/voice/providers and prove the child filesystem/network deny
controls. No production runtime data, secrets, VM163 state or private guest image
is copied. A failed guard prevents importing the payload rather than becoming a
manual-copy/install workaround.

Expected evidence: new exact source/interpreter/lock/artifact/sandbox identities,
dependency consistency, protected-path/network denial results, real ASGI failure
responses and scheduler lifecycle behavior, fixture-only filesystem inventories,
and actual bounds/exit status. No live isolation, PVE, guest or Gate6K privileged
qualification is inferred.

## Authorization boundaries remain separate

Routine offline planning and source engineering remain authorized. Installation
and imports are simply outside this consolidation-only unit; no new approval is
requested here. Broker protected system installation, restricted executor setup,
credential issuance, PVE VM164 grants, trusted guest bootstrap/changes, live
activation and privileged Gate6K qualification remain specifically pending under
the existing staged approval packet. This proposal authorizes none of them.
