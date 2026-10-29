# Timeline investigation evidence

This packet extends, and does not rewrite, `p7-b2-gate6k-vm164-r4-investigation`. Its 43 prior packet members and manifest seal were reverified unchanged. The earlier root-cause report remains historical; this update makes an earlier installation followed by installer re-entry the leading explanation and recommends read-only completion checks before any replacement decision.

| File | Provenance / scope |
|---|---|
| `ASSESSMENT.md` | Timeline, evidence/inference separation, source analysis and revised disposition |
| `READ-ONLY-PLAN.md` | Exact proposed operator queries and static completion/boot checks; no live execution |
| `evidence/operator-timeline.json` | New user-supplied trusted evidence; no raw task logs/headers independently acquired |
| `evidence/shutdown-controller.py` | Exact source extracted with `unsquashfs -cat` from retained hash-verified Subiquity 7403 snap; not imported/executed |
| `evidence/input-provenance.json` | Snap/source hashes and prior packet identity; existing source references for install flow, r4 guard/config and late guard |
| `evidence/verification.json` | Local plan/source validation, previous-packet preservation checks, scope limits and public reference URLs |

Snap SHA256: `ee9467fec724cf2a7f4fc61641a4a05d84f7730f06b8fefaceaf0b51a9a0331b`.

Current report relies on user-supplied filesystem creation/last-write and host mtime/ctime values. It contains no raw disk image, filesystem readout, prior-boot journal, host task UPID/exit log, current RAM capture or observed target boot. No installation success or orderly shutdown is asserted. Public documentation verifies query semantics only; exact retained installer source establishes its code ordering, not live execution.

`SHA256SUMS` covers all packet files except itself. The adjacent `.seal` records its SHA256; this is an integrity digest, not a signed witness. The completion entry is appended separately to `tasks/loop-log.md`. No prior seal or report is edited.

Verify from the project root:

```bash
sha256sum -c tasks/p7-b2-gate6k-vm164-installation-timeline.seal
(
    cd tasks/p7-b2-gate6k-vm164-installation-timeline
    sha256sum -c SHA256SUMS
)
```
