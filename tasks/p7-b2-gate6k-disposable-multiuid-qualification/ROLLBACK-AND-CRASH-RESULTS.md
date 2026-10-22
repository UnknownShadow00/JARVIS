# Rollback and crash evidence

Existing isolated tests exercise controller/accepted-attempt/D09, D04/checkpoint, old backup, source/config identity, missing/corrupt root and whole service-writable-tree rollback against retained authority. They refuse disagreement and do not automatically recreate/restore authority. Real child-process interruptions before/after durable transactions preserve consumed nonces, acceptance and possible-send uncertainty. Full results are recorded in TEST-RESULTS.md.

The negative control test_complete_authority_rollback_still_possible_to_owner deliberately succeeds in restoring an old protected checkpoint when the authority owner rolls back its whole state. Its test PASS confirms this limitation, not a defense against host rollback. Protection depends on the independently retained authority being outside the application's writable domain. Arbitrary root, hypervisor or complete host rollback is not defeated; no external witness was added.

New extraction interruption tests preserve the private partial destination and refuse reuse. Interrupted runner preparation now produces and seals FAIL evidence when a fresh fixture already exists; preflight refusal is BLOCKED with no fixture write. Old evidence is never reset or overwritten by retry.

Actual distinct-UID crash, helper process restart and rollback qualification: NOT RUN. No VM power cut, snapshot rollback or production process interruption occurred. Future runner journal reopen is not relabeled as a new helper process; that distinction remains in the execution matrix.
