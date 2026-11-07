# Unified release outputs

- REPORT.md — unified decision, source identity, actual results and limitations.
- release/BUILD.json and release/*.tar.gz — reproducible committed source archive,
  exact315-file manifest and31-package offline lock.
- SOURCE-REVISION.json, SOURCE-SHA256.json, SOURCE.patch — exact revision/bytes.
- BASIS.json, INITIAL-STATE.json, reconciliation-diffs/ — original candidate
  identities, dirty-tree preservation and exact alternative differences.
- INTEGRATION-MATRIX.md/.json —408 file-by-file decisions and hashes.
- RESULTS.json, TEST-INVENTORY.json, TEST-OUTCOMES.json, runs/ — actual unique
  tests, exclusions and every accepted/unsuccessful run input/output.
- SECURITY-SELECTED-RESULTS.json, SECURITY-PINNED-INVOCATIONS.json, agents/ —
  selected179-case repeat, socket fixture, four shared-history groups, dependency
  validation and bounded raw audit attempts.
- SYNTHETIC-DEMONSTRATION.md and *DEMONSTRATION.json — actual joined application
  lifecycle, execution, recovery, witnesses and inert restoration.
- CRASH-RECOVERY.json, *BENCHMARKS.json —37 fresh crash observations and13 benchmarks.
- INDEPENDENT-SECURITY-REVIEW.md, INDEPENDENT-REVIEW-PINS.json,
  SECURITY-CROSSWALK.md — independent review,39 exact pins and negative coverage.
- DEPENDENCY-CONFIGURATION.json, SECURITY-DEPENDENCY-SHA256.json,
  STATIC-CHECKS.json, WARNINGS.json, SECURITY-WARNINGS.json — qualified dependency,
  configuration, narrow static checks and explicit advisory/tool limitations.
- KNOWN-LIMITATIONS.md, AUTHORIZATION-REQUIREMENTS.md,
  LIVE-READONLY-PROPOSAL.md/.json — blocked installed facts and exact later scope.
- PREDECESSOR-SHA256.json, PREDECESSOR-SYMLINKS.json — preservation of177,460
  existing task files and original links, with append-only canonical log handling.
- COMPLETION-LOG.json, FINAL-VERIFICATION.json, SHA256SUMS — canonical task log
  binding, final verifier output and sealed artifact inventory.
- REPRODUCE.md, replay.py, verify_release.py — isolated fresh-packet replay and
  read-only archive/evidence verification.

The canonical shared source and both predecessor candidates were preserved.
The merged application is the clean exclusive sibling JARVIS-unified-rc1, at the
revision in SOURCE-REVISION.json, and the immutable source archive. Task links
resolve in the canonical evidence workspace/companion. Nothing was deployed.
