# Independent source and evidence review

Reviewer: separate `/root/audit_review` agent. Scope: read-only source review,
security/correctness reasoning and spot checks of final guarded test/benchmark
outputs. Runtime tests were executed by the primary, not independently by the
reviewer. No real configuration/state/credential access, external network,
application imports outside the cage or privileged qualification.

Final verdict: **PASS; no unresolved scoped correctness/security finding**.
[INDEPENDENT-REVIEW.json](INDEPENDENT-REVIEW.json) binds all ten final module hashes
and accepted limitations. Earlier comments drove the following implementation
fixes, which were followed by focused and broad validation:

1. **HIGH, CLOSED — Standalone archive could not prove audited export completion.** Protected post-completion attestation binds manifest, snapshot, completion receipt and publication checkpoint; later SQL marker binds attestation.

2. **HIGH, CLOSED — Rollover required authenticated continuity, not local head selection.** Retained generations, global sequence, previous transition/head/policy/key bindings, exact inventory and external expected-ancestor reference.

3. **MEDIUM, CLOSED — Reference head not constrained to declared generation.** Epoch range, rollover hash and head ancestry now checked; wrong generation/rollback/key/expiry tests.

4. **HIGH, CLOSED — Shallow restore phase checks could misreport missing prepared evidence.** Exact phase groups, UUID/schema/auth, intent/prepared/final hashes, source attestation and lineage validated before reporting.

5. **HIGH, CLOSED — Restore required exact reconstruction and exclusive durable publication.** Trusted schema/no archive SQL, strict ordered types/rowids, FULL transaction, integrity/logical/semantic checks, fsync, read-only inert artifact and RENAME_NOREPLACE.

6. **MEDIUM, CLOSED — Shared live operations could race.** Shared reentrant serialization; separate CLI requires exclusive existing journal lock.

7. **HIGH, CLOSED — Admitted rollover recovery could become stuck after permit expiry.** Continue exact durable original admission without new authorization; recovery receipt hash bound to commit; independent SIGKILL test.

8. **MEDIUM, CLOSED — Missing attestations/receipts needed durable linkage.** Cross-linked phase records, source attestation markers, readiness and missing-phase negative tests.

9. **MEDIUM, CLOSED — Disaster and hostile archive coverage incomplete.** Page corruption, missing/duplicate/reordered content, HMAC/trust/policy errors, injected storage failures, paths/races,15 SIGKILL cases and UNKNOWN cancellation preservation.

10. **MEDIUM, CLOSED — Restore accepted legacy v1 despite documented lineage requirement.** Explicit v2 guard added; actual signed v1 remains inspectable but restore fails with restore_checkpoint_lineage_required.

11. **BENCHMARK, CLOSED — Initial synthetic fixture violated guarded import/admission requirements.** Fenced synthetic historical batch preserves provenance; UNKNOWN created first; migration/admission capacity unchanged.

Final observed results: core254/254; application54/54 plus11 scenarios and3 native
checks; benchmark4/4. All final runs contain97 hashes matching current app source.
The final v2-only correction and signed legacy-export negative test were rechecked
before this verdict. Shared serialization, missing-owner failure handling, reporter
receipt/artifact distinction and the no-sidecar inert activation refusal were
also reviewed. No finding was closed by weakening authorization or antirollback.

Residual trust boundaries: protected external key/reference custody and secure
time, trusted local Python/OS/same-UID context, finite retention capacity, linear
verification, no physical power-loss qualification and no runtime restored-branch
activation. A local checksum/HMAC packet is not independent privileged-attacker
antirollback protection. Live deployment/security qualification was not performed.
