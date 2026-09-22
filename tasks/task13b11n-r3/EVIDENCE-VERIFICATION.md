# Evidence verification
All 41 sealed bundles present before sealing R3 were reverified with sha256sum -c SHA256SUMS from each bundle root: zero failures.
Per-bundle entry counts and manifest digests are recorded in readiness-audit.json. No old bundle was modified.
Task A bundle manifest digest: 9e7f1e1fdcd78f19798932b761295345495f48108ed419d938b7378c45434986.
Task B bundle manifest digest: 77d168c60816eee4d4efb385febd5511a7750cf2d9eb21235ab01aed945e66a6 (50 entries / 51 files).
Task M digest still 503644df20a56b6ce631aec17ce91b24b87e93427b9f2b1e9b947e0a3f213d28.
R1/R2 historical aggregate-formula anomaly from classifier reconciliation remains open; verified file manifests do not establish an undocumented historical aggregate formula. New bundles consistently report SHA-256 of the literal SHA256SUMS bytes.
R3 gets a new bundle; its own SHA256SUMS excludes itself, and is verified after all files/commit references are present.
