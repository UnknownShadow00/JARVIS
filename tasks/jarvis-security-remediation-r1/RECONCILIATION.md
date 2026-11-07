# Audited snapshot to final source

Audited source: comprehensive R1 snapshot-packaged,390 files. Final package:398 public files,26 added/changed paths. Exact hashes below and in final-source-reconciliation.json. Original ten post-cutoff paths were all reviewed.

| Path | State | Final SHA256 |
|---|---|---|
| `.dockerignore` | added | `436872700f9951b29b86d038a9b8305b536455bc49a10194d336e771b302e685` |
| `PROJECT_STATUS.md` | changed | `0e1bc194c90629612b6bfed3a4fb13442c6022767ed029f82e0aaec0999e2f1e` |
| `README.md` | changed | `84c8d62617a4ed7774080c76c7047c23d7a6f82e3d848f7eaddd6f4375ac1b04` |
| `app/agent/api.py` | changed | `0542b611e3d71d18910641aff6ef04334fe9b51651a53e627c763dd0b3ca636a` |
| `app/agent/authority.py` | changed | `ef6277075896f9b69c4469ab126fafacaaee072ca94ea85a9d3660c46c83f787` |
| `app/agent/ledger.py` | changed | `5b5e449949c7297b3f39872c83ad1d32e58bb5efc2b5ab1ea943a03de7ed2982` |
| `app/agent/storage_paths.py` | added | `1ca989b1baee5e24f4784a9f5d0fba2c3bf72c023aa6e83c737ed6fe403d474a` |
| `app/cli.py` | changed | `d34dfab21a46ab97fc50849e558c1dc157aeca44714d1b792d24b1e0e0abd83c` |
| `app/comms/ue5_bridge.py` | changed | `631675731ad8a35c0d6a57491be9a36df42f468054705194cf1d97fbf2a008b3` |
| `app/resource_manager.py` | changed | `8eb9027ddfe9880d05f041c05d52973971092533f6545d09c56439c663e3a77f` |
| `app/server.py` | changed | `5d01ef8541026fc9a6fb0b21f4529c1d05a68227acdced7d3d518794c84a9afb` |
| `config.yaml.example` | changed | `e60ed452191343a15eeb8bdb16c6d9122ba84a01d7b1080eddc777a1037a87f0` |
| `docs/end_to_end_readiness.md` | added | `229f465bed1b5741f0b37fe2219fdc36bf566c002f4a217e0b20a69230b19f3c` |
| `docs/operator_recovery.md` | changed | `3708ec78734067102c0d27afd520fee64f80ea5ff04819371cf26cba7350f0f2` |
| `docs/security_baseline.md` | added | `a1ef6f64006f65ecd1f1f2cab5d6c2d46a85f2ba7e6768ef0b56869b6b2a3a55` |
| `docs/task_api.md` | changed | `2b77f067567383131700a5f8ca553582cab5b3934b1f50446b79ebbd89884177` |
| `tests/test_audit_integration_fixes.py` | changed | `d29390c1aa2c9f9bd75571c97021e8ce4ebeb47a6d26475a0365c62b5d139221` |
| `tests/test_authority_http_security.py` | added | `aaedb0c963b6c1d4563463c4d7bbba5ac2bc57a4ab05ec02e62ffce45b343c24` |
| `tests/test_enrollment_app.py` | changed | `e950e5ce6d44e6661d25dce18c79ba033923b83eaa7647c266880469bd08b7ad` |
| `tests/test_execution_pipeline.py` | changed | `ababd7cf3efee60272402fef9cc528ced18f60298996248c47436ea912e0e62d` |
| `tests/test_release_security.py` | added | `f8abca234d6760d73f3e34df83ef54b8ba0509e8d98a2bed5692a452e0256493` |
| `tests/test_secure_transport.py` | changed | `a272beed2ad03678eeb9ef5f2d868e63df6537c8dcce126a2e8b3959b4794236` |
| `tests/test_server_auth.py` | changed | `3f795820068dadde3aa850efe3897859fbe092f0fe6b178158f46460483e8749` |
| `tests/test_storage_ancestry_security.py` | added | `2a644ea1ef3750c467507b58cd2bb4bf045c2f1965c37913b1da9c6184d261ad` |
| `tests/test_ue5_security.py` | added | `a7b89f0f570307be6699028a363daea7e0c0c2d31ea2b93bbdffe4f47dacdc59` |
| `tests/transport_fixtures.py` | changed | `98ba8ec1e719695f212ef39aa63e8d8fed4e4668a5baab8118be4aff0550bb2c` |


## Boundary review

- Authentication/API/WebSocket: router-wide async configured-credential enforcement including `/ready`; normal middleware/Origin controls preserved; UE5 all-exit cleanup, policy close deadline, finite manager state and sibling registration cleanup tested.
- Execution authorization: unchanged exact pure endpoint/type/permit/MAC enforcement. Test forgery now authenticates altered dummy response bodies where needed, testing semantic binding beyond MAC failure; second fixed hash endpoint adds no arbitrary destination.
- Queue/scheduler/receipts: implementation bytes unchanged; real worker API, nominal occurrence identity, cancellation and original receipt replay tested with explicit credentials.
- Recovery decisions/witness renewal/archive restoration: implementation bytes unchanged; same-history integrated witness renewal, UNKNOWN reconciliation, separate publication, inert restore and nonactivating proposal approval tested. New storage checks add refusal, not recovery or activation authority.
- Filesystem: ancestry and lifetime fences integrated; creation validated before mutation through retained no-follow directory descriptors. Parent replacement, bad modes and symlink races tested with dummy paths. No atomic SQLite VFS or hostile-owner guarantee.
- CLI/resource manager: original post-cutoff removal of local offline host effects and stronger child-lease identity checked. No implicit process start/termination fallback remains; regressions use declared inert dummy children only.
- Proxmox: all43 public current-successor files match audited hashes. No broker/worker hookup, token/ACL/guest/NIC/console/power or qualification operation occurred.
- Configuration/docs/build: credential contract corrected, runtime config untouched; Docker context now restricted to explicit COPY inputs. No Docker build or dependency installation occurred.

Initial engineering source was dirty. Concurrent source edits already in progress were preserved and reviewed; this task additionally completed lifecycle, auth/readiness, descriptor-relative creation, tests, docs and context hardening. SOURCE.patch records this task's before-to-final public-source differences; it is not a git reset or a rewrite of prior sprint changes. Separate review/source pins are not conflated with final runtime evidence.
