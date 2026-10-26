# Actual offline results

| Layer | Result | Interpretation |
|---|---|---|
| Standalone runner/preflight |133 passed,0 failed |84 existing +49 new cases; actual files, metadata, malformed mounts and import-only subprocesses; same UID fixtures |
| Extracted replacement archive standalone |133 passed,0 failed |Repeat of the same cases on actual extracted bytes; do not add to total |
| Full applicable isolated suite |7741 passed,11 deselected,0 failed,2 warnings |Final run 501.912s; application/dependency pins unchanged |
| Handoff destination/host/interface policy |5 passed |Separate mocked CLI gates; extraction mocked; no root/UID qualification |
| Focused sandbox canary |1 passed |Subset of full suite; actual libc file-read denial and non-AF_UNIX socket denial |
| Archive validation/extraction |619 members verified/extracted |618 source entries plus manifest; unprivileged Nexus fixture |
| Source syntax |361 Python modules parsed |Human shell blocks:3 syntax-valid, not executed |
| Ubuntu compatibility |Ubuntu26.04 LTS,x86-64,kernel7.0.0-38-generic |Actual Nexus OS; VM-specific mounts/credentials remain fixtures/operator reports |
| Required runtime |Python3.14.4,SQLite3.46.1,crypto46.0.5,pytest9.1.1,127 pins matched |No package/system Python changes |
| Genuine distinct-UID / privileged VM qualification |NOT RUN |No VM connection or qualification entrypoint execution |

Final tests ran with LandlockABI8 and seccomp denying non-AF_UNIX sockets, external writes and dangerous syscalls. The signal broker retains direct-child, UID, executable, cwd and pidfd validation. Fake integrations only. Existing real AF_UNIX and crash/rollback cases are included in the full suite; they are not new cross-UID evidence. Golden12/20 is historical and was not run.

New tests cover empty OS containers, real synthetic credential payloads (including empty payload files), cache review/snapshot invalidation, known credential indicators, ownership/modes, symlinks/hardlinks/FIFO, inaccessible/changing metadata, directory-only opening, bounded traversal, approved/unapproved `/boot`, unsafe/shared/protected mounts, credential tmpfs flags, active networking/prohibited hosts, protocol approval fields and `-I` import without qualification execution.

Intermediate failures are preserved: first130-case run had8 fixture failures because Nexus's default umask made synthetic parents group-writable. Setting the fixture umask to022 restored the intended safe baseline while separate unsafe-mode assertions remained. The first guarded133-case run had7 errors because no permitted TMPDIR was configured; the runner now supplies its isolated stage. Initial full run:7740 passed,1 failed,11 deselected; the explicit historical `/tmp/jarvis-gate6c-denied-dummy.txt` canary was absent (ENOENT), not denied (EACCES/EPERM). Exclusive creation of that harmless synthetic file fixed the prerequisite, with no assertion/source change. Its inode/owner identity is retained in the private canary record; no existing unknown file was read or overwritten. Final full rerun passes all7741. No failures were deselected or silently skipped.

Full and intermediate raw logs remain private at paths/digests in evidence/retained-log-index.json. Minimized summaries, final standalone logs and kernel restriction records are sealed here. The2 warnings are existing FastAPI/Starlette deprecations. Static pyright/ruff and coverage tools are absent from the pinned environment: NOT RUN / coverage NOT MEASURED; no dependencies were added to obtain those optional results.
