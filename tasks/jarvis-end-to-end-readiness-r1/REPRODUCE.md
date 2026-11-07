# Offline reproduction

Work from `/opt/apps/IT TRAINING PROJECT CODE/projects/JARVIS`. Do not run the stock
server, real tools, optional providers or production configuration. The runner
copies public config.yaml.example only and constructs disposable in-cage state.
It verifies the preexisting bwrap/interpreter, predecessor guard, dependency plan,
installed target RECORD/manifest and exact 28-package closure before payload work.
No installation, network or fake package/module substitution is required.

Run each mode sequentially, with no overlapping audit/test payload. Example:

```sh
python3 -I -B -S tasks/jarvis-end-to-end-readiness-r1/run_checks.py --mode focused --target tasks/jarvis-authority-readiness-r1/runs/20261031T090522534346Z/output/site-packages
```

Repeat the command changing only --mode to `full-app`, `core`, `enrollment`,
`recovery`, then `benchmark`. Exit75 means an observed independent audit payload is
active and no test was started; wait for it to finish rather than interrupt it.
Do not weaken namespace/resource/hash controls if the retained target is unavailable.
Each run writes a fresh timestamped directory; never overwrite earlier evidence.

The cage unshares user/mount/PID/network/IPC/UTS namespaces, drops capabilities,
sets no-new-privileges, exposes source/dependencies read-only and scratch writable,
checks canaries, and records guards/headroom/toolchain and native library hashes.
All tests and demonstrations run inside it, including actual ASGI lifespan,
AF_UNIX frames and independent subprocess SIGKILL tests. No HTTP listener is opened.
The operator CLI subprocesses receive disposable keys only on inherited FDs.

Inspect the final run directories named in RESULTS.json. Each includes RUN.json,
stdout/stderr, input manifest, synthetic output and limits. Intermediate failures
are retained. INTEGRATED-DEMONSTRATION.json contains the same-history application
workflow; CRASH-RECOVERY.json aggregates the new 15 crash observations.

Verify the current sealed packet without running application code:

```sh
python3 -I -B -S tasks/jarvis-end-to-end-readiness-r1/verify_evidence.py
```

The assembler build_evidence.py is an engineering-time generator, not a reader or
operator mutation command. Do not rerun it to replace a sealed packet. Source.patch
applies against before/, which records the actual dirty pre-Sprint6 source rather
than pretending earlier sprint changes were part of this sprint. No migration or
production rollout command is authorized by this document.
