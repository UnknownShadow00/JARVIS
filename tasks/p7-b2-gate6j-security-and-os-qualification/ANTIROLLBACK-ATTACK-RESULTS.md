# Rollback outcomes

The full applicable suite retains Gate6G/6H/6I rollback cases: controller/accepted rows, older checkpoint/backup, signed root/commitment substitution, source/config/process identity drift, missing/corrupt authority and all service-writable directories replaced together. Protected history retains accepted ordinal/claim/send associations and rejects disagreement; backups never initialize or restore authority.

Protected ControllerReader checks exact schema, signed claims, permit associations, accepted IDs and every protected SEND. CHECKPOINT requires a current authority sequence/seal plus coordinated D04/D09/D06 joins. New snapshot handling captures each file once with bounded no-follow component-by-component opens. It rejects FIFO, hardlink, symlink parent and oversized data; untrusted SQLite evaluation has a finite VM-instruction budget. This addresses denial-of-service and inconsistent repeated reads without claiming a coherent cross-file live snapshot when the service races changes: inconsistent data must refuse.

The negative control test_complete_authority_rollback_still_possible_to_owner is deliberately retained and run. Replacing the authority owner's complete checkpoint can restore old valid-looking history. Its test PASS means the attack succeeds as expected, not that host rollback is defeated.

Security depends on a genuinely protected authoritative state remaining outside service write control. Same-host authority does not independently resist root, physical-host or hypervisor rollback. Additional hashes cannot fix that boundary. Stronger guarantees need a separately trusted anchor and reviewed recovery protocol; none was implemented or contacted.
