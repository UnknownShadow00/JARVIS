# Delivery index

- REPORT.md / RESULTS.json — current scope, measured results and blocked live gates.
- BUNDLE.json — exact final delivery archive/tool/install-manifest identities.
- The directory named in BUNDLE.json — reproducible source/wheel package and exact manifest.
- tools/lab_package.py — standalone verify/probe/install/validate/quarantine tool.
- tools/smoke_runner.py / tools/worker_preflight.py — future installed synthetic
  runner and read-only dormant-worker metadata checker.
- tools/observer.py / evidence/observer-classified.json — unchanged GET-only
  observer and current401 result with no secret output or mutation.
- INSTALLATION-TEST-RESULTS.json / SMOKE-INVOCATION.json / BROKER-TEST-RESULTS.json /
  FULL-ROLLBACK-RESULT.json / runs/ —67 install tests,210 app cases/20 groups,
  71 broker methods/305 subtests, and complete2,444-file quarantine verification.
- WHEEL-PROVENANCE.json / SBOM.cdx.json / SBOM-VALIDATION.json /
  ADVISORY-RESULTS.json / ADVISORY-DETAILS.json / ADVISORY-ASSESSMENT.md —31 exact
  wheels,45 SBOM components, current advisory findings and explicit scope limits.
- BROKER-RECONCILIATION.md/.json — original12 vs reviewed13 files and RC1 pins.
- INSTALLATION-PROCEDURE.md / ROLLBACK-AND-PRESERVATION.md /
  BOOTSTRAP-AND-WORKER-BLOCKERS.md / RESOURCE-REVIEW.json — exact procedures,
  preservation controls and measured/unknown resource/bootstrap facts.
- AUTHORIZATION-REQUEST.md / approval.example.json — one next preflight decision
  and a separate null-filled future protected-install template; neither is approval.
- REPRODUCE.md / tools/verify_preparation.py / SHA256SUMS / SYMLINKS.json — safe
  verification/replay, exact artifact/link inventories and predecessor preservation.
- DRAFT-CANDIDATES.json — superseded package drafts retained; not delivery.

The standalone package omits OS/runtime installation and operational authority
configuration. The canonical original RC1/source/evidence and dirty development
checkout remain preserved. No VM or protected installation occurred.
