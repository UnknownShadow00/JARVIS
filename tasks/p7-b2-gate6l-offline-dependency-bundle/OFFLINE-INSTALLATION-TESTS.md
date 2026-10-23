# Offline installation tests

Gate 6L isolated Nexus preparation only. No privileged VM execution or production access.

| Check | Actual result |
|---|---|
|48 new preparation regression tests |48 PASS, 0 failures; no deselections |
|Static Python parsing |All delivered Python tools PASS; no shell scripts |
|109 downloaded wheel structures / RECORDs / identities |PASS |
|43 available PyPI attestations |43 signature verifications PASS;73 acquired releases have none |
|CPython source Sigstore |PASS online and offline with kernel network denial |
|Signed Ubuntu metadata/package/ISO chain |PASS |
|Pure wheel full-resolution attempt |Expected REFUSAL: missing cffi; not a successful full install |
|Closed103-wheel subset |PASS install and pip check; explicitly a subset |
|Mixed route first runtime probe |FAIL missing native _cffi_backend; original evidence preserved |
|Corrected mixed route |127 exact distributions; Python 3.14.4 / SQLite 3.46.1 / cryptography 46.0.5 / seccomp 2.6.0; Ed25519 PASS |
|Fresh copied bundle installation |Five steps PASS |
|Packaged archive extraction and second clean installation |Extraction PASS; five steps PASS; exact native-library origin checks PASS |
|GPUtil offline builds |Two builds byte-identical; source scripts reviewed |
|Wrong hash / path / links / special modes / unexpected packages / ABI versions / library fallback |Negative regression refusals PASS |
|Actual VM boot / four Linux UIDs |NOT RUN |
|Full V3 application suite |NOT RERUN; source unchanged; historical 7741 passed /11 deselected /0 failed preserved |

The installer uses --no-index, --require-hashes, --only-binary=:all:, isolated pip configuration, clean environment and process-inherited seccomp socket denial. It invokes no provider or operational utility. Existing work refuses instead of being erased. All expected failures are recorded distinctly from passes. An early test-harness error expected the wrong rejection when its parent was /tmp; the fixture was corrected to use a private parent. No security assertion was weakened.

Coverage includes malicious tar paths, duplicate/conflicting entries, symlink/hardlink/device/FIFO/setuid/world-writable rejection, hash mismatch, missing/extra files, wrong Python/SQLite/architecture, duplicate/extra/missing distributions, and host-library fallback. Long canonical PAX path metadata is tested because legitimate wheel filenames exceed100 bytes; all other PAX metadata refuses. Whole-host or root compromise is not covered.

Detailed results and failure reproductions remain in the private bundle results/ directory. Task evidence contains minimized logs and selected JSON, not environment dumps or keys.

The original-name Gate 6K flat export failed ARCHIVE_PATH on upstream `+`/`~` filenames. Digest-only evidence aliases fixed this without changing upstream bytes or installation filenames. The unchanged Gate 6K verifier now passes all 131 records. The failed export remains preserved.
