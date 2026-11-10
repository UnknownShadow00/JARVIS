# Source-backed baseline decision

BASELINE.json records exact baseline, parent tree, worktree and branch. b738a473d has parent764097552; their only difference is tasks/loop-log.md. Common ancestor with Unified RC1 is f4cac30259a7bf4610add2063679ae49138ee637. RC1's two commits543ca9d1d/e9b473474 are on a sibling release line; reliability commits e310e5871/b199acede/b0c8865a9 descend from it. Current nightly history has not merged that line.

Design evidence (hashes in DESIGN-SOURCES.json):

- tasks/jarvis-v2-unified-rc1/INTEGRATION-MATRIX.md: lines5,51,67,71,85 and server row explicitly select the stronger semantic union, ready client, ancestry verification, WebSocket ownership and disabled resource defaults.
- tasks/jarvis-v2-unified-rc1/REPORT.md: reconciliation section states the same decisions; documents the actual whitespace-token startup mismatch and three regression tests; explicitly adds ready with12 tests and identifies actual clients/liveness consumers.
- tasks/jarvis-v2-unified-rc1/INDEPENDENT-SECURITY-REVIEW.md: reviews retained WebSocket/ancestry safeguards.
- tasks/jarvis-v2-release-readiness-r1/INDEPENDENT-REVIEW.md: records real live-but-untracked peer and precreation ancestry findings that motivated the stronger implementation.

History examination: git log --all -- app/cli.py and tests/test_ready_client.py shows the command/test introduced in543ca9d1d. The canonical nightly commit is rooted in the other line and has no readiness deprecation message. Existing readiness-report/pre-server tools are local build/dependency reports, not equivalent authenticated /ready consumers. The server's API still authenticates /ready. No evidence supports replacement or deliberate deprecation. Strict classification: a branch-integration omission (closest to A), not proof of a person's accidental action. B/C lack supporting design evidence; D is unnecessary because an explicit reviewed design already exists.

The R3 branch already contains the necessary application reconciliation as inherited RC1 bytes. We select only documented app/test/tool paths, not its task packets or sealed artifacts. Source identity comparison confirms final app/ Python bytes equal R3, while unrelated current development files remain on b738a473d. No stale canonical checkout, reset, stash, merge, rebase or branch rewrite occurred.
