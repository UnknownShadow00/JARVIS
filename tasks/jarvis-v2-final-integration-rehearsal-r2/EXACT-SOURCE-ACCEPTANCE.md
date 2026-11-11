# Acceptance of the exact approved source

The independent audit explicitly reviewed `da67d936566d330fad02fa8f23f8e1be2d4b80ad`. Both approval files are preserved with hashes. All acceptance jobs ran from its newly copied public input tree, before creating the final documentation commit. Source Git tree: `9cc1a9ecc3134b2f835017f6b5b0a55d215cebb4`. Input fingerprint: `da3f737d827f7e33cc18e82a6dee65808af399823a8ac7b9a1db829055667373`. The final commit is a documentation/evidence child of this source, not a newly reviewed application implementation.

Exact fresh launcher command, from the rehearsal worktree:

```sh
python3 -B tasks/jarvis-v2-baseline-coverage-remediation-r2/accept_snapshot.py '/opt/apps/IT TRAINING PROJECT CODE/projects/JARVIS-v2-final-integration-rehearsal-r2/tasks/jarvis-v2-final-integration-rehearsal-r2/acceptance'
```

Exit0; stdout PASS886; all14 jobs exited0. EXECUTION.json and acceptance/RESULT.json preserve the command, exact interpreter, per-job arguments and exits. This is a NEW output directory; no prior acceptance is reused. The launcher requires tracked clean inputs, rejects symlinks, snapshots266 public files, and verifies before/copy/after equality. Private config, credentials, runtime paths, VM paths and host sockets are not mounted.

Retained snapshot: `/tmp/jarvis-coverage-acceptance-8xj_w2p7/source`. Files0444, directories0555. Namespace execution uses read-only binds, unshare-all including networking, cleared environment, dropped capabilities and resource bounds. Test scratch and output are separate. Actual process gates require the pinned manifest, successful collection and complete successful phase evidence for each exact expected identity; zero subprocess exit alone cannot pass.

The extra12 audit attacks were replayed by replay_audit_attacks.py with explicit snapshot/output arguments. Only disposable clones become writable. The approved source, module policy and acceptance snapshot were not modified. AUDIT-ATTACK-EXECUTION.json preserves its command/exit. The original audit helper digest and the narrow adapter changes are in EXECUTION.json. This is a reproduction of audit attacks by this engineer, not a new independent organizational review.

Fresh independent reconstruction command:

```sh
python3 -B tasks/jarvis-v2-final-integration-rehearsal-r2/verify_rehearsal.py --output tasks/jarvis-v2-final-integration-rehearsal-r2/VERIFICATION.json
```

It checks source bytes against the approved Git blobs, snapshot permissions, inventory/policy hashes, actual module partition, exact node/opaque-ID sets, every phase, both fixed seeds, child/gate exits, all contract summaries, missing Astra identities, evidence digests and dependency metadata. It never regenerates or promotes the required inventory. Re-run with a NEW output path, or omit --output for read-only verification. The snapshot must be retained; absence fails rather than bypassing source checks.

To recreate acceptance, choose a new output path; the launcher refuses overwriting old evidence. Use a clean checkout of the exact approved commit for exact-source provenance. A later evidence-only commit has a different Git tree; compare its266 source inputs against this record rather than changing the provenance label.
