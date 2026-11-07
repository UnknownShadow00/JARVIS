# Independent security and correctness review

Separate reviewer: `/root/audit_review`. Scope: read-only/static implementation
review and retained output spot checks. The primary executed guarded runtime
checks; the reviewer did not perform independent live/privileged qualification,
network access, real config/state/key access or app imports outside the cage.

**Final verdict: PASS, no unresolved scoped blocking findings.** Exact seven
module hashes, run identities and accepted limitations are in
[INDEPENDENT-REVIEW.json](INDEPENDENT-REVIEW.json).

1. **HIGH, CLOSED — Implicit creation and schema-shaped legacy bypass.** Normal opening refuses absent/zero/schema-only; no O_CREAT/DDL; enrolled state needs guard/witness; unmarked state requires explicit exact-state/path/head trusted-local compatibility capability.

2. **MEDIUM, CLOSED — Missing physical genesis/no-follow binding.** Bounded no-follow reads, physical hash whenever logical state remains genesis, identity/postread checks and exact original enrollment record/receipt checks.

3. **MEDIUM, CLOSED — Branch verify/reopen race and identity collision.** Expected full-byte hash and before/after inode/byte validation plus original-request collision refusal; negative/read-only/race tests.

4. **HIGH, CLOSED — Owner metadata rejected by consistency validator.** Strict VERIFIED/LEGACY_APPROVED schemas with historical four-field compatibility; repeated focused/core/app validation.

5. **MEDIUM, CLOSED — Legacy empty-head binding and sequence-based physical binding.** Guarded compatibility binds current protected head; genesis physical binding follows logical seed equality rather than sequence.

6. **LOW, CLOSED — Malformed Actor and UUID domains.** Exact Actor validation and distinct enrollment/store/trust; branch identities cannot equal store/restore/original operation IDs.

Final evidence spot checks confirm254 core +59 focused +58 app =371 unique
pytest cases, all passed with0 failures/skips;13 app scenarios,3 native probes
and7 benchmark cases passed. All four final runs bind identical99 application
source hashes. Intermediate failing inputs/results are preserved and accurately
explained in REPORT.md. The demo preserves UNKNOWN/cancellation uncertainty and
keeps real execution and restored branch activation false.

The reviewer specifically accepted the documented caller-rooted compatibility
boundary: a local caller can instantiate its own verifier, so the grant is an
explicit trusted embedding capability and cannot authenticate historical provenance
independently. No default capability/key issuance exists. External reservation,
post-enrollment witness, later checkpoint minimum, trusted registry and secure time
must have independent custody for the corresponding rollback/freshness claims.

No real enrollment/re-anchoring, real executor/provider, VM/Proxmox action, physical
power-loss guarantee or general production readiness is claimed. A future branch
registry/decision ceremony must remain separately authorized before activation.
