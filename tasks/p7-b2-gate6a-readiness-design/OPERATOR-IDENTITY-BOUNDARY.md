# Operator authority and OS identity

Codex and the current service can act as jarvis UID1000. A jarvis-owned0700 directory,0600 file, local command, Unix socket or typed acknowledgment does **not** technically distinguish the human from Codex. The previous private-auth helper's human-only use was a workflow boundary, not an OS capability unavailable to that Unix identity. No claim of stronger separation is inherited here.

| Boundary | What it establishes | Limitation |
| --- | --- | --- |
| Workflow authorization | Explicit operator approval tied to a task/release | Same-UID software can disregard a convention |
| File/socket modes under jarvis | Excludes other unprivileged identities | Does not exclude Codex as jarvis or same-UID memory/data mutation |
| Separate privileged operator authentication | Requires credentials/session unavailable to automation | Must actually be provisioned and reviewed; shared root credentials weaken attribution |
| Dedicated service UID + root-owned immutable release | Separates agent from runtime memory/control/storage under ordinary OS policy | Root/kernel/hypervisor remain trusted; dependencies/import paths must also be protected |
| Trusted console/user-presence authentication | Gives the human an independent approval path | .50→Core SSH as jarvis alone does not provide this separation |
| Audit challenge/operator ID | Attributes the privileged approval and exact runtime binding | A recorded name alone is not identity proof; privileged audit integrity is assumed |

Recommended stronger design: a dedicated non-login pilot service identity, a protected system-managed service with Restart=no/autostart disabled, root-owned reviewed code/config/import dependencies, and a root-owned bounded authorization helper callable only after human-exclusive privileged authentication. Codex's jarvis identity must have no general or helper NOPASSWD permission, no operator credential, no service-writable code/import path and no ability to impersonate the service UID. The helper accepts only fixed reviewed manifests/challenges, not shell/URL/path commands.

The existing user manager cannot simply change to another User identity without a privileged supervisor transition. The proposed system service, identity provisioning, D06/backup ownership compatibility and credential provisioning are **new separately approvable changes**. No account/unit/permission was created. Current D06/backup readers check effective UID; ownership changes cannot be treated as a transparent chown or silently reuse old checks. Preserve bytes/associations and qualify the full migration after the authorized service stop.

A service-owned private Unix socket may transport control to the future runtime, but the runtime must require SO_PEERCRED uid0 and the helper must verify the socket peer's dedicated UID/PID/start/boot/invocation against the exact approved supervisor. Nonroot jarvis clients are rejected. Any root process remains in the trusted base; “uid0” is not proof of a particular human. Root helper audit must record the separately authenticated operator/session and explicit approval artifact.

An externally signed grant can strengthen attribution if the signing key and user-presence operation are outside automation, but it does not by itself protect a jarvis-writable runtime/database. Introducing signing/privileged credentials requires its own design and approval; the offline model supplies dummy verified-authority facts and implements neither PAM/FIDO nor cryptography/SO_PEERCRED.

If the operator instead accepts a same-UID workflow-only boundary, that is an explicit weaker-policy decision requiring separate review. It must never be described as technically human-only. This packet recommends the separated identity design.
