# Unified RC1 installation readiness — secondary offline review

RC1 stays pinned to `e9b4734740070b9e7c990735e43801e592c114c6`.
No source, dependencies, approval template, release archive or broker candidate
was changed. This review used retained artifacts only; no new advisory query,
package installation, native import qualification, protected installation or
service activation occurred.

## What the current local check establishes

The new artifact review verified the final 23,548,033-byte bundle against
`0c42464637a8ffd1f443f532a087acf0d9a7c48213f9803b4e228aeda5a898ba`,
all manifest member hashes, 315 source entries, 31 wheel artifacts and their
RECORD contents, and the resulting 2,444-file in-memory install inventory against
installed-manifest SHA256
`c2c0047a2d337e4ee98efcfb1a5c79044009c807b8cd10fc4543c1c4309a5e67`.
Nothing was extracted or installed. This is a fresh byte-integrity check, not a
rerun of historical application/rollback/privileged tests.

The retained lab report records 67 installer tests, 210 regressions, 20 application
groups, 71 broker methods/305 subtests and a complete 2,444-file quarantine. Those
remain historical evidence, not additional tests executed by this sprint.

## Ranked remaining gaps

| Priority | Gap and evidence | Later acceptance requirement |
|---|---|---|
| High | Trusted bootstrap/root closure and current target facts remain unqualified; see H1–H5 | Complete a safe separately supervised preflight, then review actual facts; no installation assumption from synthetic PASS |
| High | Bundle includes no OS/CPython/native-runtime installer; `check_target()` pins CPython 3.14.4, SQLite 3.46.1, OpenSSL 3.5.5 and private ext4 | Independently establish signed OS/runtime provenance, protected actual executable/library/bwrap hashes and private rootfs; missing/mismatched prerequisites block |
| High | Root/operator/service/agent custody and actual restricted identities are not proved by same-UID fixtures | Existing qualified nonroot principal, protected ancestry, no inherited privilege/channels, separate approval and actual multi-UID qualification before activation |
| High | Installation approval binds one current boot; bootstrap shutdown destroys that boot context | Fresh same-boot probe/binding, exact destination/package/interpreter pins and finite protected approval immediately before installation; no reuse of debug-boot ID |
| Medium | 45-component CycloneDX schema success is scope/schema assurance; **all 45 entries lack a `licenses` array**, even though wheel provenance supplies expressions for 22/31 wheels | Supplement in a new versioned SBOM: validated license data/retained files and uncertainty; do not rewrite the approved bundle or infer a legal conclusion from missing metadata |
| Medium | 14/31 provenance entries lack the retained `PEP740 signature verified` claim; 9/31 lack a license expression | Preserve hash/RECORD evidence and distinguish archive integrity from publisher attestation/license identification; operator provenance acceptance remains pending |
| Medium | 31 Python wheels plus 13 npm lock-only components plus one dormant broker do not inventory the installed OS/native/full optional graph | Later installed-image/runtime SBOM and native/OS advisory qualification; do not promote the 45-component count to completeness of the VM |
| Medium | Retained advisory snapshot flags certifi and Electron/undici; no fresh lookup occurred here | Keep network/frontend use blocked per retained assessment; any remediation requires a new reviewed release and affected tests |
| Medium | `quarantine()` validates bytes/ownership and renames; it does not independently discover external activation/open processes | Operator must establish never-activated dormant state before using this rollback. A hash-valid tree alone cannot prove it is unused. Activated-state rollback needs its own stop/state/evidence scope |
| Medium | Partial publication is deliberately nontransactional/preserved; the fixed candidate destination is not automatically reusable | Retain partial bytes and failures; review a new destination/approval. No automatic deletion, chmod/chown repair or retry |
| Low | Performance/headroom measured on Nexus is not VM164 capacity | Fresh actual 4-vCPU, >=5GiB RAM/3GiB available and >=20GiB disk headroom; existing 6000MiB planning data does not meet or waive the separate full Gate6K recommendation |

The provenance/attestation/license counts above are fresh local metadata
observations in `evidence/local-artifact-review.json`; they do not independently
verify a publisher's signature or license text. SBOM schema validation was retained
from the earlier packet and not rerun using external tooling in this sprint.

## Native compatibility

The four non-pure wheel filenames are:

- NumPy 2.5.3: CPython 3.14, x86_64, manylinux 2.27/2.28 tags;
- pydantic-core 2.46.5: CPython 3.14, x86_64, manylinux 2.17/2014 tags;
- PyYAML 6.0.3: CPython 3.14, x86_64, manylinux 2014/2.17/2.28 tags;
- psutil 7.2.2: CPython 3.6 stable ABI (`abi3`), x86_64,
  manylinux 2010/2.12/2.28 tags.

These tags and verified bytes do not establish the guest's loader, libc, CPU
features, shared-library resolution, Python build or native provenance. Retained
Nexus dependency/native checks do not establish VM164 compatibility. Exact runtime
version requirements are intentionally conservative; do not substitute the guest's
available version or install a missing package under preflight authorization.

## Clean installation and interruption recovery

The dormant installer creates no service/account/database or activation marker,
does not update a current-release pointer, and uses exclusive descriptor-relative
publication, retained parent handles, hashes, safe ownership/modes and fsyncs.
It rechecks approval/target before writing. Those are useful code-derived controls;
no actual protected guest execution is claimed.

An interrupted tree is preserved and refuses normal exact-inventory validation.
Reusing the same destination refuses. Complete, unchanged, proven-dormant files
may be quarantined under a still-current exact approval; every byte is retained.
Quarantine is not rollback of a running app, a real DB, authority state, services,
tokens or a VM. Physical power-loss/fsync semantics and multi-UID races need their
separate qualification. No real power or crash test was run here.

The private smoke is designed for a no-network namespace, public inputs, synthetic
state and inactive candidate. Its actual namespace enforcement and worker
separation must be measured in the later approved environment; local import or
install success does not waive it. The broker candidate remains dormant, and no
reviewed live JARVIS task-ID-to-broker adapter is supplied by this packet.

Follow-ups are documented rather than silently patched into pinned RC1. New
SBOM/license enrichment, a revised bootstrap helper or dependency remediation
belongs in a new reviewed version with its own artifact identities.
