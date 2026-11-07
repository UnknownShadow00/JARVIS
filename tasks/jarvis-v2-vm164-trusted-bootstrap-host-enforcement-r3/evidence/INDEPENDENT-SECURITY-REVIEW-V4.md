# Independent security review v4

## Verdict

`PASS_OFFLINE_HOST_ENFORCEMENT_ENGINEERING_ONLY`

The frozen source passed 17 independent mocked security tests under
process-wide tripwires that would fail any `subprocess.Popen` or `os.killpg`
attempt. The independently constructed positive authorization path did not run
`dpkg-query`; it supplied and asserted one exact metadata command through a
mocked `Runner.run` boundary.

## Admission and package binding

Host authorization now requires canonical hash binding of the protected Stage2
record and candidate review record, explicit reviewed record kinds, current
source identity, exact host/kernel data, pinned executable bytes, a complete
Stage2 prerequisite assessment, and exact equality between four protected
package-version pins and the bounded runtime metadata response.

Independent negatives show that a canonically self-consistent synthetic record
kind is still denied, and that changing one protected package version is denied
when the mocked runtime response does not match. The package command is a fixed
argv list with no shell and no caller-controlled package names.

## Source-generation fence

Review found and the candidate fixed a stale-generation gap: an old armed plan
could previously be read by a new source generation because the plan's stored
source hash was not rechecked on action paths. A central `_plan` fence now binds
start, expiry, cleanup, retirement, verification and observation to the exact
session source. CLI also compares the initial source digest with the permit's
post-authorization digest before constructing the backend. The independent
negative verifies refusal before fake VM state changes.

## Budget and callback separation

The CLI creates one absolute boot-clock deadline before host authorization.
Authorization's mocked package query and the later backend Runner both clamp
their local budgets to that deadline; authorization cannot reset the remaining
budget. The installed systemd RuntimeMax remains an outer bound but is not
qualified by this offline review.

The future Stage2 callback is a separate non-root/non-VM script. It rejects root
UIDs, checks its exact public path, root-owned non-writable ancestors, a bounded
single-link regular leaf and caller-supplied exact source hash. It imports no
subprocess or network library and performs no filesystem write. This design is
distinct from the Stage3 root pre-arm selfcheck and grants no VM authority.

## Remaining blockers

No mocked result proves package-manager output on the Proxmox host, systemd 257
serialization or enforcement, transient timer execution, suspend/reexec/reboot
behavior, journal retention, Proxmox command semantics, guest ACPI response, or
exclusive host custody. Stage2 and Stage3 retained raw evidence remain required.
Policy A cannot guarantee expiration; Policy B is disabled and separately
unauthorized. Trusted-root bootstrap therefore remains NO-GO.
