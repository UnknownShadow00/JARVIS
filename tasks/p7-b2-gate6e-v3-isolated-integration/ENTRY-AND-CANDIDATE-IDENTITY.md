# Entry and candidate identity

Nonproduction Gate 6E reference implementation. No production installation, experiment approval, model traffic, credential use or measurement. G6D-LP-1 remains a proposal.

Gate6D evidence seal `9782bace6fbd697cd823e2ba125f8c3b26e4d48de83aa21d93113f60a40c958d`: 112 members verified. Its 581-file full source/qualification inventory verified before copying. All four mandatory Gate6D document hashes match the operator pins, locally and on Core. Fifteen earlier evidence seals and 65 authority documents reverified; their accepted decisions remain unchanged.

Original Gate6C identity `0d81f9fd49217ac0ac672aeefd1abb0190071c93da291a0ad92947636f8e738c` and Gate6D identity `fbc53bd51a3d9968484275443817ef2e8eb41c853748c24a2b371ab4dc899ad1` are SHA256 digests of source/qualification manifests, **not Git commits**. Original archives remain under `/home/jarvis/.hermes-poc/gate6d-candidates/`.

Gate6E artifact: `/home/jarvis/.hermes-poc/gate6e-candidates/engineering-r2/repo`.
Source/qualification manifest digest: `c28942a9d7254376117bfd58cc0fa6549112a84f1be6a60752ef75c00442567b`. See evidence CANDIDATE-SOURCE-SHA256SUMS, FULL-SOURCE-SHA256SUMS and candidate-vs-gate6d.patch. Review documentation is separate from source. No Git commit or push created.

Production: HEAD `bd53dbc799fb9284a21fae8cce3f5d9539e31141`, config `00d7b460932a9434d947cf3a08d7bfbe5d5c4b15ce06a57d53779d0f7bf4350c`, user-service PID594042, invocation103e420f4f334237a96654048a3edaf4, epoch606a991a06b74fd79ed72b308417cc3f. Entry has no drift: SHADOW, admissions closed, zero durable attempts/submissions/receipts, D06 empty, Restart=no, restarts0, disabled autostart. Epoch OPEN is bookkeeping, not admissions.

Candidate files are private same-UID storage outside live working directory/import paths, with no symlinks or credential/runtime-store inclusion. No immutable or privileged-tamper-resistant claim. Qualification uses copied source, read-only venv packages, isolated HOME, Landlock and seccomp; production data and credentials are inaccessible. System/venv libraries are deliberate read-only external dependencies. Direct live process environment was never inspected.
