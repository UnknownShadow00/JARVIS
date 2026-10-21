# Evidence manifest and verification

SHA256SUMS contains SHA-256 entries for every regular file in this packet except SHA256SUMS itself. Its SHA-256 is the evidence seal, stored in ../p7-b2-gate6g-release-hardening.seal and reported in the final response. The seal is an integrity checksum, not a signed operator authorization.

Verify from this directory:
```
sha256sum -c SHA256SUMS
sha256sum SHA256SUMS
```

Evidence includes historical task/entry reconciliation; read-only production entry/intermediate/final and nonmutation comparison; Gate 6F source/seal preservation; valid terminal-archive/live logical equality; final candidate source/full manifests, review patch and identity; exact input-source checks and full logs/counters for all six isolated runs; static and dependency checks; this task's loop-log entry copy. Canonical candidate and qualification-harness files live in the separate versioned isolated source archive on both hosts, covered by the source/full manifests.

The five Python qualification harness files are byte-identical to Gate 6F. The task-specific launch/collection tools reject writes to an already sealed packet. Source and evidence directories are same-UID archives, not immutable storage. A future revision must use a new versioned candidate/evidence packet; do not overwrite this one.
