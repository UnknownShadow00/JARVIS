# Bounded input and command contract

`src/bounded.py` checks regular type, link count, owner, nonwritable mode and advertised size before reading. Privileged callers use protected directory descriptors: no symlink traversal, root:root and nonwritable ancestry. Reads use bounded chunks, an aggregate ceiling, a monotonic deadline and exact expected size; identity is rechecked after reading. Partial chunks continue; premature EOF, growth, metadata change, digest mismatch, allocation failure or timeout fail. No output or exception echoes file contents. Metadata inspection reports leaf symlinks without following them; resolved executable paths must be independently approved before hashing.

Policy/plain manual input is at most 1 MiB. Compressed manuals are at most 1 MiB before decompression; output is at most 8 MiB and 128 times compressed length. GzipFile is consumed through bounded reads, including CRC/trailer checks and the aggregate bound across concatenated members. Malformed/truncated data and bombs fail. Binary hashing permits at most 32 MiB. Large inputs are refused rather than silently sampled. The retained 2,441-byte pinned callback is unchanged; its non-root read is bounded by its own source check plus service limits, not presented as the new privileged reader.

Future Python inspection/install commands have RLIMIT_AS=128 MiB, RLIMIT_CPU=3 seconds and RLIMIT_NOFILE=64. The exact first R01 is preserved byte-for-byte and therefore uses the recorder's process/resource limits rather than changing its body. `/proc` and cgroup virtual files have bounded streaming readers; regular-file st_size is not misused for those virtual files. Process scan maximum: 8,192 entries, 64 KiB per status, 8 seconds internally. Cgroup files: 64 KiB each, 3 seconds internally.

| Operation | Client timeout | stdout ceiling | stderr ceiling | Kill/reap reserve |
|---|---:|---:|---:|---:|
| Read-only preflight, clocks, metadata, ACL, hashes, versions | 10 s | 1 MiB | 64 KiB | 2 s |
| Manual decompression | 10 s | 8 MiB | 64 KiB | 2 s |
| Exclusive callback installation | 20 s | 1 MiB | 64 KiB | 2 s |
| systemd-run create / deliberate duplicate | 5 s each | 1 MiB | 64 KiB | 2 s |
| Exact systemctl show | 5 s | 1 MiB | 64 KiB | 2 s |
| Exact case journal | 10 s | 8 MiB | 64 KiB | 2 s |
| R22 owned cgroup | 5 s | 1 MiB | 64 KiB | 2 s |
| Exact owned timer or service stop | 5 s each | 1 MiB | 64 KiB | 2 s |

Every external command requires null stdin, no shell, no prompt and the minimal environment in SECURITY-REVIEW.md. `command_envelope` admits a command only when both UTC and BOOTTIME leave its entire cap plus two seconds; it never extends the authorization or converts a timeout into evidence. Python limits are in addition to output/time bounds. A mandatory independently reviewed console recorder must enforce them; this packet deliberately contains no host command executor. If that capability cannot be established, the session cannot start.

Record exact argv, stream bytes (or incomplete partial bytes), exit code/signal, start/end clock evidence, timeout/overflow flags and the console receipt. A timed-out command is FAIL/UNKNOWN even if partial stdout resembles success. Interrupt only the recorder's known client process; no PID scanning or unrelated signaling. A lost systemd-run acknowledgement may leave a timer armed: preserve the pending ownership record, do not retry the name, and reconcile exact owned units. Killing the client does not cancel a manager transaction or undo filesystem writes. Uninterruptible kernel operations and failed managers preclude guaranteed expiration.
