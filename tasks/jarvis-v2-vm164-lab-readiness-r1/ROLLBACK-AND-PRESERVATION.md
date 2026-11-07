# Tested rollback and evidence preservation

Installation never updates a current-release pointer or starts a service. The
previous application and broker remain untouched. Every destination is exclusive;
any preexisting path refuses. There is no automatic retry, cleanup or deletion.

The fixture suite tests interrupted publication: bytes already written remain at
the failed destination, validation refuses the incomplete inventory, and reusing
the same path refuses. Retain the complete directory and all output. A new attempt
needs a reviewed fresh name/destination and new authorization; the fixed production
candidate destination cannot be reused automatically.

For a complete never-activated dormant release, the protected `quarantine` command
first validates every installed file, owner/mode, hash and exact inventory, then
renames the directory into an exclusively created same-parent quarantine container.
All bytes and metadata remain present; no state is erased. The fixture suite checks
the hashes at the preserved location. Existing quarantine names refuse; parent
handles remain retained and fsynced. Runtime state, authority DBs and services are
not part of this dormant-release operation.

A future operator can use, under a fresh still-valid exact installation approval:

```text
/usr/bin/python3.14 -I -B /root/protected-bootstrap/lab_package.py quarantine /approved-local-staging/BUNDLE.tar.gz EXACT_BUNDLE_SHA256 /etc/jarvis-v2-lab/approval.json
```

Partial, modified or unexpectedly activated releases do not pass this command.
Leave them in place for operator review. No reset, recursive removal, permission
repair, ledger clearance, VM snapshot/restore/delete, power operation, role/token
revocation or existing-service stop is authorized by this preparation. Actual VM
rollback after activation requires a separately reviewed state/volatile-evidence
retention and stop/revoke plan. Same-UID fixture success is not actual root/multi-UID
filesystem, physical durability or live rollback qualification.
