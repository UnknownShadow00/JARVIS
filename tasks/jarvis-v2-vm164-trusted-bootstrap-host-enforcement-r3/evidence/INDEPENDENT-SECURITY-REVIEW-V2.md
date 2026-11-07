# Independent security review v2

## Verdict

`PASS_OFFLINE_HOST_ENFORCEMENT_ENGINEERING_ONLY`

The offline candidate now fail-closes at the reviewed code boundaries exercised
by 15 independent mocked tests. This verdict is limited to source behavior and
fixture-backed interfaces. It is not live host qualification or authorization
to boot VM164.

## Findings resolved by code

- Setup failure attempts cancellation for every timer phase whose creation was
  attempted and records unknown/orphaned state instead of allowing a start.
- A pre-action interface failure does not consume the only worker opportunity;
  phase claims are live locks with two durable bounded attempts.
- An evidence failure after claim but before actuation prevents the VM command;
  `ACTION_INTENT` is a strict durable gate.
- Duplicate cleanup and late expiry after authenticated `CLOSED` are historical
  no-ops. `CLOSED` remains absorbing even if later journal records exist.
- Retiring an active registry requires a stopped, closed session, inactive units
  and a distinct finite approval; prior session evidence is retained.
- Host authorization binds source, Stage2 prerequisites, review-record hash and
  non-root Policy A scope.
- Native runtime has no forced-stop command path. Policy B remains rejected.
- Unit verification now reads back and strictly checks UMask `0077`, MemoryMax
  `134217728`, TasksMax `16`, SendSIGKILL, null stdin, journal stdout/stderr and
  a 10-second start timeout in addition to runtime/stop timeouts and command.

## Remaining unverified assumptions

- Mock output cannot prove systemd 257 transient timer creation, absolute
  boot-clock deadlines, firing latency, command execution, manager reexec,
  reboot invalidation, journal retention or property serialization.
- Mock output cannot prove Proxmox 9.2.5 `qm`, `pvesh` or `pvesm` semantics,
  protection/lock behavior, guest ACPI response or absence of another host
  controller during the snapshot-to-action interval.
- Policy A intentionally stops at bounded graceful shutdown and therefore does
  not guarantee expiration. Policy B would require a separately reviewed native
  implementation and explicit data-loss authorization; neither exists here.
- Transient units provide no demonstrated host-reboot enforcement guarantee.

These are Stage2/Stage3 qualification requirements, not offline passes. The
candidate remains NO-GO for trusted-root bootstrap until those stages and a new
finite authorization are complete.
