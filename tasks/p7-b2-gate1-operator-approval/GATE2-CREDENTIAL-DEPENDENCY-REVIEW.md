# Gate 2 credential dependency review — PREPARED, NOT APPROVED

Inspection UTC 2026-10-09T02:56:42Z; canonical jarvis@192.168.0.162. This review grants no permission or provisioning authority. Follow the unchanged [AUTH-PROVISIONING-GUIDE.md](../p7-b2-supervised-deployment-staging/AUTH-PROVISIONING-GUIDE.md), SHA256 `32b5c948ebe15ebbb38d2917507772667bafd91b27b91ce59039c404dcd566b7`, only after a separate explicit Gate 2 decision.

## Exact proposed restriction

| Object | Observed | Proposed later action |
|---|---|---|
| /home/jarvis/.config/jarvis | Directory0775, jarvis:jarvis uid/gid1000:1000, no symlink or access/default ACL xattrs | Restrict this directory alone to0700; preserve owner/group |
| /home/jarvis/.config/jarvis/jarvis.env | Only existing child; regular file0600, jarvis:jarvis, no symlink/ACL | Preserve bytes, ownership and0600 |
| /home/jarvis/.config/jarvis/p7-b2.env | Absent | Later human-only hidden input, exclusive O_EXCL/O_NOFOLLOW0600 create and fsync, as the guide specifies |

The proposed directory command is `chmod 0700 -- /home/jarvis/.config/jarvis`, **NOT RUN**. No recursive chmod, chown, ACL edit or change to /home/jarvis/.config, JARVIS/data or any other parent is proposed. Reverify metadata and dependencies immediately before a separately approved change. Any existing credential target, symlink, ownership drift or new dependency means stop and review.

Changing0775 to0700 preserves jarvis owner's read/write/traverse rights and removes group/other directory listing/traversal and group write. Existing0600 file permissions are unchanged. Root/privileged access is not prevented. This is local access restriction, not per-person authentication.

## Installed dependencies and impact

Only installed consumer found: /home/jarvis/.config/systemd/user/jarvis.service line9, with EnvironmentFile=/home/jarvis/.config/jarvis/jarvis.env. Its default.target.wants/jarvis.service link resolves to the same unit, not a second service. This is jarvis's user-manager service; User and Group overrides are empty. Owner jarvis retains access under0700, as does privileged root. No service reload or restart is necessary to apply the directory mode alone.

The directory contains no other file or subtree. Group jarvis has no supplementary members and its only primary-group user is jarvis. No external symlink into the credential directory and no other installed unit, inspected scheduled job or inspected executable script references it. Repository matches outside that unit are historical task documents and proposals. Therefore **no other operational dependency was identified that would lose required access**. Other users currently able to list/traverse0775 would lose that access; this is the intended restriction. No claim is made that undiscoverable or future consumers do not exist.

Coverage: 1192 readable files across tracked canonical repository files; jarvis user units; /etc/systemd/system and /usr/lib/systemd/system; /etc/crontab and cron.d/daily/hourly/weekly/monthly; /home/jarvis/bin and ~/.local/bin where present; and shell startup files. No unreadable file was encountered in this scope. jarvis has no user crontab. No inspected process has an open descriptor into the directory. /proc descriptor access for 126 other-user processes was denied; those processes' descriptors were not inspected, and no sudo escalation or secrets inspection was used. Unregistered scripts, other users' private jobs and arbitrary applications outside the inspected scope remain an explicit evidence limit.

Raw metadata and filename/line-number-only references are in [CREDENTIAL-DEPENDENCY-REVIEW.json](CREDENTIAL-DEPENDENCY-REVIEW.json). No token, token hash, credential contents, environment dump or process command line was captured.

## Separate human decisions required

1. Approve or reject restricting exactly /home/jarvis/.config/jarvis from0775 to0700 while preserving uid/gid1000:1000 and existing jarvis.env0600.
2. Approve or reject the unchanged guide's human-only private provisioning of p7-b2.env0600. The token must never enter Codex, chat, Git, evidence, arguments or logs. Existing or partial targets are retained for explicit review, not overwritten.
3. If desired in a later authorized preparation step, explicitly approve the guide's proposed /home/jarvis/.config/systemd/user/jarvis.service.d/p7-b2.conf, parent0700/file0600, additional EnvironmentFile, UMask0077 and Restart=no. Nothing is installed now.
4. Name any daemon-reload or LEGACY auth-verification service window separately. Such operations, SHADOW activation, D06 provision and traffic are not implied by a directory/provisioning approval.

This task stops at Gate 1. Gate 2 and each later gate require separate explicit approval; the current review is ready for that decision and performs none of its changes.
