# Test results (Gate 6F)

Candidate `ff2444df135fcf8027d36cca9fa02fd7000884f88f78f76d74ddc68707dce733`. Both final stages were verified byte-identical to the 596-file inventory (0 mismatches).

Invocation (no credential environment), on Core with the read-only production venv:
```
env -i PATH=/usr/bin:/bin HOME=<stage>/home TMPDIR=<stage> P7_OFFLINE_STAGE=<stage> PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /home/jarvis/JARVIS/.venv/bin/python -B <stage>/supervise_tests.py <label> [paths]
```
Same 6E harness: Landlock ABI 8 (stage writable, venv/system read-only, home/production denied), seccomp (INET/PACKET sockets, connect, signals, ptrace, process-vm, mount, reboot, bpf/io_uring denied), Python audit hook.

## Final runs

| Run | Stage FS | Result | Time |
|---|---|---|---|
| Focused `g6f-focused-2`: v3_candidate, v3_security, v3_integration, v3_release_qualification | ext4 | **303 passed, 0 failed** (247 baseline + 56 new) | 110.6 s |
| Full `g6f-full-1`: repository pytest.ini | tmpfs | **7,469 passed, 11 deselected, 0 failed, 2 warnings** (7,413 baseline + 56 new) | 31.5 s |

Warnings are the two pre-existing Starlette/anyio deprecations. Zero newly introduced regressions. Historical Golden 12/20 (same eight failures) was **not rerun**; no real-model testing.

## Sandbox counters

| Run | blocked INET | network events | credential / production / external-write / execution blocks | approved offline children | broker signals |
|---|---|---|---|---|---|
| focused-2 | 0 | 0 | 0 / 0 / 0 / 0 | 10 | 0 |
| full-1 | 15 (pre-existing localhost discovery, refused before send, same as 6E) | 15 | 0 / 0 / 0 / 0 | 22 | 2 (verified disposable children only) |

Real external provider transmissions: **0**.

## Intermediate runs (all retained in evidence)

1. `g6f-new-1`: new file only, 51 passed / 5 failed — envelope arithmetic error in the test (1,460 vs 1,500 s) and 4 tamper tests unable to write the read-only V2 bundle. Test-only corrections; no assertion weakened.
2. `g6f-new-2`: 56 passed.
3. `g6f-focused-1`: 302 passed / 1 failed — `test_kernel_sandbox_canaries` got ENOENT instead of EACCES because the Core reboot cleared `/tmp/jarvis-gate6c-denied-dummy.txt`. Recreated the empty canary; no code change.

## Coverage and limits

New tests cover the L1 source-fidelity proofs, request-size fit with the real memory snapshot, oversize refusal, truthful operation counts (7 variants), time envelope, topology A–D, pre-send conflict refusal, remote-unknown retention, control replay (3 verbs), 9 process bindings, restart hold, trickling control peer, V2 stop attribution, 5 archive corruptions, partial and full rollback, real-kernel `RLIMIT_FSIZE` short write and EFBIG, permission drift and evidence symlink. Not covered: distinct OS identities, power loss, real wire/Ollama behaviour, external lifecycle actors. No dependency was installed.
