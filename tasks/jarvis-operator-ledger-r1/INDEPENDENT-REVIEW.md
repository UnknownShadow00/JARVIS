# Independent source review

Reviewer: `/root/recovery_review`, separate reviewer-role agent. Read-only static
review plus retained run/evidence spot-checks; no source/evidence changes and no
independent runtime or live security qualification. The eight final application
hashes are pinned in INDEPENDENT-REVIEW.json and match both final test runs.

Final verdict: PASS, no unresolved HIGH correctness/security findings. The
reviewer checked the final lexical-path/symlink hardening delta and final194/51
pass records. An initial private_directory indentation concern was retracted
by the reviewer after confirming target-only ownership checks.

Closed findings and implemented changes:

- Durable SQLite ordering alone was not tamper/rollback proof: added separately
  protected chained full-state HMAC checkpoints; no public-key signature claim.
- Exact schema probe could self-block new tables: used existing records kinds,
  retained schema version1, and refused implicit enrollment of old real stores.
- Async/rotating JSONL audit could not establish continuity: authoritative action
  receipts/events commit in SQLite and are covered by the protected state digest.
- Owner takeover and every mutation must be covered: verify before ownership
  changes; intent before COMMIT, final checkpoint before acknowledgement. Replays
  do not advance anchors. Added genesis prior-state anchor and pending resolution.
- Hard-link publication had a two-link crash window: replaced with Linux atomic
  no-replace rename, file/parent fsync, strict files and bounded staging inventory.
- Signed malformed metadata could raise raw shape errors: strict manifest,
  checkpoint, row order, event, field and identity validation now rejects it.
- Missing receipt/occurrence relationships were invisible: bounded diagnostic
  summaries expose receipt presence/state/hash/audit, occurrence bindings, owner
  generation and scheduler control, with conservative completion explanations.
- Recovery could trust result metadata too broadly: both automatic and local
  publication revalidate exact bounded pure output and synthetic terminal states.
- Global metadata could cross caller scope: operator diagnostics require the
  exact trusted local-service namespace and configured bearer authentication.
- Expired export permit could strand audit publication: preserve durable original
  authorization, keep idempotency payload stable, and support audit-only same-ID
  reconciliation of a complete anchored snapshot without regeneration.
- Archive preview could be incomplete or stale: hold one owner mutex, include
  totals/cutoff/decision hash/checkpoint, refuse >200 eligible tasks, and require
  exact task-record coverage in the verified exported snapshot.
- Schedule bulk cancellation rewrote terminal history: filter active/unresolved
  tasks; completed records remain unchanged. Tested normal and operator paths.
- Export storage could grow indefinitely: dedicated root,16-directory/64MiB caps,
  free-space refusal and incomplete-export accounting, with no cleanup/deletion.
- Lexical `..` could defeat tree separation; mkdir preceded symlink validation:
  reject traversal and symlinks before creation and test no child is created.

Accepted remaining limits:

- First schema DDL to first genesis intent crash is fail-closed/manual quarantine.
- Same-UID key compromise, check/create races or coordinated DB+anchor rollback
  are outside the local trust model; no hardware counter, key rotation or
  multi-host consensus is provided.
- Finite checkpoint/export/selection bounds require operator capacity planning;
  no protected deletion or automatic cleanup is implemented.
- Real activation needs external key/FD provisioning, private OS-separated paths,
  Linux renameat2 support, disk monitoring, recovery drills and approved policy.
- The two upstream Starlette/AnyIO warnings cannot be safely fixed within the
  retained verified dependency closure. They remain visible, not suppressed.
