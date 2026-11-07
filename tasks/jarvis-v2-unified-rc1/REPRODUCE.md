# Reproduce the merged offline candidate

Run from `/opt/apps/IT TRAINING PROJECT CODE/projects/JARVIS`. Do not start the
application, run unguarded root pytest, substitute real config/databases, install
packages or activate a provider/real executor to reproduce these results.

Read-only verification of source, exact test inputs, independent review pins,
predecessor preservation and full artifact manifest:

```sh
python3 -I -B -S tasks/jarvis-v2-unified-rc1/verify_release.py --check-working-source
```

`--archive-only` verifies every source archive member, metadata, embedded identity
and byte-identical deterministic rebuild without requiring historical dependencies
or task evidence. Copy BUILD.json, SOURCE-SHA256.json and requirements-offline.lock
alongside the archive in their recorded relative layout. This is a source archive,
not a self-contained installed environment or signed OS image.

Replay all ten main modes and seven selected/security/configuration groups in a
**new exclusive task packet**, leaving this packet unchanged:

```sh
python3 -I -B -S tasks/jarvis-v2-unified-rc1/replay.py
```

The replay verifies the clean committed worktree and all315 public hashes first,
then copies only harnesses, public source view, fixture inputs and metadata into a
new timestamped sibling under canonical JARVIS/tasks. No real config/credential,
sealed predecessor tree or runtime database is copied into the test cage. Main
modes and selected groups run sequentially; no resource limit is increased.
Every main mode gets a new timestamped run/input/output/manifest; every selected
artifact uses exclusive creation. Stop on a failing guard or preflight and retain
its evidence; do not relabel it as a passing run.

Required existing local prerequisites: hash-qualified bwrap and Python3.14;
`tasks/jarvis-fixture-integration-r1` guard/provenance; exact28 target at
`tasks/jarvis-authority-readiness-r1/runs/20261031T090522534346Z/output/site-packages`;
the predecessor release packet's three RECORD-verified optional wheels/target;
and the pre-existing selected-test environment at
`/home/nexus/.local/share/jarvis-gate6l-offline/bundle-r1/work/mixed-env-r2/lib/python3.14/site-packages`.
The latter is pinned by SECURITY-DEPENDENCY-SHA256.json and verified before/after
every final selected replay. A different host needs these exact public retained
artifacts and supported namespace/native-library semantics. Missing prerequisites
block replay; do not fetch/install/substitute them silently.

The current failure history remains in runs and invocation logs: close-code test
union corrections and a pre-test instrumentation hook failure. Final accepted
runs are explicitly selected in RESULTS.json. Security-selected179 and full-app103
are subsets of the1,023 unique passed tests; four replayed integrated groups are
not added to the20 main application groups. The original168/998 totals are history.

Fresh advisory tools are not required for this source replay to claim an advisory
PASS: no such PASS is claimed. pip_audit absence and npm memory refusal are retained
as deployment blockers in DEPENDENCY-CONFIGURATION.json. No limit was relaxed.
Hardware/desktop exclusions, live assumptions and VM164/Gate6K approval requirements
remain exactly as reported. Canonical task completion logs always belong under
JARVIS/tasks/loop-log.md, never under /home/nexus or a sibling source worktree.
