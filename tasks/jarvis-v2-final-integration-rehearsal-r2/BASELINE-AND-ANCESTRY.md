# Exact baseline and ancestry

Verified source: `da67d936566d330fad02fa8f23f8e1be2d4b80ad`, tree `9cc1a9ecc3134b2f835017f6b5b0a55d215cebb4`. Canonical branch: `docs/p7-d06-d07-passive-review`, HEAD `b09fa10a661c9704f51e900ec857a51153cbcbbe`. The tracked working-tree change already present was tasks/loop-log.md. INITIAL-STATE.json records initial refs/status/hash/length; PRESERVATION.json checks all nine pre-existing worktrees before the mandatory final log append.

History:

- Historical Unified RC1: `e9b4734740070b9e7c990735e43801e592c114c6`.
- Development snapshot: `7640975527cf997435203b0377eaaf58b6d9f7b2`.
- Shared development ancestor: `b738a473d27471f35df60d31ccd93047bf9d1a6e`.
- Canonical subsequently adds its baseline-audit packet and log entries, reaching `b09fa10a661c9704f51e900ec857a51153cbcbbe`.
- Reconciliation: `7a5e1e99c` then reviewed `5c878448a90077ab277430f2b8ab3eec6b60a103` descend from the shared development ancestor.
- Coverage source/test enrollment: `34f354939`; launcher corrections: `183e29f8c`; disposable-copy permission fix: `5e1d5af0c3cfb363646a319c342a33394958c553`; evidence seal: `18a9d82c14e21869a179f110925165d9af9371a3`; final reviewed packet: `da67d936566d330fad02fa8f23f8e1be2d4b80ad`.

RC1/Reliability R3 form the historically reviewed source lineage; reconciliation copied the reviewed safeguards onto development instead of making those release commits Git ancestors. Source equivalence, not an invented ancestry, establishes their inclusion: `git diff b0c8865a da67d936 -- app` is empty. The R3 commit is `b0c8865a93608bae748445b38a3ea50175796806`. R1 `e310e587188f6802ea8a3301d49cb796ad9788a8` provided Simulator/timestamp/Gauntlet; R2 `b199acede69962919933d5bca364a587b1a2e8ca` provided scheduler ownership and sanitized completion evidence; R3 provided required identities. Reconciliation and coverage then explicitly extended source/test enrollment and retained source semantics.

The source tree was not manufactured again. New worktree creation used:

```sh
git worktree add -b codex/jarvis-v2-final-integration-rehearsal-r2 '../JARVIS-v2-final-integration-rehearsal-r2' da67d936566d330fad02fa8f23f8e1be2d4b80ad
```

Canonical changed128 paths since the common base; approved candidate changed761. Full path sets are in INITIAL-STATE.json, PRESERVATION.json and SOURCE-DELTA.json. Their intersection and file/directory prefix collisions are empty. This path analysis establishes no present content conflict; it is not a claimed merge execution. Canonical app/scripts/tests/public-example/pytest inputs have no change since the shared base. Later source changes invalidate that assumption.

The candidate's nine application differences relative to canonical/common development are:

- `app/agent/authority.py`
- `app/agent/scheduler.py`
- `app/agent/scheduler_backend.py`
- `app/agent/simulation.py`
- `app/agent/storage_paths.py`
- `app/cli.py`
- `app/comms/ue5_bridge.py`
- `app/config.py`
- `app/server.py`

The public example, nine runner/inventory tools and tests are also explicit in SOURCE-DELTA.json. This rehearsal adds no integrated runtime file. It neither copies newer host-enforcement tools nor modifies sealed packets. Frozen RC1, earlier reliability/reconciliation/rehearsal refs and their tracked status match the initial records.
