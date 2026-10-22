# Kernel identity results

GENUINE MULTI-UID QUALIFICATION: NOT RUN — AWAITING EXACT DISPOSABLE VM AUTHORIZATION.

Current unprivileged preparation/extraction ran as Nexus UID1000. A fresh disposable child kernel probe also passed: no_new_privs=1; AF_INET, AF_INET6 and AF_PACKET socket creation denied with PermissionError; AF_UNIX usable; UID unchanged. This is real per-process OS restriction evidence, not UID separation. No connection was attempted and no host policy changed; see evidence/kernel-runner-probe.json. Isolated Core unit tests use the existing jarvis identity inside private ext4 test stages with kernel write/network restrictions. These identities were not used as simultaneously separated operator/service/authority/agent principals. No genuine multi-UID or privileged VM result exists.

Future role model: AUTHORITY=root; OPERATOR=g6j-operator; SERVICE=g6j-service; AGENT=g6j-agent. Measure actual UIDs/GIDs/PIDs and private groups. Reject root/non-distinct role UID/GID, login shells and supplementary administrative/shared groups. No sudo or policy changes. Kernel DAC tests must attempt write/truncate/chmod/unlink/rename/link, key reads and socket directory replacement; only actual PermissionError counts as the expected denial. Missing files and other errors fail the test.

Prepared existing workflow tests valid signed operations and real peer enforcement across these principals, operator/service/agent storage and key denials, immutable import-file denial and retained-root rollback. Gate6K adds invalid/expired signatures from the otherwise permitted operator peer and service socket mutation denials. These future additions are code-reviewed/static-tested but have NOT executed across distinct UIDs.

Every real-UID requirement is NOT RUN in evidence/qualification-matrix.json. A successful same-UID logical test or a refused setup cannot fill those entries. A future PASS must reference the actual kernel/process evidence for each requirement, not only an aggregate runner exit.
