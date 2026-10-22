# Actual test results

| Layer | Actual result | Count interpretation |
|---|---|---|
| Unprivileged runner/prequalification |84 passed,0 failed |30 existing +54 new standalone unittest cases |
| Focused protected authority/runtime/security |200 passed,0 failed |existing cases; subset of full suite |
| Full applicable isolated suite |7741 passed /11 deselected /0 failed /2 warnings |exact revised616-file candidate; no new application cases |
| Real accept-based AF_UNIX |included in focused200 |same UID, with actual separate-PID delegation tests; not an additional count |
| Durable process crash/rollback |included in focused200 |real child process exits and disposable state; no VM power cuts |
| Genuine distinct-UID tests |NOT RUN |no approved VM or privileged execution |
| Offline dependency artifacts |BLOCKED |127 distributions+4 interpreter/library/image requirements unsupplied |

Focused duration 129.33737341407686 seconds. All616 staged source files verify. Tests ran on private Core ext4 data under LandlockABI8 and seccomp restrictions denying non-AF_UNIX sockets and production/home state access. Existing venv was read-only. No real providers or operational tools.

Intermediate evidence:76 checks first passed; subsequently added restrictive-umask regression failed once before its fix; r1 finished81 pass; r2 adds three mount tests and finishes84 pass. Historical raw tar synthetic probe exited2 while leaving a symlink but refused the follow-write. That probe is a policy negative control, not a final test failure. Nexus runner invocation is expected BLOCKED before writes, not a passed security invariant. Syntax parsed358 release Python modules and four human shell blocks; shell commands were NOT executed.

New application pytest cases:0 (no runtime source changes). New standalone prequalification cases:54. Do not add focused200 to the full total, or count archive extraction/static checks as additional pytest cases. Golden12/20 remains historical and was not rerun.

Preserved r1 also completed7741/11/0 before the mount-override correction. The final r2 run below is independently source-verified. Focused200 ran on r1; runtime code is identical.
Full duration: 400.374s. Candidate: `/home/jarvis/jarvis-gate6k-full-r2-AJs3QWLT/repo`. All616 staged files match the final bundle. The focused200 cases overlap the full7741; the84 standalone runner cases are separate. No final failure or silently skipped failure. The11 marker deselections preserve the historical applicable suite. No Golden/model-capable evaluation ran.
