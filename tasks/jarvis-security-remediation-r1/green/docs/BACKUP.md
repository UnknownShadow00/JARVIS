# JARVIS Restic Backup and Recovery

JARVIS uses [Restic](https://restic.net/) for encrypted snapshots of local state that Git cannot recreate. The backup scripts do not contain credentials or machine-specific repository paths.

## Backup scope

The complete JARVIS root is supplied to Restic so ignored durable state is preserved alongside the matching source configuration. The committed `config/restic-excludes.txt` removes known reproducible or temporary material.

Included when present:

- `data/`, including Chroma state and future runtime traces;
- `logs/audit.jsonl`, while transient server and smoke logs are excluded;
- local `.env` configuration, protected by Restic encryption;
- ignored local configuration such as `.claude/`;
- custom assets or voice-reference files stored within the repository;
- additional absolute paths listed in the optional protected `JARVIS_BACKUP_PATHS_FILE`.

The optional paths file is useful for a private voice-reference WAV stored outside the repository. Use one absolute path per line; blank lines and lines beginning with `#` are ignored. Store this file outside Git.

Excluded because they are reproducible, downloaded, cached, or temporary:

- `.git/`, `node_modules/`, Python bytecode, pytest caches, and build output;
- `models/`, `piper/`, and `.ollama/` downloaded runtimes and model weights;
- the reproducible `data/tool_embeddings.json` embedding cache;
- test-created `tasks/tmp*.wav` files and audio caches;
- generated wake diagnostics and transient server/smoke logs.

`logs/audit.jsonl` is deliberately not excluded.

## Required environment

```bash
export RESTIC_REPOSITORY=/persistent/path/to/jarvis-restic
export RESTIC_PASSWORD_FILE=/protected/path/to/restic-password
export JARVIS_ROOT=/path/to/JARVIS
```

`JARVIS_ROOT` defaults to the repository containing the script. If Restic is not on `PATH`, set `RESTIC_BIN` to its absolute path. Set `JARVIS_BACKUP_PATHS_FILE` when durable data, such as private voice-reference audio, lives outside `JARVIS_ROOT`.

The password file should be outside the repository, owned by the backup user, and mode `0600` on Unix-like hosts.

> The Restic repository cannot be recovered without its encryption password.

Keep a protected recovery copy of the password separate from both the source disk and the backup repository.

## Manual backup

For the initial pre-Hermes snapshot:

```bash
JARVIS_BACKUP_TAG=pre-hermes ./scripts/backup_restic.sh
```

Later snapshots can omit `JARVIS_BACKUP_TAG` or provide an appropriate lifecycle tag.

## List snapshots

```bash
restic snapshots --tag jarvis
```

## Integrity and restore verification

The verification script runs `restic check`, restores to a uniquely named temporary directory, byte-compares durable state, and removes only the temporary restored copy:

```bash
./scripts/verify_restic_backup.sh latest
```

For small repositories, a stronger encrypted-pack read can also be run:

```bash
restic check --read-data
```

## Restore to an alternate directory

Never restore directly over a running JARVIS instance. Restore to a separate location first:

```bash
mkdir -p /tmp/jarvis-restore
restic restore latest --target /tmp/jarvis-restore
```

Because the backup source path is absolute, the restored tree appears below the target with its original absolute path components.

## Restore a single item

List snapshot contents to find the stored absolute path, then include that path:

```bash
restic ls latest
restic restore latest --target /tmp/jarvis-restore \
  --include /absolute/path/to/JARVIS/logs/audit.jsonl
```

## Disaster recovery

1. Clone the JARVIS GitHub repository.
2. Check out the desired tag or release, such as `v0.7-pre-hermes`.
3. Install the documented application and Restic dependencies.
4. Restore the protected Restic password file and set `RESTIC_REPOSITORY`.
5. Restore the snapshot to an alternate directory and copy reviewed runtime state into the clone.
6. Verify configuration, imports, `/health`, and authentication before normal startup.

## Scheduling

A scheduler may run `scripts/backup_restic.sh` after exporting the required environment. Do not enable unattended scheduling until the repository resides on persistent external or off-host storage. A same-disk repository proves recovery mechanics but does not protect against disk loss.

## Phase 0 validation record

The initial `nexus-services` validation used Restic 0.18.1 from Ubuntu's official package and a local encrypted repository at `/home/nexus/backups/jarvis-restic`. Snapshot `9140284d` was tagged `jarvis,pre-hermes`; `restic check`, `restic check --read-data`, a full temporary restore, and byte comparisons of runtime state all passed.

This repository is on the same physical disk as the live JARVIS checkout. It provides **LOCAL RESTORE PROTECTION ONLY — NOT DRIVE-FAILURE PROTECTION** and should be replicated to external or off-host storage before relying on it for disaster recovery.
