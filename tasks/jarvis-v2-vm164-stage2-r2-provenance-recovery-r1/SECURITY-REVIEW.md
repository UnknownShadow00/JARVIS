# Security review of provenance recovery

Scope: workspace-write profile for isolated Git recovery, local Python replay and report artifacts. The available environment has broader permissions; all activity was restricted to local repository/worktree operations and synthetic fixtures. No network, Proxmox, NSS query, credentials, package installation, VM, guest, systemd activation, host account, deployment or Gate 6K action occurred.

Expected source digests came from the previously pinned independent audit inventory. File sets, regular-file type, symlink-free R2 ancestry, bytes, size and current executable bits were checked before copying, in the index, and after commit. Both physical R2 copies matched. Only 94 explicit paths were staged. Hooks and commit signing were disabled per-command to avoid arbitrary hook execution or credential/provider interaction; shared configuration was not changed.

The baseline inherits the verified existing parent. Its canonical application files are untouched. The old worktree, six historical canonical packets and preexisting task-log entries remain intact. Recovery adds a new isolated branch/worktree/commit, separate report folder and the required task-log append. No reset, stash, clean, merge, push or deletion of existing user work was used.

Subprocesses used for recovery are local Git or isolated Python with explicit tool deadlines. Test subprocesses, sockets, NSS functions and signaling are blocked by the reviewed harness. The implementation's inert host command strings are never executed. The new wrapper requires committed test source identity and blocks canonical-source fallback. Its first failed guard attempt is retained; no source/test assertions were weakened to make the baseline match.

R2 itself remains rejected. This recovery preserves known unsafe predicates and historical reports verbatim. Retained historical PASS labels are not current safety approval. Sixteen independent defects still fail, and the approved outcome here is only reproducible source provenance for R3 engineering.

Limitations: historical mode/owner custody was not independently recorded; current non-executable modes were cross-checked and preserved. Git normalizes regular modes to 100644. Local hashes and an unsigned commit establish content equality, not independently protected external custody. Older absolute evidence symlinks are preserved as literal Git data only, never treated as trusted source paths or installation instructions. Python here is the local test interpreter, not verification of the reported host Python/systemd versions.

No unresolved material source-hash or dependency blocker remains. Host qualification and human authorization remain separate unmet requirements.
