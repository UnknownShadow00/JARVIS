# Read-only verification and fresh replay

Run from the canonical JARVIS workspace. Existing RC1 and predecessor packets
remain sealed. No target, real config/database, credential or service is needed.

```sh
python3 -I -B -S tasks/jarvis-v2-vm164-lab-readiness-r1/tools/verify_preparation.py
```

This checks final archive bytes and deterministic reconstruction, exact source and
wheel RECORDs, accepted tests, full quarantine preservation, SBOM/advisory records,
observer denial, canonical log and original sealed RC1/predecessor inventories.
It never imports the application or opens a runtime store. It requires the retained
canonical evidence/worktree and original source/dependency records; a different
host can independently verify the package using the standalone bootstrap and
its externally retained SHA256 without that historical workspace.

The final BUNDLE.json names the only delivery archive. All other bundle directories
are superseded retained engineering drafts. The bundle's `verify` command needs
that exact64-hex independent pin and checks all source/wheel bytes before reporting
VERIFIED_INERT_BUNDLE. It does not grant installation authority.

Installation/negative fixtures can be rerun by tools/run_install_tests.py. It
creates a fresh timestamped namespace/output and installs into a new synthetic
UID1000 work directory. Because it adds new evidence, **copy the prepared packet
into a fresh exclusive sibling task packet first** and leave this sealed packet
unchanged. Keep it at the same JARVIS/tasks depth. Existing native bwrap/Python3.14.4
and original local idna wheel are prerequisites; no install/download fallback.
Each fresh result binds actual source/tool/test and final bundle hashes. The known
namespace preflight refusal is retained and excluded from final acceptance totals.

The actual final installed smoke invocation and exact output are named in
SMOKE-INVOCATION.json; it passed210 cases plus20 groups. Its verified install source
was subsequently moved intact by the complete-release rollback test into the
FULL-ROLLBACK-RESULT.json path. To replay smoke, make a fresh fixture installation;
do not reuse, edit or reactivate the quarantined evidence. Smoke accepts a new
output path and the independent installed_manifest_sha256 from BUNDLE.json.

The broker's71-method/305-subtest no-network suite can be replayed in a fresh packet
with tools/run_broker_tests.py. It copies only the pinned dormant candidate into
fresh scratch; never run the predecessor tests in their sealed original packet.
The SBOM validator uses retained official schemas and existing analysis-only
jsonschema tooling in a networkless cage. OSV advisory data and the observer result
are snapshots; future refreshes belong in a fresh task/evidence packet. Refreshing
advisories sends exact public package/version metadata only. Observer refresh is
GET-only, pinned and secret-suppressing; a401 is a blocker, not permission to repair
or replace a token. Do not run capture scripts to overwrite sealed evidence.

All protected/guest operations are future-only templates in INSTALLATION-PROCEDURE.md.
The next authorization request is AUTHORIZATION-REQUEST.md. The package includes no
active approval, OS/runtime installer, credentials, real provider or execution grant.
