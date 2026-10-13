# Operator authority: workflow, OS, cryptography and durability

| Question | Current evidence and required release answer |
|---|---|
| What prevents Codex producing a valid production permit? | Current V2 has no opening interface; candidate factory refuses. Candidate dummy verifier/peer injection cannot distinguish Codex from a human. Future external user-presence signer and protected service/helper required |
| Can normal jarvis open admissions? | Not in unchanged V2. In an isolated runtime the same UID can supply verifier/peer values or replace code/state; filesystem0700 is not human separation |
| Service privileges | Proposed dedicated non-login unprivileged UID; read protected release/public verification material and private runtime API credential; write only enumerated V3 data/receipt/checkpoint roots; no sudo, root signing key, unit management or lineage-root rewrite |
| Human privileges | Independently authenticated operator action through fixed protected helper, hardware-backed user-presence key or equally approved boundary; provisioning/retirement needs separately authorized administration |
| Replay | Persisted unique control nonces and permits, exact request/session/transport binding and short expiry; opening state refuses repetition. Same-UID DB rollback remains unprotected without independent high-water authority |
| Substitute epoch/PID/runtime | Exact fixture Bindings equality tested for every field. No fresh kernel PID/start/boot/invocation attestation or helper service-peer verification implemented |
| Malformed permit | Strict canonical JSON, finite values, bounded signature, exact payload keys; typed peer parser hardened. Store acceptance remains atomic; malformed request never partly consumes permit |
| Survive restart | Durable spend remains; Runtime starts recovery hold/terminal, sessions not restored. An old unspent permit cannot open the new Runtime. No approved resume path |
| Restart opens admissions? | No. Live V2 rejects epoch reuse; candidate never derives opening permission from stored audit |
| Helper arbitrary command/file abuse | No real helper exists. Proposed schema accepts no paths/URLs/commands. Future helper must use fixed manifests/dirfds and no shell/dynamic module/user path; cannot claim it reviewed before implementation |

Recommended operator action binds exact manifest hash including all source/config/unit/dependency/provider/profile/lineage/Gate5 evidence, action, expected accepted ordinal/high-water, exact kernel/runtime identity, challenge and expiry. Current Bindings covers only selected strings; named resources, unit/dependency inventory, lineage authority, expected ordinal and renewed Gate5 are not independently authenticated by that object. A signed arbitrary label is not a verified deployment.

Workflow restrictions, Unix privilege separation, cryptographic attribution and durable anti-replay are separate properties. Do not replace one with another. Root/kernel/hypervisor and protected interpreter/dependencies remain trusted. No OS users, sudo policy, root services, real keys or credential files were created. Actual separate-UID adversarial testing, protected parent/dirfd TOCTOU testing, credential loader tests with dummy files and supervisor identity tests require an approved disposable privilege environment. Passing current single-UID fixtures supplies none of those claims.
