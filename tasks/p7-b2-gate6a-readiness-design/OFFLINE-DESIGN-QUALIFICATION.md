# Isolated design qualification

Two distinct fresh checks passed; neither demonstrates deployed opening capability.

## Abstract candidate model

Isolation: `/tmp/jarvis-gate6a-design-s1tea4uf/` on nexus-services. The model and tests are outside the canonical application and its normal import paths. No production checkout/worktree was modified. The evidence copy is under the separate .hermes-poc evidence root, not app/ or a production plugin path. The task packet carries only the patch as a non-importable review artifact.

Candidate patch SHA256: **6a27801a05a0503ffb007be00173eb01b931dfc3a752e3c7cfa704c67ecc2565**.

Model source SHA256: **56f1464fa32568e6b79e0522a72d3b5f50a36fa6c6581a42a226053e405484d9**. No candidate commit, merge or deployment exists. candidate-manifest.json records every model/test/runner hash.

Final result: **55 unittest tests passed, 0 failures/errors**, plus **625 bounded four-event sequences** checked for monotonic accepted count, cap and zero tool/legacy dispatch. Python3.14.4/SQLite3.46.1; final measured run0.1048s. SQLite state is disposable in-memory fixtures. Test peers/operator/API authorization are dummy facts, never the production credential. Guards recorded **0 network, 0 production/credential opens, 0 external writes and 0 process execution**.

Coverage includes fresh CLOSED/no acceptance; valid explicit opening without transmission; initial-zero prerequisite; wrong epoch/source/config/PID/invocation/boot/start tick/runtime nonce/resource/profile/checkpoint/contract/Gate5/predecessor; missing/wrong operator authority, same-UID agent/untrusted peer, expiry/repeat/replay; cap/two-per-transport; D06 active/unknown and endpoint conflict; invalid backup/control; rechecks before admission; partial transaction rollback and post-commit crash; concurrent REST/WS, wrong API credential/session/scope, voice/direct refusal; proposal/receipt/backup failure; irreversible stop; missing/corrupt database/control; restart hold and separately authorized hypothetical recovery preserving count/quota/origin/eligibility; predecessor acceptance refusal and no same-ID relabeling. No actual provider terminal is fabricated; D06 fixture state is supplied independently of D09.

Limitations: this is a **state-machine design model**, not a production opener. It does not implement real SO_PEERCRED/PAM/FIDO/signatures, protected identities, durable filesystem/fsync failure behavior, actual V3 schema migration/backup manifests, real REST/WS session/history protocol, PID/socket TOCTOU defenses or production driver-only routing. The model's dummy authority flag is not an accepted implementation technique. Fake transmission counters are not provider calls; zero legacy/tool counters prove only the modeled separation. These require new implementation/security/integration qualification before deployment. Crash injection covers SQLite transaction/memory boundaries, not hardware power-loss guarantees.

## Existing canonical-source focused suite

Fresh isolated copy on Core: `/tmp/p7-b2-gate4i2-offline-y3v9ss3p/repo`. The reviewed runner excludes runtime data/logs/.env, uses the committed baseline config for legacy-compatible tests and private explicit PILOT fixtures with fake transports. No human authentication utility/test was run.

Selected suites: test_model_ownership; shadow_pilot_safety_test; shadow_pilot_test; shadow_controller_test; shadow_pilot_backup_test; shadow_backup_recovery_test. **357 passed, 0 failed, 2 existing deprecation warnings, 2.26s**. Guards recorded0 INET/DNS, credential, production-runtime, external-write or unapproved-execution attempts; three approved fixture subprocesses. Copied-source/config manifests and exact output are sealed.

Ten source-analysis copies additionally match both the current canonical hashes and the Gate4 installed implementation inventory. Findings include current epoch/restart refusal, terminal shutdown, missing opener and legacy sidecar ingress incompatibility. Historical full7166/11deselected/0fail and Golden12/20 remain historical; no model-capable digest was regenerated and no dependency installed.

Future implementation must replace the model with tests of actual authorization/credential boundaries, pure pilot routing, transaction/permit joins, schema migration, backup coordination, restart reconstruction, tool/voice isolation and 30s drain. Offline passes do not authorize production implementation or pilot execution.
