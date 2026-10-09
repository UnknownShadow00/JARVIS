# Gate 3 — production D06/storage/backup readiness, NOT APPROVED

Gate2C placed the private drop-in on disk only. Service remains stopped/inactive, mode LEGACY, credential verified solely by metadata, manager not reloaded. These are readiness observations, not authorization for provision, service operations, SHADOW or requests.

The next specific operator decision is explicit Gate3 authorization for the unchanged [D06-DEPLOYMENT-PROVISIONING.md](../p7-b2-supervised-deployment-staging/D06-DEPLOYMENT-PROVISIONING.md) and storage/backup readiness, with all participating lifecycle/generation callers quiescent. Existing or unexpected/partial/remote-unknown state requires review, never automatic repair or overwrite.

Required future checks/work, only within a separately approved scope:

1. Reverify actual legacy endpoint exclusion and the pinned resource ollama/http://192.168.0.200:11434/hermes-candidate-granite41-30b-q3km-64k; native profile jarvis.p7.ollama.granite41.b1r2.v1/context64000. Do not infer remote terminal/completion from PID, restart, GPU, expiry or idle model observations. No generation/load/unload request is granted.
2. Reverify Core disk/inode capacity, uid/gid, symlinks, ACLs, private storage/backup roots and absence of unexpected production state. Actual D06 state remains absent at this boundary.
3. If specifically authorized with callers quiescent, provision /home/jarvis/JARVIS/data/model-ownership-v1 and adjacent managed guard using the reviewed API, preserving exclusive marker/state creation and legacy exclusion. Verify directory0700, files0600, pinned scope/digest/schema and current=None. Do not open a D09 controller/pilot epoch or create D04 records as part of readiness.
4. Verify existing Core-local Option A baseline seals and create a NEW secret-free configuration/source/unit/D06 readiness baseline reflecting the authorized changes. Do not read or copy either environment file; exclude credential content/hash and any runtime environment. Preserve all existing evidence and the pilot-only host-loss acceptance. No backup job/prune/automation change.
5. Keep Gate4 activation, Gate5 zero-generation deployed checks and Gate6 traffic separate. Any systemd manager reload, LEGACY start/auth-verification window or other service action must be explicitly named and separately authorized; Gate3 storage/provision approval does not imply those actions.

No item above was executed in this Gate2C task. Gate3 remains unapproved. Preserve the stopped-only restore contract and newer evidence before any separately authorized rollback.
