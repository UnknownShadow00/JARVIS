# Reproduce the frozen candidate offline

Use the retained workspace `/opt/apps/IT TRAINING PROJECT CODE/projects/JARVIS`.
The detached source tree is its sibling `JARVIS-release-r1`; final payloads copy
that candidate, not the concurrently edited shared application source. The canonical
log and task artifacts always resolve against the original JARVIS project.

Do not start production JARVIS, import its real config, install dependencies or run
an unguarded root pytest command. The qualified runner copies the public example,
sanitizes synthetic settings and creates disposable SQLite/custody inside its cage.
The manual Ollama CLI helper has zero test functions and is excluded before import;
no provider is installed or contacted to make a collection pass.

First verify the retained packet, source archive and input identities:

```sh
python3 -I -B -S tasks/jarvis-v2-release-readiness-r1/verify_release.py
```

The read-only verifier never imports application code, provisions keys, opens
runtime stores or modifies the sealed packet. `--archive-only` verifies the source
release without requiring every predecessor/test toolchain file. Optional
`--check-working-source` additionally compares the current detached worktree with
its frozen archive. A future edit there does not rewrite the existing release.

Retained prerequisites: the exact verified Python3.14 interpreter and bwrap, the
prior guard packet and exact28 dependency target named below, and the packet's
read-only optional-target (three verified wheels) for broader modes. Complete
wheel/upstream/RECORD hashes are retained. No downloads are necessary here.
A separate host would need these same public retained artifacts and supported
namespace/native-library semantics; the source tar is not an OS/container image.
Do not weaken guards or substitute an unrelated installed environment if they
are missing. `materialize_optional.py` was an exclusive build-time generator and
refuses an existing target; its current target is already preserved.

Run modes sequentially with no overlapping heavy payload:

```sh
python3 -I -B -S tasks/jarvis-v2-release-readiness-r1/run_checks.py --mode core --target tasks/jarvis-authority-readiness-r1/runs/20261031T090522534346Z/output/site-packages
```

Repeat changing only --mode to `broad-collect`, `broad-safe`, `broad-legacy`,
`broad-security`, `focused`, `full-app`, `enrollment`, `recovery`, and `benchmark`.
`broad-safe` now includes the two bounded slow tests. Nine actual desktop/hardware
cases remain deselected and are listed in TEST-INVENTORY.json. No failure or
skip is relabeled as a pass. Exit75 defers before a run starts if the independent
comprehensive audit payload is observed; wait instead of interrupting it.

Every invocation uses a fresh timestamped run directory, verified read-only input
and dependency mounts, network/user/mount/PID/IPC/UTS isolation, dropped capabilities,
no-new-privileges, controlled scratch and canary checks. It retains stdout/stderr,
input hashes, headroom, source hashes, native origins and resource observations.
Bounds are AS1GiB/process, aggregate RSS768MiB, CPU120/121s, wall120s, 64MiB/file,
FD64/core0, 20,000 files/256MiB controlled storage and two payload processes plus
namespace machinery. NumPy threads are constrained. No real device, production
state or external provider mount is added.

Full-app executes actual ASGI lifespan without opening a network listener and
actual synthetic AF_UNIX messages, SQLite writes and CLI key-FD reconciliation.
The scheduler's original nominal callback is explicitly invoked; no wall-clock
cron timing claim is made. Crash tests kill independent fixture processes and
reopen the original databases; they do not simulate a physical power cut.

The archive is fixed-metadata USTAR/gzip with sorted public members and no symlinks,
keys, .env, real config.yaml, state, logs, models or sealed task evidence. Its
SOURCE-SHA256.json and minimal 31-package lock are embedded under _release/.
`build_candidate.py` refuses repeat publication and performed a second identical
in-memory rebuild. Do not rerun build_evidence.py or summarize_results.py to replace
this sealed packet; they were construction tools. New engineering evidence belongs
in a new task packet or fresh run directory, with a new explicit seal.
