# Dependency status: BLOCKED

Version pinning passes: requirements-versions.txt exactly matches all127 effective distribution versions in dependency-versions.json. Fresh read-only comparison of the current test runtime also matched all127 versions, Python3.14.4 / SQLite3.46.1 / cryptography46.0.5; see evidence/current-test-runtime-versions.json. This does not establish interpreter, wheel, OS image or library authenticity.

The exact missing inventory is `ARTIFACTS-REQUIRED.json` and `evidence/dependency-artifact-status.json`:127 distribution artifacts plus CPython3.14.4, SQLite3.46.1, the reviewed libseccomp.so.2 build and the reviewed Linux x86-64 image. None has been supplied with an independently approved artifact digest/provenance record. No download, package installation, network resolver or version substitution was performed. Existing test-host software is a regression environment, not the independently reviewed offline VM supply chain.

Distinct verification layers:

| Layer | Actual status | Required evidence |
|---|---|---|
| Exact versions | PASS:127 lock entries agree | retained pin files and effective runtime comparison |
| Wheel/distribution bytes | BLOCKED | each exact artifact plus independently retained SHA256 and signed upstream/build provenance |
| Interpreter | BLOCKED | reviewed offline CPython3.14.4 build, build inputs/signatures and artifact SHA256 |
| OS libraries/image | BLOCKED | reviewed offline image and SQLite/libseccomp builds, package signatures/build records and hashes |
| Future VM runtime | NOT RUN | actual interpreter/SQLite/crypto/imported distributions and OS-library build readback |

The list includes Ubuntu/system packages such as python-apt3.1.0+ubuntu1.1, python-debian1.0.1+ubuntu2, command-not-found0.3, ubuntu-drivers-common0.0.0 and ubuntu-pro-client8001. Do not assume that all127 are installable PyPI wheels or issue the historical blanket pip-install command. An operator must provide a reviewed offline image/environment that reproduces these exact effective versions, or explicitly approve a separately reviewed dependency correction with new source identity. No correction is silently selected here.

`offline_artifacts.py` verifies the hash of a separately retained ARTIFACTS.json record, exact inventory/version schema, bounded regular non-writable files, file hashes and provenance references. Its synthetic positive/tamper/missing-record tests pass. References and hashes alone are not independent authenticity; the operator must verify original signatures/build chain outside the VM. The future runner requires this record at /opt/g6k-offline, its digest in exact VM approval, and still checks actual runtime versions. It does not install artifacts or claim their contents are trustworthy merely because their version strings match.

No complete offline installation command can truthfully be supplied until those actual artifacts and OS packaging/build layout are provided. This is an external dependency blocker, not a reason to enable networking. Stop this branch; retain the prepared validators and exact missing-artifact inventory.
