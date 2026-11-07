# Independent timer-clock review v3

## Verdict

`PASS_OFFLINE_HOST_ENFORCEMENT_ENGINEERING_ONLY`

The revised code no longer assumes that `NextElapseUSecMonotonic` is directly
comparable to a `CLOCK_BOOTTIME` deadline. It binds the readback clock domain to
the protected Stage2 prerequisite record and converts a monotonic timestamp by
using paired boot-minus-monotonic clock samples taken around the unit readback.

## Source properties verified offline

- The clock domain is restricted to `CLOCK_MONOTONIC` or `CLOCK_BOOTTIME`.
- Paired samples bound the boot-minus-monotonic offset before and after the two
  unit reads. More than 1000 microseconds of change is rejected as capture skew
  or a suspend during capture.
- A historical suspend offset may be much larger than 1000 microseconds; only
  the uncertainty width is limited. The independent test exercises a 50-second
  offset with a 500-microsecond interval.
- A BOOTTIME readback is retained without conversion and records zero stored
  conversion offsets, after the paired capture itself has passed its skew gate.
- Core verification independently recomputes the normalized interval from the
  raw timestamp and stored offsets, requires the planned deadline to fall in
  that interval, and still checks exact configured `OnBootUSec`.
- The protected, hash-bound Stage2 prerequisite record must name the qualified
  readback domain and assert paired-clock conversion qualification before the
  future native adapter can be authorized.

## Remaining real-host blockers

These source properties do not reveal which domain systemd 257 actually uses
for the selected text readback, prove the exact serialization, or demonstrate
behavior across real suspend, manager reexec, host reboot, timer firing, journal
retention, command failure, or guest shutdown. Those facts require retained raw
Stage2/Stage3 evidence under separate authorization. A mocked conversion is not
evidence that the host timer will enforce a deadline.

Policy A therefore still lacks a strict expiration guarantee. Policy B remains
disabled and unauthorized, and trusted-root bootstrap remains NO-GO.
