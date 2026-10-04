# Deterministic integrity and sealing

Use the project's existing SHA-256 / canonical sorted UTF-8 JSON convention (registry_metadata.py:45–53) for the explicitly versioned evidence entry. See SERIALIZATION.md for the exact logical payload. Validate schema and digest on recovery; do not accept a corrupt/partial or unknown-version entry as valid evidence.

The final formal P7 bundle must bind the exact evaluated evidence set to stable ordered committed positions, entry digests/versions and recoverable coverage reconciliation. Preserve that ordered set/aggregate inputs and decisions in sealed evidence; verify SHA256SUMS excluding itself with zero failures. Current established sealed task-bundle manifests supply this convention. Counts alone do not identify the evaluated set; missing/duplicated/substituted entries must not disappear behind a new aggregate.

SHA256 is integrity comparison, not encryption, signing, authenticated origin or tamper-proofing against a writer able to replace both content and manifest. Protect local access and retain sealed references. No signing/PKI, hash-chain, remote attestation or migration scheme invented. Binding fingerprints may be dictionary-linked; hashing does not anonymize identity/target information.
