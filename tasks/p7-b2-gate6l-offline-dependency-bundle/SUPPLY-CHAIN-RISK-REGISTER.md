# Supply-chain risk register

Gate 6L — Nexus-only development evidence. No VM, privileged provisioning, production access, provider generation or pilot activity occurred. Historical Gate 6K source remains unchanged.

| Item | Result / control | Remaining boundary |
|---|---|---|
|67 selected distributions lack stronger publisher signatures | Exact URL/hash/RECORD recorded; GPUtil reviewed and reproduced | Human supplier-risk acceptance; do not call these independently authenticated |
|Python signing root | Sigstore identity+issuer verified, online and offline | Verifier/bootstrap and trust-root policy must be retained independently |
|Ubuntu signing root | Full fingerprints, valid signatures, index-to-package hash chain | Root/host compromise and malicious trusted publisher are outside this proof |
|GPUtil PyPI archive unsafe modes | Rejected; retained without extraction; reviewed tagged source used | Unsigned upstream tag remains weaker provenance; archive SHA pins actual bytes |
|Debian vs PyPI package identity | Same version can have different dependency metadata and bytes | Use exact selected artifacts; no substitution by version string |
|Native CFFI dependency | Failed smoke test preserved; signed backend added; Ed25519 passes | Do not accept metadata-only validation |
|Source archives / installer hooks | Safe extraction rejects paths, links, special entries, unsafe modes;48 focused cases | No privileged extraction or arbitrary package scripts |
|Manifest circularity | Contents → SHA256SUMS → external digest; archive digest retained outside | Human must compare independently retained values before running bootstrap |
|Temporary download failures | Quarantined; retries separately recorded and hashed | Never install partial files merely because a filename exists |
|Complete host rollback | No external trust anchor implemented | Protected authority still cannot prove arbitrary root/host rollback absence |
|OS image and kernel | Signed Ubuntu 26.04.1 ISO acquired; compatible host rehearsal | Actual guest boot, mounts, no-NIC state and four-UID enforcement await approval |
