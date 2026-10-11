# Fresh isolated qualification and limits

Canonical-source focused suite: **478 passed, zero failures, two existing deprecation warnings, 3.06seconds**. Source was copied into private Core `/tmp/p7-b2-gate4i2-offline-c1qmcwnf/repo`; the runner uses committed baseline config for legacy fixtures and explicit dummy PILOT fixtures. Production config/source/state were untouched. Selected suites cover model ownership, closed fence, pilot/controller, coordinated backup/recovery, admission/history, shadow runtime and server integration. No human authentication helper or helper test was executed.

Per-process guards recorded zero INET/DNS, production runtime/credential access, external writes and unapproved execution attempts; three approved fixture children. Existing tests use fake transports/dummy credentials. Two FastAPI/Starlette test-client deprecation warnings are preserved, not addressed by installing dependencies. Historical full regression7166passed/11deselected/zero failures and Golden12/20 with eight established failures remain historical; no full regression or model-capable digest was rerun.

## New Gate6B design model

Location `/tmp/jarvis-gate6b-review/` on nexus; source is outside canonical application/import paths. Review copies in evidence remain outside the production repository. The task packet contains only a non-importable patch and manifest, not an installed module. No candidate commit/merge/deployment exists.

**57 unittest tests passed, zero failures/errors**, approximately0.035seconds. Independent audit guard recorded zero network, production/credential opens, external writes and process execution. Patch SHA256: `585df7f6ea4e4f6977149d14af61df854b54088b2386abe9c8be54abbdbfb911`. candidate-manifest.json contains exact model/test/runner hashes. Test logs and source are sealed in evidence.

| Scenario | Fresh result and scope |
| --- | --- |
| One successor / concurrent controllers | SQLite unique parent/child reservation, two-connection concurrent reservation leaves exactly one winner |
| Partial successor creation | Before/after commit and partial initialization injections preserve PREPARED/INITIALIZED holds; no duplicate UUID or silent ready state |
| Four-attempt global cap | Four durable ordinals/two transports; synthetic ancestor rows consume cap; used V2 predecessor separately refused |
| Permits/crash | Spent permit and accepted ID atomic; partial/precommit rollback; postcommit crash retains acceptance with zero fake dispatch |
| Replay / wrong identity | Repeat opening/permit, wrong source/config/release/PID/invocation/epoch, API-token/same-UID/untrusted authority refused |
| Concurrency / ingress | Concurrent REST/WS cannot both consume one permit; voice/direct/wrong-transport refusal; no queue |
| Closed/terminal/restart | Initial CLOSED, stop/abort and restart refuse opening; spent opening commit survives restart without opening |
| V2 retirement | OPEN, incomplete, used, unknown, auth-aborted or unverified archive refused |
| D06/checkpoint/lifecycle | Active/unknown/missing checkpoint/conflict blocks opening; conflict after acceptance prevents fake dispatch; failed backup stops next permit |
| In-flight stop | Accepted count retained; remote_unknown preserved; no later Granite substep after uncertain fake legacy call |
| Legacy-visible semantics | Fake legacy reply is visible/history; fake Granite candidate absent from output/history/database; proposal from either lane stops without execution |
| Access separation | Policy-table dummy identities deny Codex/jarvis/model/client access to credentials/controller/control; service cannot write release or invoke helper |
| Actual pure legacy responder | Exact copied pure source returns None for all original four proposed inputs; numeric arithmetic control returns expected legacy formatting |

These tests do **not** prove actual OS DAC/PAM/FIDO/SO_PEERCRED enforcement, fsync hardware/power-loss durability, protected deployment/migration, true network timing, full two-lane provider integration, production legacy response equivalence, or a valid V3 D04/backup implementation. Access checks are a policy model, not real different-UID credential tests. Crash tests inject logical exceptions around actual disposable SQLite transactions, not machine power cuts. Fake replies cannot qualify authentic legacy/Granite behavior. Model concurrency tests enforce no double acceptance; the proposed production rule to terminally freeze on unexpected concurrent ingress still needs actual integration testing.

Future implementation must test those unimplemented boundaries, expiry/signature/request/session binding, all dispatch tripwires, content minimization, actual30second drain, I/O faults and crash-safe root reservation publication. Until approved legacy identities/budgets exist, no test may substitute a successful fake run for an approved experiment.
