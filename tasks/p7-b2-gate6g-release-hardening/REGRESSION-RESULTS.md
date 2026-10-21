# Gate 6G regression results

Final source: release-r1, source-manifest digest `7e797307b2ae2d372cc1a8bbe00894b66b468ee472ec3296d18bc8d08de9c370` (32 members). Full inventory: 599 files. Every run was verified against its own input archive after testing; zero mismatches, including all 599 files in both final runs and the ext4 repeat.

| Run | Result | Filesystem | pytest time |
|---|---|---|---|
| Gate 6F historical focused | 303 passed | ext4 | 110.6 s |
| Gate 6F historical full | 7,469 passed, 11 deselected, 2 warnings | tmpfs | 31.5 s |
| g6g-focused-final | **375 passed, 0 failed** | tmpfs | **9.81 s** |
| g6g-full-final | **7,541 passed, 11 deselected, 0 failed, 2 warnings** | tmpfs | **33.12 s** |
| g6g-ext4-final (new hardening file) | **72 passed, 0 failed** | ext4 | **18.20 s** |

The two warnings are the existing FastAPI/Starlette httpx and anyio BlockingPortal deprecations. No dependency was installed or upgraded. `pip check` reports no broken requirements. In-memory compilation succeeded for 145 app/candidate/focused-test Python files. Imports are exercised by the focused/full suites. No separate established lint/type gate was invoked; the actual patch was reviewed manually. Coverage was not measured; passing counts are not a coverage claim. No independent peer review or multi-UID qualification was performed.

Final focused command on Nexus (use a new task/run version after sealing):
```
python3 tools/run_isolated.py <unique-label> tests/execution/v3_candidate_test.py tests/execution/v3_security_test.py tests/execution/v3_integration_test.py tests/execution/v3_release_qualification_test.py tests/execution/v3_release_hardening_test.py
```
The full command omits paths and uses the copied repository's pytest.ini. Ext4 uses `STAGE_PARENT=/home/jarvis` with the new hardening test file. The launcher uses env -i, a private disposable HOME/TMPDIR, Python -B, disabled plugin autoload and the read-only existing Core venv. It runs the unchanged Gate 6F qualification harness: Landlock ABI 8, seccomp and Python audit hook. The writable stage is isolated; production state, credentials and actual network sends are denied. No live listener or provider call is needed.

Final focused/ext4: no network events and zero credential/production/external-write/execution blocks. Final full: 15 pre-existing network/DNS discovery attempts blocked before send; zero credential/production/external-write/execution blocks. The broker signaled two independently verified disposable children only, preserving the existing writer-crash tests. Counts and raw logs are in evidence/sandbox-results.json and evidence/runs/.

Earlier runs retained: g6g-new-1, 60 passed/1 failed (test fixture type corrected, exact refusal assertion retained); g6g-focused-1, 364 passed; g6g-full-1, 7,539 passed/11 deselected/2 warnings. Two subsequent tests plus the actual isolated lifespan hook account for the final 375/7,541 totals. No production or actual model behavior was measured. Historical golden 12/20 is not re-certified or fixed.
