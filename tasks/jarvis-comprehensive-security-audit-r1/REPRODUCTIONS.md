# Bounded reproduction index

No confirmed exploitable security vulnerability is claimed. Current D7 input/commands/result/fix are in [IMPLEMENTATION-DEFECTS.md](IMPLEMENTATION-DEFECTS.md). Six earlier reproduced mechanics are historical and now gated/fixed at their reviewed call sites; replay only against the recorded capture in historical-defects.json.

| Check | Fixture | Capture / result artifact |
|---|---|---|
| Conditional authority | agents/verify-latest-auth/scratch/verify_auth_packaged.py | snapshot-packaged / agents/verify-latest-auth/artifacts/verify_auth_packaged.txt |
| UE5 binary cleanup | agents/hunt-packaged-safety/scratch/ue5_binary_cleanup.py | snapshot-packaged / agents/hunt-packaged-safety/artifacts/ue5_binary_cleanup.txt |
| Safety fixes | agents/hunt-packaged-safety/scratch/packaged_safety_tests.py | snapshot-packaged / agents/hunt-packaged-safety/artifacts/packaged_safety_tests.txt |
| Transport/offline recovery | agents/hunt-packaged-transport/scratch/packaged_transport_tests.py | snapshot-packaged / agents/hunt-packaged-transport/artifacts/packaged_transport_tests.txt |
| Legacy effect denial | agents/hunt-latest-safety/scratch/latest_safety.py | snapshot-latest / agents/hunt-latest-safety/artifacts/latest_safety.txt |
| Ancestor substitution | agents/parent-current/scratch/ancestor-current.py | snapshot-current / agents/parent-current/artifacts/ancestor-current.txt |
| Hot-journal recovery | agents/parent-final/scratch/hot-journal-controls.py | snapshot-final / agents/parent-final/artifacts/hot-journal-controls.txt |
| Current broker chain | agents/hunt-infra-current-chain/scratch/current_chain_controls.py | snapshot-expanded / agents/hunt-infra-current-chain/artifacts/current_chain_controls.txt |
| Current preissuance/files | agents/hunt-infra-current-files/scratch/current-file-controls.py | snapshot-expanded / agents/hunt-infra-current-files/artifacts/current-file-controls.txt |

From this audit directory, copy a fixture to a fresh basename in the same owner's scratch, then run `python3 sandbox-runner.py OWNER COPIED_FIXTURE SNAPSHOT`. Every replay needs a fresh stem; existing results are never overwritten. Target sees readonly source/tools, empty allowlisted environment and scratch-local writes, with no external network, host home, credentials, services, devices or other agents' artifacts. Namespace/process termination precedes bounded predeclared no-follow descriptor-confined promotion.

Runner code, safe environment and exact resource limits are retained in sandbox-runner.py/validation-summary.json. Toolchain inventory is not deployment identity. No screenshot or separate-UID/native-writer qualification was performed; the current application capture path is rejected.
