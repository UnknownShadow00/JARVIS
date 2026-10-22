# Phase B is not authorized

GENUINE MULTI-UID QUALIFICATION: NOT RUN — AWAITING EXACT DISPOSABLE VM AUTHORIZATION.

No VMID, VM UUID, guest machine-id, hypervisor, disk or console session has been approved. No VM was created, accessed or modified. No users/groups/helpers were installed. A local marker is only a record of human authorization, not evidence that a VM is disposable.

Proposed estimates:4vCPU,8GiB RAM,40GiB private ext4 disk, noGPU, Linux x86-64, noNIC, no shared mounts, no production credentials or forwarded agents. At least20GiB free is enforced immediately before fixture creation. These are estimates, not measured minimums. Use trusted management console verification of VMID/UUID/node/disk/guest identity, fresh image provenance, disconnected interfaces, mounts and absence of production attachment. No physical power cuts or snapshot rollback are approved.

`OPERATOR-APPROVAL-TEMPLATE.json` is deliberately invalid until completed. Required: actual machine-id, new nonproduction VMID+UUID, hypervisor node, exact isolated disk identity, operator console/session, exact synthetic no-powercut scope, snapshot/failure-preservation policy, source-manifest digest, archive digest and reviewed dependency-artifact-record digest. Root-owned0600 regular single-link /etc/g6k-disposable-approved.json is read with a bounded no-follow parser; duplicate keys and incomplete/wrong scopes refuse. The record must match a separately retained human approval.

This exact authorization is needed because the user explicitly reserves privileged VM execution to Phase B. Existence of a VM, this task's GO for preparation, an operator marker or silence is not authorization. New source digest requires new approval. The earlier Gate6J digest cannot authorize this revised bundle.
