# Local operator control

Nonproduction Gate 6E reference implementation. No production installation, experiment approval, model traffic, credential use or measurement. G6D-LP-1 remains a proposal.

`local_control.py` handles one bounded length-prefixed canonical packet on an already connected AF_UNIX socket. It reads Linux SO_PEERCRED itself, checks the configured UID and positive PID, rejects oversized/truncated/schema-invalid requests, and passes only signed fixed verbs to Authority. No path, command, shell, arbitrary file operation or public HTTP/WS opening endpoint exists.

Authority binds source/config/release/runtime PID/invocation/boot/start/challenge/epoch, fresh checkpoint, nonce, expiry and exact payload. OPEN_HOLD and AUTHORIZE_ONE are separate one-use records; repeat refusal is durable. Restart starts closed; an aborted terminal epoch never reopens. A signed request cannot substitute identity fields. Kernel socketpair tests exercise the current UID and dummy signer without a listener or installed helper.

IMPLEMENTED, OS QUALIFICATION PENDING. The test UID is the same as Codex's test process; SO_PEERCRED therefore does NOT prove human-only authority. Dummy signer presence is synthetic. Runtime identity values are injected, not independently attested to a supervisor. Future service identity needs narrowly scoped consumer/socket/state access; the human approval path needs a separate protected signer/identity and fixed operation authorization. Neither should grant a general privileged shell/file API. The normal jarvis/Codex UID must lack signer and protected-root write access.

No real helper, user, sudo/polkit/PAM rule, socket unit, systemd reload or credential was installed/read. Provisioning and real privilege separation tests require separate authority. Documentation alone is not enforcement.
