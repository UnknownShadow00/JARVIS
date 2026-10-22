# Findings and fixes

| ID | Severity / violated property | Reproduction and repair |
|---|---|---|
| J1 | High: direct dispatch bypassed protected SEND | Two pre-fix failures in redteam-before. Bind native seam to same authority client; atomically consume one DISPATCH for exact pending association. Replay, mismatch, race and crash regressions pass. |
| J2 | High: delegated socket writer retained connector identity | delegated-before actual second-PID write accepted. Add Linux per-message credentials, retaining signature and process-pin checks. |
| J3 | High: misleading terminal completion | terminal-before protected acceptance with no D09 join produced local COMPLETE. Read/reconcile protected status and downgrade on mismatch/unavailability. |
| J4 | High in future privileged runner: inherited operator pipes | Unprivileged fork negative control inherits unrelated descriptors. Spawn fresh role interpreters; positive exclusion test uses a real child process. |
| J5 | High in future privileged runner: lower-privilege pickle input | Negative control selects an executable callable through Connection.recv. Replace with bounded JSON, fixed types, explicit tag allowlist and whole-transfer deadlines; malicious pickle/tag and partial-frame tests refuse. |
| J6 | Medium: privileged snapshot reads unbounded/repeated | Source inspection showed Path.read_bytes before/after digest checks. Capture bounded bytes once, no-follow every component, verify owner/mode/link/inode changes, validate schema before queries, cap SQLite work. FIFO/size/link/capture/budget regressions pass. |
| J7 | Medium: protected envelope allowed an extra second-turn classifier | Protected SEND role policy originally allowed router for every ordinal. Root now enforces ordinal2 omission and total11; dedicated attack refuses. Existing runtime semantics already omitted this call. |
| J8 | Runner correctness: overbroad denial classification and incomplete failure records | Only PermissionError counts as DAC denial. Missing path errors fail. Suite timeout now900 seconds with retained FAIL report/log, replacing180 seconds and lost timeout evidence. Source/VM/environment/dependency preflight and report sealing are explicit. |

Fixes are confined to the new candidate. No production app module changed. evidence/gate6i-to-gate6j.patch and evidence/source preserve exact reviewable changes. Runtime bugs have failing pre-fix artifacts; runner inheritance/pickle use explicit negative controls. Snapshot and operation-budget findings arose from source inspection and have targeted adversarial regression tests; they are not falsely described as captured pre-fix end-to-end exploits.

An intermediate import-path defect introduced while separating runner modules failed one focused test; fixed package-relative import setup, retained failure and reran. An initial manifest positive fixture was legitimately rejected for group-writable NEW Gate6J directories; only those isolated directories were tightened, never production or historical trees. Dependency capture initially selected duplicate system metadata versions; corrected to effective import-precedence versions and verified all127 pins.
