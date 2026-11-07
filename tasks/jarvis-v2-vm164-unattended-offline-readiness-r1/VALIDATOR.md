# Offline validator contract

`tools/state_validator.py` evaluates local synthetic or saved JSON. It never
connects to Proxmox, calls a command, imports a payload, reads credentials or
writes a file. JSON receipts go to stdout. Exit 0 means offline consistency only;
exit 1 means refusal. Even exit 0 includes false live/authorization/Gate6K flags.

Run the retained **synthetic** corrected-boot example from the project root:

```sh
python3 -I -B -S tasks/jarvis-v2-vm164-unattended-offline-readiness-r1/tools/state_validator.py \
  --bundle tasks/jarvis-v2-vm164-unattended-offline-readiness-r1/fixtures/attached-restored-boot.json \
  --as-of 2026-11-06T18:00:30Z
```

This uses a fixed replay clock and proves no current VM state. Omitting `--as-of`
uses the local UTC clock; old fixtures should then refuse as stale. A manually
chosen recent clock still cannot turn saved evidence into a live check. Optional
`--expected-digest` compares the latest opaque PVE digest to an independently
supplied expected string; it does not compute PVE's digest algorithm or authorize
a management command.

## Envelope and raw evidence

[fixtures/attached-restored-boot.json](fixtures/attached-restored-boot.json) is the
complete shape. `format` is `vm164-offline-evidence-v1`; `kind` must be `synthetic`
or `saved_readback`. `session_reference` is a bounded public identifier, not an
approval. No `live`/`attested` source label is accepted.

Each snapshot supplies a unique ID, procedural state, asserted node pve/VM164,
UTC start/end, previous snapshot hash (null at entry), exact config digest,
`readbacks` and an ISO observation. Each readback contains:

- `raw`: original UTF-8 JSON text, including its original whitespace/newlines;
- `sha256`: SHA256 of those original UTF-8 bytes;
- `captured_at`: strict UTC `YYYY-MM-DDTHH:MM:SSZ`;
- `endpoint`: exact asserted current-config, status/current or pending endpoint.

Original raw files must be retained separately; the envelope is a transport
representation, not a replacement custody record. Exact endpoint strings are
`/nodes/pve/qemu/164/config?current=1`, `/nodes/pve/qemu/164/status/current`, and
`/nodes/pve/qemu/164/pending`. The explicit query requirement avoids assuming a
default config view; actual installed query support/semantics remain supervised.
No command to acquire evidence is implemented.

Attached snapshots require `iso_verification` with the fixed volume, full SHA256,
196608 bytes, observation time, and `config_readback_sha256`. This is an explicitly
supplied host-volume observation, not proof that this tool read that volume. An
attached name cannot establish byte identity. Detached snapshots require null.

The config requires explicit identity/name, scsi0, ide2, boot, onboot, agent,
serial0, vga, hotplug, protection, digest, cores/sockets/memory/balloon. A host
that omits a default does not automatically satisfy it; preserve its raw output
and review the schema instead of silently synthesizing the field. No defaults
are invented. Fixed disk serial/size/volume and unique option keys are checked.
Unexpected config keys fail closed, including extra devices and future options.
Optional recognized metadata also remains unchanged across transitions.

Pending may be empty or contain unchanged `key/value` rows matching current
config exactly. Duplicate/malformed rows, unknown fields, any `pending`, `delete`
or `deleted` key (even null/false), or mismatched current values refuse. This is
a conservative accepted subset, not a claim to implement every PVE version's
schema. It intentionally cannot approve clearing pending operations.

## Sequence and time policy

Allowed success-path progression:

```text
initial_empty (optional stopped entry)
  -> preflight_attached (stopped; also allowed as chain entry)
  -> debug_attached (running)
  -> debug_empty (running)
  -> closed_empty (stopped)
  -> clean_running (running)
  -> final_empty (stopped)
```

Repeated fresh observations of the same state are allowed. Reversal, skipped
states or arbitrary post-entry transitions refuse. Failure/recovery paths must
be recorded separately for operator review; they cannot be relabeled success.
These labels assert intended procedural position. Config/status cannot prove a
debug shell, successful cleanup or clean login; every accepted receipt expressly
leaves those checks false. No guest read is performed.

Previous hashes are SHA256 of the prior snapshot's canonical JSON: sorted keys,
compact separators, ASCII escaping, no NaN/Infinity. Original readback hashes
remain over original bytes. All config fields except ide2/digest must match
between steps. Digest must change when media changes and remain identical when
config does not. This is a strict consistency policy, not host authentication.

Policy bounds: 1–32 snapshots; at most 2MiB input; strict regular non-symlink,
single-link file; no duplicate JSON keys or nonfinite numbers; at most 30 seconds
per capture; every readback inside that span; strictly increasing nonoverlapping
captures; latest capture starts at most 120 seconds before reference time; history
at most one hour old; supplied ISO observation at most 120 seconds before its
capture ends. These are conservative engineering defaults, not additions to an
operator's authorized window. They never extend that window or the watchdog.

## Limits

This validator cannot discover missing snapshots, later changes, false origin,
invented timestamps, credential misuse, hidden host state, atomicity, actual ISO
bytes, guest media presence, timer deadlines, cleanup or persistent root access.
Config digest is concurrency metadata, raw SHA256 is integrity metadata, and a
hash chain is consistency metadata. All need independent operator custody and
fresh acquisition. Its receipt is never an instruction to act.

The official r1 guard remains untouched and must still run in the approved
procedure. A stricter supplemental refusal must be reviewed, not bypassed by
using the older guard's broader acceptance. Tests and fixtures are exclusively
offline, including the apparently successful running/ejected sequence.
