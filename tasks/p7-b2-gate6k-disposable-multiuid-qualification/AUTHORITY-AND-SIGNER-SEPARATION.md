# Authority and signer boundaries

Intended disposable root AUTHORITY owns ledger/source/config and narrow fixed-schema transactions. OPERATOR alone among lower-privilege roles owns the ephemeral Ed25519 signing key; authority receives public verification material. SERVICE uses the restricted service interface; AGENT has no administrative authority. Bearer authentication grants no signed OPEN/STOP/succession/permit privilege. Neither client may supply executable callbacks, paths, SQL or shell/Python code.

Root can read any same-host file by design. The test evaluates protection against lower-privilege service/operator/agent, not against root. Separate kernel identities and actual filesystem/socket DAC remain NOT RUN. Existing tests use synthetic signing material only; no real private production credential or key was read/copied/generated.

Spawn and bounded fixed-type JSON IPC retain Gate6J's descriptor and deserialization protections. No lower-role pickle recv is used. The future process-local no_new_privs/seccomp guard denies non-AF_UNIX socket families; no host firewall/policy is changed. No NIC/shared mounts/credentials plus independent human VM verification remain mandatory; a local JSON approval cannot establish that independently.

Protected Python/interpreter/import and artifact ownership must be verified before execution. No service/agent writable code may be imported into root authority. The release extractor and manifest check establish the prepared package bytes; the offline interpreter/OS supply chain is still BLOCKED.
