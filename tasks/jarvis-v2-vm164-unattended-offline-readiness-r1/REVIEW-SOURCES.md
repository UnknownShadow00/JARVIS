# Repository sources and evidence interpretation

No external network sources were consulted. The review uses the checked-in/local
retained sources below. Upstream URLs in predecessor documents are historical
references; this sprint does not claim to have refreshed them.

| Source | Use in this review |
|---|---|
| `../jarvis-v2-vm164-trusted-bootstrap-r1/REPORT.md`, `ENGINEERING-REVIEW.md`, `AUTHORIZATION-REQUEST.md`, `OPERATOR-PROCEDURE.md` | Full current preparation policy, operator flow, declared limits and approved-image distinction |
| Same packet `tools/host_guard.py`, `verify_packet.py`, `seal_packet.py` | Host validation, original inventory/seal/verifier scope and external-pin traversal |
| Same packet `payload/BOOT.PY` | Guest identity/cmdline/watchdog/stage/probe/capture/closure implementation |
| Same packet `tools/build_media.py`, `check_media.py`, `decode_probe.py`, `test_bootstrap.py`, `test_generator.py` | Delivery hashes/nonboot structure, capture checks, all existing test boundaries and mock limitations |
| Same packet manifest/seal/external pins and full local file/link inventory | Exact local byte preservation; external `/home` pin contents not opened |
| Same packet `delivery-r4/DELIVERY.json`, `evidence/final-media-inspection-r4.json`, `media-build-9/`, `media-build-10/` | Current approved image and reproducibility; earlier deliveries remain superseded history |
| Same packet `evidence/entry.json`, retained test/syntax/predecessor results, `evidence/generator-tests/RESULT.json` and stock unit | Original operator report, historical test scope, Restart=always/KillMode=process and generator-versus-manager distinction |
| `../p7-b2-gate6k-vm164-disk-matching-r4/ROOT-CAUSE-AND-CORRECTION.md` | Hardware serial versus udev identity lesson; synthetic success is narrower than real installer success |
| `../p7-b2-gate6k-vm164-r4-investigation/ROOT-CAUSE-REPORT.md` | Initialized evidence-disk preservation, early-command limitations, no replay of mutating guards |
| `../p7-b2-gate6k-vm164-installation-timeline/ASSESSMENT.md` | Later installer-ISO reboot explanation and supersession of the immediate blank-disk recommendation; historical uncertainty is not a current observation |
| `../p7-b2-gate6k-disposable-multiuid-qualification/FINAL-REPORT.md` | Same-UID/kernel fixtures versus genuine privileged multi-UID qualification; missing native artifacts and approvals |
| `../proxmox-automation-phase3-review-r1/src/g6k_serial/transport.py` (`GETS`, `observe`) | Earlier reviewed read-only transport explicitly requests `/config?current=1`; no transport/client code was executed |
| `../jarvis-v2-unified-rc1/KNOWN-LIMITATIONS.md`, `AUTHORIZATION-REQUIREMENTS.md`, `release/BUILD.json` | Pinned RC1 scope, synthetic-only transport, deferred production/live requirements |
| `../jarvis-v2-vm164-lab-readiness-r1/REPORT.md`, `BOOTSTRAP-AND-WORKER-BLOCKERS.md`, `INSTALLATION-PROCEDURE.md`, `ROLLBACK-AND-PRESERVATION.md` | Protected installation design, guest/native/worker facts still required, partial preservation |
| Same lab packet `tools/lab_package.py`, `tools/verify_preparation.py`, `tests/test_installation.py` relevant cases | Read-only probe, exact target/approval predicates, manifest/wheel verification, publication/quarantine behavior and verifier scope |
| Same lab packet `BUNDLE.json`, final bundle/manifest, `WHEEL-PROVENANCE.json`, `SBOM.cdx.json`, `ADVISORY-ASSESSMENT.md` | Independently checked local bytes; current metadata gaps; retained advisory findings, not new queries |
| Current user instructions and supplied last state | Authoritative unattended restrictions, stopped-state report, attached r4 ISO and outstanding disk-only correction |

Supersession matters: old incident documents refer to a running failed installer,
and earlier lab preparation calls installed-OS/root access unknown. The current
user reports an installed OS and stopped VM. Both historical evidence and current
report are retained with their actual provenance; none permits a live query here.

The new artifact review verifies all 104 regular files and 5 symlinks of the sealed
bootstrap packet, including superseded builds, without following absolute links.
It parses all 29 retained Python files/copies. The nine new hazard tests import
only the current pinned helper/guard, whose imports perform no action, and replace
manager/guest fact calls with mocks. The original 43 tests were likewise replayed
locally with all service/power calls mocked and temporary paths in this new task.
The native generator, ISO builder, old disk guards, observer, broker transport,
installer/probe entry points and predecessor CLI verifier were not executed.
