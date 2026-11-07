# Exact remaining guest bootstrap and worker boundaries

Current VM164 guest state is UNKNOWN to this sprint. Historical records include an
initialized incident disk, an automatically failed r4 early-command and unresolved
installer-completion/first-boot evidence. Later host-side disk-only boot metadata
is not guest boot or trusted-root proof. The current observer authentication failed.
Never rerun the old disk guard (it writes), infer a virgin disk, retry autoinstall,
replace media, repair boot, unlock root or use a guest agent to close that gap.

Before protected application installation: trusted installed Ubuntu26.04.1 root
context, original VM/disk identity, current machine/boot/rootfs UUID/device, signed
OS/runtime provenance and root protection, native library/bwrap identity, private
mounts/no external channels, existing restricted lab principal, measured headroom,
approved offline code delivery and independently retained package/tool hashes.
The package requires4 vCPUs, actual RAM at least5GiB with3GiB available,20GiB free
on the existing64GiB private ext4 target. Historical6000MiB is a headless bounded-
smoke planning input, not a fresh capacity PASS or a change to the separate8GiB
Gate6K/full127-package recommendation. No VM resize, package install or mount/
propagation change is authorized or performed.

Before installing an operational serial worker: independently bind the actual
existing/fresh-approved locked nonroot g6k-bridge UID/GID, root-controlled exact
reviewed13-file source at /opt/g6k-serial, root-protected disabled worker config,
private audit custody and installed unit hashes. ttyS0 must already be exclusive,
private and owned by the worker; no getty, kernel/early console, root autologin,
debug shell or competing serial attachment. The prepared metadata checker never
opens ttyS0 and never calls systemctl. Missing facts remain failures; no automated
account/group/chown/bootloader/service repair is included.

Before any broker activation: actual restricted caller without sudo/docker/lxd/
polkit/ptrace/privileged FDs, distinct broker/worker principals, independent protected
finite-grant/key/token/CA/time/revocation custody, preissuance no-transport canary
acceptance, exact effective separated VM.Audit+VM.Console at /vms/164 only, actual
TLS/PVE schema/service/egress/device/seccomp/DAC controls, durable audit and stop/
revoke acceptance. The current Audit-only observer is unchanged. The staged setup
in ../proxmox-automation-phase3-review-r1/APPROVAL-PACKET.md is still an unexecuted
separate request; original Phase3 source is superseded by that reviewed successor.

The bundled serial-candidate is dormant review material. JARVIS RC1 accepts only
its signed synthetic transport, not this live broker. No reviewed UUID-to-32-hex
broker request bridge or real adapter exists. Those are separate integration work,
not configuration switches. Metadata checks, synthetic receipts, restored approval
and one identity-only broker window do not authorize real application execution.

Privileged Gate6K qualification remains NOT RUN. It needs independently reviewed
identity-bound installed manifests/final marker, actual root/operator/service/agent
separation, native/runtime/storage and mount-policy evidence, exact privileged
commands/targets/negative controls, bounded window and stop/preservation scope.
Nothing in this packet creates that marker or waives those gates. Production,
providers/models, VM162, preserved VM163, AI server and V3 remain untouched.
