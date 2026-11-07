# Bounded reproductions and negative controls

No confirmed security vulnerability is claimed. Exact saved native reproductions of six implementation defects are in IMPLEMENTATION-DEFECTS.md, with original input, condition, observed result, fix and regression invariant. Their native commands use the OS-isolated runner and new output stems to preserve retained evidence.

| Check | Saved fixture | Retained result | Result scope |
|---|---|---|---|
| Independent anonymous authority validation | agents/verify-auth/scratch/verify_auth_controls.py | agents/verify-auth/artifacts/verify_auth_controls.txt | Genuine stock lifespan refuses missing state; explicit synthetic binding permits anonymous read/cancel; configured credential and operator checks reject |
| Ancestor connection substitution | agents/parent-current/scratch/ancestor-current.py | agents/parent-current/artifacts/ancestor-current.txt | Exact same-UID swap occurred; SQLite rejected writable construction; no invented cross-UID qualification |
| Final registry hot-journal recovery | agents/parent-final/scratch/hot-journal-controls.py | agents/parent-final/artifacts/hot-journal-controls.txt | Two disposable child-interruption cases: exact authenticated recovery succeeds; foreign protected custody refuses with unchanged database/journal bytes |
| Current broker chain | agents/hunt-infra-current-chain/scratch/current_chain_controls.py | agents/hunt-infra-current-chain/artifacts/current_chain_controls.txt | Eight synthetic current-source identity/receipt/precheck/protocol controls |
| Current preissuance/files | agents/hunt-infra-current-files/scratch/current-file-controls.py | agents/hunt-infra-current-files/artifacts/current-file-controls.txt | Ten fully mocked preissuance/prompt-delay and scratch-local file/journal controls |

To replay, copy the named fixture to a new basename in the same owner's scratch directory, then call sandbox-runner.py with that owner, copied fixture path and recorded snapshot name. It refuses overwriting old output. The source/toolchain are mounted read-only; writes stay in a 32 MiB ephemeral scratch namespace. Target processes receive no external network, host home, credentials, sockets or devices. All processes terminate before bounded descriptor-confined output promotion.

Detailed runner code and exact safe environment/resource settings are retained in sandbox-runner.py and validation-summary.json. Preexisting toolchain versions are in agents/parent-final/artifacts/toolchain-inventory.txt; they are not deployment evidence. The screenshot two-UID/native-writer check was not run because its decisive dependency/runtime/principal conditions are unresolved; its safe resolution plan is in NEEDS-VALIDATION.md.
