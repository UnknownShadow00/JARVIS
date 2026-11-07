# Reproduce the offline baseline

Run from the JARVIS root. The runner creates only an isolated ephemeral namespace with readonly source/toolchain and bounded scratch. It needs the already available bwrap, Python3.14 and recorded local dependency tree; it installs nothing and never loads production config/data. Do not substitute live databases or provider settings.

Evidence promotion is exclusive. Copy each named harness to a **fresh basename** in the same owner's scratch directory for every replay, then run:

```sh
python3 tasks/jarvis-security-remediation-r1/sandbox-runner.py regression tasks/jarvis-security-remediation-r1/agents/regression/scratch/NEW_BASENAME.py final-2
```

| Purpose | Existing harness (copy before replay) | Owner |
|---|---|---|
|109 HTTP/WS/ancestry cases|agents/regression/scratch/http_regressions_updated_final.py|regression|
|33 execution/scheduler/lifecycle cases|agents/regression/scratch/execution_regressions_updated_final.py|regression|
|13 transport/publication cases|agents/regression/scratch/transport_regressions_updated_final.py|regression|
|13 ledger/restore/witness cases|agents/regression/scratch/durability_regressions_final.py|regression|
|Genuine lifespan/socket, separate client process|agents/authority/scratch/authority_socket_final_checked.py|authority|
|Four integrated shared-history groups|agents/integration/scratch/sprint6_replay_final.py|integration|

Use the corresponding owner and harness path for the last two rows. All final runtime code/test/config bytes match the runtime-tested `final` snapshot; `final-2` adds only .dockerignore. Per-run manifests bind source, harness, runner and inputs. Source hashes are in SOURCE.sha256.

Pre-fix comparisons are deliberately separate: ue5_red.py targets snapshot `red`; authority_socket_probe.py targets `before`; storage_creation_red.py targets `candidate-3`. Expected failures must not be mixed into final pass totals or replayed as if final source. Original artifacts and intermediate failures remain retained.

Limits: 10CPU seconds,512MiB address space,64 processes,96 descriptors,2MiB individual file size,32MiB scratch,25-second wall,256KiB output, explicit0077 umask, empty allowlisted environment, no external network/host home/credentials/devices/services. Trusted parent code promotes only bounded predeclared regular output using retained no-follow directory descriptors after namespace termination. Network listeners exist only inside the unshared network namespace, on ephemeral loopback ports with dummy state. DifferentUID mapping is unavailable. Docker configuration is statically reviewed; no actual image build was performed.
