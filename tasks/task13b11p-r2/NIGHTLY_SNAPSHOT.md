# NIGHTLY SNAPSHOT JOB — read-only inspection (§47)

Inspected without modification. Not disabled, not edited, not re-scheduled.

| Property | Value |
|---|---|
| Script | `/opt/apps/nightly-snapshot.sh` |
| Trigger | user `nexus` crontab: `59 23 * * * /opt/apps/nightly-snapshot.sh` |
| Schedule | daily at 23:59 local |
| Log | `/opt/apps/nightly-snapshot.log` |
| Swept paths | every `"/opt/apps/IT TRAINING PROJECT CODE/projects"/*/` containing a `.git` |
| Protected (never mutated) | `projects/nexus-admin-academy` only |
| Action on a non-protected repo | `git add -A`; `git commit -m "Nightly snapshot $DATE"`; `git push origin HEAD:snapshot --force` |
| Action on a protected repo | records HEAD; archives drift to `~/backups/nexus/drift/`; never stages, commits or pushes |

## Exposure assessment for this task

- The JARVIS workspace clone **is** swept: it is `projects/JARVIS` and is not in
  `PROTECTED_DIRS`. This task's working documents under `tasks/task13b11p-r2/` were
  therefore exposed while uncommitted.
- The **production** repository is **not** swept. It lives at
  `jarvis@192.168.0.162:/home/jarvis/JARVIS`, outside `PROJECTS_DIR` and on a different
  host, so the job cannot reach production code, `config.yaml` or the sealed evidence.
- The push target is the `snapshot` branch, force-pushed. The job never writes
  `origin/main`; `origin/main` remains `2d7a2ec816500610eafdba4c1a3c0d73f5594c18`.

## Events during this task

None. The last snapshot commit is `5ac314f` "Nightly snapshot 2026-10-01", created during
task 13B11P-R1 and already recorded in that task's `FREEZE_RECORD.md`. The next firing is
23:59 today; this task ran shortly after 00:00 and completed well before it. Had the job
fired, it would be recorded here as an automated event and explicitly not as an authorized
manual push.

## Mitigation applied, within normal workflow

Working documents were committed promptly rather than left as mutable drafts in a swept
path, which is the only exposure reduction available without touching the job. No change
to the job was made or proposed; altering or disabling it needs operator approval.
