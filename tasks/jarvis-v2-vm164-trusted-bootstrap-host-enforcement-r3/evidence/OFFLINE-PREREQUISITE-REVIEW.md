# Offline prerequisite review: systemd timer and Proxmox command assumptions

Date: 2026-11-06  
Scope: local retained documentation and r3 source only; no network, Proxmox,
VM, service-manager, timer, or `qm` command was used. The local documentation
host is not the operator-reported Proxmox host.

## Conclusion

The absolute `OnBootSec` construction itself is supported by the local manual:
an `OnBootSec` value is a duration measured from machine boot, so computing
`CLOCK_BOOTTIME-at-arm + 540s/600s` and passing that absolute boot-relative
duration does **not** require an additional service-manager-start offset. A
literal `540s` or `600s` would be wrong once host uptime exceeds those values
and would immediately elapse. `OnStartupSec`, not `OnBootSec`, is relative to
service-manager startup. The documented container-only mapping of system-manager
`OnBootSec` to `OnStartupSec` is not evidence about the reported bare Proxmox
host and must not be silently assumed to apply.

However, the proposed claim that configured `OnBootUSec` and
`NextElapseUSecMonotonic` are read back in the same `CLOCK_BOOTTIME` domain is
**refuted by the retained D-Bus manual**. It specifies that the third member of
each `TimersMonotonic` tuple and `NextElapseUSecMonotonic` are timestamps in the
`CLOCK_MONOTONIC` domain. Separately, `systemd.timer(5)` says
`WakeSystem=yes` changes the timer's operational clock to `CLOCK_BOOTTIME`.
Consequently:

- strict equality of the configured `OnBootUSec` offset to the planned
  boot-relative deadline is a reasonable fail-closed check, subject to proving
  systemd 257 serialization;
- strict equality of `NextElapseUSecMonotonic` to that same boot-relative
  deadline is not justified by the documentation when the host has accumulated
  any suspend time;
- a successful synthetic fixture with equal values does not prove the real
  conversion or the systemd 257 output format.

The current check fails closed rather than authorizing a start when this
assumption is false, but it can reject a correctly armed timer. It therefore
cannot be marked qualified offline. Stage 2 must establish the exact systemd
257 property serialization and clock conversion before any Stage 3 use.

## Source-path findings

- `src/host_adapter.py:38`: `Clock.us()` reads `CLOCK_BOOTTIME`.
- `src/model.py:165-170`: `armed_us`, `grace_us`, and `deadline_us` are built in
  that clock domain and are bound to the current boot ID.
- `src/systemd_codec.py:59-66`: `timer_command()` renders the resulting absolute
  microsecond value as `--on-boot=<seconds.microseconds>s`, with
  `WakeSystem=yes`, `AccuracySec=1us`, and `RandomizedDelaySec=0`.
- `src/systemd_codec.py:43-50`: the parser assumes an exact human-readable
  `TimersMonotonic={ OnBootUSec=... ; next_elapse=... }` serialization.
- `src/model.py:146-147`: `verify_unit()` requires both parsed `OnBootUSec` and
  `NextElapseUSecMonotonic` to equal the boot-relative deadline exactly.
- `tests/test_host_adapter.py:19-25`: the fixture assigns identical values to
  both properties, so it models the disputed assumption rather than testing a
  real manager conversion.
- `src/preflight.py:20-25`: the design correctly leaves
  `systemd_show_codec_qualified`, `boottime_deadline_readback_qualified`,
  `wake_system_qualified`, manager-reexec, reboot, and journal behavior as
  mandatory supplied Stage 2 facts.

Current source hashes at review time:

| File | SHA-256 |
|---|---|
| `src/systemd_codec.py` | `96860f80fd6898885998bf908f7611e2194042cbefccf56feb9d254da9a57def` |
| `src/model.py` | `08d86156598a073aefdae124485d11fd6977da4278733a97b0453dcf32b3c3ef` |
| `src/host_adapter.py` | `7e205a681dc141dcaf803a63b821410a70499954fc39276f8c0a3098eaa4193a` |
| `src/preflight.py` | `6bd10797e8e2adce907cf19422ae92ef0d668b9daba9d19ccf52174aa31410b2` |
| `src/stage2_canary.py` | `a286871438f52760f1b9872d301b6782b1f8e55686cbe1980d210ee3ff5462aa` |

These are review-time hashes, not a new release manifest.

## Retained primary documentation

The local package is `systemd 259.5-0ubuntu3.4`, not the operator-reported host
version `257 (257.13-1~deb13u1)`. These manuals provide offline design evidence
but cannot prove exact behavior or serialization on that host.

| Local manual | SHA-256 | Relevant retained statement |
|---|---|---|
| `/usr/share/man/man5/systemd.timer.5.gz` | `876019cee4eeb45fbcf5f449b16efcc0d6330747f878a8738243de81cc9d363d` | `OnBootSec` is relative to machine boot; past values fire immediately; `WakeSystem=yes` selects `CLOCK_BOOTTIME`; `AccuracySec=1us` is the documented highest-accuracy setting. |
| `/usr/share/man/man5/org.freedesktop.systemd1.5.gz` | `e8dff008d5581b8fffabbe74a19e121f4db708f01997cabfa1af598dc031bf09` | `TimersMonotonic` is `a(stt)`; its next-elapse member and `NextElapseUSecMonotonic` are documented in `CLOCK_MONOTONIC`. |
| `/usr/share/man/man1/systemd-run.1.gz` | `7d2d03b82f9ca9817d02b830357af875cb4201cc5f28723fca36a8e2e9020636` | With timer options, the timer starts immediately and triggers the service later; `Type=exec` detects `execve` failure when the service starts, not when only the timer is armed. |
| `/usr/share/man/man5/systemd.service.5.gz` | `3293c11ca405a7be1860004fd4ea5f93be5565900398bc14f59135c1daf83db7` | `Type=exec` reports process setup/`execve` failures but not failures in the program's own initialization. |
| `/usr/share/man/man1/systemctl.1.gz` | `a71be5f8afe4e7d9dddbce8b346ae5fe9cc75f76891cc2a27caf1eb823646bef` | General `show` interface; it does not establish the candidate parser's exact systemd 257 compound-value text. |
| `/usr/share/doc/systemd/TRANSIENT-SETTINGS.md.gz` | `d07e5759d91ad4da3d59ada92de99bc1eec4e104bfd14f6b1a9bf480e778d9ff` | Lists transient support for `Type`, timeouts, `WakeSystem`, `RemainAfterElapse`, accuracy/randomization, `OnActiveSec`, and `OnBootSec`. |

## What is established offline

1. `OnBootSec` is boot-relative, not timer-activation-relative or
   manager-start-relative. No nonzero manager offset is called for.
2. Past `OnBootSec` values fire immediately, validating the future-deadline
   check and rejecting literal 540/600-second values at normal host uptime.
3. `WakeSystem=yes` is the documented selector for a suspend-advancing timer
   clock.
4. Boot-ID binding is necessary because a reboot changes the relevant clock
   epoch. The manuals do not make a transient monotonic timer a durable reboot
   fence.
5. Creating and observing an active timer is not proof that its service can
   execute at expiration. `Type=exec` provides useful execution failure
   reporting only when service activation occurs.
6. `TimersMonotonic` and `NextElapseUSecMonotonic` exist in the documented
   D-Bus interface, but the exact `systemctl show` text consumed by the r3 codec
   is not specified as a stable wire format in the retained manuals.

## Mandatory Stage 2 evidence

Stage 2 should remain a separately authorized, non-VM qualification and must
retain raw, hashable evidence rather than boolean assertions alone:

1. Exact host boot ID, systemd version, binary custody/hashes, and paired
   `CLOCK_BOOTTIME`/`CLOCK_MONOTONIC` readings immediately around timer arming.
2. The exact allowlisted `systemd-run` argv, exit status, unit names, and
   timestamps for a harmless non-VM callback.
3. Raw `systemctl show` bytes for every property in `TIMER_PROPS` and
   `SERVICE_PROPS`, captured at least twice while waiting, plus parser result.
   This must prove the exact systemd 257 `TimersMonotonic`, `ExecStart`, duration,
   and boolean serialization. A hand-authored fixture is insufficient.
4. Explicit comparison of configured `OnBootUSec`, exposed
   `NextElapseUSecMonotonic`, and the measured boot-minus-monotonic clock delta.
   Qualification must not presume those timestamps are identical.
5. Observed firing no earlier than the intended boot-time deadline, including
   callback `Type=exec` success and an intentional exec-failure case.
6. Timer/service states and results before firing, after success, and after
   failure; cancellation, duplicate-name collision, rearming, and retained
   journal/receipt behavior.
7. Separately supervised manager-reexec and host-reboot behavior. Until those
   tests are authorized and pass, a reboot or service-manager restart during an
   active session remains a blocker, not an expiration guarantee.

Merely creating a timer, reading `active/waiting`, or running a separate canary
does not prove that the expiration worker will execute successfully.

## Proxmox command-interface uncertainty

No local `qm(1)` manual, `qemu-server`/`pve-manager` source, or matching
Proxmox package documentation was found in the retained offline environment.
Therefore this review cannot establish that Proxmox 9.2.5 accepts or implements
the candidate's exact `qm shutdown 164 --timeout 15 --forceStop 0` contract, or
how protection and locks affect shutdown/stop tasks. The absence of any
allowlisted `qm stop`, `--skiplock`, unlock, or protection-bypass path is a
positive source property, but it is not command-interface qualification.

Stage 2 requires an approved read-only capture and independent review of the
exact host's `qm` help/manual and package versions. Stage 3 is required to prove
VM164-specific task behavior, task completion readback, timeout behavior,
protection/lock handling, and the race with natural guest poweroff. No forced
stop is authorized or implemented by this evidence review.

## Offline verdict

`NO_GO_LIVE_HOST_QUALIFICATION_PENDING`

The absolute boot-relative deadline design survives offline review without an
extra manager-start offset. The same-domain equality assumption does not. The
candidate remains correctly gated by Stage 2 prerequisites and must not be
described as live-qualified, expiration-guaranteeing, temporary-root-ready, or
VM164-installation-ready.
