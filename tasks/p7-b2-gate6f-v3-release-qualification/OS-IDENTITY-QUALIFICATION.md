# OS identity qualification

**Actual OS operator/service separation: NOT QUALIFIED.**

## What was checked (read-only, no privilege change)

| Host | Finding |
|---|---|
| nexus-services (dev) | uid 1000; `kernel.apparmor_restrict_unprivileged_userns=1`; `unshare -U -r` → `uid_map: Operation not permitted`; no `newuidmap`/`newgidmap`; subuid range exists but is unusable without the setuid helpers |
| Core 192.168.0.162 | Same: AppArmor restriction on, no `newuidmap`, `sudo -n` needs a password; one non-system account (`jarvis`) |

No already-authorized disposable second identity exists. The only other routes (docker or lxd group membership, sudo, installing uidmap, adding accounts, changing the AppArmor sysctl) are privilege escalations or system changes and were **not** used. Same-UID mocked peers are not evidence of human/service separation.

## What was tested at the same UID (kernel-real but not separation proof)

- AF_UNIX `SO_PEERCRED` extraction on real `socketpair` sockets; a peer whose uid ≠ configured operator uid is refused (6E).
- Bounded control packets; new 6F whole-request deadline cuts off a trickling peer in under 1.5 s (`test_afunix_trickling_peer_is_cut_off`).
- Mode/ownership policy: storage and evidence files must be owner-only regular files, single link, no symlinked ancestor; drift is refused before the kernel is asked (`test_permission_drift_blocks_checkpoint_and_next_permit`, `test_symlinked_evidence_file_refused`).
- Real kernel resource enforcement: `RLIMIT_FSIZE` short write / `EFBIG` (FILESYSTEM-FAILURE-RESULTS).

## Kernel/credential boundary a privileged deployment must enforce

1. Distinct uids: `jarvis-v3` (service), `jarvis-op` (human signer), and the existing `jarvis` uid (Codex/dev) which must have **no** write access to service state or signer keys.
2. Control socket directory `0750 root:jarvis-op-ctl`, socket `0660`; service checks `SO_PEERCRED.uid == jarvis-op`.
3. Signer key readable only by `jarvis-op` (or a hardware token); never by the service or `jarvis`.
4. Release directory and imports `root:root 0755`, files `0644`; service has no write access to its own code.
5. Controller, domain, high-water, evidence and backup roots owned by `jarvis-v3`, `0700`; the protected high-water root additionally writable only through a narrow append-only helper (PROTECTED-LINEAGE).
6. Service unit: `NoNewPrivileges`, `ProtectSystem=strict`, `ReadWritePaths=` only the state roots, `RestrictAddressFamilies=AF_UNIX AF_INET` (INET only for the attested endpoints, via `IPAddressAllow=`).

## Disposable test plan (needs separate operator approval; root on a disposable VM, never Core)

1. Create a throwaway VM or snapshot; create `g6f-svc`, `g6f-op`, `g6f-dev` accounts there.
2. Install the candidate read-only as root; run the service under `g6f-svc` with the unit hardening above.
3. Tests: (a) `g6f-dev` and `g6f-svc` connect to the control socket → refused by `SO_PEERCRED`; (b) `g6f-dev` cannot read the signer key, write the release, or write any state root (EACCES); (c) `g6f-op` cannot write state roots; (d) revoked operator (removed from group) → new connections refused; (e) replay/duplicate/stale-binding permits refused across a service restart; (f) chmod the state root during shutdown → final checkpoint becomes forensic/incomplete, never complete.
4. Destroy the VM; keep only the sealed results.
