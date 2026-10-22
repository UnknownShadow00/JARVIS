# Evidence scope and verification

SHA256SUMS covers every file in this new packet except itself. Its digest is recorded separately in the sibling .seal file. This is an integrity record, not a signature, operator approval or OS attestation.

- entry-provenance.json: verified Gate6I235 evidence members/606 source members before copying.
- historical-seals-reverified.json: unchanged Gate6I and Gate6H sealed evidence.
- candidate-identity.json, SOURCE-SHA256SUMS, FULL-SOURCE-SHA256SUMS: exact final bundle and612 source members/613 inventory members.
- gate6i-to-gate6j.patch and source/: actual changed/new source, with no production app changes.
- runs/: minimized known test outputs, kernel/audit metadata and each run's independent source verification. Failing reproductions remain present.
- final-test-source-association.json: exact613-file final candidate association; supplemental wire run adds one explicitly identified test file.
- runner-final-r2.txt, kernel-runner-probe.json, compile.json and dependency-pin-check-final.json: actual unprivileged package evidence.
- disposable-qualification-status.json: all genuine distinct-UID properties explicitly NOT RUN.
- production-entry.json, production-final.json and production-comparison.json: fresh minimized read-only snapshots,21 comparable fields, no differences.
- completion-log-entry.md: required completion record appended before sealing.

No real private signing key, credential value, protected environment dump or real conversation is included. Synthetic private keys remain ephemeral/in disposable fixture storage and are not exported. Archives remain in the separately versioned private candidate location. Snapshot-synchronized task documents contain only reviewed code, hashes and minimized nonsecret evidence. Future VM exports must use the explicit report allowlist, not a recursive archive of its signing/app state.
