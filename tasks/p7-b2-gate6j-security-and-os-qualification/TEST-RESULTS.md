# Actual test results

Final release-r2 full applicable suite: **7741 passed / 11 deselected / zero failures / 2 existing warnings**, 536.72 seconds, ext4 disposable Core stage under Landlock8 and non-AF_UNIX socket denial. All613 staged bundle files match the final candidate. The earlier full-r1 also passed7741/11/zero, before final runner packaging/security changes; it is retained, not mislabeled as final.

Historical Gate6I baseline7719 passes is preserved; **22 new candidate regression cases** account for the full-suite increase. Additionally **30 unprivileged runner unit cases** and **3 supplemental actual-socket probes** pass. Thus55 new test cases across these three sets, plus a separately recorded real same-UID kernel-confinement probe. Do not add focused re-runs to the full-suite count.

| Run | Actual outcome | Interpretation |
|---|---|---|
| redteam-before | 2 failed | Confirmed direct provider/native bypasses on unchanged Gate6I code |
| redteam-r1 | 110 passed | First15 new cases plus95 prior protected-runtime cases |
| delegated-before | 1 failed /15 deselected | Real second-PID writer inherited connector authority |
| terminal-before | 1 failed /17 deselected | Protected INCOMPLETE disagreed with local COMPLETE |
| focused-r2 | 569 passed /1 failed | Newly introduced runner module import path error; corrected, no assertion weakened |
| redteam-final | 22 passed | All candidate red-team regressions after fixes |
| full-r1 | 7741 passed /11 deselected /0 failed | Intermediate complete runtime regression |
| full-final | 7741 passed /11 deselected /0 failed | Exact final bundle regression |
| wire-final | 3 passed | Final613 candidate files plus separately manifested wire probe harness |
| runner-final-r2.txt | 30 passed | Actual unprivileged package tests; source matches final copied runner |
| kernel-runner-probe.json | PASS | Child UID1000 unchanged; actual no_new_privs and socket-family refusal |
| compile.json | 147 modules PASS | No bytecode written |
| dependency-pin-check-final.json | 127 effective package pins match | Python3.14.4/SQLite3.46.1/crypto46.0.5 match; no installation |
| current-host runner entry | BLOCKED as expected | Nonroot preflight refusal; not OS security qualification |
| genuine distinct-UID VM run | NOT RUN | No approved VM or privileged execution |

Intermediate runner manifest-fixture failure (22 pass/1 error) is retained. Its newly created parent directories were group-writable; only new Gate6J directory modes were tightened. Initial dependency capture had11 duplicate system/venv metadata mismatches; effective-version capture corrected them. Earlier unprivileged runner passes are retained as intermediate revisions. No failing test was silently skipped and no security assertion was relaxed.

The two full-suite warnings are existing FastAPI/Starlette/httpx/AnyIO deprecations. No package upgrade was made. Historical Golden12/20 with eight failures remains historical; model-capable Golden evaluations were not run. No live provider, model lifecycle or operational execution was used. New process-crash tests use disposable child os._exit, not VM power cuts. Same-UID actual sockets/processes and pure fixture checks are labeled separately from NOT RUN cross-UID tests.
