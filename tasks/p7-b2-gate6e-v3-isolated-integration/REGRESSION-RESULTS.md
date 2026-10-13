# Regression results

Nonproduction Gate 6E reference implementation. No production installation, experiment approval, model traffic, credential use or measurement. G6D-LP-1 remains a proposal.

See sealed qualification-results for exact commands, kernel policy, timings, warnings and all intermediate failures. Final r2: **247 focused passed / 0 failed (92.55s on disposable ext4)**; **7,413 full passed / 11 deselected / 0 failed / 2 warnings (29.27s)**. This adds 98 passing tests to the Gate6D baseline of 7,315. No tests were skipped in these final runs; 11 cases were deselected by existing repository exclusions. Warnings are the existing Starlette httpx TestClient and anyio BlockingPortal deprecations.

Invocation pattern (no credential environment):
```
env -i PATH=/usr/bin:/bin HOME=<stage>/home TMPDIR=<stage> P7_OFFLINE_STAGE=<stage> PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 /home/jarvis/JARVIS/.venv/bin/python -B <stage>/supervise_tests.py <label> [test paths]
```
Focused paths: tests/execution/v3_candidate_test.py, v3_security_test.py, v3_integration_test.py. Full run uses the repository pytest.ini exclusions:11 deselected, no live Golden requalification. Historical Golden12/20, same eight failures, remains historical only.

Landlock ABI8 permits writes only within disposable stage; system/venv read-only, other home/production state denied. Seccomp blocks INET/PACKET sockets, all connect, signals, ptrace, process-vm, mount, reboot and bpf/io_uring. Existing narrowly reviewed supervisor signals only its disposable direct test children. Python audit adds credential/production-write/network/execution checks. Actual AF_UNIX testing uses socketpair, not an installed listener.

New transport tests inject MockTransport/byte streams; no Ollama request is sent. Full-suite existing localhost discovery attempts are blocked before network access and counted as denied attempts, not successful transmissions. No dependency install or network audit was run; no commit was created. Host-wide unrelated network activity is outside this task's claim.

Initial integration collection failed on an incorrect import; corrected. First41 integration tests passed. One focused run was terminated for a test-only no-message-handshake wait. Subsequent runs:221 passed/2 failed (import contract and fixture attribute);229 passed/1 failed (missing done_reason fixture);240 passed/0 failed. All logs are retained. R1 then passed 242 focused and 7,408 full tests; r1 remains archived. R2 added independent rehashed-checkpoint consistency and transport drain checks, with the final counts above.
