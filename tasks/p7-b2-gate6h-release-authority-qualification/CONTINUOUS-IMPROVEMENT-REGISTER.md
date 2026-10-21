# Continuous improvement register

Only three candidate files differ from Gate6G: new protected_authority.py, appended AuthoritySocket in existing local_control.py, new v3_protected_authority_test.py. Application modules and experimental legacy/Granite profiles unchanged. Source changes/manifests/patch retained. No production commit/push.

| ID | Delivered isolated improvement/fix | Tests/limits |
|---|---|---|
| H01 | Public-key Ed25519 verification, no signing API/private key in engine | Real signature/wrong-key/schema/replay cases; human presence not proved |
| H02 | One append transaction for nonce/root/reservation; cap/order/session/checkpoint and fresh proof/identity | Concurrent real connections, actual pre/post-commit exits, stale fields/expiry; companion only |
| H03 | First prototype protected only attempt count; would miss rollback of ledger within accepted attempt. Added protected SEND/SETTLE and independently associated terminal requirement | Pending unknown survives restart, blocks checkpoint/send/permit; wrong/stale terminal/resources refuse; crash cases. Real trusted reader absent |
| H04 | Checked root file owner but attacker-writable ancestor could replace directory. Added parent-owner/writable/sticky-root policy | Writable-parent regression plus real lstat/symlink/hardlink/inode/mode tests; actual distinct UID pending |
| H05 | Bounded operator socket and reply deadline; preserved existing single socket-import boundary by placing handler in local_control | Real SO_PEERCRED, malformed/oversize/trickle/wrong-allowlist cases; actual second UID/listener pending |
| H06 | Corrected legacy attestation variable to source JARVIS_OLLAMA_BASE_URL; stopped importing whole settings loader for narrow attestation | Source inspection; documentation correction, no runtime environment read |
| H07 | Corrected production D04 collector path to p7-shadow-evidence-v1; corrected historical source inventory location to Gate4 archive; original sealed docs located under docs/ | Read-only collector retries retained; final D04 absent/installed baseline match. No production defect/drift implied |

Qualification-only fixture defects and launch error are documented in TEST-RESULTS, not represented as product fixes. No baseline security assertion loosened, no experimental approval activated. In particular no32768→8192 runtime/default change, no memory/keep_alive/Granite/source prompt change.

Remaining proposals: protected service client/export/runtime wiring; trusted fixed-path source/process and independent terminal/checkpoint evidence; actual multi-UID/helper/signer; immutable dependencies/config/source signature policy; credential loader; external witness/host-loss recovery; real model/endpoint/topology/actor attestations; approved bootstrap/attach and X decisions. No broad architecture rewrite or historical tracing/reboot investigation performed.
