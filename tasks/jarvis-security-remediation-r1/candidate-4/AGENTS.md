# JARVIS task workspace

Run JARVIS work from `/opt/apps/IT TRAINING PROJECT CODE/projects/JARVIS`.
Resolve task artifacts and `tasks/loop-log.md` against this project root, even
when a command or installed helper lives under `/home/nexus`.

Before declaring any task complete, append the required timestamp, Task,
Files changed, Result and Next entry to this project's `tasks/loop-log.md`.
Never append JARVIS task entries to `/home/nexus/tasks/loop-log.md`.
Preserve existing logs; do not move, truncate, rewrite or delete them.

Proxmox Phase 2 is planning and non-destructive validation only until separate
operator authorization: no new ACLs/tokens, guest changes, package installation,
console input, guest-agent execution, power operations or privileged qualification.
Keep VM164 without a NIC. VM162, VM163 and the AI server are outside this task.
