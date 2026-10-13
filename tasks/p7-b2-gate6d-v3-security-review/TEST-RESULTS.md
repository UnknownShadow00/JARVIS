# Exact isolated qualification results

| Run | Result | Interpretation |
|---|---|---|
| security-before |18 failed /2 passed,0.27s | Initial adversarial reproductions. Stop fault hooks were introduced with the fix; their initial failure establishes missing tested transaction boundary, not an injected old crash |
| security-after |114 passed,1.56s | Initial fixes + unchanged94 candidate tests |
| security-expanded |137 passed,2.23s | Added process exits, binding and ledger tests |
| focused-final |**149 passed,0 failed**,2.29s | Final source:94 existing +55 new adversarial cases |
| full-final (invalid global-token fixture) |36 failed /7279 passed /11 deselected,27.79s | Launcher injected DUMMY_GATE6D_ONLY globally, conflicting with historical empty-token baseline. This was a harness invocation error; preserved evidence |
| full-corrected |**7315 passed /11 deselected /0 failed**,2 existing warnings,27.02s | Identical source/tests; removed global env override. Per-test dummy authentication remains. No assertions/exclusions weakened |
| focused-ext4 |**149 passed /0 failed**,17.24s | Exact final source repeated in private disposable directory on Core root ext4; includes all five actual process exits |

Full result equals7166 canonical +149 candidate tests, versus Gate6C7260. Golden remains historical12/20 and the same eight failures; no Golden generation/digest requalification.

Commands (Core, task-private existing environment; no package installs):

```sh
env -i PATH=/usr/bin:/bin   HOME=/tmp/jarvis-gate6d-tests-WCbozC3X/home   TMPDIR=/tmp/jarvis-gate6d-tests-WCbozC3X   P7_OFFLINE_STAGE=/tmp/jarvis-gate6d-tests-WCbozC3X   PYTHONDONTWRITEBYTECODE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1   /home/jarvis/JARVIS/.venv/bin/python -B   /tmp/jarvis-gate6d-tests-WCbozC3X/supervise_tests.py full-corrected tests
```

Focused command is the same launcher with `JARVIS_API_TOKEN=DUMMY_GATE6D_ONLY` and arguments `focused-final tests/execution/v3_security_test.py tests/execution/v3_candidate_test.py`. Initial full failure used that global dummy override and label full-final. Other focused labels selected the same modules except security-before selected only v3_security_test.py. Launcher adds `-q --capture=sys -p pytest_asyncio.plugin -p offline_fixtures -p no:cacheprovider --basetemp <stage>/fixtures-<label>`. Existing pytest.ini selects `not desktop and not manual and not hardware and not slow and not e2e and not stress and not perf`; same11 exclusions as Gate6C.

Landlock ABI8 denied production/credential file contents and outside writes, allowing only the candidate stage plus read-only interpreter/system dependencies. Seccomp denied INET/PACKET sockets, connect, signals/ptrace/process_vm and other escape operations; existing canaries verify kernel denial. Python audit guard provided counters. No actual provider/model traffic occurred. Full run recorded15 blocked localhost DNS requests from existing error-path tests,17 approved fixture child launches,0 credential/production-content/external-write attempts,0 prohibited execution attempts. Five new os._exit children per crash-test run intentionally cannot emit atexit audit. The ext4 repeat used the same command with stage `/home/jarvis/gate6d-fs-test-vRWRQNW1`, label focused-ext4 and the two focused modules, no global token override;0 blocked DNS/credential/production-content attempts and5 approved children. Two canonical writer-crash children were independently verified and signalled through a narrow pidfd broker; no service signal.

No dependency installation, dependency upgrade or commit was performed, so no precommit package audit was triggered. Dependency security is not newly certified; the two existing deprecations remain. Tests ran against copied committed baseline config; separate entry/exit readbacks bind the deployed SHADOW config and untouched app source. Full test logs, kernel policy, broker output and audit counters are retained in qualification-results. Raw production replies/environments/credentials are absent.
